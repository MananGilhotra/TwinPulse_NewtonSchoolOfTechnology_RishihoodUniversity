"""The TwinPulse physiology twin.

A compact glucose-insulin model (Bergman minimal model with subcutaneous insulin,
gut absorption and an exercise effect), personalised to each patient from their
own past nights, then run forward as an ensemble to "live tonight first".

States (5-minute steps):
    G   glucose (mg/dL)
    X   remote insulin action (1/min)
    S1, S2  rapid-acting insulin depots (bolus + pump basal)
    L1, L2  long-acting insulin depots (NPH or glargine injections)
    Q1, Q2  carbohydrate in the gut (g)
    E   lingering exercise effect (0..~1)

Personal parameters (fitted):
    si   insulin sensitivity             (1/min per U/min)
    sg   glucose effectiveness           (1/min)
    gb   glucose the body settles at with usual basal insulin (mg/dL)
    cf   glucose rise per gram of carbohydrate (mg/dL per g)
    ex   exercise effect on glucose uptake (1/min)
    ib   usual insulin delivery rate (U/min), estimated from the patient's records
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from numba import njit
from scipy.optimize import least_squares

DT = 5.0
P2 = 0.02          # 1/min, insulin action rate
TAU_I = 55.0       # min, rapid-acting absorption
KABS = 0.03        # 1/min, gut absorption
TAU_E = 240.0      # min, exercise effect lingers ~4 h (delayed night lows)
STEP_NORM = 500.0  # steps per 5 min that count as "full" activity
LONG_ACTING = {"glargine": 600.0, "nph": 240.0}  # absorption time constant (min)

PARAM_NAMES = ["si", "sg", "gb", "cf", "ex"]
LOWER = np.array([1e-4, 1e-3, 70.0, 1.0, 1e-5])
UPPER = np.array([2.0, 0.05, 300.0, 15.0, 0.02])
DEFAULT = np.array([0.3, 0.005, 140.0, 4.0, 0.002])


@njit(cache=True)
def simulate(params, ib, tau_l, bolus, basal, inj, carbs, steps, g_obs, nudge_until, gain, noise):
    """Simulate N parameter sets over T steps.

    params: (N, 5) array of [si, sg, gb, cf, ex]; noise: (N, T) process noise on glucose (mg/dL per step).
    Before `nudge_until`, glucose is pulled toward observations (data assimilation);
    after it, the twin runs free: that is the forecast.
    """
    N = params.shape[0]
    T = bolus.shape[0]
    out = np.empty((N, T))
    for n in range(N):
        si, sg, gb, cf, ex = params[n, 0], params[n, 1], params[n, 2], params[n, 3], params[n, 4]
        G = gb
        for t in range(T):
            if not np.isnan(g_obs[t]):
                G = g_obs[t]
                break
        X = 0.0
        S1 = ib * TAU_I
        S2 = ib * TAU_I
        L1 = 0.0
        L2 = 0.0
        Q1 = 0.0
        Q2 = 0.0
        E = 0.0
        for t in range(T):
            # inputs arrive at the start of the step
            S1 += bolus[t] + basal[t]
            L1 += inj[t]
            Q1 += carbs[t]
            for _ in range(5):  # 1-minute Euler sub-steps
                ia = S2 / TAU_I + L2 / tau_l
                dS1 = -S1 / TAU_I
                dS2 = (S1 - S2) / TAU_I
                dL1 = -L1 / tau_l
                dL2 = (L1 - L2) / tau_l
                dQ1 = -KABS * Q1
                dQ2 = KABS * (Q1 - Q2)
                ra = cf * KABS * Q2
                dX = -P2 * X + P2 * si * (ia - ib)
                a = steps[t] / STEP_NORM
                if a > 1.5:
                    a = 1.5
                dE = (a - E) / TAU_E
                dG = -(sg + X) * G + sg * gb + ra - ex * E * G
                S1 += dS1
                S2 += dS2
                L1 += dL1
                L2 += dL2
                Q1 += dQ1
                Q2 += dQ2
                X += dX
                E += dE
                G += dG
            if t < nudge_until and not np.isnan(g_obs[t]):
                G = G + gain * (g_obs[t] - G)
            else:
                G += noise[n, t]
            if G < 20.0:
                G = 20.0
            if G > 500.0:
                G = 500.0
            out[n, t] = G
    return out


@dataclass
class NightWindow:
    """Inputs for one night: from 05:00 (warm-up, assimilated) to 07:00 next day (free run after 23:00)."""
    start: pd.Timestamp
    bolus: np.ndarray
    basal: np.ndarray
    inj: np.ndarray
    carbs: np.ndarray
    steps: np.ndarray
    glucose: np.ndarray
    nudge_until: int
    times: pd.DatetimeIndex = field(repr=False, default=None)


def impute_meals(bolus: np.ndarray, carbs: np.ndarray, tdd: float) -> np.ndarray:
    """Many logs record the mealtime insulin but not the meal. Infer the missing carbs with the
    clinical 500 rule (1 U covers ~500/TDD g) when a bolus of 1 U or more has no carbs within 30 min."""
    carbs = carbs.copy()
    icr = 500.0 / tdd
    for t in np.flatnonzero(bolus >= 1.0):
        lo, hi = max(0, t - 6), min(len(carbs), t + 7)
        if carbs[lo:hi].sum() == 0:
            carbs[t] += bolus[t] * icr
    return carbs


def night_window(d: pd.DataFrame, day: pd.Timestamp, bedtime_hour: int = 23,
                 tdd: float | None = None) -> NightWindow | None:
    """d: one patient's 5-min table indexed by time. With `tdd`, unlogged meals are inferred."""
    start = day + pd.Timedelta(hours=5)
    end = day + pd.Timedelta(days=1, hours=7, minutes=30)  # includes the morning finger-prick
    w = d.loc[(d.index >= start) & (d.index < end)]
    idx = pd.date_range(start, end, freq="5min", inclusive="left")
    if len(w) < 0.8 * len(idx):
        return None
    w = w.reindex(idx)
    nudge_until = int((pd.Timedelta(hours=bedtime_hour - 5)) / pd.Timedelta(minutes=5))
    bolus = w["bolus"].fillna(0).to_numpy(float)
    carbs = w["carbs"].fillna(0).to_numpy(float)
    if tdd:
        carbs = impute_meals(bolus, carbs, tdd)
    return NightWindow(start=start, bolus=bolus, basal=w["basal"].fillna(0).to_numpy(float),
                       inj=w["basal_inj"].fillna(0).to_numpy(float), carbs=carbs,
                       steps=w["steps"].fillna(0).to_numpy(float), glucose=w["glucose"].to_numpy(float),
                       nudge_until=nudge_until, times=idx)


@dataclass
class Twin:
    params: np.ndarray
    ib: float
    tau_l: float = LONG_ACTING["glargine"]
    noise_sd: float = 2.0
    fit_rmse: float = float("nan")
    n_nights: int = 0

    def as_dict(self) -> dict:
        return {**{k: float(v) for k, v in zip(PARAM_NAMES, self.params)}, "ib_u_per_h": self.ib * 60,
                "noise_sd": self.noise_sd, "fit_rmse": self.fit_rmse, "n_nights": self.n_nights}

    def run(self, w: NightWindow, n: int = 500, seed: int = 0, param_jitter: float = 0.15,
            overrides: dict | None = None) -> np.ndarray:
        """Live the night n times. Returns (n, T) glucose trajectories."""
        overrides = overrides or {}
        rng = np.random.default_rng(seed)
        p = np.tile(self.params, (n, 1))
        p *= np.exp(rng.normal(0, param_jitter, size=p.shape))
        p[:, 2] = self.params[2] + rng.normal(0, 12, size=n)  # set-point varies night to night
        p = np.clip(p, LOWER, UPPER)
        T = len(w.bolus)
        noise = rng.normal(0, self.noise_sd, size=(n, T))
        inputs = {k: getattr(w, k).copy() for k in ["bolus", "basal", "inj", "carbs", "steps"]}
        for k, v in overrides.items():
            inputs[k] = v
        tau_l = overrides.get("tau_l", self.tau_l) if isinstance(overrides.get("tau_l", None), float) else self.tau_l
        return simulate(p, self.ib, tau_l, inputs["bolus"], inputs["basal"], inputs["inj"], inputs["carbs"],
                        inputs["steps"], w.glucose, w.nudge_until, 0.6, noise)


def _residuals(theta, windows, ib, tau_l, center):
    p = np.exp(theta)[None, :]
    res = []
    zero = None
    for w in windows:
        if zero is None or zero.shape[1] != len(w.bolus):
            zero = np.zeros((1, len(w.bolus)))
        g = simulate(p, ib, tau_l, w.bolus, w.basal, w.inj, w.carbs, w.steps, w.glucose, w.nudge_until, 0.6, zero)[0]
        obs = w.glucose[w.nudge_until:]
        r = (g[w.nudge_until:] - obs) / 30.0
        res.append(np.where(np.isnan(r), 0.0, r))
    # Pull toward clinically typical values; insulin sensitivity is anchored to the 1800 rule.
    prior = (theta - center) * np.array([8.0, 0.3, 0.5, 0.3, 0.1])
    return np.concatenate(res + [prior])


def estimate_ib(d: pd.DataFrame) -> float:
    """Usual insulin delivery rate (U/min): basal plus long-acting, averaged over the record."""
    days = max((d.index.max() - d.index.min()).total_seconds() / 86400, 1)
    total_basal = d["basal"].sum() + d["basal_inj"].sum()
    total = total_basal + d["bolus"].sum()
    if total_basal <= 0:
        return max(total, 10 * days) / days / 1440.0 * 0.5
    return total_basal / days / 1440.0


def estimate_tdd(d: pd.DataFrame) -> float:
    """Total daily insulin dose (U/day) from the record, with a sensible floor when logs are sparse."""
    days = max((d.index.max() - d.index.min()).total_seconds() / 86400, 1)
    return float(max((d["basal"].sum() + d["basal_inj"].sum() + d["bolus"].sum()) / days, 15.0))


def si_from_tdd(tdd: float, typical_bg: float = 140.0) -> float:
    """1800 rule: one unit lowers glucose by ~1800/TDD mg/dL; in this model that drop is ~G * si."""
    return float(np.clip((1800.0 / tdd) / typical_bg, LOWER[0], UPPER[0]))


def fit_twin(windows: list[NightWindow], ib: float, tau_l: float = LONG_ACTING["glargine"],
             tdd: float | None = None) -> Twin:
    center = np.log(DEFAULT.copy())
    if tdd:
        center[0] = np.log(si_from_tdd(tdd))
    theta0 = center.copy()
    sol = least_squares(_residuals, theta0, args=(windows, ib, tau_l, center),
                        bounds=(np.log(LOWER), np.log(UPPER)), max_nfev=200, x_scale=1.0)
    params = np.exp(sol.x)
    n_obs = sum(np.isfinite(w.glucose[w.nudge_until:]).sum() for w in windows)
    rmse = float(np.sqrt(np.sum(sol.fun[:-len(theta0)] ** 2) / max(n_obs, 1)) * 30.0)
    # Process noise sized so a free-running night spreads like the patient's real nights.
    noise_sd = float(np.clip(rmse / np.sqrt(96) * 1.2, 1.0, 6.0))
    return Twin(params=params, ib=ib, tau_l=tau_l, noise_sd=noise_sd, fit_rmse=rmse, n_nights=len(windows))


def night_risk(traj: np.ndarray, w: NightWindow, thr: float = 70.0, run: int = 3) -> dict:
    """Probability of a low between 00:00 and 06:00, likely onset time and depth."""
    hours = w.times.hour
    mask = (hours >= 0) & (hours < 6) & (w.times > w.times[w.nudge_until - 1])
    seg = traj[:, mask]
    below = seg < thr
    # a low = 3 consecutive steps below the threshold
    hits = below[:, 2:] & below[:, 1:-1] & below[:, :-2]
    has = hits.any(axis=1)
    onset = np.where(has, hits.argmax(axis=1), -1)
    times = w.times[mask]
    onset_times = [times[i] for i in onset[has]]
    return {
        "p_low": float(has.mean()),
        "p_low_l2": float(((seg[:, 2:] < 54) & (seg[:, 1:-1] < 54) & (seg[:, :-2] < 54)).any(axis=1).mean()),
        "median_onset": (pd.Series(onset_times).sort_values().iloc[len(onset_times) // 2].strftime("%H:%M")
                         if onset_times else None),
        "p10_min": float(np.percentile(seg.min(axis=1), 10)),
        "median_min": float(np.median(seg.min(axis=1))),
        "band": {q: np.percentile(traj, q, axis=0) for q in (5, 25, 50, 75, 95)},
    }
