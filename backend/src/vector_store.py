# このファイルの設計思想：
# 埋め込みモデルでembeddingを作成する。
# ベクトルストアを定義する。
# ドキュメントをロードし、ベクトルストアに追加する。

#===　1.モジュール等の事前準備の段階 ===#
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector  # 新しい主役！
from src import config
from time import sleep
from logger import get_logger

logger = get_logger(__name__)
class Vectorstore:
    def __init__(self, embedding_model:str, collection_name:str = "RaAG_docs"):
        self._embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        self._connection_url = f"postgresql+psycopg2://{config.USER}:{config.PASSWORD}@{config.HOST}:{config.PORT}/{config.DBNAME}"
        self._store = PGVector(
            embeddings=self._embeddings,
            collection_name=collection_name, # テーブル名のようなもの
            connection=self._connection_url,
            use_jsonb=True,
        )
        
    
    def add(self, chunks, batch_size:int, sleep_time:int):
        try:
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                self._store.add_documents(documents=batch)
                if i + batch_size < len(chunks):
                    sleep(sleep_time)
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")

    def search(self, query:str, k:int):
        return self._store.similarity_search(query=query, k=k)

    def search_score(self, query:str, k:int):
        return self._store.similarity_search_with_score(query=query, k=k)