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
