T="mod"
class Box[T]:
    first=T
    T="cls"
    second=T
    def get(self, default=T):
        return default
print(Box.first, Box.second, Box().get(), Box.__type_params__[0].__name__)
