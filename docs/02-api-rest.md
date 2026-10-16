# 02 · Referência da API REST

- **Base URL (local):** `http://127.0.0.1:8000`
- **Documentação interativa:** `/docs` (Swagger UI) · `/redoc` · esquema em `/openapi.json`

## Autenticação (OAuth2 password)

```bash
curl -X POST "http://127.0.0.1:8000/api/usuarios/login" \
  -d "username=ana" -d "password=senha123"
# 200 → {"access_token": "eyJhbGciOi...", "token_type": "bearer"}
```

| Item | Valor |
|---|---|
| Algoritmo | JWT assinado com **HS256** |
| Validade | **60 minutos** (`exp` no payload) |
| Payload | `{"sub": "<id>", "nome_usuario": "...", "exp": ...}` |
| Envio | header `Authorization: Bearer <token>` |
| Erros | `400` credenciais inválidas · `401` token ausente/inválido/expirado |

## Endpoints de usuários

### POST `/api/usuarios/` — criar usuário (pública)

```json
{ "nome_usuario": "ana", "nome_completo": "Ana Souza", "senha": "senha123" }
```

| Regra | Resposta |
|---|---|
| válido | `201` com `{"id": 4, "nome_usuario": "ana", "nome_completo": "Ana Souza"}` (a **senha nunca** aparece) |
| nome já existe | `409` `{"detail": "Já existe um usuário com este nome."}` |
| nome < 3 ou senha < 4 | `422` (validação do Pydantic) |

### POST `/api/usuarios/login` — gerar token (pública)

Recebe **form-urlencoded** (`username`, `password` — padrão OAuth2 do Swagger). Resposta `200` com `access_token` + `token_type`; `400` com `{"detail": "Usuário ou senha incorretos."}`.

### GET `/api/usuarios/` — listar usuários (🔒)

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/usuarios/
# 200 → [ {"id": 1, "nome_usuario": "lucas", "nome_completo": "Lucas silva"}, ... ]
```
Sem token → `401`. Não há paginação (limitação conhecida — ver roadmap).

## Endpoints de mensagens

### POST `/api/mensagens/` — enviar mensagem direta (🔒)

```json
{ "conteudo": "Olá, tudo bem?", "destinatario_id": 2 }
```

| Regra | Resposta |
|---|---|
| válido | `201` com a mensagem completa |
| destino = você mesmo | `400` `{"detail": "Não é possível enviar mensagem para si mesmo."}` |
| remetente/destinatário inexistente | `404` |
| conteúdo vazio ou > 500 | `422` |

Resposta `201` (com os dois lados já resolvidos):

```json
{
  "id": 7,
  "conteudo": "Olá, tudo bem?",
  "data_envio": "2026-10-05T23:35:52.724828",
  "usuario_id": 1,
  "destinatario_id": 2,
  "remetente":   { "id": 1, "nome_usuario": "lucas" },
  "destinatario": { "id": 2, "nome_usuario": "pamela" }
}
```

### GET `/api/mensagens/{usuario_id}/{destinatario_id}` — histórico (🔒)

Devolve **toda a conversa** entre os dois IDs em ordem cronológica.

```bash
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8000/api/mensagens/1/2
```

| Situação | Resposta |
|---|---|
| token dono de `usuario_id` | `200` → lista de mensagens |
| sem token | `401` |
| token de **outro** usuário | `403` `{"detail": "Acesso negado: você só pode ler a própria conversa."}` |

> Esta rota exigia autenticação **nem verificava dono** até a correção de segurança de 05/10/2026 (ver `docs/06-historico-de-mudancas.md`).

## Formato de erro padrão

Toda a API devolve erros como `{"detail": "<mensagem>"}`:

| Código | Quando |
|---|---|
| `400` | regra de negócio violada (senha errada, auto-mensagem) |
| `401` | sem token, token inválido ou expirado |
| `403` | token válido, mas não é o dono do recurso |
| `404` | recurso inexistente |
| `409` | conflito (nome de usuário duplicado) |
| `422` | corpo/parâmetros fora das regras do Pydantic |

## Outros

- `GET /` → `{"status": "online", "service": "CHATLOCAL API", "docs": "/docs"}`
- CORS: origens liberadas via variável `CORS_ORIGINS` no `.env` (padrão: `localhost:5173`)
- Rate limiting, refresh token e paginação **não existem ainda** — ver `docs/04-seguranca.md`