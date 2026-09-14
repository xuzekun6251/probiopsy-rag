"""naive_rag — keyword-retrieval baseline (PLAN.md §5).

Retrieves top-k evidence chunks by lexical scoring (EvidenceStore) and asks
the chat LLM to answer using only that context. No graph, no rules, no
entity awareness beyond what the raw text carries.
"""
from __future__ import annotations

from .evidence_store import EvidenceStore
from .llm_client import LLMClient

NAIVE_SYSTEM = (
    "You are a clinical decision-support assistant for prostate biopsy. "
    "Answer STRICTLY from the provided evidence excerpts. If the excerpts do "
    "not settle the question, answer with the closest supported statement. "
    "Keep the answer under 120 words."
)

NAIVE_PROMPT = """Evidence excerpts:
{context}

Question: {question}

Answer the question using only the evidence above."""


def naive_rag_answer(
    question: str,
    store: EvidenceStore,
    client: LLMClient,
    k: int = 6,
    char_budget: int = 6000,
) -> tuple[str, int]:
    """Return (answer_text, context_chars_retrieved)."""
    hits = store.retrieve(question, k=k)
    context = store.pack_context(hits, char_budget=char_budget)
    resp = client.complete(prompt=NAIVE_PROMPT.format(context=context, question=question),
                           system=NAIVE_SYSTEM)
    if getattr(resp, "degraded", False):
        return f"[llm error] {resp.text[:120]}", len(context)
    return resp.text, len(context)
