# -*- coding: utf-8 -*-
"""Prepare the repository for public release regarding ProBIOPSY text copyright.

data/seed/probiopsy_statements.csv contains statement_text_en (full consensus
statement text, (c) Elsevier), and data/evidence/ + data/processed/lightrag_index/
contain text derived from the same source. If the source article's license does
not permit redistribution (check the license badge on the article page via
institutional access), run this script BEFORE publishing:

  .venv\\Scripts\\python.exe scripts\\scrub_statement_text.py scrub

- drops the statement_text_en column from data/seed/probiopsy_statements.csv
  (statement_id, domain, labels, decision items and source_locator are kept);
- moves data/evidence/ and data/processed/lightrag_index/ to data/_local_only/
  (gitignored), so your local installation keeps working from the moved copies.

To move them back after cloning elsewhere (or undo locally):

  .venv\\Scripts\\python.exe scripts\\scrub_statement_text.py restore
"""
import csv
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed" / "probiopsy_statements.csv"
LOCAL = ROOT / "data" / "_local_only"
MOVE = [ROOT / "data" / "evidence", ROOT / "data" / "processed" / "lightrag_index"]
DESTS = [LOCAL / "evidence", LOCAL / "lightrag_index"]
COL = "statement_text_en"


def scrub() -> None:
    rows = list(csv.DictReader(open(SEED, encoding="utf-8-sig")))
    if rows and COL not in rows[0]:
        print(f"statement_text_en 列不存在，CSV 已是脱敏状态，跳过")
    else:
        fields = [f for f in rows[0] if f != COL]
        with open(SEED, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow({k: v for k, v in r.items() if k != COL})
        print(f"✓ {SEED.relative_to(ROOT)}: 已删除 {COL} 列（{len(rows)} 行，其余字段保留）")
    for src, dst in zip(MOVE, DESTS):
        if not src.exists():
            print(f"- {src.relative_to(ROOT)} 不存在，跳过")
            continue
        if dst.exists():
            print(f"- {dst.relative_to(ROOT)} 已存在，跳过（不覆盖）")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"✓ {src.relative_to(ROOT)} → {dst.relative_to(ROOT)}")
    print("\n完成：仓库可公开部分已不再包含共识原文。本地如需继续运行 demo/Streamlit，"
          "运行 restore 可把 evidence 与索引移回原位。")


def restore() -> None:
    for src, dst in zip(DESTS, MOVE):
        if not src.exists():
            print(f"- {src.relative_to(ROOT)} 不存在，跳过")
            continue
        if dst.exists():
            print(f"- {dst.relative_to(ROOT)} 已存在，跳过（不覆盖）")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        print(f"✓ {src.relative_to(ROOT)} → {dst.relative_to(ROOT)}")
    print("完成（statement_text_en 列不可恢复——如需原文请从共识原文重建）。")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "scrub":
        scrub()
    elif mode == "restore":
        restore()
    else:
        print(__doc__)
        sys.exit(1)
