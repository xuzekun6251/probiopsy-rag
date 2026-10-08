# -*- coding: utf-8 -*-
"""Run real patient-education consultations through the education mode (temp driver).

Mirrors app/streamlit_app.py chat_tab patient branch exactly: hybrid context-only
graph retrieval + lexical retrieval + keyword-matched curated fact base + single
GLM generation with the patient-education system prompt. Saves verbatim
transcripts to outputs/demo_cases/patient_edu/ for Supplementary S7.
"""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass

from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter
from probiopsy_rag_agent.llm_client import LLMClient
from probiopsy_rag_agent.pipeline import INDEX_DIR, load_assets

OUT = ROOT / "outputs" / "demo_cases" / "patient_edu"
OUT.mkdir(parents=True, exist_ok=True)
FACTS_CSV = ROOT / "data" / "seed" / "patient_education_facts.csv"

PATIENT_SYSTEM = (
    "You are the patient-education voice of QianLieAnHui, a decision-support agent for the "
    "prostate biopsy pathway. You are speaking to a patient or family member, NOT a clinician. "
    "Answer in simple, warm Chinese: lay language, short sentences, explain every medical term "
    "in one short sentence. Ground every factual claim ONLY in the 【患者教育要点】 fact entries "
    "and 【证据】 blocks provided below; never invent statistics, percentages or study results. "
    "Structure the answer as: (1) a direct answer to the question in 2-4 short numbered points; "
    "(2) a short paragraph starting with '什么情况要及时就医：' using the safety-netting advice "
    "from the fact entries; (3) one closing sentence advising the patient to discuss their own "
    "case with the treating urologist. Do NOT issue an action verdict, drug dose, or schedule "
    "that is not in the materials. Cite fact ids in square brackets like [edu_negative_result] "
    "and evidence tags like [证据N] for claims taken from the materials."
)

QUESTIONS = [
    "医生，我穿刺结果是良性的，是不是以后就不用管了，也不用再查PSA了？",
    "我报告上写着非典型小腺泡增生（ASAP），这是什么意思？严重吗？",
    "我很怕疼，所以一直不敢做前列腺穿刺，能不做吗？",
]


def load_facts() -> list[dict]:
    with FACTS_CSV.open(encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def match_facts(question: str, facts: list[dict], cap: int = 3) -> list[dict]:
    q = (question or "").lower()
    scored = []
    for f in facts:
        kws = [k.strip().lower() for k in
               ((f.get("zh_keywords") or "") + "|" + (f.get("en_keywords") or "")).split("|")
               if k.strip()]
        hits = [k for k in kws if k in q]
        if hits:
            scored.append({"hits": len(hits), "matched": hits, **f})
    scored.sort(key=lambda f: -f["hits"])
    return scored[:cap]


def build_prompt(question: str, matched: list[dict], hits, graph_ctx: str) -> str:
    parts = []
    if matched:
        fb = []
        for i, f in enumerate(matched, 1):
            fb.append(f"【患者教育要点{i}】[{f['fact_id']}] {f['topic_en']} / {f['topic_zh']}\n"
                      f"核心解释：{f['lay_explanation_en']}\n"
                      f"就医提示（safety-netting）：{f['safety_netting_en']}\n"
                      f"来源：{f['sources']}")
        parts.append("【Patient-education fact entries (curated, source-traceable)】\n"
                     + "\n\n".join(fb))
    blocks = [f"【证据{i}】({r.chunk.chunk_id} | {r.chunk.source_locator})\n{r.chunk.text}"
              for i, r in enumerate(hits, 1)]
    if blocks:
        parts.append("【Evidence blocks】\n" + "\n\n".join(blocks))
    if graph_ctx.strip():
        parts.append("【Knowledge-graph context (retrieval-only)】\n" + graph_ctx[:2500])
    parts.append(f"【Patient question】\n{question}")
    return "\n\n".join(parts)


def main() -> int:
    assets = load_assets()
    adapter = LightRAGAdapter(working_dir=str(INDEX_DIR), language="English")
    llm = LLMClient(provider="deepseek", temperature=0.2, max_tokens=2048)
    facts = load_facts()

    for qi, question in enumerate(QUESTIONS, 1):
        print(f"--- Q{qi}: {question}")
        t0 = time.perf_counter()
        graph_ctx = adapter.query(question, mode="hybrid", only_need_context=True) or ""
        t_graph = time.perf_counter() - t0
        hits = assets.store.retrieve(question, k=6)
        t_lex = time.perf_counter() - t0 - t_graph
        matched = match_facts(question, facts)
        print(f"    graph {t_graph:.1f}s · lex {t_lex:.2f}s · facts={[f['fact_id'] for f in matched]}")
        prompt = build_prompt(question, matched, hits, graph_ctx)
        t3 = time.perf_counter()
        resp = llm.complete(prompt=prompt, system=PATIENT_SYSTEM)
        t_gen = time.perf_counter() - t3
        answer = resp.text
        print(f"    GLM {t_gen:.1f}s · degraded={resp.degraded} · {len(answer)} chars")

        ev = [{"n": i, "chunk_id": r.chunk.chunk_id, "locator": r.chunk.source_locator}
              for i, r in enumerate(hits, 1)]
        record = {
            "run_id": f"patient_edu_q{qi}",
            "question_zh": question,
            "mode": "patient_education",
            "matched_fact_ids": [f["fact_id"] for f in matched],
            "matched_fact_sources": [f["sources"] for f in matched],
            "n_evidence_chunks": len(hits),
            "evidence_chunks": ev,
            "answer_zh": answer,
            "degraded": bool(resp.degraded),
            "timings_s": {"graph": round(t_graph, 2), "lexical": round(t_lex, 2),
                          "generation": round(t_gen, 2)},
            "generator": "GLM-5.3 via OpenAI-compatible API (temperature 0.2)",
            "corpus": "frozen 357-chunk ProBIOPSY corpus (benchmark index, unchanged)",
        }
        (OUT / f"patient_edu_q{qi}.json").write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")

        md = [f"## Patient consultation {qi} (verbatim)", "",
              f"**Patient question (Chinese):** {question}", "",
              f"**Matched fact entries:** {', '.join(f['fact_id'] for f in matched) or 'none'}"
              f" — sources: {'; '.join(f['sources'] for f in matched) or '-'}", "",
              f"**Retrieval:** {len(hits)} evidence chunks (frozen benchmark corpus) "
              f"+ knowledge-graph context (context-only mode)", "",
              "**Agent answer (Chinese, verbatim):**", "", answer, "",
              f"**Timings:** graph {t_graph:.1f}s · lexical {t_lex:.2f}s · generation {t_gen:.1f}s"
              + (" · DEGRADED" if resp.degraded else ""), ""]
        (OUT / f"patient_edu_q{qi}.md").write_text("\n".join(md), encoding="utf-8")

    print(f"[patient-edu] transcripts saved to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
