import unittest
from os import path
import ast
import _ast
import pycep.analyzer

SAMPLE_PROGRAMS = path.abspath(path.join(path.dirname(__file__), "programs"))
SNIPPETS = path.abspath(path.join(path.dirname(__file__), "snippets"))

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(_ast.Module, "assertAstEqual")

    def test_beer(self):
        source = open(path.join(SAMPLE_PROGRAMS, "beer.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_classes(self):
        source = open(path.join(SAMPLE_PROGRAMS, "classes.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_cliexception(self):
        source = open(path.join(SAMPLE_PROGRAMS, "cliexception.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_fib(self):
        source = open(path.join(SAMPLE_PROGRAMS, "fib.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_friends(self):
        source = open(path.join(SAMPLE_PROGRAMS, "friends.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_functions(self):
        source = open(path.join(SAMPLE_PROGRAMS, "functions.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_helloworld(self):
        source = open(path.join(SAMPLE_PROGRAMS, "helloworld.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))
    
    def test_parentsbabies(self):
        source = open(path.join(SAMPLE_PROGRAMS, "parentsbabies.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))
    
    def test_primes(self):
        source = open(path.join(SAMPLE_PROGRAMS, "primes.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def test_variable_scope(self):
        source = open(path.join(SNIPPETS, "pos", "variable_scope.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))

    def assertAstEqual(self, first, second, msg=None):
        def astShallowEqual(first, second):
            """ Only check shallow equality - don't recurse into sub-items """
            for (fieldname, value) in ast.iter_fields(first):
                if not hasattr(second, fieldname):
                    return False
                value2 = getattr(second, fieldname)

                if type(value) != type(value2):
                    return False
                
                if isinstance(value, list):
                    if len(value) != len(value2):
                        return False
                # Fields can be AST items too, e.g. ast.arguments(),
                # ast.Store(), ast.Load(), ast.Param(). Recurse into those items
                elif isinstance(value, ast.AST):
                    result = astShallowEqual(value, value2)
                    if not result:
                        return False
                else:
                    if value != value2:
                        return False
            
            return True
        
        if type(first) != type(second):
            self.fail("Expected: %s\n\nActual: %s" % (dump(first), dump(second)))
        elif isinstance(first, ast.AST):
            # the reason to first do a shallow equality check rather than a deep one
            # is that it gives better debugging output - rather than only seeing the
            # sub-node that caused the inequality, we can see the full faulty node
            if not astShallowEqual(first, second):
                self.fail("Expected: %s\n\nActual: %s" % (dump(first), dump(second)))
            else:
                for (fieldname, value) in ast.iter_fields(first):
                    # given shallow equality, we know first and second have the same
                    # attributes, and list attributes are of the same length
                    value2 = getattr(second, fieldname)
                    if isinstance(value, list):
                        for idx, v in enumerate(value):
                            v2 = value2[idx]
                            self.assertAstEqual(v, v2)
                    else:
                        self.assertAstEqual(value, value2)

def dump(node, annotate_fields=True, include_attributes=False, indent='  '):
    """
    A pretty-printing dump function for the ast module.  The code was copied from
    the ast.dump function and modified slightly to pretty-print.

    Alex Leone (acleone ~AT~ gmail.com), 2010-01-30

    From http://alexleone.blogspot.co.uk/2010/01/python-ast-pretty-printer.html

    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, level=0):
        if isinstance(node, ast.AST):
            fields = [(a, _format(b, level)) for a, b in ast.iter_fields(node)]
            if include_attributes and node._attributes:
                fields.extend([(a, _format(getattr(node, a), level))
                               for a in node._attributes])
            return ''.join([
                node.__class__.__name__,
                '(',
                ', '.join(('%s=%s' % field for field in fields)
                           if annotate_fields else
                           (b for a, b in fields)),
                ')'])
        elif isinstance(node, list):
            lines = ['[']
            lines.extend((indent * (level + 2) + _format(x, level + 2) + ','
                         for x in node))
            if len(lines) > 1:
                lines.append(indent * (level + 1) + ']')
            else:
                lines[-1] += ']'
            return '\n'.join(lines)
        return repr(node)

    if not isinstance(node, ast.AST) and not isinstance(node, list):
        raise TypeError('expected AST or list, got %r' % node.__class__.__name__)
    return _format(node)