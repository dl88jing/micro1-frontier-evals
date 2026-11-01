# PyScope LEGB results (hardened)

Protocol: temperature 0, **3 trials** per task/model, report **pass@1** (= mean trial pass rate).
Oracle graders: **10/10**. Empty API replies retried up to 3×.

| Model | pass@1 mean | all-pass tasks | all-fail tasks |
|---|---|---|---|
| `Beam-1.0-501B-A23B` | 77.8% | 5/9 | 0/9 |
| `muse-spark-open-1026` | 13.3% | 0/10 | 8/10 |
| `muse-wonder-1.0` | 6.7% | 0/10 | 9/10 |

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
| `08_nested_two_shadows` | 100% | 0% | 0% |
| `09_pep695_type_param` | 33% | 0% | 0% |
| `10_walrus_and_default` | — | 0% | 0% |

