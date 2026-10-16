from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database.session import obter_sessao
from usuario.models import Usuario
from usuario.security import obter_usuario_logado
from .schemas import CriarMensagemSchema, MensagemSchema
from .services import criar_mensagem, listar_mensagens_privadas

router = APIRouter()

@router.post("/", response_model=MensagemSchema, status_code=status.HTTP_201_CREATED, summary="Enviar mensagem direta")
def enviar_mensagem(dados: CriarMensagemSchema, session: Session = Depends(obter_sessao), usuario_atual_id: int = Depends(obter_usuario_logado)):
    # Verificar se o utilizador tenta enviar mensagem para si mesmo
    if usuario_atual_id == dados.destinatario_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível enviar mensagem para si mesmo.")
    
    remetente = session.get(Usuario, usuario_atual_id)
    destinatario = session.get(Usuario, dados.destinatario_id)
    
    if not remetente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Remetente não encontrado.")
    
    if not destinatario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Destinatário não encontrado.")
    
    # Chama a função do ficheiro services.py, acedendo aos valores dentro de 'dados'
    mensagem = criar_mensagem(
        session=session,
        conteudo=dados.conteudo,
        usuario_id=usuario_atual_id,
        destinatario_id=dados.destinatario_id
    )
    return mensagem


# Utilizamos List (maiúsculo) para evitar bugs de tipagem no Pydantic
# Acesso protegido: cada usuário só pode ler a própria conversa (evita IDOR)
@router.get("/{usuario_id}/{destinatario_id}", response_model=List[MensagemSchema], summary="Listar chat privado")
def obter_historico_privado(usuario_id: int, destinatario_id: int, session: Session = Depends(obter_sessao), usuario_atual_id: int = Depends(obter_usuario_logado)):
    if usuario_atual_id != usuario_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado: você só pode ler a própria conversa.")
    return listar_mensagens_privadas(session=session, usuario_id=usuario_id, destinatario_id=destinatario_id)