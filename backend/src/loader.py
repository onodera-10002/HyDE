# Loaderの設計としての役割　->　ETL設計(Extract(抽出), Transform(データの変換), Load(格納))

#===　1.モジュール等の事前準備の段階 ===#
from abc import ABC, abstractmethod
import os
import bs4
from langchain_community.document_loaders import WebBaseLoader, PDFMinerLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src import config
from logger import get_logger


class BaseLoader(ABC):
    def __init__(self, source:str):
        self._source = source
        self._text_splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
        self._logger = get_logger(__name__)

    @property
    def source(self):
        return self._source
    
    @property
    def text_splitter(self):
        return self._text_splitter

    @abstractmethod
    def _extract(self):
        pass
    
    def _transform(self, docs):
        return self.text_splitter.split_documents(docs)
        
    
    def load(self):
        raw_docs = self._extract()
        return self._transform(raw_docs)

# このクラス分けは、まず__init__で変数の隠蔽を行う。
# @poertyでinitの中身を外部から参照できるようにすると同時に、のちにurlという変数の変更や、textsplitteのモジュールの変更の際に、ここを変更すればよいようにする。
# extract, tranceform, loadの3つのメゾットを用意し、最終的にtranceformを呼び出すので、doc_loadでまとめて呼び出せるようにする。


class AozoraLoader(BaseLoader):
    def _extract(self):
        try:
            loader = WebBaseLoader(
                web_path = (self.source,),
                bs_kwargs = dict(
                    parse_only = bs4.SoupStrainer(class_="main_text")
                ),
                requests_kwargs=dict(timeout=30)
                )
            return loader.load()# メゾットとしてのload。関数としてのloadではないことに注意.
        except Exception as e:
            self._logger.error(f"ドキュメントの抽出中にエラーが発生しました: {e}")
            raise ValueError(f"ドキュメントの抽出中にエラーが発生しました: {e}") from e

class PDFLoader(BaseLoader):
    def _extract(self):
        try:
            if not os.path.exists(self.source):
                raise FileNotFoundError(f"The file at {self.source} was not found.")
            
            loader = PDFMinerLoader(file_path=self.source)
            return loader.load()
        except Exception as e:
            self._logger.error(f"ドキュメントの抽出中にエラーが発生しました: {e}")
            raise ValueError(f"ドキュメントの抽出中にエラーが発生しました: {e}") from e








