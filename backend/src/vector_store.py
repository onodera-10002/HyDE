# このファイルの設計思想：
# 埋め込みモデルでembeddingを作成する。
# ベクトルストアを定義する。
# ドキュメントをロードし、ベクトルストアに追加する。

#===　1.モジュール等の事前準備の段階 ===#
from src import config
from time import sleep
from logger import get_logger
import time
from pinecone import Pinecone
import uuid
from langchain_core.documents import Document

logger = get_logger(__name__)
class Vectorstore:
    def __init__(self):
        self._pc = Pinecone(api_key=config.PINECONE_API_KEY)
        self._index_name = "rag-hyde-database"
        self._index = self._pc.Index(name=self._index_name)
        
    
    def add(self, chunks):
        try:
            records = []
            for item in chunks:
                # Document型とDict型の両方に対応
                if isinstance(item, Document):
                    # Document型の場合
                    content = item.page_content
                    page_no = item.metadata.get("page", item.metadata.get("page_no", "?"))
                    source = item.metadata.get("source_file", item.metadata.get("source", "Unknown"))
                elif isinstance(item, dict):
                    # Dict型の場合
                    content = item["content"]
                    page_no = item["page_no"]
                    source = item["source"]
                else:
                    logger.warning(f"⚠️ Unknown document type: {type(item)}")
                    continue
                
                records.append({
                    "_id": str(uuid.uuid4()),      # 一意のID
                    "text": content, # ここがベクトル化される（field_mapで指定したキー）
                    "page_no": page_no,   # これ以降は自動的にメタデータになる
                    "source": source,
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
                        self._index.upsert_records(namespace="rag-hyde-database", records=batch)

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
        from langchain_core.documents import Document
        
        # 検索の実行
        response = self._index.search(
            namespace=self._index_name,
            query={
                "inputs": {"text": query}, 
                "top_k": k                  
            },
            fields=["text", "page_no", "source"]  # chunk_textではなくtext
        )
        
        # Pineconeの結果をDocument型に変換
        documents = []
        
        # Pineconeのレスポンス構造: response.result.hits
        if hasattr(response, 'result') and hasattr(response.result, 'hits'):
            hits = response.result.hits
            for item in hits:
                fields = item.get('fields', {})
                doc = Document(
                    page_content=fields.get("text", ""),  # chunk_textではなくtext
                    metadata={
                        "page_no": fields.get("page_no", "?"),
                        "source": fields.get("source", "Unknown"),
                        "score": item.get("_score", 0.0),
                        "id": item.get("_id", "")
                    }
                )
                documents.append(doc)
        
        return documents
