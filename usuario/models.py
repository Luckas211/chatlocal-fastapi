from sqlalchemy.orm import Mapped, mapped_column
from database.registry import tabela_registro


from sqlalchemy.orm import Mapped, mapped_column
from database.registry import tabela_registro

@tabela_registro.mapped_as_dataclass
class Usuario:
    __tablename__ = "usuarios"

    # init=False avisa ao dataclass que não precisamos passar o id na criação manual
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    nome_usuario: Mapped[str] = mapped_column(unique=True, index=True)
    nome_completo: Mapped[str] = mapped_column()
    senha: Mapped[str] = mapped_column()
