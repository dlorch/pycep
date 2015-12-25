Portability
===========

Although PyCep is written in pure Python and it tries to be as self-sufficient
as possible, it defers certain elements to the host language (which conveniently
happens to be a Python itself). These items are listed here:

* `String literal`_ evaluation (see ``ast.literal_eval()``)
* String formatting (see ``%``)
* Type checking, e.g. for arithmetic operations
* `Built-ins`_

.. _String literal: https://docs.python.org/2/reference/lexical_analysis.html#string-literals
.. _Built-ins: https://docs.python.org/2/library/functions.html