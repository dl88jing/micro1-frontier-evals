#!/usr/bin/env python3
"""Build PyScope LEGB eval tasks with oracle-backed answers."""
from __future__ import annotations

import io
import json
import contextlib
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"


def run_py(code: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<task>", "exec"), {})
    return buf.getvalue()


def write_task(
    tid: str,
    title: str,
    category: str,
    failure_mode: str,
    code: str | None,
    prompt: str,
    answer: dict,
    rationale: str,
):
    d = TASKS / tid
    d.mkdir(parents=True, exist_ok=True)
    (d / "task.json").write_text(
        json.dumps(
            {
                "id": tid,
                "title": title,
                "category": category,
                "difficulty": "hard",
                "failure_mode": failure_mode,
                "python": "3.13",
            },
            indent=2,
        )
        + "\n"
    )
    (d / "prompt.md").write_text(prompt.strip() + "\n")
    (d / "answer.json").write_text(json.dumps(answer, indent=2) + "\n")
    (d / "rationale.md").write_text(rationale.strip() + "\n")
    if code is not None:
        (d / "snippet.py").write_text(textwrap.dedent(code).lstrip())
    grade = '''#!/usr/bin/env python3
"""Oracle-backed grader: compare FINAL_ANSWER JSON to answer.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "graders"))
from common import extract_final_answer, grade_payload  # type: ignore


def main() -> None:
    task_dir = Path(__file__).resolve().parent
    expected = json.loads((task_dir / "answer.json").read_text())
    raw = sys.stdin.read() if not sys.argv[1:] else Path(sys.argv[1]).read_text()
    payload = extract_final_answer(raw)
    result = grade_payload(payload, expected)
    print(json.dumps(result))
    sys.exit(0 if result.get("pass") else 1)


if __name__ == "__main__":
    main()
'''
    (d / "grade.py").write_text(grade)
    print(f"wrote {tid} answer={answer}")


def stdout_prompt(code: str) -> str:
    return f"""Predict the exact stdout of this Python 3.13 (CPython) program.

Rules:
- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions).
- Report stdout exactly as printed (preserve spaces/newlines).
- Do not run tools; reason from language rules.

```python
{textwrap.dedent(code).strip()}
```

End with:
FINAL_ANSWER: {{"stdout":"..."}}
"""


def main():
    # --- 01 listcomp in class (Wonder fails) ---
    c01 = '''
x = "outer"
class C:
    x = "class"
    y = [x for i in range(1)]
    z = (lambda: x)()
    @staticmethod
    def f(x=x):
        return x
print(C.y[0], C.z, C.f(), C.f("arg"))
'''
    write_task(
        "01_listcomp_class",
        "Listcomp vs class scope",
        "legb_class_body",
        "Models treat class body as enclosing scope for listcomps; CPython listcomps in class bodies look up from the module/function scope, not the class dict.",
        c01,
        stdout_prompt(c01),
        {"stdout": run_py(c01)},
        """In CPython, a class body is not an enclosing scope for nested functions or comprehensions.
`[x for i in range(1)]` creates a nested function scope whose free variable `x` resolves to the module-global `"outer"`, not the class attribute `x = "class"`.
`(lambda: x)()` likewise closes over the module.
The default `x=x` on `f` is evaluated in the class body namespace, so it captures `"class"`.
Correct stdout: `outer outer class arg`.
Frontier models often answer `class outer class arg`, wrongly feeding class-local `x` into the listcomp.
""",
    )

    # --- 02 nested listcomp ---
    c02 = '''
v = "G"
class A:
    v = "C"
    rows = [[v for k in range(2)] for _ in range(2)]
    gen = list(v for _ in range(1))
    def meth(self, x=v):
        return x, self.v
print(A.rows, A.gen, A().meth(), A.meth(A(), "Q"))
'''
    write_task(
        "02_nested_listcomp",
        "Nested listcomp + genexp in class",
        "legb_class_body",
        "Nested comprehensions in class bodies still close over the module; models substitute the class attribute `v`.",
        c02,
        stdout_prompt(c02),
        {"stdout": run_py(c02)},
        """Both the outer and inner listcomps are nested scopes. Free variable `v` resolves to module `"G"`.
The genexp `list(v for _ in range(1))` similarly sees module `v`.
Method default `x=v` is evaluated in the class namespace → `"C"`.
Models frequently produce rows filled with `"C"`.
""",
    )

    # --- 03 class local binding NameError ---
    c03 = '''
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
'''
    write_task(
        "03_class_local_bind",
        "Class-body local binding NameError",
        "legb_class_body",
        "Models miss that assigning to `x` anywhere in a class nested in a function makes `x` local for the whole class body, so `y = x + 1` raises NameError.",
        c03,
        stdout_prompt(c03),
        {"stdout": run_py(c03)},
        """When a class is nested in a function, names assigned anywhere in the class body are treated as class-local for the entire body.
Because `x = 100` appears later, `y = x + 1` does not read the enclosing `x = 10`; it looks for a class-local `x` that is not yet bound → NameError.
Models often invent stdout `11 100 101` as if sequential enclosing lookup applied.
""",
    )

    # --- 04 genexp vs list ---
    c04 = '''
n = 7
class T:
    n = 3
    data = list((n + i) for i in range(3))
    vals = [n, n + 1]
    def g(self):
        return list((n + i) for i in range(2))
print(T.data, T.vals, T().g())
'''
    write_task(
        "04_genexp_vs_list",
        "Genexp vs bare name in class",
        "legb_class_body",
        "Genexps close over module `n`; list displays use class-local `n`. Models often unify them.",
        c04,
        stdout_prompt(c04),
        {"stdout": run_py(c04)},
        """`data` uses a generator expression (nested scope) → module `n=7` → `[7,8,9]`.
`vals = [n, n+1]` evaluates bare `n` in the class body after `n=3` → `[3,4]`.
`g`'s genexp closes over module `n` again → `[7,8]`.
""",
    )

    # --- 05 lambda scopes ---
    c05 = '''
a = "mod"
class K:
    a = "cls"
    f1 = lambda: a
    f2 = (lambda a=a: a)
    f3 = [(lambda: a) for _ in range(1)][0]
print(K.f1(), K.f2(), K.f3())
'''
    write_task(
        "05_lambda_scopes",
        "Three lambdas in a class body",
        "legb_class_body",
        "Bare lambda and listcomp-lambda close over module; default-arg lambda captures class. Models collapse these cases.",
        c05,
        stdout_prompt(c05),
        {"stdout": run_py(c05)},
        """`f1 = lambda: a` → free `a` from module → `mod`.
`f2 = (lambda a=a: a)` → default evaluated in class body → `cls`.
`f3` from a listcomp → nested scope → module `mod`.
Stdout: `mod cls mod`.
""",
    )

    # --- 06 annotations (eager 3.13) ---
    c06 = '''
X = "outer"
class M:
    X = "inner"
    a: X = 1
    b = X
    def f(self, p: X = X):
        return p, M.__annotations__
print(M.b, M.__annotations__, M().f())
'''
    write_task(
        "06_annotations_class",
        "Class annotation evaluation order",
        "legb_class_body",
        "Without from __future__ import annotations, class annotations evaluate eagerly with class locals; models confuse this with stringified annotations.",
        c06,
        stdout_prompt(c06),
        {"stdout": run_py(c06)},
        """On CPython 3.13 without `from __future__ import annotations`, `a: X = 1` evaluates `X` in the class body after `X = "inner"`, so `__annotations__['a'] == 'inner'`.
With `from __future__ import annotations` it would be the string `'X'` instead — a common confusion.
""",
    )

    # --- 07 decorator default ---
    c07 = '''
def deco(f):
    f.marked = True
    return f
q = "outer"
class S:
    q = "class"
    @deco
    def h(self, x=q):
        return x
    p = [q]
print(S().h(), S.h.marked, S.p)
'''
    write_task(
        "07_decorator_default",
        "Decorator + default in class",
        "legb_class_body",
        "Defaults and list literals in class bodies see class locals; some models still pull module `q`.",
        c07,
        stdout_prompt(c07),
        {"stdout": run_py(c07)},
        """`x=q` and `p=[q]` evaluate in the class namespace after `q = "class"`.
Decorator runs at definition time and sets `marked`.
""",
    )

    # --- 08 MRO ---
    c08 = '''
class A:
    def f(self):
        return "A"
class B(A):
    def f(self):
        return "B"+super().f()
class C(A):
    def f(self):
        return "C"+super().f()
class D(C,B):
    def f(self):
        return "D"+super().f()
print(D().f())
print([c.__name__ for c in D.__mro__])
'''
    write_task(
        "08_mro_super",
        "Cooperative super MRO",
        "object_model",
        "Models reorder MRO (B before C) or break cooperative super chaining.",
        c08,
        stdout_prompt(c08),
        {"stdout": run_py(c08)},
        """`D(C,B)` MRO is D, C, B, A, object. Cooperative super yields `DCBA`.
""",
    )

    # --- 09 bool vs len ---
    c09 = '''
class Fake:
    def __bool__(self):
        print("bool")
        return False
    def __len__(self):
        print("len")
        return 0
print(bool(Fake()))
class Fake2:
    def __len__(self):
        print("len2")
        return 0
print(bool(Fake2()))
'''
    write_task(
        "09_bool_prefers",
        "bool() prefers __bool__ over __len__",
        "object_model",
        "Models call __len__ even when __bool__ exists, or skip the len2 fallback.",
        c09,
        stdout_prompt(c09),
        {"stdout": run_py(c09)},
        """`bool()` uses `__bool__` if present; otherwise `__len__`.
Fake prints `bool` then False. Fake2 prints `len2` then False.
""",
    )

    # --- 10 DST footgun ---
    from datetime import datetime
    from zoneinfo import ZoneInfo

    tz = ZoneInfo("America/Los_Angeles")
    t1 = datetime(2024, 3, 9, 1, 30, tzinfo=tz)
    t2 = datetime(2024, 3, 10, 3, 30, tzinfo=tz)
    ghost = datetime(2024, 3, 10, 2, 30, tzinfo=tz)
    answer10 = {
        "absolute_hours": (t2.timestamp() - t1.timestamp()) / 3600,
        "same_tzinfo_sub_hours": (t2 - t1).total_seconds() / 3600,
        "ghost_offset_h": ghost.utcoffset().total_seconds() / 3600,
        "span_sec": datetime(2024, 3, 10, 4, 0, tzinfo=tz).timestamp()
        - datetime(2024, 3, 10, 1, 0, tzinfo=tz).timestamp(),
    }
    prompt10 = '''Python 3.13 + zoneinfo, timezone America/Los_Angeles:

```python
from datetime import datetime
from zoneinfo import ZoneInfo
tz = ZoneInfo("America/Los_Angeles")
t1 = datetime(2024, 3, 9, 1, 30, tzinfo=tz)
t2 = datetime(2024, 3, 10, 3, 30, tzinfo=tz)
ghost = datetime(2024, 3, 10, 2, 30, tzinfo=tz)  # spring-forward gap
absolute_hours = (t2.timestamp() - t1.timestamp()) / 3600
same_tzinfo_sub_hours = (t2 - t1).total_seconds() / 3600
ghost_offset_h = ghost.utcoffset().total_seconds() / 3600
span_sec = (
    datetime(2024, 3, 10, 4, 0, tzinfo=tz).timestamp()
    - datetime(2024, 3, 10, 1, 0, tzinfo=tz).timestamp()
)
```

Compute the four values exactly as CPython would.

FINAL_ANSWER: {"absolute_hours":N,"same_tzinfo_sub_hours":N,"ghost_offset_h":N,"span_sec":N}
'''
    write_task(
        "10_dst_footgun",
        "DST absolute vs same-tzinfo subtraction",
        "temporal_semantics",
        "Models confuse wall-clock timedelta (same tzinfo object ignores tz and subtracts naive walls) with absolute timestamp elapsed time across the spring-forward transition.",
        None,
        prompt10,
        answer10,
        """When two aware datetimes share the identical tzinfo object, Python subtracts them as naive wall times → 26 hours.
`timestamp()` difference is absolute elapsed time → 25 hours across the lost spring-forward hour.
The non-existent 02:30 is still constructible; fold=0 keeps UTC-8.
01:00→04:00 local spans 7200 absolute seconds, not 10800.
""",
    )

    print("done", len(list(TASKS.iterdir())), "tasks")


if __name__ == "__main__":
    main()
