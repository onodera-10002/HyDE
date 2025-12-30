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
import time
from pinecone import Pinecone
import uuid

logger = get_logger(__name__)
class Vectorstore:
    def __init__(self, embedding_model:str):
        self._embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        self._pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self._index_name = "rag-hyde-database"
        self._index = self._pc.Index(name=self._index_name)
        
    
    def add(self, chunks):
        try:
            records = []
            for doc in chunks:
                records.append({
                    "_id": str(uuid.uuid4()),      # 一意のID
                    "chunk_text": doc["content"], # ここがベクトル化される（field_mapで指定したキー）
                    "page_no": doc["page_no"],   # これ以降は自動的にメタデータになる
                    "source": doc["source"],
                })
                # リトライロジック（API制限対策）
            max_retries = 3
            retry_delay = 30  # 30秒待機
                
            for attempt in range(max_retries):
                try:
                    if not self._pc.has_index(self._index_name):
                        self._pc.create_index_for_model(
                            name=self._index_name,
                            cloud="aws",
                            region="us-east-1",
                            embed={
                                "model":"llama-text-embed-v2",
                                "field_map":{"text": "chunk_text"}
                                }
                                )
                    for j in range(0, len(records), config.BATCH_SIZE):
                        batch = records[j : j + config.BATCH_SIZE]
                        self._index.upsert_records(namespace=self._index_name, records=batch)

                    logger.info(f"Batch {j//config.BATCH_SIZE + 1} added successfully")
                    break
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "quota" in error_msg.lower():
                        if attempt < max_retries - 1:
                            logger.warning(f"⚠️ Rate limit hit. Waiting {retry_delay} seconds before retry {attempt + 1}/{max_retries}...")
                            time.sleep(retry_delay)
                            retry_delay *= 2  # 指数バックオフ
                        else:
                            logger.error(f"❌ Rate limit exceeded after {max_retries} retries")
                            raise
                    else:
                        raise
                
        except Exception as e:
            logger.error(f"❌ Error adding documents to vector store: {e}")
            raise

    def search(self, query:str, k:int):
        return self._store.similarity_search(query=query, k=k)

    def search_score(self, query:str, k:int):
        return self._store.similarity_search_with_score(query=query, k=k)