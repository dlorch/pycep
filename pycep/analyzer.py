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
    tree = Analyzer().visit(parse_tree.totuple())
    ast.fix_missing_locations(tree) # TODO

    return tree

class Analyzer():
    """Convert a parse tree into an abstract syntax tree.
    
    See also:
        * Visitor Design Pattern https://sourcemaking.com/design_patterns/visitor
    """
    
    def visit(self, tree, ctx=ast.Load()):
        key, values = tree[0], tree[1:]

        if key in symbol.sym_name:
            method = "visit_" + symbol.sym_name[key]
        elif key in token.tok_name:
            method = "visit_" + token.tok_name[key]
        else:
            raise ValueError("Unexpected symbol/token `%d'" % key)

        visitor = getattr(self, method)
            
        return visitor(values, ctx)

    def visit_single_input(self, values, ctx):
        """single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE"""
        raise NotImplementedError("single_input")
        
    def visit_file_input(self, values, ctx):
        """file_input: (NEWLINE | stmt)* ENDMARKER"""
        node = ast.Module()
        node.body = []
        
        for value in values[:-2]:
            node.body.append(self.visit(value, ctx))

        assert values[-2][0] == token.NEWLINE
        assert values[-1][0] == token.ENDMARKER
        
        return node
        
    def visit_eval_input(self, values, ctx):
        """eval_input: testlist NEWLINE* ENDMARKER"""
        raise NotImplementedError("eval_input")
        
    def visit_decorator(self, values, ctx):
        """decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE"""
        raise NotImplementedError("decorator")

    def visit_decorators(self, values, ctx):
        """decorators: decorator+"""
        raise NotImplementedError("decorators")

    def visit_decorated(self, values, ctx):
        """decorated: decorators (classdef | funcdef)"""
        raise NotImplementedError("decorated")
    
    def visit_funcdef(self, values, ctx):
        """funcdef: 'def' NAME parameters ':' suite"""
        node = ast.FunctionDef()
        assert len(values) == 5
        assert values[0][0] == token.NAME
        assert values[0][1] == "def"
        assert values[1][0] == token.NAME
        node.name = values[1][1]
        node.args = self.visit(values[2], ast.Param())
        assert values[3][0] == token.COLON
        assert values[3][1] == ":"
        node.body = self.visit(values[4], ctx)
        node.decorator_list = [] # TODO
        return node
    
    def visit_parameters(self, values, ctx):
        """parameters: '(' [varargslist] ')'"""
        
        if len(values) == 2:
            node = ast.arguments()
            node.args = []
            node.vararg = None
            node.kwarg = None
            node.defaults = []
        else:
            varargslist = values[1]
            node = self.visit(varargslist, ctx)
            
        return node
        
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
            
            varargslist = values[1][1:]
            
            raise NotImplementedError(varargslist)
            
            for vararg in varargslist:
                if vararg[0] == symbol.fpdef:
                    if vararg[1][0] == token.NAME:
                        n = ast.Name()
                        n.id = vararg[1][1]
                        n.ctx = ast.Param()
                        args.append(n)
                    else:
                        raise NotImplementedError
                elif vararg[0] == token.COMMA:
                    pass
                elif vararg[0] == token.EQUAL:
                    pass
                else:
                    raise NotImplementedError(vararg)
            
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
    
    def visit_varargslist(self, values, ctx):
        """varargslist: ((fpdef ['=' test] ',')*
                         ('*' NAME [',' '**' NAME] | '**' NAME) |
                         fpdef ['=' test] (',' fpdef ['=' test])* [','])"""
        
        node = ast.arguments()
        node.args = []
        node.vararg = None
        node.kwarg = None
        node.defaults = []
        
        idx = 0
        
        while idx < len(values):
            if values[idx][0] == token.COMMA:
                idx += 1
            elif values[idx][0] == token.EQUAL:
                test = self.visit(values[idx+1], ctx)
                node.defaults.append(test)
                idx += 2
            elif values[idx][0] == token.STAR:
                raise NotImplementedError
            elif values[idx][0] == token.DOUBLESTAR:
                raise NotImplementedError
            else:
                fpdef = self.visit(values[idx], ctx)
                node.args.append(fpdef)
                idx += 1

        return node
    
    def visit_fpdef(self, values, ctx):
        """fpdef: NAME | '(' fplist ')'"""
        if values[0][0] == token.NAME:
            node = ast.Name()
            node.id = values[0][1]
            node.ctx = ctx
            return node
        else:
            raise NotImplementedError
    
    def visit_fplist(self, values, ctx):
        """fplist: fpdef (',' fpdef)* [',']"""
        raise NotImplementedError("fplist")
    
    def visit_stmt(self, values, ctx):
        """stmt: simple_stmt | compound_stmt"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_simple_stmt(self, values, ctx):
        """simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_small_stmt(self, values, ctx):
        """small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
                        import_stmt | global_stmt | exec_stmt | assert_stmt)"""
        # TODO
        return self.visit(values[0], ctx)
        
    def visit_expr_stmt(self, values, ctx):
        """expr_stmt: testlist (augassign (yield_expr|testlist) |
                                ('=' (yield_expr|testlist))*)"""
        if len(values) > 1:
            if values[1][0] == token.EQUAL:
                node = ast.Assign()

                if len(values[0]) > 2: # TODO
                    targets = ast.Tuple()
                    targets.ctx = ast.Store()
                    targets.elts = self.visit(values[0], ctx=targets.ctx)
                else:
                    targets = self.visit(values[0], ctx=ast.Store())
                    
                node.targets = [targets] # TODO why is this an array but value is not?
                
                if len(values[2]) > 2:
                    value = ast.Tuple()
                    value.ctx = ast.Load()
                    value.elts = self.visit(values[2], ctx=value.ctx)
                else:
                    value = self.visit(values[2], ctx=ast.Load())
                
                node.value = value
                
                return node
            else:
                node = ast.AugAssign()
                node.target = self.visit(values[0], ast.Store())
                node.op = self.visit(values[1], ast.Store())
                node.value = self.visit(values[2], ast.Load())
                return node
        elif len(values) == 1:
            result = self.visit(values[0], ctx)
            
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
    
    def visit_augassign(self, values, ctx):
        """augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
           '<<=' | '>>=' | '**=' | '//=')"""
        if values[0][0] == token.PLUSEQUAL:
            return ast.Add()
        elif values[0][0] == token.MINEQUAL:
            return ast.Sub()
        else:
            raise NotImplementedError("augassign: " + token.tok_name[values[0][0]])

    def visit_print_stmt(self, values, ctx):
        """print_stmt: 'print' ( [ test (',' test)* [','] ] |
                                 '>>' test [ (',' test)+ [','] ] )"""
        node = ast.Print()
        node.dest = None # TODO
        node.values = []
    
        # TODO ">>"
        for value in values[1:]:
            if value[0] != token.COMMA:
                node.values.append(self.visit(value, ctx))

        node.nl = True # TODO
        return node
    
    def visit_del_stmt(self, values, ctx):
        """del_stmt: 'del' exprlist"""
        raise NotImplementedError("del_stmt")
        
    def visit_pass_stmt(self, values, ctx):
        """pass_stmt: 'pass'"""
        raise NotImplementedError("pass_stmt")

    def visit_flow_stmt(self, values, ctx):
        """flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt"""
        return self.visit(values[0], ctx)

    def visit_break_stmt(self, values, ctx):
        """break_stmt: 'break'"""
        raise NotImplementedError("break_stmt")

    def visit_continue_stmt(self, values, ctx):
        """continue_stmt: 'continue'"""
        raise NotImplementedError("continue_stmt")

    def visit_return_stmt(self, values, ctx):
        """return_stmt: 'return' [testlist]"""
        node = ast.Return()
        
        if len(values) == 2:
            node.value = self.visit(values[1], ctx)
        
        return node

    def visit_yield_stmt(self, values, ctx):
        """yield_stmt: yield_expr"""
        raise NotImplementedError("yield_stmt")

    def visit_raise_stmt(self, values, ctx):
        """raise_stmt: 'raise' [test [',' test [',' test]]]"""
        raise NotImplementedError("raise_stmt")

    def visit_import_stmt(self, values, ctx):
        """import_stmt: import_name | import_from"""
        return self.visit(values[0])

    def visit_import_name(self, values, ctx):
        """import_name: 'import' dotted_as_names"""
        node = ast.Import()
        node.names = self.visit(values[1])

        return node

    def visit_import_from(self, values, ctx):
        """import_from: ('from' ('.'* dotted_name | '.'+)
                         'import' ('*' | '(' import_as_names ')' | import_as_names))"""
        raise NotImplementedError("import_from")

    def visit_import_as_name(self, values, ctx):
        """import_as_name: NAME ['as' NAME]"""
        raise NotImplementedError("import_as_name")

    def visit_dotted_as_name(self, values, ctx):
        """dotted_as_name: dotted_name ['as' NAME]"""
        if len(values) > 1:
            raise NotImplementedError("dotted_as_name with multiple arguments not supported")
        
        node = ast.alias()
        node.name = self.visit(values[0])
        node.asname = None
        
        return node

    def visit_import_as_names(self, values, ctx):
        """import_as_names: import_as_name (',' import_as_name)* [',']"""
        raise NotImplementedError("import_as_names")
    
    def visit_dotted_as_names(self, values, ctx):
        """dotted_as_names: dotted_as_name (',' dotted_as_name)*"""
        if len(values) > 1:
            raise NotImplementedError("dotted_as_names with multiple arguments not supported")
        return [self.visit(values[0])]

    def visit_dotted_name(self, values, ctx):
        """dotted_name: NAME ('.' NAME)*"""
        if len(values) > 1:
            raise NotImplementedError("dotted_name with multiple arguments not supported")
        return values[0][1]

    def visit_global_stmt(self, values, ctx):
        """global_stmt: 'global' NAME (',' NAME)*"""
        raise NotImplementedError("global_stmt")

    def visit_exec_stmt(self, values, ctx):
        """exec_stmt: 'exec' expr ['in' test [',' test]]"""
        raise NotImplementedError("exec_stmt")

    def visit_assert_stmt(self, values, ctx):
        """assert_stmt: 'assert' test [',' test]"""
        raise NotImplementedError("assert_stmt")

    def visit_compound_stmt(self, values, ctx):
        """compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated"""
        # TODO
        return self.visit(values[0], ctx)
    
    def visit_if_stmt(self, values, ctx):
        """if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]"""
        raise NotImplementedError("if_stmt")

    def visit_while_stmt(self, values, ctx):
        """while_stmt: 'while' test ':' suite ['else' ':' suite]"""
        node = ast.While()

        assert len(values) == 4    
        assert values[0][0] == token.NAME
        assert values[0][1] == "while"
        
        node.test = self.visit(values[1], ctx)
        
        assert values[2][0] == token.COLON
        assert values[2][1] == ":"
        
        node.body = self.visit(values[3], ctx)
        node.orelse = [] # TODO

        return node

    def visit_for_stmt(self, values, ctx):
        """for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]"""
        raise NotImplementedError("for_stmt")

    def visit_try_stmt(self, values, ctx):
        """try_stmt: ('try' ':' suite
                      ((except_clause ':' suite)+
                       ['else' ':' suite]
                       ['finally' ':' suite] |
                      'finally' ':' suite))"""
        # TODO
        node = ast.TryExcept()
        node.body = self.visit(values[2])
        
        handler = self.visit(values[3])
        handler.body = self.visit(values[5])
        
        node.handlers = [handler]
        node.orelse = []
        
        return node

    def visit_with_stmt(self, values, ctx):
        """with_stmt: 'with' with_item (',' with_item)*  ':' suite"""
        raise NotImplementedError("with_stmt")

    def visit_with_item(self, values, ctx):
        """with_item: test ['as' expr]"""
        raise NotImplementedError("with_item")

    def visit_except_clause(self, values, ctx):
        """except_clause: 'except' [test [('as' | ',') test]]"""
        if len(values) != 2:
            raise NotImplementedError("except_clause supported only with 2 arguments")
        
        node = ast.ExceptHandler()
        node.type = self.visit(values[1])
        node.name = None

        return node
    
    def visit_suite(self, values, ctx):
        """suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT"""
        if values[0][0] == token.NEWLINE:
            assert values[1][0] == token.INDENT
            assert values[1][1] == ''
            result = []
            
            for value in values[2:-1]:
                result.append(self.visit(value, ctx))
            
            assert values[-1][0] == token.DEDENT
            assert values[-1][1] == ''
        else:
            raise NotImplementedError

        return result

    def visit_testlist_safe(self, values, ctx):
        """testlist_safe: old_test [(',' old_test)+ [',']]"""
        raise NotImplementedError("testlist_safe")

    def visit_old_test(self, values, ctx):
        """old_test: or_test | old_lambdef"""
        raise NotImplementedError("old_test")

    def visit_old_lambdef(self, values, ctx):
        """old_lambdef: 'lambda' [varargslist] ':' old_test"""
        raise NotImplementedError("old_lambdef")

    def visit_test(self, values, ctx):
        """test: or_test ['if' or_test 'else' test] | lambdef"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_or_test(self, values, ctx):
        """or_test: and_test ('or' and_test)*"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_and_test(self, values, ctx):
        """and_test: not_test ('and' not_test)*"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_not_test(self, values, ctx):
        """not_test: 'not' not_test | comparison"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_comparison(self, values, ctx):
        """comparison: expr (comp_op expr)*"""
        if len(values) > 1: # TODO only doing particular cases here
            node = ast.Compare()
            node.left = self.visit(values[0], ctx)
            node.ops = self.visit(values[1], ctx)
            node.comparators = [self.visit(values[2], ctx)]
            return node
        elif len(values) == 1:
            return self.visit(values[0], ctx)
        else:
            raise NotImplementedError

    def visit_comp_op(self, values, ctx):
        """comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'"""
        if values[0][0] == token.LESS:
            node = ast.Lt()
            return [node]
        elif values[0][0] == token.GREATER:
            node = ast.Gt()
            return [node]
        else:
            raise NotImplementedError(values)

    def visit_expr(self, values, ctx):
        """expr: xor_expr ('|' xor_expr)*"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_xor_expr(self, values, ctx):
        """xor_expr: and_expr ('^' and_expr)*"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_and_expr(self, values, ctx):
        """and_expr: shift_expr ('&' shift_expr)*"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_shift_expr(self, values, ctx):
        """shift_expr: arith_expr (('<<'|'>>') arith_expr)*"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_arith_expr(self, values, ctx):
        """arith_expr: term (('+'|'-') term)*"""
        if len(values) == 3:
            node = ast.BinOp()
            node.left = self.visit(values[0], ctx)
            
            if values[1][0] == token.PLUS:
                node.op = ast.Add()
            elif values[1][0] == token.MINUS:
                node.op = ast.Sub()
            else:
                raise ValueError("Unexpected symbol/token %s" % values[1])
            
            node.right = self.visit(values[2], ctx)
            return node
        elif len(values) == 1:
            return self.visit(values[0], ctx)
        else:
            raise NotImplementedError

    def visit_term(self, values, ctx):
        """term: factor (('*'|'/'|'%'|'//') factor)*"""
        if len(values) == 3:
            node = ast.BinOp()
            node.left = self.visit(values[0], ctx)
            
            if values[1][0] == token.PERCENT:
                node.op = ast.Mod()
            else:
                raise NotImplementedError("Token %s", token.tok_name[values[1][0]])

            #raise NotImplementedError(values[2])
            node.right = self.visit(values[2], ctx)
            return node
        elif len(values) == 1:
            return self.visit(values[0], ctx)
        else:
            raise NotImplementedError

    def visit_factor(self, values, ctx):
        """factor: ('+'|'-'|'~') factor | power"""
        # TODO
        return self.visit(values[0], ctx)

    def visit_power(self, values, ctx):
        """power: atom trailer* ['**' factor]"""
        
        node = self.visit(values[0], ctx)
        
        for rest in values[1:]:
            if rest[0] == symbol.trailer:
                trailer = self.visit(rest, ctx)

                if isinstance(trailer, ast.Attribute):
                    node.ctx = ast.Load()
                    trailer.value = node
                elif isinstance(trailer, ast.Call):
                    trailer.func = node
                elif isinstance(trailer, ast.Subscript):
                    trailer.value = node
                else:
                    raise NotImplementedError
    
                node = trailer
            elif rest[0] == symbol.factor:
                raise NotImplementedError
        
        return node

    def visit_atom(self, values, ctx):
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
            node.elts = self.visit(values[1], ctx)
            node.ctx = ctx
            # TODO other values?
            return node
        else:
            return self.visit(values[0], ctx) # TODO

    def visit_listmaker(self, values, ctx):
        """listmaker: test ( list_for | (',' test)* [','] )"""
        raise NotImplementedError("listmaker")

    def visit_testlist_comp(self, values, ctx):
        """testlist_comp: test ( comp_for | (',' test)* [','] )"""
        result = []
        for value in values:
            if value[0] != token.COMMA:
                result.append(self.visit(value, ctx))
        return result

    def visit_lambdef(self, values, ctx):
        """lambdef: 'lambda' [varargslist] ':' test"""
        raise NotImplementedError("lambdef")

    def visit_trailer(self, values, ctx):
        """trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME"""
        
        if values[0][0] == token.LPAR:
            node = ast.Call()
            
            # TODO
            if values[1][0] == symbol.arglist:
                node.args = self.visit(values[1], ctx)
            else:
                node.args = []
        
            node.keywords = [] # TODO
            node.starargs = None # TODO
            node.kwargs = None # TODO
        elif values[0][0] == token.LSQB:
            node = ast.Subscript()
            node.slice = self.visit(values[1], ctx)
            node.ctx = ctx
        elif values[0][0] == token.DOT:
            node = ast.Attribute()
            node.attr = values[1][1]
            node.ctx = ctx
        else:
            raise ValueError
        
        return node

    def visit_subscriptlist(self, values, ctx):
        """subscriptlist: subscript (',' subscript)* [',']"""
        if len(values) == 1:
            return self.visit(values[0], ctx)
        else:
            raise NotImplementedError("subscriptlist with len(values) > 1 not supported")

    def visit_subscript(self, values, ctx):
        """subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]"""
        if len(values) > 1:
            if values[0][0] == symbol.test:
                test = self.visit(values[0])
                # TODO
                
                node = ast.Slice()
                node.lower = test
                node.upper = None
                node.step = None

                return node
            else:
                raise NotImplementedError("Not implemented: ", values[0][0])
        else:
            raise NotImplementedError("subscript with len(values) <= 1 not supported")
    
    def visit_sliceop(self, values, ctx):
        """sliceop: ':' [test]"""
        raise NotImplementedError("sliceop")

    def visit_exprlist(self, values, ctx):
        """exprlist: expr (',' expr)* [',']"""
        if len(values) > 1:
            raise NotImplementedError("exprlist with multiple arguments not supported")
        return [self.visit(values[0], ctx)]

    def visit_testlist(self, values, ctx):
        """testlist: test (',' test)* [',']"""
        if len(values) > 1:
            result = []
            for value in values:
                if value[0] != token.COMMA:
                    test = self.visit(value, ctx)
                    result.append(test)
            return result
        else:
            return self.visit(values[0], ctx)

    def visit_dictorsetmaker(self, values, ctx):
        """dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
                             (test (comp_for | (',' test)* [','])) )"""
        raise NotImplementedError("dictorsetmaker")

    def visit_classdef(self, values, ctx):
        """classdef: 'class' NAME ['(' [testlist] ')'] ':' suite"""
        
        name = values[1]

        node = ast.ClassDef()
        node.name = name[1]
        
        if values[2][0] == token.LPAR:
            if values[3][0] == token.RPAR:
                suite = values[5]
            else:
                testlist = values[3]
                node.bases = [self.visit(testlist, ctx)] # TODO check list?
                suite = values[6]
        else:
            suite = values[3]
            
        node.body = self.visit(suite, ctx)
        node.decorator_list = [] # TODO
        
        return node

    def visit_arglist(self, values, ctx):
        """arglist: (argument ',')* (argument [',']
                                    |'*' test (',' argument)* [',' '**' test]
                                    |'**' test)"""
        result = []

        for value in values:
            result.append(self.visit(value, ctx))
            
        return result

    def visit_argument(self, values, ctx):
        """argument: test [comp_for] | test '=' test"""
        if len(values) == 2:
            test = self.visit(values[0], ctx)
            comp_for = self.visit(values[1], ctx)

            # TODO
            node = ast.GeneratorExp()
            node.elt = test
            node.generators = [comp_for]

            return node
        elif len(values) == 1:
            return self.visit(values[0], ctx)
        else:
            raise NotImplementedError("symbol.argument with len(values) > 2 not supported")

    def visit_list_iter(self, values, ctx):
        """list_iter: list_for | list_if"""
        raise NotImplementedError("list_iter")

    def visit_list_for(self, values, ctx):
        """list_for: 'for' exprlist 'in' testlist_safe [list_iter]"""
        raise NotImplementedError("list_for")

    def visit_list_if(self, values, ctx):
        """list_if: 'if' old_test [list_iter]"""
        raise NotImplementedError("list_if")

    def visit_comp_iter(self, values, ctx):
        """comp_iter: comp_for | comp_if"""
        raise NotImplementedError("comp_iter")

    def visit_comp_for(self, values, ctx):
        """comp_for: 'for' exprlist 'in' or_test [comp_iter]"""
        if len(values) > 4:
            raise NotImplementedError("comp_for with more than 4 arguments not supported")

        node = ast.comprehension()
        node.target = self.visit(values[1], ast.Store())[0] # TODO
        node.iter = self.visit(values[3], ctx)
        node.ifs = []
        
        return node

    def visit_testlist1(self, values, ctx):
        """testlist1: test (',' test)*"""
        raise NotImplementedError("testlist1")

    def visit_encoding_decl(self, values, ctx):
        """encoding_decl: NAME"""
        raise NotImplementedError("encoding_decl")
        
    def visit_yield_expr(self, values, ctx):
        """yield_expr: 'yield' [testlist]"""
        raise NotImplementedError("yield_expr")

    def visit_STRING(self, values, ctx):
        node = ast.Str(ast.literal_eval(values[0])) # TODO
        return node
