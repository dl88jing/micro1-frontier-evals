v = "G"
class A:
    v = "C"
    rows = [[v for k in range(2)] for _ in range(2)]
    gen = list(v for _ in range(1))
    def meth(self, x=v):
        return x, self.v
print(A.rows, A.gen, A().meth(), A.meth(A(), "Q"))
