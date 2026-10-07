from app.analyzers.ast_analyzer import analyze_ast
from app.analyzers.ruff_analyzer import analyze_ruff
from app.schemas.compare import (
    CodeResult,
    CompareRequest,
    CompareResponse,
    Difference,
    ImportComparison,
)

METRICS = {
    "total_lines": "전체 줄 수", "code_lines": "코드 줄 수", "blank_lines": "빈 줄 수",
    "comment_lines": "주석 줄 수", "functions": "함수 수", "async_functions": "비동기 함수 수",
    "classes": "클래스 수", "imports": "import 문 수", "decorators": "데코레이터 수",
    "try_blocks": "try 블록 수", "except_handlers": "except 처리기 수",
    "raise_count": "raise 수", "await_count": "await 수",
    "parameter_type_hint_functions": "매개변수 타입 힌트 함수 수",
    "return_type_hint_functions": "반환 타입 힌트 함수 수",
    "function_type_hint_ratio": "매개변수 타입 힌트 비율",
    "return_type_hint_ratio": "반환 타입 힌트 비율",
    "function_docstrings": "함수 문서 문자열 수", "class_docstrings": "클래스 문서 문자열 수",
    "average_function_length": "평균 함수 길이", "max_function_length": "최대 함수 길이",
    "max_nesting_depth": "최대 중첩 깊이", "ruff_issue_count": "Ruff 문제 수",
}


def analyze_code(code: str, label: str) -> CodeResult:
    metrics, syntax_error = analyze_ast(code)
    if metrics is None:
        return CodeResult(label=label, valid_python=False, syntax_error=syntax_error)
    issues, ruff_error = analyze_ruff(code)
    metrics.ruff_issue_count = len(issues)
    return CodeResult(label=label, valid_python=True, metrics=metrics, ruff_issues=issues, ruff_error=ruff_error)


def compare_codes(request: CompareRequest) -> CompareResponse:
    a = analyze_code(request.code_a, request.label_a.strip() or "CODE A")
    b = analyze_code(request.code_b, request.label_b.strip() or "CODE B")
    differences: list[Difference] = []
    summary: list[str] = []
    imports = ImportComparison(shared=[], only_a=[], only_b=[])
    if a.metrics and b.metrics:
        for key, label in METRICS.items():
            value_a = getattr(a.metrics, key)
            value_b = getattr(b.metrics, key)
            differences.append(Difference(metric=key, label=label, a=value_a, b=value_b,
                                          difference=round(abs(value_a - value_b), 3)))
        set_a, set_b = set(a.metrics.import_modules), set(b.metrics.import_modules)
        imports = ImportComparison(shared=sorted(set_a & set_b), only_a=sorted(set_a - set_b),
                                   only_b=sorted(set_b - set_a))
        for key in ("total_lines", "functions", "classes", "async_functions", "imports", "try_blocks", "max_nesting_depth"):
            value_a, value_b = getattr(a.metrics, key), getattr(b.metrics, key)
            if value_a != value_b:
                larger = "CODE A" if value_a > value_b else "CODE B"
                summary.append(f"{larger}의 {METRICS[key]}가 {abs(value_a - value_b)} 더 많습니다.")
        if a.metrics.async_functions and b.metrics.async_functions:
            summary.append("두 코드 모두 비동기 함수를 사용합니다.")
        if not summary:
            summary.append("선택한 구조 지표의 수치가 같습니다.")
    return CompareResponse(prompt=request.prompt, code_a=a, code_b=b,
                           differences=differences, import_comparison=imports, summary=summary)
