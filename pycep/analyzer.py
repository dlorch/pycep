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
    >>> tree = pycep.analyzer.parse('print "Hello, world!"')
    >>> ast.dump(tree)
    "Module(body=[Print(dest=None, values=[Str(s='Hello, world!')], nl=True)])"

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
            Str -> "\\'Hello, world!\\'" [label = "s"];
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
        """single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE"""
        raise NotImplementedError("single_input")
    elif key == symbol.file_input:
        """file_input: (NEWLINE | stmt)* ENDMARKER"""
        node = ast.Module()
        node.body = []
        
        for value in values[:-2]:
            node.body.append(_parse(value, ctx))

        assert values[-2][0] == token.NEWLINE
        assert values[-1][0] == token.ENDMARKER
        
        return node
    elif key == symbol.eval_input:
        """eval_input: testlist NEWLINE* ENDMARKER"""
        raise NotImplementedError("eval_input")
    elif key == symbol.decorator:
        """decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE"""
        raise NotImplementedError("decorator")
    elif key == symbol.decorators:
        """decorators: decorator+"""
        raise NotImplementedError("decorators")
    elif key == symbol.decorated:
        """decorated: decorators (classdef | funcdef)"""
        raise NotImplementedError("decorated")
    elif key == symbol.funcdef:
        """funcdef: 'def' NAME parameters ':' suite"""
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
        """parameters: '(' [varargslist] ')'"""
        node = ast.arguments()
        
        assert values[0][0] == token.LPAR
        assert values[0][1] == "("

        if len(values) == 2:
            node.args = []
            node.vararg = None
            node.kwarg = None
            node.defaults = []
            assert values[1][0] == token.RPAR
            assert values[1][1] == ")"
        elif len(values) == 3:
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
        else:
            raise NotImplementedError
        
        return node
    elif key == symbol.varargslist:
        """varargslist: ((fpdef ['=' test] ',')*
                         ('*' NAME [',' '**' NAME] | '**' NAME) |
                         fpdef ['=' test] (',' fpdef ['=' test])* [','])"""
        raise NotImplementedError("varargslist")
    elif key == symbol.fpdef:
        """fpdef: NAME | '(' fplist ')'"""
        raise NotImplementedError("fpdef")
    elif key == symbol.fplist:
        """fplist: fpdef (',' fpdef)* [',']"""
        raise NotImplementedError("fplist")
    elif key == symbol.stmt:
        """stmt: simple_stmt | compound_stmt"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.simple_stmt:
        """simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.small_stmt:
        """small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
                        import_stmt | global_stmt | exec_stmt | assert_stmt)"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.expr_stmt:
        """expr_stmt: testlist (augassign (yield_expr|testlist) |
                                ('=' (yield_expr|testlist))*)"""
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
                node = ast.AugAssign()
                node.target = _parse(values[0], ast.Store())
                node.op = _parse(values[1], ast.Store())
                node.value = _parse(values[2], ast.Store())
                return node
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
        """augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
           '<<=' | '>>=' | '**=' | '//=')"""
        if values[0][0] == token.MINEQUAL:
            return ast.Sub()
        else:
            raise NotImplementedError("augassign: " + token.tok_name[values[0][0]])
    elif key == symbol.print_stmt:
        """print_stmt: 'print' ( [ test (',' test)* [','] ] |
                                 '>>' test [ (',' test)+ [','] ] )"""
        node = ast.Print()
        node.dest = None # TODO
        node.values = []
    
        # TODO ">>"
        for value in values[1:]:
            if value[0] != token.COMMA:
                node.values.append(_parse(value, ctx))

        node.nl = True # TODO
        return node
    elif key == symbol.del_stmt:
        """del_stmt: 'del' exprlist"""
        raise NotImplementedError("del_stmt")
    elif key == symbol.pass_stmt:
        """pass_stmt: 'pass'"""
        raise NotImplementedError("pass_stmt")
    elif key == symbol.flow_stmt:
        """flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt"""
        raise NotImplementedError("flow_stmt")
    elif key == symbol.break_stmt:
        """break_stmt: 'break'"""
        raise NotImplementedError("break_stmt")
    elif key == symbol.continue_stmt:
        """continue_stmt: 'continue'"""
        raise NotImplementedError("continue_stmt")
    elif key == symbol.return_stmt:
        """return_stmt: 'return' [testlist]"""
        raise NotImplementedError("return_stmt")
    elif key == symbol.yield_stmt:
        """yield_stmt: yield_expr"""
        raise NotImplementedError("yield_stmt")
    elif key == symbol.raise_stmt:
        """raise_stmt: 'raise' [test [',' test [',' test]]]"""
        raise NotImplementedError("raise_stmt")
    elif key == symbol.import_stmt:
        """import_stmt: import_name | import_from"""
        raise NotImplementedError("import_stmt")
    elif key == symbol.import_name:
        """import_name: 'import' dotted_as_names"""
        raise NotImplementedError("import_name")
    elif key == symbol.import_from:
        """import_from: ('from' ('.'* dotted_name | '.'+)
                         'import' ('*' | '(' import_as_names ')' | import_as_names))"""
        raise NotImplementedError("import_from")
    elif key == symbol.import_as_name:
        """import_as_name: NAME ['as' NAME]"""
        raise NotImplementedError("import_as_name")
    elif key == symbol.dotted_as_name:
        """dotted_as_name: dotted_name ['as' NAME]"""
        raise NotImplementedError("dotted_as_name")
    elif key == symbol.dotted_name:
        """dotted_name: NAME ('.' NAME)*"""
        raise NotImplementedError("dotted_name")
    elif key == symbol.global_stmt:
        """global_stmt: 'global' NAME (',' NAME)*"""
        raise NotImplementedError("global_stmt")
    elif key == symbol.exec_stmt:
        """exec_stmt: 'exec' expr ['in' test [',' test]]"""
        raise NotImplementedError("exec_stmt")
    elif key == symbol.assert_stmt:
        """assert_stmt: 'assert' test [',' test]"""
        raise NotImplementedError("assert_stmt")
    elif key == symbol.compound_stmt:
        """compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.if_stmt:
        """if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]"""
        raise NotImplementedError("if_stmt")
    elif key == symbol.while_stmt:
        """while_stmt: 'while' test ':' suite ['else' ':' suite]"""
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
        """for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]"""
        raise NotImplementedError("for_stmt")
    elif key == symbol.try_stmt:
        """try_stmt: ('try' ':' suite
                      ((except_clause ':' suite)+
                       ['else' ':' suite]
                       ['finally' ':' suite] |
                      'finally' ':' suite))"""
        raise NotImplementedError("try_stmt")
    elif key == symbol.with_stmt:
        """with_stmt: 'with' with_item (',' with_item)*  ':' suite"""
        raise NotImplementedError("with_stmt")
    elif key == symbol.with_item:
        """with_item: test ['as' expr]"""
        raise NotImplementedError("with_item")
    elif key == symbol.except_clause:
        """except_clause: 'except' [test [('as' | ',') test]]"""
        raise NotImplementedError("except_clause")
    elif key == symbol.suite:
        """suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT"""
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
        """testlist_safe: old_test [(',' old_test)+ [',']]"""
        raise NotImplementedError("testlist_safe")
    elif key == symbol.old_test:
        """old_test: or_test | old_lambdef"""
        raise NotImplementedError("old_test")
    elif key == symbol.old_lambdef:
        """old_lambdef: 'lambda' [varargslist] ':' old_test"""
        raise NotImplementedError("old_lambdef")
    elif key == symbol.test:
        """test: or_test ['if' or_test 'else' test] | lambdef"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.or_test:
        """or_test: and_test ('or' and_test)*"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.and_test:
        """and_test: not_test ('and' not_test)*"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.not_test:
        """not_test: 'not' not_test | comparison"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.comparison:
        """comparison: expr (comp_op expr)*"""
        if len(values) > 1: # TODO only doing particular cases here
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
        """comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'"""
        if values[0][0] == token.LESS:
            node = ast.Lt()
            return [node]
        elif values[0][0] == token.GREATER:
            node = ast.Gt()
            return [node]
        else:
            raise NotImplementedError(values)
    elif key == symbol.expr:
        """expr: xor_expr ('|' xor_expr)*"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.xor_expr:
        """xor_expr: and_expr ('^' and_expr)*"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.and_expr:
        """and_expr: shift_expr ('&' shift_expr)*"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.shift_expr:
        """shift_expr: arith_expr (('<<'|'>>') arith_expr)*"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.arith_expr:
        """arith_expr: term (('+'|'-') term)*"""
        if len(values) == 3:
            node = ast.BinOp()
            node.left = _parse(values[0], ctx)
            
            if values[1][0] == token.PLUS:
                node.op = ast.Add()
            elif values[1][0] == token.MINUS:
                node.op = ast.Sub()
            else:
                raise ValueError("Unexpected symbol/token %s" % values[1])
            
            node.right = _parse(values[2], ctx)
            return node
        elif len(values) == 1:
            return _parse(values[0], ctx)
        else:
            raise NotImplementedError
    elif key == symbol.term:
        """term: factor (('*'|'/'|'%'|'//') factor)*"""
        if len(values) == 3:
            node = ast.BinOp()
            node.left = _parse(values[0], ctx)
            
            if values[1][0] == token.PERCENT:
                node.op = ast.Mod()
            else:
                raise NotImplementedError("Token %s", token.tok_name[values[1][0]])

            #raise NotImplementedError(values[2])
            node.right = _parse(values[2], ctx)
            return node
        elif len(values) == 1:
            return _parse(values[0], ctx)
        else:
            raise NotImplementedError
    elif key == symbol.factor:
        """factor: ('+'|'-'|'~') factor | power"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.power:
        """power: atom trailer* ['**' factor]"""
        
        atom, rest = values[0], values[1:]

        node = _parse(atom, ctx)

        for rest in values[1:]:
            if rest[0] == symbol.trailer:
                trailer = _parse(rest, ctx)
                trailer.func = node
                node = trailer
            elif rest[0] == symbol.factor:
                raise NotImplementedError
        
        return node
    elif key == symbol.atom:
        """atom: ('(' [yield_expr|testlist_comp] ')' |
                  '[' [listmaker] ']' |
                  '{' [dictorsetmaker] '}' |
                  '`' testlist1 '`' |
                  NAME | NUMBER | STRING+)"""
        if values[0][0] == token.NAME:
            node = ast.Name()
            node.id = values[0][1]
            node.ctx = ctx
            return node
        elif values[0][0] == token.NUMBER:
            node = ast.Num()
            node.n = int(values[0][1]) # TODO
            return node
        elif values[0][0] == token.LPAR:
            node = ast.Tuple()
            node.elts = _parse(values[1], ctx)
            node.ctx = ctx
            # TODO other values?
            return node
        else:
            return _parse(values[0], ctx) # TODO
    elif key == symbol.listmaker:
        """listmaker: test ( list_for | (',' test)* [','] )"""
        raise NotImplementedError("listmaker")
    elif key == symbol.testlist_comp:
        """testlist_comp: test ( comp_for | (',' test)* [','] )"""
        result = []
        for value in values:
            if value[0] != token.COMMA:
                result.append(_parse(value, ctx))
        return result
    elif key == symbol.lambdef:
        """lambdef: 'lambda' [varargslist] ':' test"""
        raise NotImplementedError("lambdef")
    elif key == symbol.trailer:
        """trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME"""
        
        if values[0][0] == token.LPAR:
            node = ast.Call()
            
            # TODO
            if values[1][0] == symbol.arglist:
                node.args = _parse(values[1])
            else:
                node.args = []
        
            node.keywords = [] # TODO
            node.starargs = None # TODO
            node.kwargs = None # TODO
        else:
            raise NotImplementedError
        
        return node
    elif key == symbol.subscriptlist:
        """subscriptlist: subscript (',' subscript)* [',']"""
        raise NotImplementedError("subscriptlist")
    elif key == symbol.subscript:
        """subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]"""
        raise NotImplementedError("subscript")
    elif key == symbol.sliceop:
        """sliceop: ':' [test]"""
        raise NotImplementedError("sliceop")
    elif key == symbol.exprlist:
        """exprlist: expr (',' expr)* [',']"""
        raise NotImplementedError("exprlist")
    elif key == symbol.testlist:
        """testlist: test (',' test)* [',']"""
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
        """dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
                             (test (comp_for | (',' test)* [','])) )"""
        raise NotImplementedError("dictorsetmaker")
    elif key == symbol.classdef:
        """classdef: 'class' NAME ['(' [testlist] ')'] ':' suite"""
        raise NotImplementedError("classdef")
    elif key == symbol.arglist:
        """arglist: (argument ',')* (argument [',']
                                    |'*' test (',' argument)* [',' '**' test]
                                    |'**' test)"""
        result = []

        for value in values:
            result.append(_parse(value, ctx))
            
        return result
    elif key == symbol.argument:
        """argument: test [comp_for] | test '=' test"""
        # TODO
        return _parse(values[0], ctx)
    elif key == symbol.list_iter:
        """list_iter: list_for | list_if"""
        raise NotImplementedError("list_iter")
    elif key == symbol.list_for:
        """list_for: 'for' exprlist 'in' testlist_safe [list_iter]"""
        raise NotImplementedError("list_for")
    elif key == symbol.list_if:
        """list_if: 'if' old_test [list_iter]"""
        raise NotImplementedError("list_if")
    elif key == symbol.comp_iter:
        """comp_iter: comp_for | comp_if"""
        raise NotImplementedError("comp_iter")
    elif key == symbol.comp_for:
        """comp_for: 'for' exprlist 'in' or_test [comp_iter]"""
        raise NotImplementedError("comp_for")
    elif key == symbol.testlist1:
        """testlist1: test (',' test)*"""
        raise NotImplementedError("testlist1")
    elif key == symbol.encoding_decl:
        """encoding_decl: NAME"""
        raise NotImplementedError("encoding_decl")
    elif key == symbol.yield_expr:
        """yield_expr: 'yield' [testlist]"""
        raise NotImplementedError("yield_expr")
    elif key == token.STRING:
        node = ast.Str(ast.literal_eval(values[0])) # TODO
        return node
    else:
        raise ValueError("Unexpected symbol/token `%d'" % key)