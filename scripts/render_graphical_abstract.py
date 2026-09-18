"""Graphical abstract: three-layer architecture + headline benchmark result."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "submission"

plt.rcParams.update({"font.family": "Arial", "svg.fonttype": "none", "pdf.fonttype": 42})
C_RULE, C_KG, C_LLM = "#5B8FF9", "#5AD8A6", "#F6BD16"

fig, (ax, axr) = plt.subplots(1, 2, figsize=(6.3, 2.8),
                              gridspec_kw={"width_ratios": [1.25, 1]})
ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
axr.set_xlim(0, 100); axr.set_ylim(0, 100); axr.axis("off")


def box(a, x, y, w, h, text, fc, ec, fs=6.6, weight="normal"):
    a.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6",
                               fc=fc, ec=ec, lw=0.9))
    a.text(x + w / 2, y + h / 2, text, ha="center", va="center",
           fontsize=fs, fontweight=weight)


def arrow(a, x1, y1, x2, y2, **kw):
    a.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                mutation_scale=8, lw=0.9, color="#4B5563", **kw))


# left: architecture
box(ax, 0, 38, 24, 26, "Patient\nscenario ×\ndecision item\n(51 × 54)", "#F3F4F6", "#9CA3AF", 5.8)
box(ax, 34, 74, 64, 18, "1 · Rule engine\n16 deterministic rules → hard constraints",
    "#EFF6FF", C_RULE, 6.2)
box(ax, 34, 46, 64, 18, "2 · LightRAG retrieval\n357 chunks · 1,864 entities · 3,078 relations",
    "#ECFDF5", C_KG, 6.2)
box(ax, 34, 18, 64, 18, "3 · LLM arbiter (GLM-5.3)\n5-class verdict + Q-code citations",
    "#FFFBEB", C_LLM, 6.2)
arrow(ax, 24, 51, 34, 82)
arrow(ax, 66, 74, 66, 64)
arrow(ax, 66, 46, 66, 36)
ax.text(66, 6, "endorse · endorse_option · conditional · report_option · against",
        ha="center", fontsize=5.8, color="#374151")

# right: headline result
axr.text(50, 93, "ProBIOPSY gold standard: 112 statements × 5 seeds", ha="center",
         fontsize=6.6, color="#111827", fontweight="bold")
methods = [("pure LLM", 0.304, "#B8B8B8"), ("naive RAG", 0.605, "#9D2933"),
           ("LightRAG only", 0.613, "#5AD8A6"), ("QianLieAnHui", 0.805, "#5B8FF9")]
y = 72
for name, v, c in methods:
    axr.barh([y], [v * 100], color=c, height=7.5)
    axr.text(v * 100 + 1.5, y, f"{v:.3f}", va="center", fontsize=6.4)
    axr.text(-1.5, y, name, va="center", ha="right", fontsize=6.4)
    y -= 17
axr.set_xlim(-30, 105)
axr.axis("off")
axr.text(50, 8.5, "exact-5 accuracy (κ 0.730 vs 0.525 best baseline)", ha="center",
         fontsize=6.2, color="#374151")
axr.set_title("Benchmark result", fontsize=7.5, pad=2)

fig.tight_layout()
for ext in ("svg", "png"):
    fig.savefig(OUT / f"graphical_abstract.{ext}", dpi=300, bbox_inches="tight")
print("graphical_abstract.svg/png written")
