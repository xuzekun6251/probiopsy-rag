"""evidence_store — retrieval over the entity-linked evidence chunks.

Loads ``data/seed/evidence_chunks.jsonl`` (357 chunks from the ProBIOPSY
corpus) and provides:
  - keyword retrieval with idf-weighted term overlap (the naive_rag baseline
    and the full system's fallback context provider);
  - entity-aware filtering (boost chunks linked to the decision item /
    scenario flags of the query);
  - char-precise context packing with a budget.

No external dependencies (no FAISS/sklearn) — the naive baseline must stay
honest: plain lexical scoring is exactly what "naive RAG" means here.
"""
from __future__ import annotations

import ast
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

_TOKEN_RE = re.compile(r"[a-z0-9]{2,}")
_STOP = {
    "the", "of", "and", "to", "in", "a", "for", "is", "are", "be", "on", "or",
    "with", "as", "by", "that", "this", "an", "at", "from", "was", "were",
    "it", "its", "their", "has", "have", "had", "not", "but", "which", "can",
    "may", "should", "would", "could", "will", "than", "then", "these",
    "those", "such", "into", "when", "if", "no", "we", "they", "there",
}


@dataclass
class Chunk:
    chunk_id: str
    text: str
    level: str = ""            # A_guideline/B_consensus/C_rct_meta/D_review
    weight: int = 1
    entities_a: list[str] = field(default_factory=list)
    entities_b: list[str] = field(default_factory=list)
    source_locator: str = ""
    tokens: list[str] = field(default_factory=list)


@dataclass
class Retrieved:
    chunk: Chunk
    score: float


def _parse_entities(val) -> list[str]:
    """entities_a/entities_b are stored as python-literal strings ('[...]') or lists."""
    if isinstance(val, list):
        return [str(x) for x in val]
    if isinstance(val, str) and val.strip():
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, (list, tuple)):
                return [str(x) for x in parsed]
        except (ValueError, SyntaxError):
            return []
    return []


class EvidenceStore:
    def __init__(self, path: str | Path) -> None:
        self.chunks: list[Chunk] = []
        with Path(path).open(encoding="utf-8") as fh:
            for line in fh:
                if not line.strip():
                    continue
                c = json.loads(line)
                self.chunks.append(Chunk(
                    chunk_id=c.get("evidence_id", c.get("chunk_id", "")),
                    text=c.get("text", ""),
                    level=c.get("source_quality_rank", c.get("level", "")),
                    weight=int(float(c.get("weight") or 1)),
                    entities_a=_parse_entities(c.get("entities_a")),
                    entities_b=_parse_entities(c.get("entities_b")),
                    source_locator=c.get("source_locator", ""),
                ))
        self._df: dict[str, int] = {}
        for c in self.chunks:
            c.tokens = [t for t in _TOKEN_RE.findall(c.text.lower()) if t not in _STOP]
            for t in set(c.tokens):
                self._df[t] = self._df.get(t, 0) + 1
        self._n = max(len(self.chunks), 1)

    # ------------------------------------------------------------------ #
    def _idf(self, term: str) -> float:
        return math.log((self._n + 1) / (self._df.get(term, 0) + 0.5))

    def retrieve(
        self,
        query: str,
        k: int = 6,
        boost_entities_b: list[str] | None = None,
        boost_entities_a: list[str] | None = None,
    ) -> list[Retrieved]:
        qtokens = [t for t in _TOKEN_RE.findall(query.lower()) if t not in _STOP]
        qb = set(boost_entities_b or [])
        qa = set(boost_entities_a or [])
        results: list[Retrieved] = []
        for c in self.chunks:
            if not qtokens:
                base = 0.0
            else:
                tf: dict[str, int] = {}
                for t in c.tokens:
                    tf[t] = tf.get(t, 0) + 1
                base = sum((1 + math.log(tf[t])) * self._idf(t) for t in qtokens if t in tf)
                base /= math.sqrt(len(c.tokens) + 40)  # mild length normalization
            bonus = 0.0
            if qb & set(c.entities_b):
                bonus += 2.0
            if qa & set(c.entities_a):
                bonus += 1.0
            if c.weight > 1:
                bonus += 0.25 * (c.weight - 1)   # consensus statements weigh more
            score = base * (1 + bonus)
            if score > 0:
                results.append(Retrieved(chunk=c, score=score))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    def pack_context(self, retrieved: list[Retrieved], char_budget: int = 6000) -> str:
        """Pack retrieved chunks into a citation-tagged context string."""
        parts: list[str] = []
        used = 0
        for r in retrieved:
            tag = f"[{r.chunk.chunk_id}|{r.chunk.level}|{r.chunk.source_locator}]"
            block = f"{tag}\n{r.chunk.text}"
            if used + len(block) > char_budget:
                remain = char_budget - used
                if remain < 200:
                    break
                block = block[:remain]
            parts.append(block)
            used += len(block)
        return "\n\n---\n\n".join(parts)
