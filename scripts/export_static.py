"""Export everything the dashboard needs as static JSON, so it runs without a server (GitHub Pages).

The what-if rehearsal still runs live: each child's fitted twin (parameters + tonight's inputs) is
exported and the browser re-simulates the night (dashboard/src/twin.js).
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse import service  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "dashboard", "public", "data")


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [clean(v) for v in x]
    if isinstance(x, np.ndarray):
        return clean(x.tolist())
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else round(float(x), 5)
    if isinstance(x, np.integer):
        return int(x)
    return x


def dump(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(clean(obj), f, separators=(",", ":"))


def main():
    dump(os.path.join(OUT, "board.json"), {"tonight": service.TONIGHT.strftime("%Y-%m-%d"), "patients": service.board()})
    dump(os.path.join(OUT, "validation.json"), service.validation())
    for pid in service.cohort_meta():
        p = service.patient(pid)
        twin = service.patient_twin(pid)
        w = service.tonight_window(pid)
        p["twin_input"] = {
            "start": w.times[0].strftime("%Y-%m-%dT%H:%M"), "nudge_until": int(w.nudge_until),
            "bolus": w.bolus, "basal": w.basal, "inj": w.inj, "carbs": w.carbs, "steps": w.steps, "glucose": w.glucose,
            "params": twin.params, "ib": twin.ib, "tau_l": twin.tau_l, "noise_sd": twin.noise_sd,
        }
        dump(os.path.join(OUT, "patients", f"{pid}.json"), p)
    print("exported to", OUT)


if __name__ == "__main__":
    main()
