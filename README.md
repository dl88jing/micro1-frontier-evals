# PyScope — Frontier LEGB / Class-Body Evals

Solo entry for the **micro1 Eval Hackathon** (HackerRank).

**Author:** Dylan Ler · **Affiliation:** Green Robin Labs · **Handle:** Northbridge

Ten original, automatically graded tasks that probe **CPython 3.13 class-body scoping** (LEGB traps): list/gen comprehensions inside `class`, nested function locals that shadow outer names, annotation evaluation order, decorator/default capture, cooperative `super()` MRO, `__bool__` vs `__len__`, and a DST/`datetime` footgun.

## Empirical results

| Model | Pass / Total | Pass rate |
|---|---|---|
| Muse Wonder 1.0 | 8/10 | 80% |
| Muse Spark Open | 8/10 | 80% |
| Oracle (ground truth) | 10/10 | 100% |

Full matrix: [`results/RESULTS.md`](results/RESULTS.md) · Live page: see repo README / Vercel after deploy.

Wonder misses class-scope listcomp free-var rules; Spark misses whole-body `NameError` binding in nested classes.

## Layout

```
tasks/NN_name/     prompt.md  answer.json  grade.py  rationale.md  task.json  [snippet.py]
graders/           shared JSON grader (common.py) + oracle runner
scripts/           build_tasks.py, run_models.py, probes
results/           RESULTS.md, summary.json, grade_oracle.json
web/               static results page (Vercel)
video/             HyperFrames storyboard + Kokoro VO script
submission.md      HackerRank submission checklist
```

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python graders/run_all.py          # oracle must be 10/10
# optional empirical re-run (API keys — see .env.example):
.venv/bin/python scripts/run_models.py
```

Each task asks the model to emit:

```
FINAL_ANSWER: {"stdout": "..."}   # or structured JSON for task 10
```

Graders parse that JSON and exact-match against `answer.json` (stdout normalized for trailing newlines / escaped `\n`).

## Why these fail frontiers

Class bodies are **not** enclosing scopes for nested functions / comprehensions. Defaults and annotations *do* see class locals. Nested assignment makes a name local for the whole class body (`NameError`). Same-`tzinfo` datetime arithmetic uses wall clocks, not absolute time. Models trained on “LEGB” slogans still conflate these cases.

## License

MIT — original prompts, graders, and rationale. No proprietary Adobe material. Affiliation: **Green Robin Labs** only.
