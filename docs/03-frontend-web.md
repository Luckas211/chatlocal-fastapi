# 03 · Frontend web (Jinja2 + htmx)

> Como funciona a camada de interface: páginas, templates, autenticação por cookie e o polling sem JavaScript.

## Estrutura

```
web/
├── views.py              # /login, /registo, /logout + helpers compartilhados
├── chat_views.py         # /chat, /chat/mensagens/{id}, /chat/enviar
├── templates/
│   ├── base.html         # layout (topo, rodapé) + carrega o htmx
│   ├── login.html        # formulário de entrada
│   ├── registo.html      # criação de conta
│   ├── chat.html         # sidebar + painel + formulário de envio
│   └── _mensagens.html   # fragmento: bolhas, avisos, sessão expirada
└── static/
    ├── style.css         # visual dark escrito à mão (sem framework)
    └── vendor/htmx.min.js  # htmx 2.0.11 local — funciona offline, sem CDN
```

## Rotas

| Método | Rota | O que faz | Sem sessão |
|---|---|---|---|
| GET | `/login` | página de login | — (com sessão → 303 `/chat`) |
| POST | `/login` | valida e grava cookie | `400` + mensagem na página |
| GET/POST | `/registo` | criação de conta | `400` validação · `409` duplicado |
| POST | `/logout` | apaga o cookie | — |
| GET | `/chat` | tela do chat (`?contato_id=` opcional) | **303 → /login** |
| GET | `/chat/mensagens/{id}` | fragmento do painel (**polling**) | `200` + aviso "sessão expirou" |
| POST | `/chat/enviar` | grava e devolve o painel atualizado | `200` + aviso |
| GET | `/static/*` | CSS + htmx | público |

## Autenticação: por que cookie e não Bearer?

Formulários HTML **não conseguem** enviar cabeçalhos personalizados. A solução:

1. `POST /login` → `criar_token_acesso()` gera o JWT
2. Resposta grava `Set-Cookie: access_token=...; HttpOnly; SameSite=Lax; Max-Age=3600`
3. O navegador **anexa o cookie sozinho** a toda requisição same-origin
4. `usuario_do_cookie()` (`web/views.py`) decodifica e devolve o `id`; token expirado/inválido → `None` → redirect ou aviso

O servidor **não guarda sessão alguma** — a identidade vive no JWT, igual à API.

## O polling (a "mágica" sem JavaScript)

Em `chat.html`:

```html
<div id="painel-mensagens" class="mensagens"
     hx-get="/chat/mensagens/{{ contato.id }}"
     hx-trigger="load, every 3s"
     hx-swap="innerHTML scroll:bottom">
```

| Atributo | Efeito |
|---|---|
| `hx-get` | busca o fragmento `_mensagens.html` |
| `hx-trigger="load, every 3s"` | busca **ao carregar** (resolve o scroll inicial) e **depois a cada 3 s** |
| `hx-swap="innerHTML scroll:bottom"` | substitui o conteúdo **e rola até a última mensagem** |

Por que **HTTP 200 sempre** no fragmento: se devolvesse `401/303` em erro, o htmx não faria swap e o usuário ficaria sem feedback. Em vez disso, o template `_mensagens.html` tem estados:

- `sessao_expirada=True` → aviso com link "Entrar novamente"
- `erro="..."` → bolha de erro (ex.: "Não é possível enviar mensagem para si mesmo")
- `mensagens=[...]` → bolhas normais (`class="bolha eu"` à direita, `outro` à esquerda)

Todos os fragmentos saem com `Cache-Control: no-store` — senão o navegador poderia servir mensagens velhas no polling.

## Envio

```html
<form hx-post="/chat/enviar"
      hx-target="#painel-mensagens"
      hx-swap="innerHTML scroll:bottom"
      hx-on::after-request="this.reset()">
```

- O servidor grava a mensagem e **devolve o painel inteiro já atualizado**
- `hx-on::after-request="this.reset()"` limpa o campo após a requisição — é a **única expressão estilo-JS** do projeto (8 caracteres dentro de um atributo htmx; nenhum arquivo `.js` escrito à mão)
- Trocando por `<textarea>` + Enter exigiria JS de verdade; por isso a entrada é `input type="text"` (Enter = enviar, nativo do HTML)

## CSS (`static/style.css`)

- Tema dark com variáveis CSS em `:root` (`--fundo`, `--destaque`, `--eu`...) — trocar a paleta = editar 10 linhas
- Layout: `body` em coluna flex → `.chat` em **grid** `290px 1fr` (sidebar + conversa)
- Bolhas: `align-self: flex-end` (eu) / `flex-start` (outro)
- Responsivo: abaixo de **760px** a sidebar vira faixa superior (`.lateral { max-height: 34vh }`)
- Barras de rolagem estilizadas via `::-webkit-scrollbar`

## Receita: adicionar uma página nova

1. Rota em `web/views.py` (ou novo módulo + `include_router` no `core/api.py`)
2. Template em `web/templates/` estendendo `base.html`
3. `return _pagina(request, "meu-template.html", {...})`
4. Protegida? Chame `usuario_do_cookie(request)` e redirecione se `None`

## Por que não WebSocket (ainda)?

Sem JavaScript não existe WebSocket no navegador (a API é JS). O polling de 3 s é a alternativa 100% HTML — e é a razão de o HTML trocar a cada ciclo. O roadmap prevê **SSE/WebSocket** quando a camada de apresentação aceitar JS (htmx já tem extensão oficial para SSE).