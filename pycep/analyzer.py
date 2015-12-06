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
    
    if key == symbol.single_input:
        raise NotImplementedError("single_input")
    elif key == symbol.file_input:
        node = ast.Module()
        node.body = []
        node.body.append(_parse(values[0])) # TODO
        return node
    elif key == symbol.eval_input:
        raise NotImplementedError("eval_input")
    elif key == symbol.decorator:
        raise NotImplementedError("decorator")
    elif key == symbol.decorators:
        raise NotImplementedError("decorators")
    elif key == symbol.decorated:
        raise NotImplementedError("decorated")
    elif key == symbol.funcdef:
        raise NotImplementedError("funcdef")
    elif key == symbol.parameters:
        raise NotImplementedError("parameters")
    elif key == symbol.varargslist:
        raise NotImplementedError("varargslist")
    elif key == symbol.fpdef:
        raise NotImplementedError("fpdef")
    elif key == symbol.fplist:
        raise NotImplementedError("fplist")
    elif key == symbol.stmt:
        # TODO
        return _parse(values[0])
    elif key == symbol.simple_stmt:
        # TODO
        return _parse(values[0])
    elif key == symbol.small_stmt:
        # TODO
        return _parse(values[0])
    elif key == symbol.expr_stmt:
        raise NotImplementedError("expr_stmt")
    elif key == symbol.augassign:
        raise NotImplementedError("augassign")
    elif key == symbol.print_stmt:
        node = ast.Print()
        node.dest = None # TODO
        node.values = [_parse(values[1])] # TODO
        node.nl = True # TODO
        return node
    elif key == symbol.del_stmt:
        raise NotImplementedError("del_stmt")
    elif key == symbol.pass_stmt:
        raise NotImplementedError("pass_stmt")
    elif key == symbol.flow_stmt:
        raise NotImplementedError("flow_stmt")
    elif key == symbol.break_stmt:
        raise NotImplementedError("break_stmt")
    elif key == symbol.continue_stmt:
        raise NotImplementedError("continue_stmt")
    elif key == symbol.return_stmt:
        raise NotImplementedError("return_stmt")
    elif key == symbol.yield_stmt:
        raise NotImplementedError("yield_stmt")
    elif key == symbol.raise_stmt:
        raise NotImplementedError("raise_stmt")
    elif key == symbol.import_stmt:
        raise NotImplementedError("import_stmt")
    elif key == symbol.import_name:
        raise NotImplementedError("import_name")
    elif key == symbol.import_from:
        raise NotImplementedError("import_from")
    elif key == symbol.import_as_name:
        raise NotImplementedError("import_as_name")
    elif key == symbol.dotted_as_name:
        raise NotImplementedError("dotted_as_name")
    elif key == symbol.dotted_name:
        raise NotImplementedError("dotted_name")
    elif key == symbol.global_stmt:
        raise NotImplementedError("global_stmt")
    elif key == symbol.exec_stmt:
        raise NotImplementedError("exec_stmt")
    elif key == symbol.assert_stmt:
        raise NotImplementedError("assert_stmt")
    elif key == symbol.compound_stmt:
        raise NotImplementedError("compound_stmt")
    elif key == symbol.if_stmt:
        raise NotImplementedError("if_stmt")
    elif key == symbol.while_stmt:
        raise NotImplementedError("while_stmt")
    elif key == symbol.for_stmt:
        raise NotImplementedError("for_stmt")
    elif key == symbol.try_stmt:
        raise NotImplementedError("try_stmt")
    elif key == symbol.with_stmt:
        raise NotImplementedError("with_stmt")
    elif key == symbol.with_item:
        raise NotImplementedError("with_item")
    elif key == symbol.except_clause:
        raise NotImplementedError("except_clause")
    elif key == symbol.suite:
        raise NotImplementedError("suite")
    elif key == symbol.testlist_safe:
        raise NotImplementedError("testlist_safe")
    elif key == symbol.old_test:
        raise NotImplementedError("old_test")
    elif key == symbol.old_lambdef:
        raise NotImplementedError("old_lambdef")
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
    elif key == symbol.comp_op:
        raise NotImplementedError("comp_op")
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
    elif key == symbol.listmaker:
        raise NotImplementedError("listmaker")
    elif key == symbol.testlist_comp:
        raise NotImplementedError("testlist_comp")
    elif key == symbol.lambdef:
        raise NotImplementedError("lambdef")
    elif key == symbol.trailer:
        raise NotImplementedError("trailer")
    elif key == symbol.subscriptlist:
        raise NotImplementedError("subscriptlist")
    elif key == symbol.subscript:
        raise NotImplementedError("subscript")
    elif key == symbol.sliceop:
        raise NotImplementedError("sliceop")
    elif key == symbol.exprlist:
        raise NotImplementedError("exprlist")
    elif key == symbol.testlist:
        raise NotImplementedError("testlist")
    elif key == symbol.dictorsetmaker:
        raise NotImplementedError("dictorsetmaker")
    elif key == symbol.classdef:
        raise NotImplementedError("classdef")
    elif key == symbol.arglist:
        raise NotImplementedError("arglist")
    elif key == symbol.argument:
        raise NotImplementedError("argument")
    elif key == symbol.list_iter:
        raise NotImplementedError("list_iter")
    elif key == symbol.list_for:
        raise NotImplementedError("list_for")
    elif key == symbol.list_if:
        raise NotImplementedError("list_if")
    elif key == symbol.comp_iter:
        raise NotImplementedError("comp_iter")
    elif key == symbol.comp_for:
        raise NotImplementedError("comp_for")
    elif key == symbol.testlist1:
        raise NotImplementedError("testlist1")
    elif key == symbol.encoding_decl:
        raise NotImplementedError("encoding_decl")
    elif key == symbol.yield_expr:
        raise NotImplementedError("yield_expr")
    elif key == token.STRING:
        node = ast.Str(values[0][1:-1].decode("string-escape"))
        return node
    else:
        raise ValueError("Unexpected symbol/token `%d'" % key)