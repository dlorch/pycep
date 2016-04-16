# -*- coding: utf-8 -*-

from __future__ import absolute_import
import pycep.tokenizer
import parser
import token
import tokenize
import symbol
from StringIO import StringIO

def suite(source, totuple=False):
    """The parser takes a string containing the source code as an input and
    returns a parse tree.

    >>> import pycep.parser
    >>> st = pycep.parser.suite('print "Hello, world!"')
    >>> st.totuple()
    (257, (267, (268, (269, (272, (1, 'print'), (304, (305, (306, (307, (308, (310, (311, (312, (313, (314, (315, (316, (317, (318, (3, '"Hello, world!"'))))))))))))))))), (4, ''))), (4, ''), (0, ''))

    Args:
        source (string): Source code
        totuple (boolean): (for testing) Return internal parser data structure, don't convert to ``parser.st`` object
        
    Returns:
        parser.st: Parse Tree

    Raises:
        SyntaxError: Syntax error in the source code

    Parse Tree of Hello World Example:

    .. graphviz::
        :alt: Parse Tree of Hello World Example

        digraph foo {
            bgcolor = "transparent";
            node [shape=plaintext];
            file_input -> stmt;
            file_input -> NEWLINE;
            file_input -> ENDMARKER;
            stmt -> simple_stmt;
            simple_stmt -> small_stmt;
            simple_stmt -> "NEWLINE ";
            small_stmt -> print_stmt;
            print_stmt -> "NAME \\"print\\"";
            print_stmt -> test;
            test -> or_test;
            or_test -> and_test;
            and_test -> not_test;
            not_test -> comparison;
            comparison -> expr;
            expr -> xor_expr;
            xor_expr -> and_expr;
            and_expr -> shift_expr;
            shift_expr -> arith_expr;
            arith_expr -> term;
            term -> factor;
            factor -> power;
            power -> atom;
            atom -> "STRING \\"Hello, world!\\""
        }


    See also:
        * Python Language Reference: https://docs.python.org/2/reference/grammar.html
        * Non-Terminal Symbols: https://hg.python.org/cpython/file/2.7/Lib/symbol.py
        * Leaf Nodes: https://docs.python.org/2/library/token.html
    """

    tokens = TokenIterator(pycep.tokenizer.generate_tokens(StringIO(source).readline))
    result = _file_input(tokens)

    if totuple:
        # recursively convert list-of-lists to tuples-of-tuples
        def listit(t):
            return tuple(map(listit, t)) if isinstance(t, (list, tuple)) else t

        return listit(result)
    else:
        return parser.sequence2st(result)

def syntax_error(reason, token, filename="<string>"):
    return SyntaxError(reason, (filename, token[2][0], token[2][1], token[4]))

def _single_input(tokens):
    """Parse a single input.

    ::

        single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    """
    raise NotImplementedError

def _file_input(tokens):
    """Parse a module or sequence of command read from an input file.

    ::
    
        file_input: (NEWLINE | stmt)* ENDMARKER
    """
    result = [symbol.file_input]
    
    try:
        while not tokens.peek()[0] == token.ENDMARKER:
            if tokens.peek()[0] == token.NEWLINE:
                result.append((tokens.peek()[0], ''))
                tokens.next()
            else:
                result.append(_stmt(tokens))
    except StopIteration:
        pass # raise "Expecting ENDMARKER" in next block

    # No trailing NEWLINE defined in grammar, but Python's parser always
    # appends it, thus imitate this behavior 
    result.append((token.NEWLINE, ''))

    if tokens.next()[0] != token.ENDMARKER:
        raise syntax_error("Expecting ENDMARKER", tokens.peek())

    result.append((token.ENDMARKER, ''))

    return result

def _eval_input(tokens):
    """Parse an evaluation input.

    ::

        eval_input: testlist NEWLINE* ENDMARKER
    """
    raise NotImplementedError

def _decorator(tokens):
    """Parse a decorator.

    ::

        decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
    """
    result = [symbol.decorator]
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "@"):
        raise SyntaxError("Expecting '@'")
    result.append((token.AT, "@"))
    tokens.next()
    
    result.append(_dotted_name(tokens))
        
    # [ '(' [arglist] ')' ]
    def arglist(tokens):
        result = []
        
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "("):
            raise SyntaxError("Expecting '('")
        result.append((token.LPAR, "("))
        tokens.next()
        
        option = matcher(tokens, [_arglist], optional=True)
        if option:
            result.append(option)
        
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ")"):
            raise SyntaxError("Expecting ')'")
        result.append((token.RPAR, ")"))
        tokens.next()
        
        return result
    
    option = matcher(tokens, [arglist], optional=True)
    if option:
        result = result + option
    
    if tokens.peek()[0] != token.NEWLINE:
        raise SyntaxError
    result.append((token.NEWLINE, ''))
    tokens.next()
    
    return result

def _decorators(tokens):
    """Parse a list of decorators.

    ::

        decorators: decorator+
    """
    result = [symbol.decorators]
    
    result = result + matcher(tokens, [[_decorator]], repeat=True)
    
    return result

def _decorated(tokens):
    """Parse a decorated statement.

    ::

        decorated: decorators (classdef | funcdef)
    """
    result = [symbol.decorated]
    
    result.append(_decorators(tokens))
    
    result.append(matcher(tokens, [_classdef, _funcdef]))
    
    return result

def _funcdef(tokens):
    """Parse a function definition.

    ::

        funcdef: 'def' NAME parameters ':' suite
    """
    result = [symbol.funcdef]

    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "def"):
        raise syntax_error("Expecting 'def'", tokens.peek())
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    if not (tokens.peek()[0] == token.NAME):
        raise syntax_error("Expecting function name", tokens.peek())
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()

    result.append(_parameters(tokens)) 

    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ':'):
        raise syntax_error("Expecting ':'", tokens.peek())
    result.append((token.COLON, ':'))
    tokens.next()
    
    result.append(_suite(tokens))
    
    return result

def _parameters(tokens):
    """Parse a parameter list.

    ::

        parameters: '(' [varargslist] ')'
    """
    result = [symbol.parameters]

    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == '('):
        raise syntax_error("Expecting '('", tokens.peek())
    result.append((token.LPAR, '('))
    tokens.next()

    varargslist = matcher(tokens, [_varargslist], optional=True)
    if varargslist:
        result.append(varargslist)
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ')'):
        raise syntax_error("Expecting ')'", tokens.peek())
    result.append((token.RPAR, ')'))
    tokens.next()

    return result

def _varargslist(tokens):
    """Parse a variable argument list.

    ::

        varargslist: ((fpdef ['=' test] ',')*
                      ('*' NAME [',' '**' NAME] | '**' NAME) |
                      fpdef ['=' test] (',' fpdef ['=' test])* [','])
    """
    result = [symbol.varargslist]
    
    # TODO this grammar is not left-factored and needs to be rewritten
    
    # fpdef ['=' test]
    def option2a(tokens):
        result = []
        result.append(_fpdef(tokens))

        if tokens.peek()[0] == token.OP and tokens.peek()[1] == "=":
            result.append((token.EQUAL, "="))
            tokens.next()
            result.append(_test(tokens))

        return result

    # ',' fpdef ['=' test]
    def option2b(tokens):
        result = []
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ","):
            raise SyntaxError
        result.append((token.COMMA, ","))
        tokens.next()
        
        result = result + option2a(tokens)
        
        return result

    # fpdef ['=' test] (',' fpdef ['=' test])* [',']
    def option2(tokens):
        result = []
        result = result + option2a(tokens)
        result = result + matcher(tokens, [option2b], repeat=True, optional=True)

        if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
            result.append((token.OP, ","))
            tokens.next()

        return result

    # TODO option1
    result = result + option2(tokens)

    return result

def _fpdef(tokens):
    """Parse function parameter definition.

    ::

        fpdef: NAME | '(' fplist ')'
    """
    result = [symbol.fpdef]

    if tokens.peek()[0] == token.NAME:
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "(":
        result.append((token.OP, "("))
        tokens.next()
        result.append(_fplist(tokens))
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ")"):
            raise SyntaxError
    else:
        raise SyntaxError

    return result

def _fplist(tokens):
    """Parse a function parameter list

    ::

        fplist: fpdef (',' fpdef)* [',']
    """
    raise NotImplementedError

def _stmt(tokens):
    """Parse a statement.

    ::

        stmt: simple_stmt | compound_stmt
    """
    result = [symbol.stmt]

    try:
        result.append(matcher(tokens, [_simple_stmt, _compound_stmt]))
    except SyntaxError:
        raise syntax_error("Expecting simple_stmt | compound_stmt", tokens.peek())

    return result

def _simple_stmt(tokens):
    """Parse a simple statement.

    ::

        simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
    """
    result = [symbol.simple_stmt]

    result.append(_small_stmt(tokens))

    # TODO this is incorrect, needs to be rewritten with matcher
    while tokens.peek()[0] == token.OP and tokens.peek()[1] == ";":
        result.append((token.SEMI, ";"))
        tokens.next()
        result.append(_small_stmt(tokens))
        
    if tokens.peek()[0] == token.OP and tokens.peek()[1] == ";":
        result.append((token.SEMI, ";"))
        tokens.next()

    # trailing NEWLINE is mandatory according to grammar, but in Python's parser
    # it is optional, thus imitate this behavior
    if tokens.peek()[0] == token.NEWLINE:
        tokens.next()
    
    result.append((token.NEWLINE, ''))

    return result

def _small_stmt(tokens):
    """Parse a small statement.

    ::

        small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
                     import_stmt | global_stmt | exec_stmt | assert_stmt)
    """
    result = [symbol.small_stmt]

    try:
        result.append(matcher(tokens, [_expr_stmt, _print_stmt,
            _flow_stmt, _import_stmt])) # TODO
    except SyntaxError:
        raise syntax_error("Expecting (expr_stmt | print_stmt  | del_stmt | "
            "pass_stmt | flow_stmt | import_stmt | global_stmt | exec_stmt | "
            "assert_stmt", tokens.peek())
            
    return result

def _expr_stmt(tokens):
    """Parse an expr stmt.

    ::

        expr_stmt: testlist (augassign (yield_expr|testlist) |
                             ('=' (yield_expr|testlist))*)
    """
    result = [symbol.expr_stmt]
    
    result.append(_testlist(tokens))

    def yield_expr_or_testlist(tokens):
        return matcher(tokens, [_yield_expr, _testlist])

    def option1(tokens):
        result = []
        result.append(_augassign(tokens))
        result.append(yield_expr_or_testlist(tokens))
        return result
        
    def option2(tokens):
        result = []
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "="):
            raise SyntaxError
        result.append((token.EQUAL, "="))
        tokens.next()
        result.append(yield_expr_or_testlist(tokens))
        return result

    def option2repeat(tokens):
        return matcher(tokens, [option2], repeat=True)

    match = matcher(tokens, [option1, option2repeat], optional=True)
    
    if match:
        result = result + match

    return result

def _augassign(tokens):
    """Parse an augmented assign statement.

    ::

        augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
        '<<=' | '>>=' | '**=' | '//=')
    """
    result = [symbol.augassign]

    if tokens.peek()[0] == token.OP:
        if tokens.peek()[1] == "+=":
            result.append((token.PLUSEQUAL, "+="))
            tokens.next()
        elif tokens.peek()[1] == "-=":
            result.append((token.MINEQUAL, "-="))
            tokens.next()
        elif tokens.peek()[1] == "*=":
            result.append((token.STAREQUAL, "*="))
            tokens.next()
        elif tokens.peek()[1] == "/=":
            result.append((token.SLASHEQUAL, "/="))
            tokens.next()
        elif tokens.peek()[1] == "%=":
            result.append((token.PERCENTEQUAL, "%="))
            tokens.next()
        elif tokens.peek()[1] == "&=":
            result.append((token.AMPEREQUAL, "&="))
            tokens.next()
        elif tokens.peek()[1] == "|=":
            result.append((token.VBAREQUAL, "|="))
            tokens.next()
        elif tokens.peek()[1] == "^=":
            result.append((token.CIRCUMFLEXEQUAL, "^="))
            tokens.next()
        elif tokens.peek()[1] == "<<=":
            result.append((token.LEFTSHIFTEQUAL, "<<="))
            tokens.next()
        elif tokens.peek()[1] == ">>=":
            result.append((token.RIGHTSHIFTEQUAL, ">>="))
            tokens.next()
        elif tokens.peek()[1] == "**=":
            result.append((token.DOUBLESTAREQUAL, "**="))
            tokens.next()
        elif tokens.peek()[1] == "//=":
            result.append((token.DOUBLESLASHEQUAL, "//="))
            tokens.next()
        else:
            raise SyntaxError
    else:
        raise SyntaxError

    return result

def _print_stmt(tokens):
    """Parse a print statement.

    ::

        print_stmt: 'print' ( [ test (',' test)* [','] ] |
                              '>>' test [ (',' test)+ [','] ] )
    """
    result = [symbol.print_stmt]

    # test (',' test)* [',']
    def option1(tokens):
        result = []
        result.append(_test(tokens))

        result = result + matcher(tokens, [comma_test], repeat=True, optional=True)
        
        if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
            result.append((token.COMMA, ","))
            tokens.next()
        
        return result

    # (',' test)
    def comma_test(tokens):
        result = []
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ","):
            raise SyntaxError
        result.append((token.COMMA, ","))
        tokens.next()
        
        result.append(_test(tokens))

        return result

    if tokens.peek()[0] == token.NAME and tokens.peek()[1] == "print":
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()

        result = result + matcher(tokens, [option1]) # TODO
    else:
        raise SyntaxError

    return result

def _del_stmt(tokens):
    """Parse a delete statement.

    ::

        del_stmt: 'del' exprlist
    """
    raise NotImplementedError


def _pass_stmt(tokens):
    """Parse a pass statement.

    ::

        pass_stmt: 'pass'
    """
    raise NotImplementedError

def _flow_stmt(tokens):
    """Parse a flow statement.

    ::

        flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
    """
    result = [symbol.flow_stmt]
    
    try:
        result.append(matcher(tokens, [_break_stmt, _return_stmt, _yield_stmt]))
    except SyntaxError:
        raise syntax_error("Expecting: break_stmt | continue_stmt | return_stmt | " \
            "raise_stmt | yield_stmt", tokens.peek())

    return result

def _break_stmt(tokens):
    """Parse a break statement.

    ::

        break_stmt: 'break'
    """
    result = [symbol.break_stmt]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "break"):
        raise SyntaxError
    
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    return result

def _continue_stmt(tokens):
    """Parse a continue statement.

    ::

        continue_stmt: 'continue'
    """
    raise NotImplementedError

def _return_stmt(tokens):
    """Parse a return statement.

    ::

        return_stmt: 'return' [testlist]
    """
    result = [symbol.return_stmt]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "return"):
        raise SyntaxError
    result.append((token.NAME, "return"))
    tokens.next()
    
    testlist = matcher(tokens, [_testlist], optional=True)
    if testlist:
        result.append(testlist)
    
    return result

def _yield_stmt(tokens):
    """Parse a yield statement.

    ::

        yield_stmt: yield_expr
    """
    result = [symbol.yield_stmt]
    
    result.append(_yield_expr(tokens))
    
    return result

def _raise_stmt(tokens):
    """Parse a raise statement.

    ::

        raise_stmt: 'raise' [test [',' test [',' test]]]
    """
    raise NotImplementedError

def _import_stmt(tokens):
    """Parse an import statement.

    ::

        import_stmt: import_name | import_from
    """
    result = [symbol.import_stmt]
    
    #result.append(matcher(tokens, [_import_name, _import_from]))
    result.append(_import_name(tokens))
    
    return result

def _import_name(tokens):
    """Parse an import name.

    ::

        import_name: 'import' dotted_as_names
    """
    result = [symbol.import_name]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "import"):
        raise SyntaxError
        
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    result.append(_dotted_as_names(tokens))

    return result

def _import_from(tokens):
    """Parse an import from.

    ::

        import_from: ('from' ('.'* dotted_name | '.'+)
                      'import' ('*' | '(' import_as_names ')' | import_as_names))
    """
    raise NotImplementedError

def _import_as_name(tokens):
    """Parse an import as names.

    ::

        import_as_name: NAME ['as' NAME]
    """
    raise NotImplementedError

def _dotted_as_name(tokens):
    """Parse a dotted as name.

    ::

        dotted_as_name: dotted_name ['as' NAME]
    """
    result = [symbol.dotted_as_name]
    
    result.append(_dotted_name(tokens))
    
    if tokens.peek()[1] == "as":
        raise NotImplementedError
    
    return result

def _import_as_names(tokens):
    """Parse import as names.

    ::

        import_as_names: import_as_name (',' import_as_name)* [',']
    """
    raise NotImplementedError

def _dotted_as_names(tokens):
    """Parse dotted as names.

    ::

        dotted_as_names: dotted_as_name (',' dotted_as_name)*
    """
    result = [symbol.dotted_as_names]
    
    result.append(_dotted_as_name(tokens))
        
    if tokens.peek()[1] == ",":
        raise NotImplementedError

    return result

def _dotted_name(tokens):
    """Parse a dotted name.

    ::

        dotted_name: NAME ('.' NAME)*
    """
    result = [symbol.dotted_name]
    
    if not tokens.peek()[0] == token.NAME:
        raise syntax_error("Expecting: NAME", tokens.peek())
        
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    if tokens.peek()[1] == ".":
        raise NotImplementedError
    
    return result

def _global_stmt(tokens):
    """Parse a global statement.

    ::

        global_stmt: 'global' NAME (',' NAME)*
    """
    raise NotImplementedError

def _exec_stmt(tokens):
    """Parse an exec statement.

    ::

        exec_stmt: 'exec' expr ['in' test [',' test]]
    """
    raise NotImplementedError

def _assert_stmt(tokens):
    """Parse an assert statement.

    ::

        assert_stmt: 'assert' test [',' test]
    """
    raise NotImplementedError

def _compound_stmt(tokens):
    """Parse a compound statement.

    ::

        compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
    """
    result = [symbol.compound_stmt]
  
    try:
        result.append(matcher(tokens, [_if_stmt, _while_stmt, _try_stmt, _funcdef,
            _for_stmt, _classdef, _decorated]))
    except SyntaxError:
        raise syntax_error("Expecting: if_stmt | while_stmt | for_stmt | "
            "try_stmt | with_stmt | funcdef | classdef | decorated", tokens.peek())

    return result

def _if_stmt(tokens):
    """Parse and if statement.

    ::

        if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
    """
    result = [symbol.if_stmt]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "if"):
        raise SyntaxError
    result.append((token.NAME, "if"))
    tokens.next()
    
    result.append(_test(tokens))
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise SyntaxError
    result.append((token.COLON, ":"))
    tokens.next()
    
    result.append(_suite(tokens))
    
    if tokens.peek()[1] == "elif":
        raise NotImplementedError
    
    def else_suite(tokens):
        result = []
        
        if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "else"):
            raise SyntaxError
        result.append((token.NAME, "else"))
        tokens.next()
        
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
            raise SyntaxError
        result.append((token.COLON, ":"))
        tokens.next()
        
        result.append(_suite(tokens))
        
        return result
    
    else_result = matcher(tokens, [else_suite], optional=True)
    if else_result:
        result = result + else_result
        
    return result

def _while_stmt(tokens):
    """Parse a while statement.

    ::

        while_stmt: 'while' test ':' suite ['else' ':' suite]
    """
    result = [symbol.while_stmt]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "while"):
        raise syntax_error("Expecting 'while'", tokens.peek())
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()

    result.append(_test(tokens))

    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise syntax_error("Expecting ':'", tokens.peek())
    result.append((token.COLON, ":"))
    tokens.next()

    result.append(_suite(tokens))

    if tokens.peek()[0] == token.NAME and tokens.peek()[1] == "else":
        tokens.next()
        
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
            raise syntax_error("Expecting ':'", tokens.peek())
            
        result.append(_suite(tokens))

    return result

def _for_stmt(tokens):
    """Parse a for statement.

    ::

        for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
    """
    result = [symbol.for_stmt]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "for"):
        raise SyntaxError
    result.append((token.NAME, "for"))
    tokens.next()

    result.append(_exprlist(tokens))
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "in"):
        raise SyntaxError
    result.append((token.NAME, "in"))
    tokens.next()

    result.append(_testlist(tokens))
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise SyntaxError
    result.append((token.COLON, ":"))
    tokens.next()
    
    result.append(_suite(tokens))
    
    def optional_else(tokens):
        result = []
        
        if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "else"):
            raise SyntaxError
        result.append((token.NAME, "else"))
        tokens.next()

        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
            raise SyntaxError
        result.append((token.COLON, ":"))
        tokens.next()

        result.append(_suite(tokens))

        return result
    
    option = matcher(tokens, [optional_else], optional=True)
    if option:
        result.append(option)

    return result

def _try_stmt(tokens):
    """Parse a try statement.

    ::

        try_stmt: ('try' ':' suite
                   ((except_clause ':' suite)+
                    ['else' ':' suite]
                    ['finally' ':' suite] |
                   'finally' ':' suite))
    """
    result = [symbol.try_stmt]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "try"):
        raise syntax_error("Expecting: try", tokens.peek())
    
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise syntax_error("Expecting: ':'", tokens.peek())

    result.append((token.COLON, tokens.peek()[1]))
    tokens.next()

    result.append(_suite(tokens))
    
    # TODO repeat
    result.append(_except_clause(tokens))
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise syntax_error("Expecting: ':'", tokens.peek())

    result.append((token.COLON, tokens.peek()[1]))
    tokens.next()

    result.append(_suite(tokens))

    # TODO else/finally
    
    return result

def _with_stmt(tokens):
    """Parse a with statement.

    ::

        with_stmt: 'with' with_item (',' with_item)*  ':' suite
    """
    raise NotImplementedError

def _with_item(tokens):
    """Parse a with item.

    ::

        with_item: test ['as' expr]
    """
    raise NotImplementedError

def _except_clause(tokens):
    """Parse an except clause.

    ::

        except_clause: 'except' [test [('as' | ',') test]]
    """
    result = [symbol.except_clause]

    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "except"):
        raise syntax_error("Expecting 'except'", tokens.peek())
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    # TODO
    result.append(_test(tokens))

    return result
    
def _suite(tokens):
    """Parse a suite.

    ::

        suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    """
    result = [symbol.suite]

    if tokens.peek()[0] == token.NEWLINE:
        result.append((token.NEWLINE, ""))
        tokens.next()

        if tokens.peek()[0] != token.INDENT:
            raise syntax_error("Expecting INDENT", tokens.peek())
        result.append((token.INDENT, ''))
        tokens.next()
        
        try:
            while tokens.peek()[0] != token.DEDENT:
                result.append(_stmt(tokens))

        except StopIteration:
            pass # raise "Expecting DEDENT" in next block

        if tokens.peek()[0] != token.DEDENT:
            raise syntax_error("Expecting DEDENT", tokens.peek())
        result.append((token.DEDENT, ''))
        tokens.next()
    else:
        raise NotImplementedError

    return result

def _testlist_safe(tokens):
    """Parse a testlist safe.

    ::

        testlist_safe: old_test [(',' old_test)+ [',']]
    """
    result = [symbol.testlist_safe]

    result.append(_old_test(tokens))
    
    # TODO

    return result

def _old_test(tokens):
    """Parse an old test.

    ::

        old_test: or_test | old_lambdef
    """
    result = [symbol.old_test]
    
    result.append(_or_test(tokens))

    # TODO
    
    return result

def _old_lambdef(tokens):
    """Parse an old lambda definition.

    ::

        old_lambdef: 'lambda' [varargslist] ':' old_test
    """
    raise NotImplementedError

def _test(tokens):
    """Parse a test statement.

    ::

        test: or_test ['if' or_test 'else' test] | lambdef
    """
    result = [symbol.test]
    result.append(_or_test(tokens))
    
    # TODO if/lambdef
    
    return result

def _or_test(tokens):
    """Parse an or_test statement

    ::

        or_test: and_test ('or' and_test)*
    """
    result = [symbol.or_test]
    result.append(_and_test(tokens))

    # TODO or and_test
    
    return result

def _and_test(tokens):
    """Parse an and test statement.

    ::

        and_test: not_test ('and' not_test)*
    """
    result = [symbol.and_test]
    result.append(_not_test(tokens))
    
    # TODO and not_test
    
    return result

def _not_test(tokens):
    """Parse a not test statement.

    ::

        not_test: 'not' not_test | comparison
    """
    result = [symbol.not_test]

    # 'not' not_test
    def not_test(tokens):
        result = []
        
        if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "not"):
            raise SyntaxError
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()

        result.append(_not_test(tokens))
        
        return result
    
    result = result + matcher(tokens, [not_test, [_comparison]])

    return result

def _comparison(tokens):
    """Parse a comparison.

    ::

        comparison: expr (comp_op expr)*
    """
    result = [symbol.comparison]
    
    result.append(_expr(tokens))
    result = result + matcher(tokens, [(_comp_op, _expr)], optional=True, repeat=True)

    return result

def _comp_op(tokens):
    """Parse a compare operator statement.

    ::

        comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    """
    result = [symbol.comp_op]

    parser_error = syntax_error("Expecting: '<'|'>'|'=='|'>='|'<='|'<>'|'!='"
        "|'in'|'not' 'in'|'is'|'is' 'not'", tokens.peek())

    if tokens.peek()[0] == token.OP:
        if tokens.peek()[1] == "<":
            result.append((token.LESS, "<"))
            tokens.next()
        elif tokens.peek()[1] == ">":
            result.append((token.GREATER, ">"))
            tokens.next()
        elif tokens.peek()[1] == "==":
            result.append((token.EQEQUAL, "=="))
            tokens.next()
        elif tokens.peek()[1] == ">=":
            result.append((token.GREATEREQUAL, ">="))
            tokens.next()
        elif tokens.peek()[1] == "<=":
            result.append((token.LESSEQUAL, "<="))
            tokens.next()
        elif tokens.peek()[1] == "<>":
            result.append((token.NOTEQUAL, "<>"))
            tokens.next()
        elif tokens.peek()[1] == "!=":
            result.append((token.NOTEQUAL, "!="))
            tokens.next()
        else:
            raise parser_error
    elif tokens.peek()[0] == token.NAME:
        if tokens.peek()[1] == "in":
            result.append((tokens.peek()[0], tokens.peek()[1]))
            tokens.next()
        elif tokens.peek()[1] == "not":
            result.append((tokens.peek()[0], tokens.peek()[1]))
            tokens.next()
            if tokens.peek()[0] == "in":
                result.append((tokens.peek()[0], tokens.peek()[1]))
                tokens.next()
            else:
                raise parser_error
        elif tokens.peek()[1] == "is":
            result.append((tokens.peek()[0], tokens.peek()[1]))
            tokens.next()
            if tokens.peek()[0] == "not":
                result.append((tokens.peek()[0], tokens.peek()[1]))
                tokens.next()
    else:
        raise parser_error

    return result

def _expr(tokens):
    """Parse an expression statement.

    ::

        expr: xor_expr ('|' xor_expr)*
    """
    result = [symbol.expr]
    result.append(_xor_expr(tokens))

    # TODO | xor_expr
    
    return result

def _xor_expr(tokens):
    """Parse an xor expression statement.

    ::

        xor_expr: and_expr ('^' and_expr)*
    """
    result = [symbol.xor_expr]
    result.append(_and_expr(tokens))

    # TODO ^ and_exr
    
    return result

def _and_expr(tokens):
    """Parse an and expression statement.

    ::

        and_expr: shift_expr ('&' shift_expr)*
    """
    result = [symbol.and_expr]
    result.append(_shift_expr(tokens))
    
    # TODO
    
    return result

def _shift_expr(tokens):
    """Parse a shift_expr statement

    ::

        shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    """
    result = [symbol.shift_expr]
    result.append(_arith_expr(tokens))
    
    # TODO
    
    return result

def _arith_expr(tokens):
    """Parse an arithmetic expression statement.

    ::

        arith_expr: term (('+'|'-') term)*
    """
    result = [symbol.arith_expr]
    result.append(_term(tokens))
    
    if tokens.peek()[0] == token.OP and tokens.peek()[1] == "+":
        result.append((token.PLUS, "+"))
        tokens.next()
        result.append(_term(tokens))
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "-":
        result.append((token.MINUS, "-"))
        tokens.next()
        result.append(_term(tokens))
    
    # TODO: repetition

    return result

def _term(tokens):
    """Parse a term statement.

    ::

        term: factor (('*'|'/'|'%'|'//') factor)*
    """
    result = [symbol.term]
    result.append(_factor(tokens))
    
    def _factor_op(tokens):
        if tokens.peek()[0] == token.OP and tokens.peek()[1] == "*":
            result = (token.STAR, "*")
            tokens.next()
        elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "/":
            result = (token.SLASH, "/")
            tokens.next()
        elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "%":
            result = (token.PERCENT, "%")
            tokens.next()
        elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "//":
            result = (token.DOUBLESLASH, "//")
            tokens.next()
        else:
            raise SyntaxError

        return result
    
    result = result + matcher(tokens, [(_factor_op, _factor)], optional=True, repeat=True)

    return result
    
def _factor(tokens):
    """Parse a factor statement.

    ::

        factor: ('+'|'-'|'~') factor | power
    """
    result = [symbol.factor]
    
    # TODO
    
    result.append(_power(tokens))
    return result
    
def _power(tokens):
    """Parse a power statement.

    ::

        power: atom trailer* ['**' factor]
    """
    result = [symbol.power]
    
    result.append(_atom(tokens))
    
    result = result + matcher(tokens, [[_trailer]], optional=True, repeat=True)

    # TODO ['**' factor]

    return result

def _atom(tokens):
    """Parse an atom statement.

    ::

        atom: ('(' [yield_expr|testlist_comp] ')' |
               '[' [listmaker] ']' |
               '{' [dictorsetmaker] '}' |
               '`' testlist1 '`' |
               NAME | NUMBER | STRING+)
    """
    result = [symbol.atom]
    
    keywords = ["and", "as", "assert", "break", "class", "continue", "def",
        "del", "elif", "else", "except", "exec", "finally", "for", "from",
        "global", "if", "import", "in", "is", "lambda", "not", "or", "pass",
        "print", "raise", "return", "try", "while", "with", "yield"]

    if tokens.peek()[0] == token.OP and tokens.peek()[1] == "(":
        result.append((token.LPAR, "("))
        tokens.next()

        # TODO yield_expr
        result.append(_testlist_comp(tokens))

        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "("):
            result.append((token.RPAR, ")"))
            tokens.next()
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "[":
        result.append((token.LSQB, "["))
        tokens.next()
        listmaker = matcher(tokens, [_listmaker], optional=True)
        if listmaker:
            result.append(listmaker)
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "]"):
            raise SyntaxError
        result.append((token.RSQB, "]"))
        tokens.next()
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "{":
        raise NotImplementedError
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "`":
        raise NotImplementedError
    elif tokens.peek()[0] == token.NUMBER:
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
    elif tokens.peek()[0] == token.NAME:
        if tokens.peek()[1] in keywords:
            raise SyntaxError # keywords cannot appear here
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
    elif tokens.peek()[0] == token.STRING:
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
    else:
        raise syntax_error("Expecting: ('(' [yield_expr|testlist_comp] ')' | "
            "'[' [listmaker] ']' | "
            "'{' [dictorsetmaker] '}' | "
            "'`' testlist1 '`' | "
            "NAME | NUMBER | STRING+)", tokens.peek())
        
    return result
    
def _listmaker(tokens):
    """Parse a listmaker statement.

    ::

        listmaker: test ( list_for | (',' test)* [','] )
    """
    result = [symbol.listmaker]
    
    result.append(_test(tokens))

    # ',' test
    def comma_test(tokens):
        result = []
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ","):
            raise SyntaxError
        result.append((token.COMMA, ","))
        tokens.next()
        result.append(_test(tokens))
        return result
    
    # (',' test)*
    def comma_test_repeat(tokens):
        return matcher(tokens, [comma_test], repeat=True, optional=True)

    # (',' test)* [',']
    def comma_test_repeat_comma(tokens):
        result = comma_test_repeat(tokens)
        if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
            result.append((token.COMMA, ","))
            tokens.next()
        return result
    
    result = result + matcher(tokens, [[_list_for], comma_test_repeat_comma])
    return result

def _testlist_comp(tokens):
    """Parse a testlist comp statement.

    ::

        testlist_comp: test ( comp_for | (',' test)* [','] )
    """
    result = [symbol.testlist_comp]
    
    result.append(_test(tokens))

    # TODO comp_for
    
    # TODO this is incorrect, needs to be rewritten with matcher
    while tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
        result.append((token.COMMA, ","))
        tokens.next()
        
        result.append(_test(tokens))
    
    if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
        result.append((token.COMMA, ","))
        tokens.next()

    return result

def _lambdef(tokens):
    """Parse a lambda definition.

    ::

        lambdef: 'lambda' [varargslist] ':' test
    """
    raise NotImplementedError

def _trailer(tokens):
    """Parse a trailer.

    ::

        trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
    """
    result = [symbol.trailer]

    if tokens.peek()[0] == token.OP and tokens.peek()[1] == "(":
        result.append((token.LPAR, "("))
        tokens.next()

        arglist = matcher(tokens, [_arglist], optional=True)
        if arglist:
            result.append(arglist)

        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ")"):
            raise syntax_error("Expecting ')'", tokens.peek())
        result.append((token.RPAR, ")"))
        tokens.next()
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "[":
        result.append((token.LSQB, "["))
        tokens.next()
        
        result.append(_subscriptlist(tokens))
        
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "]"):
            raise syntax_error("Expecting ')'", tokens.peek())
        result.append((token.RSQB, "]"))
        tokens.next()
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == ".":
        result.append((token.DOT, "."))
        tokens.next()
        
        if not (tokens.peek()[0] == token.NAME):
            raise syntax_error("Expecting name", tokens.peek())
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
    else:
        raise syntax_error("Expecting '(', '[' or '.'", tokens.peek())
    
    return result

def _subscriptlist(tokens):
    """Parse a subscriptlist.

    ::

        subscriptlist: subscript (',' subscript)* [',']
    """
    result = [symbol.subscriptlist]
    
    result.append(_subscript(tokens))
    
    if tokens.peek()[1] == ",":
        raise NotImplementedError
    
    return result

def _subscript(tokens):
    """Parse a subscript.

    ::

        subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
    """
    # This grammar is *not* left-factored and has to be rewritten as follows
    # (<=> denotes "if and only if"). Derivation:
    #
    #   subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
    #   <=>
    #   subscript: '.' '.' '.' | test | test ':' [test] [slicep] | ':' [test] [sliceop]
    #   <=>
    #   subscript: '.' '.' '.' | test [':' [test] [slicep]] | ':' [test] [slicep]
    #   <=>
    #   subscript: '.' '.' '.' | test [rest] | rest
    #   rest:      ':' [test] [slicep]
    #

    result = [symbol.subscript]
    
    # TODO
    result.append(_test(tokens))
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise SyntaxError
    result.append((token.COLON, tokens.peek()[1]))
    tokens.next()

    return result

def _sliceop(tokens):
    """Parse a slice operation.

    ::

        sliceop: ':' [test]
    """
    raise NotImplementedError

def _exprlist(tokens):
    """Parse an expression list.

    ::

        exprlist: expr (',' expr)* [',']
    """
    result = [symbol.exprlist]
    
    result.append(_expr(tokens))

    # ',' expr
    def comma_expr(tokens):
        result = []
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ","):
            raise SyntaxError
        result.append((token.COMMA, ","))
        tokens.next()
        result.append(_expr(tokens))
        return result

    more_expr = matcher(tokens, [comma_expr], optional=True, repeat=True)
    if more_expr:
        result = result + more_expr
    
    if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
        result.append((token.COMMA, ","))
        tokens.next()

    return result

def _testlist(tokens):
    """Parse a testlist.

    ::

        testlist: test (',' test)* [',']
    """
    result = [symbol.testlist]
    
    result.append(_test(tokens))
    
    # TODO this is incorrect, needs to be rewritten with matcher
    while tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
        result.append((token.COMMA, ","))
        tokens.next()
        result.append(_test(tokens))

    if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
        result.append((token.COMMA, ","))
        tokens.next()

    return result

def _dictorsetmaker(tokens):
    """Parse a dict or set maker statement.

    ::

        dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
                          (test (comp_for | (',' test)* [','])) )
    """
    raise NotImplementedError

def _classdef(tokens):
    """Parse a class definition.

    ::

            classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
    """
    result = [symbol.classdef]

    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "class"):
        raise syntax_error("Expecting 'class'", tokens.peek())
        
    result.append((token.NAME, "class"))
    tokens.next()
    
    if not (tokens.peek()[0] == token.NAME):
        raise syntax_error("Expecting class name", tokens.peek())
    
    result.append((token.NAME, tokens.peek()[1]))
    tokens.next()
    
    if tokens.peek()[0] == token.OP and tokens.peek()[1] == "(":
        result.append((token.LPAR, "("))
        tokens.next()
        
        testlist = matcher(tokens, [_testlist], optional=True)
        if testlist:
            result.append(testlist)
        
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ")"):
            raise syntax_error("Expecting ')'", tokens.peek())
        result.append((token.RPAR, ")"))
        tokens.next()
    
    if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ":"):
        raise syntax_error("Expecting ':'", tokens.peek())

    result.append((token.COLON, ":"))
    tokens.next()

    result.append(_suite(tokens))

    return result

def _arglist(tokens):
    """Parse an argument list.

    ::

        arglist: (argument ',')* (argument [',']
                                 |'*' test (',' argument)* [',' '**' test]
                                 |'**' test)
    """
    result = [symbol.arglist]

    # argument ','
    def argument_comma(tokens):
        result = []
        result.append(_argument(tokens))
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == ","):
            raise SyntaxError
        result.append((token.COMMA, ","))
        tokens.next()
        return result
        
    result = result + matcher(tokens, [argument_comma], repeat=True, optional=True)
    
    # argument [',']
    def option1(tokens):
        result = []
        result.append(_argument(tokens))
        if tokens.peek()[0] == token.OP and tokens.peek()[1] == ",":
            result.append((token.COMMA, ","))
            tokens.next()
        return result

    # TODO option2 '*' test (',' argument)* [',' '**' test]
    # TODO option3 '**' test

    result = result + matcher(tokens, [option1])

    return result

def _argument(tokens):
    """Parse an argument.

    ::

        argument: test [comp_for] | test '=' test
    """
    # This grammar is *not* left-factored and has to be rewritten as follows
    # (ε denotes the empty string):
    #
    #   argument: test option
    #   option:   ε | comp_for | '=' test
    #

    result = [symbol.argument]

    result.append(_test(tokens))

    # '=' test
    def equals_test(tokens):
        result = []
        if not (tokens.peek()[0] == token.OP and tokens.peek()[1] == "="):
            raise SyntaxError
        result.append((token.EQUAL, "="))
        tokens.next()
        result.append(_test(tokens))
        return result
    
    option = matcher(tokens, [[_comp_for], equals_test], optional=True)
    if option:
        result = result + option

    return result

def _list_iter(tokens):
    """Parse a list iteration.

    ::

        list_iter: list_for | list_if
    """
    result = [symbol.list_iter]

    result.append(matcher(tokens, [_list_for, _list_if]))

    return result

def _list_for(tokens):
    """Parse a list for.

    ::

        list_for: 'for' exprlist 'in' testlist_safe [list_iter]
    """
    result = [symbol.list_for]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "for"):
        raise SyntaxError
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()

    result.append(_exprlist(tokens))

    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "in"):
        raise SyntaxError
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()

    result.append(_testlist_safe(tokens))

    list_iter = matcher(tokens, [_list_iter], optional=True)
    if list_iter:
        result.append(list_iter)

    return result

def _list_if(tokens):
    """Parse a list if.

    ::

        list_if: 'if' old_test [list_iter]
    """
    result = [symbol.list_if]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "if"):
        raise SyntaxError
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()

    result.append(_old_test(tokens))

    list_iter = matcher(tokens, [_list_iter], optional=True)
    if list_iter:
        result.append(list_iter)
       
    return result

def _comp_iter(tokens):
    """Parse a comp iter.

    ::

        comp_iter: comp_for | comp_if
    """
    raise NotImplementedError

def _comp_for(tokens):
    """Parse a comp for.

    ::

        comp_for: 'for' exprlist 'in' or_test [comp_iter]
    """
    result = [symbol.comp_for]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "for"):
        raise SyntaxError
    result.append((token.NAME, "for"))
    tokens.next()

    result.append(_exprlist(tokens))

    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "in"):
        raise SyntaxError
    result.append((token.NAME, "in"))
    tokens.next()

    result.append(_or_test(tokens))

    return result

def _comp_if(tokens):
    """Parse a comp if.

    ::

        comp_if: 'if' old_test [comp_iter]
    """
    raise NotImplementedError

def _testlist1(tokens):
    """Parse a testlist1.

    ::

        testlist1: test (',' test)*
    """
    raise NotImplementedError

def _encoding_decl(tokens):
    """Parse an encoding declaration.

    ::

        encoding_decl: NAME
    """
    raise NotImplementedError

def _yield_expr(tokens):
    """Parse a yield expression.

    ::

        yield_expr: 'yield' [testlist]
    """
    result = [symbol.yield_expr]
    
    if not (tokens.peek()[0] == token.NAME and tokens.peek()[1] == "yield"):
        raise syntax_error("Expecting 'yield'", tokens.peek())
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    result.append(matcher(tokens, [_testlist], optional=True))
    
    return result

def matcher(tokens, choices, repeat=False, optional=False):
    """The matcher finds a parse path among multiple choices.
    
    The end of a recursion is indicated by a ``SyntaxError``. When a child path has
    failed, the tokens generator is "rolled back" to the last good position.

    Args:
        tokens (TokenIterator): token iterator
        choices (list): a list of 
        repeat: repeat a choice (only a single choice possible)
        optional: matching optional or mandatory (does at least one match need to occur?)

    Returns:
        list: The matching parse tree element, ``None`` for no matches

    Raises:
        SyntaxError: Syntax Error

    >>> from pycep.tokenizer import generate_tokens
    >>> from StringIO import StringIO
    >>> from pycep.parser import TokenIterator, matcher
    >>> from pycep.parser import _expr_stmt, _print_stmt, _del_stmt, _testlist,
    ...     _comp_op, _expr

    Suppose the following example with multiple choices (abbreviated):
    
    ::

        small_stmt: (expr_stmt | print_stmt  | del_stmt)

    This would be written as:
    
    >>> t1 = TokenIterator(generate_tokens(StringIO('print "Hello, world!"').readline))
    >>> matcher(t1, [_expr_stmt, _print_stmt, _del_stmt])
    [272, (1, 'print'), [304, [305, [306, [307, [308, [310, [311, [312, [313, [314, [315, [316, [317, [318, (3, '"Hello, world!"')]]]]]]]]]]]]]]]

    Suppose the following example with an optional argument ``testlist``:
    
    ::
    
        yield_expr: 'yield' [testlist]
    
    This would be written as:
    
    >>> t2 = TokenIterator(generate_tokens(StringIO("yield 5").readline))
    >>> t2.next()
    (1, 'yield', (1, 0), (1, 5), 'yield 5')
    >>> matcher(t2, [_testlist], optional=True)
    [327, [304, [305, [306, [307, [308, [310, [311, [312, [313, [314, [315, [316, [317, [318, (2, '5')]]]]]]]]]]]]]]]
    
    Suppose the following example with a repetition of the sequence ``comp_op expr``:
    
    ::

        comparison: expr (comp_op expr)*

    This would be written as:
    
    >>> t3 = TokenIterator(generate_tokens(StringIO("1 < 2").readline))
    >>> _expr(t3)
    [310, [311, [312, [313, [314, [315, [316, [317, [318, (2, '1')]]]]]]]]]
    >>> matcher(t3, [(_comp_op, _expr)], optional=True, repeat=True)
    [[309, (20, '<')], [310, [311, [312, [313, [314, [315, [316, [317, [318, (2, '2')]]]]]]]]]]

    """

    last_good = tokens.index
    result, success = None, False

    if repeat:
        if len(choices) != 1:
            raise ValueError("Can only repeat a single choice")
        
        choice = choices[0]
        result = []
       
        while True:
            try:
                # given a sequence, only succeed if the *entire* sequence succeeds
                if type(choice) in [list, tuple]:
                    tmp = []
    
                    for sequence in choice:
                        tmp.append(sequence(tokens))
                    
                    # all paths were successful -> add to result
                    result = result + tmp
                else:
                    result = result + choice(tokens)

                success = True
                last_good = tokens.index
            except SyntaxError:
                tokens.seek(last_good)
                break # stop loop

    else:
        for choice in choices:
            try:
                # given a sequence, only succeed if the *entire* sequence succeeds
                if type(choice) in [list, tuple]:
                    result = tmp = []
    
                    for sequence in choice:
                        tmp.append(sequence(tokens))
                    
                    # all paths were successful -> add to result
                    result = tmp
                else:
                    result = choice(tokens)
    
                success = True
                break # stop iteration
            except SyntaxError:
                tokens.seek(last_good)

    if not optional and not success:
        raise SyntaxError

    return result

class TokenIterator(object):
    """Wrapper for token generator which adds peeking and seeking.
    Furthermore, physical line breaks (``tokenize.NL``) and comments
    (``token.N_TOKENS``) are skipped from the input.
       
    >>> from pycep.tokenizer import generate_tokens
    >>> from StringIO import StringIO
    >>> from pycep.parser import TokenIterator
    >>> tokens = TokenIterator(generate_tokens(StringIO('print "Hello, world!"').readline))
    >>> tokens.peek()
    (1, 'print', (1, 0), (1, 5), 'print "Hello, world!"')
    >>> tokens.next()
    (1, 'print', (1, 0), (1, 5), 'print "Hello, world!"')
    >>> tokens.next()
    (3, '"Hello, world!"', (1, 6), (1, 19), 'print "Hello, world!"')
    >>> tokens.next()
    (0, '', (2, 0), (2, 0), '')
    >>> tokens.seek(-1)
    >>> tokens.peek()
    (1, 'print', (1, 0), (1, 5), 'print "Hello, world!"')
    """

    def __init__(self, generator):
        self.index = -1
        self._values = list(generator)

    def __iter__(self):
        return self

    def next(self):
        value = self._next()

        while self._is_skip(value[0]):
            value = self._next()

        return value
    
    def _next(self):
        if self.index + 1 < len(self._values):
            self.index += 1
            value = self._values[self.index]
        else:
            raise StopIteration

        return value
    
    def peek(self):
        lookahead = 1
        value = self._peek(lookahead)

        while self._is_skip(value[0]):
            lookahead += 1
            value = self._peek(lookahead)

        return value
        
    def _peek(self, lookahead):
        if self.index + lookahead < len(self._values):
            value = self._values[self.index + lookahead]
        else:
            raise StopIteration
            
        return value

    def _is_skip(self, value):
        return value == tokenize.NL or value == token.N_TOKENS # physical line breaks and comments

    def seek(self, index):
        if index < -1 or index > len(self._values) - 1:
            raise IndexError("Invalid seek")
        
        self.index = index