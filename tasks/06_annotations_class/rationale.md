On CPython 3.13 without `from __future__ import annotations`, `a: X = 1` evaluates `X` in the class body after `X = "inner"`, so `__annotations__['a'] == 'inner'`.
With `from __future__ import annotations` it would instead store the string `'X'` — a common confusion that also appears when builders themselves enable postponed evaluation.
