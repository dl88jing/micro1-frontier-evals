# PyScope LEGB results (hardened)

Protocol: temperature 0, **3 trials** per task/model, report **pass@1** (= mean trial pass rate).
Oracle graders: **10/10**. Empty API replies retried up to 3×.

| Model | pass@1 mean | all-pass tasks | all-fail tasks |
|---|---|---|---|
| `Beam-1.0-501B-A23B` | 81.0% | 4/7 | 0/7 |
| `muse-spark-open-1026` | 19.1% | 0/7 | 5/7 |
| `muse-wonder-1.0` | 8.3% | 0/8 | 7/8 |

## Matrix (pass@1)

| Task | `Beam-1.0-501B-A23B` | `muse-spark-open-1026` | `muse-wonder-1.0` |
|---|---|---|---|
| `01_listcomp_class` | 67% | 67% | 0% |
| `02_nested_listcomp` | 33% | 67% | 0% |
| `03_class_local_bind` | 100% | 0% | 67% |
| `04_default_shadow` | 67% | 0% | 0% |
| `05_genexp_late_bind` | 100% | 0% | 0% |
| `06_default_fallthrough` | 100% | 0% | 0% |
| `07_method_reads_shadow` | 100% | 0% | 0% |
| `08_nested_two_shadows` | — | — | 0% |

