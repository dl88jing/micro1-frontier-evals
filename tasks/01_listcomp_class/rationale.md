In CPython, a class body is not an enclosing scope for nested functions or comprehensions.
`[x for i in range(1)]` creates a nested function scope whose free variable `x` resolves to the module-global `"outer"`, not the class attribute `x = "class"`.
`(lambda: x)()` likewise closes over the module.
The default `x=x` on `f` is evaluated in the class body namespace, so it captures `"class"`.
Correct stdout: `outer outer class arg`.
Frontier models often answer `class outer class arg`, wrongly feeding class-local `x` into the listcomp.
