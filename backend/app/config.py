import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    str(BASE_DIR / "data" / "chroma")
)

COLLECTION_NAME = "documind_documents"

CHUNK_SIZE = 180
CHUNK_OVERLAP = 30

TOP_K = 5

DISTANCE_THRESHOLD = 0.75