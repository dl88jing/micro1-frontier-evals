Generator expressions always create a nested function scope; free `n` is looked up when the genexp runs, seeing the module global that was current at class creation time (still 5).
List comprehensions in class scope also keep a nested function scope (PEP 709 does not inline them there), so they likewise close over module `n=5`, not the later class attribute `n=99`.
Models frequently predict `[5, 5] [99, 99] 99`.
