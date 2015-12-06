from __future__ import absolute_import
import ast
import token
import symbol
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
            Str -> "\\'Hello World\\'" [label = "s"];
        }

    See also:
        * Python Abstract Grammar: https://docs.python.org/2/library/ast.html
        * Green Tree Snakes - the missing Python AST docs: https://greentreesnakes.readthedocs.org/
    """
    parse_tree = pycep.parser.suite(source)
    tree = _parse(parse_tree.totuple())
    ast.fix_missing_locations(tree) # TODO

    return tree

def _parse(parse_tree):
    key, values = parse_tree[0], parse_tree[1:]
    
    if key == symbol.file_input:
        node = ast.Module()
        node.body = []
        node.body.append(_parse(values[0])) # TODO
        return node
    elif key == symbol.stmt:
        # TODO
        return _parse(values[0])
    elif key == symbol.simple_stmt:
        # TODO
        return _parse(values[0])
    elif key == symbol.small_stmt:
        # TODO
        return _parse(values[0])
    elif key == symbol.print_stmt:
        node = ast.Print()
        node.dest = None # TODO
        node.values = [_parse(values[1])] # TODO
        node.nl = True # TODO
        return node
    elif key == symbol.test:
        # TODO
        return _parse(values[0])
    elif key == symbol.or_test:
        # TODO
        return _parse(values[0])
    elif key == symbol.and_test:
        # TODO
        return _parse(values[0])
    elif key == symbol.not_test:
        # TODO
        return _parse(values[0])
    elif key == symbol.comparison:
        # TODO
        return _parse(values[0])
    elif key == symbol.expr:
        # TODO
        return _parse(values[0])
    elif key == symbol.xor_expr:
        # TODO
        return _parse(values[0])
    elif key == symbol.and_expr:
        # TODO
        return _parse(values[0])
    elif key == symbol.shift_expr:
        # TODO
        return _parse(values[0])
    elif key == symbol.arith_expr:
        # TODO
        return _parse(values[0])
    elif key == symbol.term:
        # TODO
        return _parse(values[0])
    elif key == symbol.factor:
        # TODO
        return _parse(values[0])
    elif key == symbol.power:
        # TODO
        return _parse(values[0])
    elif key == symbol.atom:
        # TODO
        return _parse(values[0])
    elif key == token.STRING:
        node = ast.Str(values[0][1:-1].decode("string-escape"))
        return node
    else:
        if key in token.tok_name:
            tok_name = token.tok_name[key]
        elif key in symbol.sym_name:
            tok_name = symbol.sym_name[key]
        else:
            tok_name = None

        raise NotImplementedError(tok_name)