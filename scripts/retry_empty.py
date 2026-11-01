#!/usr/bin/env python3
"""Re-run rows that returned empty / unparseable output (API flake)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "graders"))
from common import load_json, grade_payload  # type: ignore
import run_models as rm  # type: ignore

RESULTS = ROOT / "results"
RAW = RESULTS / "raw"
summary = json.loads((RESULTS / "summary.json").read_text())
rows = summary["rows"]
clients = rm.load_clients()

def is_flake(row):
    if row.get("error"):
        return True
    raw = ROOT / row["raw"]
    if not raw.exists() or raw.stat().st_size == 0:
        return True
    text = raw.read_text()
    if "FINAL_ANSWER" not in text and grade_payload(text, load_json(ROOT / "tasks" / row["task"] / "answer.json"))["pred"] is None:
        return True
    return False

flakes = [r for r in rows if is_flake(r)]
print(f"Retrying {len(flakes)} flake rows...", flush=True)

for row in flakes:
    label = row["model"]
    client, model = clients[label]
    task = ROOT / "tasks" / row["task"]
    prompt = (task / "prompt.md").read_text()
    expected = load_json(task / "answer.json")
    text, tok, err = "", 0, None
    for attempt in range(3):
        print(f"RETRY {row['task']} {label} attempt {attempt+1}", flush=True)
        try:
            text, tok = rm.ask(client, model, prompt)
            err = None
        except Exception as e:
            text, tok, err = f"ERROR: {e}", 0, str(e)
        if text.strip() and "ERROR:" not in text[:20]:
            break
        time.sleep(2)
    raw_path = RAW / f"{row['task']}__{label}.txt"
    raw_path.write_text(text)
    graded = grade_payload(text, expected)
    row.update({
        "pass": graded["pass"],
        "detail": graded["detail"],
        "tokens": tok,
        "error": err,
        "retried": True,
    })
    rm.save(rows)
    print(f"  -> {'PASS' if row['pass'] else 'FAIL'} {row['detail'][:140]}", flush=True)

summary = rm.save(rows)
print(json.dumps(summary["by_model"], indent=2))
