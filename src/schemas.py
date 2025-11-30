from pydantic import BaseModel, Field, field_validator

class ChatInput(BaseModel):
    """ユーザーからの入力データの仕様書"""
    question: str = Field(..., min_length=1, max_length=1500)

    @field_validator("question")
    @classmethod
    def validate_question(cls, v):
        if not v.strip():
            raise ValueError("質問は空白だけではいけません。")
        return v
    

class ChatOutput(BaseModel):
    """チャットボットの出力データの仕様書"""
    answer: str