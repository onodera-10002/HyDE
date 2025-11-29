import os
import getpass
from dotenv import load_dotenv
load_dotenv()
# === 1. 設定管理の段階 === #
os.environ["LANGSMITH_TRACING"] = "true"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google API Key: ")
if not LANGSMITH_API_KEY:
    os.environ["LANGSMITH_API_KEY"] = getpass.getpass("Enter your LangSmith API Key: ")

# === 2. 定数の定義 === #
WEB_PATH = "https://www.aozora.gr.jp/cards/000076/files/1016_19596.html"
CHAT_MODEL = "gemini-2.5-flash"
MODEL_PROVIDER = "google-genai"
EMBEDDING_MODEL = "models/gemini-embedding-001"
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
RETRIEVER_K = 5

# === プロンプトのテンプレート ===#
TEMPLATE = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Use three sentences maximum and keep the answer as concise as possible.
If you asked alot of question, for each question, provide a separate answer.
{context}
Question: {question}
Helpful Answer:"""

HYDE_TEMPLATE = """以下の質問に対して、回答となるであろう「架空の文書」を作成してください。これは検索精度を上げるために使用します。余計な解説（「これは架空の回答です」など）は一切含めず、回答の本文だけを生成してください。質問: {question}架空の回答:"""


QUESTIONS_LIST = [
    {"question": "「ともちゃん」とは、この小説の登場人物のうちの誰のことを指すか？"},
    {"question": "この小説の主題はなんですか？"},
    {"question": "湊は最後、ともよに何をあげましたか？"},
    {"question": "湊にとって、鮨を食べることはなぜ慰みになるのですか？"}
]