outs=[]
try:
    compile("class C:\n data=[(y:=i) for i in range(1)]\n","<x>","exec")
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
