from app.analyzers.ast_analyzer import analyze_ast


def metrics_for(code: str):
    metrics, error = analyze_ast(code)
    assert error is None
    assert metrics is not None
    return metrics


def test_regular_function_and_line_counts():
    metrics = metrics_for("# note\n\ndef add(a, b):\n    return a + b\n")
    assert (metrics.total_lines, metrics.code_lines, metrics.blank_lines, metrics.comment_lines) == (4, 2, 1, 1)
    assert (metrics.functions, metrics.async_functions, metrics.max_function_length) == (1, 0, 2)


def test_class_imports_and_docstrings():
    metrics = metrics_for('''"""Module."""
import os, sys
from fastapi.responses import JSONResponse

class Service:
    """Class."""
    def run(self):
        """Method."""
        return 1
''')
    assert metrics.classes == 1
    assert metrics.imports == 2
    assert metrics.import_modules == ["fastapi", "os", "sys"]
    assert (metrics.module_docstring, metrics.class_docstrings, metrics.function_docstrings) == (True, 1, 1)


def test_async_try_await_nesting_and_type_hints():
    metrics = metrics_for('''async def fetch(url: str) -> str:
    try:
        if url:
            return await get(url)
    except ValueError:
        raise
''')
    assert (metrics.async_functions, metrics.await_count, metrics.try_blocks, metrics.except_handlers, metrics.raise_count) == (1, 1, 1, 1, 1)
    assert (metrics.parameter_type_hint_functions, metrics.return_type_hint_functions) == (1, 1)
    assert (metrics.function_type_hint_ratio, metrics.return_type_hint_ratio) == (1, 1)
    assert metrics.max_nesting_depth == 2


def test_syntax_error_returns_location():
    metrics, error = analyze_ast("def broken()\n    pass")
    assert metrics is None
    assert error is not None
    assert error.line == 1
    assert error.offset is not None
