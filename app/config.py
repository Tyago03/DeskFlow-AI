"""Configuração explícita: sem tokens dentro do repositório."""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv
load_dotenv(BASE / ".env")
DATA_DIR = Path(os.getenv("DESKFLOW_DATA_DIR", str(BASE / "data"))).resolve()
DB_PATH = DATA_DIR / "deskflow.sqlite3"
MODEL = os.getenv("DESKFLOW_MODEL", "qwen3:4b-instruct")
OLLAMA_URL = os.getenv("DESKFLOW_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/")
DEMO_MODE = os.getenv("DESKFLOW_DEMO_MODE", "0").lower() in {"1", "yes", "true"}
INGEST_KEY = os.getenv("DESKFLOW_INGEST_KEY", "").strip()
