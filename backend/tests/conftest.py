import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.documents import Document
from src.bot import ChatBot

# =========モックを作成する基準3選========= #
# 1.外部APIや外部サービスを介してしまうもの
# 2.実行に時間がかかるもの
# 3.一貫した結果を返さないもの（ランダム性がある等）

# 全てのテストで使える「偽のVectorStore」
@pytest.fixture
def mock_vector_db():
    db = MagicMock()
    
    # searchメソッドが呼ばれたら、この「ダミーデータ」を返すように設定
    # 本物のDBには繋ぎに行かせない！
    db.search.return_value = [
        Document(page_content="これはテスト用のドキュメントAです。"),
        Document(page_content="これはテスト用のドキュメントBです。")
    ]
    return db

@pytest.fixture
def mock_chatbot(mock_vector_db):
    """正常系のテスト: ChatBot.runが期待通りに動作するか"""
    # 準備
    with patch("src.bot.init_chat_model") as mock_init_chat_model,\
         patch("src.bot.PromptTemplate"):
    #=======回答を生成するためのllmをモック化=======#
        mock_llm = AsyncMock()
        mock_init_chat_model.return_value = mock_llm

    #=======botの設定=======#
        template = "質問: {question}\nコンテキスト"
        hyde_template = "仮想ドキュメントを作成します。"
        bot = ChatBot(
            template = template,
            hyde_template = hyde_template,
            vector_db = mock_vector_db,
        )

        bot._hyde_chain = MagicMock()
        bot._hyde_chain.invoke.return_value = "事前生成のクエリ。"

        bot._graph = AsyncMock()
        bot._graph.ainvoke.return_value = {"answer": "テスト成功です！"}

    yield bot




        


