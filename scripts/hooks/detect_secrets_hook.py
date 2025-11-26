"""Custom detect-secrets hook that works on Windows.

This script ensures the baseline file exists (and is valid JSON) before
executing the standard ``detect-secrets`` pre-commit hook via
``python -m detect_secrets.pre_commit_hook``.  Running the hook through
Python instead of the compiled ``detect-secrets-hook.exe`` avoids
PowerShell redirection quirks when reading ``.secrets.baseline`` and lets
us post-process stdout to strip warnings emitted ahead of the JSON payload.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / ".secrets.baseline"


def _extract_json_payload(raw_output: str) -> dict[str, Any]:
    """Strip non-JSON noise from detect-secrets output and parse it."""

    start = raw_output.find("{")
    end = raw_output.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("Failed to locate JSON payload in detect-secrets output")

    payload = raw_output[start : end + 1]
    return json.loads(payload)


def _write_baseline(obj: dict[str, Any]) -> None:
    BASELINE.write_text(
        json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _generate_baseline() -> int:
    """Generate a fresh baseline if it is missing or invalid."""
    result = subprocess.run(
        [sys.executable, "-m", "detect_secrets", "scan", "--all-files"],
        check=False,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )

    if result.returncode != 0:
        sys.stderr.write("detect-secrets scan failed while creating baseline.\n")
        sys.stderr.write(result.stderr)
        return result.returncode

    try:
        payload = _extract_json_payload(result.stdout)
    except Exception as exc:  # pragma: no cover - defensive guard
        sys.stderr.write(f"Failed to parse detect-secrets output: {exc}\n")
        sys.stderr.write(result.stdout)
        return 1

    _write_baseline(payload)
    return 0


def _ensure_baseline() -> int:
    if not BASELINE.exists():
        print("[detect-secrets] baseline missing, generating a new one...")
        return _generate_baseline()

    try:
        json.loads(BASELINE.read_text(encoding="utf-8"))
    except Exception:
        print("[detect-secrets] baseline invalid, regenerating...")
        return _generate_baseline()

    return 0


def main() -> int:
    status = _ensure_baseline()
    if status != 0:
        return status

    process = subprocess.run(
        [
            sys.executable,
            "-m",
            "detect_secrets.pre_commit_hook",
            "--baseline",
            str(BASELINE),
        ],
        cwd=REPO_ROOT,
        check=False,
    )
    return process.returncode


if __name__ == "__main__":
    raise SystemExit(main())
