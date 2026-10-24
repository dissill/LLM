"""PromptForge Demo v0.1 CLI.

Usage:
  python -m promptforge.cli --task tasks/fastapi-todo/v0.1 --out runs/demo-001
  python -m promptforge.cli --task tasks/fastapi-todo/v0.1 --out runs/demo-replay --replay
  python -m promptforge.cli --task tasks/fastapi-todo/v0.1 --self-check
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from . import model_client, runner

ROOT = Path(__file__).resolve().parent.parent


def _price(task: dict) -> tuple[float | None, float | None]:
    p = task.get("pricing") or {}
    in_price = p.get("input_per_m_cny")
    out_price = p.get("output_per_m_cny")
    if in_price is None:
        in_price = _env_float("MODEL_PRICE_IN_CNY_PER_M")
    if out_price is None:
        out_price = _env_float("MODEL_PRICE_OUT_CNY_PER_M")
    return in_price, out_price


def _env_float(name: str) -> float | None:
    raw = os.environ.get(name)
    try:
        return float(raw) if raw else None
    except ValueError:
        return None


def _cost(usage: dict, in_price: float | None, out_price: float | None) -> dict:
    tin = usage.get("prompt_tokens")
    tout = usage.get("completion_tokens")
    cny = None
    if tin is not None and tout is not None and in_price is not None and out_price is not None:
        cny = round(tin / 1e6 * in_price + tout / 1e6 * out_price, 4)
    return {"tokens_in": tin, "tokens_out": tout, "cny": cny,
            "price_snapshot": {"input_per_m_cny": in_price, "output_per_m_cny": out_price}}


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def self_check(task_dir: Path) -> int:
    task = runner.load_task(task_dir)
    python_exe = sys.executable
    print("== harness self-check ==")
    base = runner.run_baseline(task, python_exe)
    print("baseline:", base["status"], "passed=%s/%s" % (base["passed"], base["total"]),
          "failed_cases=%s" % base["failed_cases"])
    if base["status"] == "passed":
        print("ERROR: baseline should fail before the feature is implemented")
        return 1

    repo = runner.prepare_repo(task_dir, task["baseline_repo"])
    try:
        ref = task_dir / "reference" / "main.py"
        runner.apply_candidate(repo, ref.read_text(encoding="utf-8"))
        ref_result = runner.run_pytest(repo, python_exe, len(task["acceptance"]))
    finally:
        import shutil
        shutil.rmtree(repo.parent, ignore_errors=True)
    print("reference:", ref_result["status"], "passed=%s/%s" % (ref_result["passed"], ref_result["total"]))
    if ref_result["status"] != "passed":
        print("ERROR: reference solution does not pass all acceptance tests")
        return 1
    print("OK: baseline fails, reference passes 6/6")
    return 0


def run(task_dir: Path, out_dir: Path, replay: bool) -> int:
    task = runner.load_task(task_dir)
    python_exe = sys.executable
    baseline_code = (task_dir / task["baseline_repo"] / "app" / "main.py").read_text(encoding="utf-8")
    tests_code = (task_dir / task["baseline_repo"] / "tests" / "test_tags_pagination.py").read_text(encoding="utf-8")
    expected_total = len(task["acceptance"])
    in_price, out_price = _price(task)

    out_dir.mkdir(parents=True, exist_ok=True)

    base = runner.run_baseline(task, python_exe)
    _write_json(out_dir / "evidence" / "baseline.json", {"candidate": "baseline", "source": "execution", "tests": base})
    print("baseline: %s/%s passed" % (base["passed"], base["total"]))

    evidences = []
    for cand in task["candidates"]:
        cid = cand["id"]
        print("== candidate %s (%s / %s) ==" % (cid, cand["model"], cand["strategy"]))
        cand_dir = out_dir / "candidates" / cid
        cand_dir.mkdir(parents=True, exist_ok=True)

        if replay:
            cache = task_dir / "cache" / cid / "main.py"
            if not cache.exists():
                print("ERROR: replay cache missing:", cache)
                return 2
            code = cache.read_text(encoding="utf-8")
            meta = {"candidate": cid, "source": "replay", "model": cand["model"],
                    "strategy": cand["strategy"], "note": "replay of a previously recorded real response"}
            usage = {}
            model_latency = None
        else:
            prompt = runner.build_prompt(task_dir, cand, baseline_code, tests_code)
            (cand_dir / "prompt.md").write_text(prompt, encoding="utf-8")
            try:
                resp = model_client.chat(cand["model"], [{"role": "user", "content": prompt}])
            except model_client.ModelError as exc:
                print("ERROR: model call failed:", exc)
                return 3
            code = runner.extract_python_block(resp["content"])
            usage = resp.get("usage") or {}
            model_latency = resp.get("latency_ms")
            meta = {"candidate": cid, "source": "model", "model": cand["model"],
                    "strategy": cand["strategy"], "usage": usage, "model_latency_ms": model_latency}

        (cand_dir / "main.py").write_text(code, encoding="utf-8")
        _write_json(cand_dir / "meta.json", meta)

        tests = runner.run_candidate(task, cand, code, python_exe)
        cost = _cost(usage, in_price, out_price)
        evidence = {
            "candidate": cid,
            "source": meta["source"],
            "model": cand["model"],
            "strategy": cand["strategy"],
            "tests": tests,
            "cost": cost,
            "model_latency_ms": model_latency,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "task_id": task["task_id"],
        }
        _write_json(out_dir / "evidence" / ("%s.json" % cid), evidence)
        evidences.append(evidence)
        print("  tests: %s passed=%s/%s failed=%s runtime=%sms cost=%s"
              % (tests["status"], tests["passed"], tests["total"], tests["failed"], tests["duration_ms"], cost["cny"]))

    _write_decision(out_dir, evidences)
    print("wrote:", out_dir / "decision.md")
    return 0


def _write_decision(out_dir: Path, evidences: list[dict]) -> None:
    def key(e: dict):
        t = e["tests"]
        return (t["passed"], -(e.get("cost", {}).get("cny") or 0), -t["duration_ms"])

    ranked = sorted(evidences, key=key, reverse=True)
    passing = [e for e in ranked if e["tests"]["status"] == "passed"]
    best = passing[0] if passing else None

    lines = ["# PromptForge Demo v0.1 — 决策卡", ""]
    if best:
        lines.append("**推荐：候选 %s（%s / %s）** — 测试 %s/%s 通过（硬约束满足）。"
                     % (best["candidate"], best["model"], best["strategy"],
                        best["tests"]["passed"], best["tests"]["total"]))
    else:
        lines.append("**无候选满足硬约束（6/6）** — 建议调整提示策略或更换模型后重跑。")
    lines.append("")
    lines.append("| 候选 | 模型 | 策略 | 测试 | 耗时 | token 费用 | 结论 |")
    lines.append("|---|---|---|---|---|---|---|")
    for e in ranked:
        t = e["tests"]
        verdict = "推荐" if best and e is best else ("达标备选" if t["status"] == "passed" else "观察/不推荐")
        cost = e.get("cost", {}).get("cny")
        lines.append("| %s | %s | %s | %s/%s | %sms | %s | %s |"
                     % (e["candidate"], e["model"], e["strategy"], t["passed"], t["total"],
                        t["duration_ms"], ("¥%s" % cost) if cost is not None else "未配置价格", verdict))
    lines.append("")
    if best:
        failed = best["tests"].get("failed_cases") or []
        lines.append("证据引用：pytest 输出、候选代码、耗时与 token usage 均在 `evidence/` 与 `candidates/` 下。")
        lines.append("")
        lines.append("> 说明：Demo v0.1 仅做单任务单轮决策，样本少，结论仅用于演示；不宣称统计显著性。")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "decision.md").write_text("\n".join(lines), encoding="utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="PromptForge Demo v0.1 CLI")
    parser.add_argument("--task", default=str(ROOT / "tasks" / "fastapi-todo" / "v0.1"))
    parser.add_argument("--out", default=str(ROOT / "runs" / "demo-001"))
    parser.add_argument("--replay", action="store_true", help="use cached candidate code instead of calling models")
    parser.add_argument("--self-check", action="store_true", help="verify harness: baseline fails, reference passes")
    args = parser.parse_args(argv)

    task_dir = Path(args.task).resolve()
    if args.self_check:
        return self_check(task_dir)
    return run(task_dir, Path(args.out).resolve(), args.replay)


if __name__ == "__main__":
    raise SystemExit(main())
