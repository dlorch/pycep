# Python 2.7's *parser* is context-sensitive

# Derivation of ``print``:
#
# +- stmt
#    +- simple_stmt
#       +- small_stmt
#          +- print_stmt
#             +- "print"
#             +- test
#                +- ...
#                   +- atom
#                      +- "("
#                      +- testlist_comp
#                         +- ...
#                            +- atom: 5
#                      +- ")"
#
print(5)

# Derivation of ``print``:
#
# +- stmt
#    +- simple_stmt
#       +- small_stmt
#          +- expr_stmt
#             +- ...
#                +- term
#                   +- factor
#                      +- power
#                         +- atom: "print"
#                         +- trailer
#                            +- "("
#                            +- arglist
#                               +- ...
#                                  +- atom: 5
#                            +- ")"
#
from __future__ import print_function
print(5)
