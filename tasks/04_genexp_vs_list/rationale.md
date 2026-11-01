`data` uses a generator expression (nested scope) → module `n=7` → `[7,8,9]`.
`vals = [n, n+1]` evaluates bare `n` in the class body after `n=3` → `[3,4]`.
`g`'s genexp closes over module `n` again → `[7,8]`.
