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
        if type(first) != type(second):
            self.fail("%s != %s" % (str(first), str(second)))
        elif isinstance(first, ast.AST):
            for (fieldname, value) in ast.iter_fields(first):
                value2 = getattr(second, fieldname, None)
                self.assertAstEqual(value, value2)
        elif isinstance(first, list):
            if len(first) != len(second):
                self.fail("%s != %s" % (str(first), str(second)))
            else:
                for idx, value in enumerate(first):
                    value2 = second[idx]
                    self.assertAstEqual(value, value2)
        else:
            self.assertEquals(first, second, msg)