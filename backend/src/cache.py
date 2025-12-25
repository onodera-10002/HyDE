from langchain_core.documents import Document
from src.vector_store import Vectorstore
from logger import get_logger

logger = get_logger("SemanticCache")

class SemanticCache:
    def __init__(self, embedding_model:str, threshold:float = 0.2):
        self._vector_store = Vectorstore(embedding_model=embedding_model, collection_name="SemanticCache")
        self._threshold = threshold

    def _check(self, query:str):
        result = self._vector_store.search_score(query=query, k=1)
        if not result:
            return None
        doc, score = result[0]
        if score < self._threshold:
            return doc.metadata.get("answer")
    
    def add_question_answer(self, question:str, answer:str):
        doc = Document(
            page_content=question,
            metadata={"answer": answer}
        )
        self._vector_store.add([doc], batch_size=1, sleep_time=0)