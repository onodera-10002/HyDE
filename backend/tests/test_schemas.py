import pytest
from pydantic import ValidationError
from src.schemas import ChatInput

# 正常な入力ならばばバリデーションが通ることを確認するテスト
# 空文字でエラーを出すテスト
# 異常な型でエラーを出すテスト
# 長すぎる文字列でエラーを出すテスト
# questionとquestionsの両方が指定された場合にエラーを出すテスト
# questionとquestionsの両方が未指定の場合にエラーを出すテスト



class TestChatInput:
    def test_正確な入力に対してバリデーションが通ること(self):
        # 準備
        valid_text = "ともちゃんって誰？"

        #　実行
        data = ChatInput(question=valid_text)
        assert data.question == valid_text

    @pytest.mark.parametrize("invalid_text",[
        "",# 空文字
        " ",# 半角スペース
        "　",# 全角スペース
        "\n",# 改行のみ
        "\t"# タブ改行のみ
    ])

    def test_questionが空文字の場合にバリデーションエラーを出すこと(self, invalid_text):
        # 実行と検証
        with pytest.raises(ValidationError):
            ChatInput(question=invalid_text)
        
    
    @pytest.mark.parametrize("invalid_type",[
        {"key": "value"},   # 辞書
        None                # NoneType
    ])

    def test_questionがstr以外の時にValidationErrorを出すこと(self, invalid_type):
        with pytest.raises(ValidationError):
            ChatInput(question=invalid_type)
        

    def test_questionが長すぎる場合にバリデーションエラーを出すこと(self):
        # 準備
        long_text = "a"*2000 # 長い文字列
        # 実行と検証
        with pytest.raises(ValidationError):
            ChatInput(question=long_text)
        

    def test_questionとquestionsの両方が指定された場合にバリデーションエラーを出すこと(self):
        # 実行と検証
        with pytest.raises(ValidationError):
            ChatInput(question="質問1", questions=["質問2", "質問3"])
        
    
    def test_questionとquestionsの両方が未指定の場合にバリデーションエラーを出すこと(self):
        # 実行と検証
        with pytest.raises(ValidationError):
            ChatInput()
        
    
    
        


