# -*- coding: utf-8 -*-
"""Rebuild outputs/submission/submission_pkg.zip (writer 7_8 refresh).

Includes the revised English manuscript, supplementary material, submission
paraphernalia, and final figures (figure1/2/4/5 — figure3 stays out until the
expert panel fills its pre-registered columns). The internal review report is
deliberately excluded (internal quality gate, not for submission).
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "outputs" / "submission"
FIG = ROOT / "outputs" / "figures"

files = [
    (ROOT / "outputs" / "paper" / "manuscript.en.md", "manuscript.en.md"),
    (ROOT / "outputs" / "paper" / "manuscript.md", "manuscript_zh.md"),
    (SUB / "supplementary.md", "supplementary.md"),
    (SUB / "cover_letter.md", "cover_letter.md"),
    (SUB / "highlights.md", "highlights.md"),
    (SUB / "data_availability.md", "data_availability.md"),
    (SUB / "graphical_abstract.svg", "graphical_abstract.svg"),
    (SUB / "graphical_abstract.png", "graphical_abstract.png"),
]
for stem in ["figure1_architecture", "figure2_performance",
             "figure4_demo_case", "figure5_reasoning_trace"]:
    for ext in ["svg", "pdf", "png", "tiff"]:
        files.append((FIG / f"{stem}.{ext}", f"figures/{stem}.{ext}"))

missing = [str(p) for p, _ in files if not p.exists()]
if missing:
    raise SystemExit("MISSING: " + "; ".join(missing))

zip_path = SUB / "submission_pkg.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
    for p, arc in files:
        zf.write(p, arc)
print(f"[zip] {zip_path} ({zip_path.stat().st_size:,} bytes, {len(files)} files)")
