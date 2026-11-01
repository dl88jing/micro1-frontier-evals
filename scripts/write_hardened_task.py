#!/usr/bin/env python3
"""Write hardened task N (0..6). Usage: write_hardened_task.py INDEX"""
from __future__ import annotations
import json, shutil, subprocess, sys, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"
GRADE_TMPL = (TASKS / "03_class_local_bind" / "grade.py").read_text()

SWAPS = [
(
"04_default_shadow",
"04_genexp_vs_list",
"Default arg then class assign → NameError",
"Models evaluate `a=x` as if it closed over the enclosing list, ignoring that later `x = ...` makes x class-local for the whole body so the default raises NameError.",
"In a class nested in a function, any assignment to `x` marks `x` local for the entire class body.\n"
"The default `a=x` is evaluated while building the function object, before `x = [\"class\"]` runs, so the class-local `x` is still unbound → NameError.\n"
"Frontier models often predict `(['outer'], ['class'])`.",
'''
def f():
    x = ["outer"]
    class C:
        def m(self, a=x):
            return list(a)
        x = ["class"]
    return C().m(), C.x
try:
    print(f())
except Exception as e:
    print(type(e).__name__)
''',
),
(
"05_genexp_late_bind",
"05_lambda_scopes",
"Class genexp vs listcomp with late assign",
"Models treat class-body listcomps like they see the later class attribute `n`.",
"Generator expressions always create a nested function scope; free `n` is looked up when the genexp runs, seeing the module global that was current at class creation time (still 5).\n"
"List comprehensions in class scope also keep a nested function scope (PEP 709 does not inline them there), so they likewise close over module `n=5`, not the later class attribute `n=99`.\n"
"Models frequently predict `[5, 5] [99, 99] 99`.",
'''
n = 5
class C:
    g = (n for _ in range(2))
    n = 99
    L = [n for _ in range(2)]
print(list(C.g), C.L, C.n)
''',
),
(
"06_default_fallthrough",
"06_annotations_class",
"Default LOAD_NAME fallthrough vs method closure",
"Models unify default and free-var lookup, predicting both see the enclosing function local.",
"Class-body name lookup for bare names is class dict → globals → builtins (not the enclosing function).\n"
"Because `x = \"C\"` appears later, `a=x` in the default uses LOAD_NAME, finds no class binding yet, and falls through to the module global `\"G\"`.\n"
"The method body free variable `x` closes over the enclosing function local `\"L\"`.\n"
"Wrong answer seen in probes: `('L', 'L', 'C')`.",
'''
x = "G"
def f():
    x = "L"
    class C:
        def m(self, a=x):
            return a
        def n(self):
            return x
        x = "C"
    return C().m(), C().n(), C.x
print(f())
''',
),
(
"07_method_reads_shadow",
"07_decorator_default",
"Method free var + class-local assign → NameError",
"Models allow `y = x + 1` to read the enclosing function local even though a later class assignment makes `x` local for the whole body.",
"Assignment `x = 100` anywhere in the class body makes `x` a class-local for every bare reference in that body, including `y = x + 1` before the assignment → NameError at class creation.\n"
"The nested method never runs. Models invent `(11, 10, 101)` or `UnboundLocalError`.",
'''
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
''',
),
(
"08_nested_two_shadows",
"08_mro_super",
"Two shadowed names in nested class body",
"Models sequentially bind `a`/`b` from the enclosing function and ignore whole-body class-local rules for both names.",
"Both `a` and `b` are assigned later in the class body, so they are class-local for the entire body.\n"
"`x = a` runs before `a` is bound → NameError. Models predict `(1, 2, (1, 2), 10, 20)`.",
'''
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
''',
),
(
"09_pep695_type_param",
"09_bool_prefers",
"PEP 695 type-param scope vs class assign",
"Models mishandle PEP 695 type-parameter scopes when the same name is later assigned in the class body.",
"In `class Box[T]:`, the type parameter `T` is visible in the class body as the parameter object for early references.\n"
"`first = T` sees the type parameter (prints as the name via str in some contexts — here the annotation/value prints the TypeVar-like param's presence through the name lookup returning the param); after `T = \"cls\"`, bare `T` is the string; default `default=T` sees `\"cls\"`.\n"
"`Box.__type_params__[0].__name__` remains `\"T\"`. Oracle stdout: `mod cls cls T`.",
'''
T="mod"
class Box[T]:
    first=T
    T="cls"
    second=T
    def get(self, default=T):
        return default
print(Box.first, Box.second, Box().get(), Box.__type_params__[0].__name__)
''',
),
(
"10_walrus_and_default",
"10_dst_footgun",
"Walrus-in-class SyntaxError + default NameError",
"Models miss that assignment expressions in class comprehensions are SyntaxError, and/or miss the default+later-assign NameError.",
"PEP 572: an assignment expression target in a comprehension inside a class body is a SyntaxError.\n"
"Separately, `def m(self, a=x)` with a later `x = [\"c\"]` in the same class nested in a function raises NameError when evaluating the default.\n"
"Stdout is the two exception type names joined: `SyntaxError|NameError`.",
'''
outs=[]
try:
    compile("class C:\\n data=[(y:=i) for i in range(1)]\\n","<x>","exec")
    outs.append("ok")
except SyntaxError:
    outs.append("SyntaxError")
def f():
    x=["o"]
    class C:
        def m(self,a=x):
            return a
        x=["c"]
    return C().m()
try:
    outs.append(repr(f()))
except Exception as e:
    outs.append(type(e).__name__)
print("|".join(outs))
''',
),
]

def oracle(code: str) -> str:
    script = "code = " + repr(textwrap.dedent(code)) + "\nexec(compile(code, '<t>', 'exec'), {'__name__':'__main__'})\n"
    p = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=10)
    assert p.returncode == 0, p.stderr
    return p.stdout

def write_one(idx: int):
    new_id, old_id, title, fail, rationale, code = SWAPS[idx]
    code = textwrap.dedent(code).strip() + "\n"
    out = oracle(code)
    dest = TASKS / new_id
    old = TASKS / old_id
    if dest.exists() and dest.resolve() != (TASKS / new_id).resolve():
        pass
    if old.exists() and old.name != new_id:
        shutil.rmtree(old)
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    (dest / "snippet.py").write_text(code)
    (dest / "answer.json").write_text(json.dumps({"stdout": out}, indent=2) + "\n")
    (dest / "task.json").write_text(json.dumps({
        "id": new_id,
        "title": title,
        "category": "legb_class_body",
        "difficulty": "hard",
        "failure_mode": fail,
        "python": "3.13",
        "probe_fails": ">=2 of wonder/spark/beam (see results/probe_*.json)",
    }, indent=2) + "\n")
    (dest / "rationale.md").write_text(rationale.strip() + "\n")
    (dest / "grade.py").write_text(GRADE_TMPL)
    prompt = (
        "Predict the exact stdout of this Python 3.13 (CPython) program.\n\n"
        "Rules:\n"
        "- Simulate CPython 3.13 semantics exactly (LEGB, class body, comprehensions, PEP 695/709/572).\n"
        "- Report stdout exactly as printed (preserve spaces/newlines).\n"
        "- Do not run tools; reason from language rules.\n\n"
        f"```python\n{code.strip()}\n```\n\n"
        "End with:\n"
        'FINAL_ANSWER: {"stdout":"..."}\n'
    )
    (dest / "prompt.md").write_text(prompt)
    print(f"WROTE {new_id} gt={out!r}")
    return new_id, out

if __name__ == "__main__":
    idx = int(sys.argv[1])
    write_one(idx)
