from pydantic import BaseModel, Field, field_validator
from src.config import MAX_CHARACTER_LENGTH
class ChatInput(BaseModel):
    questions: list[str] | None = Field(None, min_length=1, max_length=10, examples=[["質問1", "質問2", "質問3"]])
    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if v is not None:
            for question in v:
                if question.strip() == "":
                    raise ValueError("questions cannot contain empty or whitespace strings")
        return v
    
    @field_validator('questions')
    @classmethod
    def validate_question_length(cls, v):
        length = []
        if v is not None:
            length = [len(q) for q in v]
            if any(l > MAX_CHARACTER_LENGTH for l in length):
                    raise ValueError("Each question must be at most 1000 characters long")
        return v


class ChatOutput(BaseModel):
    """チャットボットの出力データの仕様書"""
    responses: list[dict] | None = None