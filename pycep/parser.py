from __future__ import absolute_import
import pycep.tokenizer
import parser
from StringIO import StringIO

def suite(source):
    """The parser takes a string containing the source code as an input and
    returns a parse tree.

    >>> import pycep.parser
    >>> st = pycep.parser.suite('print "Hello World"')
    >>> st.totuple()
    (257, (267, (268, (269, (272, (1, 'print'), (304, (305, (306, (307, (308, (310, (311, (312, (313, (314, (315, (316, (317, (318, (3, '"Hello World"'))))))))))))))))), (4, ''))), (4, ''), (0, ''))

    See also:
        * Python Language Reference: https://docs.python.org/2/reference/grammar.html
        * Non-Terminal Symbols: https://hg.python.org/cpython/file/2.7/Lib/symbol.py
        * Leaf Nodes: https://docs.python.org/2/library/token.html

    Args:
        source (string): Source code
        
    Returns:
        parser.st: Parse Tree
    """
    # TODO: this is a stub
    st = parser.suite(source)
    return st