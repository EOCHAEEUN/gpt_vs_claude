from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.schemas.compare import CompareRequest


class OllamaStatus(BaseModel):
    available: bool
    model: str | None
    message: str


class ExplainRequest(CompareRequest):
    prompt: str = Field(default="", max_length=2000)

    @field_validator("code_a", "code_b")
    @classmethod
    def limit_ai_code(cls, value: str) -> str:
        if len(value) > 12_000:
            raise ValueError("AI 해설은 코드당 12,000자 이하를 지원합니다. 정적 분석은 더 긴 코드도 비교할 수 있습니다.")
        return value


class ArchitectureAnalysis(BaseModel):
    title: str = Field(min_length=1)
    explanation: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list, max_length=4)


class Tradeoff(BaseModel):
    topic: str = Field(min_length=1)
    code_a: str = Field(min_length=1)
    code_b: str = Field(min_length=1)
    explanation: str = Field(min_length=1)


class LearningPoint(BaseModel):
    concept: str = Field(min_length=1, max_length=120)
    reason: str = Field(min_length=1, max_length=1000)
    related_code: Literal["A", "B", "both"] | None = None
    difficulty: Literal["beginner", "intermediate", "advanced"]


class AIExplanation(BaseModel):
    summary: str = Field(min_length=1)
    architecture: list[ArchitectureAnalysis] = Field(min_length=1, max_length=4)
    tradeoffs: list[Tradeoff] = Field(min_length=1, max_length=4)
    learning_points: list[LearningPoint] = Field(default_factory=list, max_length=3)
    recommendation_context: str = Field(min_length=1)


class ConceptRequest(BaseModel):
    concept: str = Field(min_length=1, max_length=120)
    prompt: str = Field(default="", max_length=2000)
    code_a: str = Field(min_length=1, max_length=12_000)
    code_b: str = Field(min_length=1, max_length=12_000)
    context: str = Field(min_length=1, max_length=1000)

    @field_validator("concept", "code_a", "code_b", "context")
    @classmethod
    def require_nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field cannot be blank")
        return value


class ConceptExplanation(BaseModel):
    concept: str = Field(min_length=1)
    simple_explanation: str = Field(min_length=1)
    analogy: str = Field(min_length=1)
    in_this_code: str = Field(min_length=1)
    simple_example: str = Field(min_length=1)
    when_to_use: str = Field(min_length=1)
    necessity: str = Field(min_length=1)
