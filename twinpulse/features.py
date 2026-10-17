"""Event labels and model features.

Definitions (international CGM consensus, Battelino et al., Diabetes Care 2019):
    level-1 low: glucose < 70 mg/dL for at least 15 minutes (3 readings)
    level-2 low: glucose < 54 mg/dL for at least 15 minutes
    night:       00:00-06:00
"""
from __future__ import annotations

import numpy as np
import pandas as pd

STEP_MIN = 5
HYPO = 70.0
HYPO_L2 = 54.0
MIN_RUN = 3  # 3 x 5 min = 15 minutes
BEDTIME_HOUR = 23  # the twin "lives the night" from 23:00
NIGHT_START_H, NIGHT_END_H = 0, 6
FINGERSTICK_TIMES = ["07:30", "13:00", "19:30", "22:30"]  # pre-meal + bedtime checks


def insulin_activity_kernel(td: float = 300.0, tp: float = 75.0, step: float = STEP_MIN) -> tuple[np.ndarray, np.ndarray]:
    """Rapid-acting insulin action (OpenAPS exponential model).

    Returns (activity per step, insulin-on-board fraction) for one unit dosed at t=0.
    """
    t = np.arange(0, td + step, step)
    tau = tp * (1 - tp / td) / (1 - 2 * tp / td)
    a = 2 * tau / td
    S = 1 / (1 - a + (1 + a) * np.exp(-td / tau))
    activity = (S / tau**2) * t * (1 - t / td) * np.exp(-t / tau)
    iob = 1 - S * (1 - a) * ((t**2 / (tau * td * (1 - a)) - t / tau - 1) * np.exp(-t / tau) + 1)
    return activity * step, np.clip(iob, 0, 1)


def carb_kernel(duration_min: float = 180.0, step: float = STEP_MIN) -> np.ndarray:
    """Fraction of a meal's carbs still unabsorbed (linear absorption)."""
    t = np.arange(0, duration_min + step, step)
    return np.clip(1 - t / duration_min, 0, 1)


def _causal_conv(x: np.ndarray, kernel: np.ndarray) -> np.ndarray:
    return np.convolve(x, kernel)[: len(x)]


def add_physiology_signals(d: pd.DataFrame) -> pd.DataFrame:
    """Insulin on board and carbs on board, computed only from the past."""
    d = d.copy()
    _, iob_k = insulin_activity_kernel()
    d["iob"] = _causal_conv(d["bolus"].to_numpy(), iob_k)
    d["cob"] = _causal_conv(d["carbs"].to_numpy(), carb_kernel())
    return d


def runs_below(values: np.ndarray, thr: float, min_run: int = MIN_RUN) -> bool:
    run = 0
    for v in values:
        if not np.isnan(v) and v < thr:
            run += 1
            if run >= min_run:
                return True
        else:
            run = 0
    return False


def first_low_time(times: pd.DatetimeIndex, values: np.ndarray, thr: float = HYPO, min_run: int = MIN_RUN):
    run = 0
    for i, v in enumerate(values):
        if not np.isnan(v) and v < thr:
            run += 1
            if run >= min_run:
                return times[i - min_run + 1]
        else:
            run = 0
    return None


def _window(d: pd.DataFrame, start, end) -> pd.DataFrame:
    return d.loc[(d.index > start - pd.Timedelta(seconds=1)) & (d.index < end)]


def nightly_table(df: pd.DataFrame) -> pd.DataFrame:
    """One row per patient-night with features known at 23:00 and the night's outcome."""
    rows = []
    for (dataset, patient), d in df.groupby(["dataset", "patient"], sort=False):
        d = add_physiology_signals(d.sort_values("time")).set_index("time")
        days = pd.date_range(d.index.min().normalize(), d.index.max().normalize(), freq="D")
        past_nights = []
        for day in days:
            t0 = day + pd.Timedelta(hours=BEDTIME_HOUR)
            n0 = day + pd.Timedelta(days=1, hours=NIGHT_START_H)
            n1 = day + pd.Timedelta(days=1, hours=NIGHT_END_H)
            night = _window(d, n0, n1)
            if len(night) < 60 or night["glucose"].notna().mean() < 0.7:
                continue
            last24 = _window(d, t0 - pd.Timedelta(hours=24), t0)
            if len(last24) < 200 or last24["glucose"].notna().mean() < 0.7:
                continue
            g24 = last24["glucose"]
            g3 = _window(d, t0 - pd.Timedelta(hours=3), t0)["glucose"]
            g1 = _window(d, t0 - pd.Timedelta(hours=1), t0)["glucose"]
            if g1.notna().sum() < 6:
                continue
            g_now = g1.dropna().iloc[-1]
            g30 = _window(d, t0 - pd.Timedelta(minutes=35), t0 - pd.Timedelta(minutes=25))["glucose"].mean()
            evening = _window(d, day + pd.Timedelta(hours=16), t0)
            at = d.loc[d.index <= t0].iloc[-1]
            day_rows = _window(d, day, t0)
            hr_day = day_rows["hr"].dropna()

            # Fingerstick mode: only four glucose readings that day are visible.
            fs = {}
            for k, hm in enumerate(FINGERSTICK_TIMES):
                ts = day + pd.Timedelta(hours=int(hm[:2]), minutes=int(hm[3:]))
                near = _window(d, ts - pd.Timedelta(minutes=10), ts + pd.Timedelta(minutes=10))["glucose"].dropna()
                fs[f"fs_bg{k + 1}"] = near.iloc[0] if len(near) else np.nan

            prior = past_nights[-14:]
            row = dict(
                dataset=dataset, patient=patient, date=day.date().isoformat(),
                # CGM features
                bg_now=g_now, bg_slope30=(g_now - g30) / 30 if not np.isnan(g30) else np.nan,
                bg_mean1h=g1.mean(), bg_min1h=g1.min(), bg_mean3h=g3.mean(), bg_min3h=g3.min(), bg_sd3h=g3.std(),
                bg_mean24=g24.mean(), bg_sd24=g24.std(), bg_min24=g24.min(),
                tbr24=(g24 < HYPO).mean(), tar24=(g24 > 180).mean(),
                lows_today=int(runs_below(day_rows["glucose"].to_numpy(), HYPO)),
                # insulin and meals
                iob=at["iob"], cob=at["cob"],
                bolus_evening=evening["bolus"].sum(), carbs_evening=evening["carbs"].sum(),
                bolus24=last24["bolus"].sum(), basal24=last24["basal"].sum(), basal_inj24=last24["basal_inj"].sum(),
                basal_night_plan=_window(d, t0 - pd.Timedelta(hours=24), t0 - pd.Timedelta(hours=17))["basal"].sum(),
                carbs24=last24["carbs"].sum(),
                # wearable features
                steps_evening=evening["steps"].sum(), steps_day=day_rows["steps"].sum(),
                hr_evening=evening["hr"].mean(), hr_day_p10=hr_day.quantile(0.1) if len(hr_day) else np.nan,
                weekday=day.dayofweek,
                # patient history known so far (the twin's memory)
                prior_nights=len(prior), prior_hypo_rate=np.mean(prior) if prior else np.nan,
                **fs,
            )
            ng = night["glucose"].to_numpy()
            row["hypo_night"] = int(runs_below(ng, HYPO))
            row["hypo_night_l2"] = int(runs_below(ng, HYPO_L2))
            ft = first_low_time(night.index, ng)
            row["hypo_onset_min"] = (ft - t0).total_seconds() / 60 if ft is not None else np.nan
            row["night_min"] = np.nanmin(ng)
            rows.append(row)
            past_nights.append(row["hypo_night"])
    t = pd.DataFrame(rows)
    # Resting-heart-rate deviation from the patient's own running baseline (illness / stress signal).
    t["hr_rest_dev"] = t.groupby("patient")["hr_day_p10"].transform(lambda s: s - s.expanding().median().shift(1))
    return t


CGM_FEATURES = ["bg_now", "bg_slope30", "bg_mean1h", "bg_min1h", "bg_mean3h", "bg_min3h", "bg_sd3h",
                "bg_mean24", "bg_sd24", "bg_min24", "tbr24", "tar24", "lows_today"]
FINGERSTICK_FEATURES = ["fs_bg1", "fs_bg2", "fs_bg3", "fs_bg4"]
INSULIN_MEAL_FEATURES = ["iob", "cob", "bolus_evening", "carbs_evening", "bolus24", "basal24", "basal_inj24",
                         "basal_night_plan", "carbs24"]
WEARABLE_FEATURES = ["steps_evening", "steps_day", "hr_evening", "hr_day_p10", "hr_rest_dev"]
HISTORY_FEATURES = ["prior_nights", "prior_hypo_rate", "weekday"]


def realtime_table(df: pd.DataFrame, every: int = 3) -> pd.DataFrame:
    """Rows every `every` x 5 min with lagged features and future targets for CGM mode."""
    out = []
    lags = [0, 1, 2, 3, 6, 9, 12, 18, 24]
    for (dataset, patient), d in df.groupby(["dataset", "patient"], sort=False):
        d = add_physiology_signals(d.sort_values("time")).reset_index(drop=True)
        g = d["glucose"]
        f = pd.DataFrame({"dataset": dataset, "patient": patient, "time": d["time"]})
        for L in lags:
            f[f"g_lag{L}"] = g.shift(L)
        f["g_d1"] = g - g.shift(1)
        f["g_d3"] = g - g.shift(3)
        f["g_d6"] = g - g.shift(6)
        f["g_sd1h"] = g.rolling(12, min_periods=6).std()
        f["iob"] = d["iob"]
        f["cob"] = d["cob"]
        f["bolus_2h"] = d["bolus"].rolling(24, min_periods=1).sum()
        f["carbs_2h"] = d["carbs"].rolling(24, min_periods=1).sum()
        f["basal_2h"] = d["basal"].rolling(24, min_periods=1).sum()
        f["steps_1h"] = d["steps"].rolling(12, min_periods=1).sum()
        f["steps_6h"] = d["steps"].rolling(72, min_periods=1).sum()
        f["hr_now"] = d["hr"].rolling(3, min_periods=1).mean()
        f["hr_dev"] = f["hr_now"] - d["hr"].rolling(288 * 3, min_periods=288).median()
        f["hour_sin"] = np.sin(2 * np.pi * d["time"].dt.hour / 24)
        f["hour_cos"] = np.cos(2 * np.pi * d["time"].dt.hour / 24)
        for h in [6, 12, 24]:
            f[f"y_{h * 5}"] = g.shift(-h)
        fut = pd.concat([g.shift(-k) for k in range(1, 13)], axis=1)
        f["low_next60"] = (fut < HYPO).sum(axis=1).ge(MIN_RUN).astype(float)
        f.loc[fut.notna().sum(axis=1) < 9, "low_next60"] = np.nan
        fut2 = pd.concat([g.shift(-k) for k in range(1, 25)], axis=1)
        f["low_next120"] = (fut2 < HYPO).sum(axis=1).ge(MIN_RUN).astype(float)
        f.loc[fut2.notna().sum(axis=1) < 18, "low_next120"] = np.nan
        f = f.iloc[::every]
        out.append(f[f["g_lag0"].notna() & f["g_lag6"].notna()])
    return pd.concat(out, ignore_index=True)


RT_FEATURES = [f"g_lag{L}" for L in [0, 1, 2, 3, 6, 9, 12, 18, 24]] + [
    "g_d1", "g_d3", "g_d6", "g_sd1h", "iob", "cob", "bolus_2h", "carbs_2h", "basal_2h",
    "steps_1h", "steps_6h", "hr_now", "hr_dev", "hour_sin", "hour_cos"]
RT_GLUCOSE_ONLY = [f"g_lag{L}" for L in [0, 1, 2, 3, 6, 9, 12, 18, 24]] + ["g_d1", "g_d3", "g_d6", "g_sd1h", "hour_sin", "hour_cos"]
