#!/usr/bin/env python3
"""Oracle + multi-model probe for hardened LEGB candidates."""
from __future__ import annotations
import io, contextlib, json, re, textwrap, time, subprocess, tempfile
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "probe_candidates.json"

CANDIDATES = {
"walrus_class_syntax": '''
x = 0
try:
    compile("class C:\\n data = [(y := i) for i in range(3)]\\n", "<x>", "exec")
    print("compiled")
except SyntaxError as e:
    print(type(e).__name__)
''',
"default_shadow_assign": '''
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
"super_nested_runtime": '''
class A:
    def f(self):
        return "A"
class B(A):
    def f(self):
        def inner():
            return super().f()
        return inner()
try:
    print(B().f())
except Exception as e:
    print(type(e).__name__)
''',
"exc_delete": '''
e = "keep"
try:
    1/0
except ZeroDivisionError as e:
    msg = str(e)
print(msg, end="|")
try:
    print(e)
except Exception as ex:
    print(type(ex).__name__)
''',
"genexp_late_bind": '''
n = 5
class C:
    g = (n for _ in range(2))
    n = 99
    L = [n for _ in range(2)]
print(list(C.g), C.L, C.n)
''',
"pep695_shadow": '''
T = "mod"
class C[T]:
    a = T
    T = "cls"
    b = T
print(C.a, C.b, C.__type_params__[0].__name__)
''',
"type_alias_param": '''
type Vec[T] = list[T]
print(Vec.__name__, Vec.__type_params__[0].__name__, Vec.__value__)
''',
"pep709_class_x": '''
x = 7
class C:
    vals = [x for x in (1, 2)]
    after = x
print(C.vals, C.after, getattr(C, "x", "NO"), x)
''',
"class_cell_listcomp": '''
class A:
    pass
class B(A):
    def f(self):
        return [__class__.__name__ for _ in range(1)][0]
print(B().f())
''',
"ann_future_absent": '''
X = "mod"
class C:
    X = "cls"
    a: X
    b: list[X]
print(C.__annotations__)
''',
"method_reads_later_assign": '''
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
"dictcomp_vs_default": '''
k = "G"
class C:
    k = "C"
    d = {i: k for i in range(2)}
    def f(self, x=k):
        return x
print(C.d, C().f())
''',
"setcomp_module": '''
v = 3
class C:
    v = 100
    s = {v * i for i in (1, 2)}
print(sorted(C.s), C.v)
''',
"lambda_immediate": '''
x = "mod"
class C:
    x = "cls"
    a = (lambda: x)()
    b = (lambda x=x: x)()
    c = [x for _ in (0,)][0]
print(C.a, C.b, C.c)
''',
"nested_class_local_read": '''
def outer():
    x = 1
    class C:
        y = x
        def f(self):
            return x
        x = 2
    return C.y, C().f(), C.x
try:
    print(outer())
except Exception as e:
    print(type(e).__name__)
''',
}

def oracle(code: str) -> str:
    # run in clean subprocess to avoid future annotations contamination
    script = "import textwrap\ncode = " + repr(textwrap.dedent(code)) + "\nexec(compile(code, '<t>', 'exec'), {})\n"
    p = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=10)
    if p.returncode != 0:
        # some candidates print exception types themselves; if script failed unexpectedly:
        err = (p.stderr or "").strip().splitlines()[-1:] or ["ERR"]
        return "SUBPROC_ERR:" + err[-1]
    return p.stdout

def load_clients():
    clients = {}
    meta = Path("/workspace/meta-hack/.meta_api_key")
    if meta.exists():
        clients["wonder"] = (OpenAI(api_key=meta.read_text().strip(), base_url="https://api.meta.ai/v1", timeout=300), "muse-wonder-1.0")
    baseten = Path("/home/box/.config/seefix/baseten.env")
    if baseten.exists():
        env = {l.split("=",1)[0]: l.split("=",1)[1].strip() for l in baseten.read_text().splitlines() if "=" in l and not l.startswith("#")}
        clients["spark"] = (OpenAI(api_key=env["BASETEN_API_KEY"], base_url=env["BASETEN_BASE_URL"], timeout=300), env.get("BASETEN_MODEL","meta-models/muse-spark-open-1026"))
    beam = Path("/workspace/beam-hack/.reflection_api_key")
    if beam.exists():
        clients["beam"] = (OpenAI(api_key=beam.read_text().strip(), base_url="https://api.reflection.ai/openai/v1", timeout=400), "Beam-1.0-501B-A23B")
    nebius_path = Path("/home/box/.config/micro1-eval/nebius.env")
    # only if real key (not placeholder)
    if nebius_path.exists():
        env = {}
        for l in nebius_path.read_text().splitlines():
            if "=" in l and not l.strip().startswith("#"):
                k,v=l.split("=",1); env[k]=v.strip().strip('"')
        nk = env.get("NEBIUS_API_KEY","")
        if nk and "SENSITIVE" not in nk and len(nk) > 20:
            nb = env.get("NEBIUS_BASE_URL") or "https://api.tokenfactory.us-central1.nebius.com/v1/"
            clients["nemotron-super"] = (OpenAI(api_key=nk, base_url=nb, timeout=400), "nvidia/nemotron-3-super-120b-a12b")
            clients["deepseek-v3"] = (OpenAI(api_key=nk, base_url=nb, timeout=400), "deepseek-ai/DeepSeek-V3")
    return clients

def ask(client, model, code, expected):
    prompt = f"""Predict the exact stdout of this Python 3.13 (CPython) program.
Rules: exact CPython 3.13 semantics. Report stdout exactly. End with FINAL_ANSWER: {{"stdout":"..."}}

```python
{textwrap.dedent(code).strip()}
```
"""
    text = ""
    for attempt in range(3):
        r = client.chat.completions.create(
            model=model, temperature=0, max_tokens=4096,
            messages=[
                {"role":"system","content":"Predict CPython 3.13 exactly. Be concise. End with FINAL_ANSWER: <json>."},
                {"role":"user","content":prompt},
            ],
        )
        text = r.choices[0].message.content or ""
        if text.strip():
            break
        time.sleep(1.5)
    m = re.search(r'FINAL_ANSWER\s*:\s*(\{.*\})\s*\Z', text, re.S|re.I)
    pred = None
    if m:
        try:
            pred = json.loads(m.group(1)).get("stdout")
        except Exception:
            pred = None
    # normalize
    def norm(s):
        if s is None: return None
        s = s if isinstance(s,str) else str(s)
        if "\\n" in s and "\n" not in s.rstrip("\n"):
            s = s.replace("\\n","\n")
        return s.rstrip("\n")
    ok = norm(pred) == norm(expected)
    return ok, pred, len(text)

def main():
    oracles = {}
    for name, code in CANDIDATES.items():
        out = oracle(code)
        oracles[name] = out
        print(f"ORACLE {name}: {out!r}", flush=True)

    clients = load_clients()
    print("CLIENTS", list(clients), flush=True)
    results = {}
    for name, code in CANDIDATES.items():
        exp = oracles[name]
        if exp.startswith("SUBPROC_ERR"):
            continue
        results[name] = {"gt": exp, "models": {}}
        fails = 0
        for label, (client, model) in clients.items():
            print(f"ASK {name} {label}...", flush=True)
            try:
                ok, pred, n = ask(client, model, code, exp)
            except Exception as e:
                ok, pred, n = False, f"ERR:{e}", 0
            results[name]["models"][label] = {"pass": ok, "pred": pred}
            print(f"  {label} {'PASS' if ok else 'FAIL'} pred={pred!r}", flush=True)
            if not ok:
                fails += 1
        results[name]["fail_count"] = fails
    OUT.write_text(json.dumps(results, indent=2)+"\n")
    print("\n=== SUMMARY (fail_count / models) ===")
    for name, r in results.items():
        print(f"{name}: fails={r['fail_count']} gt={r['gt']!r}")
        for m, v in r["models"].items():
            print(f"  {m}: {'PASS' if v['pass'] else 'FAIL'} {v['pred']!r}")

if __name__ == "__main__":
    main()
