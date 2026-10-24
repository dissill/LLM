"""Minimal OpenAI-compatible model client for the demo.

Reads configuration from environment variables only; never stores secrets.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request


class ModelError(RuntimeError):
    pass


def chat(model: str, messages: list[dict], timeout: int = 180) -> dict:
    """Call an OpenAI-compatible /chat/completions endpoint.

    Required env:
      MODEL_BASE_URL  e.g. https://<endpoint>/v2
      MODEL_API_KEY   API key
    """
    base = os.environ.get("MODEL_BASE_URL", "").rstrip("/")
    key = os.environ.get("MODEL_API_KEY", "")
    if not base or not key:
        raise ModelError("MODEL_BASE_URL / MODEL_API_KEY are not set")

    url = base + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + key,
        },
        method="POST",
    )
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")[:300]
        raise ModelError(f"HTTP {exc.code}: {detail}") from exc
    except Exception as exc:  # network errors
        raise ModelError(f"{type(exc).__name__}: {exc}") from exc

    try:
        data = json.loads(raw)
        content = data["choices"][0]["message"]["content"]
    except Exception as exc:
        raise ModelError(f"invalid response: {raw[:300]}") from exc

    return {
        "content": content,
        "usage": data.get("usage") or {},
        "latency_ms": int((time.time() - start) * 1000),
        "model": model,
    }
