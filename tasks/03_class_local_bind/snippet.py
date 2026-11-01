def build():
    x = 10
    class E:
        y = x + 1
        x = 100
        z = x + 1
    return E
try:
    E = build()
    print(E.y, E.x, E.z)
except Exception as e:
    print(type(e).__name__)
