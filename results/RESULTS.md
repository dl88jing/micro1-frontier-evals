# PyScope LEGB results

Empirical runs against **Muse Wonder 1.0** (Meta API) and **Muse Spark Open** (Baseten).
Oracle graders: **10/10**. Temperature 0. Empty API replies were retried up to 3×.

| Model | Pass | Fail | Rate |
|---|---|---|---|
| muse-wonder-1.0 | 8 | 2 | 80% |
| muse-spark-open-1026 | 8 | 2 | 80% |

| Task | Wonder | Spark | Trap |
|---|---|---|---|
| `01_listcomp_class` | FAIL | PASS | listcomp free vars skip class scope |
| `02_nested_listcomp` | FAIL | PASS | nested comps + defaults disagree |
| `03_class_local_bind` | PASS | FAIL | assign → whole-body local → NameError |
| `04_genexp_vs_list` | PASS | PASS | genexp closes module; bare name is class |
| `05_lambda_scopes` | PASS | PASS | lambda vs default vs listcomp-lambda |
| `06_annotations_class` | PASS | PASS | annotations see class locals (no PEP 563) |
| `07_decorator_default` | PASS | PASS | defaults bind class namespace at def time |
| `08_mro_super` | PASS | PASS | cooperative super MRO C before B |
| `09_bool_prefers` | PASS | PASS | __bool__ beats __len__ for truthiness |
| `10_dst_footgun` | PASS | FAIL | wall-clock tzinfo sub vs absolute time |

## Notable wrong answers (not empty replies)

- **01 Wonder**: predicted `class outer class arg` — treated class body as enclosing scope for listcomp/lambda free vars.
- **02 Wonder**: nested listcomp used class `C` instead of module `G`.
- **03 Spark**: predicted `11 100 101` instead of `NameError` (missed whole-body local binding).
- **10 Spark**: empty completion after retries (counted fail; Wonder passed structured DST fields).

