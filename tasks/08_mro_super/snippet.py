class A:
    def f(self):
        return "A"
class B(A):
    def f(self):
        return "B"+super().f()
class C(A):
    def f(self):
        return "C"+super().f()
class D(C,B):
    def f(self):
        return "D"+super().f()
print(D().f())
print([c.__name__ for c in D.__mro__])
