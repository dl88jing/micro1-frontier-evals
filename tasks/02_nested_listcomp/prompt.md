Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
v = "G"
class A:
    v = "C"
    rows = [[v for k in range(2)] for _ in range(2)]
    gen = list(v for _ in range(1))
    def meth(self, x=v):
        return x, self.v
print(A.rows, A.gen, A().meth(), A.meth(A(), "Q"))
```

End with:
FINAL_ANSWER: {"stdout":"..."}
