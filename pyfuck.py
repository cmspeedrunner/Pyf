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

    def visit_FunctionDef(self, node):
        # Translate each function into Brainfuck code
        bf_code = ""
        for stmt in node.body:
            if isinstance(stmt, ast.Expr):
                if isinstance(stmt.value, ast.Call):
                    func = stmt.value.func.id
                    if func == "print":
                        args = []
                        for arg in stmt.value.args:
                            if isinstance(arg, ast.Constant):
                                args.append(arg.value)
                            else:
                                args.append(eval(compile(ast.Expression(arg), '', 'eval'), self.variables))
                        self.print_calls.append(args)
                elif isinstance(stmt.value, ast.BinOp):
                    result = eval(compile(ast.Expression(stmt.value), '', 'eval'), self.variables)
                    target = stmt.targets[0].id
                    self.variables[target] = result
        for args in self.print_calls:
            for arg in args:
                bf_code += "".join(["+" * ord(c) + ".> " for c in str(arg)])
            bf_code += "<" * (len(args) + 1) + "[>]>[.]<"

        for input_call in self.input_calls:
            if isinstance(input_call.args[0], ast.Constant):
                prompt = input_call.args[0].value
                bf_code += "".join(["+" * ord(c) + ".> " for c in prompt])
            bf_code += ",>"

        return bf_code

def python_to_brainfuck(code):
    # Parse the Python code to find all print, input and function statements
    tree = ast.parse(code)
    printer = PrintFinder()
    printer.visit(tree)

    # Translate each function into Brainfuck code
    bf_code = ""
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef):
            bf_code += printer.visit_FunctionDef(stmt)

    with open(flo, 'w') as f:
        f.write(bf_code)
    return bf_code

fl = input("Enter the Python file to convert: ")
flo = input("Enter file to ouput: ")
with open(fl) as f:
    content = f.read()

python_to_brainfuck(content)
