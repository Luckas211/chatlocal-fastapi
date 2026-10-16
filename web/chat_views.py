"""Rotas da tela de chat — fragmentos htmx com polling de 3 segundos."""
from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from database.session import obter_sessao
from mensagem.services import criar_mensagem, listar_mensagens_privadas
from usuario.models import Usuario
from usuario.services import listar_usuarios

from web.views import _fragmento, _pagina, usuario_do_cookie

router = APIRouter()


@router.get("/chat", response_class=HTMLResponse, summary="Tela do chat")
def tela_chat(request: Request, contato_id: int | None = None, session: Session = Depends(obter_sessao)):
    uid = usuario_do_cookie(request)
    if uid is None:
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    eu = session.get(Usuario, uid)
    if eu is None:  # token válido, mas o usuário saiu do banco
        resposta = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
        resposta.delete_cookie("access_token", path="/")
        return resposta

    contatos = [u for u in listar_usuarios(session) if u.id != uid]
    # Sem ?contato_id= assume o primeiro contato (bom para a demonstração)
    contato = next((u for u in contatos if u.id == contato_id), contatos[0] if contatos else None)
    mensagens = listar_mensagens_privadas(session, uid, contato.id) if contato else []
    return _pagina(request, "chat.html", {"eu": eu, "contatos": contatos, "contato": contato, "mensagens": mensagens})


@router.get("/chat/mensagens/{contato_id}", response_class=HTMLResponse, summary="Painel de mensagens (fragmento htmx, polling)")
def painel_mensagens(request: Request, contato_id: int, session: Session = Depends(obter_sessao)):
    uid = usuario_do_cookie(request)
    if uid is None:
        return _fragmento(request, None, sessao_expirada=True)

    eu = session.get(Usuario, uid)
    if eu is None:
        return _fragmento(request, None, sessao_expirada=True)

    contato = session.get(Usuario, contato_id)
    if contato is None or contato.id == uid:
        return _fragmento(request, eu, erro="Conversa não encontrada.")

    mensagens = listar_mensagens_privadas(session, uid, contato.id)
    return _fragmento(request, eu, mensagens)


@router.post("/chat/enviar", response_class=HTMLResponse, summary="Enviar mensagem (fragmento htmx)")
def enviar_mensagem_web(request: Request, destinatario_id: int = Form(...), conteudo: str = Form(...), session: Session = Depends(obter_sessao)):
    uid = usuario_do_cookie(request)
    if uid is None:
        return _fragmento(request, None, sessao_expirada=True)

    eu = session.get(Usuario, uid)
    if eu is None:
        return _fragmento(request, None, sessao_expirada=True)

    destinatario = session.get(Usuario, destinatario_id)
    if destinatario is None:
        return _fragmento(request, eu, erro="Usuário destinatário não encontrado.")
    if destinatario.id == uid:
        return _fragmento(request, eu, erro="Não é possível enviar mensagem para si mesmo.")

    conteudo = conteudo.strip()
    if not conteudo:
        return _fragmento(request, eu, erro="A mensagem não pode ficar vazia.")
    if len(conteudo) > 500:
        return _fragmento(request, eu, erro="Mensagem muito longa (máximo de 500 caracteres).")

    criar_mensagem(session=session, conteudo=conteudo, usuario_id=uid, destinatario_id=destinatario.id)
    mensagens = listar_mensagens_privadas(session, uid, destinatario.id)
    return _fragmento(request, eu, mensagens)