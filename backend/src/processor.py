import shutil
import os
from pathlib import Path
from fastapi import UploadFile
from langchain_core.documents import Document
# あなたが定義したPDFLoaderをインポート
from src.loader import PDFLoader


class DocumentProcessor:
    def __init__(self, upload_dir: str = "temp_uploads"):
        self._upload_dir = Path(upload_dir)
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        
    
    async def process(self, file: UploadFile, user_title: str) -> list[Document]:
        file_path = self._upload_dir / file.filename
        try:
            # 1. 一時保存
            await self._save_temp_file(file, file_path)
            
            # 2. 読み込み (PDFPlumberLoader使用)
            loader = PDFLoader(source=str(file_path))
            documents = loader.load()
            
            # 3. メタデータ正規化 (ページ付与・タイトル注入)
            enriched_docs = self._enrich_metadata(documents, user_title, file.filename)
            
            return enriched_docs

        finally:
            # 4. 後片付け (必ず実行される)
            self._cleanup(file_path)

    async def _save_temp_file(self, file: UploadFile, path: Path):
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    def _enrich_metadata(self, documents: list[Document], user_title: str, filename: str) -> list[Document]:
        for doc in documents:
            # ページ番号をメタデータに追加
            if "page" not in doc.metadata:
                doc.metadata["page"] = "Unknown"
            doc.metadata["user_title"] = user_title
            doc.metadata["source_file"] = filename
            doc.metadata["page_info"] = doc.metadata["page"] + 1
        return documents
    
    def _cleanup(self, path: Path):
        if path.exists():
            os.remove(path)
            