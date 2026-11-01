PEP 695 introduces a type-parameter object on `Box.__type_params__`, but ordinary class-body value expressions still use LOAD_NAME (class dict → globals).
Before `T = "cls"`, `first = T` therefore reads the module global `"mod"`, not the type parameter.
After the assignment, `second = T` and the default `default=T` see the class attribute `"cls"`.
`Box.__type_params__[0].__name__` remains `"T"`.
Stdout: `mod cls cls T`. Models often substitute the type-parameter object for `first` or confuse the default.
