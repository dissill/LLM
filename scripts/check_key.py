# -*- coding: utf-8 -*-
"""Check a DeepSeek API key without printing it.

Usage (PowerShell):
  $secure = Read-Host "DeepSeek API key" -AsSecureString
  $env:MODEL_API_KEY = [System.Net.NetworkCredential]::new("", $secure).Password
  python scripts/check_key.py

Uses a 1-token chat request to verify auth; never stores or echoes the key.
"""
from __future__ import annotations

import getpass
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("MODEL_BASE_URL", "https://api.deepseek.com").rstrip("/")
MODEL = os.environ.get("MODEL_NAME", "deepseek-flash")


def main() -> int:
    key = os.environ.get("MODEL_API_KEY") or getpass.getpass("DeepSeek API key (hidden): ")
    if not key:
        print("FAIL: empty key")
        return 2
    print("key_len =", len(key))
    if not key.startswith("sk-"):
        print("WARN: DeepSeek keys usually start with 'sk-'; check you copied the full key.")
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 1,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        BASE + "/chat/completions",
        data=payload,
        headers={
            "Authorization": "Bearer " + key,
            "Content-Type": "application/json",
            "User-Agent": "promptforge-key-check",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="ignore"))
        ok = bool(data.get("choices"))
        print("OK: auth accepted" if ok else "WARN: HTTP 200 but no choices")
        return 0 if ok else 3
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        print(f"FAIL: HTTP {exc.code}")
        print(body[:600])
        return 2
    except Exception as exc:  # noqa: BLE001 - CLI diagnostic
        print("FAIL:", type(exc).__name__, str(exc)[:300])
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
