`f1 = lambda: a` → free `a` from module → `mod`.
`f2 = (lambda a=a: a)` → default evaluated in class body → `cls`.
`f3` from a listcomp → nested scope → module `mod`.
Stdout: `mod cls mod`.
