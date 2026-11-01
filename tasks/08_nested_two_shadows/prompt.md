Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions, PEP 695/709/572).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
def outer():
    a=1; b=2
    class C:
        x=a
        def f(self):
            return a,b
        a=10
        y=b
        b=20
    return C.x, C.y, C().f(), C.a, C.b
try:
    print(outer())
except Exception as e:
    print(type(e).__name__)
```

End with:
FINAL_ANSWER: {"stdout":"..."}
