class Fake:
    def __bool__(self):
        print("bool")
        return False
    def __len__(self):
        print("len")
        return 0
print(bool(Fake()))
class Fake2:
    def __len__(self):
        print("len2")
        return 0
print(bool(Fake2()))
