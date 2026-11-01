X = "outer"
class M:
    X = "inner"
    a: X = 1
    b = X
    def f(self, p: X = X):
        return p, M.__annotations__
print(M.b, M.__annotations__, M().f())
