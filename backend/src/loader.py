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
    
    def _transform(self, docling_doc):
        # HybridChunkerで構造を維持したまま分割（ValidationErrorを回避）
        document_chunks = list(self.text_splitter.chunk(docling_doc))
        
        normalized_results = []
        source_url = self.source # コンストラクタ等で保持しているソース名
        
        for chunk in document_chunks:
            # 1. チャンクをテキスト化（表などはここでMarkdownになる）
            raw_text = self.text_splitter.serialize(chunk)
            
            # 2. テキストの正規化 (neologdnで掃除)
            clean_text = neologdn.normalize(raw_text)
            
            # 3. ページ番号の復元（チャンクのメタデータから取得）
            page_no = "?"
            if chunk.meta.doc_items:
                # 最初の要素のprovからページ番号を特定
                p = chunk.meta.doc_items[0].prov[0] if chunk.meta.doc_items[0].prov else None
                page_no = getattr(p, "page_no", "?")

            # 4. 「self_ref」などのノイズがない場合のみ、最終リストに追加
            if clean_text.strip() and "self_ref" not in clean_text:
                normalized_results.append({
                    "content": clean_text,
                    "page_no": page_no,
                    "source": source_url,
                    "headings": chunk.meta.headings # 章の見出し情報も追加
                })
        return normalized_results
    
    def _normalization(self, docs, WEB_URL=None):
        if WEB_URL is None:
            WEB_URL = self.source
        raw_text = self.text_splitter.serialize(docs)
        # テキストを正規化
        clean_text = neologdn.normalize(raw_text)
        # ページ番号を取得（チャンクに含まれる最初のアイテムから）
        page_no = "?"
        if chunk.meta.doc_items:
            p = chunk.meta.doc_items[0].prov[0] if chunk.meta.doc_items[0].prov else None
            page_no = getattr(p, "page_no", "?")

        return {
            "content": clean_text,
            "page_no": page_no,
            "source": self.source,
            "headings": chunk.meta.headings
        }

    
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
            # 辞書ではなく、DoclingDocumentオブジェクトそのものを返す
            result = self._converter.convert(self.source)
            return result.document
        except Exception as e:
            print(f"Extraction Error: {e}")
            return None






