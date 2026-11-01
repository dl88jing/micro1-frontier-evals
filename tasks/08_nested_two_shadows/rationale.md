Both `a` and `b` are assigned later in the class body, so they are class-local for the entire body.
`x = a` runs before `a` is bound → NameError. Models predict `(1, 2, (1, 2), 10, 20)`.
