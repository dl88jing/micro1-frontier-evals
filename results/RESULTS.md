# PyScope LEGB results (hardened)

Protocol: temperature 0, **3 trials** per task/model, report **pass@1** (= mean trial pass rate).
Oracle graders: **10/10**. Nebius Token Factory unreachable locally (Vercel `[SENSITIVE]` only).

| Model | pass@1 mean | all-pass tasks | all-fail tasks |
|---|---|---|---|
| `muse-wonder-1.0` | 6.7% | 0/10 | 9/10 |
| `muse-spark-open-1026` | 13.3% | 0/10 | 8/10 |
| `Beam-1.0-501B-A23B` | 76.7% | 5/10 | 0/10 |

## Matrix (pass@1)

| Task | `muse-wonder-1.0` | `muse-spark-open-1026` | `Beam-1.0-501B-A23B` |
|---|---|---|---|
| `01_listcomp_class` | 0% | 67% | 67% |
| `02_nested_listcomp` | 0% | 67% | 33% |
| `03_class_local_bind` | 67% | 0% | 100% |
| `04_default_shadow` | 0% | 0% | 67% |
| `05_genexp_late_bind` | 0% | 0% | 100% |
| `06_default_fallthrough` | 0% | 0% | 100% |
| `07_method_reads_shadow` | 0% | 0% | 100% |
| `08_nested_two_shadows` | 0% | 0% | 100% |
| `09_pep695_type_param` | 0% | 0% | 33% |
| `10_walrus_and_default` | 0% | 0% | 67% |

## Hardening notes

- Kept `01`/`02`/`03`; replaced former soft passers `04`–`10` from wave1/wave2 probes where ≥2 of Wonder/Spark/Beam failed.
- Wonder + Spark all-fail on every hardened task `04`–`10` (and most of `01`–`03`).
- Beam is stronger (pass@1 mean 76.7%) but still fails `01`/`02`/`09` often and is imperfect on `04`/`10`.

