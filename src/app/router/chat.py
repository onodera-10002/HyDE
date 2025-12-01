# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas import ChatInput, ChatOutput
from src.bot import ChatBot
from app.dependencies import get_bot # さっき作った依存関係

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatOutput)
def chat_endpoint(
    payload: ChatInput, 
    bot: ChatBot = Depends(get_bot) # ここで準備済みのBotを受け取る
):
    # ユーザーの質問
    question = payload.question
    
    try:
        # あなたの作った bot.run() を実行
        # 注意: bot.run の戻り値が単なる str なのか List[str] なのか確認してください。
        # 現在のあなたのコードでは List[str] の型ヒントですが、実際は answer["answer"] (str) を返しています。
        answer_text = bot.run(question)
        
        return ChatOutput(answer=answer_text)
        
    except Exception as e:
        # エラーログなどはここで処理
        raise HTTPException(status_code=500, detail=str(e))