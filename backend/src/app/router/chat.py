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
        chat_responses = await asyncio.gather(
            *[_runner(q) for q in questions]  # これはforループの各質問を並列処理する。
        )
        
        # ChatResponseオブジェクトからAnswerItemsに変換
        responses = [
            {
                "question": q, 
                "answer": resp.answer,
                "sources": [
                    {"title": src.title, "url": src.url, "page": src.page}
                    for src in resp.sources
                ] if resp.sources else None
            } 
            for q, resp in zip(questions, chat_responses)
        ]
        
        return ChatOutput(responses=responses)

        
    except Exception as e:
        # エラーログなどはここで処理
        raise HTTPException(status_code=500, detail=str(e))