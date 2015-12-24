# If a function only reads from a variable, it's assumed to be global. If the
# function writes to it ever, it's assumed to be local. In the second function,
# a is written to, so it's assumed to be local.
#
# Code in a nested function's body may access (but not rebind) local variables
# of an outer function, also known as free variables of the nested function.

a = 123
def f():
    print a

f() # prints 123

b = 123
def g():
    print b
    b = 456
    print b

g() # UnboundLocalError: local variable 'b' referenced before assignment