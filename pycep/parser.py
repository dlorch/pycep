from __future__ import absolute_import
import parser

def parse(source):
    """The parser takes a string containing the source code as an input and
    returns a parse tree.
    
    * Python Language Reference: https://docs.python.org/2/reference/grammar.html
    * Non-Terminal Symbols: https://hg.python.org/cpython/file/2.7/Lib/symbol.py
    * Leaf Nodes: https://hg.python.org/cpython/file/2.7/Lib/symbol.py

    Args:
        source (string): Source code
    """
    # TODO: this is a stub
    st = parser.suite(source)
    return st