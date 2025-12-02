from pydantic import BaseModel, Field, field_validator, model_validator

class ChatInput(BaseModel):
    
    question: str | None = Field(None, min_length=1, max_length=1500)
    questions: list[str] | None = Field(None, min_length=1, max_length=10, examples=["質問1", "質問2"])

@model_validator(mode='after')
def validate_input(self):
        # どちらか一方は必須
        if not self.question and not self.questions:
            raise ValueError("questionまたはquestionsのいずれかを指定してください。")
        
        # 両方指定はNG
        if self.question and self.questions:
            raise ValueError("questionとquestionsは同時に指定できません。")
        
        # questionsの各要素をチェック
        if self.questions:
            for q in self.questions:
                if not q.strip():
                    raise ValueError("質問は空白だけではいけません。")
                if len(q) > 1500:
                    raise ValueError("各質問は1500文字以内にしてください。")
        
        # questionのチェック
        if self.question and not self.question.strip():
            raise ValueError("質問は空白だけではいけません。")
        
        return self
    

class ChatOutput(BaseModel):
    """チャットボットの出力データの仕様書"""
    answer: str | None = None
    responses: list[dict] | None = None