"""Execution + evidence collection for PromptForge Demo v0.1."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path


def load_task(task_dir: Path) -> dict:
    task_file = task_dir / "task.json"
    with task_file.open("r", encoding="utf-8") as fh:
        task = json.load(fh)
    task["_dir"] = str(task_dir)
    return task


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def build_prompt(task_dir: Path, candidate: dict, baseline_code: str, tests_code: str) -> str:
    prompt_path = task_dir / candidate["prompt"]
    template = read_text(prompt_path)
    return template.replace("{{BASELINE}}", baseline_code).replace("{{TESTS}}", tests_code)


def extract_python_block(text: str) -> str:
    """Extract the largest python code block from a model response."""
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", text, flags=re.S)
    if not blocks:
        # accept responses that are pure code without fences, but require FastAPI content
        if "FastAPI" in text and ("app = FastAPI" in text or "from fastapi" in text):
            return text.strip()
        raise ValueError("no fenced python code block found")
    blocks.sort(key=len, reverse=True)
    code = blocks[0].strip()
    if "FastAPI" not in code:
        raise ValueError("extracted block does not look like a FastAPI module")
    return code


def run_pytest(repo_dir: Path, python_exe: str, expected_total: int, timeout: int = 180) -> dict:
    start = time.time()
    proc = subprocess.run(
        [python_exe, "-m", "pytest", "-q"],
        cwd=str(repo_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=timeout,
    )
    duration_ms = int((time.time() - start) * 1000)
    output = (proc.stdout or "") + "\n" + (proc.stderr or "")
    passed = 0
    failed = 0
    m = re.search(r"(\d+)\s+passed", output)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+)\s+failed", output)
    if m:
        failed = int(m.group(1))
    failed_cases = sorted(set(re.findall(r"FAILED\s+\S+::(\w+)", output)))
    if failed_cases == [] and failed:
        # pytest -q prints "FAILED tests/...::test_x - ..." on newer versions; fallback scan
        failed_cases = sorted(set(re.findall(r"::(test_\w+)", output)))
    status = "passed" if proc.returncode == 0 and passed >= expected_total else "failed"
    return {
        "status": status,
        "returncode": proc.returncode,
        "passed": passed,
        "total": expected_total,
        "failed": failed,
        "failed_cases": failed_cases,
        "duration_ms": duration_ms,
        "output_tail": output[-4000:],
    }


def prepare_repo(task_dir: Path, baseline: str) -> Path:
    repo = task_dir / baseline
    tmp = Path(tempfile.mkdtemp(prefix="promptforge-cand-"))
    dst = tmp / "repo"
    shutil.copytree(
        repo,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"),
    )
    return dst


def apply_candidate(repo_dir: Path, code: str) -> None:
    target = repo_dir / "app" / "main.py"
    target.write_text(code, encoding="utf-8")


def run_baseline(task: dict, python_exe: str) -> dict:
    repo = prepare_repo(Path(task["_dir"]), task["baseline_repo"])
    try:
        return run_pytest(repo, python_exe, len(task["acceptance"]))
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)


def run_candidate(task: dict, candidate: dict, code: str, python_exe: str) -> dict:
    repo = prepare_repo(Path(task["_dir"]), task["baseline_repo"])
    try:
        apply_candidate(repo, code)
        return run_pytest(repo, python_exe, len(task["acceptance"]))
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)
