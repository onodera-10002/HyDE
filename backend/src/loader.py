# Loaderの設計としての役割　->　ETL設計(Extract(抽出), Transform(データの変換), Load(格納))

#===　1.モジュール等の事前準備の段階 ===#
from abc import ABC, abstractmethod
import os
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src import config
from logger import get_logger
from docling.document_converter import DocumentConverter
from docling.datamodel.document import TableItem
import neologdn
import pandas as pd
from docling.chunking import HybridChunker

class BaseLoader(ABC):
    def __init__(self, source:str):
        self._source = source
        self._text_splitter = HybridChunker()
        self._logger = get_logger(__name__)
        self._converter = DocumentConverter()

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
        return self.text_splitter.chunk(docs)
    
    def _normalization(self, docs, WEB_URL=None):
        if WEB_URL is None:
            WEB_URL = self.source
        document = docs
        clean_document = []
        for item, _ in document.iterate_items():
            content = ""
            p = item.prov[0]
            page_no = p.page_no
            if item.label in config.NORMALIZE_LABELS:
                if hasattr(item, "text") and item.text:
                    item.text = neologdn.normalize(item.text)
                    content = item.text
                    

            elif item.label == "table":
                if isinstance(item, TableItem):
                    df = item.export_to_dataframe(document)
                    df_cleaned = df.map(lambda x: neologdn.normalize(str(x)) if pd.notnull(x) else "")
                    content = df_cleaned.to_markdown(index=False)
            else:
                content = item
            if isinstance(content, str) and content.strip():
                if "self_ref" not in content:
                    clean_document.append({
                    "content": content,
                    "page_no": page_no,
                    "source": WEB_URL
                })
                    
        return clean_document, print(clean_document)

    
    def load(self):
        clean_docs = self._extract()
        return self._transform(clean_docs)


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
            DoclingDocument = self._converter.convert(self.source).document
            return self._normalization(DoclingDocument)
        except Exception as e:
            self._logger.error(f"ドキュメントの抽出中にエラーが発生しました: {e}")
            raise ValueError(f"ドキュメントの抽出中にエラーが発生しました: {e}") from e








