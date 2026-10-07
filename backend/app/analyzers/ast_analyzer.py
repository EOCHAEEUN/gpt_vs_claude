import ast

from app.analyzers.code_metrics import line_metrics
from app.schemas.compare import CodeMetrics, SyntaxErrorInfo

NESTING_NODES = (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith, ast.Match)
if hasattr(ast, "TryStar"):
    NESTING_NODES += (ast.TryStar,)


def max_nesting(tree: ast.AST) -> int:
    maximum = 0

    def visit(node: ast.AST, depth: int) -> None:
        nonlocal maximum
        current = depth + int(isinstance(node, NESTING_NODES))
        maximum = max(maximum, current)
        for child in ast.iter_child_nodes(node):
            visit(child, current)

    visit(tree, 0)
    return maximum


def analyze_ast(code: str) -> tuple[CodeMetrics | None, SyntaxErrorInfo | None]:
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        return None, SyntaxErrorInfo(message=error.msg, line=error.lineno, offset=error.offset)

    nodes = list(ast.walk(tree))
    functions = [node for node in nodes if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
    classes = [node for node in nodes if isinstance(node, ast.ClassDef)]
    imports = [node for node in nodes if isinstance(node, (ast.Import, ast.ImportFrom))]
    modules: set[str] = set()
    for node in imports:
        if isinstance(node, ast.Import):
            modules.update(alias.name.split(".")[0] for alias in node.names)
        elif node.module:
            modules.add(node.module.split(".")[0])
        else:
            modules.update(alias.name.split(".")[0] for alias in node.names)

    hinted_parameters = 0
    hinted_returns = 0
    for function in functions:
        args = function.args
        parameters = [*args.posonlyargs, *args.args, *args.kwonlyargs]
        if args.vararg:
            parameters.append(args.vararg)
        if args.kwarg:
            parameters.append(args.kwarg)
        hinted_parameters += any(argument.annotation is not None for argument in parameters)
        hinted_returns += function.returns is not None

    lengths = [(node.end_lineno or node.lineno) - node.lineno + 1 for node in functions]
    longest_index = max(range(len(lengths)), key=lengths.__getitem__) if lengths else None
    total, code_lines, blank, comments = line_metrics(code)
    count = len(functions)
    return CodeMetrics(
        total_lines=total, code_lines=code_lines, blank_lines=blank, comment_lines=comments,
        functions=count, async_functions=sum(isinstance(node, ast.AsyncFunctionDef) for node in functions),
        classes=len(classes), imports=len(imports), import_modules=sorted(modules),
        decorators=sum(len(node.decorator_list) for node in [*functions, *classes]),
        try_blocks=sum(isinstance(node, (ast.Try, ast.TryStar)) for node in nodes),
        except_handlers=sum(isinstance(node, ast.ExceptHandler) for node in nodes),
        raise_count=sum(isinstance(node, ast.Raise) for node in nodes),
        await_count=sum(isinstance(node, ast.Await) for node in nodes),
        parameter_type_hint_functions=hinted_parameters,
        return_type_hint_functions=hinted_returns,
        function_type_hint_ratio=round(hinted_parameters / count, 3) if count else 0,
        return_type_hint_ratio=round(hinted_returns / count, 3) if count else 0,
        module_docstring=ast.get_docstring(tree) is not None,
        function_docstrings=sum(ast.get_docstring(node) is not None for node in functions),
        class_docstrings=sum(ast.get_docstring(node) is not None for node in classes),
        average_function_length=round(sum(lengths) / count, 2) if count else 0,
        max_function_length=max(lengths, default=0),
        longest_function=functions[longest_index].name if longest_index is not None else None,
        max_nesting_depth=max_nesting(tree),
    ), None
