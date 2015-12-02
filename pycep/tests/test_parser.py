import unittest
from os import path
import parser
import pycep.parser

SAMPLE_PROGRAMS = path.abspath(path.join(path.dirname(__file__), "programs"))

class TestParser(unittest.TestCase):

    def test_beer(self):
        source = open(path.join(SAMPLE_PROGRAMS, "beer.py")).read()
        self.assertEquals(parser.suite(source).totuple(),
            pycep.parser.suite(source, totuple=True))

    def test_fib(self):
        source = open(path.join(SAMPLE_PROGRAMS, "fib.py")).read()
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