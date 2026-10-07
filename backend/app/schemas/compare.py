from pydantic import BaseModel, Field, field_validator


class CompareRequest(BaseModel):
    prompt: str = ""
    code_a: str = Field(max_length=200_000)
    code_b: str = Field(max_length=200_000)
    label_a: str = Field(default="CODE A", max_length=80)
    label_b: str = Field(default="CODE B", max_length=80)

    @field_validator("code_a", "code_b")
    @classmethod
    def require_code(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Code cannot be empty")
        return value


class SyntaxErrorInfo(BaseModel):
    message: str
    line: int | None
    offset: int | None


class RuffIssue(BaseModel):
    code: str
    message: str
    line: int
    column: int


class CodeMetrics(BaseModel):
    total_lines: int
    code_lines: int
    blank_lines: int
    comment_lines: int
    functions: int
    async_functions: int
    classes: int
    imports: int
    import_modules: list[str]
    decorators: int
    try_blocks: int
    except_handlers: int
    raise_count: int
    await_count: int
    parameter_type_hint_functions: int
    return_type_hint_functions: int
    function_type_hint_ratio: float
    return_type_hint_ratio: float
    module_docstring: bool
    function_docstrings: int
    class_docstrings: int
    average_function_length: float
    max_function_length: int
    longest_function: str | None
    max_nesting_depth: int
    ruff_issue_count: int = 0


class CodeResult(BaseModel):
    label: str
    valid_python: bool
    syntax_error: SyntaxErrorInfo | None = None
    metrics: CodeMetrics | None = None
    ruff_issues: list[RuffIssue] = Field(default_factory=list)
    ruff_error: str | None = None


class Difference(BaseModel):
    metric: str
    label: str
    a: int | float
    b: int | float
    difference: int | float


class ImportComparison(BaseModel):
    shared: list[str]
    only_a: list[str]
    only_b: list[str]


class CompareResponse(BaseModel):
    prompt: str
    code_a: CodeResult
    code_b: CodeResult
    differences: list[Difference]
    import_comparison: ImportComparison
    summary: list[str]
