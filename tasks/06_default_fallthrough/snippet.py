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
