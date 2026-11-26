# -*- coding: utf-8 -*-
"""Build submission-ready EN Word file (manuscript.en.docx) from manuscript.en.md.

With --bmj, also emit the BMJ Digital Health submission extras under
outputs/submission/bmj_dh/: an anonymised main document (author/affiliation
stripped, CRediT name masked) plus a separate title page — the journal
anonymises manuscripts for peer review.
"""
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "outputs" / "paper" / "manuscript.en.md"
OUT = ROOT / "outputs" / "submission" / "manuscript.en.docx"

ASCII, EA = "Times New Roman", "宋体"

CITE = re.compile(r"\[\d+(?:\s*[,–-]\s*\d+)*\]")
TOKEN = re.compile(r"(\[\d+(?:\s*[,–-]\s*\d+)*\]|<sup>.+?</sup>|\*\*.+?\*\*|`[^`]+`|\*[^*]+\*)")


def set_run(run, size=12, bold=False, sup=False):
    run.font.name = ASCII
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.superscript = sup
    rPr = run._element.get_or_add_rPr()
    rPr.get_or_add_rFonts().set(qn("w:eastAsia"), EA)


def new_doc():
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.top_margin = s.bottom_margin = Mm(25.4)
    s.left_margin = s.right_margin = Mm(31.7)
    lnnum = s._sectPr.makeelement(qn("w:lnNumType"), {qn("w:countBy"): "1", qn("w:restart"): "newPage"})
    s._sectPr.append(lnnum)
    style = d.styles["Normal"]
    style.font.name = ASCII
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), EA)
    return d


def add_inline(doc, p, text, size=12, base_bold=False):
    for tok in TOKEN.split(text):
        if not tok:
            continue
        if re.fullmatch(CITE, tok):
            # BMJ style: numbered citations as superscript, no brackets
            r = p.add_run(tok[1:-1])
            set_run(r, size=size, bold=base_bold, sup=True)
        elif tok.startswith("<sup>"):
            r = p.add_run(tok[5:-6].replace("\\*", "*"))
            set_run(r, size=size, bold=base_bold, sup=True)
        elif tok.startswith("**"):
            r = p.add_run(tok[2:-2].replace("\\*", "*"))
            set_run(r, size=size, bold=True)
        elif tok.startswith("`"):
            r = p.add_run(tok[1:-1])
            set_run(r, size=size, bold=base_bold)
        elif tok.startswith("*") and tok.endswith("*") and len(tok) > 2:
            r = p.add_run(tok[1:-1].replace("\\*", "*"))
            set_run(r, size=size, bold=base_bold)
            r.font.italic = True
        else:
            r = p.add_run(tok.replace("\\*", "*"))
            set_run(r, size=size, bold=base_bold)


def build_doc(md_text, out_path):
    text = "\n".join(ln for ln in md_text.splitlines() if not ln.strip().startswith(">"))
    doc = new_doc()

    def add_body(txt, indent=True):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = 2.0
        pf.space_before = Pt(0)
        pf.space_after = Pt(0)
        if indent:
            pf.first_line_indent = Pt(36)
        add_inline(doc, p, txt)
        return p

    def add_heading_md(txt, level):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = 1.5
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        size = {1: 15, 2: 14, 3: 12}[level]
        if level == 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_inline(doc, p, txt, size=size, base_bold=True)
        pPr = p._p.get_or_add_pPr()
        pPr.append(pPr.makeelement(qn("w:outlineLvl"), {qn("w:val"): str(level - 1)}))
        return p

    def add_table(rows):
        cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
        cells = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
        if not cells:
            return
        t = doc.add_table(rows=len(cells), cols=len(cells[0]))
        t.style = "Table Grid"
        for i, row in enumerate(cells):
            for j, val in enumerate(row):
                cell = t.cell(i, j)
                cell.text = ""
                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.15
                add_inline(doc, p, val, size=10.5, base_bold=(i == 0))
        doc.add_paragraph()

    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    current_section = ""
    for b in blocks:
        raw_lines = b.splitlines()
        if all(l.lstrip().startswith("|") for l in raw_lines if l.strip()):
            add_table(raw_lines)
            continue
        for ln in raw_lines:
            s = ln.strip()
            if not s or s == "---":
                continue
            if s.startswith("### "):
                add_heading_md(s[4:], 3)
            elif s.startswith("## "):
                current_section = s[3:]
                add_heading_md(s[3:], 2)
            elif s.startswith("# "):
                current_section = s[2:]
                add_heading_md(s[2:], 1)
            elif s.startswith("- "):
                p = doc.add_paragraph(style="List Bullet")
                p.paragraph_format.line_spacing = 2.0
                add_inline(doc, p, s[2:])
            elif current_section.lower().startswith("references") and re.match(r"^\d+\.\s", s):
                add_body(s, indent=False)
            else:
                add_body(s, indent=True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    print(f"[docx] {out_path} ({out_path.stat().st_size:,} bytes)")


def build_title_page(out_path):
    full = SRC.read_text(encoding="utf-8")
    title = full.splitlines()[0].lstrip("# ")
    tp = Document()
    s = tp.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.top_margin = s.bottom_margin = Mm(25.4)
    s.left_margin = s.right_margin = Mm(31.7)
    st = tp.styles["Normal"]
    st.font.name = ASCII
    st.font.size = Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), EA)

    def par(txt, bold=False, center=False):
        p = tp.add_paragraph()
        p.paragraph_format.line_spacing = 1.5
        if center:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(txt)
        set_run(r, size=12, bold=bold)

    par(title, bold=True, center=True)
    par("")
    par("Article type: Original research.")
    par("Running title: A hybrid rule engine–knowledge graph–LLM agent for prostate biopsy decisions.")
    par("")
    par("Author: XU Zekun")
    par("Affiliation: Department of Urology, Affiliated Jinhua Hospital, Zhejiang University School of Medicine.")
    par("Corresponding author: XU Zekun, xuzekunurology@163.com (ORCID iD to be linked at submission).")
    par("")
    par("Word counts: abstract ~335 / main text ~7,560 (excl. tables, legends, references).")
    par("Funding: this research received no external funding.")
    par("Conflicts of interest: the authors declare no conflicts of interest.")
    par("Data availability: the rule base, dual seed registries, evidence chunks, gold standard, all 2,240 raw "
        "prediction records, residual-error decomposition artefacts, and evaluation scripts are released with "
        "the code repository (see the Data availability section of the manuscript).")
    par("Declaration of generative AI and AI-assisted technologies: see the corresponding section of the manuscript.")
    par("Patient and public involvement: patients and/or the public were not involved in the design, conduct, "
        "reporting, or dissemination plans of this research (see the Patient and public involvement subsection).")
    par("Provenance and peer review: not commissioned; externally peer reviewed.")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tp.save(out_path)
    print(f"[docx] {out_path} ({out_path.stat().st_size:,} bytes)")


def main():
    text = SRC.read_text(encoding="utf-8")
    build_doc(text, OUT)

    if "--bmj" in sys.argv:
        BMJ = OUT.parent / "bmj_dh"
        BMJ.mkdir(parents=True, exist_ok=True)
        # mask the CRediT statement first (so it survives as an anonymised line),
        # then drop the author block (bare name / affiliation / correspondence lines)
        anon = text.replace("XU Zekun: Conceptualization",
                            "[Anonymised for review]: Conceptualization")
        anon = "\n".join(
            ln for ln in anon.splitlines()
            if not ln.startswith(("XU Zekun", "<sup>1</sup> Department", "<sup>\\*</sup> Corresponding"))
        )
        build_doc(anon, BMJ / "manuscript_BMJ_DH_anon.docx")
        build_title_page(BMJ / "title_page_BMJ_DH.docx")


if __name__ == "__main__":
    main()
