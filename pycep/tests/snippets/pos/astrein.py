# nonsense-script to explore edge edge cases in pycep's parser and analyzer

@my_decorator
@another_decorator('/login', methods=['GET', 'POST'])
@third_decorator()
def decorated_func():
    return 5
    
@classdecorator
class decorated_class():
    pass
    
for num in range(2, 10):
    if num % 2 == 0:
        print "Found an even number", num
        continue
    print "Found a number", num
    
for x in [1, 2, 3]:
    pass
del x

glob = 1
another = 2
def globalvar():
    global glob
    global glob, another
    glob = 5
    another = 6
globalvar()