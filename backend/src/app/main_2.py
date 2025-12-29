# あなたの作成したモジュールをインポート
from src.factories import Factories
import os

# 1. これを最優先で追加
os.environ["USER_AGENT"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

loader = Factories.choiseloader("https://www.jstage.jst.go.jp/article/taxa/43/0/43_30/_pdf")
docs = loader.load()

print(docs)  # ロードしたドキュメントのチャンクを表示