from src import config
from src.loader import AozoraLoader
from src.vector_store import Vectorstore
from src.bot import ChatBot
from logger import get_logger


def main():
    logger = get_logger(__name__)
    try:
        loader = AozoraLoader(url = config.WEB_PATH)
        chunks = loader.doc_load()
        # ここまででloader.pyの役割を完了した。
        logger.info(f"ドキュメントを読み込み(url={config.WEB_PATH})、{len(chunks)}個のチャンクに分割しました。")
        db = Vectorstore(embedding_model=config.EMBEDDING_MODEL)
        db.add(chunks)
    # ここまででvector_store.pyの役割を完了した。
        logger.info(f"チャンクをベクトルストアに追加しました。チャンク数: {len(chunks)}")

        bot = ChatBot(
            template = config.TEMPLATE,
            hyde_template = config.HYDE_TEMPLATE,
            vector_db = db
       )

        questions = config.QUESTIONS_LIST
        for qa in questions:
            qa = qa["question"]
            answers = bot.run(question=qa)
            logger.info(f"\nQ: {qa}\nA: {answers}\n")
    except Exception as e:
        logger.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()

     


    





