# 05 · Guia de desenvolvimento

## Pré-requisitos
- Python **3.12+** (testado em 3.12.0 / Windows)
- pip

## Setup (Windows)

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

copy .env.example .env
# gere uma SECRET_KEY e edite o .env:
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Linux/macOS: `python -m venv venv && source venv/bin/activate && cp .env.example .env`

## Rodar

```powershell
uvicorn main:app --reload     # com auto-reload (DEBUG=True)
python main.py                # equivalente (127.0.0.1:8000)
```

| URL | O que é |
|---|---|
| http://127.0.0.1:8000/chat | aplicação web (login + chat) |
| http://127.0.0.1:8000/docs | Swagger da API |
| http://127.0.0.1:8000/ | status JSON da API |

> `main.py` carrega o `.env` **antes** de importar a aplicação e cria as tabelas com `iniciar_banco()` (idempotente — nunca apaga dados).

## Variáveis de ambiente (`.env`)

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DATABASE_URL` | não | `sqlite:///chatlocal.db` | URL do SQLAlchemy |
| `DEBUG` | não | `True` | liga o `--reload` do uvicorn |
| `SECRET_KEY` | **sim (produção)** | gerada no boot | assinatura dos JWTs |
| `CORS_ORIGINS` | não | `localhost:5173` | allowlist (separada por vírgula) |

## Demonstração com duas contas

1. Abra `/registo` em **aba anônima** → crie o usuário `bia`
2. Na janela normal, crie `ana` e faça login
3. Troque mensagens — chegam em ~3 s sem recarregar a página

## Verificação rápida (sem subir servidor)

```powershell
python -B -c "from fastapi.testclient import TestClient; import main; c = TestClient(main.app); r = c.get('/login'); print(r.status_code, 'OK' if 'password' in r.text else 'ERRO')"
```

Checklist manual: login certo/errado · registo duplicado → `409` · `/chat` sem cookie → redirect · enviar/receber mensagem · API sem token → `401` · API com token de outro → `403` · logout.

> Ainda **não existe suíte com pytest** (roadmap). A validação E2E completa — 29 checagens automatizadas — foi executada em 05/10/2026; detalhes em `06-historico-de-mudancas.md`.

## Convenções do código

- **Identificadores em português** (`criar_mensagem`, `obter_sessao`) — consistência acima de tudo
- Rotas finas: validam → chamam `services.py` → respondem (nunca SQL na rota)
- Schemas Pydantic separam entrada/saída (`CriarMensagemSchema` vs `MensagemSchema`)
- Comentários explicam o **porquê**, não o **o quê**
- Sem formatação automática configurada (Black/Ruff = roadmap)

## Solução de problemas

| Sintoma | Causa provável | Correção |
|---|---|---|
| `ModuleNotFoundError: jinja2` | venv sem dependências novas | `pip install -r requirements.txt` |
| Volta ao login a todo momento | `SECRET_KEY` mudou ou não está definida | fixe `SECRET_KEY` no `.env` |
| `address already in use` | porta 8000 ocupada | encerre o processo anterior |
| Tokens inválidos após reinício | boot sem `SECRET_KEY` | defina no `.env` |
| Mensagens antigas "somem" | banco recriado | `chatlocal.db` é regenerável (gitignored) |

## Roadmap

- [ ] WebSocket/SSE para tempo real (htmx já possui extensão oficial de SSE)
- [ ] pytest + `TestClient` em `tests/`
- [ ] Dockerfile + docker-compose
- [ ] Paginação do histórico e busca de usuários
- [ ] Black/Ruff + CI (GitHub Actions)
- [ ] `git init` + primeiro commit (o projeto **ainda não é repositório git**)