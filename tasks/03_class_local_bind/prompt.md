Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
def build():
    x = 10
    class E:
        y = x + 1
        x = 100
        z = x + 1
    return E
try:
    E = build()
    print(E.y, E.x, E.z)
except Exception as e:
    print(type(e).__name__)
```

End with:
FINAL_ANSWER: {"stdout":"..."}
