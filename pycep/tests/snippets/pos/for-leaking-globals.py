# Python 2.7 and Python 3 produce different outputs due to
# "..loop control variables are no longer leaked into the surrounding scope.."
# https://docs.python.org/3/whatsnew/3.0.html

i = 1
print([i for i in range(5)])
print(i)
