"""Figures for the README, deck and video (docs/figures/*.png)."""
from __future__ import annotations

import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from twinpulse import service  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "figures")
INK, MUTED, BRAND, GOOD, BAD, WARN = "#111827", "#6b7280", "#4f46e5", "#059669", "#dc2626", "#d97706"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.edgecolor": "#d1d5db", "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "figure.dpi": 160})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight", facecolor="white")
    plt.close(fig)


def guard_events(extra):
    ge = extra["guard_events"]
    labels = ["Night lows warned\n≥15 min ahead", "Median warning\n(minutes)", "False alarms\nper night"]
    u, e = ge["unseen_patients"]["0.2"], ge["external"]["0.2"]
    vals_u = [u["caught_15min_ahead"] * 100, u["median_warning_min"], u["false_alarms_per_night"]]
    vals_e = [e["caught_15min_ahead"] * 100, e["median_warning_min"], e["false_alarms_per_night"]]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
    fmt = ["{:.0f}%", "{:.0f} min", "{:.2f}"]
    for ax, lab, a, b, f in zip(axes, labels, vals_u, vals_e, fmt):
        bars = ax.bar(["Unseen\npatients", "External\n(UK)"], [a, b], color=[BRAND, "#a5b4fc"], width=0.6)
        for bar, v in zip(bars, [a, b]):
            ax.text(bar.get_x() + bar.get_width() / 2, v, f.format(v), ha="center", va="bottom", fontsize=13, fontweight="bold")
        ax.set_title(lab, fontsize=12, pad=22)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
    fig.suptitle(f"Night guard on real patients ({u['night_lows']} + {e['night_lows']} night-time lows)", fontweight="bold")
    save(fig, "guard_events.png")


def forecast(metrics):
    fc = metrics["realtime"]["forecast"]
    hs = ["30min", "60min", "120min"]
    series = [("Assume no change", "persistence", "#d1d5db"), ("Extend the trend", "linear_trend", "#9ca3af"),
              ("TwinPulse", "full_twin", BRAND)]
    x = np.arange(len(hs))
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, (lab, key, col) in enumerate(series):
        v = [fc[h][key]["rmse"] for h in hs]
        ax.bar(x + (i - 1) * 0.26, v, 0.26, label=lab, color=col)
        for xi, vi in zip(x + (i - 1) * 0.26, v):
            ax.text(xi, vi + 1, f"{vi:.0f}", ha="center", fontsize=10)
    ax.set_xticks(x, ["30 min", "60 min", "2 hours"])
    ax.set_ylabel("Forecast error, RMSE (mg/dL)")
    ax.set_title("Glucose forecast error on unseen patients (lower is better)", fontweight="bold")
    ax.legend(frameon=False)
    save(fig, "forecast_rmse.png")


def honest(metrics, extra):
    n = metrics["night"]
    rows = [("Night guard: low within 60 min", metrics["realtime"]["low_next60"]["night_22_06_full_twin"]["auroc"], GOOD),
            ("Night guard: low within 2 h", metrics["realtime"]["low_next120"]["night_22_06_full_twin"]["auroc"], GOOD),
            ("Bedtime: glucose rule", n["cv"]["rule_bedtime_bg"]["auroc"], WARN),
            ("Bedtime: ML, all signals", n["cv"]["full_twin"]["auroc"], WARN),
            ("Bedtime: physiology twin", extra["twin_bedtime"]["HUPA-UCM"]["twin_auroc"], WARN),
            ("Bedtime: finger-prick + band", n["cv"]["fingerstick_band"]["auroc"], WARN)]
    fig, ax = plt.subplots(figsize=(8.5, 4))
    y = np.arange(len(rows))[::-1]
    ax.barh(y, [r[1] - 0.5 for r in rows], left=0.5, color=[r[2] for r in rows], height=0.6)
    for yi, r in zip(y, rows):
        ax.text(r[1] + 0.01, yi, f"{r[1]:.2f}", va="center", fontsize=11)
    ax.set_yticks(y, [r[0] for r in rows])
    ax.axvline(0.5, color=MUTED, lw=1, ls="--")
    ax.text(0.505, len(rows) - 0.45, "coin toss", color=MUTED, fontsize=9)
    ax.set_xlim(0.45, 1.0)
    ax.set_xlabel("AUROC on unseen patients")
    ax.set_title("What works, and what doesn't (real patients)", fontweight="bold")
    save(fig, "what_works.png")


def sensor(extra):
    t = extra["sensor_ranking"]["table"]
    x = [r["week1_tbr"] * 100 for r in t]
    y = [r["later_night_low_rate"] * 100 for r in t]
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    ax.scatter(x, y, s=60, color=BRAND, alpha=0.8)
    ax.set_xlabel("Week 1 on a trial sensor: % time below 70 mg/dL")
    ax.set_ylabel("Later: % of nights with a low")
    sr = extra["sensor_ranking"]
    ax.set_title(f"One trial sensor ranks who needs CGM most\nSpearman {sr['spearman_week1_tbr_vs_later']:.2f}, "
                 f"{sr['patients']} real patients", fontweight="bold", fontsize=12)
    save(fig, "sensor_ranking.png")


def tonight_fan():
    pid = "TP-001"
    t = service.tonight(pid)
    w = service.whatif(pid, snack_g=15, long_acting_shift_min=90)
    band, alt = t["band"], w["band"]
    xs = np.arange(len(band))
    labels = [b["t"][11:16] for b in band]
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.axhspan(70, 180, color="#ecfdf5")
    ax.fill_between(xs, [b["p5"] for b in band], [b["p95"] for b in band], color=BRAND, alpha=0.12, lw=0)
    ax.fill_between(xs, [b["p25"] for b in band], [b["p75"] for b in band], color=BRAND, alpha=0.25, lw=0)
    ax.plot(xs, [b["p50"] for b in band], color=BRAND, lw=2, label=f"As planned: {t['risk']['p_low']:.0%} of nights go low")
    ax.fill_between(xs, [b["p5"] for b in alt], [b["p95"] for b in alt], color=GOOD, alpha=0.15, lw=0)
    ax.plot(xs, [b["p50"] for b in alt], color=GOOD, lw=2.5,
            label=f"Bedtime snack + NPH 90 min later: {w['risk']['p_low']:.0%}")
    ax.axhline(70, color=BAD, ls="--", lw=1)
    ticks = xs[::18]
    ax.set_xticks(ticks, [labels[i] for i in ticks])
    ax.set_ylim(40, 260)
    ax.set_ylabel("Glucose (mg/dL)")
    ax.set_title("Ananya (synthetic), tonight lived 500 times on her twin", fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    save(fig, "tonight_rehearsal.png")


def guard_replay():
    g = service.night_guard("TP-002")
    s = g["series"]
    xs = np.arange(len(s))
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axhspan(70, 180, color="#ecfdf5")
    ax.plot(xs, [r["cgm"] for r in s], color=INK, lw=2, label="CGM glucose")
    ax.axhline(70, color=BAD, ls="--", lw=1)
    ax2 = ax.twinx()
    ax2.fill_between(xs, [r["p120"] for r in s], color=BAD, alpha=0.15)
    ax2.plot(xs, [r["p120"] for r in s], color=BAD, lw=1, label="risk of a low within 2 h")
    ax2.set_ylim(0, 1)
    ax2.set_ylabel("Risk", color=BAD)
    lab = [r["t"][11:16] for r in s]
    ia = lab.index(g["first_alert"])
    io = lab.index(g["low_onset"])
    ax.axvline(ia, color=BAD, lw=2)
    ax.text(ia + 1, 235, f"Parent called {g['first_alert']}", color=BAD, fontweight="bold")
    ax.axvline(io, color=INK, ls=":", lw=1.5)
    ax.text(io + 1, 215, f"Low begins {g['low_onset']}", color=INK)
    ticks = xs[::12]
    ax.set_xticks(ticks, [lab[i] for i in ticks])
    ax.set_ylim(40, 250)
    ax.set_ylabel("Glucose (mg/dL)")
    ax.set_title(f"Arjun (synthetic): night guard gives {g['lead_min']} minutes of warning", fontweight="bold")
    save(fig, "guard_replay.png")


def main():
    os.makedirs(OUT, exist_ok=True)
    metrics = json.load(open(os.path.join(ROOT, "reports", "metrics.json")))
    extra = json.load(open(os.path.join(ROOT, "reports", "metrics_extra.json")))
    guard_events(extra)
    forecast(metrics)
    honest(metrics, extra)
    sensor(extra)
    tonight_fan()
    guard_replay()
    print(sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
