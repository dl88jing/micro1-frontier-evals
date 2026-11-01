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
