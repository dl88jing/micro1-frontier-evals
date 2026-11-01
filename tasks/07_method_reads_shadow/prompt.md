Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions, PEP 695/709/572).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
def build():
    x = 10
    class C:
        y = x + 1
        def bump(self):
            return x
        x = 100
        z = x + 1
    return C.y, C().bump(), C.z
try:
    print(build())
except Exception as e:
    print(type(e).__name__)
```

End with:
FINAL_ANSWER: {"stdout":"..."}
