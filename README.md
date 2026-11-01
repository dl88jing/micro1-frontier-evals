# PyScope — Frontier LEGB / Class-Body Evals (hardened)

Solo entry for the **micro1 Eval Hackathon** (HackerRank).

**Author:** Dylan Ler · **Affiliation:** Green Robin Labs · **Handle:** Northbridge

Ten original, automatically graded tasks that probe **CPython 3.13 class-body scoping**: LEGB traps, PEP 709 comprehension inlining edges, PEP 695 type-parameter scopes, PEP 572 walrus-in-class SyntaxError, default LOAD_NAME fallthrough vs closures, and whole-body class-local `NameError`s.

## Empirical results

Protocol: temperature 0, **3 trials / task / model**, report **pass@1** (mean trial pass rate). Oracle **10/10**.

| Model | pass@1 mean | all-pass | all-fail |
|---|---|---|---|
| Muse Wonder 1.0 (Meta) | **6.7%** | 0/10 | 9/10 |
| Muse Spark Open (Baseten) | **13.3%** | 0/10 | 8/10 |
| Beam-1.0-501B-A23B (Reflection) | **76.7%** | 5/10 | 0/10 |

Nebius Token Factory key is only on Vercel as `[SENSITIVE]` and could not be used locally.

Full matrix: [`results/RESULTS.md`](results/RESULTS.md) · Live page: [pyscope-evals.vercel.app](https://pyscope-evals.vercel.app) · Demo: [GitHub Releases](https://github.com/dl88jing/micro1-frontier-evals/releases/tag/v1.1.0)

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

Each of 04–10 was selected from multi-model probes where **≥2** of Wonder/Spark/Beam failed (see `results/probe_candidates.json`, `results/probe_wave2.json`).

## Layout

```
tasks/NN_name/     prompt.md  answer.json  grade.py  rationale.md  task.json  snippet.py
graders/           shared JSON grader (common.py) + oracle runner
scripts/           build_tasks.py, run_models.py, write_hardened_task.py, probes
results/           RESULTS.md, summary.json, probe_*.json
web/               static results page (Vercel)
video/             HyperFrames storyboard + Kokoro VO script
submission.md      HackerRank submission checklist
```

## Quick start

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python graders/run_all.py          # oracle must be 10/10
# optional empirical re-run (API keys — see .env.example):
.venv/bin/python scripts/run_models.py       # 3 trials → pass@1
```

Each task asks the model to emit:

```
FINAL_ANSWER: {"stdout": "..."}
```

## License

MIT — original prompts, graders, and rationale. No proprietary Adobe material. Affiliation: **Green Robin Labs** only.
