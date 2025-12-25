import pytest

# ここでは @pytest.mark.asyncio が必要
@pytest.mark.asyncio
async def test_bot_run_flow(mock_chatbot): # 工場の名前(mock_chatbot)を指定！
    # 準備は完了しているので、いきなり実行できる
    answer = await mock_chatbot.run("こんにちは")
    
    assert answer == "テスト成功です！"






        
    
