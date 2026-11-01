In a class nested in a function, any assignment to `x` marks `x` local for the entire class body.
The default `a=x` is evaluated while building the function object, before `x = ["class"]` runs, so the class-local `x` is still unbound → NameError.
Frontier models often predict `(['outer'], ['class'])`.
