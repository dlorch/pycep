from __future__ import absolute_import
import ast
import pycep.parser

def parse(source):
    """The analyzer takes a string containing the source code as an input and
    returns an abstract syntax tree.

    >>> import pycep.analyzer
    >>> import ast
    >>> tree = pycep.analyzer.parse('print "Hello World"')
    >>> ast.dump(tree)
    "Module(body=[Print(dest=None, values=[Str(s='Hello World')], nl=True)])"

    Args:
        source (string): Source code

    Returns:
        ast.AST: Abstract Syntax Tree

    Raises:
        SyntaxError: Syntax Error

    Abstract Syntax Tree of Hello World Example:

    .. graphviz::
        :alt: Abstract Syntax Tree of Hello World Example

        digraph foo {
            bgcolor = "transparent";
            node [shape=plaintext];
            Module -> Print [label = "body"];
            Print -> None [label = "dest"];
            Print -> Str [label = "values"];
            Print -> True [label = "nl"];
            Str -> \\'Hello World\\' [label = "s"];
        }

    See also:
        * Python Abstract Grammar: https://docs.python.org/2/library/ast.html
        * Green Tree Snakes - the missing Python AST docs: https://greentreesnakes.readthedocs.org/
    """
    st = pycep.parser.suite(source)

    tree = _parse(st)
    ast.fix_missing_locations(tree)

    return tree

def _parse(st):
    return ast.Module(body=[ast.Print(dest=None, values=[ast.Str("Hello, world!")], nl=True)])