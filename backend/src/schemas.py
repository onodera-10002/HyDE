from pydantic import BaseModel, Field, field_validator, model_validator

class ChatInput(BaseModel):
    
    question: str | None = Field(None, min_length=1, max_length=1500)
    questions: list[str] | None = Field(None, min_length=1, max_length=10, examples=["質問1", "質問2"])

    @field_validator('question')
    @classmethod
    def validate_question(cls, v):
        if v is not None and v.strip() == "":
            raise ValueError("question cannot be empty or whitespace")
        return v
    
    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        if v is not None:
            for question in v:
                if question.strip() == "":
                    raise ValueError("questions cannot contain empty or whitespace strings")
        return v
    
    @model_validator(mode='after')
    def check_either_or(self):
        q = self.question
        qs = self.questions
        if (q is None or q.strip() == "") and (qs is None or len(qs) == 0):
            raise ValueError("Either question or questions must be provided")
        if q is not None and qs is not None:
            raise ValueError("Only one of question or questions should be provided")
        return self


class ChatOutput(BaseModel):
    """チャットボットの出力データの仕様書"""
    answer: str | None = None
    responses: list[dict] | None = None