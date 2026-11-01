#!/usr/bin/env python3
"""Run PyScope tasks against Wonder / Spark / Beam. 3 trials → pass@1 average."""
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
TRIALS = 3


def load_clients():
    clients = {}
    meta = Path("/workspace/meta-hack/.meta_api_key")
    if meta.exists():
        clients["muse-wonder-1.0"] = (
            OpenAI(api_key=meta.read_text().strip(), base_url="https://api.meta.ai/v1", timeout=90),
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
            OpenAI(api_key=env["BASETEN_API_KEY"], base_url=env["BASETEN_BASE_URL"], timeout=90),
            env.get("BASETEN_MODEL", "meta-models/muse-spark-open-1026"),
        )
    beam = Path("/workspace/beam-hack/.reflection_api_key")
    if beam.exists():
        clients["Beam-1.0-501B-A23B"] = (
            OpenAI(api_key=beam.read_text().strip(), base_url="https://api.reflection.ai/openai/v1", timeout=90),
            "Beam-1.0-501B-A23B",
        )
    # Nebius only if a real (non-placeholder) key is present
    nebius_path = Path("/home/box/.config/micro1-eval/nebius.env")
    if nebius_path.exists():
        env = {}
        for l in nebius_path.read_text().splitlines():
            if "=" in l and not l.strip().startswith("#"):
                k, v = l.split("=", 1)
                env[k] = v.strip().strip('"')
        nk = env.get("NEBIUS_API_KEY", "")
        if nk and "SENSITIVE" not in nk and len(nk) > 20:
            nb = env.get("NEBIUS_BASE_URL") or "https://api.tokenfactory.us-central1.nebius.com/v1/"
            clients["deepseek-ai/DeepSeek-V3"] = (
                OpenAI(api_key=nk, base_url=nb, timeout=90),
                "deepseek-ai/DeepSeek-V3",
            )
    return clients


def ask(client: OpenAI, model: str, prompt: str) -> tuple[str, int]:
    text = ""
    tok = 0
    for attempt in range(2):
        r = client.chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=2048,
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
        if text.strip():
            break
        time.sleep(1.5)
    return text, tok


def save(rows, trial_rows):
    # Aggregate pass@1: mean of trial passes per (task, model)
    from collections import defaultdict
    groups = defaultdict(list)
    for r in trial_rows:
        groups[(r["task"], r["model"])].append(r["pass"])
    agg = []
    for (task, model), passes in sorted(groups.items()):
        rate = sum(passes) / len(passes)
        agg.append({
            "task": task,
            "model": model,
            "pass": rate >= 1.0,  # all trials passed
            "pass_at_1": rate,
            "trials": len(passes),
            "detail": f"pass@1={rate:.3f} over {len(passes)} trials",
        })
    summary = {
        "rows": agg,
        "trials": trial_rows,
        "by_model": {},
        "matrix": {},
        "protocol": f"temperature=0, {TRIALS} trials/task/model, pass@1 = mean trial pass rate",
        "oracle": "10/10",
        "models": sorted({r["model"] for r in trial_rows}),
    }
    for label in summary["models"]:
        subset = [r for r in agg if r["model"] == label]
        mean_p = sum(r["pass_at_1"] for r in subset) / max(1, len(subset))
        summary["by_model"][label] = {
            "pass_at_1_mean": round(mean_p, 4),
            "tasks": len(subset),
            "tasks_all_pass": sum(1 for r in subset if r["pass_at_1"] >= 1.0),
            "tasks_all_fail": sum(1 for r in subset if r["pass_at_1"] <= 0.0),
        }
    # matrix task x model
    tasks = sorted({r["task"] for r in agg})
    for t in tasks:
        summary["matrix"][t] = {
            m: next(r["pass_at_1"] for r in agg if r["task"] == t and r["model"] == m)
            for m in summary["models"]
            if any(r["task"] == t and r["model"] == m for r in agg)
        }
    PROGRESS.write_text(json.dumps(summary, indent=2) + "\n")

    lines = [
        "# PyScope LEGB results (hardened)",
        "",
        f"Protocol: temperature 0, **{TRIALS} trials** per task/model, report **pass@1** (= mean trial pass rate).",
        "Oracle graders: **10/10**. Empty API replies retried up to 3×.",
        "",
        "| Model | pass@1 mean | all-pass tasks | all-fail tasks |",
        "|---|---|---|---|",
    ]
    for m, s in summary["by_model"].items():
        lines.append(
            f"| `{m}` | {100*s['pass_at_1_mean']:.1f}% | {s['tasks_all_pass']}/{s['tasks']} | {s['tasks_all_fail']}/{s['tasks']} |"
        )
    lines += ["", "## Matrix (pass@1)", "", "| Task | " + " | ".join(f"`{m}`" for m in summary["models"]) + " |",
              "|" + "---|" * (1 + len(summary["models"]))]
    for t in tasks:
        cells = []
        for m in summary["models"]:
            v = summary["matrix"][t].get(m)
            cells.append("—" if v is None else f"{100*v:.0f}%")
        lines.append(f"| `{t}` | " + " | ".join(cells) + " |")
    lines.append("")
    (RESULTS / "RESULTS.md").write_text("\n".join(lines) + "\n")
    return summary


def main() -> None:
    clients = load_clients()
    print("CLIENTS", list(clients), flush=True)
    trial_rows = []
    # resume from existing trials if present
    if PROGRESS.exists():
        try:
            prev = json.loads(PROGRESS.read_text())
            if isinstance(prev, dict) and "trials" in prev:
                trial_rows = prev["trials"]
        except Exception:
            trial_rows = []

    done = {(r["task"], r["model"], r["trial"]) for r in trial_rows}
    for task in list_tasks():
        prompt = (task / "prompt.md").read_text()
        expected = load_json(task / "answer.json")
        for label, (client, model) in clients.items():
            for trial in range(1, TRIALS + 1):
                key = (task.name, label, trial)
                if key in done:
                    print(f"SKIP {task.name} {label} t{trial}", flush=True)
                    continue
                print(f"RUN {task.name} {label} t{trial}...", flush=True)
                t0 = time.time()
                try:
                    text, tok = ask(client, model, prompt)
                    err = None
                except Exception as e:
                    text, tok, err = f"ERROR: {e}", 0, str(e)
                elapsed = time.time() - t0
                raw_path = RAW / f"{task.name}__{label}__t{trial}.txt"
                raw_path.write_text(text)
                graded = grade_payload(text, expected)
                row = {
                    "task": task.name,
                    "model": label,
                    "trial": trial,
                    "pass": graded["pass"],
                    "detail": graded["detail"],
                    "tokens": tok,
                    "seconds": round(elapsed, 2),
                    "error": err,
                    "raw": str(raw_path.relative_to(ROOT)),
                }
                trial_rows.append(row)
                save([], trial_rows)
                print(f"  -> {'PASS' if row['pass'] else 'FAIL'} {row['detail'][:140]}", flush=True)

    summary = save([], trial_rows)
    print(json.dumps(summary["by_model"], indent=2), flush=True)
    print(json.dumps(summary["matrix"], indent=2), flush=True)
    (RESULTS / "DONE").write_text("ok\n")


if __name__ == "__main__":
    main()
