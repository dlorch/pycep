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

def _parse(parse_tree, ctx=ast.Load()):
    key, values = parse_tree[0], parse_tree[1:]
    
    if key == symbol.single_input:
        raise NotImplementedError("single_input")
    elif key == symbol.file_input:
        node = ast.Module()
        node.body = []
        
        for value in values[:-2]:
            node.body.append(_parse(value, ctx))

        assert values[-2][0] == token.NEWLINE
        assert values[-1][0] == token.ENDMARKER
        
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
        node = ast.FunctionDef()
        assert len(values) == 5
        assert values[0][0] == token.NAME
        assert values[0][1] == "def"
        assert values[1][0] == token.NAME
        node.name = values[1][1]
        node.args = _parse(values[2], ctx)
        assert values[3][0] == token.COLON
        assert values[3][1] == ":"
        node.body = _parse(values[4], ctx)
        node.decorator_list = [] # TODO
        return node
    elif key == symbol.parameters:
        node = ast.arguments()
        assert len(values) == 3
        assert values[0][0] == token.LPAR
        assert values[0][1] == "("
        assert values[1][0] == symbol.varargslist
        
        args = []
        vararg = []
        kwarg = []
        defaults = []
        
        for value in values[1][1:]:
            if value[0] == symbol.fpdef:
                if value[1][0] == token.NAME:
                    n = ast.Name()
                    n.id = value[1][1]
                    n.ctx = ast.Param()
                    args.append(n)
                else:
                    raise NotImplementedError
            else:
                raise NotImplementedError
        
        if len(args) > 0:
            node.args = args
        else:
            node.args = None

        if len(vararg) > 0:
            node.vararg = vararg
        else:
            node.vararg = None
            
        if len(kwarg) > 0:
            node.kwarg = kwarg
        else:
            node.kwarg = None
            
        node.defaults = defaults
        
        assert values[2][0] == token.RPAR
        assert values[2][1] == ")"
        return node
    elif key == symbol.fpdef:
        raise NotImplementedError(values)
    elif key == symbol.fplist:
        raise NotImplementedError("fplist")
    elif key == symbol.stmt:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.simple_stmt:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.small_stmt:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.expr_stmt:
        if len(values) > 1:
            if values[1][0] == token.EQUAL:
                node = ast.Assign()

                if len(values[0]) > 2: # TODO
                    targets = ast.Tuple()
                    targets.ctx = ast.Store()
                    targets.elts = _parse(values[0], ctx=targets.ctx)
                else:
                    targets = _parse(values[0], ctx=ast.Store())
                    
                node.targets = [targets] # TODO why is this an array but value is not?
                
                if len(values[2]) > 2:
                    value = ast.Tuple()
                    value.ctx = ast.Load()
                    value.elts = _parse(values[2], ctx=value.ctx)
                else:
                    value = _parse(values[2], ctx=ast.Load())
                
                node.value = value
                
                return node
            else:
                raise NotImplementedError("expr_stmt -> augassign")
        elif len(values) == 1:
            result = _parse(values[0], ctx)
            
            # if the return value of an expression isn't used or stored, it is
            # wrapped into an Expr() node
            if isinstance(result, ast.Call): 
                node = ast.Expr()
                node.value = result
            else:
                node = result
            
            return node
        else:
            raise NotImplementedError("expr_stmt")
    elif key == symbol.augassign:
        raise NotImplementedError("augassign")
    elif key == symbol.print_stmt:
        node = ast.Print()
        node.dest = None # TODO
        node.values = [_parse(values[1], ctx)] # TODO
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
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.if_stmt:
        raise NotImplementedError("if_stmt")
    elif key == symbol.while_stmt:
        node = ast.While()

        assert len(values) == 4    
        assert values[0][0] == token.NAME
        assert values[0][1] == "while"
        
        node.test = _parse(values[1], ctx)
        
        assert values[2][0] == token.COLON
        assert values[2][1] == ":"
        
        node.body = _parse(values[3], ctx)
        node.orelse = [] # TODO

        return node
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
        if values[0][0] == token.NEWLINE:
            assert values[1][0] == token.INDENT
            assert values[1][1] == ''
            result = []
            
            for value in values[2:-1]:
                result.append(_parse(value, ctx))
            
            assert values[-1][0] == token.DEDENT
            assert values[-1][1] == ''
        else:
            raise NotImplementedError

        return result
    elif key == symbol.testlist_safe:
        raise NotImplementedError("testlist_safe")
    elif key == symbol.old_test:
        raise NotImplementedError("old_test")
    elif key == symbol.old_lambdef:
        raise NotImplementedError("old_lambdef")
    elif key == symbol.test:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.or_test:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.and_test:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.not_test:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.comparison:
        if len(values) == 3: # TODO only doing particular cases here
            node = ast.Compare()
            node.left = _parse(values[0], ctx)
            node.ops = _parse(values[1], ctx)
            node.comparators = [_parse(values[2], ctx)]
            return node
        elif len(values) == 1:
            return _parse(values[0], ctx)
        else:
            raise NotImplementedError
    elif key == symbol.comp_op:
        if values[0][0] == token.LESS:
            node = ast.Lt()
            return [node]
        else:
            raise NotImplementedError
    elif key == symbol.expr:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.xor_expr:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.and_expr:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.shift_expr:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.arith_expr:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.term:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.factor:
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.power:
        if len(values) > 1:
            if values[0][0] == symbol.atom and values[1][0] == symbol.trailer \
                and values[1][1][0] == token.LPAR \
                and values[1][3][0] == token.RPAR:

                node = ast.Call()
                node.func = _parse(values[0], ctx)
                node.args = _parse(values[1][2], ctx)
                node.keywords = [] # TODO
                node.starargs = None # TODO
                node.kwargs = None # TODO

                return node
            else:
                raise NotImplementedError
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.atom:
        if values[0][0] == token.NAME:
            node = ast.Name()
            node.id = values[0][1]
            node.ctx = ctx
            return node
        elif values[0][0] == token.NUMBER:
            node = ast.Num()
            node.n = int(values[0][1]) # TODO
            return node
        else:
            return _parse(values[0], ctx) # TODO
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
        if len(values) > 1:
            result = []
            for value in values:
                if value[0] != token.COMMA:
                    result.append(_parse(value, ctx))
            return result
        elif len(values) == 1:
            return _parse(values[0], ctx)
        else:
            raise NotImplementedError
    elif key == symbol.dictorsetmaker:
        raise NotImplementedError("dictorsetmaker")
    elif key == symbol.classdef:
        raise NotImplementedError("classdef")
    elif key == symbol.arglist:
        result = []

        for value in values:
            result.append(_parse(value, ctx))
            
        return result
    elif key == symbol.argument:
        # TODO
        return _parse(values[0], ctx)
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