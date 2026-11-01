When a class is nested in a function, names assigned anywhere in the class body are treated as class-local for the entire body.
Because `x = 100` appears later, `y = x + 1` does not read the enclosing `x = 10`; it looks for a class-local `x` that is not yet bound → NameError.
Models often invent stdout `11 100 101` as if sequential enclosing lookup applied.
