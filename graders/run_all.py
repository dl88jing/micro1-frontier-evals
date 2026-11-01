#!/usr/bin/env python3
"""Grade oracle answers and optional model raw outputs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import list_tasks, load_json, grade_payload

ROOT = Path(__file__).resolve().parents[1]


def grade_oracle() -> dict:
    rows = []
    for task in list_tasks():
        expected = load_json(task / "answer.json")
        # Oracle: feed the expected JSON as if the model emitted it
        fake = "FINAL_ANSWER: " + json.dumps(expected)
        result = grade_payload(fake, expected)
        rows.append({"task": task.name, "pass": result["pass"], "detail": result["detail"]})
    return {"oracle": rows, "pass_count": sum(1 for r in rows if r["pass"]), "total": len(rows)}


def main() -> None:
    report = grade_oracle()
    out = ROOT / "results" / "grade_oracle.json"
    out.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    if report["pass_count"] != report["total"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
