# Code in a nested function's body may access (but not rebind) local variables
# of an outer function, also known as free variables of the nested function.

def a():
    n = 12
    def b():
        n = n + 1
    b()
 
a()