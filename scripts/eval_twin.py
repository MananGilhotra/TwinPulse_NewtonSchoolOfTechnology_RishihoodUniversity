"""Walk-forward test of the physiology twin on real nights.

For every night (after a patient's first 5), fit the twin on that patient's previous
nights only (up to 14), live tonight 300 times, and record P(low). Refit every 7 nights.
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse.data import load_all  # noqa: E402
from twinpulse.twin import estimate_ib, estimate_tdd, fit_twin, night_risk, night_window  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_PRIOR, MAX_PRIOR, REFIT_EVERY = 5, 14, 7


def main(datasets=("HUPA-UCM", "T1D-UOM")):
    df = load_all()
    nights = pd.read_parquet(os.path.join(ROOT, "data", "processed", "nights.parquet"))
    rows = []
    t0 = time.time()
    for (dataset, patient), d in df[df.dataset.isin(datasets)].groupby(["dataset", "patient"], sort=False):
        d = d.set_index("time").sort_index()
        ib = estimate_ib(d)
        tdd = estimate_tdd(d)
        pn = nights[nights.patient == patient].sort_values("date")
        windows = {}
        for date in pn["date"]:
            w = night_window(d, pd.Timestamp(date), tdd=tdd)
            if w is not None:
                windows[date] = w
        dates = [x for x in pn["date"] if x in windows]
        twin = None
        for i, date in enumerate(dates):
            if i < MIN_PRIOR:
                continue
            if twin is None or (i - MIN_PRIOR) % REFIT_EVERY == 0:
                twin = fit_twin([windows[x] for x in dates[max(0, i - MAX_PRIOR):i]], ib, tdd=tdd)
            w = windows[date]
            risk = night_risk(twin.run(w, n=300, seed=i), w)
            rows.append({"dataset": dataset, "patient": patient, "date": date, "twin_p_low": risk["p_low"],
                         "twin_median_min": risk["median_min"], "twin_fit_rmse": twin.fit_rmse})
        print(f"{patient}: {len(dates)} nights, {time.time() - t0:.0f}s", flush=True)
    out = pd.DataFrame(rows).merge(nights[["patient", "date", "hypo_night", "bg_now"]], on=["patient", "date"])
    out.to_parquet(os.path.join(ROOT, "data", "processed", "twin_walkforward.parquet"))
    for ds, g in out.groupby("dataset"):
        print(ds, "nights", len(g), "twin AUROC", round(roc_auc_score(g.hypo_night, g.twin_p_low), 3),
              "bedtime-BG rule AUROC", round(roc_auc_score(g.hypo_night, -g.bg_now), 3))


if __name__ == "__main__":
    main()
