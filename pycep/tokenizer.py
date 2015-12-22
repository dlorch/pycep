import tokenize

def generate_tokens(readline):
    """The tokenizer takes a file handle containing the source code as an input
    and returns a sequence of tokens.

    >>> import pycep.tokenizer
    >>> from StringIO import StringIO
    >>> tokens = pycep.tokenizer.generate_tokens(StringIO('print "Hello World"').readline)
    >>> list(tokens)
    [(1, 'print', (1, 0), (1, 5), 'print "Hello World"'), (3, '"Hello World"', (1, 6), (1, 19), 'print "Hello World"'), (0, '', (2, 0), (2, 0), '')]

    See also:
        * Python is not context free http://trevorjim.com/python-is-not-context-free/
    """
    
    # TODO: this is a stub
    return tokenize.generate_tokens(readline)