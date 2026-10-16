# 01 · Arquitetura do CHATLOCAL

> Visão geral do sistema, mapa de módulos, modelo de dados e fluxos principais.

## Visão geral

O CHATLOCAL é uma aplicação full-stack em Python com **dois clientes sobre a mesma base de regras de negócio**:

1. **API REST** (`/api/...`) — consome JSON autenticado por JWT no header `Authorization`
2. **Aplicação web** (`/login`, `/chat`) — páginas HTML geradas com Jinja2 + htmx, autenticadas por cookie httpOnly

```
     ┌──────────────┐          ┌──────────────────┐
     │  Navegador   │          │ Cliente HTTP/API │
     │ (HTML + htmx)│          │   (curl, app)    │
     └──────┬───────┘          └────────┬─────────┘
            │ cookie JWT               │ Bearer JWT
     ┌──────▼───────────────────────────▼─────────┐
     │            FastAPI (core/api.py)          │
     │  CORS · /static · rotas web · rotas API   │
     ├────────────────┬──────────────────────────┤
     │     web/       │  usuario/ · mensagem/    │
     │  views.py      │  api.py (rotas REST)     │
     │  chat_views.py │  services.py (regras)    │
     │  templates/    │  models.py · schemas.py  │
     │  static/       │  security.py (JWT/bcrypt)│
     ├────────────────┴──────────────────────────┤
     │        database/ (engine + sessão)        │
     │            SQLite: chatlocal.db           │
     └───────────────────────────────────────────┘
```

## Mapa de módulos

| Pasta | Responsabilidade | Arquivos |
|---|---|---|
| `core/` | Composição da aplicação | `api.py` — cria o `app`, CORS, `/static`, registra todos os routers |
| `database/` | Infraestrutura de dados | `connection.py` (engine/sessão), `session.py` (`obter_sessao`), `registry.py`, `init_db.py` |
| `usuario/` | Usuários e autenticação | `api.py`, `services.py`, `models.py`, `schemas.py`, `security.py` |
| `mensagem/` | Mensagens | `api.py`, `services.py`, `models.py`, `schemas.py` |
| `web/` | Frontend server-side | `views.py` (login/registo/logout), `chat_views.py` (chat), `templates/`, `static/` |
| raiz | Entrada e configuração | `main.py`, `.env`, `requirements.txt`, `README.md` |

**Regra de dependência: rota → service → model.** As rotas (`api.py`, `views.py`, `chat_views.py`) só orquestram: validam, chamam `services.py` e devolvem a resposta. As regras de negócio vivem em `services.py`. Nunca há SQL nas rotas.

## Modelo de dados

```mermaid
erDiagram
    usuarios ||--o{ mensagens : "envia (usuario_id)"
    usuarios ||--o{ mensagens : "recebe (destinatario_id)"
    usuarios {
        int id PK
        string nome_usuario UK "3-50 caracteres, index único"
        string nome_completo "1-120 caracteres"
        string senha "hash bcrypt"
    }
    mensagens {
        int id PK
        string conteudo "1-500 caracteres"
        int usuario_id FK "remetente"
        int destinatario_id FK "destinatário"
        datetime data_envio "default: agora (UTC)"
    }
```

- ORM: SQLAlchemy 2.0 no padrão `registry` + `mapped_as_dataclass` (`database/registry.py`)
- Um chat privado entre A e B são as mensagens com `(usuario_id=A AND destinatario_id=B) OR (usuario_id=B AND destinatario_id=A)`
- O histórico usa `joinedload`, então 2 usuários = **1 única query** (evita o problema N+1)

## Fluxos principais

### Login (camada web)

```mermaid
sequenceDiagram
    participant N as Navegador
    participant W as web/views.py
    participant S as security.py
    participant B as SQLite
    N->>W: POST /login (username, password)
    W->>B: SELECT usuario WHERE nome_usuario=?
    W->>S: verificar_senha(senha, hash bcrypt)
    S-->>W: True
    W->>S: criar_token_acesso(id, nome)
    S-->>W: JWT válido por 60min
    W-->>N: 303 /chat + Set-Cookie access_token (HttpOnly)
```

### Envio e recebimento de mensagens

```mermaid
sequenceDiagram
    participant A as Ana (chat aberto)
    participant W as web/chat_views.py
    participant B as SQLite
    participant C as Bia (chat aberto)
    A->>W: POST /chat/enviar (hx-post)
    W->>W: valida cookie + destinatário + conteúdo
    W->>B: INSERT mensagens
    W-->>A: fragmento _mensagens.html (200)
    Note over A: painel atualizado e form limpo
    loop a cada 3s (hx-trigger="every 3s")
        C->>W: GET /chat/mensagens/{id}
        W->>B: SELECT histórico
        W-->>C: fragmento com as mensagens
    end
```

## Camada web vs API

| | API REST | Camada web |
|---|---|---|
| Regras de negócio | `services.py` | **as mesmas** (reutiliza as funções) |
| Autenticação | header `Authorization: Bearer` | cookie `access_token` (httpOnly) |
| Formato | JSON + Pydantic | HTML + Jinja2 |
| Sessão no servidor | nenhuma (stateless) | nenhuma — o próprio JWT carrega a identidade |

Essa decisão mantém o servidor **stateless**: adicionar réplicas ou trocar o banco não quebra a autenticação.

## Pontos de extensão
- `web/` é um pacote isolado: páginas novas = novo arquivo de rotas + templates, sem tocar no domínio
- WebSocket/SSE entrará como rota adicional no mesmo `app` (ver roadmap no README)
- A API continua sendo o contrato estável para qualquer outro cliente (mobile, tests, automações)