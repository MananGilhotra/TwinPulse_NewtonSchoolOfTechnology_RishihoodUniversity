"""Evaluation helpers: Clarke error grid and night-alarm trade-offs."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def clarke_zone(ref: float, pred: float) -> str:
    """Clarke error grid zone for one (reference, prediction) pair in mg/dL."""
    if (ref <= 70 and pred <= 70) or (0.8 * ref <= pred <= 1.2 * ref):
        return "A"
    if (ref >= 180 and pred <= 70) or (ref <= 70 and pred >= 180):
        return "E"
    if (70 <= ref <= 290 and pred >= ref + 110) or (130 <= ref <= 180 and pred <= (7 / 5) * ref - 182):
        return "C"
    if (ref >= 240 and 70 <= pred <= 180) or (ref <= 175 / 3 and 70 <= pred <= 180) or \
       (175 / 3 <= ref <= 70 and pred >= (6 / 5) * ref):
        return "D"
    return "B"


def clarke_summary(ref: np.ndarray, pred: np.ndarray) -> dict:
    zones = np.array([clarke_zone(r, p) for r, p in zip(ref, pred)])
    return {z: float((zones == z).mean()) for z in "ABCDE"}


def regression_summary(y: np.ndarray, p: np.ndarray) -> dict:
    err = p - y
    return {"rmse": float(np.sqrt(np.mean(err**2))), "mae": float(np.mean(np.abs(err)))}


def classification_summary(y: np.ndarray, s: np.ndarray) -> dict:
    return {"auroc": float(roc_auc_score(y, s)), "auprc": float(average_precision_score(y, s)),
            "prevalence": float(np.mean(y))}


def parent_sleep_tradeoff(y: np.ndarray, s: np.ndarray, targets=(0.7, 0.8, 0.9)) -> list[dict]:
    """For each target share of low nights caught, how many nights can the parent sleep through?"""
    out = []
    order = np.sort(np.unique(s))[::-1]
    for target in targets:
        for thr in order:
            alarm = s >= thr
            caught = alarm[y == 1].mean()
            if caught >= target:
                out.append({"target_caught": target, "caught": float(caught),
                            "nights_alarm": float(alarm.mean()),
                            "nights_sleep_through": float(1 - alarm.mean()),
                            "false_alarm_nights": float(alarm[y == 0].mean()),
                            "threshold": float(thr)})
                break
    return out
