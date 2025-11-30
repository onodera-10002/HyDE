import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

# srcが見つからない問題の防止
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src import config
from src.loader import AozoraLoader
from src.vector_store import Vectorstore # VectorDBに直したならそっちで
from src.bot import ChatBot
from src.schemas import ChatInput, ChatOutput
from logger import get_logger

logger = get_logger("API")

# === 1. 起動時の準備 (Lifespan) ===
# サーバーが立ち上がっている間だけメモリに保持する変数
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- 起動時 (Startup) ---
    logger.info("🚀 API Server Starting...")
    
    try:
        # 1. データの準備 (重い処理はここで1回だけやる！)
        logger.info(f"📡 Loading data from: {config.WEB_PATH}")
        loader = AozoraLoader(url=config.WEB_PATH)
        chunks = loader.load()
        
        logger.info("💾 Indexing to VectorDB...")
        db = Vectorstore(embedding_model=config.EMBEDDING_MODEL)
        db.add(chunks)
        
        # 2. Botの生成
        logger.info("🤖 Initializing ChatBot...")
        bot = ChatBot(
            template=config.TEMPLATE,
            hyde_template=config.HYDE_TEMPLATE,
            vector_db=db
        )
        
        # グローバル辞書に保存（これでAPI全体から使える）
        models["bot"] = bot
        logger.info("✅ Ready to accept requests!")
        
        yield # ここでAPIが稼働する
        
    except Exception as e:
        logger.error(f"❌ Critical Error during startup: {e}")
        raise e
    
    # --- 終了時 (Shutdown) ---
    logger.info("👋 API Server Shutting down...")
    models.clear()

# === 2. アプリ定義 ===
app = FastAPI(title="RAG ChatBot API", lifespan=lifespan)

# === 3. エンドポイント (窓口) ===

@app.get("/")
def health_check():
    """生存確認用"""
    return {"status": "ok"}

@app.post("/chat", response_model=ChatOutput)
def chat(payload: ChatInput):
    """
    チャットのエンドポイント
    - 入力: ChatInput (Pydanticでバリデーション済み)
    - 出力: ChatOutput
    """
    # 準備しておいたBotを取り出す
    bot = models.get("bot")
    
    if not bot:
        logger.error("Bot is not initialized.")
        raise HTTPException(status_code=500, detail="Server not ready")

    question = payload.question
    logger.info(f"📩 Request: {question}")

    try:
        # Botを実行
        answer = bot.run(question)
        logger.info("📤 Response sent.")
        
        # 定義した型に入れて返す
        return ChatOutput(answer=answer)

    except Exception as e:
        logger.error(f"❌ Error handling request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")