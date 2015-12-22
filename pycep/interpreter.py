# -*- coding: utf-8 -*-

from __future__ import absolute_import
import parser
import pycep.analyzer
import ast

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
    source = open(filename).read()
    tree = pycep.analyzer.parse(source)
    Interpreter().visit(tree)
    
class Interpreter(ast.NodeVisitor):
    """An AST-based interpreter"""

    def visit_Module(self, node):
        for stmt in node.body:
            self.visit(stmt)

    def visit_Print(self, node):
        for value in node.values:
            # TODO dest, nl
            print self.visit(value)

    def visit_Str(self, node):
        return node.s

    def generic_visit(self, node):
        raise NotImplementedError(ast.dump(node))