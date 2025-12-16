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
            logger.info(f"Adding {len(chunks)} chunks to vector store in batches of {batch_size}")
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} documents")
                
                # リトライロジック（API制限対策）
                max_retries = 3
                retry_delay = 30  # 30秒待機
                
                for attempt in range(max_retries):
                    try:
                        self._store.add_documents(documents=batch)
                        logger.info(f"Batch {i//batch_size + 1} added successfully")
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
                
                if i + batch_size < len(chunks):
                    logger.info(f"Sleeping for {sleep_time} seconds...")
                    sleep(sleep_time)
            logger.info(f"✅ All {len(chunks)} chunks added to vector store")
        except Exception as e:
            logger.error(f"❌ Error adding documents to vector store: {e}")
            raise

    def search(self, query:str, k:int):
        return self._store.similarity_search(query=query, k=k)

    def search_score(self, query:str, k:int):
        return self._store.similarity_search_with_score(query=query, k=k)