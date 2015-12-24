import unittest
from os import path
import parser
import pycep.parser

SAMPLE_PROGRAMS = path.abspath(path.join(path.dirname(__file__), "programs"))
SNIPPETS = path.abspath(path.join(path.dirname(__file__), "snippets"))

class TestParser(unittest.TestCase):

    def test_beer(self):
        source = open(path.join(SAMPLE_PROGRAMS, "beer.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))

    def test_fib(self):
        source = open(path.join(SAMPLE_PROGRAMS, "fib.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))

    def test_friends(self):
        source = open(path.join(SAMPLE_PROGRAMS, "friends.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))

    def test_functions(self):
        source = open(path.join(SAMPLE_PROGRAMS, "functions.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))

    def test_helloworld(self):
        source = open(path.join(SAMPLE_PROGRAMS, "helloworld.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))
            
    def test_parentsbabies(self):
        source = open(path.join(SAMPLE_PROGRAMS, "parentsbabies.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))
            
    def test_variable_scope(self):
        source = open(path.join(SNIPPETS, "pos", "variable_scope.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))