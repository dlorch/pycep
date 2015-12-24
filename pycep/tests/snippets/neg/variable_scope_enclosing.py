# UnboundLocalError: local variable 'n' referenced before assignment

def a():
    n = 12
    def b():
        n = n + 1
    b()
 
a()