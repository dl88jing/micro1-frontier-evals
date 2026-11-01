n = 7
class T:
    n = 3
    data = list((n + i) for i in range(3))
    vals = [n, n + 1]
    def g(self):
        return list((n + i) for i in range(2))
print(T.data, T.vals, T().g())
