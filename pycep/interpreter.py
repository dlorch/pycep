from __future__ import absolute_import
import parser
import pycep.analyzer

def execfile(filename):
    # TODO: this is a stub
    source = open(filename).read()
    ast = pycep.analyzer.parse(source)
    code = parser.compileast(ast, filename=filename)
    exec code