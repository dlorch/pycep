import ast

def parse(source):
    # TODO: implement
    node = ast.parse(source, mode='exec')
    return node