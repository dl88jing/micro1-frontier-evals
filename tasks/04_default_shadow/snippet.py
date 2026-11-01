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
