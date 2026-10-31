# -*- coding: utf-8 -*-
"""Minimal, dependency-free validator for the IAOV example sequence.

For full JSON Schema validation install `jsonschema`; this script is intentionally
usable in the demo's minimal venv:
  python spec/iaov/validate_iaov.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCHEMA = ROOT / "iaov.schema.json"
SEQ = ROOT / "example.sequence.jsonl"

REQUIRED = {"schema_version", "message_id", "trace_id", "task_id", "candidate_id",
            "endpoint_id", "kind", "from", "to", "timestamp", "contract_hash",
            "permission_scope", "budget", "payload"}
KINDS = {"intent": "goal", "action": "tool", "observation": "status", "verdict": "decision"}
PAYLOAD_REQUIRED = {
    "intent": {"goal", "acceptance", "constraints"},
    "action": {"tool", "arguments", "timeout_ms", "idempotency_key"},
    "observation": {"status", "summary", "evidence_refs", "metrics", "artifacts"},
    "verdict": {"decision", "score", "confidence", "evidence_refs", "rationale"},
}
HASH_RE = re.compile(r"^sha256:[a-f0-9]{64}$")


def fail(msg: str) -> None:
    print("FAIL:", msg)
    raise SystemExit(1)


def check_envelope(obj: dict, line_no: int) -> None:
    missing = REQUIRED - set(obj)
    if missing:
        fail(f"line {line_no}: missing {sorted(missing)}")
    if obj["schema_version"] != "iaov/1.0":
        fail(f"line {line_no}: schema_version")
    if obj["kind"] not in KINDS:
        fail(f"line {line_no}: kind")
    for side in ("from", "to"):
        ep = obj[side]
        if not isinstance(ep, dict) or not ep.get("role") or not ep.get("endpoint_id"):
            fail(f"line {line_no}: {side} endpoint")
    if not HASH_RE.match(obj["contract_hash"]):
        fail(f"line {line_no}: contract_hash")
    budget = obj["budget"]
    for key in ("max_tokens", "used_tokens", "max_cny"):
        if key not in budget:
            fail(f"line {line_no}: budget.{key}")
    payload = obj["payload"]
    if not isinstance(payload, dict):
        fail(f"line {line_no}: payload")
    miss = PAYLOAD_REQUIRED[obj["kind"]] - set(payload)
    if miss:
        fail(f"line {line_no}: payload missing {sorted(miss)}")


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        fail("schema $schema")
    if "iaov/1.0" not in json.dumps(schema, ensure_ascii=False):
        fail("schema version")
    lines = [ln for ln in SEQ.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if len(lines) != 4:
        fail(f"expected 4 messages, got {len(lines)}")
    kinds = []
    for i, line in enumerate(lines, 1):
        check_envelope(json.loads(line), i)
        kinds.append(json.loads(line)["kind"])
    if kinds != ["intent", "action", "observation", "verdict"]:
        fail(f"sequence order: {kinds}")
    print(f"OK: schema JSON valid; {len(lines)} IAOV messages valid")
    print("OK: sequence = Intent -> Action -> Observation -> Verdict")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
