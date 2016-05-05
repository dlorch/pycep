# -*- coding: utf-8 -*-
# pylint: disable=C0302

from __future__ import absolute_import
import parser
import token
import tokenize
import symbol
from StringIO import StringIO
import pycep.tokenizer

def suite(source, totuple=False):
    """The parser takes a string containing the source code as an input and
    returns a parse tree.

    >>> import pycep.parser
    >>> st = pycep.parser.suite('print "Hello, world!"')
    >>> st.totuple()
    (257, (267, (268, (269, (272, (1, 'print'), (304, (305, (306, (307, (308, (310, (311, (312, (313, (314, (315, \
    (316, (317, (318, (3, '"Hello, world!"'))))))))))))))))), (4, ''))), (4, ''), (0, ''))

    Formally, this is an LL(2) (Left-to-right, Leftmost derivation with two-token lookahead), recursive-descent parser.

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
        * LL Parser: https://en.wikipedia.org/wiki/LL_parser
        * Recursive-Descent Parser: https://en.wikipedia.org/wiki/Recursive_descent_parser
    """

    tokens = TokenIterator(pycep.tokenizer.generate_tokens(StringIO(source).readline))
    result = _file_input(tokens)

    if totuple:
        # recursively convert list-of-lists to tuples-of-tuples
        def listit(tup):
            if isinstance(tup, (list, tuple)):
                return tuple([listit(el) for el in tup])
            else:
                return tup

        return listit(result)
    else:
        return parser.sequence2st(result)

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
        while not tokens.check(token.ENDMARKER):
            if tokens.check(token.NEWLINE):
                result.append(tokens.accept(token.NEWLINE, result_name=""))
            else:
                result.append(_stmt(tokens))
    except StopIteration:
        pass # raise "Expecting ENDMARKER" in next block

    # No trailing NEWLINE defined in grammar, but Python's parser always
    # appends it, thus imitate this behavior
    result.append((token.NEWLINE, ""))

    result.append(tokens.accept(token.ENDMARKER, result_name=""))

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

    result.append(tokens.accept(token.OP, "@", result_token=token.AT))
    result.append(_dotted_name(tokens))

    if tokens.check(token.OP, "("):
        result.append(tokens.accept(token.OP, "(", result_token=token.LPAR))

        if not tokens.check(token.OP, ")"):
            result.append(_arglist(tokens))

        result.append(tokens.accept(token.OP, ")", result_token=token.RPAR))

    result.append(tokens.accept(token.NEWLINE, result_name=""))

    return result

def _decorators(tokens):
    """Parse a list of decorators.

    ::

        decorators: decorator+
    """
    result = [symbol.decorators]

    result.append(_decorator(tokens))

    while tokens.check(token.OP, "@"):
        result.append(_decorator(tokens))

    return result

def _decorated(tokens):
    """Parse a decorated statement.

    ::

        decorated: decorators (classdef | funcdef)
    """
    result = [symbol.decorated]

    result.append(_decorators(tokens))

    if tokens.check(token.NAME, "class"):
        result.append(_classdef(tokens))
    elif tokens.check(token.NAME, "def"):
        result.append(_funcdef(tokens))
    else:
        tokens.error("Expecting (classdef | funcdef)")

    return result

def _funcdef(tokens):
    """Parse a function definition.

    ::

        funcdef: 'def' NAME parameters ':' suite
    """
    result = [symbol.funcdef]

    result.append(tokens.accept(token.NAME, "def"))
    result.append(tokens.accept(token.NAME))
    result.append(_parameters(tokens))
    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    return result

def _parameters(tokens):
    """Parse a parameter list.

    ::

        parameters: '(' [varargslist] ')'
    """
    result = [symbol.parameters]

    result.append(tokens.accept(token.OP, "(", result_token=token.LPAR))

    if not tokens.check(token.OP, ")"):
        result.append(_varargslist(tokens))

    result.append(tokens.accept(token.OP, ")", result_token=token.RPAR))

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
    # TODO the implementation below is incomplete

    result.append(_fpdef(tokens))

    if tokens.check(token.OP, "="):
        result.append(tokens.accept(token.OP, "=", result_token=token.EQUAL))
        result.append(_test(tokens))

    while tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
        result.append(_fpdef(tokens))

        if tokens.check(token.OP, "="):
            result.append(tokens.accept(token.OP, "=", result_token=token.EQUAL))
            result.append(_test(tokens))

    if tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

    return result

def _fpdef(tokens):
    """Parse function parameter definition.

    ::

        fpdef: NAME | '(' fplist ')'
    """
    result = [symbol.fpdef]

    if tokens.check(token.NAME):
        result.append(tokens.accept(token.NAME))
    elif tokens.check(token.OP, "("):
        result.append(tokens.accept(token.OP, "("))
        result.append(_fplist(tokens))
        result.append(tokens.accept(token.OP, ")"))
    else:
        tokens.error("Expecting NAME | '(' fplist ')'")

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

    if tokens.check(token.NAME, ("if", "while", "for", "try", "with", "def", "class")) or \
        tokens.check(token.OP, "@"):

        result.append(_compound_stmt(tokens))
    else:
        result.append(_simple_stmt(tokens))

    return result

def _simple_stmt(tokens):
    """Parse a simple statement.

    ::

        simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
    """
    result = [symbol.simple_stmt]

    result.append(_small_stmt(tokens))

    while tokens.check(token.OP, ";"):
        result.append(tokens.accept(token.OP, ";", result_token=token.SEMI))
        result.append(_small_stmt(tokens))

    if tokens.check(token.OP, ";"):
        result.append(tokens.accept(token.OP, ";", result_token=token.SEMI))

    # trailing NEWLINE is mandatory according to grammar, but in Python's parser
    # it is optional, thus imitate this behavior
    if tokens.check(token.NEWLINE):
        result.append(tokens.accept(token.NEWLINE, result_name=""))
    else:
        result.append((token.NEWLINE, ""))

    return result

def _small_stmt(tokens):
    """Parse a small statement.

    ::

        small_stmt: (expr_stmt | print_stmt | del_stmt | pass_stmt | flow_stmt |
                     import_stmt | global_stmt | exec_stmt | assert_stmt)
    """
    result = [symbol.small_stmt]

    if tokens.check(token.NAME, "print"):
        result.append(_print_stmt(tokens))
    elif tokens.check(token.NAME, "del"):
        result.append(_del_stmt(tokens))
    elif tokens.check(token.NAME, "pass"):
        result.append(_pass_stmt(tokens))
    elif tokens.check(token.NAME, "break") or tokens.check(token.NAME, "continue") or \
        tokens.check(token.NAME, "return") or tokens.check(token.NAME, "raise") or \
        tokens.check(token.NAME, "yield"):
        result.append(_flow_stmt(tokens))
    elif tokens.check(token.NAME, "import"):
        result.append(_import_stmt(tokens))
    elif tokens.check(token.NAME, "global"):
        result.append(_global_stmt(tokens))
    elif tokens.check(token.NAME, "exec"):
        result.append(_exec_stmt(tokens))
    elif tokens.check(token.NAME, "assert"):
        result.append(_assert_stmt(tokens))
    elif tokens.check(token.OP, ("+", "-", "~")) or \
        tokens.check(token.NUMBER) or tokens.check(token.STRING) or \
        tokens.check(token.NAME): # make sure the "catchall" tokens.check(token.NAME) belongs to the last condition
        result.append(_expr_stmt(tokens))
    else:
        tokens.error("Expecting (expr_stmt | print_stmt  | del_stmt | "
                     "pass_stmt | flow_stmt | import_stmt | global_stmt | exec_stmt | "
                     "assert_stmt)")

    return result

def _expr_stmt(tokens):
    """Parse an expr stmt.

    ::

        expr_stmt: testlist (augassign (yield_expr|testlist) |
                             ('=' (yield_expr|testlist))*)
    """
    result = [symbol.expr_stmt]

    result.append(_testlist(tokens))

    if tokens.check(token.OP, ("+=", "-=", "*=", "/=", "%=", "&=", "|=", \
                               "^=", "<<=", ">>=", "**=", "//=")):

        result.append(_augassign(tokens))

        if tokens.check(token.NAME, "yield"):
            result.append(_yield_expr(tokens))
        else:
            result.append(_testlist(tokens))

    else:
        while tokens.check(token.OP, "="):
            result.append(tokens.accept(token.OP, "=", result_token=token.EQUAL))

            if tokens.check(token.NAME, "yield"):
                result.append(_yield_expr(tokens))
            else:
                result.append(_testlist(tokens))

    return result

# pylint: disable=R0912
def _augassign(tokens):
    """Parse an augmented assign statement.

    ::

        augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
        '<<=' | '>>=' | '**=' | '//=')
    """
    result = [symbol.augassign]

    if tokens.check(token.OP, "+="):
        result.append(tokens.accept(token.OP, "+=", result_token=token.PLUSEQUAL))
    elif tokens.check(token.OP, "-="):
        result.append(tokens.accept(token.OP, "-=", result_token=token.MINEQUAL))
    elif tokens.check(token.OP, "*="):
        result.append(tokens.accept(token.OP, "*=", result_token=token.STAREQUAL))
    elif tokens.check(token.OP, "/="):
        result.append(tokens.accept(token.OP, "/=", result_token=token.SLASHEQUAL))
    elif tokens.check(token.OP, "%="):
        result.append(tokens.accept(token.OP, "%=", result_token=token.PERCENTEQUAL))
    elif tokens.check(token.OP, "&="):
        result.append(tokens.accept(token.OP, "&=", result_token=token.AMPEREQUAL))
    elif tokens.check(token.OP, "|="):
        result.append(tokens.accept(token.OP, "|=", result_token=token.VBAREQUAL))
    elif tokens.check(token.OP, "^="):
        result.append(tokens.accept(token.OP, "^=", result_token=token.CIRCUMFLEXEQUAL))
    elif tokens.check(token.OP, "<<="):
        result.append(tokens.accept(token.OP, "<<=", result_token=token.LEFTSHIFTEQUAL))
    elif tokens.check(token.OP, ">>="):
        result.append(tokens.accept(token.OP, ">>=", result_token=token.RIGHTSHIFTEQUAL))
    elif tokens.check(token.OP, "**="):
        result.append(tokens.accept(token.OP, "**=", result_token=token.DOUBLESTAREQUAL))
    elif tokens.check(token.OP, "//="):
        result.append(tokens.accept(token.OP, "//=", result_token=token.DOUBLESLASHEQUAL))
    else:
        tokens.error()

    return result

def _print_stmt(tokens):
    """Parse a print statement.

    ::

        print_stmt: 'print' ( [ test (',' test)* [','] ] |
                              '>>' test [ (',' test)+ [','] ] )
    """
    # This grammar is *not* left-factored and has to be rewritten as follows
    # (<=> denotes "if and only if", ε denotes the empty string). Derivation:
    #
    #   print_stmt: 'print' ( [ test (',' test)* [','] ] |
    #                         '>>' test [ (',' test)+ [','] ] )
    #   <=>
    #   print_stmt: 'print' ( ε |
    #                         test (',' test)* [','] |
    #                         '>>' test [ (',' test)+ [','] ] )
    #   <=>
    #   print_stmt: 'print' [ test (',' test)* [','] |
    #                         '>>' test [ (',' test)+ [','] ] ]
    #
    result = [symbol.print_stmt]

    result.append(tokens.accept(token.NAME, "print"))

    if tokens.check_test():
        result.append(_test(tokens))

        while tokens.check(token.OP, ",") and tokens.check_test(lookahead=2):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
            result.append(_test(tokens))

        if tokens.check(token.OP, ","):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

    elif tokens.check(token.OP, ">>"):
        result.append(tokens.accept(token.OP, ">>", result_token=token.RIGHTSHIFT))
        result.append(_test(tokens))

        if tokens.check(token.OP, ","):
            while tokens.check(token.OP, ",") and tokens.check_test(lookahead=2):
                result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
                result.append(_test(tokens))

            if tokens.check(token.OP, ","):
                result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

    return result

def _del_stmt(tokens):
    """Parse a delete statement.

    ::

        del_stmt: 'del' exprlist
    """
    result = [symbol.del_stmt]

    result.append(tokens.accept(token.NAME, "del"))
    result.append(_exprlist(tokens))

    return result

def _pass_stmt(tokens):
    """Parse a pass statement.

    ::

        pass_stmt: 'pass'
    """
    result = [symbol.pass_stmt]

    result.append(tokens.accept(token.NAME, "pass"))

    return result

def _flow_stmt(tokens):
    """Parse a flow statement.

    ::

        flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
    """
    result = [symbol.flow_stmt]

    if tokens.check(token.NAME, "break"):
        result.append(_break_stmt(tokens))
    elif tokens.check(token.NAME, "continue"):
        result.append(_continue_stmt(tokens))
    elif tokens.check(token.NAME, "return"):
        result.append(_return_stmt(tokens))
    elif tokens.check(token.NAME, "raise"):
        result.append(_raise_stmt(tokens))
    elif tokens.check(token.NAME, "yield"):
        result.append(_yield_stmt(tokens))
    else:
        tokens.error("Expecting: break_stmt | continue_stmt | return_stmt | "
                     "raise_stmt | yield_stmt")

    return result

def _break_stmt(tokens):
    """Parse a break statement.

    ::

        break_stmt: 'break'
    """
    result = [symbol.break_stmt]

    result.append(tokens.accept(token.NAME, "break"))

    return result

def _continue_stmt(tokens):
    """Parse a continue statement.

    ::

        continue_stmt: 'continue'
    """
    result = [symbol.continue_stmt]

    result.append(tokens.accept(token.NAME, "continue"))

    return result

def _return_stmt(tokens):
    """Parse a return statement.

    ::

        return_stmt: 'return' [testlist]
    """
    result = [symbol.return_stmt]

    result.append(tokens.accept(token.NAME, "return"))

    if tokens.check_test():
        result.append(_testlist(tokens))

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
    result = [symbol.raise_stmt]

    result.append(tokens.accept(token.NAME, "raise"))

    if tokens.check_test():
        result.append(_test(tokens))

        if tokens.check(token.OP, ","):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
            result.append(_test(tokens))

            if tokens.check(token.OP, ","):
                result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
                result.append(_test(tokens))

    return result

def _import_stmt(tokens):
    """Parse an import statement.

    ::

        import_stmt: import_name | import_from
    """
    result = [symbol.import_stmt]

    # TODO
    result.append(_import_name(tokens))

    return result

def _import_name(tokens):
    """Parse an import name.

    ::

        import_name: 'import' dotted_as_names
    """
    result = [symbol.import_name]

    result.append(tokens.accept(token.NAME, "import"))
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

    if tokens.check(token.NAME, "as"):
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

    if tokens.check(token.OP, ","):
        raise NotImplementedError

    return result

def _dotted_name(tokens):
    """Parse a dotted name.

    ::

        dotted_name: NAME ('.' NAME)*
    """
    result = [symbol.dotted_name]

    result.append(tokens.accept(token.NAME))

    if tokens.check(token.OP, "."):
        raise NotImplementedError

    return result

def _global_stmt(tokens):
    """Parse a global statement.

    ::

        global_stmt: 'global' NAME (',' NAME)*
    """
    result = [symbol.global_stmt]

    result.append(tokens.accept(token.NAME, "global"))
    result.append(tokens.accept(token.NAME))

    while tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, result_token=token.COMMA))
        result.append(tokens.accept(token.NAME))

    return result

def _exec_stmt(tokens):
    """Parse an exec statement.

    ::

        exec_stmt: 'exec' expr ['in' test [',' test]]
    """
    result = [symbol.exec_stmt]

    result.append(tokens.accept(token.NAME, "exec"))
    result.append(_expr(tokens))

    if tokens.check(token.NAME, "in"):
        result.append(tokens.accept(token.NAME, "in"))
        result.append(_test(tokens))

        if tokens.check(token.OP, ","):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
            result.append(_test(tokens))

    return result

def _assert_stmt(tokens):
    """Parse an assert statement.

    ::

        assert_stmt: 'assert' test [',' test]
    """
    result = [symbol.assert_stmt]

    result.append(tokens.accept(token.NAME, "assert"))
    result.append(_test(tokens))

    if tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
        result.append(_test(tokens))

    return result

def _compound_stmt(tokens):
    """Parse a compound statement.

    ::

        compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
    """
    result = [symbol.compound_stmt]

    if tokens.check(token.NAME, "if"):
        result.append(_if_stmt(tokens))
    elif tokens.check(token.NAME, "while"):
        result.append(_while_stmt(tokens))
    elif tokens.check(token.NAME, "for"):
        result.append(_for_stmt(tokens))
    elif tokens.check(token.NAME, "try"):
        result.append(_try_stmt(tokens))
    elif tokens.check(token.NAME, "with"):
        result.append(_with_stmt(tokens))
    elif tokens.check(token.NAME, "def"):
        result.append(_funcdef(tokens))
    elif tokens.check(token.NAME, "class"):
        result.append(_classdef(tokens))
    elif tokens.check(token.OP, "@"):
        result.append(_decorated(tokens))
    else:
        tokens.error("Expecting: if_stmt | while_stmt | for_stmt | "
                     "try_stmt | with_stmt | funcdef | classdef | decorated")

    return result

def _if_stmt(tokens):
    """Parse and if statement.

    ::

        if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
    """
    result = [symbol.if_stmt]

    result.append(tokens.accept(token.NAME, "if"))
    result.append(_test(tokens))
    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    if tokens.check(token.NAME, "elif"):
        raise NotImplementedError

    if tokens.check(token.NAME, "else"):
        result.append(tokens.accept(token.NAME, "else"))
        result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
        result.append(_suite(tokens))

    return result

def _while_stmt(tokens):
    """Parse a while statement.

    ::

        while_stmt: 'while' test ':' suite ['else' ':' suite]
    """
    result = [symbol.while_stmt]

    result.append(tokens.accept(token.NAME, "while"))
    result.append(_test(tokens))
    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    if tokens.check(token.NAME, "else"):
        result.append(tokens.accept(token.NAME, "else"))
        result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
        result.append(_suite(tokens))

    return result

def _for_stmt(tokens):
    """Parse a for statement.

    ::

        for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
    """
    result = [symbol.for_stmt]

    result.append(tokens.accept(token.NAME, "for"))
    result.append(_exprlist(tokens))
    result.append(tokens.accept(token.NAME, "in"))
    result.append(_testlist(tokens))
    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    if tokens.check(token.NAME, "else"):
        result.append(tokens.accept(token.NAME, "else"))
        result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
        result.append(_suite(tokens))

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

    result.append(tokens.accept(token.NAME, "try"))
    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    if tokens.check(token.NAME, "except"):
        while tokens.check(token.NAME, "except"):
            result.append(_except_clause(tokens))
            result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
            result.append(_suite(tokens))

        if tokens.check(token.NAME, "else"):
            result.append(tokens.accept(token.NAME, "else"))
            result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
            result.append(_suite(tokens))

        if tokens.check(token.NAME, "finally"):
            result.append(tokens.accept(token.NAME, "finally"))
            result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
            result.append(_suite(tokens))

    elif tokens.check(token.NAME, "finally"):
        result.append(tokens.accept(token.NAME, "finally"))
        result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
        result.append(_suite(tokens))

    else:
        tokens.error("Expecting ((except_clause ':' suite)+ "
                     "['else' ':' suite] "
                     "['finally' ':' suite] | "
                     "'finally' ':' suite)")

    return result

def _with_stmt(tokens):
    """Parse a with statement.

    ::

        with_stmt: 'with' with_item (',' with_item)*  ':' suite
    """
    result = [symbol.with_stmt]

    result.append(tokens.accept(token.NAME, "with"))
    result.append(_with_item(tokens))

    while tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
        result.append(_with_item(tokens))

    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    return result

def _with_item(tokens):
    """Parse a with item.

    ::

        with_item: test ['as' expr]
    """
    result = [symbol.with_item]

    result.append(_test(tokens))

    if tokens.check(token.NAME, "as"):
        result.append(tokens.accept(token.NAME, "as"))
        result.append(_expr(tokens))

    return result

def _except_clause(tokens):
    """Parse an except clause.

    ::

        except_clause: 'except' [test [('as' | ',') test]]
    """
    result = [symbol.except_clause]

    result.append(tokens.accept(token.NAME, "except"))

    if tokens.check_test():
        result.append(_test(tokens))

        if tokens.check(token.NAME, "as") or tokens.check(token.OP, ","):
            if tokens.check(token.NAME, "as"):
                result.append(tokens.accept(token.NAME, "as"))
            elif tokens.check(token.OP, ","):
                result.append(tokens.accept(token.OP, ","))
            else:
                tokens.error("Expecting ('as' | ',')")

            result.append(_test(tokens))

    return result

def _suite(tokens):
    """Parse a suite.

    ::

        suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    """
    result = [symbol.suite]

    if tokens.check(token.NEWLINE):
        result.append(tokens.accept(token.NEWLINE, result_name=""))
        result.append(tokens.accept(token.INDENT, result_name=""))

        try:
            while not tokens.check(token.DEDENT):
                result.append(_stmt(tokens))

        except StopIteration:
            pass # raise "Expecting DEDENT" in next block

        result.append(tokens.accept(token.DEDENT, result_name=""))
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

    if tokens.check(token.NAME, "lambda"):
        result.append(_lambdef(tokens))
    else:
        result.append(_or_test(tokens))

        if tokens.check(token.NAME, "if"):
            result.append(tokens.accept(token.NAME, "if"))
            result.append(_or_test(tokens))
            result.append(tokens.accept(token.NAME, "else"))
            result.append(_test(tokens))

    return result

def _or_test(tokens):
    """Parse an or_test statement

    ::

        or_test: and_test ('or' and_test)*
    """
    result = [symbol.or_test]
    result.append(_and_test(tokens))

    while tokens.check(token.NAME, "or"):
        result.append(tokens.accept(token.NAME, "or"))
        result.append(_and_test(tokens))

    return result

def _and_test(tokens):
    """Parse an and test statement.

    ::

        and_test: not_test ('and' not_test)*
    """
    result = [symbol.and_test]
    result.append(_not_test(tokens))

    while tokens.check(token.NAME, "and"):
        result.append(tokens.accept(token.NAME, "and"))
        result.append(_not_test(tokens))

    return result

def _not_test(tokens):
    """Parse a not test statement.

    ::

        not_test: 'not' not_test | comparison
    """
    result = [symbol.not_test]

    if tokens.check(token.NAME, "not"):
        result.append(tokens.accept(token.NAME, "not"))
        result.append(_not_test(tokens))
    else:
        result.append(_comparison(tokens))

    return result

def _comparison(tokens):
    """Parse a comparison.

    ::

        comparison: expr (comp_op expr)*
    """
    result = [symbol.comparison]

    result.append(_expr(tokens))

    while tokens.check_comp_op():
        result.append(_comp_op(tokens))
        result.append(_expr(tokens))

    return result

def _comp_op(tokens):
    """Parse a compare operator statement.

    ::

        comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    """
    result = [symbol.comp_op]

    if tokens.check(token.OP, "<"):
        result.append(tokens.accept(token.OP, "<", result_token=token.LESS))
    elif tokens.check(token.OP, ">"):
        result.append(tokens.accept(token.OP, ">", result_token=token.GREATER))
    elif tokens.check(token.OP, "=="):
        result.append(tokens.accept(token.OP, "==", result_token=token.EQEQUAL))
    elif tokens.check(token.OP, ">="):
        result.append(tokens.accept(token.OP, ">=", result_token=token.GREATEREQUAL))
    elif tokens.check(token.OP, "<="):
        result.append(tokens.accept(token.OP, "<=", result_token=token.LESSEQUAL))
    elif tokens.check(token.OP, "<>"):
        result.append(tokens.accept(token.OP, "<>", result_token=token.NOTEQUAL))
    elif tokens.check(token.OP, "!="):
        result.append(tokens.accept(token.OP, "!=", result_token=token.NOTEQUAL))
    elif tokens.check(token.NAME, "in"):
        result.append(tokens.accept(token.NAME, "in"))
    elif tokens.check(token.NAME, "not") and tokens.check(token.NAME, "in", lookahead=2):
        result.append(tokens.accept(token.NAME, "not"))
        result.append(tokens.accept(token.NAME, "in"))
    elif tokens.check(token.NAME, "is"):
        result.append(tokens.accept(token.NAME, "is"))
        if tokens.check(token.NAME, "not"):
            result.append(tokens.accept(token.NAME, "not"))
    else:
        tokens.error("Expecting: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'")

    return result

def _expr(tokens):
    """Parse an expression statement.

    ::

        expr: xor_expr ('|' xor_expr)*
    """
    result = [symbol.expr]
    result.append(_xor_expr(tokens))

    while tokens.check(token.OP, "|"):
        result.append(tokens.accept(token.OP, "|", result_token=token.VBAR))
        result.append(_xor_expr(tokens))

    return result

def _xor_expr(tokens):
    """Parse an xor expression statement.

    ::

        xor_expr: and_expr ('^' and_expr)*
    """
    result = [symbol.xor_expr]
    result.append(_and_expr(tokens))

    while tokens.check(token.OP, "^"):
        result.append(tokens.accept(token.OP, "^", result_token=token.CIRCUMFLEX))
        result.append(_and_expr(tokens))

    return result

def _and_expr(tokens):
    """Parse an and expression statement.

    ::

        and_expr: shift_expr ('&' shift_expr)*
    """
    result = [symbol.and_expr]
    result.append(_shift_expr(tokens))

    while tokens.check(token.OP, "&"):
        result.append(tokens.accept(token.OP, "&", result_token=token.AMPER))
        result.append(_shift_expr(tokens))

    return result

def _shift_expr(tokens):
    """Parse a shift_expr statement

    ::

        shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    """
    result = [symbol.shift_expr]
    result.append(_arith_expr(tokens))

    while tokens.check(token.OP, "<<") or tokens.check(token.OP, ">>"):
        if tokens.check(token.OP, "<<"):
            result.append(tokens.accept(token.OP, "<<", result_token=token.LEFTSHIFT))
        elif tokens.check(token.OP, ">>"):
            result.append(tokens.accept(token.OP, ">>", result_token=token.RIGHTSHIFT))

        result.append(_arith_expr(tokens))

    return result

def _arith_expr(tokens):
    """Parse an arithmetic expression statement.

    ::

        arith_expr: term (('+'|'-') term)*
    """
    result = [symbol.arith_expr]
    result.append(_term(tokens))

    while tokens.check(token.OP, "+") or tokens.check(token.OP, "-"):
        if tokens.check(token.OP, "+"):
            result.append(tokens.accept(token.OP, "+", result_token=token.PLUS))
            result.append(_term(tokens))
        elif tokens.check(token.OP, "-"):
            result.append(tokens.accept(token.OP, "-", result_token=token.MINUS))
            result.append(_term(tokens))

    return result

def _term(tokens):
    """Parse a term statement.

    ::

        term: factor (('*'|'/'|'%'|'//') factor)*
    """
    result = [symbol.term]
    result.append(_factor(tokens))

    while tokens.check(token.OP, "*") or tokens.check(token.OP, "/") or \
          tokens.check(token.OP, "%") or tokens.check(token.OP, "//"):

        if tokens.check(token.OP, "*"):
            result.append(tokens.accept(token.OP, "*", result_token=token.STAR))
        elif tokens.check(token.OP, "/"):
            result.append(tokens.accept(token.OP, "/", result_token=token.SLASH))
        elif tokens.check(token.OP, "%"):
            result.append(tokens.accept(token.OP, "%", result_token=token.PERCENT))
        elif tokens.check(token.OP, "//"):
            result.append(tokens.accept(token.OP, "//", result_token=token.DOUBLESLASH))

        result.append(_factor(tokens))

    return result

def _factor(tokens):
    """Parse a factor statement.

    ::

        factor: ('+'|'-'|'~') factor | power
    """
    result = [symbol.factor]

    if tokens.check(token.OP, "+") or tokens.check(token.OP, "-") or tokens.check(token.OP, "~"):
        if tokens.check(token.OP, "+"):
            result.append(tokens.accept(token.OP, "+", result_token=token.PLUS))
        elif tokens.check(token.OP, "-"):
            result.append(tokens.accept(token.OP, "-", result_token=token.MINUS))
        elif tokens.check(token.OP, "~"):
            result.append(tokens.accept(token.OP, "~", result_token=token.TILDE))

        result.append(_factor(tokens))
    else:
        result.append(_power(tokens))

    return result

def _power(tokens):
    """Parse a power statement.

    ::

        power: atom trailer* ['**' factor]
    """
    result = [symbol.power]

    result.append(_atom(tokens))

    while tokens.check(token.OP, "(") or tokens.check(token.OP, "[") or tokens.check(token.OP, "."):
        result.append(_trailer(tokens))

    if tokens.check(token.OP, "**"):
        result.append(tokens.accept(token.OP, "**", result_token=token.DOUBLESTAR))
        result.append(_factor(tokens))

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

    keywords = ("and", "as", "assert", "break", "class", "continue", "def",
                "del", "elif", "else", "except", "exec", "finally", "for", "from",
                "global", "if", "import", "in", "is", "lambda", "not", "or", "pass",
                "print", "raise", "return", "try", "while", "with", "yield")

    if tokens.check(token.OP, "("):
        result.append(tokens.accept(token.OP, "(", result_token=token.LPAR))

        # TODO yield_expr
        result.append(_testlist_comp(tokens))

        result.append(tokens.accept(token.OP, ")", result_token=token.RPAR))
    elif tokens.check(token.OP, "["):
        result.append(tokens.accept(token.OP, "[", result_token=token.LSQB))

        if not tokens.check(token.OP, "]"):
            result.append(_listmaker(tokens))

        result.append(tokens.accept(token.OP, "]", result_token=token.RSQB))
    elif tokens.check(token.OP, "{"):
        raise NotImplementedError
    elif tokens.check(token.OP, "`"):
        raise NotImplementedError
    elif tokens.check(token.NUMBER):
        result.append(tokens.accept(token.NUMBER))
    elif tokens.check(token.NAME):
        if tokens.check(token.NAME, keywords):
            raise tokens.error("Keywords cannot appear here")
        result.append(tokens.accept(token.NAME))
    elif tokens.check(token.STRING):
        result.append(tokens.accept(token.STRING))
    else:
        tokens.error("Expecting: ('(' [yield_expr|testlist_comp] ')' | "
                     "'[' [listmaker] ']' | "
                     "'{' [dictorsetmaker] '}' | "
                     "'`' testlist1 '`' | "
                     "NAME | NUMBER | STRING+)")

    return result

def _listmaker(tokens):
    """Parse a listmaker statement.

    ::

        listmaker: test ( list_for | (',' test)* [','] )
    """
    result = [symbol.listmaker]

    result.append(_test(tokens))

    if tokens.check(token.NAME, "for"):
        result.append(_list_for(tokens))
    elif tokens.check(token.OP, ","):
        # this is a difficult one. the ',' we just matched could either be from
        # the subexpression (',' test)* or from the subexpression [','], since
        # the * operator from the first subexpression could be matching zero times.
        while tokens.check(token.OP, ",") and tokens.check_test(lookahead=2):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
            result.append(_test(tokens))

        if tokens.check(token.OP, ","):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

    return result

def _testlist_comp(tokens):
    """Parse a testlist comp statement.

    ::

        testlist_comp: test ( comp_for | (',' test)* [','] )
    """
    result = [symbol.testlist_comp]

    result.append(_test(tokens))

    if tokens.check(token.NAME, "for"):
        result.append(_comp_for(tokens))
    elif tokens.check(token.OP, ","):
        # this is a difficult one. the ',' we just matched could either be from
        # the subexpression (',' test)* or from the subexpression [','], since
        # the * operator from the first subexpression could be matching zero times.
        while tokens.check(token.OP, ",") and tokens.check_test(lookahead=2):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
            result.append(_test(tokens))

        if tokens.check(token.OP, ","):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

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

    if tokens.check(token.OP, "("):
        result.append(tokens.accept(token.OP, "(", result_token=token.LPAR))

        if not tokens.check(token.OP, ")"):
            result.append(_arglist(tokens))

        result.append(tokens.accept(token.OP, ")", result_token=token.RPAR))
    elif tokens.check(token.OP, "["):
        result.append(tokens.accept(token.OP, "[", result_token=token.LSQB))
        result.append(_subscriptlist(tokens))
        result.append(tokens.accept(token.OP, "]", result_token=token.RSQB))
    elif tokens.check(token.OP, "."):
        result.append(tokens.accept(token.OP, ".", result_token=token.DOT))
        result.append(tokens.accept(token.NAME))
    else:
        tokens.error("Expecting '(', '[' or '.'")

    return result

def _subscriptlist(tokens):
    """Parse a subscriptlist.

    ::

        subscriptlist: subscript (',' subscript)* [',']
    """
    result = [symbol.subscriptlist]

    result.append(_subscript(tokens))

    if tokens.check(token.OP, ","):
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

    if tokens.check(token.OP, ":"):
        result.append(tokens.accept(token.OP, ":", result_token=token.COLON))

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

    while tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
        result.append(_expr(tokens))

    if tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

    return result

def _testlist(tokens):
    """Parse a testlist.

    ::

        testlist: test (',' test)* [',']
    """
    result = [symbol.testlist]

    result.append(_test(tokens))

    while tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
        result.append(_test(tokens))

    if tokens.check(token.OP, ","):
        result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

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

    result.append(tokens.accept(token.NAME, "class"))
    result.append(tokens.accept(token.NAME))

    if tokens.check(token.OP, "("):
        result.append(tokens.accept(token.OP, "(", result_token=token.LPAR))

        if not tokens.check(token.OP, ")"):
            result.append(_testlist(tokens))

        result.append(tokens.accept(token.OP, ")", result_token=token.RPAR))

    result.append(tokens.accept(token.OP, ":", result_token=token.COLON))
    result.append(_suite(tokens))

    return result

def _arglist(tokens):
    """Parse an argument list.

    ::

        arglist: (argument ',')* (argument [',']
                                 |'*' test (',' argument)* [',' '**' test]
                                 |'**' test)
    """
    # This grammar is *not* left-factored and has to be rewritten as follows
    # (ε denotes the empty string):
    #
    #   arglist: (argument ',')* (argument [',']
    #                            |'*' test (',' argument)* [',' '**' test]
    #                            |'**' test)
    #   <=>
    #   arglist: (argument ',')* (argument [','])
    #            |
    #
    result = [symbol.arglist]

    # TODO this is so wrong
    if tokens.check_test():
        result.append(_argument(tokens))
        if tokens.check(token.OP, ","):
            result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))
            if tokens.check_test():
                result.append(_argument(tokens))
                if tokens.check(token.OP, ","):
                    result.append(tokens.accept(token.OP, ",", result_token=token.COMMA))

    # TODO option2 '*' test (',' argument)* [',' '**' test]
    # TODO option3 '**' test

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

    if tokens.check(token.NAME, "for"):
        result.append(_comp_for(tokens))
    elif tokens.check(token.OP, "="):
        result.append(tokens.accept(token.OP, "=", result_token=token.EQUAL))
        result.append(_test(tokens))

    return result

def _list_iter(tokens):
    """Parse a list iteration.

    ::

        list_iter: list_for | list_if
    """
    result = [symbol.list_iter]

    if tokens.check(token.NAME, "for"):
        result.append(_list_for(tokens))
    elif tokens.check(token.NAME, "if"):
        result.append(_list_if(tokens))
    else:
        tokens.error("Expecting list_for | list_if")

    return result

def _list_for(tokens):
    """Parse a list for.

    ::

        list_for: 'for' exprlist 'in' testlist_safe [list_iter]
    """
    result = [symbol.list_for]

    result.append(tokens.accept(token.NAME, "for"))
    result.append(_exprlist(tokens))
    result.append(tokens.accept(token.NAME, "in"))
    result.append(_testlist_safe(tokens))

    if tokens.check(token.NAME, "for") or tokens.check(token.NAME, "if"):
        result.append(_list_iter(tokens))

    return result

def _list_if(tokens):
    """Parse a list if.

    ::

        list_if: 'if' old_test [list_iter]
    """
    result = [symbol.list_if]

    result.append(tokens.accept(token.NAME, "if"))
    result.append(_old_test(tokens))

    if tokens.check(token.NAME, "for") or tokens.check(token.NAME, "if"):
        result.append(_list_iter(tokens))

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

    result.append(tokens.accept(token.NAME, "for"))
    result.append(_exprlist(tokens))
    result.append(tokens.accept(token.NAME, "in"))
    result.append(_or_test(tokens))

    # TODO: comp_iter

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

    result.append(tokens.accept(token.NAME, "yield"))

    if tokens.check_test():
        result.append(_testlist(tokens))

    return result

class TokenIterator(object):
    """Wrapper for token generator which allows checking for and accepting
    tokens. Physical line breaks (``tokenize.NL``) and comments (``token.N_TOKENS``)
    are skipped from the input.
    """

    def __init__(self, generator, skip_tokens=(tokenize.NL, token.N_TOKENS)):
        self._index = -1
        self._values = [tok for tok in list(generator) if tok[0] not in skip_tokens]
        self.filename = "<string>"

    def check(self, token_type, token_name=None, lookahead=1):
        if self._index + lookahead >= len(self._values):
            return False

        tok = self._values[self._index + lookahead]

        if tok[0] != token_type:
            return False

        if token_name:
            if isinstance(token_name, basestring):
                if tok[1] != token_name:
                    return False
            else:
                if tok[1] not in token_name:
                    return False

        return True

    # pylint: disable=R0913
    def accept(self, token_type, token_name=None, result_token=None, result_name=None, error_msg=None):
        if not error_msg:
            if not token_name:
                error_msg = "Expecting %s" % token.tok_name[token_type]
            else:
                error_msg = "Expecting '%s'" % token_name

        if self._index + 1 >= len(self._values):
            self.error(error_msg)

        tok = self._values[self._index + 1]

        if tok[0] != token_type:
            self.error(error_msg, tok=tok)

        if not token_name is None and (tok[1] != token_name):
            self.error(error_msg, tok=tok)

        if result_token is None:
            result_token = tok[0]

        if result_name is None:
            result_name = tok[1]

        result = (result_token, result_name)

        self._index = self._index + 1

        return result

    def error(self, error_msg=None, tok=None):
        if not tok:
            tok = self._values[self._index]

        # the second argument to SyntaxError is a 4-tuple with:
        # 1. the filename
        # 2. line number (indexes starting at 1)
        # 3. column number (indexes starting at 1)
        # 4. line of code (string)
        raise SyntaxError(error_msg, (self.filename, tok[2][0], tok[2][1] + 1, tok[4]))

    def check_test(self, lookahead=1):
        """Shorthand notation to check whether next statement is a ``test``"""
        return self.check(token.NAME, "not", lookahead=lookahead) or \
            self.check(token.OP, ("+", "-", "~", "(", "[", "{", "`"), lookahead=lookahead) or \
            self.check(token.NAME, lookahead=lookahead) or \
            self.check(token.NUMBER, lookahead=lookahead) or \
            self.check(token.STRING, lookahead=lookahead)

    def check_comp_op(self):
        """Shorthand notation to check whether next statement is a ``comp_op``"""
        return self.check(token.OP, ("<", ">", "==", ">=", "<=", "<>", "!=")) or \
            self.check(token.NAME, ("in", "not", "is"))
