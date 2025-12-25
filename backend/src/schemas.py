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

class SourceItem(BaseModel):
    title: str | None = None  # 画面表示用（例: "社内規定.pdf 5ページ"）
    url: str    # クリック時の遷移先（例: "/files/doc1.pdf#page=5"）
    page: int | None = None  # ページ番号

class AnswerItems(BaseModel):
    question: str
    answer: str
    sources: list[SourceItem] | None = None

class ChatOutput(BaseModel):
    """チャットボットの出力データの仕様書"""
    responses: list[AnswerItems] | None = None