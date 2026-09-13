"""LightRAG adapter wiring DeepSeek (chat/entity extraction) + ArkVisionEmbedding.

(v2.6) This is the REAL implementation that ``phase4_build_index.py`` and the
Streamlit RAG-chat tab call. Earlier versions left this as an empty stub, which
meant importing ``LightRAGAdapter`` raised ``AttributeError`` at runtime.

(v2.6.1 patch) hardens the asyncio + filesystem handling so the adapter works
both from the CLI (phase4 build, no running loop) AND from inside Streamlit
(which runs inside its own event loop). Key fixes:
  - ``_run(coro)`` loop-safe runner: uses ``asyncio.run`` on a worker thread
    when a loop is already running (Streamlit/Jupyter), else ``asyncio.run``
    directly. Avoids the deprecated ``get_event_loop().run_until_complete``
    pattern that raises ``RuntimeError: event loop already running`` in Streamlit.
  - ``os.makedirs(working_dir, exist_ok=True)`` before LightRAG construction.
  - ``EmbeddingFunc`` imported from ``lightrag.base`` (canonical; ``lightrag.utils``
    re-exports it in some versions but moved across releases).
  - relative imports with an absolute-import fallback (works on direct run too).
  - ``stats()`` uses the real ``graph_storage`` attribute / ``get_knowledge_graph``.

Architecture:
  - chat / entity-extraction LLM  → DeepSeek V4 Flash (OpenAI-compatible)
  - embedding                     → doubao-embedding-vision-251215 (Ark multimodal)
  - storage backends              → defaults (JsonKV / NanoVectorDB / NetworkX)
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import os
from typing import Any

# relative import with absolute fallback so the file works both as a package
# module (post-scaffold) and when run directly (tests, ad-hoc import).
try:
    from .embedding_client import ArkVisionEmbedding
    from .llm_client import LLMClient
except ImportError:
    from embedding_client import ArkVisionEmbedding  # type: ignore
    from llm_client import LLMClient  # type: ignore


class LightRAGAdapter:
    """Wrapper around ``lightrag.LightRAG`` with DeepSeek + Ark embedding wired in.

    Usage::

        adapter = LightRAGAdapter(working_dir="data/processed/lightrag_index")
        adapter.insert_chunks(["evidence text 1", "evidence text 2", ...])
        answer = adapter.query("what is the effect of PM2.5 on COPD?", mode="hybrid")
    """

    def __init__(
        self,
        working_dir: str | None = None,
        chat_client: LLMClient | None = None,
        embed_client: ArkVisionEmbedding | None = None,
        language: str = "Chinese",
    ) -> None:
        # lazy import: lightrag-hku is a heavy dep; keep import error informative
        try:
            from lightrag import LightRAG, QueryParam  # type: ignore
            # EmbeddingFunc canonical home is lightrag.base; some versions also
            # re-export from lightrag.utils. Try base first, fall back to utils.
            try:
                from lightrag.base import EmbeddingFunc  # type: ignore
            except ImportError:
                from lightrag.utils import EmbeddingFunc  # type: ignore
        except ImportError as e:
            raise ImportError(
                "LightRAGAdapter requires lightrag-hku. Install with: "
                "pip install 'lightrag-hku>=1.0,<2.0'"
            ) from e

        self._QueryParam = QueryParam
        self.working_dir = working_dir or os.getenv(
            "LIGHTRAG_WORKING_DIR", "data/processed/lightrag_index"
        )

        # ensure the working dir exists BEFORE LightRAG tries to open files in it
        os.makedirs(self.working_dir, exist_ok=True)

        # wire clients
        self.chat = chat_client or LLMClient(provider="deepseek")
        self.embed = embed_client or ArkVisionEmbedding()

        # build llm_model_func (async, LightRAG protocol)
        async def llm_model_func(
            prompt: str,
            system_prompt: str | None = None,
            history_messages: list[dict] | None = None,
            keyword_extraction: bool = False,
            **kwargs: Any,
        ) -> str:
            # keyword_extraction → use a terse system prompt to get just keywords
            sys_p = system_prompt
            if keyword_extraction and not sys_p:
                sys_p = (
                    "Extract up to 10 high-level keywords from the text. "
                    "Return comma-separated keywords only, no prose."
                )
            resp = self.chat.complete(prompt=prompt, system=sys_p)
            return resp.text

        # build embedding_func wrapped in EmbeddingFunc with attrs.
        # LightRAG expects a numpy array (it calls .size on the result), so we
        # convert the list-of-lists to np.asarray before returning.
        async def _embed_async(texts: list[str]):
            import numpy as np  # local import; numpy is a LightRAG dep
            vecs = self.embed.embed(texts)
            return np.asarray(vecs, dtype=np.float32)

        embedding_func = EmbeddingFunc(
            embedding_dim=self.embed.embedding_dim,
            max_token_size=8192,
            func=_embed_async,
        )

        self.rag = LightRAG(
            working_dir=self.working_dir,
            llm_model_func=llm_model_func,
            llm_model_name=self.chat.model,
            embedding_func=embedding_func,
            addon_params={"language": language},
        )
        self._initialized = False

    # ------------------------------------------------------------------ #
    # loop-safe coroutine runner (works in CLI AND inside Streamlit's loop)
    # ------------------------------------------------------------------ #
    # LightRAG's internal async state (PriorityQueues, locks) is bound to ONE
    # event loop. If we create a fresh loop per call (as asyncio.run does),
    # subsequent calls hit "<PriorityQueue> is bound to a different event loop".
    # Solution: keep ONE dedicated worker thread with ONE persistent loop for
    # the lifetime of this adapter, and submit all coroutines to it. This also
    # makes the adapter safe inside Streamlit/Jupyter (which have their own
    # running loop that we must NOT call run_until_complete on).
    def _start_loop_thread(self):
        import queue
        self._call_q: "queue.Queue" = queue.Queue()
        self._result_q: "queue.Queue" = queue.Queue()

        def _loop_runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._loop = loop
            while True:
                coro = self._call_q.get()
                if coro is None:  # shutdown sentinel
                    break
                try:
                    result = loop.run_until_complete(coro)
                    self._result_q.put(("ok", result))
                except Exception as e:
                    self._result_q.put(("err", e))
            loop.close()

        import threading
        self._loop_thread = threading.Thread(target=_loop_runner, daemon=True)
        self._loop_thread.start()

    def _run(self, coro):
        """Submit a coroutine to the dedicated worker-thread loop and block on the result."""
        if not hasattr(self, "_loop_thread"):
            self._start_loop_thread()
        self._call_q.put(coro)
        status, payload = self._result_q.get()
        if status == "err":
            raise payload
        return payload

    def _ensure_init(self) -> None:
        if not self._initialized:
            self._run(self.rag.initialize_storages())
            self._initialized = True

    # ------------------------------------------------------------------ #
    # public API (sync wrappers for phase4 / streamlit convenience)
    # ------------------------------------------------------------------ #
    def insert_chunks(self, chunks: list[str], batch_size: int = 50) -> None:
        """Insert evidence chunks in batches to avoid OOM (see failure_modes.md)."""
        self._ensure_init()
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            self._run(self.rag.ainsert(batch))

    def insert_text(self, text: str) -> None:
        self._ensure_init()
        self._run(self.rag.ainsert(text))

    def query(self, question: str, mode: str = "hybrid") -> str:
        """Query the index. mode in {local, global, hybrid, naive, mix}."""
        self._ensure_init()
        param = self._QueryParam(mode=mode)
        return self._run(self.rag.aquery(question, param=param))

    def stats(self) -> dict:
        """Return a small stats dict for phase4 progress.json + Streamlit Overview."""
        disk_bytes = 0
        if os.path.isdir(self.working_dir):
            for root, _dirs, files in os.walk(self.working_dir):
                for f in files:
                    disk_bytes += os.path.getsize(os.path.join(root, f))
        # entity / relation counts: prefer the async get_knowledge_graph() API,
        # fall back to the graph_storage backend's NetworkX graph if present.
        ents = rels = 0
        try:
            kg = self._run(self.rag.get_knowledge_graph())
            ents = kg.number_of_nodes()
            rels = kg.number_of_edges()
        except Exception:
            try:
                storage = getattr(self.rag, "graph_storage", None)
                g = getattr(storage, "_graph", None) or getattr(storage, "graph", None)
                if g is not None:
                    ents = g.number_of_nodes()
                    rels = g.number_of_edges()
            except Exception:
                pass
        return {
            "working_dir": self.working_dir,
            "entities_extracted": ents,
            "relations_extracted": rels,
            "index_disk_kb": disk_bytes // 1024,
            "llm_provider": f"deepseek:{self.chat.model}",
            "embedding_provider": f"ark:{self.embed.model_field}",
            "embedding_dim": self.embed.embedding_dim,
        }
