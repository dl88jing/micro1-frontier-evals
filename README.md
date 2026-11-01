# PyScope — Frontier LEGB / Class-Body Evals (hardened)

Solo entry for the **micro1 Eval Hackathon** (HackerRank).

**Author:** Dylan Ler · **Affiliation:** Green Robin Labs · **Handle:** Northbridge

Ten original, automatically graded tasks that probe **CPython 3.13 class-body scoping**: LEGB traps, PEP 709 comprehension inlining edges, PEP 695 type-parameter scopes, PEP 572 walrus-in-class SyntaxError, default LOAD_NAME fallthrough vs closures, and whole-body class-local `NameError`s.

## Headline results (measured)

Protocol: temperature 0, **3 trials / task / model**, report **pass@1** (mean trial pass rate). Oracle **10/10**. Source of truth: [`results/summary.json`](results/summary.json).

| Model | pass@1 mean | all-pass | all-fail |
|---|---|---|---|
| Muse Wonder 1.0 (Meta) | **6.7%** | 0/10 | 9/10 |
| Muse Spark Open (Baseten) | **13.3%** | 0/10 | 8/10 |
| Beam-1.0-501B-A23B (Reflection) | **76.7%** | 5/10 | 0/10 |

Nebius Token Factory key is only on Vercel as a redacted secret and was **not** used for the submitted matrix.

Live results: [pyscope-evals.vercel.app](https://pyscope-evals.vercel.app) · Full matrix: [`results/RESULTS.md`](results/RESULTS.md) · Submitted zip: [v1.1.0](https://github.com/dl88jing/micro1-frontier-evals/releases/tag/v1.1.0)

## Demo video

Simulated-user screen recording of the live results page plus a terminal session running the oracle grader.

[![PyScope demo](https://img.youtube.com/vi/sVFSqWVqjPk/maxresdefault.jpg)](https://youtu.be/sVFSqWVqjPk)

- **YouTube:** https://youtu.be/sVFSqWVqjPk
- **MP4 (fallback):** [pyscope-demo-v2.mp4](https://github.com/dl88jing/micro1-frontier-evals/releases/download/v1.2.0/pyscope-demo-v2.mp4)

## For judges

**Reproduce in one minute (no API keys):**

```bash
git clone https://github.com/dl88jing/micro1-frontier-evals.git
cd micro1-frontier-evals
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v   # grader + task-shape + matrix guards
.venv/bin/python graders/run_all.py                 # must print oracle pass_count 10 / total 10
```

**What that proves**

- Each of the 10 tasks has `prompt.md`, `answer.json`, `grade.py`, `rationale.md`, `task.json`.
- The JSON grader accepts the oracle answer for every task (no false fails on ground truth).
- Headline pass@1 numbers in this README match `results/summary.json` (Wonder 6.7% / Spark 13.3% / Beam 76.7%).

**Optional empirical re-run (API keys):** copy `.env.example` → `.env`, then `.venv/bin/python scripts/run_models.py` (3 trials → pass@1). Keys are never committed.

**Why this eval:** frontier models often “know” LEGB slogans but mis-predict class-body binding (listcomp free vars skipping class scope, assignment making a name local for the whole body, PEP 695 defaults resolving to the module, walrus-in-class SyntaxError). Failures are meaningful for anyone shipping Python tooling, agent coding, or static analysis — not riddles.

Method diagram: [`docs/method.md`](docs/method.md).

## Method

```mermaid
flowchart LR
  A[CPython 3.13<br/>class-body / LEGB expertise] --> B[Candidate traps]
  B --> C[Probe Wonder · Spark · Beam]
  C --> D{≥2 models fail?}
  D -->|yes| E[Hardened task]
  D -->|no| F[Drop / rewrite]
  E --> G[Oracle 10/10]
  G --> H[pass@1 · 3 trials · temp 0]
```

Tasks 04–10 were selected from multi-model probes where **≥2** of Wonder/Spark/Beam failed (see `results/probe_candidates.json`, `results/probe_wave2.json`).

## Tasks

| # | Id | Trap |
|---|---|---|
| 01 | `listcomp_class` | listcomp free vars skip class scope |
| 02 | `nested_listcomp` | nested comps + defaults disagree |
| 03 | `class_local_bind` | assign → whole-body local → NameError |
| 04 | `default_shadow` | default `a=x` then class assign → NameError |
| 05 | `genexp_late_bind` | class genexp/listcomp close over module `n` |
| 06 | `default_fallthrough` | default LOAD_NAME → global; body closes local |
| 07 | `method_reads_shadow` | `y=x+1` before class `x=…` → NameError |
| 08 | `nested_two_shadows` | two later assigns → NameError on first read |
| 09 | `pep695_type_param` | PEP 695: `first=T` is module, not type param |
| 10 | `walrus_and_default` | walrus-in-class SyntaxError \| default NameError |

## Layout

```
tasks/NN_name/     prompt.md  answer.json  grade.py  rationale.md  task.json  snippet.py
graders/           shared JSON grader (common.py) + oracle runner
tests/             unittest suite (CI)
scripts/           build_tasks.py, run_models.py, write_hardened_task.py, probes
results/           RESULTS.md, summary.json, probe_*.json
docs/method.md     architecture / selection flowchart
web/               static results page (Vercel)
video/             HyperFrames storyboard + Kokoro VO script
submission.md      HackerRank submission checklist
.github/workflows  CI: unittest + oracle on 3.11–3.13
```

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python graders/run_all.py          # oracle must be 10/10
# optional empirical re-run (API keys — see .env.example):
.venv/bin/python scripts/run_models.py       # 3 trials → pass@1
```

Each task asks the model to emit:

```
FINAL_ANSWER: {"stdout": "..."}
```

## License

MIT — original prompts, graders, and rationale. No proprietary Adobe material. Affiliation: **Green Robin Labs** only. Public copy uses Northbridge / Avery & Morgan pseudonyms only.
