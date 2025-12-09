# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.router import upload
from src.app.router import chat
from src.app.dependencies import set_bot
from logger import get_logger

# あなたの作成したモジュールをインポート
from src import config
from src.vector_store import Vectorstore
from src.bot import ChatBot
from fastapi.middleware.cors import CORSMiddleware
from src.factories import Factories

# グローバル変数として保持（簡易的な実装）
# 実際は app.state に持たせるのがきれいですが、わかりやすさ優先でここに書きます
bot_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリ起動時に1回だけ実行される処理
    ここで重たい処理（データのロード、VectorStoreの構築）を済ませる
    """
    logger = get_logger("Lifespan")
    logger.info("🚀 System Starting... Loading Data...")

    # 1. データのロード (ETL)
    loader = Factories.choiseloader(config.WEB_PATH)
    docs = loader.load()
    logger.info(f"✅ Loaded {len(docs)} chunks from {config.WEB_PATH}.")

    # 2. VectorStoreの初期化
    vector_store = Vectorstore(config.EMBEDDING_MODEL, collection_name="RAG_docs")
    app.state.vector_store = vector_store  # FastAPIのstateにも保存しておく

    # 3. ChatBotのインスタンス化 (ここで作成した vector_store を渡す)
    bot_instance = ChatBot(
        template=config.TEMPLATE,
        hyde_template=config.HYDE_TEMPLATE,
        vector_db=vector_store
    )
    set_bot(bot_instance)
    logger.info("🤖 Bot is ready!")

    yield  # ここでアプリが稼働開始

    # 終了時の処理（必要なら）
    logger.info("🛑 System Shutdown.")
    set_bot(None)
    bot_instance = None


# アプリ作成
app = FastAPI(lifespan=lifespan, title="Aozora RAG API")



# === CORS設定 (Security Policy) ===
    
    # 1. 許可するオリジン（アクセス元）のリスト
    # 本番環境(Production)と開発環境(Development)で分けるのが定石
origins = [
        "http://localhost:3000",    # React (Create React App)
        "http://127.0.0.1:3000",    # 上記のIP指定版
        "http://localhost:5173",    # React (Vite)
        "http://127.0.0.1:5173",    # 上記のIP指定版
        # "https://your-production-app.vercel.app", # 本番デプロイ時のURL
    ]

app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,      # 招待リスト（これ以外はブロック）
        allow_credentials=True,     # Cookie/認証ヘッダーの許可
        allow_methods=["*"],        # 許可するHTTPメソッド (GET, POST...)
        allow_headers=["*"],        # 許可するHTTPヘッダー
    )
    
app.include_router(chat.router)
app.include_router(upload.router)

if __name__ == "__main__":
    import uvicorn
    # ここで自分自身(app)を起動させる
    # reload=True は開発中便利ですが、この起動方法だと効かないことがあるので
    # コードを書き換えたら手動で再起動が必要になる場合があります
    uvicorn.run(app, host="127.0.0.1", port=8005)