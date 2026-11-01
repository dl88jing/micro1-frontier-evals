def build():
    x = 10
    class C:
        y = x + 1
        def bump(self):
            return x
        x = 100
        z = x + 1
    return C.y, C().bump(), C.z
try:
    print(build())
except Exception as e:
    print(type(e).__name__)
