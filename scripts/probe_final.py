#!/usr/bin/env python3
from __future__ import annotations
import io, json, re, contextlib
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI

meta_key = Path("/workspace/meta-hack/.meta_api_key").read_text().strip()
env = Path("/home/box/.config/seefix/baseten.env").read_text()
bk = {l.split("=",1)[0]:l.split("=",1)[1].strip() for l in env.splitlines() if "=" in l and not l.startswith("#")}
W = OpenAI(api_key=meta_key, base_url="https://api.meta.ai/v1", timeout=400)
S = OpenAI(api_key=bk["BASETEN_API_KEY"], base_url=bk["BASETEN_BASE_URL"], timeout=400)

def run_py(code: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<t>", "exec"), {})
    return buf.getvalue()

def ask(client, model, prompt):
    r = client.chat.completions.create(
        model=model, temperature=0, max_tokens=8192,
        messages=[
            {"role":"system","content":"Think step-by-step about Python 3.12/3.13 semantics. End with FINAL_ANSWER: <compact json>"},
            {"role":"user","content":prompt},
        ],
    )
    text = r.choices[0].message.content or ""
    m = re.search(r"FINAL_ANSWER\s*:\s*(.*)$", text, re.S|re.I)
    return (m.group(1).strip() if m else f"<no_final L={len(text)}>")[:400], getattr(r.usage,"completion_tokens",0)

TASKS = []

def add_stdout(tid, code, rationale):
    out = run_py(code)
    prompt = (
        "Exact stdout of this Python 3.13 program (CPython). "
        "If it raises before printing, stdout may be partial; still report what was printed, "
        "and include the exception in the JSON.\n"
        f"```\n{code.strip()}\n```\n"
        'If no exception: FINAL_ANSWER: {"stdout":"..."}\n'
        'If exception: FINAL_ANSWER: {"stdout":"...","exc_type":"...","exc_msg":"..."}'
    )
    # determine if exception
    exc = None
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(compile(code, "<t>", "exec"), {})
        out = buf.getvalue()
        gt = {"stdout": out}
    except Exception as e:
        out = buf.getvalue()
        gt = {"stdout": out, "exc_type": type(e).__name__, "exc_msg": str(e)}
    TASKS.append((tid, prompt, gt, rationale, code))
    print(tid, "GT", gt)

# 1 listcomp class
add_stdout("01_listcomp_class", '''
x = "outer"
class C:
    x = "class"
    y = [x for i in range(1)]
    z = (lambda: x)()
    @staticmethod
    def f(x=x):
        return x
print(C.y[0], C.z, C.f(), C.f("arg"))
''', "Listcomp in class body looks up enclosing module scope, not class scope.")

# 2 double comp
add_stdout("02_double_comp", '''
v = "G"
class A:
    v = "C"
    rows = [[v for k in range(2)] for _ in range(2)]
    gen = list(v for _ in range(1))
    def meth(self, x=v):
        return x, self.v
print(A.rows, A.gen, A().meth(), A.meth(A(), "Q"))
''', "Nested listcomps in class body bind from enclosing module; defaults bind class scope.")

# 3 nested class NameError
add_stdout("03_class_local_bind", '''
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
''', "Assigning to x anywhere in class body nested in a function makes x local for the whole class body → NameError on y=x+1.")

# 4 genexp vs list in class
add_stdout("04_genexp_vs_list", '''
n = 7
class T:
    n = 3
    data = list((n + i) for i in range(3))
    vals = [n, n + 1]
    def g(self):
        return list((n + i) for i in range(2))
print(T.data, T.vals, T().g())
''', "Genexp in class body closes over module n; bare name n in list uses class-local after assignment.")

# 5 annotations
add_stdout("05_annotations", '''
X = "outer"
class M:
    X = "inner"
    a: X = 1
    b = X
    def f(self, p: X = X):
        return p, M.__annotations__
print(M.b, M.__annotations__, M().f())
''', "Class-body annotations evaluate with class locals visible sequentially.")

# 6 decorator defaults
add_stdout("06_decorator_default", '''
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
''', "Default args in methods resolve at function def time using class namespace.")

# 7 lambda default vs body in class
add_stdout("07_lambda_scopes", '''
a = "mod"
class K:
    a = "cls"
    f1 = lambda: a
    f2 = (lambda a=a: a)
    f3 = [(lambda: a) for _ in range(1)][0]
print(K.f1(), K.f2(), K.f3())
''', "lambda: a in class body closes over module; default a=a captures class; listcomp lambda closes over module.")

# 8 MRO (control / may pass)
add_stdout("08_mro_super", '''
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
''', "Cooperative super MRO order C before B.")

# 9 bool vs len
add_stdout("09_bool_len", '''
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
''', "__bool__ preferred over __len__ for truthiness.")

# 10 DST footgun as non-stdout task
tz = ZoneInfo("America/Los_Angeles")
t1 = datetime(2024,3,9,1,30,tzinfo=tz)
t2 = datetime(2024,3,10,3,30,tzinfo=tz)
ghost = datetime(2024,3,10,2,30,tzinfo=tz)
gt_dst = {
    "absolute_hours": (t2.timestamp()-t1.timestamp())/3600,
    "same_tzinfo_sub_hours": (t2-t1).total_seconds()/3600,
    "ghost_offset_h": ghost.utcoffset().total_seconds()/3600,
    "span_sec": datetime(2024,3,10,4,0,tzinfo=tz).timestamp()-datetime(2024,3,10,1,0,tzinfo=tz).timestamp(),
}
TASKS.append(("10_dst_footgun", '''Python 3.13 + zoneinfo, America/Los_Angeles:
t1=datetime(2024,3,9,1,30,tzinfo=ZoneInfo("America/Los_Angeles"))
t2=datetime(2024,3,10,3,30,tzinfo=ZoneInfo("America/Los_Angeles"))
ghost=datetime(2024,3,10,2,30,tzinfo=ZoneInfo("America/Los_Angeles"))
Compute:
absolute_hours=(t2.timestamp()-t1.timestamp())/3600
same_tzinfo_sub_hours=(t2-t1).total_seconds()/3600
ghost_offset_h=ghost.utcoffset().total_seconds()/3600
span_sec=datetime(2024,3,10,4,0,tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()-datetime(2024,3,10,1,0,tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()
FINAL_ANSWER: {"absolute_hours":N,"same_tzinfo_sub_hours":N,"ghost_offset_h":N,"span_sec":N}
''', gt_dst, "Same-tzinfo datetime subtraction uses wall time; timestamp() is absolute; spring-forward ghost keeps fold=0 PST offset.", None))
print("10", gt_dst)

results = {}
for tid, prompt, gt, rationale, code in TASKS:
    print(f"\n==== {tid} GT={gt}")
    results[tid] = {"gt": gt, "rationale": rationale}
    for lab, client, model in [("W", W, "muse-wonder-1.0"), ("S", S, "meta-models/muse-spark-open-1026")]:
        try:
            ans, tok = ask(client, model, prompt)
        except Exception as e:
            ans, tok = f"ERR {e}", 0
        ok = False
        try:
            j = ans[ans.find("{"):ans.rfind("}")+1]
            got = json.loads(j)
            ok = True
            for k,v in gt.items():
                if isinstance(v, float):
                    ok = ok and abs(float(got[k])-v) < 1e-9
                elif k == "stdout":
                    ok = ok and got.get("stdout","").rstrip("\n") == v.rstrip("\n")
                else:
                    ok = ok and got.get(k) == v
        except Exception:
            ok = False
        results[tid][lab] = {"pass": ok, "ans": ans[:350], "tok": tok}
        print(f"  {lab} {'PASS' if ok else 'FAIL'} tok={tok}: {ans[:200]}")

Path("/workspace/micro1-eval/results/probe_final.json").write_text(json.dumps(results, indent=2))
print("\nSUMMARY")
for tid,r in results.items():
    print(tid, "W", r["W"]["pass"], "S", r["S"]["pass"])
