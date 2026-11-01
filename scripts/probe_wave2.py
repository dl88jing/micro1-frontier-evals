#!/usr/bin/env python3
"""Wave2 hard candidates — parallel per-task across models, incremental save."""
from __future__ import annotations
import json, re, textwrap, time, subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "probe_wave2.json"
LOG = ROOT / "results" / "probe_wave2_log.txt"

CANDIDATES = {
"default_global_fallthrough": '''
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
"walrus_and_default": '''
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
"dictcomp_default_assign": '''
k="G"
def f():
    k="L"
    class C:
        d={i:k for i in range(2)}
        def m(self,a=k):
            return a
        k="C"
    return C.d, C().m(), C.k
try:
    print(f())
except Exception as e:
    print(type(e).__name__)
''',
"lambda_default_vs_body": '''
x="mod"
def f():
    x="loc"
    class C:
        a=(lambda: x)()
        b=(lambda x=x: x)()
        c=[x for _ in (0,)][0]
        x="cls"
        d=(lambda: x)()
        e=(lambda x=x: x)()
        f=[x for _ in (0,)][0]
    return C.a,C.b,C.c,C.d,C.e,C.f
print(f())
''',
"exc_delete_unbound": '''
def run():
    e = "outer"
    try:
        try:
            1/0
        except ZeroDivisionError as e:
            inner = type(e).__name__
        return inner, e
    except Exception as ex:
        return inner, type(ex).__name__
print(run())
''',
"pep695_assign_read": '''
T="mod"
class Box[T]:
    first=T
    T="cls"
    second=T
    def get(self, default=T):
        return default
print(Box.first, Box.second, Box().get(), Box.__type_params__[0].__name__)
''',
"combo_default_listcomp": '''
x = ["G"]
def f():
    x = ["L"]
    class C:
        d = [x for _ in range(1)][0]
        def m(self, a=x):
            return a, x
        x = ["C"]
        after = x
    return C.d, C().m(), C.after
print(f())
''',
"nested_two_shadows": '''
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
"pep709_plus_default": '''
x = 7
def f():
    x = 3
    class C:
        vals = [x for x in (1, 2)]
        after = x
        def m(self, a=x):
            return a
        x = 99
    return C.vals, C.after, C().m(), getattr(C,"x","NO"), x
try:
    print(f())
except Exception as e:
    print(type(e).__name__)
''',
"genexp_vs_list_enclosing": '''
n = "G"
def f():
    n = "L"
    class C:
        g = list((n for _ in range(1)))
        L = [n for _ in range(1)]
        n = "C"
        after = n
    return C.g, C.L, C.after
print(f())
''',
"annotation_fn_enclosing": '''
X="mod"
def f():
    X="loc"
    class C:
        X="cls"
        a: X
        def m(self, v: X = X) -> X:
            return v
        b: list[X]
    return C.__annotations__, C.m.__annotations__, C().m()
print(f())
''',
"type_param_bound": '''
X = int
class C[T: X]:
    X = str
print(C.__type_params__[0].__bound__.__name__, C.X.__name__)
''',
}

def log(msg):
    with LOG.open("a") as f:
        f.write(msg+"\n")
    print(msg, flush=True)

def oracle(code: str) -> str:
    script = "code = " + repr(textwrap.dedent(code)) + "\nexec(compile(code, '<t>', 'exec'), {'__name__':'__main__'})\n"
    p = subprocess.run(["python3", "-c", script], capture_output=True, text=True, timeout=10)
    if p.returncode != 0:
        err = (p.stderr or "").strip().splitlines()[-1:] or ["ERR"]
        return "SUBPROC_ERR:" + err[-1]
    return p.stdout

def load_clients():
    clients = {}
    meta = Path("/workspace/meta-hack/.meta_api_key")
    if meta.exists():
        clients["wonder"] = (OpenAI(api_key=meta.read_text().strip(), base_url="https://api.meta.ai/v1", timeout=180), "muse-wonder-1.0")
    baseten = Path("/home/box/.config/seefix/baseten.env")
    if baseten.exists():
        env = {l.split("=",1)[0]: l.split("=",1)[1].strip() for l in baseten.read_text().splitlines() if "=" in l and not l.startswith("#")}
        clients["spark"] = (OpenAI(api_key=env["BASETEN_API_KEY"], base_url=env["BASETEN_BASE_URL"], timeout=180), env.get("BASETEN_MODEL","meta-models/muse-spark-open-1026"))
    beam = Path("/workspace/beam-hack/.reflection_api_key")
    if beam.exists():
        clients["beam"] = (OpenAI(api_key=beam.read_text().strip(), base_url="https://api.reflection.ai/openai/v1", timeout=240), "Beam-1.0-501B-A23B")
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
        try:
            r = client.chat.completions.create(
                model=model, temperature=0, max_tokens=2048,
                messages=[
                    {"role":"system","content":"Predict CPython 3.13 exactly. Be concise. End with FINAL_ANSWER: <json>."},
                    {"role":"user","content":prompt},
                ],
            )
            text = r.choices[0].message.content or ""
        except Exception as e:
            text = f"ERR:{e}"
            time.sleep(1)
            continue
        if text.strip() and not text.startswith("ERR:"):
            break
        time.sleep(1.2)
    m = re.search(r'FINAL_ANSWER\s*:\s*(\{.*\})\s*\Z', text, re.S|re.I)
    pred = None
    if m:
        try:
            pred = json.loads(m.group(1)).get("stdout")
        except Exception:
            pred = None
    if pred is None:
        # fallback: look for any FINAL_ANSWER JSON
        m2 = re.search(r'FINAL_ANSWER\s*:\s*(\{.*?\})', text, re.S|re.I)
        if m2:
            try:
                pred = json.loads(m2.group(1)).get("stdout")
            except Exception:
                pass
    def norm(s):
        if s is None: return None
        s = s if isinstance(s,str) else str(s)
        if "\\n" in s and "\n" not in s.rstrip("\n"):
            s = s.replace("\\n","\n")
        return s.rstrip("\n")
    ok = norm(pred) == norm(expected)
    return ok, pred, text[:200]

def main():
    LOG.write_text("")
    oracles = {}
    for name, code in CANDIDATES.items():
        out = oracle(code)
        oracles[name] = out
        log(f"ORACLE {name}: {out!r}")

    clients = load_clients()
    log(f"CLIENTS {list(clients)}")
    results = {}

    for name, code in CANDIDATES.items():
        exp = oracles[name]
        if exp.startswith("SUBPROC_ERR"):
            log(f"SKIP {name}")
            continue
        results[name] = {"gt": exp, "models": {}}
        # parallel across models
        futs = {}
        with ThreadPoolExecutor(max_workers=len(clients)) as ex:
            for label, (client, model) in clients.items():
                futs[ex.submit(ask, client, model, code, exp)] = label
            for fut in as_completed(futs):
                label = futs[fut]
                try:
                    ok, pred, snip = fut.result()
                except Exception as e:
                    ok, pred, snip = False, f"ERR:{e}", ""
                results[name]["models"][label] = {"pass": ok, "pred": pred}
                log(f"  {name} {label} {'PASS' if ok else 'FAIL'} pred={pred!r}")
        results[name]["fail_count"] = sum(1 for v in results[name]["models"].values() if not v["pass"])
        OUT.write_text(json.dumps(results, indent=2)+"\n")

    log("\n=== SUMMARY ===")
    hard=[]
    for name, r in results.items():
        marks={m:('P' if x['pass'] else 'F') for m,x in r['models'].items()}
        log(f"{name}: fails={r['fail_count']} {marks}")
        if r['fail_count']>=2:
            hard.append(name)
    log(f"HARD: {hard}")

if __name__ == "__main__":
    main()
