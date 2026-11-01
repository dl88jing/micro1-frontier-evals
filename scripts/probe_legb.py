#!/usr/bin/env python3
"""Probe Python LEGB/class-body tasks against Muse Wonder + Spark."""
from __future__ import annotations

import io
import json
import contextlib
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "probe_legb.json"

meta_key = Path("/workspace/meta-hack/.meta_api_key").read_text().strip()
env = Path("/home/box/.config/seefix/baseten.env").read_text()
bk = {
    l.split("=", 1)[0]: l.split("=", 1)[1].strip()
    for l in env.splitlines()
    if "=" in l and not l.startswith("#")
}
W = OpenAI(api_key=meta_key, base_url="https://api.meta.ai/v1", timeout=400)
S = OpenAI(api_key=bk["BASETEN_API_KEY"], base_url=bk["BASETEN_BASE_URL"], timeout=400)


def run_py(code: str) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(code, "<t>", "exec"), {})
    return buf.getvalue()


def ask(client, model, prompt, max_tokens=8192):
    r = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "system",
                "content": "Think step-by-step about Python 3.12 semantics. End with FINAL_ANSWER: <compact json>",
            },
            {"role": "user", "content": prompt},
        ],
    )
    text = r.choices[0].message.content or ""
    m = re.search(r"FINAL_ANSWER\s*:\s*(.*)$", text, re.S | re.I)
    ans = (m.group(1).strip() if m else f"<no_final L={len(text)}>")[:500]
    return ans, getattr(r.usage, "completion_tokens", 0)


CODES = {
    "01_listcomp_class": '''
x = "outer"
class C:
    x = "class"
    y = [x for i in range(1)]
    z = (lambda: x)()
    @staticmethod
    def f(x=x):
        return x
print(C.y[0], C.z, C.f(), C.f("arg"))
''',
    "02_double_comp": '''
v = "G"
class A:
    v = "C"
    rows = [[v for k in range(2)] for _ in range(2)]
    gen = list(v for _ in range(1))
    def meth(self, x=v):
        return x, self.v
print(A.rows, A.gen, A().meth(), A.meth(A(), "Q"))
''',
    "03_genexp_method": '''
n = 7
class T:
    n = 3
    data = list((n + i) for i in range(3))
    def g(self):
        return list((n + i) for i in range(2))
    vals = [n, n+1]
print(T.data, T.vals, T().g())
''',
    "04_annotation_class": '''
X = "outer"
class M:
    X = "inner"
    a: X = 1
    b = X
    def f(self, p: X = X):
        return p, M.__annotations__
print(M.b, M.__annotations__, M().f())
''',
    "05_enclosing_before_assign": '''
def build():
    x = 10
    class E:
        y = x + 1
        x = 100
        z = x + 1
    return E
E = build()
print(E.y, E.x, E.z)
''',
    "06_decorator_default": '''
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
''',
    "07_walrus_class": '''
m = 0
class W:
    xs = [m := i for i in range(3)]
    ys = m
print(W.xs, W.ys, m)
''',
    "08_slots_dict": '''
class P:
    __slots__ = ("x",)
    def __init__(self, x):
        self.x = x
p = P(1)
try:
    p.y = 2
    print("set_y")
except AttributeError:
    print("no_y")
print(p.x, hasattr(p, "__dict__"))
''',
    "09_mro_super": '''
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
''',
    "10_bool_len": '''
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
''',
}


def lfsr(n=24):
    state = 0xACE1
    bits = []
    for _ in range(n):
        bit = ((state >> 0) ^ (state >> 2) ^ (state >> 3) ^ (state >> 5)) & 1
        state = ((state << 1) & 0xFFFF) | bit
        bits.append(bit)
    return bits, state


def main():
    verified = {}
    for k, c in list(CODES.items()):
        try:
            out = run_py(c)
            verified[k] = out
            print(f"OK {k}: {out!r}")
        except Exception as e:
            print(f"ERR {k}: {type(e).__name__}: {e}")
            del CODES[k]

    bits, st = lfsr(24)
    gt_lfsr = {
        "bits": "".join(map(str, bits)),
        "state_hex": f"{st:04x}",
        "pop": sum(bits),
    }
    print("LFSR24", gt_lfsr)

    tz = ZoneInfo("America/Los_Angeles")
    t1 = datetime(2024, 3, 9, 1, 30, tzinfo=tz)
    t2 = datetime(2024, 3, 10, 3, 30, tzinfo=tz)
    ghost = datetime(2024, 3, 10, 2, 30, tzinfo=tz)
    gt_dst = {
        "absolute_hours": (t2.timestamp() - t1.timestamp()) / 3600,
        "same_tzinfo_sub_hours": (t2 - t1).total_seconds() / 3600,
        "ghost_offset_h": ghost.utcoffset().total_seconds() / 3600,
        "span_sec": datetime(2024, 3, 10, 4, 0, tzinfo=tz).timestamp()
        - datetime(2024, 3, 10, 1, 0, tzinfo=tz).timestamp(),
    }

    prompts = []
    for k, c in CODES.items():
        prompts.append(
            (
                k,
                "Exact stdout of this Python 3.12 program (CPython):\n```\n"
                + c.strip()
                + '\n```\nFINAL_ANSWER: {"stdout":"..."}',
                {"stdout": verified[k]},
            )
        )
    prompts.append(
        (
            "lfsr24",
            """16-bit LFSR, state starts at 0xACE1. For each of 24 steps:
  bit = (LSB XOR bit2 XOR bit3 XOR bit5)  # bits numbered from LSB=0
  state = ((state << 1) & 0xFFFF) | bit
Report the 24-bit string (first step = leftmost), final state as 4-lowercase-hex, and popcount of the 24 bits.
FINAL_ANSWER: {"bits":"01...","state_hex":"....","pop":N}
""",
            gt_lfsr,
        )
    )
    prompts.append(
        (
            "dst_pack",
            """Python 3.12 zoneinfo America/Los_Angeles:
t1=datetime(2024,3,9,1,30,tzinfo=ZoneInfo("America/Los_Angeles"))
t2=datetime(2024,3,10,3,30,tzinfo=ZoneInfo("America/Los_Angeles"))
ghost=datetime(2024,3,10,2,30,tzinfo=ZoneInfo("America/Los_Angeles"))
absolute_hours=(t2.timestamp()-t1.timestamp())/3600
same_tzinfo_sub_hours=(t2-t1).total_seconds()/3600
ghost_offset_h=ghost.utcoffset().total_seconds()/3600
span_sec=datetime(2024,3,10,4,0,tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()-datetime(2024,3,10,1,0,tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()
FINAL_ANSWER: {"absolute_hours":N,"same_tzinfo_sub_hours":N,"ghost_offset_h":N,"span_sec":N}
""",
            gt_dst,
        )
    )

    results = {}
    for name, prompt, gt in prompts:
        print(f"\n==== {name}")
        results[name] = {"gt": gt}
        for lab, client, model in [
            ("W", W, "muse-wonder-1.0"),
            ("S", S, "meta-models/muse-spark-open-1026"),
        ]:
            try:
                ans, tok = ask(client, model, prompt)
            except Exception as e:
                ans, tok = f"ERR {e}", 0
            ok = False
            try:
                j = ans[ans.find("{") : ans.rfind("}") + 1]
                got = json.loads(j)
                if "stdout" in gt:
                    ok = got.get("stdout", "").rstrip("\n") == gt["stdout"].rstrip("\n")
                else:
                    ok = True
                    for k, v in gt.items():
                        if isinstance(v, float):
                            ok = ok and abs(float(got[k]) - v) < 1e-9
                        else:
                            ok = ok and got.get(k) == v
            except Exception:
                ok = False
            results[name][lab] = {"pass": ok, "ans": ans[:300], "tok": tok}
            print(f"  {lab} {'PASS' if ok else 'FAIL'} tok={tok}: {ans[:180]}")

    OUT.write_text(json.dumps(results, indent=2))
    print("\n===== FAILS =====")
    for n, r in results.items():
        if not r["W"]["pass"] or not r["S"]["pass"]:
            print(n, "W", r["W"]["pass"], "S", r["S"]["pass"])
    print("saved", OUT)


if __name__ == "__main__":
    main()
