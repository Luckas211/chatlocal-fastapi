
from pydantic import BaseModel, Field, ConfigDict


class UsuarioSchema(BaseModel):
    id: int
    nome_usuario: str = Field(..., min_length=3, max_length=50)
    nome_completo: str = Field(..., min_length=1, max_length=120)
    
    model_config = ConfigDict(from_attributes=True)


class CriarUsuarioSchema(BaseModel):
    nome_usuario: str = Field(..., min_length=3, max_length=50)
    nome_completo: str = Field(..., min_length=1, max_length=120)
    senha: str = Field(..., min_length=4)
    
    
class token(BaseModel):
    access_token: str
    token_type: str
