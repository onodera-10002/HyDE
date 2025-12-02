# このファイルの設計思想：
# 埋め込みモデルでembeddingを作成する。
# ベクトルストアを定義する。
# ドキュメントをロードし、ベクトルストアに追加する。

#===　1.モジュール等の事前準備の段階 ===#
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore

class Vectorstore:
    def __init__(self, embedding_model:str):
        self._embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model)
        self._vector_store = InMemoryVectorStore(self._embeddings)
        
    
    def add(self, chunks):
        self._vector_store.add_documents(documents=chunks)


    def search(self, query:str, k:int):
        return self._vector_store.similarity_search(query=query, k=k)

