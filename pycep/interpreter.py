from __future__ import absolute_import
import parser
import pycep.analyzer
import ast

def execfile(filename):
    """The interpreter takes a file path pointing to a python program and
    then executes its contents.

    >>> import pycep.interpreter
    >>> pycep.interpreter.execfile("pycep/tests/programs/helloworld.py")
    Hello, world!
    """
    source = open(filename).read()
    tree = pycep.analyzer.parse(source)
    Interpreter().visit(tree)
    
class Interpreter():
    """An AST-based interpreter
    
    See also:
        * Visitor Design Pattern https://sourcemaking.com/design_patterns/visitor
    """

    def __init__(self):
        self.builtin = {}
        self.globals = {}

    def visit_Module(self, node, scope):
        for stmt in node.body:
            self.visit(stmt, scope)

    def visit_FunctionDef(self, node, scope):
        # create function-local namespace and remember parentage
        node.namespace = {}
        node.parent = scope
        self.bind(node.name, node, scope)

    def visit_Assign(self, node, scope):
        for target in node.targets:
            value = self.visit(node.value, scope)
            self.bind(target.id, value, scope)

    def visit_Print(self, node, scope):
        for value in node.values:
            # TODO dest, nl
            print self.visit(value, scope)

    def visit_Expr(self, node, scope):
        self.visit(node.value, scope)

    def visit_Call(self, node, scope):
        # retrieve the function template
        func = self.visit(node.func, scope)

        # TODO: augment scope by function call / defaults in function 
        # Call(func=Name(id='my_function', ctx=Load()), args=[], keywords=[], starargs=None, kwargs=None)
        # FunctionDef(name='my_function', args=arguments(args=[], vararg=None, kwarg=None, defaults=[]), ..)

        for stmt in func.body:
            self.visit(stmt, func)

    def visit_Num(self, node, scope):
        return node.n

    def visit_Str(self, node, scope):
        return node.s

    def visit_Name(self, node, scope):
        """For a load request, return the value or raise a NameError if not found.
        For a store request, return the matching scope"""
        if isinstance(node.ctx, ast.Load):
            return self.resolve(node.id, scope)
        elif isinstance(node.ctx, ast.Store):
            raise NotImplementedError
        else:
            raise ValueError

    def visit(self, node, scope=None):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, scope)

    def generic_visit(self, node, scope):
        raise NotImplementedError(ast.dump(node))
        
    def bind(self, name, value, local_scope=None):
        """Bind a variable name to a value.
        
        Args:
            name (string): The variable name to bind
            value (ast.AST): The value to store
            local_scope (ast.AST): The local scope to apply, ``None`` to store in globals
        """
        if not local_scope:
            self.globals[name] = value
        else:
            local_scope.namespace[name] = value

    def resolve(self, name, local_scope=None):
        """Find a variable name according to the LEGB rule.
        
        A *namespace* maps names to objects, implemented as a dictionary.
        
        A *scope* defines at which hierarchy level to search for a particular
        variable name, i.e. which namespace to apply.
        
        Python uses the LEGB (Local, Enclosed, Global, Builtin) rule for scope
        lookups.
        
        Args:
            name (string): The variable name to look up
            local_scope (ast.AST): The local scope to apply, ``None`` if there is no local scope to consider

        Returns:
            parser.st: The object found in the hierarchy corresponding to ``name``

        Raises:
            NameError: Name not defined

        See also:
            * Python's Namespaces, Scope Resolution, and the LEGB Rule: http://spartanideas.msu.edu/2014/05/12/a-beginners-guide-to-pythons-namespaces-scope-resolution-and-the-legb-rule/
            * Python Scopes and Namespaces: https://docs.python.org/2/tutorial/classes.html#python-scopes-and-namespaces
            * Variables and scope: http://python-textbok.readthedocs.org/en/latest/Variables_and_Scope.html
            * Gotcha: Python, scoping and closures: http://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/
        """
        result = None

        # Local
        if local_scope and (name in local_scope.namespace):
            return local_scope.namespace[name]
        
        # TODO Enclosed

        # Global
        if name in self.globals:
            return self.globals[name]
        
        # Builtin
        if name in self.builtin:
            return self.builtin[name]

        raise NameError("name '%s' is not defined" % name)