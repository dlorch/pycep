import unittest
from os import path
import ast
import _ast
import pycep.analyzer

SAMPLE_PROGRAMS = path.abspath(path.join(path.dirname(__file__), "programs"))

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(_ast.Module, "assertAstEqual")

    def test_helloworld(self):
        source = open(path.join(SAMPLE_PROGRAMS, "helloworld.py")).read()
        self.assertEquals(ast.parse(source), pycep.analyzer.parse(source))
    
    def assertAstEqual(self, first, second, msg=None):
        def astShallowEqual(first, second):
            """ Shallow equality, don't recurse into sub-items """
            for (fieldname, value) in ast.iter_fields(first):
                value2 = getattr(second, fieldname, None)
                if isinstance(value, list):
                    if len(value) != len(value2):
                        return False
                else:
                    if value != value2:
                        return False
            return True
        
        if type(first) != type(second):
            self.fail("%s != %s" % (ast.dump(first), ast.dump(second)))
        elif isinstance(first, ast.AST):
            if not astShallowEqual(first, second):
                self.fail("%s != %s" % (ast.dump(first), ast.dump(second)))
            else:
                for (fieldname, value) in ast.iter_fields(first):
                    value2 = getattr(second, fieldname, None)
                    if isinstance(value, list):
                        for idx, v in enumerate(value):
                            v2 = value2[idx]
                            self.assertAstEqual(v, v2)