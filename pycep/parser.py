from __future__ import absolute_import
import pycep.tokenizer
import parser
from parser import ParserError
import token
import symbol
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

    tokens = peekable(pycep.tokenizer.generate_tokens(StringIO(source).readline))
    sequence = _file_input(tokens)
    
    # recursively convert list-of-lists to tuples-of-tuples
    def listit(t):
        return tuple(map(listit, t)) if isinstance(t, (list, tuple)) else t

    if totuple:
        return listit(sequence)
    else:
        return parser.sequence2st(sequence)

def _single_input(tokens):
    """Parse a single input.

    ::

        single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE

    Returns:
        list: A parse tree element for the single input
    """
    raise NotImplementedError

def _file_input(tokens):
    """Parse a module or sequence of command read from an input file.

    ::
    
        file_input: (NEWLINE | stmt)* ENDMARKER

    Returns:
        list: A parse tree element for the file input
    """
    result = [symbol.file_input]
    
    while not tokens.peek()[0] == token.ENDMARKER:
        if tokens.peek()[0] == token.NEWLINE:
            result.append((tokens.peek()[0], ''))
            tokens.next()
        else:
            result.append(_stmt(tokens))

    # Training NEWLINE not defined in grammar, but Python's parser always
    # appends it, thus emulate this behavior 
    result.append((token.NEWLINE, ''))

    if tokens.next()[0] != token.ENDMARKER:
        raise ParseError("Expecting ENDMARKER")

    result.append((token.ENDMARKER, ''))

    return result

def _eval_input(tokens):
    """Parse an evaluation input.

    ::

        eval_input: testlist NEWLINE* ENDMARKER

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _decorator(tokens):
    """Parse a decorator.

    ::

        decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _decorators(tokens):
    """Parse a list of decorators.

    ::

        decorators: decorator+

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _decorated(tokens):
    """Parse a decorated statement.

    ::

        decorated: decorators (classdef | funcdef)

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _funcdef(tokens):
    """Parse a function definition.

    ::

        funcdef: 'def' NAME parameters ':' suite

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _parameters(tokens):
    """Parse a parameter list.

    ::

        parameters: '(' [varargslist] ')'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _varargslist(tokens):
    """Parse a variable argument list.

    ::

        varargslist: ((fpdef ['=' test] ',')*
                      ('*' NAME [',' '**' NAME] | '**' NAME) |
                      fpdef ['=' test] (',' fpdef ['=' test])* [','])

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _fpdef(tokens):
    """Parse function parameter definition.

    ::

        fpdef: NAME | '(' fplist ')'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _fplist(tokens):
    """Parse a function parameter list

    ::

        fplist: fpdef (',' fpdef)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _stmt(tokens):
    """Parse a statement.

    ::

        stmt: simple_stmt | compound_stmt

    Returns:
        list: A parse tree element
    """
    result = [symbol.stmt]

    if (tokens.peek()[0] == token.NAME and tokens.peek()[1] in \
        ["if", "while", "try", "with", "def", "class"]):
        result.append(_compound_stmt(tokens))
    elif tokens.peek()[0] == token.OP and tokens.peek()[1] == "@":
        result.append(_compound_stmt(tokens))
    else:
        result.append(_simple_stmt(tokens))

    return result

def _simple_stmt(tokens):
    """Parse a simple statement.

    ::

        simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE

    Returns:
        list: A parse tree element
    """
    result = [symbol.simple_stmt]
    
    result.append(_small_stmt(tokens))
    
    while tokens.peek()[0] == token.SEMI and tokens.peek()[1] == ";":
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
        result.append(_small_stmt(tokens))
        
    if tokens.peek()[0] == token.SEMI and tokens.peek()[1] == ";":
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

    Returns:
        list: A parse tree element
    """
    result = [symbol.small_stmt]
    
    choices = [_print_stmt] # TODO
    subtree = None
    
    for choice in choices:
        try:
            subtree = choice(tokens)
            break # break this loop if choice matches
        except ParserError:
            pass # try next choice

    if not subtree:
        raise ParserError("Expecting (expr_stmt | print_stmt  | del_stmt | " \
            "pass_stmt | flow_stmt | import_stmt | global_stmt | exec_stmt | " \
            "assert_stmt")
            
    result.append(subtree)

    return result

def _expr_stmt(tokens):
    """Parse an expr stmt.

    ::

        expr_stmt: testlist (augassign (yield_expr|testlist) |
                             ('=' (yield_expr|testlist))*)

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _augassign(tokens):
    """Parse an augassign statement.

    ::

        augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
        '<<=' | '>>=' | '**=' | '//=')

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _print_stmt(tokens):
    """Parse a print statement.

    ::

        print_stmt: 'print' ( [ test (',' test)* [','] ] |
                              '>>' test [ (',' test)+ [','] ] )

    Returns:
        list: A parse tree element
    """
    result = [symbol.print_stmt]
    
    if tokens.peek()[0] == token.NAME and tokens.peek()[1] == "print":
        result.append((tokens.peek()[0], tokens.peek()[1]))
        tokens.next()
        
        if tokens.peek()[0] == token.OP and tokens.peek()[1] == ">>":
            raise NotImplementedError
        else:
            result.append(_test(tokens))
        
        # TODO: test is optional
    else:
        raise parser.ParserError
        
    return result

def _del_stmt(tokens):
    """Parse a delete statement.

    ::

        del_stmt: 'del' exprlist

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError


def _pass_stmt(tokens):
    """Parse a pass statement.

    ::

        pass_stmt: 'pass'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _flow_stmt(tokens):
    """Parse a flow statement.

    ::

        flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _break_stmt(tokens):
    """Parse a break statement.

    ::

        break_stmt: 'break'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _continue_stmt(tokens):
    """Parse a continue statement.

    ::

        continue_stmt: 'continue'

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _return_stmt(tokens):
    """Parse a return statement.

    ::

        return_stmt: 'return' [testlist]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _yield_stmt(tokens):
    """Parse a yield statement.

    ::

        yield_stmt: yield_expr

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _raise_stmt(tokens):
    """Parse a raise statement.

    ::

        raise_stmt: 'raise' [test [',' test [',' test]]]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_stmt(tokens):
    """Parse an import statement.

    ::

        import_stmt: import_name | import_from

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_name(tokens):
    """Parse an import name.

    ::

        import_name: 'import' dotted_as_names

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_from(tokens):
    """Parse an import from.

    ::

        import_from: ('from' ('.'* dotted_name | '.'+)
                      'import' ('*' | '(' import_as_names ')' | import_as_names))

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_as_name(tokens):
    """Parse an import as names.

    ::

        import_as_name: NAME ['as' NAME]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dotted_as_name(tokens):
    """Parse a dotted as name.

    ::

        dotted_as_name: dotted_name ['as' NAME]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _import_as_names(tokens):
    """Parse import as names.

    ::

        import_as_names: import_as_name (',' import_as_name)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dotted_as_names(tokens):
    """Parse dotted as names.

    ::

        dotted_as_names: dotted_as_name (',' dotted_as_name)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dotted_name(tokens):
    """Parse a dotted name.

    ::

        dotted_name: NAME ('.' NAME)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _global_stmt(tokens):
    """Parse a global statement.

    ::

        global_stmt: 'global' NAME (',' NAME)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _exec_stmt(tokens):
    """Parse an exec statement.

    ::

        exec_stmt: 'exec' expr ['in' test [',' test]]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _assert_stmt(tokens):
    """Parse an assert statement.

    ::

        assert_stmt: 'assert' test [',' test]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _compound_stmt(tokens):
    """Parse a compound statement.

    ::

        compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _if_stmt(tokens):
    """Parse and if statement.

    ::

        if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _while_stmt(tokens):
    """Parse a while statement.

    ::

        while_stmt: 'while' test ':' suite ['else' ':' suite]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _for_stmt(tokens):
    """Parse a for statement.

    ::

        for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _try_stmt(tokens):
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

def _with_stmt(tokens):
    """Parse a with statement.

    ::

        with_stmt: 'with' with_item (',' with_item)*  ':' suite

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _with_item(tokens):
    """Parse a with item.

    ::

        with_item: test ['as' expr]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _except_clause(tokens):
    """Parse an except clause.

    ::

        except_clause: 'except' [test [('as' | ',') test]]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _suite(tokens):
    """Parse a suite.

    ::

        suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist_safe(tokens):
    """Parse a testlist safe.

    ::

        testlist_safe: old_test [(',' old_test)+ [',']]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _old_test(tokens):
    """Parse an old test.

    ::

        old_test: or_test | old_lambdef

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _old_lambdef(tokens):
    """Parse an old lambda definition.

    ::

        old_lambdef: 'lambda' [varargslist] ':' old_test

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _test(tokens):
    """Parse a test statement.

    ::

        test: or_test ['if' or_test 'else' test] | lambdef

    Returns:
        list: A parse tree element
    """
    result = [symbol.test]
    result.append(_or_test(tokens))
    
    # TODO if/lambdef
    
    return result

def _or_test(tokens):
    """Parse an or_test statement

    ::

        or_test: and_test ('or' and_test)*

    Returns:
        list: A parse tree element
    """
    result = [symbol.or_test]
    result.append(_and_test(tokens))

    # TODO or and_test
    
    return result

def _and_test(tokens):
    """Parse an and test statement.

    ::

        and_test: not_test ('and' not_test)*

    Returns:
        list: A parse tree element
    """
    result = [symbol.and_test]
    result.append(_not_test(tokens))
    
    # TODO and not_test
    
    return result

def _not_test(tokens):
    """Parse a not test statement.

    ::

        not_test: 'not' not_test | comparison

    Return:
        list: A parse tree element
    """
    result = [symbol.not_test]
    result.append(_comparison(tokens))

    # TODO: not not_test
    
    return result

def _comparison(tokens):
    """Parse a comparison.

    ::

        comparison: expr (comp_op expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.comparison]
    result.append(_expr(tokens))
    
    # TODO: comp_op expr
    
    return result

def _comp_op(tokens):
    """Parse a compare operator statement.

    ::

        comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'

    Return:
        list: A parse tree element
    """
    raise NotImplementedError

def _expr(tokens):
    """Parse an expression statement.

    ::

        expr: xor_expr ('|' xor_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.expr]
    result.append(_xor_expr(tokens))
    
    # TODO | xor_expr
    
    return result

def _xor_expr(tokens):
    """Parse an xor expression statement.

    ::

        xor_expr: and_expr ('^' and_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.xor_expr]
    result.append(_and_expr(tokens))

    # TODO ^ and_exr
    
    return result

def _and_expr(tokens):
    """Parse an and expression statement.

    ::

        and_expr: shift_expr ('&' shift_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.and_expr]
    result.append(_shift_expr(tokens))
    
    # TODO
    
    return result

def _shift_expr(tokens):
    """Parse a shift_expr statement

    ::

        shift_expr: arith_expr (('<<'|'>>') arith_expr)*

    Return:
        list: A parse tree element
    """
    result = [symbol.shift_expr]
    result.append(_arith_expr(tokens))
    
    # TODO
    
    return result

def _arith_expr(tokens):
    """Parse an arithmetic expression statement.

    ::

        arith_expr: term (('+'|'-') term)*

    Return:
        list: A parse tree element
    """
    result = [symbol.arith_expr]
    result.append(_term(tokens))
    
    # TODO
    
    return result

def _term(tokens):
    """Parse a term statement.

    ::

        term: factor (('*'|'/'|'%'|'//') factor)*

    Return:
        list: A parse tree element
    """
    result = [symbol.term]
    result.append(_factor(tokens))
    
    # TODO
    
    return result
    
def _factor(tokens):
    """Parse a factor statement.

    ::

        factor: ('+'|'-'|'~') factor | power

    Returns:
        list: A parse tree element
    """
    result = [symbol.factor]
    
    # TODO
    
    result.append(_power(tokens))
    return result
    
def _power(tokens):
    """Parse a power statement.

    ::

        power: atom trailer* ['**' factor]

    Returns:
        list: A parse tree element
    """
    result = [symbol.power]
    result.append(_atom(tokens))
    
    # TODO
    
    return result

def _atom(tokens):
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
    
    # TODO
    
    result.append((tokens.peek()[0], tokens.peek()[1]))
    tokens.next()
    
    return result
    
def _listmaker(tokens):
    """Parse a listmaker statement.

    ::

        listmaker: test ( list_for | (',' test)* [','] )

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist_comp(tokens):
    """Parse a testlist comp statement.

    ::

        testlist_comp: test ( comp_for | (',' test)* [','] )

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _lambdef(tokens):
    """Parse a lambda definition.

    ::

        lambdef: 'lambda' [varargslist] ':' test

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _trailer(tokens):
    """Parse a trailer.

    ::

        trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _subscriptlist(tokens):
    """Parse a subscriptlist.

    ::

        subscriptlist: subscript (',' subscript)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _subscript(tokens):
    """Parse a subscript.

    ::

        subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _sliceop(tokens):
    """Parse a slice operation.

    ::

        sliceop: ':' [test]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _exprlist(tokens):
    """Parse an expression list.

    ::

        exprlist: expr (',' expr)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist(tokens):
    """Parse a testlist.

    ::

        testlist: test (',' test)* [',']

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _dictorsetmaker(tokens):
    """Parse a dict or set maker statement.

    ::

        dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
                          (test (comp_for | (',' test)* [','])) )

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _classdef(tokens):
    """Parse a class definition.

    ::

            classdef: 'class' NAME ['(' [testlist] ')'] ':' suite

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _arglist(tokens):
    """Parse an argument list.

    ::

        arglist: (argument ',')* (argument [',']
                                 |'*' test (',' argument)* [',' '**' test]
                                 |'**' test)

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _argument(tokens):
    """Parse an argument.

    ::

        argument: test [comp_for] | test '=' test

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _list_iter(tokens):
    """Parse a list iteration.

    ::

        list_iter: list_for | list_if

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _list_for(tokens):
    """Parse a list for.

    ::

        list_for: 'for' exprlist 'in' testlist_safe [list_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _list_if(tokens):
    """Parse a list if.

    ::

        list_if: 'if' old_test [list_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _comp_iter(tokens):
    """Parse a comp iter.

    ::

        comp_iter: comp_for | comp_if

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _comp_for(tokens):
    """Parse a comp for.

    ::

        comp_for: 'for' exprlist 'in' or_test [comp_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _comp_if(tokens):
    """Parse a comp if.

    ::

        comp_if: 'if' old_test [comp_iter]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _testlist1(tokens):
    """Parse a testlist1.

    ::

        testlist1: test (',' test)*

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _encoding_decl(tokens):
    """Parse an encoding declaration.

    ::

        encoding_decl: NAME

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError

def _yield_expr(tokens):
    """Parse a yield expression.

    ::

        yield_expr: 'yield' [testlist]

    Returns:
        list: A parse tree element
    """
    raise NotImplementedError