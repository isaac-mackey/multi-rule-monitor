import ast
c = 'x < 2'
for node in ast.walk(ast.parse(c)):
    print(node)
    if isinstance(node, ast.Name):
        print(node.id)