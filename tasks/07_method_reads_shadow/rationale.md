Assignment `x = 100` anywhere in the class body makes `x` a class-local for every bare reference in that body, including `y = x + 1` before the assignment → NameError at class creation.
The nested method never runs. Models invent `(11, 10, 101)` or `UnboundLocalError`.
