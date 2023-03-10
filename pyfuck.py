fl = input("Enter the Python file to convert: ")
flo = input("Enter file to ouput: ")
with open(fl) as f:
    content = f.read()

import ast

class PrintFinder(ast.NodeVisitor):
    def __init__(self):
        self.print_calls = []
        self.input_calls = []
        self.variables = {}

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant):
                    args.append(arg.value)
                else:
                    args.append(eval(compile(ast.Expression(arg), '', 'eval'), self.variables))
            self.print_calls.append(args)
        elif isinstance(node.func, ast.Name) and node.func.id == "input":
            self.input_calls.append(node)
        self.generic_visit(node)

    def visit_Assign(self, node):
        target = node.targets[0].id
        value = eval(compile(ast.Expression(node.value), '', 'eval'), self.variables)
        self.variables[target] = value

def python_to_brainfuck(code):
    # Parse the Python code to find all print and input statements
    tree = ast.parse(code)
    printer = PrintFinder()
    printer.visit(tree)

    # Translate each print and input statement into Brainfuck code
    bf_code = ""
    for args in printer.print_calls:
        for arg in args:
            bf_code += "".join(["+" * ord(c) + ".> " for c in str(arg)])
        bf_code += "<" * (len(args) + 1) + "[>]>[.]<"

    for input_call in printer.input_calls:
        if isinstance(input_call.args[0], ast.Constant):
            prompt = input_call.args[0].value
            bf_code += "".join(["+" * ord(c) + ".> " for c in prompt])
        bf_code += ",>"

    with open(flo, 'w') as f:
        f.write(bf_code)
    return bf_code

python_to_brainfuck(content)
