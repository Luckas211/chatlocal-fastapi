import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher

load_dotenv()

# Chave vinda do .env (nunca versionada). Sem definir SECRET_KEY no .env,
# é gerada uma chave temporária: tokens caem a cada reinício (ok em dev).
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(48)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def criar_token_acesso(usuario_id: int, nome_usuario: str) -> str:
    expira = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(usuario_id),
        "nome_usuario":nome_usuario,
        "exp": expira
    }
      
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/usuarios/login")
def obter_usuario_logado(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return int(usuario_id)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirou")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token inválido")
"""
1. O porteiro e a bilheteria
Python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/usuarios/login")
O que o OAuth2PasswordBearer faz?
Ele é o "porteiro" padrão do FastAPI. Ele avisa ao sistema: "Sempre que alguém tentar aceder a uma rota protegida, procurem um cabeçalho HTTP chamado 'Authorization' que contenha a palavra 'Bearer ' seguida de um código".

Por que tenho de o usar?
Porque se você não usasse, teria de escrever manualmente o código para capturar o pedido HTTP do cliente, vasculhar os cabeçalhos, recortar a palavra "Bearer " e isolar o token. Esta ferramenta faz isso automaticamente.

Por que o parâmetro exige o tokenUrl="api/usuarios/login"?
Isto serve quase exclusivamente para o Swagger (a página /docs). Lembra-se daquele cadeado verde que clicou para fazer login? O Swagger precisa saber para qual URL ele deve enviar o seu nome e senha para receber o token de volta. O tokenUrl é a "placa de sinalização" que aponta para a bilheteria.

2. A injeção da mágica (O Depends)
Python
def obter_usuario_logado(token: str = Depends(oauth2_scheme)):
O que é token: str?
É apenas você a criar uma variável chamada token e a dizer ao Python que ela vai armazenar um texto (str de string).

O que faz o Depends?
O Depends (Dependência) é o coração do FastAPI. Ele diz ao FastAPI: "Antes de rodares o código desta função, faz uma pausa, executa o que está dentro dos meus parênteses, e traz-me o resultado".

Por que colocar o oauth2_scheme dentro do Depends?
Você está a mandar o FastAPI chamar o "porteiro". O fluxo real é:

O FastAPI vê o Depends.

Chama o oauth2_scheme.

O oauth2_scheme vai à requisição do utilizador, acha o texto do token (ex: eyJhbGci...) e extrai-o.

O FastAPI pega nesse texto limpo e guarda-o dentro da sua variável token.

3. Abrindo o cofre
Python
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
O que é o jwt.decode?
A biblioteca jwt pegou nos seus dados e transformou-os numa string embaralhada lá na rota de login (usando jwt.encode). O decode é o processo inverso: ele pega no token embaralhado e tenta descodificá-lo de volta para dados legíveis.

Por que o parâmetro se chama algorithms (no plural e com colchetes [])?
Isso é uma exigência de segurança moderna da biblioteca PyJWT. Antigamente, hackers descobriram que se enviassem um token dizendo "use o algoritmo X em vez do algoritmo Y", conseguiam invadir sistemas. Para impedir isso, o PyJWT obriga-o a passar uma lista fechada dos algoritmos que você confia. Ao usar [ALGORITHM] (que no seu caso vale ["HS256"]), você diz: "Se o token não foi criado com HS256, rejeite imediatamente".

O que é payload?
payload (que traduzido significa "carga útil") é uma variável que você criou para guardar os dados descodificados. Depois que o jwt.decode faz a sua magia com a SECRET_KEY, o payload transforma-se num simples Dicionário Python. Fica com esta aparência real na memória do computador:

Python
{
   "sub": "3",
   "nome_usuario": "lucas123",
   "exp": 1790115780
}
4. Pescando a informação
Python
        usuario_id: str = payload.get("sub")
        if usuario_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
usuario_id: str é uma variável que criei?
Sim, exatamente. Você batizou essa variável aqui mesmo para guardar a ID.

O que o payload.get("sub") está a fazer?
Como o seu payload agora é um dicionário (mostrado no bloco acima), o método .get("sub") é uma pescaria. Ele diz ao Python: "Olhe para dentro do dicionário payload e traga-me o valor que está guardado na chave chamada 'sub'".
No nosso exemplo, ele vai pescar o valor "3" e guardá-lo na variável usuario_id.

Por que usamos o .get("sub") em vez de payload["sub"]?
No Python, se você tentar aceder a um dicionário com colchetes payload["sub"] e a chave não existir (imagina que alguém enviou um token falso sem a chave "sub"), o Python dá um erro fatal (KeyError) e quebra o servidor.
Se usar .get("sub"), e a chave não existir, o Python não quebra. Ele apenas devolve None (Vazio).

E é por isso que o if existe logo abaixo!
O if usuario_id is None: verifica: "O get trouxe um número, ou trouxe um Vazio?". Se trouxe Vazio, significa que o token é falso ou malformado, então você expulsa o utilizador com o erro 401 (Não Autorizado).
"""

    







gerenciador_senha = PasswordHash((BcryptHasher(),))

def obter_hash_senha(senha: str) -> str:
    return gerenciador_senha.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str) -> bool:
    return gerenciador_senha.verify(senha_pura, senha_hash)