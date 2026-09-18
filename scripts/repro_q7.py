"""Reproduce the lightrag-method NoneType error on a single gold statement."""
import csv
import sys
import io
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter

SID = sys.argv[1] if len(sys.argv) > 1 else "Q7"
rows = list(csv.DictReader((ROOT / "data" / "seed" / "probiopsy_statements.csv").open(encoding="utf-8-sig")))
row = next(r for r in rows if r["statement_id"] == SID)
flags = (row.get("scenario_flags") or "").replace("|", ", ")
question = (
    "Prostate-biopsy decision under evaluation.\n"
    f"Consensus statement: \"{row['statement_text_en']}\"\n"
    f"Stem: {row['stem_name']}. Decision item id: {row['decision_item_id']}.\n"
    f"Patient scenario flags: {flags or '(unspecified)'}.\n"
    "Which action should a guideline-faithful decision-support system take?\n"
    "End your answer with exactly one line: FINAL ACTION: <class> where <class> is one of "
    "endorse, endorse_option, conditional, report_option, against."
)

adapter = LightRAGAdapter(working_dir=str(ROOT / "data" / "processed" / "lightrag_index"))
try:
    answer = adapter.query(question, mode="hybrid")
    print("OK, answer len:", len(answer))
    print(answer[:400])
except Exception:
    traceback.print_exc()
