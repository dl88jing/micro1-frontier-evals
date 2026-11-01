a = "mod"
class K:
    a = "cls"
    f1 = lambda: a
    f2 = (lambda a=a: a)
    f3 = [(lambda: a) for _ in range(1)][0]
print(K.f1(), K.f2(), K.f3())
