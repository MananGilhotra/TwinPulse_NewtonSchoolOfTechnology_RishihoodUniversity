"""Train and evaluate TwinPulse models on real patients.

Night model:    at 23:00, will there be a low (<70 mg/dL, 15+ min) between 00:00 and 06:00?
Real-time:      glucose at +30/+60/+120 min, and a low within the next 60 min (CGM mode).

Validation: patients are split into 5 groups; every score is on patients the model never saw.
External test: train on all HUPA-UCM patients, test on T1D-UOM (different country, devices).
"""
from __future__ import annotations

import json
import os
import sys

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse.features import (CGM_FEATURES, FINGERSTICK_FEATURES, HISTORY_FEATURES, INSULIN_MEAL_FEATURES,  # noqa: E402
                                RT_FEATURES, RT_GLUCOSE_ONLY, WEARABLE_FEATURES)
from twinpulse.metrics import (classification_summary, clarke_summary, parent_sleep_tradeoff,  # noqa: E402
                               regression_summary)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC = os.path.join(ROOT, "data", "processed")
MODELS = os.path.join(ROOT, "models")
REPORTS = os.path.join(ROOT, "reports")
SEED = 7

NIGHT_SETS = {
    "cgm_only": CGM_FEATURES,
    "cgm_insulin_meals": CGM_FEATURES + INSULIN_MEAL_FEATURES,
    "cgm_insulin_meals_wearable": CGM_FEATURES + INSULIN_MEAL_FEATURES + WEARABLE_FEATURES,
    "full_twin": CGM_FEATURES + INSULIN_MEAL_FEATURES + WEARABLE_FEATURES + HISTORY_FEATURES,
    "fingerstick_only": FINGERSTICK_FEATURES,
    "fingerstick_band": FINGERSTICK_FEATURES + INSULIN_MEAL_FEATURES + WEARABLE_FEATURES + HISTORY_FEATURES,
}


def night_clf():
    return lgb.LGBMClassifier(n_estimators=250, learning_rate=0.03, num_leaves=7, min_child_samples=25,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=2.0,
                              random_state=SEED, verbose=-1)


def grouped_oof(df: pd.DataFrame, feats: list[str], target: str, make_model, kind: str = "clf", n_splits: int = 5):
    oof = np.full(len(df), np.nan)
    for tr, te in GroupKFold(n_splits=n_splits).split(df, groups=df["patient"]):
        m = make_model()
        m.fit(df.iloc[tr][feats], df.iloc[tr][target])
        oof[te] = m.predict_proba(df.iloc[te][feats])[:, 1] if kind == "clf" else m.predict(df.iloc[te][feats])
    return oof


def evaluate_nights(nights: pd.DataFrame) -> dict:
    hupa = nights[nights.dataset == "HUPA-UCM"].reset_index(drop=True)
    uom = nights[nights.dataset == "T1D-UOM"].reset_index(drop=True)
    y = hupa["hypo_night"].to_numpy()
    res = {"n_nights": int(len(hupa)), "n_patients": int(hupa.patient.nunique()), "cv": {}, "external": {}}

    # Baselines a clinician might use today.
    res["cv"]["rule_bedtime_bg"] = classification_summary(y, -hupa["bg_now"].to_numpy())
    res["cv"]["rule_bedtime_fingerstick"] = classification_summary(y, -hupa["fs_bg4"].to_numpy())
    lr = grouped_oof(hupa, ["bg_now"], "hypo_night", lambda: LogisticRegression())
    res["cv"]["logistic_bedtime_bg"] = classification_summary(y, lr)

    oofs = {}
    for name, feats in NIGHT_SETS.items():
        oofs[name] = grouped_oof(hupa, feats, "hypo_night", night_clf)
        res["cv"][name] = classification_summary(y, oofs[name])
        res["cv"][name]["parent_sleep"] = parent_sleep_tradeoff(y, oofs[name])
    res["cv"]["rule_bedtime_bg"]["parent_sleep"] = parent_sleep_tradeoff(y, -hupa["bg_now"].to_numpy())
    res["cv"]["rule_bedtime_fingerstick"]["parent_sleep"] = parent_sleep_tradeoff(y, -hupa["fs_bg4"].to_numpy())

    # External test on T1D-UOM.
    yu = uom["hypo_night"].to_numpy()
    res["external"]["rule_bedtime_bg"] = classification_summary(yu, -uom["bg_now"].to_numpy())
    for name in ["full_twin", "fingerstick_band"]:
        m = night_clf().fit(hupa[NIGHT_SETS[name]], y)
        res["external"][name] = classification_summary(yu, m.predict_proba(uom[NIGHT_SETS[name]])[:, 1])
        joblib.dump({"model": m, "features": NIGHT_SETS[name]}, os.path.join(MODELS, f"night_{name}.joblib"))

    hupa = hupa.assign(oof_full_twin=oofs["full_twin"], oof_fingerstick_band=oofs["fingerstick_band"])
    hupa.to_parquet(os.path.join(PROC, "nights_oof.parquet"))
    return res


def rt_reg():
    return lgb.LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=31, min_child_samples=50,
                             subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1)


def rt_clf():
    return lgb.LGBMClassifier(n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=50,
                              subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1)


def evaluate_realtime(rt: pd.DataFrame) -> dict:
    hupa = rt[rt.dataset == "HUPA-UCM"].reset_index(drop=True)
    res = {"n_rows": int(len(hupa)), "forecast": {}, "low_next60": {}}
    for h in [30, 60, 120]:
        target = f"y_{h}"
        d = hupa[hupa[target].notna()].reset_index(drop=True)
        y = d[target].to_numpy()
        persist = d["g_lag0"].to_numpy()
        slope = (d["g_lag0"] - d["g_lag6"]).to_numpy() / 30.0
        linear = np.clip(persist + slope * h, 40, 400)
        out = {"persistence": regression_summary(y, persist), "linear_trend": regression_summary(y, linear)}
        for name, feats in [("glucose_only", RT_GLUCOSE_ONLY), ("full_twin", RT_FEATURES)]:
            p = grouped_oof(d, feats, target, rt_reg, kind="reg")
            out[name] = regression_summary(y, p)
            if name == "full_twin":
                out[name]["clarke"] = clarke_summary(y, p)
        out["linear_trend"]["clarke"] = clarke_summary(y, linear)
        res["forecast"][f"{h}min"] = out
        m = rt_reg().fit(d[RT_FEATURES], y)
        joblib.dump({"model": m, "features": RT_FEATURES}, os.path.join(MODELS, f"forecast_{h}.joblib"))

    uom = rt[rt.dataset == "T1D-UOM"]
    hour = hupa["time"].dt.hour
    for target in ["low_next60", "low_next120"]:
        res[target] = {}
        for scope, mask in [("all_day", hour >= 0), ("night_22_06", (hour >= 22) | (hour < 6))]:
            d = hupa[mask & hupa[target].notna() & (hupa["g_lag0"] >= 80)].reset_index(drop=True)
            y = d[target].astype(int).to_numpy()
            for name, feats in [("glucose_only", RT_GLUCOSE_ONLY), ("full_twin", RT_FEATURES)]:
                p = grouped_oof(d, feats, target, rt_clf)
                r = classification_summary(y, p)
                alarm = p >= 0.3
                r.update({"threshold": 0.3, "sensitivity": float(alarm[y == 1].mean()),
                          "precision": float(y[alarm].mean()) if alarm.any() else None})
                res[target][f"{scope}_{name}"] = r
            if scope == "all_day":
                m = rt_clf().fit(d[RT_FEATURES], y)
                joblib.dump({"model": m, "features": RT_FEATURES}, os.path.join(MODELS, f"{target}.joblib"))
                uh = uom["time"].dt.hour
                for sc, um in [("all_day", uh >= 0), ("night_22_06", (uh >= 22) | (uh < 6))]:
                    du = uom[um & uom[target].notna() & (uom["g_lag0"] >= 80)]
                    res[target][f"external_{sc}"] = classification_summary(
                        du[target].astype(int).to_numpy(), m.predict_proba(du[RT_FEATURES])[:, 1])
    return res


def main():
    os.makedirs(MODELS, exist_ok=True)
    os.makedirs(REPORTS, exist_ok=True)
    nights = pd.read_parquet(os.path.join(PROC, "nights.parquet"))
    rt = pd.read_parquet(os.path.join(PROC, "realtime.parquet"))
    results = {"night": evaluate_nights(nights), "realtime": evaluate_realtime(rt)}
    with open(os.path.join(REPORTS, "metrics.json"), "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=1)[:6000])


if __name__ == "__main__":
    main()
