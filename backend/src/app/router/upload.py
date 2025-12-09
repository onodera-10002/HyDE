from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from pydantic import BaseModel
from src.processor import DocumentProcessor
from langchain_core.documents import Document


router = APIRouter()
class UploadResponse(BaseModel):
    message: str
    processed_pages: int
    
@router.post("/upload", operation_id="upload_file", response_model=UploadResponse)
async def upload_file(request: Request, file:UploadFile, title:str = Form(...)) -> list[Document]:
    """
    ファイルをアップロードし、ドキュメントとして処理します。
    
    - **file**: アップロードするファイル
    - **title**: ユーザーが指定するタイトル
    """
    try:
        processor = DocumentProcessor()
        documents = await processor.process(file, user_title=title)
        vector_store = request.app.state.vector_store
        vector_store.add(documents, batch_size=50, sleep_time=4)
        return {
            "message": f"Successfully processed '{title}'",
            "processed_pages": len(documents)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
