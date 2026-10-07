import asyncio
import json

import httpx
from fastapi.testclient import TestClient

from app.ai.ollama_client import OllamaError, generate
from app.ai.parser import parse_response
from app.ai.prompts import COMPARISON_SYSTEM_PROMPT, build_comparison_prompt
from app.main import app
from app.schemas.compare import CompareRequest
from app.schemas.explanation import AIExplanation, ConceptExplanation
from app.services.compare_service import compare_codes

client = TestClient(app)
REQUEST = {"prompt": "두 함수를 비교해줘", "code_a": "def a():\n    return 1", "code_b": "class B:\n    pass"}
EXPLANATION = {
    "summary": "CODE A는 함수, CODE B는 클래스를 사용합니다.",
    "architecture": [{"title": "구조", "explanation": "선언 방식이 다릅니다.", "evidence": ["A functions: 1", "B classes: 1"]}],
    "tradeoffs": [{"topic": "구조", "code_a": "함수 사용", "code_b": "클래스 사용", "explanation": "규모에 따라 선택합니다."}],
    "learning_points": [{"concept": "class", "reason": "CODE B에 클래스가 있습니다.", "related_code": "B", "difficulty": "beginner"}],
    "recommendation_context": "작은 기능이면 함수만으로도 충분할 수 있습니다.",
}


def test_status_offline_keeps_compare_working(monkeypatch):
    original_client = httpx.AsyncClient

    def offline(request):
        raise httpx.ConnectError("offline", request=request)

    monkeypatch.setattr("app.ai.ollama_client.httpx.AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(offline)))
    status = client.get("/api/ai/status")
    assert status.status_code == 200
    assert status.json() == {"available": False, "model": None, "message": "Ollama is not running."}
    assert client.post("/api/compare", json=REQUEST).status_code == 200


def test_status_model_available_or_missing(monkeypatch):
    original_client = httpx.AsyncClient
    monkeypatch.setenv("OLLAMA_MODEL", "local-model:7b")

    def tags(request):
        return httpx.Response(200, json={"models": [{"name": "local-model:7b"}]})

    monkeypatch.setattr("app.ai.ollama_client.httpx.AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(tags)))
    assert client.get("/api/ai/status").json()["available"] is True
    monkeypatch.setenv("OLLAMA_MODEL", "missing:7b")
    status = client.get("/api/ai/status").json()
    assert status["available"] is False
    assert status["model"] == "missing:7b"


def test_status_rejects_embedding_only_model(monkeypatch):
    original_client = httpx.AsyncClient
    monkeypatch.setenv("OLLAMA_MODEL", "embedding:latest")

    def tags(request):
        return httpx.Response(200, json={"models": [{"name": "embedding:latest", "capabilities": ["embedding"]}]})

    monkeypatch.setattr("app.ai.ollama_client.httpx.AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(tags)))
    status = client.get("/api/ai/status").json()
    assert status["available"] is False
    assert "cannot generate text" in status["message"]


def test_explain_validation():
    assert client.post("/api/explain", json={"code_a": "", "code_b": "pass"}).status_code == 422
    assert client.post("/api/explain", json={"code_a": "x" * 12_001, "code_b": "pass"}).status_code == 422
    assert client.post("/api/explain", json={**REQUEST, "code_a": "def bad()"}).status_code == 422


def test_explain_parses_model_response_and_sends_evidence(monkeypatch):
    seen = {}

    async def fake_generate(system, prompt, schema):
        seen.update(system=system, prompt=prompt, schema=schema)
        return json.dumps(EXPLANATION, ensure_ascii=False)

    monkeypatch.setattr("app.services.explanation_service.generate", fake_generate)
    response = client.post("/api/explain", json=REQUEST)
    assert response.status_code == 200
    assert response.json()["learning_points"][0]["concept"] == "class"
    assert "class B" in seen["prompt"]
    assert '"functions": 1' in seen["prompt"]
    assert "승자를 고르" in seen["system"]
    assert seen["schema"]["type"] == "object"


def test_code_fence_and_malformed_response():
    parsed = parse_response("```json\n" + json.dumps(EXPLANATION) + "\n```", AIExplanation)
    assert parsed.summary == EXPLANATION["summary"]
    try:
        parse_response("not json", AIExplanation)
    except OllamaError as error:
        assert error.code == "invalid_json"
    else:
        raise AssertionError("Malformed JSON should fail")


def test_malformed_ai_response_does_not_crash_app(monkeypatch):
    async def malformed(*args):
        return "not json"

    monkeypatch.setattr("app.services.explanation_service.generate", malformed)
    response = client.post("/api/explain", json=REQUEST)
    assert response.status_code == 502
    assert response.json()["detail"]["code"] == "invalid_json"
    assert client.post("/api/compare", json=REQUEST).status_code == 200


def test_concept_explanation_schema_and_endpoint(monkeypatch):
    data = {
        "concept": "class", "simple_explanation": "상태와 동작을 묶습니다.", "analogy": "설계도와 같습니다.",
        "in_this_code": "CODE B에 class B가 있습니다.", "simple_example": "class Box: pass",
        "when_to_use": "상태를 함께 관리할 때", "necessity": "이 예제에서는 꼭 필요하지 않습니다.",
    }
    assert ConceptExplanation.model_validate(data).concept == "class"

    async def fake_generate(*args):
        return json.dumps(data, ensure_ascii=False)

    monkeypatch.setattr("app.services.explanation_service.generate", fake_generate)
    payload = {"concept": "class", "prompt": "", "code_a": REQUEST["code_a"], "code_b": REQUEST["code_b"], "context": "CODE B에 클래스가 있습니다."}
    assert client.post("/api/explain/concept", json=payload).json()["necessity"] == data["necessity"]
    assert client.post("/api/explain/concept", json={**payload, "concept": " "}).status_code == 422


def test_prompt_is_bounded_and_identical_code_has_no_invented_difference():
    code = "def add(a, b):\n    return a + b"
    comparison = compare_codes(CompareRequest(code_a=code, code_b=code))
    prompt = build_comparison_prompt(comparison, code, code)
    assert '"detected_differences": []' in prompt
    payload = json.loads(prompt.split("\n", 1)[1])
    assert payload["code_a"]["source"] == payload["code_b"]["source"] == code
    assert "억지로 차이를 만들지 마세요" in COMPARISON_SYSTEM_PROMPT


def test_timeout_maps_to_504(monkeypatch):
    async def timeout(*args):
        raise OllamaError("timeout", "Timed out")

    monkeypatch.setattr("app.services.explanation_service.generate", timeout)
    assert client.post("/api/explain", json=REQUEST).status_code == 504


def test_unqualified_claim_is_retried_and_not_returned(monkeypatch):
    calls = 0

    async def generate_twice(*args):
        nonlocal calls
        calls += 1
        data = {**EXPLANATION, "summary": "CODE B가 더 견고한 구현입니다." if calls == 1 else EXPLANATION["summary"]}
        return json.dumps(data, ensure_ascii=False)

    monkeypatch.setattr("app.services.explanation_service.generate", generate_twice)
    response = client.post("/api/explain", json=REQUEST)
    assert response.status_code == 200
    assert calls == 2
    assert "더 견고한" not in response.json()["summary"]


def test_ollama_chat_payload_is_local_and_structured(monkeypatch):
    original_client = httpx.AsyncClient
    monkeypatch.setenv("OLLAMA_MODEL", "local-model:7b")
    observed = {}

    def chat(request):
        observed["url"] = str(request.url)
        observed["body"] = json.loads(request.content)
        return httpx.Response(200, json={"message": {"content": json.dumps(EXPLANATION)}})

    monkeypatch.setattr("app.ai.ollama_client.httpx.AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(chat)))
    content = asyncio.run(generate("system", "user", AIExplanation.model_json_schema()))
    assert json.loads(content) == EXPLANATION
    assert observed["url"] == "http://localhost:11434/api/chat"
    assert observed["body"]["model"] == "local-model:7b"
    assert observed["body"]["stream"] is False
    assert observed["body"]["format"]["type"] == "object"
    assert observed["body"]["messages"][0] == {"role": "system", "content": "system"}


def test_ollama_chat_offline(monkeypatch):
    original_client = httpx.AsyncClient
    monkeypatch.setenv("OLLAMA_MODEL", "local-model:7b")

    def offline(request):
        raise httpx.ConnectError("offline", request=request)

    monkeypatch.setattr("app.ai.ollama_client.httpx.AsyncClient", lambda **kwargs: original_client(transport=httpx.MockTransport(offline)))
    try:
        asyncio.run(generate("system", "user", {}))
    except OllamaError as error:
        assert error.code == "offline"
    else:
        raise AssertionError("Offline Ollama should fail")
