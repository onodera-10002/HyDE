"""
Document型とDict型の不一致をテストする
"""
from langchain_core.documents import Document
import pytest


def test_document型がdict型としてアクセスされるとエラーになる():
    """
    Document型はdictではないので、doc["key"]のようにアクセスできない
    """
    doc = Document(
        page_content="テスト内容",
        metadata={"page_no": 1, "source": "test.pdf"}
    )
    
    # Document型は辞書のようにアクセスできない
    with pytest.raises(TypeError):
        _ = doc["content"]  # これはエラーになる
    
    with pytest.raises(TypeError):
        _ = doc["page_no"]  # これもエラーになる


def test_document型の正しいアクセス方法():
    """
    Document型の正しいアクセス方法を確認
    """
    doc = Document(
        page_content="テスト内容",
        metadata={"page_no": 1, "source": "test.pdf"}
    )
    
    # 正しいアクセス方法
    assert doc.page_content == "テスト内容"
    assert doc.metadata["page_no"] == 1
    assert doc.metadata["source"] == "test.pdf"


def test_vector_store_addメソッドに渡すべき形式():
    """
    vector_store.py の add メソッドは、以下の形式のdictを期待している:
    {"content": str, "page_no": int, "source": str}
    
    しかし実際には Document 型が渡されている
    """
    # これが期待される形式
    expected_format = {
        "content": "テスト内容",
        "page_no": 1,
        "source": "test.pdf"
    }
    
    # これが実際に渡されている型
    actual_format = Document(
        page_content="テスト内容",
        metadata={"page": 1, "source_file": "test.pdf", "user_title": "test"}
    )
    
    # Document型をdict["content"]でアクセスしようとするとエラーになる
    with pytest.raises(TypeError):
        _ = actual_format["content"]
