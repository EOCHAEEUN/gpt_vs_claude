import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

from app.schemas.explanation import OllamaStatus

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class OllamaError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def settings() -> tuple[str, str]:
    return os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/"), os.getenv("OLLAMA_MODEL", "").strip()


async def check_status() -> OllamaStatus:
    base_url, model = settings()
    try:
        async with httpx.AsyncClient(timeout=3, trust_env=False) as client:
            response = await client.get(f"{base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
    except (httpx.HTTPError, ValueError, AttributeError):
        return OllamaStatus(available=False, model=None, message="Ollama is not running.")
    if not model:
        return OllamaStatus(available=False, model=None, message="Set OLLAMA_MODEL in backend/.env.")
    matching = next((item for item in models if isinstance(item, dict) and model in (item.get("name"), item.get("model"))), None)
    if matching is None:
        return OllamaStatus(available=False, model=model, message="The configured Ollama model is not installed.")
    capabilities = matching.get("capabilities")
    if isinstance(capabilities, list) and "completion" not in capabilities:
        return OllamaStatus(available=False, model=model, message="The configured Ollama model cannot generate text.")
    return OllamaStatus(available=True, model=model, message="Ollama is available.")


async def generate(system_prompt: str, user_prompt: str, schema: dict) -> str:
    base_url, model = settings()
    if not model:
        raise OllamaError("model_not_configured", "backend/.env의 OLLAMA_MODEL을 설정해 주세요.")
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120, connect=5), trust_env=False) as client:
            response = await client.post(f"{base_url}/api/chat", json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "format": schema,
                "options": {"temperature": 0},
            })
            response.raise_for_status()
            content = response.json()["message"]["content"]
            if not isinstance(content, str):
                raise KeyError("message.content")
            return content
    except httpx.TimeoutException as error:
        raise OllamaError("timeout", "Local AI 응답 시간이 초과되었습니다. 다시 시도해 주세요.") from error
    except httpx.HTTPStatusError as error:
        if error.response.status_code == 404:
            raise OllamaError("model_not_found", f"설정한 Ollama 모델({model})을 찾을 수 없습니다.") from error
        raise OllamaError("ollama_error", "Ollama 요청에 실패했습니다.") from error
    except httpx.RequestError as error:
        raise OllamaError("offline", "Ollama가 실행 중인지 확인해 주세요.") from error
    except (ValueError, KeyError, TypeError) as error:
        raise OllamaError("invalid_response", "Ollama 응답을 읽을 수 없습니다.") from error
