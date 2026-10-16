"""Aplicação FastAPI principal do CHATLOCAL."""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from usuario.api import router as usuarios_router
from mensagem.api import router as mensagem_router
from web.views import router as web_router
from web.chat_views import router as chat_router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="CHATLOCAL API",version="1.0.0",description="API do sistema CHATLOCAL")

# CORS: origens autorizadas a consumir a API de fora (definidas no .env)
origens = [
    origem.strip()
    for origem in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origem.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origens,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Arquivos estáticos do frontend server-side (CSS + htmx local, sem CDN)
app.mount("/static", StaticFiles(directory=BASE_DIR / "web" / "static"), name="static")


@app.get("/", tags=["apresentação"])
def Apresentacao() -> dict:
    return {"status": "online", "service": "CHATLOCAL API", "docs": "/docs"}


app.include_router(usuarios_router, prefix="/api/usuarios", tags=["Usuarios"])
app.include_router(mensagem_router,prefix="/api/mensagens", tags=["Mensagens"])
app.include_router(web_router, tags=["Web"])
app.include_router(chat_router, tags=["Web"])
