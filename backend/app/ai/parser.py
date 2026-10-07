from pydantic import BaseModel, ValidationError

from app.ai.ollama_client import OllamaError


def parse_response[T: BaseModel](content: str, schema: type[T]) -> T:
    cleaned = content.strip()
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3 and lines[0].lower() in ("```", "```json") and lines[-1] == "```":
            cleaned = "\n".join(lines[1:-1]).strip()
    try:
        return schema.model_validate_json(cleaned)
    except ValidationError as error:
        raise OllamaError("invalid_json", "AI 응답을 구조화하는 데 실패했습니다. 다시 시도해 주세요.") from error
