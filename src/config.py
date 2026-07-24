"""Configuration for NeoBank Alura RAG agent."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW_DIR = ROOT_DIR / "data" / "raw"
DATA_PROCESSED_DIR = ROOT_DIR / "data" / "processed"
VECTORSTORE_DIR = ROOT_DIR / "vectorstore" / "faiss_index"

_ENV_PATH = ROOT_DIR / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH, override=True)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
TOP_K = int(os.getenv("TOP_K", "4"))
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile").strip()


def read_api_key() -> str:
    """Lee LLM_API_KEY desde .env (sin depender de cache de imports)."""
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
    key = os.getenv("LLM_API_KEY", "").strip()
    if key:
        return key
    if not env_path.exists():
        return ""
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line.startswith("LLM_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


# Alias usado por la UI / cadena RAG
LLM_API_KEY = read_api_key()
