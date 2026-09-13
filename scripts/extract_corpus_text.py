# -*- coding: utf-8 -*-
"""Extract full text from ProBIOPSY PDFs into data/raw/ for registry building."""
import io
import sys
from pypdf import PdfReader

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

JOBS = [
    ("data/raw/ProBIOPSY_consensus_main.pdf", "data/raw/ProBIOPSY_consensus_main.txt"),
    ("data/raw/ProBIOPSY_mmc1_supplementary.pdf", "data/raw/ProBIOPSY_mmc1_supplementary.txt"),
]

for src, dst in JOBS:
    reader = PdfReader(src)
    parts = []
    for i, page in enumerate(reader.pages):
        parts.append(f"\n===== PAGE {i + 1} =====\n")
        parts.append(page.extract_text() or "")
    text = "".join(parts)
    io.open(dst, "w", encoding="utf-8").write(text)
    print(f"[ok] {src} -> {dst}: {len(reader.pages)} pages, {len(text)} chars")
