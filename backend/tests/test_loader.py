#=== 今回テストをしたいこと ===#
# 大量のドキュメントが渡された時に一気に渡してしまわないようにバッチ処理を施すようにしたい
# そのために、本番コードでは100個ずつに分割してVectorStoreに追加するようにする。
# 必要なこと
# 大量のドキュメントの用意
# 100個ずつに分割するロジック
#　100個渡して少し待ってから次の100個を渡す動作確認
# 1800個のドキュメントならば、18回追加され、17回の休憩が発生することを確認する

# ====必要なモック====#
# vectore_store.add メソッドをモック化して、呼び出し回数をカウントする
# ___init__で使うことが確定している道具である埋め込みモデルとベクトルストアのモック化

from unittest.mock import patch
from src.vector_store import Vectorstore
from langchain_core.documents import Document

def test_大量のデータが送られてきた時にバッチ処理を施す():
    # 準備
    large_number_docs = [Document(page_content="test")]*1800
    with patch("src.vector_store.GoogleGenerativeAIEmbeddings"), \
         patch("src.vector_store.InMemoryVectorStore") as MockVectorStore, \
         patch("src.vector_store.sleep", return_value=None) as mock_sleep:

    # 実行
        mock_store_instance = MockVectorStore.return_value
        db = Vectorstore(embedding_model="dummy-model")

        db.add(large_number_docs, batch_size=100, sleep_time=mock_sleep)


    # 検証
        assert mock_store_instance.add_documents.call_count == 18
        assert mock_sleep.call_count == 17





