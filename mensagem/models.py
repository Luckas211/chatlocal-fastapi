from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.registry import tabela_registro
from usuario.models import Usuario

@tabela_registro.mapped_as_dataclass
class Mensagem:
    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    conteudo: Mapped[str] = mapped_column()
    
    # 1. Chaves estrangeiras (De quem para quem)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    destinatario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))

    # 2. Data de envio corrigida (Mapped[datetime] e sem parênteses no utcnow)
    data_envio: Mapped[datetime] = mapped_column(default=datetime.utcnow, init=False)

    # 3. Relacionamentos resolvendo as rotas das chaves estrangeiras
    remetente: Mapped["Usuario"] = relationship(foreign_keys=[usuario_id], init=False)
    destinatario: Mapped["Usuario"] = relationship(foreign_keys=[destinatario_id], init=False)