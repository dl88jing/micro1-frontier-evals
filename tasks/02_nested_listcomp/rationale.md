Both the outer and inner listcomps are nested scopes. Free variable `v` resolves to module `"G"`.
The genexp `list(v for _ in range(1))` similarly sees module `v`.
Method default `x=v` is evaluated in the class namespace → `"C"`.
Models frequently produce rows filled with `"C"`.
