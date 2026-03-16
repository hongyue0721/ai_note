from pydantic import BaseModel, Field


class SolveRequest(BaseModel):
    question_text: str = Field(min_length=1)
    subject: str | None = None
    allow_ai_fallback: bool = True


class SolveResultData(BaseModel):
    subject: str
    question_type: str
    final_answer: str
    solution_steps: list[str]
    knowledge_points: list[str]
    confidence: float = Field(ge=0, le=1)
    warnings: list[str]
    model: str
