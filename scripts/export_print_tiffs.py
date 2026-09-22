# -*- coding: utf-8 -*-
"""Regenerate print-resolution TIFFs (journal upload format) from figure PDFs.

The SVG/PDF vector sources are authoritative; TIFFs are derived rasters at
600 dpi and are gitignored (too large for GitHub) — rebuild locally with:

    .venv\\Scripts\\python.exe scripts\\export_print_tiffs.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "outputs" / "figures"
STEMS = ["figure1_architecture", "figure2_performance", "figure3_expert_agreement",
         "figure4_demo_case", "figure5_reasoning_trace"]

try:
    import fitz  # PyMuPDF
    HAVE_FITZ = True
except ImportError:
    HAVE_FITZ = False
from PIL import Image

import io

for stem in STEMS:
    out = FIG / f"{stem}.tiff"
    if HAVE_FITZ:
        doc = fitz.open(FIG / f"{stem}.pdf")
        pix = doc[0].get_pixmap(dpi=600)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        doc.close()
    else:
        img = Image.open(FIG / f"{stem}.png")
    img.save(out, compression="tiff_deflate")
    print(f"  {out.name}: {out.stat().st_size / 1048576:.1f} MB "
          f"({'pdf@600dpi via PIL' if HAVE_FITZ else 'png fallback'})")
print("[tiffs] done")
