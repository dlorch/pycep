# nonsense-script to explore edge edge cases in pycep's parser and analyzer

@my_decorator
@another_decorator('/login', methods=['GET', 'POST'])
@third_decorator()
@fourth_decorator()
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

if x < 0:
    x = 0
    print 'Negative changed to zero'
elif x == 0:
    print 'Zero'
elif x == 1:
    print 'Single'
else:
    print 'More'

if x < 0: print "smaller"
elif x > 0: print "bigger"
else: print "zero"

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

4 ** 16

g = lambda x: x**2

5 if foo == 30 else 19

# Generator expression
(x + y % 2 == 0 for x in range(0, 12) for y in range(4, 30) if x < y if x != 2)

# List comprehension
[(x, y) for x in [1,2,3] for y in [3,1,4] if x != y]

# Old style test statement / lambda definition
[ x for x in lambda: True, lambda: False if x() ]

(yield i)

# Backticks are a deprecated notation for repr()
hello = decorated_class()
`hello`

myset1 = {1, 2, 3,}
myset2 = {x for x in range(1, 10) if x % 2 == 0}

mydict1 = {'jack': 4098, 'sape': 4139}

# Dict comprehension
mydict2 = {x: x**2 for x in (2, 4, 6)}

# Ellipsis
mylist[1:2, ..., 0, ]

# Slices
mylist[-1]
mylist[-2:]
mylist[:-2]
mylist[::2]

import a
import a.b
import a.b.c, d.e.f

from a import b
from a.z import b as c
from . import b
from .. import *
from ..b.c import q as r
from ...c.d import (q as r, x as y, )

def f(a, b, c=12,): pass
def g(a, *b, **c): pass
def h(a=12, **b): pass
def i(*a): pass
def j((a, (c, d), ) = None): pass

# valid according to the grammar
def x(a=12, b): pass

divide(5, 2, )

# call with arguments unpacked from a list
args = [3, 6]
range(*args) 

# dictionaries can deliver keyword arguments with the **-operator
def parrot(voltage, state='a stiff', action='voom'):
    print "-- This parrot wouldn't", action,
    print "if you put", voltage, "volts through it.",
    print "E's", state, "!"

d = {"voltage": "four million", "state": "bleedin' demised", "action": "VOOM"}
parrot(**d)

a = "implicit" "string concatenation" "is probably done in the analyzer"

g("arg1 on this line"
  "arg2 on this line")
