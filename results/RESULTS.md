# PyScope LEGB results (hardened)

Protocol: temperature 0, **3 trials** per task/model, report **pass@1** (= mean trial pass rate).
Oracle graders: **10/10**. Empty API replies retried up to 3×.

| Model | pass@1 mean | all-pass tasks | all-fail tasks |
|---|---|---|---|
| `Beam-1.0-501B-A23B` | 73.3% | 2/5 | 0/5 |
| `muse-spark-open-1026` | 22.2% | 0/6 | 4/6 |
| `muse-wonder-1.0` | 11.1% | 0/6 | 5/6 |

## Matrix (pass@1)

| Task | `Beam-1.0-501B-A23B` | `muse-spark-open-1026` | `muse-wonder-1.0` |
|---|---|---|---|
| `01_listcomp_class` | 67% | 67% | 0% |
| `02_nested_listcomp` | 33% | 67% | 0% |
| `03_class_local_bind` | 100% | 0% | 67% |
| `04_default_shadow` | 67% | 0% | 0% |
| `05_genexp_late_bind` | 100% | 0% | 0% |
| `06_default_fallthrough` | — | 0% | 0% |

