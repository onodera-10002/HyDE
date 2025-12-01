# dependencies.py
from fastapi import HTTPException

# main.py で作った bot_instance を参照するためにインポート
# 注意: 循環参照を避けるため、設計によっては工夫が必要ですが、
# シンプルな構成なら main からではなく、別ファイルで管理するか、
# ここでは簡易的に main モジュールから取得する前提で書きます。
import main 

def get_bot():
    """
    起動時に作成済みのBotインスタンスを返す
    """
    if main.bot_instance is None:
        raise HTTPException(status_code=503, detail="Bot is not initialized yet.")
    return main.bot_instance