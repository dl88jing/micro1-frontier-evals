#!/usr/bin/env python3
"""Run PyScope tasks against Muse Wonder + Muse Spark Open."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "graders"))
from common import list_tasks, load_json, grade_payload  # type: ignore

RESULTS = ROOT / "results"
RAW = RESULTS / "raw"
RAW.mkdir(parents=True, exist_ok=True)
PROGRESS = RESULTS / "summary.json"


def load_clients():
    clients = {}
    meta = Path("/workspace/meta-hack/.meta_api_key")
    if meta.exists():
        clients["muse-wonder-1.0"] = (
            OpenAI(api_key=meta.read_text().strip(), base_url="https://api.meta.ai/v1", timeout=400),
            "muse-wonder-1.0",
        )
    baseten = Path("/home/box/.config/seefix/baseten.env")
    if baseten.exists():
        env = {
            l.split("=", 1)[0]: l.split("=", 1)[1].strip()
            for l in baseten.read_text().splitlines()
            if "=" in l and not l.startswith("#")
        }
        clients["muse-spark-open-1026"] = (
            OpenAI(api_key=env["BASETEN_API_KEY"], base_url=env["BASETEN_BASE_URL"], timeout=400),
            env.get("BASETEN_MODEL", "meta-models/muse-spark-open-1026"),
        )
    return clients


def ask(client: OpenAI, model: str, prompt: str) -> tuple[str, int]:
    r = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=8192,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are predicting exact CPython 3.13 semantics. "
                    "Reason carefully, then end with one line: FINAL_ANSWER: <compact json>."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    text = r.choices[0].message.content or ""
    tok = getattr(r.usage, "completion_tokens", 0) or 0
    return text, tok


def save(rows):
    summary = {"rows": rows, "by_model": {}}
    for label in sorted({r["model"] for r in rows}):
        subset = [r for r in rows if r["model"] == label]
        summary["by_model"][label] = {
            "pass": sum(1 for r in subset if r["pass"]),
            "total": len(subset),
            "rate": sum(1 for r in subset if r["pass"]) / max(1, len(subset)),
        }
    PROGRESS.write_text(json.dumps(summary, indent=2) + "\n")
    lines = ["# PyScope LEGB results", ""]
    lines.append("| Task | Model | Pass | Detail |")
    lines.append("|---|---|---|---|")
    for r in rows:
        mark = "PASS" if r["pass"] else "FAIL"
        detail = r["detail"].replace("|", "/").replace("\n", " ")[:140]
        lines.append(f"| {r['task']} | {r['model']} | {mark} | {detail} |")
    lines.append("")
    for m, s in summary["by_model"].items():
        lines.append(f"- **{m}**: {s['pass']}/{s['total']} = {100*s['rate']:.0f}% pass")
    (RESULTS / "RESULTS.md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> None:
    clients = load_clients()
    rows = []
    if PROGRESS.exists():
        try:
            prev = json.loads(PROGRESS.read_text())
            if isinstance(prev, dict) and "rows" in prev:
                # only keep pyscope rows
                rows = [r for r in prev["rows"] if str(r.get("task", "")).startswith(("0", "1"))]
                # drop SpecCascade leftovers
                rows = [r for r in rows if "_" in r["task"] and not r["task"].startswith("01_timezone")]
        except Exception:
            rows = []

    done = {(r["task"], r["model"]) for r in rows}
    for task in list_tasks():
        prompt = (task / "prompt.md").read_text()
        expected = load_json(task / "answer.json")
        for label, (client, model) in clients.items():
            if (task.name, label) in done:
                print(f"SKIP {task.name} {label}", flush=True)
                continue
            print(f"RUN {task.name} {label}...", flush=True)
            t0 = time.time()
            try:
                text, tok = ask(client, model, prompt)
                err = None
            except Exception as e:
                text, tok, err = f"ERROR: {e}", 0, str(e)
            elapsed = time.time() - t0
            raw_path = RAW / f"{task.name}__{label}.txt"
            raw_path.write_text(text)
            graded = grade_payload(text, expected)
            row = {
                "task": task.name,
                "model": label,
                "pass": graded["pass"],
                "detail": graded["detail"],
                "tokens": tok,
                "seconds": round(elapsed, 2),
                "error": err,
                "raw": str(raw_path.relative_to(ROOT)),
            }
            rows.append(row)
            save(rows)
            print(f"  -> {'PASS' if row['pass'] else 'FAIL'} {row['detail'][:140]}", flush=True)

    summary = save(rows)
    print(json.dumps(summary["by_model"], indent=2), flush=True)
    (RESULTS / "DONE").write_text("ok\n")


if __name__ == "__main__":
    main()
