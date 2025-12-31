from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from pydantic import BaseModel
from logger import get_logger
from pathlib import Path
import shutil
import os
from src.factories import Factories

logger = get_logger(__name__)

router = APIRouter()

class UploadResponse(BaseModel):
    message: str
    processed_pages: int


async def _save_temp_file(file: UploadFile, path: Path):
    """ファイルを一時的に保存"""
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)


def _cleanup(path: Path):
    """一時ファイルを削除"""
    if path.exists():
        os.remove(path)


@router.post("/upload", operation_id="upload_file", response_model=UploadResponse)
async def upload_file(request: Request, file: UploadFile, title: str = Form(...)) -> UploadResponse:
    """
    ファイルをアップロードし、ドキュメントとして処理します。
    
    - **file**: アップロードするファイル
    - **title**: ユーザーが指定するタイトル
    """
    upload_dir = Path("temp_uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / file.filename
    
    try:
        logger.info(f"📥 Uploading file: {file.filename}, title: {title}")
        
        # 1. ファイルを一時保存
        await _save_temp_file(file, file_path)
        
        # 2. Loaderでファイルを読み込み（Dict型のリストが返る）
        loader = Factories.choiseloader(source=str(file_path))
        documents = loader.load()
        logger.info(f"📄 Loaded {len(documents)} document chunks")
        
        # 3. vector_storeに追加（Dict型をそのまま渡す）
        vector_store = request.app.state.vector_store
        logger.info(f"💾 Adding documents to vector store...")
        vector_store.add(documents)
        logger.info(f"✅ Successfully added {len(documents)} documents to vector store")
        
        return UploadResponse(
            message=f"Successfully processed '{title}'",
            processed_pages=len(documents)
        )

    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 4. 一時ファイルを削除
        _cleanup(file_path)
