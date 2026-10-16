from sqlalchemy import select, or_, and_
from sqlalchemy.orm import Session, joinedload
from .models import Mensagem
from usuario.models import Usuario

def criar_mensagem(session: Session, conteudo: str, usuario_id: int, destinatario_id: int) -> Mensagem:
    """Guarda uma nova mensagem direta na base de dados."""
    mensagem = Mensagem(
        conteudo=conteudo,
        usuario_id=usuario_id,
        destinatario_id=destinatario_id
    )
    session.add(mensagem)
    session.commit()
    session.refresh(mensagem)
    
    # Ao criar, injetamos manualmente os objetos para que o 
    # Pydantic consiga montar o JSON de resposta (POST) sem erros.
    mensagem.remetente = session.get(Usuario, usuario_id)
    mensagem.destinatario = session.get(Usuario, destinatario_id)
    
    return mensagem


def listar_mensagens_privadas(session: Session, usuario_id: int, destinatario_id: int) -> list[Mensagem]:
    """Retorna o histórico de chat entre dois utilizadores específicos."""
    
    # O joinedload obriga o SQLAlchemy a carregar os dados dos utilizadores na mesma query
    stmt = select(Mensagem).options(
        joinedload(Mensagem.remetente),
        joinedload(Mensagem.destinatario)
    ).where(
        or_(
            and_(Mensagem.usuario_id == usuario_id, Mensagem.destinatario_id == destinatario_id),
            and_(Mensagem.usuario_id == destinatario_id, Mensagem.destinatario_id == usuario_id)
        )
    ).order_by(Mensagem.data_envio)
    
    return list(session.scalars(stmt).all())