PEP 572: an assignment expression target in a comprehension inside a class body is a SyntaxError.
Separately, `def m(self, a=x)` with a later `x = ["c"]` in the same class nested in a function raises NameError when evaluating the default.
Stdout is the two exception type names joined: `SyntaxError|NameError`.
