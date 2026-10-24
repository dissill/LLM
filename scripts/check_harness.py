"""Verify the demo harness: baseline must fail, reference must pass 6/6."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASK = ROOT / "tasks" / "fastapi-todo" / "v0.1"


def run_pytest(repo: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(repo),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=180,
    )


def main() -> int:
    repo = TASK / "repo"
    tmp = ROOT / ".harness-tmp"
    if tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)

    work = tmp / "baseline"
    shutil.copytree(repo, work, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    base = run_pytest(work)
    print("== baseline ==")
    print(base.stdout[-1200:])
    if base.returncode == 0:
        print("ERROR: baseline should fail before the feature is implemented")
        return 1

    ref = tmp / "reference"
    shutil.copytree(repo, ref, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    (ref / "app" / "main.py").write_text((TASK / "reference" / "main.py").read_text(encoding="utf-8"), encoding="utf-8")
    got = run_pytest(ref)
    print("== reference ==")
    print(got.stdout[-1200:])
    if got.returncode != 0:
        print("ERROR: reference solution does not pass all acceptance tests")
        return 1
    if "6 passed" not in got.stdout:
        print("ERROR: expected 6 passed in reference run")
        return 1

    shutil.rmtree(tmp, ignore_errors=True)
    print("OK: baseline fails, reference passes 6/6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
