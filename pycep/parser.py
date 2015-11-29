from __future__ import absolute_import
import pycep.tokenizer
import parser
from parser import ParserError
import token
import tokenize
import symbol
from itertools import tee
from more_itertools import peekable
from StringIO import StringIO

def suite(source, totuple=False):
    """The parser takes a string containing the source code as an input and
    returns a parse tree.

    >>> import pycep.parser
    >>> st = pycep.parser.suite('print "Hello World"')
    >>> st.totuple()
    (257, (267, (268, (269, (272, (1, 'print'), (304, (305, (306, (307, (308, (310, (311, (312, (313, (314, (315, (316, (317, (318, (3, '"Hello World"'))))))))))))))))), (4, ''))), (4, ''), (0, ''))

    Args:
        source (string): Source code
        totuple (boolean): For testing: Return internal parser data structure, don't convert to ``parser.st`` object
        
    Returns:
        parser.st: Parse Tree

    Raises:
        ParserError: Parser Error

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
            atom -> "STRING \\"Hello World\\""
        }


    See also:
        * Python Language Reference: https://docs.python.org/2/reference/grammar.html
        * Non-Terminal Symbols: https://hg.python.org/cpython/file/2.7/Lib/symbol.py
        * Leaf Nodes: https://docs.python.org/2/library/token.html
    """

    parser.tokens = peekable(pycep.tokenizer.generate_tokens(StringIO(source).readline))
    result = _file_input()
    
    if totuple:
        # recursively convert list-of-lists to tuples-of-tuples
        def listit(t):
            return tuple(map(listit, t)) if isinstance(t, (list, tuple)) else t

        return listit(result)
    else:
        return parser.sequence2st(result)

def _single_input():
    """Parse a single input.

    ::

        single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE

    Returns:
        list: A parse tree element for the single input
    """
    raise NotImplementedError

def _file_input():
    """Parse a module or sequence of command read from an input file.

    ::
    
        file_input: (NEWLINE | stmt)* ENDMARKER

    Returns:
        list: A parse tree element for the file input
    """
    result = [symbol.file_input]
    
    try:
        while not parser.tokens.peek()[0] == token.ENDMARKER:
            if parser.tokens.peek()[0] == token.NEWLINE:
                result.append((parser.tokens.peek()[0], ''))
                parser.tokens.next()
            else:
                result.append(_stmt())
    except StopIteration:
        pass # raise "Expecting ENDMARKER" in next block

    # Training NEWLINE not defined in grammar, but Python's parser always
    # appends it, thus emulate this behavior 
    result.append((token.NEWLINE, ''))

    if parser.tokens.next()[0] != token.ENDMARKER:
        raise ParserError("Expecting ENDMARKER")

    result.append((token.ENDMARKER, ''))

    return result

def _eval_input():
    """Parse an evaluation input.

    ::

        eval_input: testlist NEWLINE* ENDMARKER

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _decorator():
    """Parse a decorator.

    ::

        decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _decorators():
    """Parse a list of decorators.

    ::

        decorators: decorator+

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _decorated():
    """Parse a decorated statement.

    ::

        decorated: decorators (classdef | funcdef)

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _funcdef():
    """Parse a function definition.

    ::

        funcdef: 'def' NAME parameters ':' suite

    Returns:
        list: A parse tree element
    """
    result = [symbol.funcdef]
    
    if not (parser.tokens.peek()[0] == token.NAME and parser.tokens.peek()[1] == "def"):
        raise ParserError("Expecting `def'")
    result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
    parser.tokens.next()
        
    if not (parser.tokens.peek()[0] == token.NAME):
        raise ParserError("Expecting function name")
    result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
    parser.tokens.next()

    result.append(_parameters()) 

    if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ':'):
        raise ParserError("Expecting `:'")
    result.append((token.COLON, ':'))
    parser.tokens.next()
    
    result.append(_suite())
    
    return result

def _parameters():
    """Parse a parameter list.

    ::

        parameters: '(' [varargslist] ')'

    Returns:
        list: A parse tree element
    """
    result = [symbol.parameters]

    if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == '('):
        raise ParserError("Expecting `('")
    result.append((token.LPAR, '('))
    parser.tokens.next()

    try:
        result.append(_varargslist())
    except ParserError:
        pass # varargslist is optional
    
    if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ')'):
        raise ParserError("Expecting `)'")
    result.append((token.RPAR, ')'))
    parser.tokens.next()

    return result

def _varargslist():
    """Parse a variable argument list.

    ::

        varargslist: ((fpdef ['=' test] ',')*
                      ('*' NAME [',' '**' NAME] | '**' NAME) |
                      fpdef ['=' test] (',' fpdef ['=' test])* [','])

    Returns:
        list: A parse tree element
    """
    result = [symbol.varargslist]
    result.append(_fpdef())

    # TODO
    
    return result

def _fpdef():
    """Parse function parameter definition.

    ::

        fpdef: NAME | '(' fplist ')'

    Returns:
        list: A parse tree element
    """
    result = [symbol.fpdef]
    result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
    parser.tokens.next()
    
    # TODO
    
    return result

def _fplist():
    """Parse a function parameter list

    ::

        fplist: fpdef (',' fpdef)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _stmt():
    """Parse a statement.

    ::

        stmt: simple_stmt | compound_stmt

    Returns:
        list: A parse tree element
    """
    result = [symbol.stmt]

    # TODO: replace this by "choice" between simple_stmt and compound_stmt
    if (parser.tokens.peek()[0] == token.NAME and parser.tokens.peek()[1] in \
        ["if", "while", "try", "with", "def", "class"]):
        result.append(_compound_stmt())
    elif parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "@":
        result.append(_compound_stmt())
    else:
        result.append(_simple_stmt())

    return result

def _simple_stmt():
    """Parse a simple statement.

    ::

        simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE

    Returns:
        list: A parse tree element
    """
    result = [symbol.simple_stmt]

    result.append(_small_stmt())

    while parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ";":
        result.append((token.SEMI, ";"))
        parser.tokens.next()
        result.append(_small_stmt())
        
    if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ";":
        result.append((token.SEMI, ";"))
        parser.tokens.next()

    # trailing NEWLINE is mandatory according to grammar, but in Python's parser
    # it is optional, thus imitate this behavior
    if parser.tokens.peek()[0] == token.NEWLINE:
        parser.tokens.next()
    
    result.append((token.NEWLINE, ''))

    # TODO hack
    if parser.tokens.peek()[0] == tokenize.NL:
        parser.tokens.next()

    return result

def _small_stmt():
    """Parse a small statement.

    ::

        small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
                     import_stmt | global_stmt | exec_stmt | assert_stmt)

    Returns:
        list: A parse tree element
    """
    result = [symbol.small_stmt]

    # Remember the last "good" position of the tokens generator
    parser.tokens, last_good_tokens = tee(parser.tokens)
    parser.tokens = peekable(parser.tokens)

    choices = [_expr_stmt, _print_stmt, _del_stmt, _pass_stmt, _flow_stmt,
        _import_stmt, _global_stmt, _exec_stmt, _assert_stmt]
    subtree = None

    # Recursively descend a path. End of recursion is indicated by a ParserError
    # from the child path. When a child path has failed, "roll back" the tokens-
    # generator to the last good position
    for choice in choices:
        try:
            subtree = choice()
            break # break this loop if choice matches
        except ParserError:
            # restore last good position
            parser.tokens = peekable(last_good_tokens)

    if not subtree:
        raise ParserError("Expecting (expr_stmt | print_stmt  | del_stmt | "
            "pass_stmt | flow_stmt | import_stmt | global_stmt | exec_stmt | "
            "assert_stmt")
            
    result.append(subtree)

    return result

def _expr_stmt():
    """Parse an expr stmt.

    ::

        expr_stmt: testlist (augassign (yield_expr|testlist) |
                             ('=' (yield_expr|testlist))*)

    Returns:
        list: A parse tree element
    """
    result = [symbol.expr_stmt]
    
    result.append(_testlist())
    
    while parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "=":
        result.append((token.EQUAL, "="))
        parser.tokens.next()
        result.append(_testlist())

    # TODO augassign / yield_expr
    
    return result

def _augassign():
    """Parse an augassign statement.

    ::

        augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
        '<<=' | '>>=' | '**=' | '//=')

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _print_stmt():
    """Parse a print statement.

    ::

        print_stmt: 'print' ( [ test (',' test)* [','] ] |
                              '>>' test [ (',' test)+ [','] ] )

    Returns:
        list: A parse tree element
    """
    result = [symbol.print_stmt]

    if parser.tokens.peek()[0] == token.NAME and parser.tokens.peek()[1] == "print":
        result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
        parser.tokens.next()
        
        if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ">>":
            raise NotImplementedError
        else:
            result.append(_test())
        
        # TODO: test is optional
    else:
        raise parser.ParserError

    return result

def _del_stmt():
    """Parse a delete statement.

    ::

        del_stmt: 'del' exprlist

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError


def _pass_stmt():
    """Parse a pass statement.

    ::

        pass_stmt: 'pass'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _flow_stmt():
    """Parse a flow statement.

    ::

        flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _break_stmt():
    """Parse a break statement.

    ::

        break_stmt: 'break'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _continue_stmt():
    """Parse a continue statement.

    ::

        continue_stmt: 'continue'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _return_stmt():
    """Parse a return statement.

    ::

        return_stmt: 'return' [testlist]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _yield_stmt():
    """Parse a yield statement.

    ::

        yield_stmt: yield_expr

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _raise_stmt():
    """Parse a raise statement.

    ::

        raise_stmt: 'raise' [test [',' test [',' test]]]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_stmt():
    """Parse an import statement.

    ::

        import_stmt: import_name | import_from

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_name():
    """Parse an import name.

    ::

        import_name: 'import' dotted_as_names

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_from():
    """Parse an import from.

    ::

        import_from: ('from' ('.'* dotted_name | '.'+)
                      'import' ('*' | '(' import_as_names ')' | import_as_names))

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_as_name():
    """Parse an import as names.

    ::

        import_as_name: NAME ['as' NAME]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dotted_as_name():
    """Parse a dotted as name.

    ::

        dotted_as_name: dotted_name ['as' NAME]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_as_names():
    """Parse import as names.

    ::

        import_as_names: import_as_name (',' import_as_name)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dotted_as_names():
    """Parse dotted as names.

    ::

        dotted_as_names: dotted_as_name (',' dotted_as_name)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dotted_name():
    """Parse a dotted name.

    ::

        dotted_name: NAME ('.' NAME)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _global_stmt():
    """Parse a global statement.

    ::

        global_stmt: 'global' NAME (',' NAME)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _exec_stmt():
    """Parse an exec statement.

    ::

        exec_stmt: 'exec' expr ['in' test [',' test]]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _assert_stmt():
    """Parse an assert statement.

    ::

        assert_stmt: 'assert' test [',' test]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _compound_stmt():
    """Parse a compound statement.

    ::

        compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated

    Returns:
        list: A parse tree element
    """
    result = [symbol.compound_stmt]
  
    # Remember the last "good" position of the tokens generator
    parser.tokens, last_good_tokens = tee(parser.tokens)
    parser.tokens = peekable(parser.tokens)

    choices = [_while_stmt, _funcdef] # TODO
    subtree = None

    # Recursively descend a path. End of recursion is indicated by a ParserError
    # from the child path. When a child path has failed, "roll back" the tokens-
    # generator to the last good position
    for choice in choices:
        try:
            subtree = choice()
            break # break this loop if choice matches
        except ParserError:
            # restore last good position
            parser.tokens = peekable(last_good_tokens)

    if not subtree:
        raise ParserError("Expecting: if_stmt | while_stmt | for_stmt | "
            "try_stmt | with_stmt | funcdef | classdef | decorated")
    
    result.append(subtree)

    return result

def _if_stmt():
    """Parse and if statement.

    ::

        if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _while_stmt():
    """Parse a while statement.

    ::

        while_stmt: 'while' test ':' suite ['else' ':' suite]

    Returns:
        list: A parse tree element
    """
    result = [symbol.while_stmt]
    
    if not (parser.tokens.peek()[0] == token.NAME and parser.tokens.peek()[1] == "while"):
        raise ParserError("Expecting `while'")
    result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
    parser.tokens.next()

    result.append(_test())

    if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ":"):
        raise ParserError("Expecting `:'")
    result.append((token.COLON, ":"))
    parser.tokens.next()

    result.append(_suite())

    if parser.tokens.peek()[0] == token.NAME and parser.tokens.peek()[1] == "else":
        parser.tokens.next()
        
        if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ":"):
            raise ParserError("Expecting `:'")
            
        result.append(_suite())

    return result

def _for_stmt():
    """Parse a for statement.

    ::

        for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _try_stmt():
    """Parse a try statement.

    ::

        try_stmt: ('try' ':' suite
                   ((except_clause ':' suite)+
                    ['else' ':' suite]
                    ['finally' ':' suite] |
                   'finally' ':' suite))

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _with_stmt():
    """Parse a with statement.

    ::

        with_stmt: 'with' with_item (',' with_item)*  ':' suite

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _with_item():
    """Parse a with item.

    ::

        with_item: test ['as' expr]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _except_clause():
    """Parse an except clause.

    ::

        except_clause: 'except' [test [('as' | ',') test]]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _suite():
    """Parse a suite.

    ::

        suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT

    Returns:
        list: A parse tree element
    """
    result = [symbol.suite]

    if parser.tokens.peek()[0] == token.NEWLINE:
        result.append((token.NEWLINE, ""))
        parser.tokens.next()

        if parser.tokens.peek()[0] != token.INDENT:
            raise ParserError("Expecting INDENT")
        result.append((token.INDENT, ''))
        parser.tokens.next()
        
        try:
            while parser.tokens.peek()[0] != token.DEDENT:
                result.append(_stmt())
        except StopIteration:
            pass # raise "Expecting DEDENT" in next block

        if parser.tokens.peek()[0] != token.DEDENT:
            raise ParserError("Expecting DEDENT")
        result.append((token.DEDENT, ''))

        parser.tokens.next()
    else:
        raise NotImplementedError

    return result

def _testlist_safe():
    """Parse a testlist safe.

    ::

        testlist_safe: old_test [(',' old_test)+ [',']]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _old_test():
    """Parse an old test.

    ::

        old_test: or_test | old_lambdef

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _old_lambdef():
    """Parse an old lambda definition.

    ::

        old_lambdef: 'lambda' [varargslist] ':' old_test

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _test():
    """Parse a test statement.

    ::

        test: or_test ['if' or_test 'else' test] | lambdef

    Returns:
        list: A parse tree element
    """
    result = [symbol.test]
    result.append(_or_test())
    
    # TODO if/lambdef
    
    return result

def _or_test():
    """Parse an or_test statement

    ::

        or_test: and_test ('or' and_test)*

    Returns:
        list: A parse tree element
    """
    result = [symbol.or_test]
    result.append(_and_test())

    # TODO or and_test
    
    return result

def _and_test():
    """Parse an and test statement.

    ::

        and_test: not_test ('and' not_test)*

    Returns:
        list: A parse tree element
    """
    result = [symbol.and_test]
    result.append(_not_test())
    
    # TODO and not_test
    
    return result

def _not_test():
    """Parse a not test statement.

    ::

        not_test: 'not' not_test | comparison

    Return:
        list: A parse tree element
    """
    result = [symbol.not_test]
    result.append(_comparison())

    # TODO: not not_test
    
    return result

def _comparison():
    """Parse a comparison.

    ::

        comparison: expr (comp_op expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.comparison]
    
    result.append(_expr())

    # Remember the last "good" position of the tokens generator
    parser.tokens, last_good_tokens = tee(parser.tokens)
    parser.tokens = peekable(parser.tokens)

    # Recursively descend a path. End of recursion is indicated by a ParserError
    # from the child path. When a child path has failed, "roll back" the tokens-
    # generator to the last good position
    try:
        comp_op = _comp_op()
        expr = _expr()

        # both paths were successful -> add to result
        result.append(comp_op)
        result.append(expr)
    except ParserError:
        # restore last good position
        parser.tokens = peekable(last_good_tokens)

    # TODO: implement loop

    return result

def _comp_op():
    """Parse a compare operator statement.

    ::

        comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'

    Return:
        list: A parse tree element
    """
    result = [symbol.comp_op]

    parser_error = ParserError("Expecting: '<'|'>'|'=='|'>='|'<='|'<>'|'!='"
        "|'in'|'not' 'in'|'is'|'is' 'not'")

    if parser.tokens.peek()[0] == token.OP:
        if parser.tokens.peek()[1] == "<":
            result.append((token.LESS, "<"))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == ">":
            result.append((token.GREATER, ">"))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == "==":
            result.append((token.EQEQUAL, "=="))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == ">=":
            result.append((token.GREATEREQUAL, ">="))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == "<=":
            result.append((token.LESSEQUAL, "<="))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == "<>":
            result.append((token.NOTEQUAL, "<>"))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == "!=":
            result.append((token.NOTEQUAL, "!="))
            parser.tokens.next()
        else:
            raise parser_error
    elif parser.tokens.peek()[0] == token.NAME:
        if parser.tokens.peek()[1] == "in":
            result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
            parser.tokens.next()
        elif parser.tokens.peek()[1] == "not":
            result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
            parser.tokens.next()
            if parser.tokens.peek()[0] == "in":
                result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
                parser.tokens.next()
            else:
                raise parser_error
        elif parser.tokens.peek()[1] == "is":
            result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
            parser.tokens.next()
            if parser.tokens.peek()[0] == "not":
                result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
                parser.tokens.next()
    else:
        raise parser_error

    return result

def _expr():
    """Parse an expression statement.

    ::

        expr: xor_expr ('|' xor_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.expr]
    result.append(_xor_expr())
    
    # TODO | xor_expr
    
    return result

def _xor_expr():
    """Parse an xor expression statement.

    ::

        xor_expr: and_expr ('^' and_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.xor_expr]
    result.append(_and_expr())

    # TODO ^ and_exr
    
    return result

def _and_expr():
    """Parse an and expression statement.

    ::

        and_expr: shift_expr ('&' shift_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.and_expr]
    result.append(_shift_expr())
    
    # TODO
    
    return result

def _shift_expr():
    """Parse a shift_expr statement

    ::

        shift_expr: arith_expr (('<<'|'>>') arith_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.shift_expr]
    result.append(_arith_expr())
    
    # TODO
    
    return result

def _arith_expr():
    """Parse an arithmetic expression statement.

    ::

        arith_expr: term (('+'|'-') term)*

    Return:
        list: A parse tree element
    """
    result = [symbol.arith_expr]
    result.append(_term())
    
    if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "+":
        result.append((token.PLUS, "+"))
        parser.tokens.next()
        result.append(_term())
    elif parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "-":
        result.append((token.MINUS, "+"))
        parser.tokens.next()
        result.append(_term())
    
    # TODO: repetition

    return result

def _term():
    """Parse a term statement.

    ::

        term: factor (('*'|'/'|'%'|'//') factor)*

    Return:
        list: A parse tree element
    """
    result = [symbol.term]
    result.append(_factor())
    
    # TODO
    
    return result
    
def _factor():
    """Parse a factor statement.

    ::

        factor: ('+'|'-'|'~') factor | power

    Returns:
        list: A parse tree element
    """
    result = [symbol.factor]
    
    # TODO
    
    result.append(_power())
    return result
    
def _power():
    """Parse a power statement.

    ::

        power: atom trailer* ['**' factor]

    Returns:
        list: A parse tree element
    """
    result = [symbol.power]
    result.append(_atom())

    if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "(":
        result.append(_trailer())
    
    # TODO factor, multiple trailers
    
    return result

def _atom():
    """Parse an atom statement.

    ::

        atom: ('(' [yield_expr|testlist_comp] ')' |
               '[' [listmaker] ']' |
               '{' [dictorsetmaker] '}' |
               '`' testlist1 '`' |
               NAME | NUMBER | STRING+)

    Returns:
        list: A parse tree element
    """
    result = [symbol.atom]
    
    keywords = ["and", "as", "assert", "break", "class", "continue", "def",
        "del", "elif", "else", "except", "exec", "finally", "for", "from",
        "global", "if", "import", "in", "is", "lambda", "not", "or", "pass",
        "print", "raise", "return", "try", "while", "with", "yield"]

    if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "(":
        result.append((token.LPAR, "("))
        parser.tokens.next()
        
        # TODO yield_expr
        result.append(_testlist_comp())
        
        if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "("):
            result.append((token.RPAR, ")"))
            parser.tokens.next()
    elif parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "[":
        raise NotImplementedError
    elif parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "{":
        raise NotImplementedError
    elif parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "`":
        raise NotImplementedError
    elif parser.tokens.peek()[0] == token.NUMBER:
        result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
        parser.tokens.next()
    elif parser.tokens.peek()[0] == token.NAME:
        if parser.tokens.peek()[1] in keywords:
            raise ParserError # keywords cannot appear here
        result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
        parser.tokens.next()
    elif parser.tokens.peek()[0] == token.STRING:
        result.append((parser.tokens.peek()[0], parser.tokens.peek()[1]))
        parser.tokens.next()
    else:
        raise ParserError("Expecting: ('(' [yield_expr|testlist_comp] ')' |\n"
            "'[' [listmaker] ']' |\n"
            "'{' [dictorsetmaker] '}' |\n"
            "'`' testlist1 '`' |\n"
            "NAME | NUMBER | STRING+)")
        
    return result
    
def _listmaker():
    """Parse a listmaker statement.

    ::

        listmaker: test ( list_for | (',' test)* [','] )

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist_comp():
    """Parse a testlist comp statement.

    ::

        testlist_comp: test ( comp_for | (',' test)* [','] )

    Returns:
        list: A parse tree element
    """
    result = [symbol.test]
    
    result.append(_test())
    
    # TODO
    
    return result

def _lambdef():
    """Parse a lambda definition.

    ::

        lambdef: 'lambda' [varargslist] ':' test

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _trailer():
    """Parse a trailer.

    ::

        trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME

    Returns:
        list: A parse tree element
    """
    result = [symbol.trailer]

    if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == "(":
        result.append((token.LPAR, "("))
        parser.tokens.next()
        
        # TODO: optional
        result.append(_arglist())
        
        if not (parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ")"):
            raise ParserError("Expecting `)'")
        result.append((token.RPAR, ")"))
        parser.tokens.next()
    else:
        raise NotImplementedError
    
    return result

def _subscriptlist():
    """Parse a subscriptlist.

    ::

        subscriptlist: subscript (',' subscript)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _subscript():
    """Parse a subscript.

    ::

        subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _sliceop():
    """Parse a slice operation.

    ::

        sliceop: ':' [test]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _exprlist():
    """Parse an expression list.

    ::

        exprlist: expr (',' expr)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist():
    """Parse a testlist.

    ::

        testlist: test (',' test)* [',']

    Returns:
        list: A parse tree element
    """
    result = [symbol.testlist]
    
    result.append(_test())
    
    while parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ",":
        result.append((token.COMMA, ","))
        parser.tokens.next()
        result.append(_test())

    if parser.tokens.peek()[0] == token.OP and parser.tokens.peek()[1] == ",":
        parser.tokens.next()
    
    return result

def _dictorsetmaker():
    """Parse a dict or set maker statement.

    ::

        dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
                          (test (comp_for | (',' test)* [','])) )

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _classdef():
    """Parse a class definition.

    ::

            classdef: 'class' NAME ['(' [testlist] ')'] ':' suite

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _arglist():
    """Parse an argument list.

    ::

        arglist: (argument ',')* (argument [',']
                                 |'*' test (',' argument)* [',' '**' test]
                                 |'**' test)

    Returns:
        list: A parse tree element
    """
    result = [symbol.arglist]
    
    result.append(_argument())
    
    # TODO

    return result

def _argument():
    """Parse an argument.

    ::

        argument: test [comp_for] | test '=' test

    Returns:
        list: A parse tree element
    """
    result = [symbol.argument]
    
    result.append(_test())
    
    # TODO
    
    return result

def _list_iter():
    """Parse a list iteration.

    ::

        list_iter: list_for | list_if

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _list_for():
    """Parse a list for.

    ::

        list_for: 'for' exprlist 'in' testlist_safe [list_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _list_if():
    """Parse a list if.

    ::

        list_if: 'if' old_test [list_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _comp_iter():
    """Parse a comp iter.

    ::

        comp_iter: comp_for | comp_if

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _comp_for():
    """Parse a comp for.

    ::

        comp_for: 'for' exprlist 'in' or_test [comp_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _comp_if():
    """Parse a comp if.

    ::

        comp_if: 'if' old_test [comp_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist1():
    """Parse a testlist1.

    ::

        testlist1: test (',' test)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _encoding_decl():
    """Parse an encoding declaration.

    ::

        encoding_decl: NAME

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _yield_expr():
    """Parse a yield expression.

    ::

        yield_expr: 'yield' [testlist]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError