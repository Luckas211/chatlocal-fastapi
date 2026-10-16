# 04 · Segurança

> O que está implementado, o que foi corrigido e o que ainda é limitação conhecida.

## Medidas implementadas

### Senhas
- Hash **bcrypt** via `pwdlib` (`usuario/security.py`: `obter_hash_senha` / `verificar_senha`)
- O banco guarda **apenas o hash** — texto puro nunca toca disco nem aparece na API
- Verificação com `verify()` (comparação segura do próprio bcrypt)

### Sessão e tokens
- JWT **HS256** com validade de 60 min (`exp` no payload)
- **API:** header `Authorization: Bearer` (padrão OAuth2 do FastAPI)
- **Web:** cookie `access_token` com:
  - `HttpOnly` — JavaScript nenhum lê o token (anti roubo via XSS)
  - `SameSite=Lax` — mitigação de CSRF em formulários cross-site
  - `Max-Age=3600` — expira junto com o token
- Logout = apagar o cookie (o token expira sozinho)

### Autorização (correção de IDOR)
`GET /api/mensagens/{usuario_id}/{destinatario_id}` agora:
1. **exige token** — sem ele responde `401`;
2. **compara o dono** — token de outro usuário responde `403`.

> Antes, **qualquer pessoa lia qualquer conversa** apenas sabendo os dois IDs.

### Segredos fora do código
- `SECRET_KEY` vive no `.env` (ignorado pelo `.gitignore`) e é lida com `os.getenv`
- Sem `SECRET_KEY`, uma chave temporária é gerada no boot (tokens caem a cada reinício — aceitável **só** em dev)
- `.env.example` documenta as variáveis sem valores reais

### XSS
- Jinja2 escapa todo `{{ }}` por padrão: conteúdo de mensagem é exibido como **texto**, jamais executado

### CORS
- Allowlist por origem via `CORS_ORIGINS` (`.env`), com `allow_credentials=True` (necessário para cookies)

### Validações
- Pydantic na API (`min_length`, `max_length`, `gt=0`) → `422`
- Re-validação nas rotas web com mensagens amigáveis → `400`/`409`
- Constraint `unique` no banco + `IntegrityError` tratado → `409` sem vazar stack trace

## Ameaça → mitigação

| Ameaça | Mitigação |
|---|---|
| Vazamento de senhas no banco | hash bcrypt |
| Forja de token | assinatura HS256 com `SECRET_KEY` secreta |
| Roubo de token por XSS | cookie HttpOnly + escape do Jinja2 |
| CSRF em formulários | `SameSite=Lax` + htmx `selfRequestsOnly` (padrão) |
| Leitura de conversa alheia (IDOR) | checagem de dono → `403` |
| Chave secreta versionada | `.env` fora do git |
| Site malicioso chamando a API | allowlist CORS |
| Polling servindo página cacheada | `Cache-Control: no-store` nos fragmentos |

## Limitações conhecidas (roadmap de segurança)

| Item | Ideia |
|---|---|
| Sem HTTPS em produção | TLS obrigatório antes de qualquer deploy (cookie sem `Secure`) |
| Sem rate limiting no login | limitar tentativas (ex.: 5/min por IP) |
| Senha mínima de 4 caracteres | subir para 8 + política de complexidade |
| Sem refresh token | sessão "curta" de 60 min é decisão consciente |
| Sem recuperação de senha | fluxo de e-mail |
| `echo=True` no engine | polui logs — amarrar ao `DEBUG` |
| `datetime.utcnow` (deprecado no 3.12) | migrar para `datetime.now(timezone.utc)` |

> **Regra de ouro:** isto é um projeto de portfólio local. Antes de qualquer deploy real: HTTPS, `SECRET_KEY` forte, rate limit e revisão da tabela acima.