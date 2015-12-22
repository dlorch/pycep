from __future__ import absolute_import
import parser
import pycep.analyzer

def execfile(filename):
    """The interpreter takes a file path pointing to a python program and
    then executes its contents.

    >>> import pycep.interpreter
    >>> pycep.interpreter.execfile("pycep/tests/programs/helloworld.py")
    Hello, world!

    See also:
        * Design of CPython’s Compiler https://docs.python.org/devguide/compiler.html
        * Disassembler for Python Bytecode https://docs.python.org/2/library/dis.html
    """

    # TODO: this is a stub
    source = open(filename).read()
    ast = pycep.analyzer.parse(source)
    code = compile(ast, filename=filename, mode="exec")
    exec code