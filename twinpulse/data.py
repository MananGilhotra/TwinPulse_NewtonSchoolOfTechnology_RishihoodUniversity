"""Load the open T1D datasets into one 5-minute table per patient.

Unified columns (one row per 5 minutes):
    time, glucose (mg/dL), carbs (g), bolus (U), basal (U delivered in the
    5-minute slot), basal_inj (U of long-acting insulin injected), steps,
    hr (bpm), dataset, patient
"""
from __future__ import annotations

import glob
import os

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
PROCESSED = os.path.join(ROOT, "data", "processed")
FREQ = "5min"
MMOL_TO_MGDL = 18.0182

COLUMNS = ["time", "glucose", "carbs", "bolus", "basal", "basal_inj", "steps", "hr"]


def _grid(start, end) -> pd.DatetimeIndex:
    return pd.date_range(pd.Timestamp(start).floor(FREQ), pd.Timestamp(end).ceil(FREQ), freq=FREQ)


def load_hupa(path: str) -> pd.DataFrame:
    d = pd.read_csv(path, sep=";", parse_dates=["time"])
    d = d.rename(columns={
        "heart_rate": "hr", "bolus_volume_delivered": "bolus",
        "carb_input": "carbs", "basal_rate": "basal",
    })
    d["time"] = d["time"].dt.floor(FREQ)
    d = d.groupby("time").agg(glucose=("glucose", "mean"), carbs=("carbs", "sum"),
                              bolus=("bolus", "sum"), basal=("basal", "sum"),
                              steps=("steps", "sum"), hr=("hr", "mean"))
    d = d.reindex(_grid(d.index.min(), d.index.max()))
    for c in ["carbs", "bolus", "basal", "steps"]:
        d[c] = d[c].fillna(0.0)
    d["basal_inj"] = 0.0
    d.index.name = "time"
    return d.reset_index()[COLUMNS]


def _read_uom(path: str, ts_col: str) -> pd.DataFrame:
    d = pd.read_csv(path, encoding="utf-8-sig")
    d = d.loc[:, ~d.columns.str.startswith("Unnamed")]
    d[ts_col] = pd.to_datetime(d[ts_col], dayfirst=True, errors="coerce")
    return d.dropna(subset=[ts_col])


def load_uom(pid: str, base: str) -> pd.DataFrame | None:
    gpath = os.path.join(base, "Glucose Data", f"UoMGlucose{pid}.csv")
    if not os.path.exists(gpath):
        return None
    g = _read_uom(gpath, "bg_ts")
    g["glucose"] = g["value"] * MMOL_TO_MGDL
    g["time"] = g["bg_ts"].dt.floor(FREQ)
    out = g.groupby("time")[["glucose"]].mean()
    out = out.reindex(_grid(out.index.min(), out.index.max()))
    out.index.name = "time"
    for c in ["carbs", "bolus", "basal", "basal_inj", "steps"]:
        out[c] = 0.0
    out["hr"] = np.nan

    def add_events(path, ts_col, val_col, target):
        if not os.path.exists(path):
            return
        e = _read_uom(path, ts_col)
        e["time"] = e[ts_col].dt.floor(FREQ)
        s = e.groupby("time")[val_col].sum()
        s = s[s.index.isin(out.index)]
        out.loc[s.index, target] += s.values

    add_events(os.path.join(base, "Nutrition Data", f"UoMNutrition{pid}.csv"), "meal_ts", "carbs_g", "carbs")
    add_events(os.path.join(base, "Insulin Data", "Bolus Data", f"UoMBolus{pid}.csv"), "bolus_ts", "bolus_dose", "bolus")

    bpath = os.path.join(base, "Insulin Data", "Basal Data", f"UoMBasal{pid}.csv")
    if os.path.exists(bpath):
        b = _read_uom(bpath, "basal_ts")
        long_acting = b[b["insulin_kind"].str.strip() == "L"].copy()
        if len(long_acting):
            long_acting["time"] = long_acting["basal_ts"].dt.floor(FREQ)
            s = long_acting.groupby("time")["basal_dose"].sum()
            s = s[s.index.isin(out.index)]
            out.loc[s.index, "basal_inj"] += s.values
        pump = b[b["insulin_kind"].str.strip() == "R"].copy()
        if len(pump):
            # Pump basal is a rate in U/h; hold each rate until the next change.
            pump["time"] = pump["basal_ts"].dt.floor(FREQ)
            rate = pump.groupby("time")["basal_dose"].last()
            rate = rate.reindex(out.index).ffill(limit=12 * 24)
            out["basal"] = (rate.fillna(0.0) / 12.0).values

    apath = os.path.join(base, "Activity Data", f"UoMActivity{pid}.csv")
    if os.path.exists(apath):
        a = _read_uom(apath, "activity_ts")
        a["time"] = a["activity_ts"].dt.floor(FREQ)
        s = a.groupby("time")["step_count"].sum()
        # Activity rows are 15-minute blocks: spread steps over three slots.
        spread = pd.concat([s / 3, (s / 3).shift(1, freq=FREQ), (s / 3).shift(2, freq=FREQ)]).groupby(level=0).sum()
        spread = spread[spread.index.isin(out.index)]
        out.loc[spread.index, "steps"] = spread.values

    spath = os.path.join(base, "Sleep Data", f"UoMsleep{pid}.csv")
    if os.path.exists(spath):
        s = _read_uom(spath, "sleep_ts")
        s = s[s["heart_rate"] > 0]
        s["time"] = s["sleep_ts"].dt.floor(FREQ)
        hr = s.groupby("time")["heart_rate"].mean()
        hr = hr[hr.index.isin(out.index)]
        out.loc[hr.index, "hr"] = hr.values

    return out.reset_index()[COLUMNS]


def load_all(cache: bool = True) -> pd.DataFrame:
    cache_path = os.path.join(PROCESSED, "all_patients.parquet")
    if cache and os.path.exists(cache_path):
        return pd.read_parquet(cache_path)
    frames = []
    for f in sorted(glob.glob(os.path.join(RAW, "hupa_ucm", "*.csv"))):
        d = load_hupa(f)
        d["dataset"] = "HUPA-UCM"
        d["patient"] = os.path.basename(f)[:8]
        frames.append(d)
    uom_base = glob.glob(os.path.join(RAW, "t1d_uom", "sharpic-*"))[0]
    pids = sorted({os.path.basename(f)[10:14] for f in glob.glob(os.path.join(uom_base, "Glucose Data", "UoMGlucose*.csv"))})
    for pid in pids:
        d = load_uom(pid, uom_base)
        if d is None:
            continue
        d["dataset"] = "T1D-UOM"
        d["patient"] = f"UOM{pid}"
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    os.makedirs(PROCESSED, exist_ok=True)
    df.to_parquet(cache_path, index=False)
    return df


if __name__ == "__main__":
    df = load_all(cache=False)
    summary = df.groupby(["dataset", "patient"]).agg(
        rows=("glucose", "size"), cgm_cover=("glucose", lambda s: s.notna().mean()),
        mean_bg=("glucose", "mean"), carbs=("carbs", "sum"), bolus=("bolus", "sum"),
        basal=("basal", "sum"), basal_inj=("basal_inj", "sum"), hr_cover=("hr", lambda s: s.notna().mean()),
    ).round(2)
    print(summary.to_string())
