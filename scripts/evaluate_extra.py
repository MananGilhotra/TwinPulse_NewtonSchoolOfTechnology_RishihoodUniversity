"""Clinically framed evaluation on real patients.

1. Night guard, event level: of all night-time lows, how many got an alert in time, how much
   warning, and how many false alarms per night? (Patients held out, 5 groups; plus external.)
2. Sensor allocation: does a child's first week of CGM rank who will have most night lows later?
3. Physiology twin, bedtime walk-forward (from scripts/eval_twin.py output).

Writes reports/metrics_extra.json.
"""
from __future__ import annotations

import json
import os
import sys

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse.data import load_all  # noqa: E402
from twinpulse.features import RT_FEATURES, realtime_table  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports")
PROC = os.path.join(ROOT, "data", "processed")
THRESHOLDS = [0.15, 0.2, 0.3]


def clf():
    return lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=50,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=7, verbose=-1)


def night_events(d: pd.DataFrame) -> pd.DataFrame:
    """Night-time low onsets (22:00-06:00) after at least 30 min at or above 70 mg/dL."""
    g = d["glucose"].to_numpy()
    below = np.nan_to_num(g, nan=999) < 70
    run = pd.Series(below).rolling(3).sum().to_numpy() >= 3
    onsets = []
    for i in range(3, len(g)):
        if run[i] and not run[i - 1]:
            start = i - 2
            prev = g[max(0, start - 6):start]
            h = d["time"].iloc[start].hour
            if len(prev) == 6 and np.all(prev >= 70) and (h >= 22 or h < 6):
                onsets.append(start)
    return d.iloc[onsets][["patient", "time"]]


def score_events(d: pd.DataFrame, p: np.ndarray, thr: float) -> dict:
    """d: one patient's 5-min rows (sorted) with glucose; p: smoothed risk per row."""
    alert = (p >= thr) & (d["glucose"].to_numpy() >= 70)
    times = d["time"].to_numpy()
    ev = night_events(d)
    leads = []
    for t in ev["time"].to_numpy():
        win = (times >= t - np.timedelta64(120, "m")) & (times <= t)
        idx = np.flatnonzero(win & alert)
        leads.append((t - times[idx[0]]) / np.timedelta64(1, "m") if len(idx) else np.nan)
    # Alert episodes at night: a new episode starts after 60 min without alert.
    hours = d["time"].dt.hour.to_numpy()
    night = (hours >= 22) | (hours < 6)
    ep_starts = []
    last = -999
    for i in np.flatnonzero(alert & night):
        if i - last > 12:
            ep_starts.append(i)
        last = i
    lows = np.nan_to_num(d["glucose"].to_numpy(), nan=999) < 70
    false_eps = 0
    for i in ep_starts:
        if not lows[i:i + 25].any():
            false_eps += 1
    n_nights = d.loc[night, "time"].dt.normalize().nunique()
    return {"events": len(leads), "leads": leads, "alert_episodes": len(ep_starts), "false_episodes": false_eps,
            "nights": int(n_nights)}


def summarise(parts: list[dict]) -> dict:
    leads = np.array([x for p in parts for x in p["leads"]], dtype=float)
    nights = sum(p["nights"] for p in parts)
    caught = ~np.isnan(leads)
    in_time = caught & (leads >= 15)
    return {"night_lows": int(len(leads)), "caught_any": float(caught.mean()) if len(leads) else None,
            "caught_15min_ahead": float(in_time.mean()) if len(leads) else None,
            "median_warning_min": float(np.nanmedian(leads)) if caught.any() else None,
            "false_alarms_per_night": sum(p["false_episodes"] for p in parts) / max(nights, 1),
            "alerts_per_night": sum(p["alert_episodes"] for p in parts) / max(nights, 1), "nights": int(nights)}


def guard_eval(df: pd.DataFrame) -> dict:
    rt = realtime_table(df, every=1)
    rt = rt.merge(df[["patient", "time", "glucose"]], on=["patient", "time"], how="left")
    rt = rt.sort_values(["patient", "time"]).reset_index(drop=True)
    hupa = rt[rt.dataset == "HUPA-UCM"].reset_index(drop=True)
    train_mask = hupa["low_next120"].notna() & (hupa["g_lag0"] >= 80)
    oof = np.full(len(hupa), np.nan)
    for tr, te in GroupKFold(5).split(hupa, groups=hupa["patient"]):
        trm = np.zeros(len(hupa), bool)
        trm[tr] = True
        trm &= train_mask.to_numpy()
        m = clf().fit(hupa.loc[trm, RT_FEATURES], hupa.loc[trm, "low_next120"])
        oof[te] = m.predict_proba(hupa.iloc[te][RT_FEATURES])[:, 1]
    hupa["p"] = oof
    m = clf().fit(hupa.loc[train_mask, RT_FEATURES], hupa.loc[train_mask, "low_next120"])
    uom = rt[rt.dataset == "T1D-UOM"].reset_index(drop=True)
    uom["p"] = m.predict_proba(uom[RT_FEATURES])[:, 1]
    out = {}
    for name, d in [("unseen_patients", hupa), ("external", uom)]:
        d["ps"] = d.groupby("patient")["p"].transform(lambda s: s.rolling(3, min_periods=1).mean())
        out[name] = {}
        for thr in THRESHOLDS:
            parts = [score_events(g.reset_index(drop=True), g["ps"].to_numpy(), thr) for _, g in d.groupby("patient")]
            out[name][str(thr)] = summarise(parts)
    return out


def sensor_ranking() -> dict:
    n = pd.read_parquet(os.path.join(PROC, "nights.parquet")).sort_values(["patient", "date"])
    n["idx"] = n.groupby("patient").cumcount()
    a = n[n.idx < 7].groupby("patient").agg(week1_tbr=("tbr24", "mean"), week1_night_lows=("hypo_night", "mean"))
    b = n[n.idx >= 7].groupby("patient").agg(later_night_low_rate=("hypo_night", "mean"), later_nights=("hypo_night", "size"))
    m = a.join(b, how="inner")
    m = m[m.later_nights >= 3]
    top = m.sort_values("week1_tbr", ascending=False)
    k = len(m) // 3
    return {"patients": int(len(m)),
            "spearman_week1_tbr_vs_later": float(m.week1_tbr.corr(m.later_night_low_rate, method="spearman")),
            "spearman_week1_nightlows_vs_later": float(m.week1_night_lows.corr(m.later_night_low_rate, method="spearman")),
            "top_third_later_rate": float(top.iloc[:k].later_night_low_rate.mean()),
            "bottom_third_later_rate": float(top.iloc[-k:].later_night_low_rate.mean()),
            "table": m.reset_index().round(4).to_dict(orient="records")}


def twin_bedtime() -> dict:
    path = os.path.join(PROC, "twin_walkforward.parquet")
    if not os.path.exists(path):
        return {}
    t = pd.read_parquet(path)
    return {ds: {"nights": int(len(g)), "twin_auroc": float(roc_auc_score(g.hypo_night, g.twin_p_low)),
                 "bedtime_bg_rule_auroc": float(roc_auc_score(g.hypo_night, -g.bg_now))}
            for ds, g in t.groupby("dataset")}


def main():
    df = load_all()
    res = {"guard_events": guard_eval(df), "sensor_ranking": sensor_ranking(), "twin_bedtime": twin_bedtime()}
    with open(os.path.join(REPORTS, "metrics_extra.json"), "w") as f:
        json.dump(res, f, indent=2)
    print(json.dumps({k: v for k, v in res.items() if k != "sensor_ranking"}, indent=1))
    print({k: v for k, v in res["sensor_ranking"].items() if k != "table"})


if __name__ == "__main__":
    main()
