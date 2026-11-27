# -*- coding: utf-8 -*-
"""Assemble the JAMIA submission folder: outputs/submission/JAMIA投稿文件/.

Contents (ScholarOne upload set):
  manuscript_JAMIA.docx            main document (rebuilt fresh from manuscript.jamia.md)
  cover_letter_JAMIA.docx          rendered from cover_letter_JAMIA.md
  supplementary_material_S1-S7.docx  rendered from outputs/submission/supplementary.md
  figure1..figure5 .tiff           600-dpi print TIFFs copied from outputs/figures/
  DECIDE-AI_checklist.docx         copied from outputs/submission/bmj_dh/
  00_README_投稿清单.md            local upload mapping (not for upload)

TIFFs are gitignored (too large for GitHub); the committed folder holds the
docx set and this script. Rebuild everything with:
    .venv\\Scripts\\python.exe scripts\\build_jamia_docx.py
    .venv\\Scripts\\python.exe scripts\\build_jamia_pkg.py
"""
import re
import shutil
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Mm, Pt

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_jamia_docx import CITE, TOKEN, add_inline, set_run  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "outputs" / "submission"
PKG = SUB / "JAMIA投稿文件"
FIG = ROOT / "outputs" / "figures"
ASCII, EA = "Times New Roman", "宋体"


def new_doc_plain():
    """A4 document without line numbers (letters / supplementary)."""
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Mm(210), Mm(297)
    s.top_margin = s.bottom_margin = Mm(25.4)
    s.left_margin = s.right_margin = Mm(31.7)
    style = d.styles["Normal"]
    style.font.name = ASCII
    style.font.size = Pt(12)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), EA)
    return d


def add_table(doc, rows, cell_size=10.0):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r":?-{2,}:?", c) for c in r)]
    if not cells:
        return
    t = doc.add_table(rows=len(cells), cols=len(cells[0]))
    # publication three-line style
    tbl_pr = t._tbl.tblPr
    borders = tbl_pr.makeelement(qn("w:tblBorders"), {})
    for tag, val, sz in (("top", "single", "12"), ("left", "none", "0"),
                         ("bottom", "single", "12"), ("right", "none", "0"),
                         ("insideH", "none", "0"), ("insideV", "none", "0")):
        borders.append(borders.makeelement(
            qn(f"w:{tag}"), {qn("w:val"): val, qn("w:sz"): sz,
                             qn("w:color"): "000000", qn("w:space"): "0"}))
    look = tbl_pr.find(qn("w:tblLook"))
    if look is not None:
        look.addprevious(borders)
    else:
        tbl_pr.append(borders)
    for cell in t.rows[0].cells:
        tc_pr = cell._tc.get_or_add_tcPr()
        tc_borders = tc_pr.makeelement(qn("w:tcBorders"), {})
        tc_borders.append(tc_borders.makeelement(
            qn("w:bottom"), {qn("w:val"): "single", qn("w:sz"): "6",
                             qn("w:color"): "000000", qn("w:space"): "0"}))
        tc_pr.append(tc_borders)
    row_pr = t.rows[0]._tr.get_or_add_trPr()
    row_pr.append(row_pr.makeelement(qn("w:cantSplit"), {qn("w:val"): "true"}))
    row_pr.append(row_pr.makeelement(qn("w:tblHeader"), {qn("w:val"): "true"}))
    for row in t.rows[1:]:
        row_pr = row._tr.get_or_add_trPr()
        row_pr.append(row_pr.makeelement(qn("w:cantSplit"), {qn("w:val"): "true"}))
    for i, row in enumerate(cells):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.1
            add_inline(doc, p, val, size=cell_size, base_bold=(i == 0))
    doc.add_paragraph()


def render_md(md_text, out_path, *, size=12, spacing=1.5, heading_sizes=(14, 12, 11),
              first_h1_centered=True, cell_size=10.0):
    """Generic md -> docx renderer (headings, paragraphs, bullets, tables)."""
    text = "\n".join(ln for ln in md_text.splitlines() if not ln.strip().startswith(">"))
    doc = new_doc_plain()
    seen_h1 = False

    def para(txt, indent=False):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = spacing
        pf.space_after = Pt(6)
        if indent:
            pf.first_line_indent = Pt(24)
        add_inline(doc, p, txt, size=size)
        return p

    def heading(txt, level):
        nonlocal seen_h1
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.line_spacing = 1.3
        pf.space_before = Pt(12 if level == 1 else 10)
        pf.space_after = Pt(4)
        if level == 1 and first_h1_centered and not seen_h1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        seen_h1 = True
        add_inline(doc, p, txt, size=heading_sizes[level - 1], base_bold=True)
        pPr = p._p.get_or_add_pPr()
        pPr.append(pPr.makeelement(qn("w:outlineLvl"), {qn("w:val"): str(level - 1)}))

    blocks = [b for b in re.split(r"\n\s*\n", text) if b.strip()]
    for b in blocks:
        raw_lines = b.splitlines()
        if all(l.lstrip().startswith("|") for l in raw_lines if l.strip()):
            add_table(doc, raw_lines, cell_size=cell_size)
            continue
        for ln in raw_lines:
            s = ln.strip()
            if not s or s == "---":
                continue
            if s.startswith("### "):
                heading(s[4:], 3)
            elif s.startswith("## "):
                heading(s[3:], 2)
            elif s.startswith("# "):
                heading(s[2:], 1)
            elif s.startswith("- "):
                p = doc.add_paragraph(style="List Bullet")
                p.paragraph_format.line_spacing = spacing
                add_inline(doc, p, s[2:], size=size)
            else:
                para(s)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    print(f"[docx] {out_path} ({out_path.stat().st_size:,} bytes)")


README = """# JAMIA 投稿文件清单（本文件仅本地参考，不上传）

投稿系统：ScholarOne（mc.manuscriptcentral.com/jamia）· Article type: **Research and Applications** · 单盲评审（作者信息在正文内，无需匿名稿）。

| 文件 | ScholarOne 上传位置 | 说明 |
|---|---|---|
| manuscript_JAMIA.docx | Main Document | 正文（含标题页、摘要五段式 249 词、正文 3,987 词、4 张三线表、图注、58 条参考文献） |
| cover_letter_JAMIA.docx | Cover Letter | 投稿信；系统若只收文本，可从 cover_letter_JAMIA.md 复制粘贴 |
| supplementary_material_S1-S7.docx | Supplementary Material (File 1) | S1 混淆矩阵 / S2 旗舰档 / S3 演示病例 / S4 运行耗时 / S5 仲裁提示词 / S6 专家盲评 / S7 患者教育逐字稿 |
| figure1_architecture.tiff | Figures | 600 dpi |
| figure2_performance.tiff | Figures | 600 dpi（2026-11-27 修复 B 面板标注重叠后的最新版） |
| figure3_expert_agreement.tiff | Figures | 600 dpi |
| figure4_demo_case.tiff | Figures | 600 dpi |
| figure5_reasoning_trace.tiff | Figures | 600 dpi |
| DECIDE-AI_checklist.docx | Reporting checklist（如系统设有该项） | 完成的 DECIDE-AI 报告规范检查单 |

## 投稿前检查

1. 表单逐项填写：Funding = none；Competing interests = none；Data availability（稿内已有，GitHub + Zenodo）。
2. ORCID 关联通讯作者；作者信息核对（XU Zekun, xuzekunurology@163.com）。
3. 参考文献 [22]（EAU 活页指南）的访问日期更新为投稿当日。
4. 矢量图源（SVG/PDF）在 outputs/figures/，编辑部若要求可补交。
5. 重建本文件夹：先跑 scripts/build_jamia_docx.py，再跑 scripts/build_jamia_pkg.py。
"""


def main():
    import build_jamia_docx  # rebuild the main manuscript fresh

    build_jamia_docx.main()

    PKG.mkdir(parents=True, exist_ok=True)

    # main manuscript + cover letter + supplementary + checklist
    shutil.copy2(build_jamia_docx.OUT, PKG / "manuscript_JAMIA.docx")
    render_md((SUB / "jamia" / "cover_letter_JAMIA.md").read_text(encoding="utf-8"),
              PKG / "cover_letter_JAMIA.docx", size=12, spacing=1.5,
              heading_sizes=(14, 12, 11), first_h1_centered=False)
    render_md((SUB / "supplementary.md").read_text(encoding="utf-8"),
              PKG / "supplementary_material_S1-S7.docx", size=11, spacing=1.15,
              heading_sizes=(14, 12, 11), cell_size=9.5)
    src_checklist = SUB / "bmj_dh" / "DECIDE-AI_checklist_BMJ_DH.docx"
    if src_checklist.exists():
        shutil.copy2(src_checklist, PKG / "DECIDE-AI_checklist.docx")
        print(f"[copy] {src_checklist.name} -> DECIDE-AI_checklist.docx")

    # 600-dpi print TIFFs
    for stem in ("figure1_architecture", "figure2_performance",
                 "figure3_expert_agreement", "figure4_demo_case",
                 "figure5_reasoning_trace"):
        src = FIG / f"{stem}.tiff"
        shutil.copy2(src, PKG / src.name)
        print(f"[copy] {src.name}")

    (PKG / "00_README_投稿清单.md").write_text(README, encoding="utf-8")
    print(f"[readme] 00_README_投稿清单.md")

    print(f"\n[pkg] {PKG}")
    for p in sorted(PKG.iterdir()):
        print(f"  {p.name}  ({p.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
