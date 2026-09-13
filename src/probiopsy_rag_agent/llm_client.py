"""LLM chat client (DeepSeek V4 Flash, OpenAI-compatible).

Provides a thin ``complete(prompt, system)`` interface used by the rule-citation
relevance judge, the Streamlit RAG-chat tab, and LightRAG's entity-extraction /
summary LLM. DeepSeek's API is OpenAI-compatible, so we use the OpenAI client
when available and fall back to raw urllib if the SDK is missing.

Reads from env (.env / os.environ):
  HUANYU_BULK_API_KEY       preferred key (== DEEPSEEK_API_KEY)
  HUANYU_BULK_MODEL         deepseek-v4-flash (default)
  HUANYU_BULK_BASE_URL      https://api.deepseek.com/v1
  HUANYU_BULK_TEMPERATURE   default 0.0
  HUANYU_BULK_MAX_TOKENS    default 1024

If no key is configured, the client enters **stub mode**: every ``complete``
returns a canned template answer and sets ``self.degraded = True`` so callers
(verify_rule_citations relevance layer, Streamlit chat) can gracefully degrade
instead of crashing the build.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass


@dataclass
class ChatResponse:
    text: str
    degraded: bool = False


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

        if provider == "stub":
            self.degraded = True
            self.api_key = ""
            self.base_url = ""
            self.model = "stub"
            self.temperature = temperature if temperature is not None else 0.0
            self.max_tokens = max_tokens or 1024
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
        # therefore starves the final content (empty ``content`` responses).
        # Floor the budget so short-answer callers still get real text.
        if "bigmodel" in (self.base_url or "") and "glm" in self.model.lower():
            self.max_tokens = max(self.max_tokens, 2048)

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
                text = self._chat(messages)
                if text and text.strip():
                    return ChatResponse(text=text, degraded=False)
                last_err = "empty content from model (transient)"
            except Exception as e:
                last_err = e
            time.sleep(1.0 * (attempt + 1))
        # network / API failure → degrade rather than crash the build
        return ChatResponse(text=f"[llm error] {last_err}", degraded=True)

    # ------------------------------------------------------------------ #
    # transport
    # ------------------------------------------------------------------ #
    def _chat(self, messages: list[dict[str, str]]) -> str:
        """Try the OpenAI SDK first, fall back to raw urllib."""
        try:
            from openai import OpenAI  # type: ignore
            client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            resp = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return resp.choices[0].message.content or ""
        except ImportError:
            pass
        # raw urllib fallback (no openai SDK installed)
        return self._chat_urllib(messages)

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
