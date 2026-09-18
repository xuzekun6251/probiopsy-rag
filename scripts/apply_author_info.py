# -*- coding: utf-8 -*-
"""Propagate configs/author_info.yaml into every file that carries author TODOs.

Replaces TODO placeholders in:
  outputs/paper/manuscript.en.md   (authors, affiliations, email, funding, COI, CRediT)
  outputs/paper/00_front_zh.md     (作者/单位/邮箱)
  outputs/submission/cover_letter.md (signature block, ethics line)
  outputs/submission/data_availability.md (repo URL, Zenodo DOI, licenses)
  LICENSE                          (copyright holder)
  .zenodo.json                     (creators)

Then reassembles the zh manuscript and rebuilds the submission zip.
Run:  .venv\\Scripts\\python.exe scripts\\apply_author_info.py
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
INFO = yaml.safe_load((ROOT / "configs" / "author_info.yaml").read_text(encoding="utf-8"))

pi = INFO.get("pi") or {}
required = ["name_en", "name_zh", "department_en", "institution_en", "email"]
missing = [k for k in required if not (pi.get(k) or "").strip()]
if missing:
    print("请先在 configs/author_info.yaml 填写 pi 的以下字段:", ", ".join(missing))
    sys.exit(1)

coauthors = INFO.get("coauthors") or []
funding = INFO.get("funding") or {}
coi = INFO.get("coi") or {}

# cover letter is in English — map common Chinese titles; pass through anything else
TITLE_EN = {"主治医师": "Attending Physician", "副主任医师": "Associate Chief Physician",
            "主任医师": "Chief Physician", "教授": "Professor", "副教授": "Associate Professor",
            "研究员": "Professor", "副研究员": "Associate Professor"}
title_en = TITLE_EN.get((pi.get("title") or "").strip(), pi.get("title", ""))

# ---- build affiliation numbering (en + zh)
affs_en, affs_zh, aff_of = [], [], {}
def aff_number(dept_en, inst_en, dept_zh, inst_zh):
    key = (dept_en, inst_en)
    if key not in aff_of:
        aff_of[key] = len(affs_en) + 1
        affs_en.append(f"<sup>{aff_of[key]}</sup> {dept_en}, {inst_en}.")
        affs_zh.append(f"<sup>{aff_of[key]}</sup>{dept_zh}，{inst_zh}；")
    return aff_of[key]

n_pi = aff_number(pi["department_en"], pi["institution_en"],
                  pi.get("department") or "", pi.get("institution") or "")

authors_en = [f'{pi["name_en"]}<sup>{n_pi},\\*</sup>']
authors_zh = [f'{pi["name_zh"]}<sup>{n_pi},\\*</sup>']
for co in coauthors:
    n = aff_number(co.get("department_en") or pi["department_en"],
                   co.get("institution_en") or pi["institution_en"],
                   co.get("department") or pi.get("department") or "",
                   co.get("institution") or pi.get("institution") or "")
    authors_en.append(f'{co.get("name_en", "?")}<sup>{n}</sup>')
    authors_zh.append(f'{co.get("name_zh", "?")}<sup>{n}</sup>')

credit_pi = "Conceptualization, Methodology, Software, Validation, Writing – original draft"
credit_lines = [f'{pi["name_en"]}: {credit_pi}.'] + [
    f'{co.get("name_en", "?")}: {co.get("contribution", "Writing – review & editing")}.'
    for co in coauthors]

replacements = {
    ROOT / "outputs" / "paper" / "manuscript.en.md": [
        ("[PI Name TODO]<sup>1,\\*</sup>, [co-authors TODO]",
         ", ".join(authors_en)),
        ("<sup>1</sup> [Department / Institution TODO]",
         " ".join(affs_en)),
        ("Corresponding author: [email TODO]",
         f'Corresponding author: {pi["email"]}'),
        ("## Funding\n\n[TODO]", f"## Funding\n\n{(funding.get('en') or '').strip() or '[TODO]'}"),
        ("## Conflicts of interest\n\n[TODO]",
         f"## Conflicts of interest\n\n{(coi.get('en') or '').strip() or '[TODO]'}"),
        ("[PI TODO]: Conceptualization, Methodology, Software, Validation, Writing – original draft. [Co-authors TODO]: [TODO].",
         " ".join(credit_lines)),
    ],
    ROOT / "outputs" / "paper" / "00_front_zh.md": [
        ("[PI 姓名 TODO]<sup>1,\\*</sup>，[合作者 TODO]", "，".join(authors_zh)),
        ("<sup>1</sup>[科室/单位 TODO]；<sup>\\*</sup>通讯作者：[邮箱 TODO]",
         f'{" ".join(affs_zh)}<sup>\\*</sup>通讯作者：{pi["email"]}'),
    ],
    ROOT / "outputs" / "submission" / "cover_letter.md": [
        ("[PI Name TODO]\n[Title TODO]\n[Department, Institution TODO]\n[Email TODO]",
         f'{pi["name_en"]}\n{title_en}\n'
         f'{pi["department_en"]}, {pi["institution_en"]}\n{pi["email"]}'),
        ("Ethics: no human participants, patient data, or biological samples were involved; corpus and gold standard derive from the published ProBIOPSY consensus; demonstration cases are synthetic.",
         "Ethics: the computational evaluation involved no patient data or biological samples (corpus and gold standard derive from the published ProBIOPSY consensus; demonstration cases are synthetic); the four-expert blinded review used anonymous, voluntary participation with no identifiable data."),
    ],
    ROOT / "outputs" / "submission" / "data_availability.md": [
        ("[GitHub repo TODO]", INFO.get("github_repo") or "[GitHub repo TODO]"),
        ("[DOI TODO]", INFO.get("zenodo_doi") or "[DOI TODO]"),
        ("[MIT TODO]", "MIT"),
        ("[CC BY 4.0 TODO]", "CC BY 4.0"),
    ],
    ROOT / "LICENSE": [
        ("[COPYRIGHT HOLDER]", f'{pi["name_en"]} ({pi["name_zh"]})'),
    ],
}

for path, pairs in replacements.items():
    text = path.read_text(encoding="utf-8")
    for old, new in pairs:
        if old in text:
            text = text.replace(old, new)
        else:
            print(f"  ! 未找到（可能已替换过）: {path.name}: {old[:60]!r}…")
    path.write_text(text, encoding="utf-8")
    print("  ✓", path.name)

# .zenodo.json creators
zpath = ROOT / ".zenodo.json"
if zpath.exists():
    z = json.loads(zpath.read_text(encoding="utf-8"))
    z["creators"] = ([{"name": pi["name_en"], "affiliation": pi["institution_en"]}] +
                     [{"name": co.get("name_en", "?"),
                       "affiliation": co.get("institution_en") or pi["institution_en"]}
                      for co in coauthors])
    if INFO.get("zenodo_doi"):
        z["related_identifiers"] = z.get("related_identifiers", [])
    zpath.write_text(json.dumps(z, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  ✓ .zenodo.json creators:", len(z["creators"]))

# reassemble zh manuscript + rebuild zip
for cmd in [[sys.executable, "scripts/assemble_manuscript.py"],
            [sys.executable, "scripts/build_submission_zip.py"]]:
    subprocess.run(cmd, cwd=ROOT, check=True)

# leftover scan
leftovers = []
for f in ["outputs/paper/manuscript.en.md", "outputs/paper/00_front_zh.md",
          "outputs/submission/cover_letter.md", "outputs/submission/data_availability.md"]:
    t = (ROOT / f).read_text(encoding="utf-8")
    if "TODO" in t and f.endswith("manuscript.en.md"):
        leftovers += [ln for ln in t.splitlines() if "TODO" in ln]
if leftovers:
    print("\n剩余 TODO（需人工处理）:")
    for ln in leftovers:
        print("  ", ln.strip()[:100])
print("\n[done] 作者信息已应用")
