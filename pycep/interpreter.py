import __builtin__
import pycep.analyzer

def eval(expression):
    node = pycep.analyzer.parse(expression)
    # TODO: implement
    return __builtin__.eval(compile(node, '<string>', mode='exec'))

def execfile(filename):
    program = "".join(open(filename).readlines())
    return eval(program)