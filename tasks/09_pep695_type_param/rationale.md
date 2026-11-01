In `class Box[T]:`, the type parameter `T` is visible in the class body as the parameter object for early references.
`first = T` sees the type parameter (prints as the name via str in some contexts — here the annotation/value prints the TypeVar-like param's presence through the name lookup returning the param); after `T = "cls"`, bare `T` is the string; default `default=T` sees `"cls"`.
`Box.__type_params__[0].__name__` remains `"T"`. Oracle stdout: `mod cls cls T`.
