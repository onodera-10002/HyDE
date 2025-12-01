# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.router import chat
from src.app.dependencies import set_bot

# あなたの作成したモジュールをインポート
from src import config
from src.loader import AozoraLoader
from src.vector_store import Vectorstore
from src.bot import ChatBot

# グローバル変数として保持（簡易的な実装）
# 実際は app.state に持たせるのがきれいですが、わかりやすさ優先でここに書きます
bot_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    アプリ起動時に1回だけ実行される処理
    ここで重たい処理（データのロード、VectorStoreの構築）を済ませる
    """
    print("🚀 System Starting... Loading Data...")

    # 1. データのロード (ETL)
    loader = AozoraLoader(config.WEB_PATH)
    docs = loader.load()
    print(f"✅ Loaded {len(docs)} chunks from Aozora.")

    # 2. VectorStoreの初期化
    vector_store = Vectorstore(config.EMBEDDING_MODEL)
    vector_store.add(docs)
    print("✅ VectorStore Initialized.")

    # 3. ChatBotのインスタンス化 (ここで作成した vector_store を渡す)
    bot_instance = ChatBot(
        template=config.TEMPLATE,
        hyde_template=config.HYDE_TEMPLATE,
        vector_db=vector_store
    )
    set_bot(bot_instance)
    print("🤖 Bot is ready!")

    yield  # ここでアプリが稼働開始

    # 終了時の処理（必要なら）
    print("🛑 System Shutdown.")
    set_bot(None)
    bot_instance = None

# アプリ作成
app = FastAPI(lifespan=lifespan, title="Aozora RAG API")
app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    # ここで自分自身(app)を起動させる
    # reload=True は開発中便利ですが、この起動方法だと効かないことがあるので
    # コードを書き換えたら手動で再起動が必要になる場合があります
    uvicorn.run(app, host="127.0.0.1", port=8004)