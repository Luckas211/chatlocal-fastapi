"""Camada web (HTML) do CHATLOCAL — páginas Jinja2 + htmx (login, registo, logout).

A API REST usa Bearer token no header Authorization; os formulários HTML
não conseguem enviar cabeçalhos, então aqui o JWT vai num cookie httpOnly
que o navegador anexa automaticamente a cada requisição.
"""
from pathlib import Path

import jwt
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.session import obter_sessao
from usuario.models import Usuario
from usuario.security import ALGORITHM, SECRET_KEY, criar_token_acesso, verificar_senha
from usuario.services import criar_usuario

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Fragmentos do chat não podem ser cacheados (senão o polling mostra mensagens velhas)
_SEM_CACHE = {"Cache-Control": "no-store"}


def usuario_do_cookie(request: Request) -> int | None:
    """Decodifica o JWT do cookie de sessão e devolve o id do usuário (ou None)."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        return None
    sub = payload.get("sub")
    return int(sub) if sub else None


def _pagina(request: Request, nome: str, contexto: dict | None = None, status_code: int = 200):
    """Renderiza uma página HTML completa."""
    return templates.TemplateResponse(
        request=request, name=nome, context=contexto or {}, status_code=status_code
    )


def _fragmento(request, eu, mensagens=None, *, erro=None, sessao_expirada=False):
    """Renderiza só o painel de mensagens (fragmento htmx — sempre HTTP 200)."""
    return templates.TemplateResponse(
        request=request,
        name="_mensagens.html",
        context={"eu": eu, "mensagens": mensagens or [], "erro": erro, "sessao_expirada": sessao_expirada},
        status_code=status.HTTP_200_OK,
        headers=_SEM_CACHE,
    )


# ------------------------------------------------------------------ login
@router.get("/login", response_class=HTMLResponse, summary="Tela de login")
def tela_login(request: Request):
    if usuario_do_cookie(request):
        return RedirectResponse("/chat", status_code=status.HTTP_303_SEE_OTHER)
    return _pagina(request, "login.html")


@router.post("/login", response_class=HTMLResponse, summary="Autenticar")
def autenticar(request: Request, username: str = Form(...), password: str = Form(...), session: Session = Depends(obter_sessao)):
    stmt = select(Usuario).where(Usuario.nome_usuario == username)
    usuario = session.scalars(stmt).first()
    if not usuario or not verificar_senha(password, usuario.senha):
        return _pagina(request, "login.html", {"erro": "Usuário ou senha incorretos."}, status.HTTP_400_BAD_REQUEST)

    token = criar_token_acesso(usuario_id=usuario.id, nome_usuario=usuario.nome_usuario)
    resposta = RedirectResponse("/chat", status_code=status.HTTP_303_SEE_OTHER)
    # Cookie httpOnly: o navegador envia sozinho; JS não consegue lê-lo
    resposta.set_cookie("access_token", token, max_age=3600, httponly=True, samesite="lax", path="/")
    return resposta


# ---------------------------------------------------------------- registo
@router.get("/registo", response_class=HTMLResponse, summary="Tela de criação de conta")
def tela_registo(request: Request):
    if usuario_do_cookie(request):
        return RedirectResponse("/chat", status_code=status.HTTP_303_SEE_OTHER)
    return _pagina(request, "registo.html")


@router.post("/registo", response_class=HTMLResponse, summary="Criar usuário")
def registar(request: Request, nome_usuario: str = Form(...), nome_completo: str = Form(...), senha: str = Form(...), session: Session = Depends(obter_sessao)):
    # Espelha as validações do schema da API (CriarUsuarioSchema)
    if not (3 <= len(nome_usuario) <= 50):
        erro = "O nome de usuário deve ter entre 3 e 50 caracteres."
    elif not (1 <= len(nome_completo) <= 120):
        erro = "Informe o nome completo (até 120 caracteres)."
    elif len(senha) < 4:
        erro = "A senha deve ter pelo menos 4 caracteres."
    else:
        erro = None
    if erro:
        return _pagina(request, "registo.html", {"erro": erro}, status.HTTP_400_BAD_REQUEST)

    try:
        criar_usuario(session=session, nome_usuario=nome_usuario, nome_completo=nome_completo, senha=senha)
    except IntegrityError:
        session.rollback()
        return _pagina(request, "registo.html", {"erro": "Já existe uma conta com esse nome de usuário."}, status.HTTP_409_CONFLICT)
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)


# ---------------------------------------------------------------- logout
@router.post("/logout", summary="Encerrar sessão")
def encerrar_sessao():
    resposta = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    resposta.delete_cookie("access_token", path="/")
    return resposta