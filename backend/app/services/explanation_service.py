from app.ai.ollama_client import OllamaError, generate
from app.ai.parser import parse_response
from app.ai.prompts import (
    COMPARISON_SYSTEM_PROMPT,
    CONCEPT_SYSTEM_PROMPT,
    build_comparison_prompt,
    build_concept_prompt,
)
from app.schemas.compare import CompareRequest
from app.schemas.explanation import (
    AIExplanation,
    ConceptExplanation,
    ConceptRequest,
    ExplainRequest,
)
from app.services.compare_service import compare_codes

UNQUALIFIED_CLAIMS = ("더 견고한", "더 우수한", "더 좋은 코드", "승리", "이겼", "프로그램이 중단", "항상 작동")


def has_unqualified_claim(result: AIExplanation) -> bool:
    statements = [result.summary, result.recommendation_context]
    statements.extend(item.explanation for item in result.architecture)
    statements.extend(item.explanation for item in result.tradeoffs)
    statements.extend(item.code_a for item in result.tradeoffs)
    statements.extend(item.code_b for item in result.tradeoffs)
    return any(phrase in statement for statement in statements for phrase in UNQUALIFIED_CLAIMS)


async def explain_comparison(request: ExplainRequest) -> AIExplanation:
    comparison = compare_codes(CompareRequest.model_validate(request.model_dump()))
    if not comparison.code_a.valid_python or not comparison.code_b.valid_python:
        raise OllamaError("syntax_error", "먼저 CODE A와 CODE B의 Python 문법 오류를 수정해 주세요.")
    prompt = build_comparison_prompt(comparison, request.code_a, request.code_b)
    for attempt in range(2):
        correction = "\n직전 출력에 단정적인 품질 평가나 확인할 수 없는 실행 결과가 있었습니다. 실제 코드에서 확인되는 차이와 조건부 trade-off로만 다시 설명하세요." if attempt else ""
        content = await generate(COMPARISON_SYSTEM_PROMPT + correction, prompt, AIExplanation.model_json_schema())
        result = parse_response(content, AIExplanation)
        if not has_unqualified_claim(result):
            return result
    raise OllamaError("invalid_response", "AI 설명에 단정적인 표현이 반복되어 결과를 표시하지 않았습니다. 다시 시도해 주세요.")


async def explain_concept(request: ConceptRequest) -> ConceptExplanation:
    content = await generate(CONCEPT_SYSTEM_PROMPT, build_concept_prompt(request), ConceptExplanation.model_json_schema())
    return parse_response(content, ConceptExplanation)
