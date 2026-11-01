"""Shared grading helpers for PyScope LEGB eval."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = ROOT / "tasks"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_final_answer(text: str) -> str:
    if not text:
        return ""
    m = re.search(r"FINAL_ANSWER\s*:\s*(.*)\s*\Z", text, flags=re.I | re.S)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"```(?:json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```\s*\Z", text)
    if m2:
        return m2.group(1).strip()
    return text.strip()


def parse_json_answer(text: str) -> Any | None:
    raw = extract_final_answer(text)
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw.strip())
    for starter in ("{", "["):
        i = raw.find(starter)
        if i >= 0:
            chunk = raw[i:]
            try:
                return json.loads(chunk)
            except json.JSONDecodeError:
                for j in range(len(chunk), 0, -1):
                    try:
                        return json.loads(chunk[:j])
                    except json.JSONDecodeError:
                        continue
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _norm_stdout(v: Any) -> str:
    if v is None:
        return ""
    s = v if isinstance(v, str) else str(v)
    # Accept literal newlines or escaped \n sequences from models
    if "\\n" in s and "\n" not in s.rstrip("\n"):
        s = s.replace("\\n", "\n")
    return s.rstrip("\n")


def grade_payload(payload: str | Any, expected: dict) -> dict:
    """Grade a FINAL_ANSWER payload (str or already-parsed) against expected dict."""
    if isinstance(payload, str):
        pred = parse_json_answer(payload if "FINAL_ANSWER" in payload else f"FINAL_ANSWER: {payload}")
        # also try parsing payload directly
        if pred is None:
            pred = parse_json_answer(f"FINAL_ANSWER: {payload}")
    else:
        pred = payload

    if pred is None:
        return {"pass": False, "detail": "could not parse JSON from model output", "pred": None}

    if not isinstance(pred, dict):
        return {"pass": False, "detail": f"expected JSON object, got {type(pred).__name__}", "pred": pred}

    mismatches = []
    for key, exp in expected.items():
        got = pred.get(key)
        if key == "stdout":
            if _norm_stdout(got) != _norm_stdout(exp):
                mismatches.append(f"stdout: got={_norm_stdout(got)!r} expected={_norm_stdout(exp)!r}")
        elif isinstance(exp, float):
            try:
                if abs(float(got) - exp) > 1e-9:
                    mismatches.append(f"{key}: got={got!r} expected={exp!r}")
            except (TypeError, ValueError):
                mismatches.append(f"{key}: got={got!r} expected={exp!r}")
        else:
            if got != exp:
                mismatches.append(f"{key}: got={got!r} expected={exp!r}")

    if mismatches:
        return {"pass": False, "detail": "; ".join(mismatches), "pred": pred}
    return {"pass": True, "detail": "exact match", "pred": pred}


def list_tasks() -> list[Path]:
    return sorted(p for p in TASKS_DIR.iterdir() if p.is_dir() and (p / "task.json").exists())
