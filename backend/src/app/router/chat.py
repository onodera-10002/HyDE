# routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from src.schemas import ChatInput, ChatOutput
from src.bot import ChatBot
from src.app.dependencies import get_bot # さっき作った依存関係
import asyncio

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatOutput)
async def chat_endpoint(
    payload: ChatInput, 
    bot: ChatBot = Depends(get_bot) # ここで準備済みのBotを受け取る
):
    sem = asyncio.Semaphore(3)

    async def _runner(q):
        async with sem:  # 整理券を取る（なければ待つ）
            return await bot.run(q)
        
    # ユーザーの質問
    questions = payload.questions

    try:
        answers = await asyncio.gather(
            *[_runner(q) for q in questions]  # これはforループの各質問を並列処理する。
        )
        
        # 質問と回答をペアリング
        responses = [
            {"question": q, "answer": a} 
            for q, a in zip(questions, answers)
        ]
        
        return ChatOutput(responses=responses)

        
    except Exception as e:
        # エラーログなどはここで処理
        raise HTTPException(status_code=500, detail=str(e))