# Loaderの設計としての役割　->　ETL設計(Extract(抽出), Transform(データの変換), Load(格納))

#===　1.モジュール等の事前準備の段階 ===#
import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src import config


class AozoraLoader:
    def __init__(self, url:str):
        self._url = url
        self._text_splitter = RecursiveCharacterTextSplitter(chunk_size=config.CHUNK_SIZE, chunk_overlap=config.CHUNK_OVERLAP)
    
    @property
    def url(self):
        return self._url
    
    @property
    def text_splitter(self):
        return self._text_splitter

    def _extract(self):
        loader = WebBaseLoader(
            web_path = (self.url,),
            bs_kwargs = dict(
                parse_only = bs4.SoupStrainer(class_="main_text")
            ))
        return loader.load()# メゾットとしてのload。関数としてのloadではないことに注意。
    
    def _transform(self, docs):
        return self.text_splitter.split_documents(docs)
        
    
    def doc_load(self):
        raw_docs = self._extract()
        return self._transform(raw_docs)

# このクラス分けは、まず__init__で変数の隠蔽を行う。
# @poertyでinitの中身を外部から参照できるようにすると同時に、のちにurlという変数の変更や、textsplitteのモジュールの変更の際に、ここを変更すればよいようにする。
# extract, tranceform, loadの3つのメゾットを用意し、最終的にtranceformを呼び出すので、doc_loadでまとめて呼び出せるようにする。









