# 06 · Histórico de alterações

> Auditoria do que mudou no projeto original. Responde, por escrito, à pergunta *"o que foi alterado?"*.

## Contexto

- **Fase 1 — análise:** somente leitura. **Nenhum** arquivo foi alterado.
- **Fase 2 — 05/10/2026:** implementação da **Opção B (Jinja2 + htmx)** escolhida pelo autor, incluindo correções de segurança.

## Arquivos criados (não existiam antes)

| Arquivo | Conteúdo |
|---|---|
| `web/__init__.py` | pacote Python |
| `web/views.py` | rotas de login/registo/logout + helpers (`usuario_do_cookie`, `_pagina`, `_fragmento`) |
| `web/chat_views.py` | tela do chat, painel com polling e envio de mensagens |
| `web/templates/base.html` | layout + carregamento do htmx local |
| `web/templates/login.html` | formulário de login |
| `web/templates/registo.html` | formulário de cadastro |
| `web/templates/chat.html` | sidebar de conversas, painel e form de envio |
| `web/templates/_mensagens.html` | fragmento: bolhas, avisos e sessão expirada |
| `web/static/style.css` | tema dark completo, responsivo (escrito à mão) |
| `web/static/vendor/htmx.min.js` | htmx 2.0.11 (52 KB) versionado — **sem CDN** |
| `README.md` | documentação principal do portfólio |
| `docs/` (6 guias) | arquitetura, API, frontend, segurança, desenvolvimento, este histórico |

## Arquivos modificados

| Arquivo | Antes | Depois | Por quê |
|---|---|---|---|
| `core/api.py` | apenas 2 routers de API | + middleware **CORS** (allowlist), + `mount /static`, + routers `web` e `chat` | servir o frontend e liberar consumo externo |
| `usuario/security.py` | `SECRET_KEY = "minha_chave_secreta_aqui"` **hardcoded** | lê `os.getenv("SECRET_KEY")` (+ fallback temporário) | segredo não pode ficar no código |
| `mensagem/api.py` | histórico **sem autenticação** — qualquer um lia qualquer conversa | exige JWT + checagem de dono → `401`/`403` | corrigir IDOR |
| `requirements.txt` | faltava o que o código importa | + `jinja2`, `python-multipart`, `PyJWT`, `pwdlib[bcrypt]` | clone do repo agora instala e roda |
| `.env.example` | 2 variáveis | + `SECRET_KEY` (placeholder) e `CORS_ORIGINS` | onboarding de novos devolvedores |
| `.env` | 2 variáveis | + `SECRET_KEY` (real, local) e `CORS_ORIGINS` | arquivo gitignored |

## Arquivos NÃO tocados (inalterados byte a byte)

`main.py` · `database/*` · `usuario/{api,models,schemas,services}.py` · `mensagem/{models,schemas,services}.py` · `.gitignore` · `.vscode/` · `chatlocal.db` *(estrutura — ver próxima seção)*

> Todas as **rotas, models, schemas e services originais permanecem iguais**.

## Alterações fora do repositório

| O quê | Detalhe |
|---|---|
| `venv` | `pip install jinja2` (3.1.6) |
| `%TEMP%` | script E2E criado, executado e **removido** |

## Registros de teste no banco (`chatlocal.db`, gitignored)

O script de validação E2E criou:

| Tipo | Registros |
|---|---|
| Usuários | `ana83cdbb`, `bia83cdbb`, `api1d9a97` |
| Mensagens | 1 mensagem ("Ola, Ana!") |

Limpeza opcional:

```sql
DELETE FROM mensagens WHERE conteudo = 'Ola, Ana!';
DELETE FROM usuarios WHERE nome_usuario IN ('ana83cdbb', 'bia83cdbb', 'api1d9a97');
```

> Os dados de 19/09 e 22/09 (Lucas, Pamela, lucas123) e os testes do autor em 05/10 (admin, admin211) **não foram tocados**.

## Validação executada (05/10/2026)

- **29 verificações E2E** com `TestClient`: criação de contas, login certo/errado, cookie httpOnly, tela do chat, polling configurado, envio/recebimento entre usuários, auto-mensagem bloqueada, sessão expirada, `401`/`403` na API, estáticos, logout e API original — **todas OK**
- **Servidor real** (`python main.py`): `/login=200 · /static/style.css=200 · htmx=51KB · /chat=200 · /=200`

## Reversibilidade

Tudo é reversível: apagar `web/` + `docs/` e restaurar os 6 arquivos modificados devolve o projeto original (o valor original do `SECRET_KEY` está registrado na tabela "Antes" acima).