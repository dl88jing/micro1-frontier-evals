x = "outer"
class C:
    x = "class"
    y = [x for i in range(1)]
    z = (lambda: x)()
    @staticmethod
    def f(x=x):
        return x
print(C.y[0], C.z, C.f(), C.f("arg"))
