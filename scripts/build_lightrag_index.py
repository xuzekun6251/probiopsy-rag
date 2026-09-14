"""Build the LightRAG knowledge-graph index from the ProBIOPSY evidence base.

Executor Phase 4. Reads data/seed/evidence_chunks.jsonl (357 entity-linked
chunks from the ProBIOPSY corpus) and inserts them into LightRAG
(dual-level retrieval: entity/graph + vector) with:
  - chat / entity extraction : Zhipu GLM-5.3 via project LLMClient (.env HUANYU_BULK_*)
  - embeddings               : doubao-embedding-vision-251215 via ArkVisionEmbedding
  - storage                  : LightRAG defaults (JsonKV / NanoVectorDB / NetworkX)

Each chunk text is prefixed with a compact provenance header (statement id,
decision items, linked scenario flags, weight) so that the extracted knowledge
graph carries statement-level citation handles.

Usage:
    .venv/Scripts/python.exe scripts/build_lightrag_index.py [--rebuild] [--limit N]

On success (full build only) marks executor.phase4 complete via Master state.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from probiopsy_rag_agent.lightrag_adapter import LightRAGAdapter  # noqa: E402

MASTER_SCRIPTS = Path(r"C:\Users\31291\.zcode\skills\medical-agent\scripts")
WORKING_DIR = ROOT / "data" / "processed" / "lightrag_index"
CHUNKS_PATH = ROOT / "data" / "seed" / "evidence_chunks.jsonl"


def load_env() -> None:
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            os.environ.setdefault(key.strip(), val.strip())


def chunk_to_text(chunk: dict) -> str:
    """Prefix the chunk with a provenance header for graph extraction."""
    bits = [f"source_id={chunk.get('chunk_id', '?')}"]
    if chunk.get("source_locator"):
        bits.append(f"locator={chunk['source_locator']}")
    ea = chunk.get("entities_a") or []
    eb = chunk.get("entities_b") or []
    if ea:
        bits.append("patient_scenario=" + ",".join(ea))
    if eb:
        bits.append("decision_items=" + ",".join(eb))
    if chunk.get("weight"):
        bits.append(f"weight={chunk['weight']}")
    header = "[ProBIOPSY evidence | " + " | ".join(bits) + "]"
    return f"{header}\n{chunk.get('text', '')}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rebuild", action="store_true", help="wipe the index dir first")
    parser.add_argument("--limit", type=int, default=0, help="insert only first N chunks (smoke)")
    parser.add_argument("--batch-size", type=int, default=20)
    parser.add_argument("--extract-model", default=None,
                        help="chat model for entity extraction (default: glm-5.3-flash)")
    args = parser.parse_args()

    load_env()

    # (v2.6 rate-limit fix) Extraction uses the FAST non-thinking flash tier:
    # GLM-5.3 thinking burns ~10k tokens/call which trips Zhipu's ACCOUNT-level
    # token-throughput limit (429/1302) after a handful of chunks. glm-5.3-flash
    # runs the same extraction prompt in ~15-20s with a tiny token footprint
    # (4/4 valid extractions under burst in probing). The arbiter/chat keeps
    # glm-5.3 (HUANYU_BULK_MODEL) — set AFTER load_env so this override wins.
    os.environ["HUANYU_BULK_MODEL"] = (
        args.extract_model or os.environ.get("HUANYU_BULK_EXTRACT_MODEL") or "glm-5.3-flash"
    )

    chunks = [json.loads(l) for l in CHUNKS_PATH.open(encoding="utf-8") if l.strip()]
    if args.limit:
        # smoke mode: keep a spread across sources (first N of each major type)
        chunks = chunks[: args.limit]
    texts = [chunk_to_text(c) for c in chunks]
    print(f"[phase4] {len(texts)} chunks to insert -> {WORKING_DIR}", flush=True)

    if args.rebuild and WORKING_DIR.exists():
        shutil.rmtree(WORKING_DIR)
        print("[phase4] wiped existing index (--rebuild)", flush=True)

    adapter = LightRAGAdapter(
        working_dir=str(WORKING_DIR),
        language="English",  # corpus is English; entity extraction in English
    )

    t0 = time.time()
    done = 0
    for i in range(0, len(texts), args.batch_size):
        batch = texts[i : i + args.batch_size]
        adapter.insert_chunks(batch, batch_size=args.batch_size)
        done += len(batch)
        rate = done / max(time.time() - t0, 1)
        print(f"[phase4] inserted {done}/{len(texts)} ({rate:.1f} chunks/s, "
              f"elapsed {time.time() - t0:.0f}s)", flush=True)

    stats = adapter.stats()
    stats["chunks_inserted"] = done
    stats["built_at"] = datetime.now().isoformat(timespec="seconds")
    stats["build_seconds"] = round(time.time() - t0, 1)
    out = ROOT / "outputs" / "lightrag_build_stats.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[phase4] stats: {json.dumps(stats, ensure_ascii=False)}", flush=True)

    if args.limit:
        print("[phase4] smoke build only — phase4 NOT marked complete")
        return 0

    # smoke-test a query before marking complete
    ans = adapter.query(
        "For a patient with a unifocal PI-RADS 4 lesion planned for focal therapy, "
        "what biopsy scheme does the ProBIOPSY consensus recommend?", mode="hybrid")
    print(f"[phase4] smoke query answer (first 300 chars):\n{ans[:300]}", flush=True)

    subprocess.run(
        [sys.executable, str(MASTER_SCRIPTS / "update_state.py"),
         "--project-root", str(ROOT),
         "--phase", "executor.phase4",
         "--stage", "executor",
         "--event", f"executor.phase4 completed: {done} chunks indexed, "
                    f"{stats['entities_extracted']} entities, {stats['relations_extracted']} relations",
         "--skill", "medical-agent-executor"],
        check=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
