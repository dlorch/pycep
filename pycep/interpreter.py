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

    def visit_AugAssign(self, node, scope):
        target = self.visit(node.target, scope)
        left = self.resolve(target, scope)
        value = self.visit(node.value, scope)

        if isinstance(node.op, ast.Sub):
            left -= value
            self.bind(target, left, scope)
        else:
            raise NotImplementedError

    def visit_Assign(self, node, scope):
        value = self.visit(node.value, scope)

        for target in node.targets:
            if isinstance(target, ast.Tuple):
                if len(target.elts) != len(value):
                    raise ValueError("too many values to unpack")
                for idx, elt in enumerate(target.elts):
                    # TODO what if we have nested tuples?
                    self.bind(elt.id, value[idx], scope)
            else:
                self.bind(target.id, value, scope)

    def visit_Print(self, node, scope):
        for idx, value in enumerate(node.values):
            # TODO dest
            if idx < len(node.values) - 1:
                print self.visit(value, scope),
            else:
                print self.visit(value, scope)

    def visit_While(self, node, scope):
        while self.visit(node.test, scope):
            for stmt in node.body:
                self.visit(stmt, scope)
        # TODO node.orelse

    def visit_Expr(self, node, scope):
        self.visit(node.value, scope)

    def visit_BinOp(self, node, scope):
        left = self.visit(node.left, scope)
        right = self.visit(node.right, scope)
        
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mod):
            return left % right
        else:
            raise NotImplementedError

    def visit_Compare(self, node, scope):
        left = self.visit(node.left, scope)
        
        if len(node.ops) > 1:
            raise NotImplementedError
        
        comparator = self.visit(node.comparators[0], scope)

        if isinstance(node.ops[0], ast.Lt):
            return left < comparator
        elif isinstance(node.ops[0], ast.Gt):
            return left > comparator
        else:
            raise NotImplementedError
            
    def visit_Call(self, node, scope):
        # retrieve the function template
        func = self.visit(node.func, scope)

        # TODO:
        # - check that required arguments to function are given
        # - bind variables to function scope
        for idx, call_arg in enumerate(node.args):
            value = self.visit(call_arg, scope)
            func_arg = func.args.args[idx]
            self.bind(func_arg.id, value, func)

        for stmt in func.body:
            self.visit(stmt, func)

    def visit_Num(self, node, scope):
        return node.n

    def visit_Str(self, node, scope):
        return node.s

    def visit_Name(self, node, scope):
        """Return the value or raise a NameError if not found."""
        if isinstance(node.ctx, ast.Load):
            return self.resolve(node.id, scope)
        elif isinstance(node.ctx, ast.Store):
            return node.id
        else:
            raise ValueError

    def visit_Tuple(self, node, scope):
        result = []
        for expr in node.elts:
            result.append(self.visit(expr, scope))
        return tuple(result)

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
