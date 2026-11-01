#!/usr/bin/env python3
"""Oracle-backed grader: compare FINAL_ANSWER JSON to answer.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "graders"))
from common import extract_final_answer, grade_payload  # type: ignore


def main() -> None:
    task_dir = Path(__file__).resolve().parent
    expected = json.loads((task_dir / "answer.json").read_text())
    raw = sys.stdin.read() if not sys.argv[1:] else Path(sys.argv[1]).read_text()
    payload = extract_final_answer(raw)
    result = grade_payload(payload, expected)
    print(json.dumps(result))
    sys.exit(0 if result.get("pass") else 1)


if __name__ == "__main__":
    main()
