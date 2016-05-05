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

exec "print 5+5"
exec "print 5+5" in globals()
exec "print 5+5" in globals(), locals()

a = 2
assert a % 2 == 0
assert a % 2 == 0, "value was odd, should be even"

import signal
with signal.blocked() as a, signal.blocked() as b:
    pass

m = 5; m += 1; print m

print
print "foo"
print "foo", "bar"
print "foo", "bar",

import sys
print >> sys.stderr
print >> sys.stderr, "error"
print >> sys.stderr, "error", "another error"
print >> sys.stderr, "error", "another error",

try:
    f = open('doesnotexist.txt')
    s = f.readline()
    i = int(s.strip())
except IOError as e:
    print "I/O error({0}): {1}".format(e.errno, e.strerror)
except ValueError:
    print "Could not convert data to an integer."
except:
    print "Unexpected error:", sys.exc_info()[0]
    raise
    raise Exception("spam")
    raise Exception, "spam"
    raise Exception, "spam", sys.exc_info()[2]
    
def divide(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        print "division by zero!"
    else:
        print "result is", result
    finally:
        print "executing finally clause"

try:
    print "Hello"
finally:
    print "World"

True or False
5 == 2 or 2 == 2 or False

True and False
12 == 2 and 4 == 4 and True

foo = 5
foo

foo | 12 | 4

12 ^ 4 ^ 32 ^ 55

5 & 42 & 10001

foo << 5 >> 42

+5
-4
~foo