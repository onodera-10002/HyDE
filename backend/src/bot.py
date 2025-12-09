#===　1.モジュール等の事前準備の段階 ===#
from langchain.chat_models import init_chat_model
from langchain_core.documents import Document
from typing_extensions import List, TypedDict
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import START, StateGraph
from src.vector_store import Vectorstore
from src import config
from src.cache import SemanticCache
from logger import get_logger
from pydantic import ValidationError, BaseModel
from typing import Optional


class SourceInfo(BaseModel):
    title: Optional[str] = None
    url: str
    page: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceInfo] = []


class State(TypedDict):
        question: str
        context: List[Document]
        answer: str
        pre_query: str


class ChatBot:
    def __init__(self, template:str, hyde_template:str, vector_db: Vectorstore, chat_model=config.CHAT_MODEL, model_provider=config.MODEL_PROVIDER):
        self._template = template
        self._hyde_template = hyde_template
        self._vector_db = vector_db
        self._llm = init_chat_model(chat_model, model_provider=model_provider, max_retries=3, timeout=30)
        hyde_prompt = PromptTemplate.from_template(self._hyde_template)
        self._prompt = PromptTemplate.from_template(self._template)
        self._hyde_chain = hyde_prompt | self._llm | StrOutputParser()
        self._graph = self._graph_builder()
        self._logger = get_logger(__name__)
        self._cache = SemanticCache(embedding_model=config.EMBEDDING_MODEL)
    
    def _hyde_preparation(self, state:State):
        original_question = state["question"]
        hypothetical_document = self._hyde_chain.invoke({"question": original_question})
        return {"pre_query": hypothetical_document}


    def _retrieve(self, state: State):
        pre_query = state["pre_query"]
        try:
            retrieved_docs = self._vector_db.search(
                query = pre_query,
                k=config.RETRIEVER_K
            )
            return {"context": retrieved_docs}
        except Exception as e:
            self._logger.error(f"ドキュメントの検索中にエラーが発生しました: {e}")
            return {"context": []}
        

    async def _generate(self, state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        if not docs_content:
            return {"answer": "申し訳ありませんが、関連する情報が見つかりませんでした。別の質問をお試しください。"}
        messages = self._prompt.invoke({"question": state["question"], "context": docs_content})
        response = await self._llm.ainvoke(messages)

        return {"answer": response.content}
    

    def _graph_builder(self):
        builder = StateGraph(State)
        # src/bot.py の _build_graph メソッド内
        # # 1. ノードを登録
        builder.add_node("hyde", self._hyde_preparation)
        builder.add_node("retrieve", self._retrieve)
        builder.add_node("generate", self._generate)
        builder.add_edge(START, "hyde")
        builder.add_edge("hyde", "retrieve")
        builder.add_edge("retrieve", "generate")
        return builder.compile()


    async def run(self, question: str) -> ChatResponse:
        try:
            cache_check = self._cache._check(question)
            if cache_check:
                self._logger.info(f"Cache hit!: {cache_check}")
                return ChatResponse(answer=cache_check, sources=[])
        
            ans = await self._graph.ainvoke({"question": question})
            
            # デバッグ: ansのデータ構造を確認
            self._logger.info(f"ans type: {type(ans)}")
            self._logger.info(f"ans keys: {ans.keys() if isinstance(ans, dict) else 'not a dict'}")
            self._logger.info(f"ans content: {ans}")
            
            self._cache.add_question_answer(question, ans["answer"])
            sources_info = ans.get("context", [])
            
            # デバッグ: メタデータ構造を確認
            if sources_info:
                self._logger.info(f"First document metadata: {sources_info[0].metadata if sources_info else 'No docs'}")
            
            sources_list = [
                SourceInfo(
                    title=s.metadata.get("user_title"),
                    url=f"/files/{s.metadata.get('source_file')}",
                    page=s.metadata.get("page_info")
                )
                for s in sources_info
            ]
            return ChatResponse(answer=ans["answer"], sources=sources_list)
        except ValidationError as e:
            self._logger.error(f"question is empty: {e}")
            error_msg = e.errors()[0]['msg']
            return f"⚠️ 入力エラー: {error_msg}"