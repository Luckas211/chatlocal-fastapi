from sqlalchemy import select 
from sqlalchemy.orm import Session

from .models import Usuario
from .security import obter_hash_senha

def criar_usuario(session: Session, nome_usuario: str, nome_completo: str, senha: str) -> Usuario:
    senha_segura = obter_hash_senha(senha)
    
    usuario = Usuario(
        nome_usuario=nome_usuario,
        nome_completo=nome_completo,
        senha=senha_segura,
    )
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


def listar_usuarios(session: Session) -> list[Usuario]:
    return list(session.scalars(select(Usuario)).all())