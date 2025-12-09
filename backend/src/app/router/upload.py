from fastapi import APIRouter, UploadFile, Form, HTTPException
from src.processor import DocumentProcessor
from langchain_core.documents import Document

router = APIRouter()

@router.post("/upload", operation_id="upload_file")
async def upload_file(file:UploadFile, title:str = Form(...)) -> list[Document]:
    """
    ファイルをアップロードし、ドキュメントとして処理します。
    
    - **file**: アップロードするファイル
    - **title**: ユーザーが指定するタイトル
    """
    try:
        processor = DocumentProcessor()
        documents = await processor.process(file, user_title=title)
        return documents
    except Exception as e:
        return HTTPException(status_code=500, detail={"error": str(e)})
