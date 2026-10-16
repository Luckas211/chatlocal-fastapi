from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select
from .security import criar_token_acesso, verificar_senha, obter_usuario_logado
from .schemas import token
from .models import Usuario
from fastapi.security import OAuth2PasswordRequestForm

from database.session import obter_sessao
from .schemas import CriarUsuarioSchema, UsuarioSchema
from .services import criar_usuario, listar_usuarios

router = APIRouter()

@router.post("/login", response_model=token)
def login(form_data:OAuth2PasswordRequestForm = Depends(), session: Session = Depends(obter_sessao)):
    stmt = select(Usuario).where(Usuario.nome_usuario == form_data.username)
    usuario = session.scalars(stmt).first()
    
    if not usuario or not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos.")
    token_gerado = criar_token_acesso(usuario_id=usuario.id,nome_usuario=usuario.nome_usuario)
    return{"access_token": token_gerado, "token_type":"bearer"}


@router.post("/", response_model=UsuarioSchema,status_code=status.HTTP_201_CREATED,summary="Criar usuário")
def registrar_usuario(dados: CriarUsuarioSchema,session:Session = Depends(obter_sessao)):
    try:
            usuario = criar_usuario(
                session=session,
                nome_usuario=dados.nome_usuario,
                nome_completo=dados.nome_completo,
                senha=dados.senha,
            )
            return usuario
    except IntegrityError:
            # Se cair aqui, significa que o nome_usuario já existe no banco (violação da constraint unique)
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Já existe um usuário com este nome.",
            )
            

@router.get("/",response_model=list[UsuarioSchema], summary="Listar usuários")
def listar_todos_usuários(session: Session = Depends(obter_sessao),usuario_atual_id: int = Depends(obter_usuario_logado) ):
    return listar_usuarios(session=session)