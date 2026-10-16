from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class UsuarioMensagemSchema(BaseModel):
    id: int
    nome_usuario: str
    
    model_config = ConfigDict(from_attributes=True)


class MensagemSchema(BaseModel):
    id: int  # <-- O erro está aqui. Deve ser 'int', não 'id'.
    conteudo: str
    data_envio: datetime
    usuario_id: int
    destinatario_id: int
    
    remetente: UsuarioMensagemSchema  # <-- O erro de digitação está aqui
    destinatario: UsuarioMensagemSchema

    model_config = ConfigDict(from_attributes=True)

class CriarMensagemSchema(BaseModel):
    conteudo: str = Field(..., min_length=1, max_length=500)
    destinatario_id: int = Field(..., gt=0)