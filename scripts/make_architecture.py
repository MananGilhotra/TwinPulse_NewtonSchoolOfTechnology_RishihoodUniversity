"""Architecture diagram: docs/TwinPulse_Architecture.pdf (2 pages) + PNG of page 1."""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
INK, MUTED = "#0f172a", "#475569"
COL = {"data": ("#eff6ff", "#3b82f6"), "prep": ("#f5f3ff", "#7c3aed"), "model": ("#eef2ff", "#4f46e5"),
       "api": ("#ecfeff", "#0891b2"), "ui": ("#ecfdf5", "#059669"), "trust": ("#fffbeb", "#d97706")}


def box(ax, x, y, w, h, title, lines, kind, title_size=11.5, line_size=9):
    fill, edge = COL[kind]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.008,rounding_size=0.015",
                                fc=fill, ec=edge, lw=1.6))
    ax.text(x + 0.012, y + h - 0.022, title, fontsize=title_size, fontweight="bold", color=INK, va="top")
    for i, line in enumerate(lines):
        cont = line.startswith("  ")
        ax.text(x + (0.026 if cont else 0.014), y + h - 0.062 - i * 0.028, line.strip() if cont else "• " + line,
                fontsize=line_size, color=MUTED, va="top")


def arrow(ax, x1, y1, x2, y2, text=None):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=16, lw=1.6, color="#64748b"))
    if text:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.012, text, fontsize=8, color=MUTED, ha="center")


def column_label(ax, x, text):
    ax.text(x, 0.885, text, fontsize=10, color="#94a3b8", fontweight="bold", ha="left")


def page1(ax):
    ax.text(0.02, 0.965, "NightTwin (Team TwinPulse, Newton School of Technology, Rishihood University): system architecture", fontsize=18, fontweight="bold", color=INK)
    ax.text(0.02, 0.925, "Digital twin that rehearses tonight to prevent night-time hypoglycaemia in children with type 1 diabetes",
            fontsize=11, color=MUTED)
    for x, t in [(0.02, "1  DATA"), (0.215, "2  PREPARE"), (0.41, "3  MODELS"), (0.645, "4  SERVE"), (0.80, "5  USERS")]:
        column_label(ax, x, t)

    box(ax, 0.02, 0.66, 0.18, 0.21, "Static: health record", ["FHIR R4 bundle (ABDM-ready)", "Age, weight, HbA1c, Hb", "Insulin regimen, daily dose",
                                                               "Severe lows, hypo awareness", "HLA genotype, autoantibodies"], "data")
    box(ax, 0.02, 0.43, 0.18, 0.21, "Dynamic: wearables", ["CGM (5 min) or finger-pricks", "Insulin doses (pen / pump)", "Meals (carbs)",
                                                            "Band: steps, heart rate", "Sleep window"], "data")
    box(ax, 0.02, 0.18, 0.18, 0.23, "Training & validation", ["HUPA-UCM: 25 T1D, Spain", "  Libre 2 + Fitbit (CC BY 4.0)", "T1D-UOM: UK, external test",
                                                               "  CGM + Garmin (CC BY 4.0)", "Synthetic Indian cohort", "  (demo only)"], "data")

    box(ax, 0.215, 0.58, 0.18, 0.29, "Personalisation", ["Fit twin on child's past nights", "Least squares, 5 parameters", "Insulin sensitivity anchored",
                                                         "  to the 1800 rule", "Refit as new nights arrive", "Assimilate today's readings"], "prep")
    box(ax, 0.215, 0.18, 0.18, 0.37, "Ingestion & features", ["Unified 5-minute timeline", "mg/dL, U, g; time-aligned", "Insulin on board (exp. model)",
                                                              "Carbs on board", "Unlogged meals: 500 rule", "Glucose lags, slopes, SD",
                                                              "Heart-rate deviation", "Events: <70 mg/dL for 15 min"], "prep")

    box(ax, 0.41, 0.58, 0.22, 0.29, "A · Physiology twin", ["Bergman glucose–insulin model", "SC rapid + NPH / glargine depots", "Gut absorption, exercise effect",
                                                            "500-member night ensemble", "→ P(low), time, depth", "What-if: snack, dose, NPH timing",
                                                            "Counterfactual explanations"], "model")
    box(ax, 0.41, 0.33, 0.22, 0.22, "B · Night guard (LightGBM)", ["Low within 60 / 120 min", "Glucose at +30 / 60 / 120 min", "15-min smoothing, alert threshold",
                                                                   "Patient-held-out + external test", "97% of night lows warned ≥15 min"], "model")
    box(ax, 0.41, 0.18, 0.22, 0.12, "C · Sensor priority", ["Week-1 trial-sensor ranking", "Spearman 0.63 on 29 patients"], "model")

    box(ax, 0.645, 0.18, 0.14, 0.69, "FastAPI service", ["GET /api/board", "GET /api/patients/{id}", "POST …/whatif", "GET /api/validation",
                                                          "Twin cache per child", "Serves dashboard", "One command: ./run.sh"], "api")
    box(ax, 0.80, 0.55, 0.18, 0.32, "Doctor dashboard", ["Overview", "Tonight Board (9 PM)", "Twin view + why", "Rehearse a plan → approve",
                                                         "Night guard replay", "Sensor Priority", "Evidence"], "ui", line_size=9)
    box(ax, 0.80, 0.18, 0.18, 0.34, "Family channel", ["WhatsApp / voice call", "Kannada, Hindi, Malayalam…", "Works on feature phones",
                                                       "Only doctor-approved actions", "Night alert ~1 h before a low"], "ui")

    box(ax, 0.02, 0.035, 0.96, 0.11, "Trust layer", [], "trust")
    ax.text(0.03, 0.075, "DPDP Act 2023 s.9: verifiable parental consent · clinic is the data fiduciary (Rules 2025, Sch. IV health exemption) · no ads / analytics on children's data"
            "\nDoctor-in-the-loop decision support · FHIR R4 / ABHA-ready · patient-held-out + external validation · honest limits published · Apache-2.0",
            fontsize=9, color=MUTED, va="center")

    arrow(ax, 0.20, 0.765, 0.215, 0.765)
    arrow(ax, 0.20, 0.50, 0.215, 0.50)
    arrow(ax, 0.20, 0.29, 0.215, 0.29)
    arrow(ax, 0.305, 0.55, 0.305, 0.58)
    arrow(ax, 0.395, 0.725, 0.41, 0.725)
    arrow(ax, 0.395, 0.44, 0.41, 0.44)
    arrow(ax, 0.395, 0.24, 0.41, 0.24)
    arrow(ax, 0.63, 0.725, 0.645, 0.725)
    arrow(ax, 0.63, 0.44, 0.645, 0.44)
    arrow(ax, 0.63, 0.24, 0.645, 0.24)
    arrow(ax, 0.785, 0.71, 0.80, 0.71)
    arrow(ax, 0.785, 0.35, 0.80, 0.35)


def page2(ax):
    ax.text(0.02, 0.965, "One night with NightTwin", fontsize=18, fontweight="bold", color=INK)
    ax.text(0.02, 0.925, "What happens, when, and who sees it", fontsize=11, color=MUTED)
    steps = [
        ("All day", "Data arrives", "CGM or finger-pricks, insulin doses, meals, steps and heart rate stream into the child's 5-minute timeline.", "data"),
        ("21:00", "Twin rehearses tonight", "Each child's twin is refitted on past nights, assimilates today's readings, and lives 23:00–07:30 500 times.", "model"),
        ("21:00", "Tonight Board", "The clinic sees every child ranked by P(low). The diabetes educator calls the red rows before bed.", "ui"),
        ("21:15", "Doctor rehearses a fix", "Bedtime snack, smaller dinner dose, or NPH at bedtime: the twin re-lives the night with each plan.", "model"),
        ("21:30", "Plan approved and sent", "The family receives only the approved action, in their language, by WhatsApp or voice call.", "ui"),
        ("23:00–07:00", "Night guard (CGM)", "Every 5 minutes: P(low within 2 h). Above threshold → voice call to the parent, median 65 min before the low.", "model"),
        ("Morning", "Learn", "The night's real data refits the twin. Over 14 days the trial sensor ranks who needs a CGM most.", "prep"),
    ]
    y = 0.84
    for t, title, text, kind in steps:
        fill, edge = COL[kind]
        ax.add_patch(FancyBboxPatch((0.03, y - 0.075), 0.94, 0.085, boxstyle="round,pad=0.006,rounding_size=0.012", fc=fill, ec=edge, lw=1.4))
        ax.text(0.045, y - 0.03, t, fontsize=12, fontweight="bold", color=edge, va="center")
        ax.text(0.19, y - 0.012, title, fontsize=12, fontweight="bold", color=INK, va="center")
        ax.text(0.19, y - 0.048, text, fontsize=10, color=MUTED, va="center")
        y -= 0.108


def main():
    os.makedirs(DOCS, exist_ok=True)
    pdf_path = os.path.join(DOCS, "TwinPulse_Architecture.pdf")
    with PdfPages(pdf_path) as pdf:
        for draw, png in [(page1, "architecture.png"), (page2, "night_flow.png")]:
            fig = plt.figure(figsize=(16.5, 9.3))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis("off")
            draw(ax)
            pdf.savefig(fig)
            fig.savefig(os.path.join(DOCS, "figures", png), dpi=150, facecolor="white")
            plt.close(fig)
    print(pdf_path)


if __name__ == "__main__":
    main()
