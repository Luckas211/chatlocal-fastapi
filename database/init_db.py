"""Inicialização do schema do banco de dados via SQLAlchemy."""
from database.connection import motor_do_banco
from database.registry import tabela_registro
from usuario.models import Usuario  # noqa: F401  (import registra a Entidade no metadata)


def iniciar_banco() -> None:
    """Cria, se necessário, todas as tabelas mapeadas pelo SQLAlchemy."""
    tabela_registro.metadata.create_all(motor_do_banco)
