import unittest
from os import path
import pycep.interpreter

SAMPLE_PROGRAMS = path.abspath(path.join(path.dirname(__file__), "programs"))

class TestInterpreter(unittest.TestCase):

    def test_helloworld(self):
        filename = path.join(SAMPLE_PROGRAMS, "helloworld.py")
        self.assertEquals(pycep.interpreter.execfile(filename), execfile(filename))