import tokenize

def generate_tokens(readline):
    """The tokenizer takes a file handle containing the source code as an input
    and returns a sequence of tokens.

    >>> import pycep.tokenizer
    >>> from StringIO import StringIO
    >>> tokens = pycep.tokenizer.generate_tokens(StringIO('print "Hello, world!"').readline)
    >>> list(tokens)
    [(1, 'print', (1, 0), (1, 5), 'print "Hello, world!"'), (3, '"Hello, world!"', (1, 6), (1, 19), 'print "Hello, world!"'), (0, '', (2, 0), (2, 0), '')]

    See also:
        * Python Language Reference: Lexical Analysis: https://docs.python.org/2/reference/lexical_analysis.html
        * Python: Myths about Indentation: http://www.secnetix.de/olli/Python/block_indentation.hawk
        * Python is not context free: http://trevorjim.com/python-is-not-context-free/
    """
    
    # TODO: this is a stub
    return tokenize.generate_tokens(readline)