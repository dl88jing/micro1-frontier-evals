Class-body name lookup for bare names is class dict → globals → builtins (not the enclosing function).
Because `x = "C"` appears later, `a=x` in the default uses LOAD_NAME, finds no class binding yet, and falls through to the module global `"G"`.
The method body free variable `x` closes over the enclosing function local `"L"`.
Wrong answer seen in probes: `('L', 'L', 'C')`.
