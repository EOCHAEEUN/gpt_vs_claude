from fastapi import APIRouter, HTTPException

from app.ai.ollama_client import OllamaError, check_status
from app.schemas.explanation import (
    AIExplanation,
    ConceptExplanation,
    ConceptRequest,
    ExplainRequest,
    OllamaStatus,
)
from app.services.explanation_service import explain_comparison, explain_concept

router = APIRouter(prefix="/api")


def ai_http_error(error: OllamaError) -> HTTPException:
    status = 422 if error.code == "syntax_error" else 504 if error.code == "timeout" else 502 if error.code in ("invalid_json", "invalid_response", "ollama_error") else 503
    return HTTPException(status_code=status, detail={"code": error.code, "message": error.message})


@router.get("/ai/status", response_model=OllamaStatus)
async def ai_status() -> OllamaStatus:
    return await check_status()


@router.post("/explain", response_model=AIExplanation)
async def explain(request: ExplainRequest) -> AIExplanation:
    try:
        return await explain_comparison(request)
    except OllamaError as error:
        raise ai_http_error(error) from error


@router.post("/explain/concept", response_model=ConceptExplanation)
async def concept(request: ConceptRequest) -> ConceptExplanation:
    try:
        return await explain_concept(request)
    except OllamaError as error:
        raise ai_http_error(error) from error
