n = 5
class C:
    g = (n for _ in range(2))
    n = 99
    L = [n for _ in range(2)]
print(list(C.g), C.L, C.n)
