# Engineering notes — LLM transport hardening (Phase 4)

Recorded 2026-09-13 during the LightRAG index build. These findings drive the
rate-limiting code in `src/probiopsy_rag_agent/llm_client.py` and
`lightrag_adapter.py` and should be reflected in the manuscript's
implementation-details section (reproducibility).

## Observed Zhipu (bigmodel.cn) account-level limits

| Symptom | Evidence |
|---|---|
| HTTP 429, error code `1302` 「您的账户已达到速率限制」 | Build log, sustained extraction load |
| Short calls (~20 tokens in / ~30 out) pass at **≥20 RPM** | `scripts/probe_rate.py`: 10/10 OK at 3 s spacing |
| Heavy thinking-model calls (GLM-5.3, ~10k tokens/call incl. reasoning) trip 1302 after a handful of chunks, even at ~4 RPM | First build run: 7 successes then all-fail waves |
| `glm-5.3-flash` (fast tier) absorbs burst extraction (4/4 heavy calls valid at 3 s spacing, 15–21 s each) | `scripts/probe_flash.py` |
| `glm-4.7-flash` shared-tier congestion (429 code `1305` 「访问量过大」) — unusable | `scripts/probe_models.py` |
| Occasional **multi-hour hangs** of individual calls (server-side queueing); two workers wedged 58 min until LightRAG's health check (480/495 s) killed them | Build log: `Worker timeout after 480s`, `actual: 3518.9s` |
| **In-flight stacking collapses throughput even under a request-start throttle**: `LIGHTRAG_MAX_ASYNC=2` + LightRAG's hardcoded merge-phase `async: 4` ⇒ up to ~6 concurrent 10k-token calls; the account starts queueing them, latency explodes past the HTTP timeout (90 s) and call budget (240 s), and success fell to ~1 call / 40 min. An isolated probe call completed cleanly in 32.5 s at the same time | `probe_heavy.py` 32.5 s OK vs build log: 8× `exceeded 240s budget`, 3× `Request timed out`, 1 cache save in 40 min |
| Re-inserting already-processed documents creates junk `dup-*` FAILED marker rows in `kv_store_doc_status.json` (dedup by content-hash happens in ANY status); cosmetic only — the original `processed` rows remain authoritative | `scripts/inspect_doc_status.py` |

## Mitigations implemented

1. **Process-global request-start throttle** (`LLM_MIN_INTERVAL`, default 12 s
   for GLM): all `LLMClient` instances share one gate — the account limit is
   account-wide, so per-client gating is useless (build runs LightRAG,
   baseline, and arbiter clients concurrently). The throttle caps request
   STARTS, not in-flight concurrency — with long thinking-model calls the two
   diverge, hence mitigation 6.
2. **429-aware backoff**: on `1302`/`429`, sleep 30 s then 60 s instead of the
   generic 1–3 s transient retry (short retries amplify the storm); every
   retry is logged to stderr (`[llm retry]`) — silent retries hid the true
   error mix during earlier build attempts.
3. **Bounded SDK client**: `OpenAI(timeout=LLM_HTTP_TIMEOUT, max_retries=1)`,
   client created once and reused (SDK defaults are timeout=600 s,
   client-per-call — a throttled call would freeze the caller for ~10 min per
   attempt).
4. **Event-loop hygiene + hard call budget**: `llm_model_func` runs the
   blocking call via `loop.run_in_executor` and enforces `LLM_CALL_BUDGET`
   with `asyncio.wait_for` (NOT `future.result()`, which blocks the event
   loop and serializes LightRAG's async merge tasks). A hang degrades to one
   failed document instead of a wedged pipeline.
5. **Model split**: bulk entity extraction → `glm-5.3-flash`
   (`--extract-model` / `HUANYU_BULK_EXTRACT_MODEL`); arbiter + chat keep
   `glm-5.3` (reasoning quality matters there, call volume is low).
6. **Concurrency capping**: `LIGHTRAG_MAX_ASYNC=1` (one document in flight).
   MAX_ASYNC=2 interacts with the merge-phase `async: 4` to stack ~6 heavy
   calls in flight; the account queues them and per-call latency collapses
   throughput (see table). MAX_ASYNC=1 restored ~1.4 docs/min.
7. **Resumable recovery**: LightRAG dedupes by content-hash doc_id in ANY
   status, so failed/interrupted docs must be re-enabled by deleting their
   rows in `kv_store_doc_status.json` (`scripts/reset_doc_status.py`, run only
   while no build is active). The LLM response cache survives restarts and
   banks completed extractions by prompt hash; progress is monitored via
   doc_status counts (`scripts/rate_check.py`), not log greps — budget-abort
   failures never print the "LLM degraded" marker.

## Build profile used for the final index

```
LLM_MIN_INTERVAL=10  LIGHTRAG_MAX_ASYNC=1  LLM_HTTP_TIMEOUT=150  LLM_CALL_BUDGET=300
python scripts/build_lightrag_index.py           # resume runs; reset_doc_status between attempts
# observed steady state: ~1.4 docs/min (extraction 15-45 s + merge calls at 10 s spacing)
```
