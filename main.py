from src import config
from src.loader import AozoraLoader
from src.vector_store import Vectorstore
from src.bot import ChatBot



def main():
    
    print("RAGの検索を開始します。")
    print("データをダウンロードします...")

    loader = AozoraLoader(url = config.WEB_PATH)
    chunks = loader.doc_load()
    # ここまででloader.pyの役割を完了した。

    print("検索を開始します...")
    db = Vectorstore(embedding_model=config.EMBEDDING_MODEL)
    db.add(chunks)
    # ここまででvector_store.pyの役割を完了した。
    bot = ChatBot(
        template = config.TEMPLATE,
        hyde_template = config.HYDE_TEMPLATE,
        vector_db = db
    )

    print("質問に回答します...")
    print("\n" + "="*20 + "\n")

    questions = config.QUESTIONS_LIST
    for qa in questions:
        qa = qa["question"]
        answers = bot.run(question=qa)
        print(f"Q: {qa}\nA: {answers}\n")
    
if __name__ == "__main__":
    main()


    
     


    





