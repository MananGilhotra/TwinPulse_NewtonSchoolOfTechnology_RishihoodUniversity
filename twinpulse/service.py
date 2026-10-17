"""Everything the dashboard asks the twin: tonight's rehearsal, what-ifs, the night guard, weekly stats."""
from __future__ import annotations

import json
import os
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd

from .features import realtime_table
from .synth import DAYS, DEMO, START
from .twin import LONG_ACTING, Twin, fit_twin, night_risk, night_window

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(ROOT, "models")
TONIGHT = START + pd.Timedelta(days=DAYS - 1)  # the day whose night we rehearse (17 Oct 2026)
N_SIMS = 500
GUARD_THRESHOLD = 0.2


def _cohort() -> list[dict]:
    with open(os.path.join(DEMO, "cohort.json")) as f:
        return json.load(f)


@lru_cache(maxsize=None)
def cohort_meta() -> dict:
    return {c["id"]: c for c in _cohort()}


@lru_cache(maxsize=None)
def patient_frame(pid: str) -> pd.DataFrame:
    df = pd.read_parquet(os.path.join(DEMO, f"{pid}.parquet"))
    meta = cohort_meta()[pid]
    # What the twin is allowed to see: CGM for CGM families, only finger-pricks otherwise.
    df["glucose_seen"] = df["glucose"] if meta["mode"] == "cgm" else df["fingerstick"]
    return df


def _twin_input(pid: str) -> pd.DataFrame:
    df = patient_frame(pid)
    d = df[["time", "glucose_seen", "carbs", "bolus", "basal", "basal_inj", "steps", "hr"]].rename(
        columns={"glucose_seen": "glucose"})
    return d.set_index("time")


@lru_cache(maxsize=None)
def patient_twin(pid: str) -> Twin:
    meta = cohort_meta()[pid]
    d = _twin_input(pid)
    windows = [night_window(d, START + pd.Timedelta(days=k), tdd=meta["tdd"]) for k in range(DAYS - 1)]
    windows = [w for w in windows if w is not None]
    tau_l = LONG_ACTING[meta["insulin_type"]]
    return fit_twin(windows, ib=meta["ib"], tau_l=tau_l, tdd=meta["tdd"])


def tonight_window(pid: str):
    meta = cohort_meta()[pid]
    return night_window(_twin_input(pid), TONIGHT, tdd=meta["tdd"])


def _band_json(w, risk) -> list[dict]:
    i0 = w.nudge_until - 24  # show from 21:00
    out = []
    for i in range(i0, len(w.times)):
        out.append({"t": w.times[i].strftime("%Y-%m-%dT%H:%M"), **{f"p{q}": round(float(risk["band"][q][i]), 1)
                                                                   for q in (5, 25, 50, 75, 95)}})
    return out


def _summ(risk) -> dict:
    return {k: risk[k] for k in ("p_low", "p_low_l2", "median_onset", "p10_min", "median_min")}


def whatif_overrides(w, snack_g=0.0, dinner_rapid_pct=0.0, long_acting_pct=0.0, long_acting_shift_min=0,
                     skip_play=False) -> dict:
    """Translate doctor-facing changes into twin inputs."""
    ov = {}
    if snack_g:
        c = w.carbs.copy()
        c[w.nudge_until - 6] += snack_g  # 22:30 bedtime snack
        ov["carbs"] = c
    evening = slice(w.nudge_until - 36, w.nudge_until)  # 20:00-23:00
    if dinner_rapid_pct:
        b = w.bolus.copy()
        b[evening] *= 1 + dinner_rapid_pct / 100
        ov["bolus"] = b
    if long_acting_pct or long_acting_shift_min:
        inj = w.inj.copy()
        idx = np.flatnonzero(inj[evening.start - 12:w.nudge_until]) + evening.start - 12  # 19:00-23:00 injections
        for i in idx:
            dose = inj[i] * (1 + long_acting_pct / 100)
            inj[i] = 0
            j = min(i + int(long_acting_shift_min // 5), len(inj) - 1)
            inj[j] += dose
        ov["inj"] = inj
    if skip_play:
        s = w.steps.copy()
        play = slice(w.nudge_until - 72, w.nudge_until - 54)  # 17:00-18:30
        s[play] = np.minimum(s[play], 60)
        ov["steps"] = s
    return ov


def explain(pid: str, w, twin: Twin, base: float) -> list[dict]:
    """Why is tonight risky? Remove one factor at a time on the twin and see how the risk moves."""
    meta = cohort_meta()[pid]
    factors = [("Evening play (17:00-18:30)", dict(skip_play=True))]
    if meta["insulin_type"] == "nph":
        factors.append(("Dinner-time NPH insulin (peaks around 1-4 AM)", dict(long_acting_pct=-20)))
    else:
        factors.append(("Bedtime long-acting insulin", dict(long_acting_pct=-20)))
    factors.append(("Dinner insulin dose", dict(dinner_rapid_pct=-20)))
    out = []
    for label, kw in factors:
        p = night_risk(twin.run(w, n=N_SIMS, seed=1, overrides=whatif_overrides(w, **kw)), w)["p_low"]
        out.append({"factor": label, "risk_without": round(p, 3), "contribution": round(base - p, 3)})
    g_now = w.glucose[:w.nudge_until]
    last = g_now[~np.isnan(g_now)]
    if len(last):
        out.append({"factor": f"Last glucose before bed: {last[-1]:.0f} mg/dL", "risk_without": None,
                    "contribution": None})
    return sorted(out, key=lambda r: -(r["contribution"] or -1))


@lru_cache(maxsize=None)
def tonight(pid: str) -> dict:
    twin = patient_twin(pid)
    w = tonight_window(pid)
    risk = night_risk(twin.run(w, n=N_SIMS, seed=1), w)
    return {"risk": _summ(risk), "band": _band_json(w, risk), "explain": explain(pid, w, twin, risk["p_low"]),
            "twin": twin.as_dict()}


def whatif(pid: str, **kw) -> dict:
    twin = patient_twin(pid)
    w = tonight_window(pid)
    risk = night_risk(twin.run(w, n=N_SIMS, seed=1, overrides=whatif_overrides(w, **kw)), w)
    return {"risk": _summ(risk), "band": _band_json(w, risk), "baseline": tonight(pid)["risk"]}


@lru_cache(maxsize=None)
def _rt_models():
    return {k: joblib.load(os.path.join(MODELS, f"{k}.joblib")) for k in ("low_next60", "low_next120", "forecast_30", "forecast_60")}


@lru_cache(maxsize=None)
def night_guard(pid: str) -> dict:
    """Replay tonight minute by minute: what the real-time guard would have said (CGM families only)."""
    meta = cohort_meta()[pid]
    if meta["mode"] != "cgm":
        return {"available": False, "reason": "Needs a CGM: this family uses finger-pricks only."}
    df = patient_frame(pid)
    d = df[["time", "glucose", "carbs", "bolus", "basal", "basal_inj", "steps", "hr"]].copy()
    d["dataset"], d["patient"] = "demo", pid
    rt = realtime_table(d, every=1)
    t0, t1 = TONIGHT + pd.Timedelta(hours=22), TONIGHT + pd.Timedelta(days=1, hours=7)
    rt = rt[(rt.time >= t0) & (rt.time < t1)].reset_index(drop=True)
    m = _rt_models()
    for k in ("low_next60", "low_next120"):
        # 15-minute smoothing so a single noisy reading does not wake a parent
        rt[k + "_p"] = pd.Series(m[k]["model"].predict_proba(rt[m[k]["features"]])[:, 1]).rolling(3, min_periods=1).mean()
    for k in ("forecast_30", "forecast_60"):
        rt[k] = m[k]["model"].predict(rt[m[k]["features"]])
    truth = df[(df.time >= t0) & (df.time < t1)].set_index("time")["glucose_true"]
    low = (truth < 70).rolling(3).sum() >= 3
    onset = truth.index[low.to_numpy().argmax() - 2] if low.any() else None
    alert = rt[(rt.low_next120_p >= GUARD_THRESHOLD) & (rt.g_lag0 >= 70)]
    first_alert = alert.time.iloc[0] if len(alert) else None
    series = [{"t": r.time.strftime("%Y-%m-%dT%H:%M"), "cgm": round(r.g_lag0, 1),
               "p60": round(r.low_next60_p, 3), "p120": round(r.low_next120_p, 3),
               "f30": round(r.forecast_30, 1), "f60": round(r.forecast_60, 1)} for r in rt.itertuples()]
    return {"available": True, "threshold": GUARD_THRESHOLD, "series": series,
            "first_alert": first_alert.strftime("%H:%M") if first_alert is not None else None,
            "low_onset": onset.strftime("%H:%M") if onset is not None else None,
            "lead_min": int((onset - first_alert).total_seconds() // 60) if onset is not None and first_alert is not None and first_alert <= onset else None}


def weekly(pid: str) -> dict:
    df = patient_frame(pid)
    g = df["glucose_true"] if cohort_meta()[pid]["mode"] == "fingerstick" else df["glucose"]
    hours = df["time"].dt.hour
    by_hour = [{"hour": h, "tbr": round(float((g[hours == h] < 70).mean()), 3)} for h in range(24)]
    cv = float(g.std() / g.mean())
    return {"source": "14-day trial sensor" if cohort_meta()[pid]["mode"] == "fingerstick" else "CGM",
            "tir": round(float(((g >= 70) & (g <= 180)).mean()), 3), "tbr70": round(float((g < 70).mean()), 3),
            "tbr54": round(float((g < 54).mean()), 3), "tar180": round(float((g > 180).mean()), 3),
            "mean": round(float(g.mean()), 1), "gmi": round(3.31 + 0.02392 * float(g.mean()), 1), "cv": round(cv, 3),
            "night_tbr": round(float((g[hours < 6] < 70).mean()), 3), "lows_by_hour": by_hour}


def recent_series(pid: str, hours: int = 36) -> list[dict]:
    df = patient_frame(pid)
    end = TONIGHT + pd.Timedelta(hours=23)
    d = df[(df.time > end - pd.Timedelta(hours=hours)) & (df.time <= end)]
    out = []
    for r in d.itertuples():
        out.append({"t": r.time.strftime("%Y-%m-%dT%H:%M"),
                    "g": None if pd.isna(r.glucose_seen) else round(float(r.glucose_seen), 1),
                    "carbs": round(float(r.carbs), 1) or None, "bolus": round(float(r.bolus), 2) or None,
                    "long": round(float(r.basal_inj), 2) or None, "steps": int(r.steps), "hr": round(float(r.hr), 1)})
    return out


def patient(pid: str) -> dict:
    meta = cohort_meta()[pid]
    with open(os.path.join(DEMO, f"{pid}_fhir.json")) as f:
        fhir = json.load(f)
    return {"meta": meta, "fhir": fhir, "series": recent_series(pid), "tonight": tonight(pid),
            "weekly": weekly(pid), "guard": night_guard(pid)}


def board() -> list[dict]:
    rows = []
    for pid, meta in cohort_meta().items():
        t = tonight(pid)
        wk = weekly(pid)
        df = patient_frame(pid)
        seen = df[df.time <= TONIGHT + pd.Timedelta(hours=23)]["glucose_seen"].dropna()
        rows.append({"id": pid, "name": meta["name"], "age": meta["age"], "town": meta["town"],
                     "language": meta["language"], "mode": meta["mode"], "regimen": meta["regimen"],
                     "p_low": t["risk"]["p_low"], "onset": t["risk"]["median_onset"],
                     "last_bg": float(seen.iloc[-1]) if len(seen) else None,
                     "night_tbr_14d": wk["night_tbr"], "tir": wk["tir"], "hero": meta.get("hero", False)})
    return sorted(rows, key=lambda r: -r["p_low"])


def validation() -> dict:
    with open(os.path.join(ROOT, "reports", "metrics.json")) as f:
        out = json.load(f)
    extra = os.path.join(ROOT, "reports", "metrics_extra.json")
    if os.path.exists(extra):
        with open(extra) as f:
            out["extra"] = json.load(f)
    return out
