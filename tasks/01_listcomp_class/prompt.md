Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
x = "outer"
class C:
    x = "class"
    y = [x for i in range(1)]
    z = (lambda: x)()
    @staticmethod
    def f(x=x):
        return x
print(C.y[0], C.z, C.f(), C.f("arg"))
```

End with:
FINAL_ANSWER: {"stdout":"..."}
