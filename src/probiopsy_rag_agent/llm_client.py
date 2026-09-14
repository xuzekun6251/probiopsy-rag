"""LLM chat client (OpenAI-compatible; Zhipu GLM-5.3 as bulk chat/extractor).

Provides a thin ``complete(prompt, system)`` interface used by the rule-citation
relevance judge, the Streamlit RAG-chat tab, and LightRAG's entity-extraction /
summary LLM. The API is OpenAI-compatible, so we use the OpenAI client when
available and fall back to raw urllib if the SDK is missing.

Rate limiting (empirical, 2026-09): Zhipu enforces an ACCOUNT-level request-
frequency limit (HTTP 429, error code 1302 「您的账户已达到速率限制」). Sustained
back-to-back extraction calls — and worse, their retries — trip it and every
in-flight call fails together. The client therefore:
  1. throttles request STARTS to one per ``LLM_MIN_INTERVAL`` seconds
     (default 12 s for GLM ⇒ ≤5 RPM worst case, under the observed ceiling);
  2. backs off 30 s (then 60 s) whenever a 429/1302 is seen, instead of the
     generic 1-3 s transient retry.

Reads from env (.env / os.environ):
  HUANYU_BULK_API_KEY       preferred key
  HUANYU_BULK_MODEL         glm-5.3 (default)
  HUANYU_BULK_BASE_URL      https://open.bigmodel.cn/api/paas/v4
  HUANYU_BULK_TEMPERATURE   default 0.0
  HUANYU_BULK_MAX_TOKENS    default 1024 (floored to 16384 for GLM thinking)
  LLM_HTTP_TIMEOUT          SDK timeout seconds (default 90; SDK default is 600)
  LLM_MIN_INTERVAL          min seconds between request starts (default 12 for GLM)

If no key is configured, the client enters **stub mode**: every ``complete``
returns a canned template answer and sets ``self.degraded = True`` so callers
(verify_rule_citations relevance layer, Streamlit chat) can gracefully degrade
instead of crashing the build.
"""
from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class ChatResponse:
    text: str
    degraded: bool = False


# Account-level request throttle shared by ALL LLMClient instances (Zhipu's
# 429/1302 limit applies to the ACCOUNT, not to a client object — the build
# runs LightRAG's client, the benchmark's baseline client and the arbiter
# client concurrently, so a per-instance gate would not protect anything).
_THROTTLE_LOCK = threading.Lock()
_LAST_REQUEST_AT = 0.0


class LLMClient:
    """OpenAI-compatible chat client (DeepSeek V4 Flash by default).

    Parameters
    ----------
    provider : str
        Currently only "deepseek" is wired (reads HUANYU_BULK_* / DEEPSEEK_*).
        "stub" forces degraded mode for offline tests.
    temperature, max_tokens : override the env defaults.
    """

    def __init__(
        self,
        provider: str = "deepseek",
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.provider = provider
        self.degraded = False
        self._sdk_client = None  # lazy OpenAI SDK client (reused across calls)

        if provider == "stub":
            self.degraded = True
            self.api_key = ""
            self.base_url = ""
            self.model = "stub"
            self.temperature = temperature if temperature is not None else 0.0
            self.max_tokens = max_tokens or 1024
            self._is_glm = False
            self._min_interval = 0.0
            return

        # DeepSeek / OpenAI-compatible resolution
        self.api_key = (
            os.getenv("HUANYU_BULK_API_KEY")
            or os.getenv("DEEPSEEK_API_KEY")
            or ""
        )
        self.base_url = (
            os.getenv("HUANYU_BULK_BASE_URL")
            or (os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/") + "/v1")
        )
        self.model = (
            os.getenv("HUANYU_BULK_MODEL")
            or os.getenv("LLM_CHAT_MODEL")
            or "deepseek-v4-flash"
        )
        self.temperature = float(
            temperature if temperature is not None
            else os.getenv("HUANYU_BULK_TEMPERATURE", "0.0")
        )
        self.max_tokens = int(
            max_tokens or os.getenv("HUANYU_BULK_MAX_TOKENS", "1024")
        )
        # Thinking models (GLM-5.x on Zhipu) spend tokens on internal reasoning
        # before emitting content; Zhipu error 1210 confirms thinking cannot be
        # switched off for these models. A small caller-supplied max_tokens
        # therefore starves the final content (empty ``content`` responses):
        # empirically 4096 is exhausted by thinking on long extraction prompts
        # ~75% of the time, 16384 restores reliable content emission.
        # Floor the budget so short-answer callers still get real text — and
        # LightRAG entity-extraction JSON fits without truncation.
        self._is_glm = (
            "bigmodel" in (self.base_url or "") and "glm" in self.model.lower()
        )
        if self._is_glm:
            self.max_tokens = max(self.max_tokens, 16384)
        # account-level request-frequency throttle (see module docstring).
        # Probed 2026-09: ≥20 RPM of short calls passes; long thinking-model
        # extractions (~10k tokens/call) trip 1302 quickly under concurrency.
        # 12 s floor ⇒ ≤5 RPM worst case (fast-failure retry loops) while the
        # natural serial-extraction pace (~2 RPM) is unaffected.
        default_interval = "12" if self._is_glm else "0"
        self._min_interval = float(os.getenv("LLM_MIN_INTERVAL", default_interval))

        if not self.api_key:
            # no key → degrade to stub so the build can proceed in keyword-only mode
            self.degraded = True
            self.model = "stub"

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def complete(self, prompt: str, system: str | None = None) -> ChatResponse:
        """Return a chat completion. ``degraded=True`` if in stub mode.

        Retries up to 3 attempts: GLM-5.3 is a thinking model and
        intermittently returns an empty ``content`` (reasoning consumed the
        token budget); empty responses are treated as transient failures.
        """
        if self.degraded:
            return ChatResponse(
                text=f"[stub] no LLM key configured; prompt was {len(prompt)} chars.",
                degraded=True,
            )
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        last_err: Exception | str = "unknown"
        for attempt in range(3):
            try:
                self._throttle()
                text = self._chat(messages)
                if text and text.strip():
                    return ChatResponse(text=text, degraded=False)
                last_err = "empty content from model (transient)"
            except Exception as e:
                last_err = e
                # Zhipu 429 (code 1302) = account-level frequency limit:
                # a short generic sleep just burns more 429s. Back off hard.
                if "1302" in str(e) or "429" in str(e):
                    time.sleep(30.0 * (attempt + 1))
                    continue
            time.sleep(1.0 * (attempt + 1))
        # network / API failure → degrade rather than crash the build
        return ChatResponse(text=f"[llm error] {last_err}", degraded=True)

    def _throttle(self) -> None:
        """Enforce a minimum interval between request STARTS (process-global)."""
        global _LAST_REQUEST_AT
        if self._min_interval <= 0:
            return
        while True:
            with _THROTTLE_LOCK:
                wait = _LAST_REQUEST_AT + self._min_interval - time.time()
                if wait <= 0:
                    _LAST_REQUEST_AT = time.time()
                    return
            time.sleep(min(wait, 5.0))

    # ------------------------------------------------------------------ #
    def _chat(self, messages: list[dict[str, str]]) -> str:
        """Try the OpenAI SDK first, fall back to raw urllib.

        The SDK client is created once and reused, with an explicit bounded
        timeout (default SDK timeout is 600 s — a throttled call would freeze
        the caller, and inside LightRAG's adapter it freezes the whole event
        loop). max_retries stays at 1: complete() already retries at a higher
        level with its own backoff.
        """
        try:
            from openai import OpenAI  # type: ignore
        except ImportError:
            return self._chat_urllib(messages)
        if self._sdk_client is None:
            self._sdk_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=float(os.getenv("LLM_HTTP_TIMEOUT", "90")),
                max_retries=1,
            )
        resp = self._sdk_client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return resp.choices[0].message.content or ""

    def _chat_urllib(self, messages: list[dict[str, str]]) -> str:
        data = json.dumps({
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }).encode("utf-8")
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url, data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        choices = data.get("choices") or []
        if not choices:
            return ""
        msg = choices[0].get("message", {})
        # DeepSeek V4 puts reasoning in `reasoning_content`; final answer in `content`
        return msg.get("content") or ""


def from_env_dual():
    """Convenience factory referenced by setup_environment.py docstring.

    Returns a single bulk (DeepSeek) client configured from env.
    """
    return LLMClient(provider="deepseek")
