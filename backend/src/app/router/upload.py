from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from pydantic import BaseModel
from src.processor import DocumentProcessor
from langchain_core.documents import Document
from logger import get_logger

logger = get_logger(__name__)

router = APIRouter()
class UploadResponse(BaseModel):
    message: str
    processed_pages: int
    
@router.post("/upload", operation_id="upload_file", response_model=UploadResponse)
async def upload_file(request: Request, file:UploadFile, title:str = Form(...)) -> UploadResponse:
    """
    ファイルをアップロードし、ドキュメントとして処理します。
    
    - **file**: アップロードするファイル
    - **title**: ユーザーが指定するタイトル
    """
    try:
        logger.info(f"📥 Uploading file: {file.filename}, title: {title}")
        processor = DocumentProcessor()
        documents = await processor.process(file, user_title=title)
        logger.info(f"📄 Processed {len(documents)} documents")
        
        vector_store = request.app.state.vector_store
        logger.info(f"💾 Adding documents to vector store...")
        # レート制限対策: バッチサイズを小さく、待機時間を長く
        vector_store.add(documents, batch_size=10, sleep_time=10)
        logger.info(f"✅ Successfully added {len(documents)} documents to vector store")
        
        return UploadResponse(
            message=f"Successfully processed '{title}'",
            processed_pages=len(documents)
        )

    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
