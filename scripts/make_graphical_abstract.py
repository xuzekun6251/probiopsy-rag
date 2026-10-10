# -*- coding: utf-8 -*-
"""Graphical abstract for QianLieAnHui (EuOS submission).

Visual language matches figure1 v4 (muted NMI pastel, fit-to-box text).
Canvas 100 x 46.5 units at 6.33 x 2.94 in -> 1900 x 883 px @300 dpi.
Dual runtime modes: clinician decision support (main band) + patient-facing
education (violet strip), above the benchmark strip.
Outputs: outputs/submission/graphical_abstract.{png,svg,pdf}
"""
import io
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "submission"

plt.rcParams.update({
    "font.family": "Arial",
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

NAVY = "#33587A"
REGION = {"rules": ("#F0F5FD", "#7FA6DE"), "kg": ("#EBF7F2", "#6FBFA4"),
          "llm": ("#FEF7E8", "#DFAE55")}
BADGE = {"rules": "#4E80C8", "kg": "#3E9B7C", "llm": "#C99237"}
INK = "#44566B"

W_IN, H_IN = 6.33, 2.94
W_U, H_U = 100.0, 46.5

fig, ax = plt.subplots(figsize=(W_IN, H_IN))
ax.set_xlim(0, W_U)
ax.set_ylim(-6.5, H_U)
ax.axis("off")
ax.set_position([0.0, 0.0, 1.0, 1.0])

measured = []


def rbox(x, y, w, h, fc, ec, lw=0.9, rs=1.0, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0.0,rounding_size={rs}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def txt(x, y, s, fs=7.0, color="#374151", weight="normal", style="normal",
        ha="center", va="center", z=3, max_w=None, rotation=0):
    t = ax.text(x, y, s, fontsize=fs, color=color, fontweight=weight,
                fontstyle=style, ha=ha, va=va, zorder=z, rotation=rotation)
    if max_w:
        measured.append((t, max_w))
    return t


def seg(pts, color=INK, lw=1.8, ls="-", head=True, z=2, ms=13):
    for i in range(len(pts) - 2):
        ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=z)
    a, b = pts[-2], pts[-1]
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>" if head else "-",
                                 mutation_scale=ms, lw=lw, color=color,
                                 linestyle=ls, shrinkA=0, shrinkB=0, zorder=z))


def badge(x, y, n, color):
    ax.add_patch(Circle((x, y), 1.15, fc=color, ec="white", lw=0.8, zorder=4))
    txt(x, y, str(n), fs=6.6, color="white", weight="bold", z=5)


def fit_all():
    renderer = fig.canvas.get_renderer()
    x_in = W_IN / W_U
    for _ in range(5):
        worst = 1.0
        for t, mw in measured:
            bb = t.get_window_extent(renderer)
            w_u = bb.width / fig.dpi / x_in
            if w_u > mw:
                t.set_fontsize(max(4.5, t.get_fontsize() * mw / w_u * 0.985))
                worst = min(worst, mw / w_u)
            else:
                worst = min(worst, 1.0)
        if worst >= 0.999:
            break


# ── title ────────────────────────────────────────────────────────────────────
txt(50, 37.6, "QianLieAnHui — a rule-gated, knowledge-graph-grounded LLM agent "
    "for prostate biopsy decisions", fs=8.2, weight="bold", color="#1F2937",
    max_w=92)

# ── query card (left) ────────────────────────────────────────────────────────
txt(9.5, 31.0, "Query", fs=7.6, weight="bold", color="#1F2937")
rbox(1.0, 12.5, 17.0, 16.5, "white", "#9AA4B2", lw=1.0, rs=1.2)
txt(9.5, 25.6, "Patient scenario (A)", fs=7.0, max_w=15.0)
txt(9.5, 23.0, "× biopsy decision (B)", fs=7.0, max_w=15.0)
txt(9.5, 20.6, "51 scenarios × 54 items", fs=6.2, color="#6B7280", max_w=15.0)
txt(9.5, 16.6, "e.g. unifocal PI-RADS 4\nlesion, focal therapy\nplanned",
    fs=6.0, style="italic", color="#B9894C")

# ── agent panel (center) ─────────────────────────────────────────────────────
rbox(21.0, 8.0, 42.0, 27.5, "#FBFCFE", "#B9C4D2", lw=1.1, rs=1.6, z=1)
txt(42.0, 33.4, "The QianLieAnHui agent — three coupled layers", fs=7.6,
    weight="bold", color="#1F2937", max_w=40)

fc, ec = REGION["rules"]
rbox(23.0, 25.6, 32.0, 5.6, fc, ec, lw=1.1, rs=1.0, z=2)
badge(25.2, 28.4, 1, BADGE["rules"])
txt(26.8, 29.2, "Rule gate — deterministic", fs=7.0, weight="bold",
    color="#3A66A8", ha="left", max_w=26)
txt(26.8, 27.0, "12 consensus + 4 patient-factor rules → hard constraints",
    fs=6.0, color="#374151", ha="left", max_w=27)

fc, ec = REGION["kg"]
rbox(23.0, 17.2, 32.0, 5.6, fc, ec, lw=1.1, rs=1.0, z=2)
badge(25.2, 20.0, 2, BADGE["kg"])
txt(26.8, 20.8, "Risk-guided retrieval", fs=7.0, weight="bold",
    color="#2E7D62", ha="left", max_w=26)
txt(26.8, 18.6, "LightRAG KG: 1,864 entities · 3,078 relations · 357 chunks",
    fs=6.0, color="#374151", ha="left", max_w=27)

fc, ec = REGION["llm"]
rbox(23.0, 8.8, 32.0, 5.6, fc, ec, lw=1.1, rs=1.0, z=2)
badge(25.2, 11.6, 3, BADGE["llm"])
txt(26.8, 12.4, "LLM arbiter — GLM-5.3", fs=7.0, weight="bold",
    color="#A8742A", ha="left", max_w=26)
txt(26.8, 10.2, "hard-constrained five-class action + statement-level citations",
    fs=6.0, color="#374151", ha="left", max_w=27)

seg([(39.0, 25.6), (39.0, 22.8)], ms=11)
seg([(39.0, 17.2), (39.0, 14.4)], ms=11)
seg([(55.0, 28.4), (58.6, 28.4), (58.6, 11.6), (55.2, 11.6)],
    color="#5B8FF9", lw=1.4, ls=(0, (4, 2.2)), ms=11)
txt(60.1, 20.0, "constraints bind", fs=5.4, color="#5B8FF9", rotation=90,
    max_w=8)

# ── verdict card (right) ─────────────────────────────────────────────────────
txt(83.5, 31.0, "Verdict", fs=7.6, weight="bold", color="#1F2937")
rbox(66.5, 12.5, 32.5, 16.5, "white", "#4B5563", lw=1.1, rs=1.2)
rows = [("Action", "conditional", "#C08A3E", 25.6),
        ("Confidence", "0.86", "#1F2937", 22.4),
        ("Rules", "R07·PF02", "#4A7DC4", 19.2),
        ("Citations", "Q41·EV0024", "#4E9C82", 16.0)]
for lab, val, col, y in rows:
    txt(68.0, y, lab, fs=6.6, style="italic", color="#5B6B7E", ha="left",
        max_w=9.0)
    txt(97.6, y, val, fs=6.6, weight="bold", color=col, ha="right", max_w=13.0)
ax.plot([68.0, 97.6], [14.4, 14.4], color="#D8DDE4", lw=0.7, zorder=3)
txt(82.8, 13.2, "every verdict ↔ consensus statements + evidence chunks",
    fs=5.6, color="#6B7280", max_w=29.0)

# main flow arrows
seg([(18.0, 21.0), (20.8, 21.0)])
seg([(63.2, 21.0), (66.3, 21.0)])

# ── patient-education strip (second runtime mode) ───────────────────────────
rbox(1.0, 0.8, 98.0, 6.2, "#F6F2FB", "#B3A3D6", lw=1.1, rs=1.2)
txt(3.4, 6.0, "Patient-facing education mode — same evidence base · lay "
    "language · safety netting", fs=6.8, weight="bold", color="#6B4FA8",
    ha="left", max_w=48)
txt(97.6, 6.0, "second runtime mode — qualitative, not benchmarked",
    fs=5.2, color="#6B7280", ha="right", max_w=40)
edu_boxes = [
    (3.4, "Patient question\n(lay language)"),
    (27.9, "Keyword-matched\ncurated fact base"),
    (52.4, "Lay-language generation\n(same GLM, safety netting)"),
    (76.9, "Plain-language answer\n[edu-*] citations"),
]
for i, (bx, lab) in enumerate(edu_boxes):
    rbox(bx, 1.6, 21.5, 3.6, "white", "#C9BBE3", lw=0.9, rs=0.9)
    txt(bx + 10.75, 3.4, lab, fs=5.6, weight="bold", color="#6B4FA8",
        max_w=19.5)
    if i:
        seg([(bx - 3.0, 3.4), (bx, 3.4)], lw=1.3, ms=9)

# ── results strip (bottom) ───────────────────────────────────────────────────
rbox(1.0, -6.2, 98.0, 5.2, NAVY, NAVY, lw=0, rs=1.0)
txt(50, -3.1, "Benchmark: 2,240 runs (4 architectures × 5 seeds × 112 ProBIOPSY "
    "statements, generator held fixed)", fs=6.6, color="white", weight="bold",
    max_w=94)
txt(50, -5.2, "exact-5 0.805 ± 0.012 · Cohen's κ 0.730 · against-F1 0.908 "
    "(+19.2 pts vs strongest baseline) — architecture, not generator tier, "
    "is the dominant lever", fs=6.0, color="#C9D7E6", max_w=94)

fit_all()

for ext in ("png", "svg", "pdf"):
    fig.savefig(OUT / f"graphical_abstract.{ext}",
                dpi=300 if ext == "png" else None,
                bbox_inches="tight", pad_inches=0.05)
plt.close(fig)
print(f"[ga] written: {OUT / 'graphical_abstract.png'} "
      f"({(OUT / 'graphical_abstract.png').stat().st_size:,} bytes) + svg/pdf")
