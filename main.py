"""Ponto de entrada da aplicação CHATLOCAL (FastAPI + SQLAlchemy).

Execute a API com:
    uvicorn main:app --reload
"""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

from core.api import app  # noqa: E402
from database.init_db import iniciar_banco  # noqa: E402

# Cria, se necessário, todas as tabelas mapeadas pelo SQLAlchemy.
iniciar_banco()

DEBUG = os.getenv("DEBUG", "True").strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port="8000", reload=DEBUG)
