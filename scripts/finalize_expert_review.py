# -*- coding: utf-8 -*-
"""Finalize the expert blind review once answers are collected.

Reads  outputs/expert_review/answer_worksheet.csv  (filled: action_choice,
likert_*, note per expert x case) and the 5 demo-case JSONs, then:
1. validates values (5-class tokens; Likert 1-5),
2. fills the official figure3 CSV (expert_rating / system_output /
   expert_majority / likert_* / note),
3. computes overall Fleiss kappa (5 subjects x 4 raters) + per-case raw
   agreement + Cohen kappa (system vs expert majority, ties excluded),
4. writes outputs/tables/expert_review_stats.json and prints a summary.

Run:  .venv\\Scripts\\python.exe scripts\\finalize_expert_review.py
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WS = ROOT / "outputs" / "expert_review" / "answer_worksheet.csv"
OFFICIAL = ROOT / "outputs" / "figures" / "source_data" / "figure3_expert_agreement.csv"
STATS_OUT = ROOT / "outputs" / "tables" / "expert_review_stats.json"
CASES_DIR = ROOT / "outputs" / "demo_cases"
ACTIONS = ["endorse", "endorse_option", "conditional", "report_option", "against"]

system_output = {}
for p in CASES_DIR.glob("*.json"):
    d = json.loads(p.read_text(encoding="utf-8"))
    system_output[d["case_id"]] = d["verdict"]["action"]

rows = list(csv.DictReader(open(WS, encoding="utf-8-sig")))
assert len(rows) == 20, f"worksheet must have 20 rows, got {len(rows)}"

ratings = {}   # (case, expert) -> action
likert = {}    # (case, expert) -> dict
notes = {}
errors = []
for r in rows:
    key = (r["case_id"], int(r["expert_id"]))
    a = (r["action_choice"] or "").strip()
    if a not in ACTIONS:
        errors.append(f"{key}: action_choice={a!r} 不是五类动作之一")
    ratings[key] = a
    lk = {}
    for k in ["likert_clarity", "likert_usefulness", "likert_recommendation",
              "likert_evidence"]:
        v = (r[k] or "").strip()
        if v not in {"1", "2", "3", "4", "5"}:
            errors.append(f"{key}: {k}={v!r} 必须为 1–5 整数")
        lk[k] = int(v) if v else None
    likert[key] = lk
    notes[key] = (r.get("note") or "").strip()
if errors:
    print("VALIDATION FAILED:")
    print("\n".join(" - " + e for e in errors))
    raise SystemExit(1)

case_ids = sorted({c for c, _ in ratings})
experts = sorted({e for _, e in ratings})

# ---- fill official CSV
out = []
with open(OFFICIAL, encoding="utf-8-sig") as f:
    rdr = csv.DictReader(f)
    fields = rdr.fieldnames
    official_rows = list(rdr)
by_case = {c: [ratings[(c, e)] for e in experts] for c in case_ids}
majority = {}
for r in official_rows:
    c, e = r["case_id"], int(r["expert_id"])
    r["expert_rating"] = ratings[(c, e)]
    r["system_output"] = system_output[c]
    r["likert_clarity"] = likert[(c, e)]["likert_clarity"]
    r["likert_usefulness"] = likert[(c, e)]["likert_usefulness"]
    r["likert_recommendation"] = likert[(c, e)]["likert_recommendation"]
    r["likert_evidence"] = likert[(c, e)]["likert_evidence"]
    r["note"] = notes[(c, e)]
    out.append(r)
    cnt = Counter(by_case[c])
    top = cnt.most_common()
    majority[c] = top[0][0] if len(top) == 1 or top[0][1] > top[1][1] else "split"
for r in out:
    r["expert_majority"] = majority[r["case_id"]]
with open(OFFICIAL, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(out)

# ---- Fleiss kappa (overall, subjects = cases, raters = 4, categories = 5)
n = len(experts)
N = len(case_ids)
cat_idx = {a: i for i, a in enumerate(ACTIONS)}
p_matrix = []
for c in case_ids:
    cnt = Counter(by_case[c])
    p_matrix.append([cnt[a] / n for a in ACTIONS])
# standard Fleiss computation
P_i = []
for row in p_matrix:
    P_i.append((sum(p * p for p in row) - 1 / len(ACTIONS)) / (n - 1))
p_j = [sum(row[k] for row in p_matrix) / N for k in range(len(ACTIONS))]
P_e = sum(p * p for p in p_j)
fleiss_kappa = (sum(P_i) / N - P_e) / (1 - P_e) if P_e < 1 else 1.0

# ---- Cohen kappa: system vs expert majority (ties excluded)
pairs = [(majority[c], system_output[c]) for c in case_ids if majority[c] != "split"]
if pairs:
    obs = sum(1 for a, b in pairs if a == b) / len(pairs)
    m_cnt = Counter(a for a, _ in pairs)
    s_cnt = Counter(b for _, b in pairs)
    exp = sum(m_cnt[a] * s_cnt[a] for a in set(m_cnt) | set(s_cnt)) / len(pairs) ** 2
    cohen_kappa = (obs - exp) / (1 - exp) if exp < 1 else 1.0
else:
    cohen_kappa, obs = None, None

stats = {
    "n_cases": N, "n_experts": n,
    "per_case_expert_ratings": by_case,
    "expert_majority": majority,
    "system_output": system_output,
    "per_case_raw_agreement": {c: f"{Counter(by_case[c]).most_common(1)[0][1]}/{n}"
                               for c in case_ids},
    "fleiss_kappa_overall": round(fleiss_kappa, 3),
    "cohen_kappa_system_vs_majority": None if cohen_kappa is None else round(cohen_kappa, 3),
    "cohen_kappa_n_pairs": len(pairs),
    "cohen_kappa_raw_agreement": None if obs is None else round(obs, 3),
    "likert_mean": {k: round(sum(likert[(c, e)][k] for c in case_ids for e in experts)
                             / (N * n), 2)
                    for k in ["likert_clarity", "likert_usefulness",
                              "likert_recommendation", "likert_evidence"]},
}
STATS_OUT.parent.mkdir(parents=True, exist_ok=True)
STATS_OUT.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")

print("[finalize] official CSV filled:", OFFICIAL)
print(f"Fleiss κ (overall, {N} subjects × {n} raters) = {fleiss_kappa:.3f}")
print(f"Cohen κ (system vs majority, n={len(pairs)}) = "
      f"{'n/a' if cohen_kappa is None else f'{cohen_kappa:.3f}'}; "
      f"raw agreement = {'n/a' if obs is None else f'{obs:.3f}'}")
print("per-case majority:", majority)
print("Likert means:", stats["likert_mean"])
print("written:", STATS_OUT)
