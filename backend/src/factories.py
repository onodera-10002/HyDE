from src.loader import AozoraLoader, PDFLoader

class Factories():
    @staticmethod
    def choiseloader(source:str):
        if "aozora" in source:
            return AozoraLoader(source)
        elif source.lower().endswith(".pdf"):
            return PDFLoader(source)
        else:
            raise ValueError("対応していないドキュメント形式です。")

