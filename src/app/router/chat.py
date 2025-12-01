# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas import ChatInput, ChatOutput
from src.bot import ChatBot
from src.app.dependencies import get_bot # さっき作った依存関係

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatOutput)
def chat_endpoint(
    payload: ChatInput, 
    bot: ChatBot = Depends(get_bot) # ここで準備済みのBotを受け取る
):
    # ユーザーの質問
    question = payload.question
    try:
        answer_text = bot.run(question)
        
        return ChatOutput(answer=answer_text)
        
    except Exception as e:
        # エラーログなどはここで処理
        raise HTTPException(status_code=500, detail=str(e))