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
| ZIP | `/workspace/micro1-eval/micro1-frontier-evals.zip` (~0.22 MB; also on release) |
| Results page | https://pyscope-evals.vercel.app |
| Demo video | https://github.com/dl88jing/micro1-frontier-evals/releases/download/v1.0.0/pyscope-demo.mp4 (~61s) |
| Release | https://github.com/dl88jing/micro1-frontier-evals/releases/tag/v1.0.0 |

## Theme

**PyScope — Class-body LEGB traps on CPython 3.13.** Ten original tasks with prompt, ground-truth JSON, automatic grader, and rationale. Empirically verified against Muse Wonder 1.0 (Meta) and Muse Spark Open (Baseten).

## Tasks

1. `01_listcomp_class` — listcomp free vars skip class scope  
2. `02_nested_listcomp` — nested comps vs defaults  
3. `03_class_local_bind` — assignment → whole-body local → NameError  
4. `04_genexp_vs_list` — genexp closes module; bare name is class  
5. `05_lambda_scopes` — lambda / default / listcomp-lambda  
6. `06_annotations_class` — annotations see class locals (no PEP 563)  
7. `07_decorator_default` — defaults bind class namespace at def time  
8. `08_mro_super` — cooperative super MRO  
9. `09_bool_prefers` — `__bool__` beats `__len__`  
10. `10_dst_footgun` — wall-clock tzinfo subtraction vs absolute time  

## Empirical failure rates

| Model | Pass | Fail | Pass rate |
|---|---|---|---|
| Muse Wonder 1.0 | 8/10 | 2 | 80% |
| Muse Spark Open | 8/10 | 2 | 80% |
| Oracle | 10/10 | 0 | 100% |

Notable wrong answers: Wonder fails `01`/`02` (class scope vs listcomp); Spark fails `03` (misses NameError from whole-body local). See `results/RESULTS.md`.

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

> PyScope: 10 original CPython 3.13 class-body / LEGB traps with automatic JSON graders. Oracle 10/10. Muse Wonder 8/10, Muse Spark Open 8/10. Repo + Vercel results + 61s demo video. Green Robin Labs / Dylan Ler (Northbridge).

## Non-affiliation

This entry is **Green Robin Labs / Dylan Ler only**. No Adobe affiliation, IP, or branding.
