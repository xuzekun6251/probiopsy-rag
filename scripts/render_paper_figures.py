"""Project-specific final renderer for probiopsy-rag paper figures.

The generic contract renderer (medical-agent-writer build_figures.py) only
auto-renders forest/grouped_bar/scatter/heatmap; schematic and domain panels
come out as placeholders. This script draws Figure 1 (architecture schematic),
Figure 2 (performance), Figure 3 (expert blind-review agreement), Figure 4
(demo case + evidence corpus), and Figure 5 (reasoning-trace timings + KG
edges) from REAL project data, overwriting the placeholder outputs at
outputs/figures/figure{N}_*.{svg,pdf,png}.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    Rectangle,
)

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 7,
    "axes.linewidth": 0.8,
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})

C_RULE = "#5B8FF9"   # layer 1
C_KG = "#5AD8A6"     # layer 2
C_LLM = "#F6BD16"    # layer 3
C_METH = {"pure_llm": "#B8B8B8", "naive_rag": "#9D2933",
          "lightrag": "#5AD8A6", "probiopsy-rag": "#5B8FF9"}
C_SEV = {"high": "#dc2626", "medium": "#ea580c", "low": "#16a34a"}
ACTIONS = ["endorse", "endorse_option", "conditional", "report_option", "against"]


def _export(fig, stem: str) -> None:
    for ext in ("svg", "pdf", "png"):
        fig.savefig(FIG / f"{stem}.{ext}", bbox_inches="tight", dpi=600 if ext != "png" else 300)
    plt.close(fig)
    print(f"  {stem}: svg/pdf/png written")


# ------------------------------------------------------------------ Figure 1
# v4: graphical-abstract layout + muted NMI-pastel palette + measured
# fit-to-box text (every constrained label is width-checked against the
# renderer and auto-shrunk, so no text can overflow its box).
def fig1() -> None:
    NAVY = "#33587A"       # muted slate-navy (KB / GLM / results boxes)
    REGION = {             # tinted module regions (low-saturation NMI pastel)
        "rules": ("#F0F5FD", "#7FA6DE"),
        "kg": ("#EBF7F2", "#6FBFA4"),
        "llm": ("#FEF7E8", "#DFAE55"),
    }
    BADGE = {"rules": "#4E80C8", "kg": "#3E9B7C", "llm": "#C99237"}
    INK = "#44566B"        # softened arrow ink

    fig, ax = plt.subplots(figsize=(7.2, 4.42))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 61)
    ax.axis("off")
    ax.set_position([0.0, 0.0, 1.0, 1.0])  # axes fills figure → 1 x-unit = 0.072 in
    # (default subplot margins would make fit_all's unit math wrong by ~29%)

    measured = []  # (text artist, max_w_xunits, max_h_yunits)

    def rbox(x, y, w, h, fc, ec, lw=0.9, rs=1.2, z=1):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle=f"round,pad=0.0,rounding_size={rs}",
                                    fc=fc, ec=ec, lw=lw, zorder=z))

    def txt(x, y, s, fs=6.0, color="#374151", weight="normal", style="normal",
            ha="center", va="center", z=3, rotation=0, max_w=None, max_h=None):
        t = ax.text(x, y, s, fontsize=fs, color=color, fontweight=weight,
                    fontstyle=style, ha=ha, va=va, zorder=z, rotation=rotation)
        if max_w or max_h:
            measured.append((t, max_w, max_h))
        return t

    def seg(pts, color=INK, lw=1.8, ls="-", head=True, z=2, ms=13):
        """Polyline through pts; arrowhead on the last segment."""
        for i in range(len(pts) - 2):
            ax.plot([pts[i][0], pts[i + 1][0]], [pts[i][1], pts[i + 1][1]],
                    color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=z)
        a, b = pts[-2], pts[-1]
        ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>" if head else "-",
                                     mutation_scale=ms, lw=lw, color=color,
                                     linestyle=ls, shrinkA=0, shrinkB=0, zorder=z))

    def badge(x, y, n, color):
        ax.add_patch(Circle((x, y), 1.15, fc=color, ec="white", lw=0.8, zorder=4))
        txt(x, y, str(n), fs=6.4, color="white", weight="bold", z=5)

    def db_icon(cx, cy):
        for dy in (2.0, 0.0, -2.0):
            ax.add_patch(Ellipse((cx, cy + dy), 6.0, 1.9, fc=NAVY,
                                 ec="white", lw=0.7, zorder=3))
        ax.add_patch(Rectangle((cx - 3.0, cy - 2.0), 6.0, 4.0, fc=NAVY,
                               ec="none", zorder=2))

    def doc_icon(x, y, label):
        rbox(x - 2.0, y - 2.6, 4.0, 5.2, "white", "#7FA6DE", lw=0.7, rs=0.4, z=3)
        for dy in (1.2, 0.2, -0.8):
            ax.plot([x - 1.2, x + 1.2], [y + dy, y + dy], color="#C4D3E6",
                    lw=0.8, zorder=4)
        txt(x, y - 1.9, label, fs=4.6, color=NAVY, weight="bold", z=4)

    def fit_all():
        """Shrink any constrained text until it fits its box (measured, not guessed)."""
        import os
        renderer = fig.canvas.get_renderer()
        x_in = 7.2 / 100    # inches per x-unit
        y_in = 4.42 / 61    # inches per y-unit
        for _ in range(5):
            worst = 1.0
            for t, mw, mh in measured:
                bb = t.get_window_extent(renderer)
                scale = 1.0
                if mw:
                    w_u = bb.width / fig.dpi / x_in
                    if w_u > mw:
                        scale = min(scale, mw / w_u * 0.985)
                if mh:
                    h_u = bb.height / fig.dpi / y_in
                    if h_u > mh:
                        scale = min(scale, mh / h_u * 0.985)
                if scale < 0.999:
                    new_fs = max(3.2, t.get_fontsize() * scale)
                    t.set_fontsize(new_fs)
                    worst = min(worst, scale)
            if worst >= 0.999:
                break
        if os.environ.get("FIG1_DEBUG"):
            for t, mw, mh in measured:
                bb = t.get_window_extent(renderer)
                w_u = bb.width / fig.dpi / x_in
                h_u = bb.height / fig.dpi / y_in
                flag_w = "OVER" if (mw and w_u > mw + 0.01) else "ok"
                flag_h = "OVER" if (mh and h_u > mh + 0.01) else "ok"
                preview = t.get_text().replace("\n", "\\n")[:38]
                print(f"[fit {flag_w}/{flag_h}] fs={t.get_fontsize():.2f} "
                      f"w={w_u:.2f}/{mw} h={h_u:.2f}/{mh}  {preview}")

    # ── top band: ProBIOPSY consensus knowledge base ─────────────────────
    db_icon(5.8, 55.3)
    txt(5.2, 50.4, "ProBIOPSY consensus\nEur Urol 2026\nCC BY 4.0", fs=5.2,
        color=NAVY, weight="bold", max_w=11.5, max_h=6.5)
    rbox(13.0, 50.0, 34.5, 9.5, NAVY, NAVY, lw=0, rs=1.4)
    txt(14.5, 57.6, "Consensus-derived knowledge base", fs=6.2, color="white",
        weight="bold", ha="left", max_w=31.5)
    txt(14.5, 55.2, "• 112 statements → five-class gold standard", fs=5.6,
        color="white", ha="left", max_w=31.5)
    txt(14.5, 53.2, "• 357 evidence chunks (B: statements, C: literature)", fs=5.6,
        color="white", ha="left", max_w=31.5)
    txt(14.5, 51.2, "• LightRAG KG: 1,864 entities / 3,078 relations", fs=5.6,
        color="white", ha="left", max_w=31.5)

    # unstructured | structured callout (top right)
    rbox(64.0, 50.0, 34.0, 9.5, "#EDF4FB", "#B7CCE4", lw=0.8, rs=1.2)
    ax.plot([81.0, 81.0], [50.6, 58.9], color="#93B2D2", lw=0.8,
            linestyle=(0, (2.5, 2.5)), zorder=3)
    txt(72.5, 58.2, "Unstructured", fs=5.8, color=NAVY, weight="bold", max_w=12)
    doc_icon(72.5, 54.2, "PDF")
    txt(90.5, 58.2, "Structured", fs=5.8, color=NAVY, weight="bold", max_w=12)
    doc_icon(90.5, 54.2, "JSON")

    # KB → rules (distillation) and KB → retrieval (index build) elbows
    seg([(26.0, 50.0), (26.0, 45.7)])
    txt(27.2, 47.8, "distils 16 rules", fs=5.4, color="#5B6B7E", ha="left",
        max_w=13)
    seg([(47.5, 54.0), (59.2, 54.0), (59.2, 33.8), (54.0, 29.8)],
        color=NAVY, lw=1.4)
    txt(53.4, 52.4, "chunks → KG index", fs=5.0, color=NAVY, max_w=9.5)

    # ── query box (left) ──────────────────────────────────────────────────
    txt(9.75, 43.2, "Query", fs=7.5, weight="bold", color="#1F2937", max_w=8)
    rbox(1.5, 19.5, 16.5, 22.0, "white", "#9AA4B2", lw=1.0, rs=1.4)
    txt(9.75, 39.0, "62-year-old man, unifocal", fs=5.6, style="italic",
        color="#4B5563", max_w=14.2)
    txt(9.75, 36.5, "PI-RADS 4 lesion", fs=5.6, style="italic",
        color="#B9894C", weight="bold", max_w=14.2)
    txt(9.75, 34.0, "on 3T mpMRI,", fs=5.6, style="italic", color="#5B8DB8",
        weight="bold", max_w=14.2)
    txt(9.75, 31.5, "focal therapy planned —", fs=5.6, style="italic",
        color="#9C8FC7", weight="bold", max_w=14.2)
    txt(9.75, 29.0, "targeted + perilesional", fs=5.6, style="italic",
        color="#4B5563", max_w=14.2)
    txt(9.75, 26.5, "cores WITHOUT added", fs=5.6, style="italic",
        color="#4B5563", max_w=14.2)
    txt(9.75, 24.0, "systematic biopsy?", fs=5.6, style="italic",
        color="#4B5563", max_w=14.2)
    txt(9.75, 17.4, "51 scenarios (A) × 54 items (B)", fs=5.4, color="#6B7280",
        max_w=15.5)
    seg([(18.0, 37.0), (19.9, 37.0)], lw=1.4)
    seg([(18.0, 23.0), (19.9, 23.0)], lw=1.4)

    # ── region 1: rule engine ────────────────────────────────────────────
    fc, ec = REGION["rules"]
    rbox(20.0, 33.0, 38.0, 12.5, fc, ec, lw=1.1, rs=1.8, z=1)
    badge(22.6, 43.4, 1, BADGE["rules"])
    txt(24.4, 43.4, "Rule engine — deterministic", fs=6.8, weight="bold",
        color="#3A66A8", ha="left", max_w=32)
    rbox(22.5, 37.4, 15.5, 4.6, "white", "#A9C4E8", lw=0.8, rs=0.9)
    txt(30.25, 39.7, "12 consensus rules", fs=6.0, max_w=13.5)
    rbox(40.0, 37.4, 16.5, 4.6, "white", "#A9C4E8", lw=0.8, rs=0.9)
    txt(48.25, 39.7, "4 patient-factor rules", fs=6.0, max_w=14.5)
    rbox(22.5, 33.8, 34.0, 2.9, "#E3EDFB", "#7FA6DE", lw=0.8, rs=0.8)
    txt(39.5, 35.25, "hard constraints (Q-coded)", fs=6.0, weight="bold",
        color="#3A66A8", max_w=31)

    # ── region 2: risk-guided retrieval ──────────────────────────────────
    fc, ec = REGION["kg"]
    rbox(20.0, 15.0, 38.0, 14.6, fc, ec, lw=1.1, rs=1.8, z=1)
    badge(22.6, 28.0, 2, BADGE["kg"])
    txt(24.4, 28.0, "Risk-guided retrieval", fs=6.8, weight="bold",
        color="#2E7D62", ha="left", max_w=32)
    rbox(22.5, 22.2, 16.0, 4.6, "white", "#9CCDBB", lw=0.8, rs=0.9)
    txt(30.5, 25.3, "LightRAG KG (semantic)", fs=5.8, max_w=14)
    txt(30.5, 23.5, "1,864 entities · 3,078 rel.", fs=5.2, color="#6B7280",
        max_w=14)
    rbox(40.5, 22.2, 16.0, 4.6, "white", "#9CCDBB", lw=0.8, rs=0.9)
    txt(48.5, 25.3, "Lexical evidence store", fs=5.8, max_w=14)
    txt(48.5, 23.5, "357 chunks, entity boosts", fs=5.2, color="#6B7280",
        max_w=14)
    rbox(22.5, 15.9, 34.0, 4.4, "white", "#9CCDBB", lw=0.8, rs=0.9)
    txt(39.5, 18.1, "Context-augmented prompt (top-k)", fs=6.0, max_w=31)
    seg([(30.5, 22.2), (30.5, 20.4)], color="#4FA98B", lw=1.3, ms=8)
    seg([(48.5, 22.2), (48.5, 20.4)], color="#4FA98B", lw=1.3, ms=8)

    # ── region 3: LLM arbiter ────────────────────────────────────────────
    fc, ec = REGION["llm"]
    rbox(62.0, 15.0, 18.0, 30.5, fc, ec, lw=1.1, rs=1.8, z=1)
    badge(64.4, 43.4, 3, BADGE["llm"])
    txt(66.2, 43.4, "LLM arbiter", fs=6.8, weight="bold", color="#A8742A",
        ha="left", max_w=13)
    rbox(63.6, 35.4, 14.8, 5.6, NAVY, NAVY, lw=0, rs=1.0)
    txt(71.0, 39.4, "Pretrained GLM-5.3", fs=6.0, color="white", weight="bold",
        max_w=13.2)
    txt(71.0, 37.2, "(thinking model)", fs=5.4, color="#C9D7E6", max_w=13.2)
    rbox(63.6, 24.0, 14.8, 7.6, "white", "#E4C186", lw=0.8, rs=0.9)
    txt(71.0, 29.6, "Hard-constrained decoding", fs=5.6, max_w=13.8)
    txt(71.0, 27.7, "5-class action", fs=5.8, weight="bold", color="#A8742A",
        max_w=13.2)
    txt(71.0, 25.8, "+ statement-level citations", fs=5.2, color="#6B7280",
        max_w=13.2)
    seg([(71.0, 35.4), (71.0, 31.7)])

    # main flow: rules → retrieval, retrieval → arbiter, arbiter → output
    seg([(39.0, 33.0), (39.0, 29.8)])
    seg([(58.0, 18.1), (62.0, 18.1)])
    txt(60.05, 19.9, "top-k\nevidence", fs=4.8, color="#5B6B7E", max_w=3.6)

    # hard-constraint bypass (dashed blue): rules chip → arbiter
    seg([(56.5, 35.25), (60.3, 35.25), (60.3, 27.8), (62.0, 27.8)],
        color="#5B8FF9", lw=1.4, ls=(0, (4, 2.2)))
    txt(61.25, 31.5, "hard constraints", fs=5.0, color="#5B8FF9", rotation=90,
        max_h=7.0)

    # ── output box (right) ───────────────────────────────────────────────
    txt(91.0, 46.2, "Output", fs=7.5, weight="bold", color="#1F2937", max_w=10)
    seg([(80.0, 30.0), (83.0, 30.0)])
    rbox(83.0, 15.0, 16.0, 30.0, "white", "#4B5563", lw=1.1, rs=1.4)
    rows = [("Action", "conditional", "#C08A3E", 40.6),
            ("Confidence", "0.86", "#1F2937", 37.6),
            ("Rules", "R07·PF02", "#4A7DC4", 34.6),
            ("Citations", "Q41·EV0024", "#4E9C82", 31.6)]
    for lab, val, col, y in rows:
        txt(84.2, y, lab, fs=5.6, style="italic", color="#5B6B7E", ha="left",
            max_w=6.6)
        txt(97.8, y, val, fs=5.6, weight="bold", color=col, ha="right",
            max_w=8.6)
    ax.plot([84.2, 97.8], [29.6, 29.6], color="#D8DDE4", lw=0.7, zorder=3)
    txt(84.2, 26.8, "Rationale (excerpt)", fs=5.4, style="italic",
        color="#6B7280", ha="left", max_w=13.6)
    txt(84.2, 23.0, "Systematic add-on is\nplan-dependent (contralateral\n"
        "yield 0.3–4%); endorse TBx\n+ perilesional cores.", fs=5.2,
        style="italic", color="#4B5563", ha="left", max_w=13.6)
    txt(91.0, 16.6, "verdict ↔ Q-codes + chunks", fs=4.8, color="#6B7280",
        max_w=13.6)

    # ── bottom strip: multi-seed benchmark ───────────────────────────────
    ax.add_patch(Rectangle((2.2, 3.4), 3.2, 4.4, fc="white", ec=NAVY,
                           lw=0.9, zorder=3))
    ax.add_patch(Rectangle((3.1, 7.8), 1.4, 1.0, fc=NAVY, ec=NAVY, zorder=3))
    for dy in (6.3, 5.3, 4.3):
        ax.plot([3.0, 4.6], [dy, dy], color="#A9C4E4", lw=0.9, zorder=4)
    txt(3.8, 2.2, "gold", fs=5.0, color="#6B7280", max_w=6)
    txt(6.0, 8.2, "Multi-method benchmark", fs=6.2, weight="bold",
        color="#1F2937", ha="left", max_w=17.0)
    txt(6.0, 6.2, "112 statements × 4 methods", fs=5.2, color="#4B5563",
        ha="left", max_w=17.0)
    txt(6.0, 4.4, "× 5 seeds = 2,240 runs", fs=5.2, color="#4B5563",
        ha="left", max_w=17.0)
    seg([(24.2, 6.2), (25.6, 6.2)], ms=10)
    chips = [("rule gate", "#7FA6DE", "#4E80C8", 29.5),
             ("RAG", "#6FBFA4", "#3E9B7C", 38.5),
             ("LLM", "#DFAE55", "#C99237", 46.5)]
    for lab, border, tcol, cx in chips:
        rbox(cx - 3.6, 4.6, 7.2, 3.2, "white", border, lw=1.0, rs=0.9)
        txt(cx, 6.2, lab, fs=6.0, weight="bold", color=tcol, max_w=6.2)
    txt(38.0, 3.0, "architectures under test (generator held fixed)",
        fs=5.0, color="#6B7280", max_w=26)
    seg([(50.4, 6.2), (52.1, 6.2)], ms=10)
    rbox(52.6, 3.2, 45.4, 7.2, NAVY, NAVY, lw=0, rs=1.2)
    txt(75.3, 8.7, "exact-5 0.805 ± 0.012 · Cohen's κ 0.730 · against-F1 0.908",
        fs=6.2, color="white", weight="bold", max_w=43.0)
    txt(75.3, 6.4, "+19.2 pts exact-5 vs strongest baseline", fs=5.2,
        color="#C9D7E6", max_w=43.0)
    txt(75.3, 4.6, "architecture — not generator tier — is the dominant lever",
        fs=5.2, color="#C9D7E6", max_w=43.0)

    fit_all()
    _export(fig, "figure1_architecture")


# ------------------------------------------------------------------ Figure 2
def fig2() -> None:
    summary = json.loads((ROOT / "outputs" / "evaluation_summary.json").read_text(encoding="utf-8"))
    methods = [("pure_llm", "pure_llm"), ("naive_rag", "naive_rag"),
               ("lightrag", "LightRAG-only"), ("probiopsy-rag", "QianLieAnHui (full)")]
    metrics = [("exact5", "Exact-5\nacc"), ("exact3", "Exact-3\nacc"),
               ("macro_f1", "Macro-F1"), ("kappa", "Cohen's κ"),
               ("against_f1", "Against-F1")]

    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(7.6, 2.9), gridspec_kw={"width_ratios": [3, 1.5, 2.1]})
    # (a) grouped bars with SD error bars
    n_m, n_met = len(methods), len(metrics)
    bw = 0.8 / n_m
    for j, (mid, label) in enumerate(methods):
        agg = summary["methods"][mid]["aggregate"]
        means = [agg[k]["mean"] for k, _ in metrics]
        sds = [agg[k]["sd"] for k, _ in metrics]
        xs = [i + j * bw - 0.4 + bw / 2 for i in range(n_met)]
        ax1.bar(xs, means, bw, yerr=sds, capsize=1.6,
                color=C_METH[mid], label=label,
                error_kw={"lw": 0.7, "elinewidth": 0.7})
    ax1.set_xticks(range(n_met))
    ax1.set_xticklabels([l for _, l in metrics], fontsize=6.2)
    ax1.set_ylabel("Score (0–1)")
    ax1.set_ylim(0, 1.0)
    ax1.legend(fontsize=5.8, ncol=4, frameon=False, loc="lower center",
               bbox_to_anchor=(0.5, 1.02))
    ax1.set_title("(a) Core metrics by method (mean ± SD, 5 seeds)",
                  fontsize=7, pad=16)
    ax1.spines[["top", "right"]].set_visible(False)

    # (b) per-seed exact-5 dots + mean dash
    for j, (mid, label) in enumerate(methods):
        seeds = [s["exact5"] for s in summary["methods"][mid]["seeds"]]
        mean = summary["methods"][mid]["aggregate"]["exact5"]["mean"]
        xs = [j] * len(seeds)
        ax2.scatter([x + 0.06 for x in xs], seeds, s=9, color=C_METH[mid],
                    zorder=3, edgecolors="none")
        ax2.hlines(mean, j - 0.22, j + 0.28, color=C_METH[mid], lw=1.6, zorder=4)
    ax2.set_xticks(range(n_m))
    ax2.set_xticklabels(["pure\nLLM", "naive\nRAG", "LightRAG\nonly", "QianLie\nAnHui"], fontsize=6)
    ax2.set_ylabel("Exact-5 accuracy")
    ax2.set_ylim(0, 1.0)
    ax2.set_title("(b) Exact-5 per seed (dash = mean)", fontsize=7)
    ax2.spines[["top", "right"]].set_visible(False)

    # (c) predicted class distribution per method (counts over 560 runs),
    #     gold-standard counts overlaid as black diamonds
    import csv
    dist = {}
    with open(ROOT / "outputs" / "figures" / "source_data" /
              "figure2_pred_distribution.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            dist[row["action"]] = row
    classes = ["endorse", "endorse_option", "conditional", "report_option", "against"]
    class_lbl = ["endorse", "endorse_\noption", "conditional", "report_\noption",
                 "against"]
    n_c = len(classes)
    bw = 0.8 / n_m
    for j, (mid, label) in enumerate(methods):
        col = "probiopsy_rag" if mid == "probiopsy-rag" else mid
        counts = [int(dist[c][col]) for c in classes]
        xs = [i + j * bw - 0.4 + bw / 2 for i in range(n_c)]
        ax3.bar(xs, counts, bw, color=C_METH[mid], label=label)
    gold = [int(dist[c]["gold_standard"]) for c in classes]
    ax3.scatter(range(n_c), gold, marker="D", s=10, color="#222222", zorder=5,
                label="gold standard")
    ax3.set_xticks(range(n_c))
    ax3.set_xticklabels(class_lbl, fontsize=5.6)
    ax3.set_ylabel("Predictions (of 560 runs)")
    ax3.legend(fontsize=5.2, frameon=False, loc="upper right",
               bbox_to_anchor=(1.02, 1.04))
    ax3.set_title("(c) Predicted class distribution", fontsize=7)
    ax3.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure2_performance")


# ------------------------------------------------------------------ Figure 4
def fig4() -> None:
    import yaml
    cfg_sev, rules = {}, {}
    cfg = yaml.safe_load((ROOT / "configs" / "rules.yaml").read_text(encoding="utf-8"))
    for r in cfg.get("rules", []):
        cfg_sev[r["id"]] = r.get("severity", "unknown")
        rules[r["id"]] = r.get("risk_type", "")
    pfr = cfg.get("patient_factor_rules", {})
    for rid, r in (pfr.items() if isinstance(pfr, dict) else enumerate(pfr)):
        if isinstance(r, dict) and "id" not in r:
            r = {"id": rid, **r}
        cfg_sev[r["id"]] = r.get("severity", "unknown")
        rules.setdefault(r["id"], "patient_factor")

    cases = []
    for jp in sorted((ROOT / "outputs" / "demo_cases").glob("case*.json")):
        d = json.loads(jp.read_text(encoding="utf-8"))
        cases.append(d)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7),
                                   gridspec_kw={"width_ratios": [1, 1]})
    # (a) evidence corpus composition (stacked single bar by source_type)
    rows = [json.loads(l) for l in
            (ROOT / "data" / "seed" / "evidence_chunks.jsonl").open(encoding="utf-8") if l.strip()]
    st = Counter(r.get("source_type", "") for r in rows)
    labels = {"consensus_statement": "Consensus statements (B)",
              "literature_reference": "Literature entries (C)",
              "consensus_narrative": "Consensus narrative",
              "systematic_review_summary": "SR summaries (D)"}
    vals = [(labels.get(k, k), v) for k, v in st.most_common()]
    total = sum(v for _, v in vals)
    y = 0.0
    colors = ["#5B8FF9", "#5AD8A6", "#F6BD16", "#B8B8B8"]
    for (lab, v), c in zip(vals, colors):
        ax2.barh([0], [v], left=[y], color=c, label=f"{lab} (n={v})", height=0.5)
        if v / total > 0.08:
            ax2.text(y + v / 2, 0, str(v), ha="center", va="center", fontsize=6.5,
                     color="white", fontweight="bold")
        y += v
    ax2.set_yticks([])
    ax2.set_xlabel("Evidence chunks (n = 357)")
    ax2.legend(fontsize=5.8, frameon=False, loc="upper center",
               bbox_to_anchor=(0.5, -0.28), ncol=2)
    ax2.set_title("(b) Evidence corpus composition", fontsize=7)
    ax2.spines[["top", "right", "left"]].set_visible(False)

    # (a) demo cases: actions + rules fired count
    case_names = ["Unifocal\nscheme", "PSMA PET\nupfront", "bpMRI\nindeterminate",
                  "Advanced\ndisease", "Infection\nrisk"]
    n_rules = [len(d.get("rules_fired") or []) for d in cases]
    actions = [d["verdict"]["action"] for d in cases]
    colors_a = [C_METH["probiopsy-rag"] if a in ("endorse", "endorse_option")
                else ("#dc2626" if a == "against" else "#F6BD16") for a in actions]
    bars = ax1.bar(range(len(cases)), n_rules, color=colors_a, width=0.62)
    for i, (b, a) in enumerate(zip(bars, actions)):
        ax1.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.06, a,
                 ha="center", fontsize=5.4, rotation=28, color="#374151")
    ax1.set_xticks(range(len(cases)))
    ax1.set_xticklabels(case_names, fontsize=6)
    ax1.set_ylabel("Consensus rules fired")
    ax1.set_ylim(0, max(n_rules) + 0.9)
    ax1.set_title("(a) Demo cases: rules fired → verdict action", fontsize=7)
    ax1.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure4_demo_case")


# ------------------------------------------------------------------ Figure 5
def fig5() -> None:
    trace = list(csv.DictReader((FIG / "source_data" / "figure5_reasoning_trace.csv")
                                .open(encoding="utf-8")))
    paths = list(csv.DictReader((FIG / "source_data" / "figure5_paths.csv")
                                .open(encoding="utf-8")))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.0, 2.7),
                                   gridspec_kw={"width_ratios": [1, 1.3]})
    # (a) per-case full-pass latency, stacked rule vs remainder
    cases, rule_ms, full_ms = [], [], []
    seen = {}
    for r in trace:
        seen.setdefault(r["case_id"], {})[r["layer"]] = float(r["duration_ms"])
    for cid, layers in seen.items():
        cases.append(cid.replace("_", " "))
        rule_ms.append(layers.get("rule_engine", 0.0))
        full_ms.append(layers.get("llm_arbiter", 0.0))
    rest = [max(f - ru, 0.0) for f, ru in zip(full_ms, rule_ms)]
    y = range(len(cases))
    ax1.barh(list(y), rule_ms, color=C_RULE, label="rule engine", height=0.55)
    ax1.barh(list(y), rest, left=rule_ms, color=C_LLM,
             label="retrieval + arbitration", height=0.55)
    ax1.set_yticks(list(y))
    ax1.set_yticklabels(cases, fontsize=6)
    ax1.set_xlabel("Latency (ms, log scale)")
    ax1.set_xscale("log")
    ax1.legend(fontsize=5.8, frameon=False, loc="upper center",
               bbox_to_anchor=(0.5, -0.22), ncol=2)
    ax1.set_title("(a) Decision-pass latency per demo case", fontsize=7)
    ax1.invert_yaxis()
    ax1.spines[["top", "right"]].set_visible(False)

    # (b) top KG edge weights
    top = paths[:12]
    labels = [f"{p['source_node'][:26]} → {p['target_node'][:26]}" for p in top]
    weights = [float(p["weight"]) for p in top]
    ax2.barh(range(len(top)), weights, color=C_KG, height=0.6)
    ax2.set_yticks(range(len(top)))
    ax2.set_yticklabels(labels, fontsize=5.4)
    ax2.invert_yaxis()
    ax2.set_xlabel("Relation weight (top-12 of 3,078 edges)")
    ax2.set_title("(b) Strongest knowledge-graph relations", fontsize=7)
    ax2.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure5_reasoning_trace")


# ------------------------------------------------------------------ Figure 3
# Contract deviation (documented): per-case Fleiss κ is undefined for a single
# subject, so panel (a) shows raw agreement; the system-vs-majority confusion
# panel is dropped (n = 4 majority cases after the pre-registered 2:2-tie
# exclusion — a 5x5 matrix would be vacuous); Likert panel shows means.
C_ACT = {"endorse": "#5AD8A6", "endorse_option": "#5B8FF9",
         "conditional": "#F6BD16", "report_option": "#B8B8B8",
         "against": "#F4664A"}
ACT_ABBR = {"endorse": "End", "endorse_option": "EndO",
            "conditional": "Cond", "report_option": "RepO", "against": "Aga"}
CASE_LABELS = {
    "case1_unifocal_scheme": "C1 unifocal scheme",
    "case2_psma_pet_upfront": "C2 PSMA PET upfront",
    "case3_bpmri_indeterminate": "C3 bpMRI PI-RADS 3",
    "case4_advanced_route_prophylaxis": "C4 advanced disease",
    "case5_infection_risk_escalation": "C5 infection risk",
}


def fig3() -> None:
    stats = json.loads((ROOT / "outputs" / "tables" /
                        "expert_review_stats.json").read_text(encoding="utf-8"))
    rows = list(csv.DictReader(open(FIG / "source_data" / "figure3_expert_agreement.csv",
                                    encoding="utf-8-sig")))
    case_ids = list(CASE_LABELS)
    rating = {(r["case_id"], int(r["expert_id"])): r["expert_rating"] for r in rows}
    system = {r["case_id"]: r["system_output"] for r in rows}

    fig, (ax1, ax2, ax3) = plt.subplots(
        1, 3, figsize=(7.6, 2.6), gridspec_kw={"width_ratios": [1.2, 1.7, 1.1]})

    # (a) per-case raw agreement (of 4 experts)
    agree = []
    for c in case_ids:
        cnt = Counter(rating[(c, e)] for e in (1, 2, 3, 4))
        agree.append(cnt.most_common(1)[0][1] / 4)
    y = range(len(case_ids))
    ax1.barh(y, agree, color=C_KG, height=0.62)
    for yi, (c, a) in enumerate(zip(case_ids, agree)):
        ax1.text(a + 0.02, yi, f"{int(a * 4)}/4", va="center", fontsize=5.8)
    ax1.axvline(0.75, color="#888888", lw=0.7, ls="--")
    ax1.text(0.755, 4.45, "3/4", fontsize=5.2, color="#666666")
    ax1.set_yticks(list(y))
    ax1.set_yticklabels([CASE_LABELS[c] for c in case_ids], fontsize=5.6)
    ax1.invert_yaxis()
    ax1.set_xlim(0, 1.08)
    ax1.set_xlabel("Modal-rating share (of 4 experts)")
    fk = stats["fleiss_kappa_overall"]
    ax1.set_title(f"(a) Inter-rater agreement\n(raw 17/20; Fleiss κ {fk:.2f}*)",
                  fontsize=6.6)
    ax1.spines[["top", "right"]].set_visible(False)

    # (b) case × rater categorical matrix (experts 1-4 + system)
    col_names = ["Expert 1", "Expert 2", "Expert 3", "Expert 4", "System"]
    ax2.set_xlim(-0.5, len(col_names) - 0.5)
    ax2.set_ylim(-0.5, len(case_ids) - 0.5)
    ax2.invert_yaxis()
    for xi, cn in enumerate(col_names):
        ax2.text(xi, -0.62, cn, ha="center", fontsize=5.8,
                 weight="bold" if cn == "System" else "normal")
    for yi, c in enumerate(case_ids):
        vals = [rating[(c, e)] for e in (1, 2, 3, 4)] + [system[c]]
        for xi, a in enumerate(vals):
            ax2.add_patch(Rectangle((xi - 0.46, yi - 0.44), 0.92, 0.88,
                                        facecolor=C_ACT[a], edgecolor="white", lw=0.8))
            ax2.text(xi, yi, ACT_ABBR[a], ha="center", va="center",
                     fontsize=5.6, color="#222222")
    ax2.set_yticks(range(len(case_ids)))
    ax2.set_yticklabels([CASE_LABELS[c] for c in case_ids], fontsize=5.6)
    ax2.set_xticks([])
    for s in ax2.spines.values():
        s.set_visible(False)
    ax2.tick_params(left=False)
    handles = [Rectangle((0, 0), 1, 1, facecolor=C_ACT[a]) for a in ACTIONS]
    ax2.legend(handles, [ACT_ABBR[a] for a in ACTIONS], fontsize=5.2, ncol=5,
               frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.04))
    ax2.set_title("(b) Ratings by case and rater", fontsize=6.6, pad=10)

    # (c) Likert means (1-5)
    dims = ["clarity", "usefulness", "recommendation", "evidence"]
    means = [stats["likert_mean"][f"likert_{d}"] for d in dims]
    ax3.bar(range(len(dims)), means, color=C_LLM, width=0.6)
    for i, m in enumerate(means):
        ax3.text(i, m + 0.08, f"{m:.1f}", ha="center", fontsize=5.8)
    ax3.set_xticks(range(len(dims)))
    ax3.set_xticklabels(dims, fontsize=5.6, rotation=18)
    ax3.set_ylim(0, 5.5)
    ax3.set_ylabel("Likert score (1–5)")
    ax3.set_title("(c) Expert Likert ratings\n(uniform 5/5 — ceiling)", fontsize=6.6)
    ax3.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    _export(fig, "figure3_expert_agreement")


if __name__ == "__main__":
    print("[render] probiopsy-rag paper figures")
    fig1()
    fig2()
    fig3()
    fig4()
    fig5()
    print("[render] done")
