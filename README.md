# 💬 CHATLOCAL

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688?style=flat&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat)
![htmx](https://img.shields.io/badge/htmx-2.0-E90E6E?style=flat)

Chat privado 1-a-1 com **API REST documentada** e **interface server-side**. Desenvolvi o backend em Python com FastAPI; a interface HTML/CSS foi gerada por IA. O sistema usa Jinja2 e htmx — versionado localmente, sem CDN — para renderizar as páginas e atualizar as mensagens por polling a cada 3 segundos. Estudei WebSockets durante o projeto, mas eles não fazem parte da implementação atual.

## 🔄 Como funciona

**1) Login**

```
POST /login (usuário + senha)
  → bcrypt confere o hash            ✔
  → JWT (HS256, 60 min) é emitido
  → gravado em cookie HttpOnly + SameSite=Lax
  → 303 redirect para /chat
```

**2) Envio e recebimento de mensagens**

```
Ana clica em Enviar ──hx-post──►  POST /chat/enviar
                                  valida cookie, destinatário e texto
                                  INSERT no banco
   ◄── fragmento HTML com o painel já atualizado

Bia (chat aberto) ──hx-get a cada 3s──►  GET /chat/mensagens/{id}
   ◄── mesmas mensagens renderizadas no servidor (Jinja2)
```

**3) Camadas:** rota → `services.py` (regras de negócio) → SQLAlchemy → SQLite.
A API JSON e as telas HTML **compartilham as mesmas regras** — dois clientes, uma só aplicação.

## ✨ Funcionalidades

- Cadastro e login com **JWT** (cookie httpOnly) e senha com **bcrypt**
- Conversas privadas 1-a-1 com histórico persistente (SQLite)
- Painel de mensagens que se **atualiza sozinho a cada 3 segundos** (polling via htmx, com scroll automático até a última mensagem)
- API REST completa documentada no **Swagger (/docs)**
- Frontend em **HTML/CSS puro** — sem build tools, sem npm, sem frameworks de UI
- CORS configurável via `.env`, rotas protegidas (`401`/`403`) e segredos fora do código

## 🛠 Stack

| Camada | Tecnologias |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Frontend | Jinja2 (templates), htmx 2 (local), CSS puro |
| Banco | SQLite (`chatlocal.db`) |
| Segurança | PyJWT, pwdlib/bcrypt, cookie httpOnly, CORS configurável |
| Servidor | Uvicorn |

## 🏗 Arquitetura

```
CHAT LOCAL/
├── core/          # app FastAPI, CORS, arquivos estáticos
├── database/      # engine, sessão e registry do SQLAlchemy
├── usuario/       # models, schemas, services e segurança (JWT/bcrypt)
├── mensagem/      # models, schemas e services das mensagens
├── web/           # ← frontend server-side
│   ├── views.py       # login, registo, logout
│   ├── chat_views.py  # tela do chat + fragmentos htmx
│   ├── templates/     # base, login, registo, chat, _mensagens
│   └── static/        # style.css + vendor/htmx.min.js
└── main.py        # ponto de entrada do servidor
```

A camada web **reutiliza as mesmas funções** de `services.py` da API — uma só regra de negócio, dois clientes (API JSON e páginas HTML).

## 🚀 Como rodar

```powershell
# 1. ambiente virtual + dependências
python -m venv venv
venv\Scripts\activate            # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# 2. configuração
copy .env.example .env           # Linux/macOS: cp .env.example .env
#    gere e salve a SECRET_KEY no .env:
python -c "import secrets; print(secrets.token_urlsafe(48))"

# 3. servidor
uvicorn main:app --reload
```

- **Chat:** http://127.0.0.1:8000/chat
- **API (Swagger):** http://127.0.0.1:8000/docs

## 🖥 Demonstração em 30 segundos

1. Abra http://127.0.0.1:8000/registo **em uma aba anônima** e crie o usuário `bia`
2. Na janela normal, crie `ana` e entre no chat
3. Troque mensagens — elas aparecem em ~3 s para o outro lado, sem recarregar a página

## 🔌 Endpoints

**Páginas (HTML)**

| Método | Rota | Descrição |
|---|---|---|
| GET/POST | `/login` | tela e autenticação |
| GET/POST | `/registo` | criação de conta |
| GET | `/chat` | tela do chat (`?contato_id=` opcional) |
| GET | `/chat/mensagens/{id}` | fragmento do painel (polling) |
| POST | `/chat/enviar` | envia mensagem (devolve fragmento) |
| POST | `/logout` | encerra sessão |

**API REST (JWT no header `Authorization: Bearer`)**

| Método | Rota | Auth |
|---|---|---|
| POST | `/api/usuarios/` | pública |
| POST | `/api/usuarios/login` | pública |
| GET | `/api/usuarios/` | ✅ |
| POST | `/api/mensagens/` | ✅ |
| GET | `/api/mensagens/{eu}/{outro}` | ✅ somente o próprio usuário |

## 🔐 Notas de segurança

- Senhas com hash **bcrypt** (nunca texto puro)
- JWT de 60 min em cookie `httponly` + `SameSite=Lax`
- Histórico protegido: sem token → `401`; token de outro usuário → `403`
- `SECRET_KEY` vive apenas no `.env` (ignorado pelo git)
- Jinja2 escapa todo o conteúdo exibido (proteção contra XSS)

## 🗺 Próximos passos

- [ ] **WebSocket/SSE** para entrega em tempo real (hoje: polling de 3 s)
- [ ] Testes automatizados (pytest + TestClient)
- [ ] Paginação do histórico e busca de usuários
- [ ] Docker + deploy

## 📚 Documentação técnica

| Guia | Conteúdo |
|---|---|
| [docs/01-arquitetura.md](docs/01-arquitetura.md) | Módulos, modelo de dados e fluxos |
| [docs/02-api-rest.md](docs/02-api-rest.md) | Referência da API + exemplos curl |
| [docs/03-frontend-web.md](docs/03-frontend-web.md) | Jinja2, htmx e cookie de sessão |
| [docs/04-seguranca.md](docs/04-seguranca.md) | Medidas de segurança e limitações |
| [docs/05-desenvolvimento.md](docs/05-desenvolvimento.md) | Setup, variáveis e convenções |
| [docs/06-historico-de-mudancas.md](docs/06-historico-de-mudancas.md) | Registro de alterações (auditoria) |

---\n
