import unittest
import sys
from os import path
from StringIO import StringIO
import pycep.interpreter

SAMPLE_PROGRAMS = path.abspath(path.join(path.dirname(__file__), "programs"))
SNIPPETS = path.abspath(path.join(path.dirname(__file__), "snippets"))

class TestInterpreter(unittest.TestCase):

    def _capture_output(self, fn, *args, **kwargs):
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        fn(*args, **kwargs)
        sys.stdout = old_stdout
        
        return captured_output.getvalue()

    def test_fib(self):
        filename = path.join(SAMPLE_PROGRAMS, "fib.py")
        self.assertEquals(self._capture_output(execfile, filename),
            self._capture_output(pycep.interpreter.execfile, filename))

    def test_helloworld(self):
        filename = path.join(SAMPLE_PROGRAMS, "helloworld.py")
        self.assertEquals(self._capture_output(execfile, filename),
            self._capture_output(pycep.interpreter.execfile, filename))

    def test_variable_scope(self):
        filename = path.join(SNIPPETS, "pos", "variable_scope.py")
        self.assertEquals(self._capture_output(execfile, filename),
            self._capture_output(pycep.interpreter.execfile, filename))