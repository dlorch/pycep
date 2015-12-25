Parser
======

The type of parser implemented is called a *recursive-descent parser with
backtracking*.
    
Eliminating Ambiguities
-----------------------

Some parts of the grammar are not suitable for parsing by recursive descent,
because they are *not left-factored*. Consider the following example where both
productions share the common prefix ``test``:
    
::
    
    argument: test [comp_for] | test '=' test
    
The issue with this production is that the recursive-descent parser could go
down the first path, return with a success and never consider the second path.
We can left-factor the grammar by making a new nonterminal ``option`` to
represent the two alternatives for the symbols following the common prefix:

::
    
    argument: test option
    option:   ε | comp_for | '=' test
    
..where ε denotes the empty string. This production is now suitable for the
recursive-descent parser.

See also
--------

* Eliminating Ambiguities http://ycpcs.github.io/cs340-fall2015/lectures/lecture05.html

.. disqus:: pycep parser