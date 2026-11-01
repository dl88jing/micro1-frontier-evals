# micro1 Eval Hackathon — Submission (PyScope)

**Contestant:** Dylan Ler  
**Affiliation:** Green Robin Labs (solo; never Adobe)  
**Handle / pseudonym:** Northbridge  
**Track:** Solo · HackerRank Eval Hackathon  

## Package

| Item | Location |
|---|---|
| Public GitHub | https://github.com/dl88jing/micro1-frontier-evals |
| Local package | `/workspace/micro1-eval/` |
| ZIP | `/workspace/micro1-eval/micro1-frontier-evals.zip` |
| Results page | https://pyscope-evals.vercel.app |
| Demo video | https://github.com/dl88jing/micro1-frontier-evals/releases/download/v1.1.0/pyscope-demo.mp4 |
| Release | https://github.com/dl88jing/micro1-frontier-evals/releases/tag/v1.1.0 |

## Theme

**PyScope — Class-body LEGB traps on CPython 3.13 (hardened).** Ten original tasks with prompt, ground-truth JSON, automatic grader, and rationale. Empirically verified with **3 trials / task / model → pass@1** against Muse Wonder 1.0 (Meta), Muse Spark Open (Baseten), and Beam-1.0-501B-A23B (Reflection). Nebius Token Factory was unreachable locally (Vercel `[SENSITIVE]` only).

## Tasks

1. `01_listcomp_class` — listcomp free vars skip class scope  
2. `02_nested_listcomp` — nested comps vs defaults  
3. `03_class_local_bind` — assignment → whole-body local → NameError  
4. `04_default_shadow` — default `a=x` then class assign → NameError  
5. `05_genexp_late_bind` — class genexp/listcomp close over module `n`  
6. `06_default_fallthrough` — default LOAD_NAME → global; body closes local  
7. `07_method_reads_shadow` — `y=x+1` before class `x=…` → NameError  
8. `08_nested_two_shadows` — two later assigns → NameError on first read  
9. `09_pep695_type_param` — PEP 695: `first=T` is module, not type param  
10. `10_walrus_and_default` — walrus-in-class SyntaxError | default NameError  

Tasks 04–10 were selected from multi-model probes where ≥2 of Wonder/Spark/Beam failed.

## Empirical failure rates

_Matrix filled after the 3× pass@1 run completes — see `results/RESULTS.md`._

| Model | pass@1 mean | Notes |
|---|---|---|
| Muse Wonder 1.0 | TBD | Meta |
| Muse Spark Open | TBD | Baseten |
| Beam-1.0-501B-A23B | TBD | Reflection |
| Oracle | 10/10 | 100% |

## HackerRank submit (manual — needs Dylan login)

Exact Instructions page is behind HackerRank auth. From public FAQ:

- Upload ZIP ≤ 50MB (prompts + graders + results; no secrets) — ready at path above / release asset  
- Link public GitHub repo  
- Link results page / video (≤5 min)  
- Short description  
- **Deadline:** Nov 9 05:15 GMT = **Nov 8, 9:15 PM America/Los_Angeles**  
- Winners announced Nov 23  

**Blocked for this agent:** submitting the form on HackerRank requires Dylan’s logged-in session. Package + repo + video + page are ready; final click is on Dylan.

### Suggested HackerRank description

> PyScope: 10 hardened CPython 3.13 class-body / LEGB traps with automatic JSON graders. Oracle 10/10. 3× pass@1 on Muse Wonder, Muse Spark Open, and Beam. Repo + Vercel results + demo video. Green Robin Labs / Dylan Ler (Northbridge).

## Non-affiliation

This entry is **Green Robin Labs / Dylan Ler only**. No Adobe affiliation, IP, or branding.
