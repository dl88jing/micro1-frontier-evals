Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
a = "mod"
class K:
    a = "cls"
    f1 = lambda: a
    f2 = (lambda a=a: a)
    f3 = [(lambda: a) for _ in range(1)][0]
print(K.f1(), K.f2(), K.f3())
```

End with:
FINAL_ANSWER: {"stdout":"..."}
