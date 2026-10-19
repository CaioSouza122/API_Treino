# 🏋️ API_Treino — API de Treinos com IA

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11" />
  <img src="https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask" />
  <img src="https://img.shields.io/badge/Google_Gemini-2.5_Flash-8E75B2?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Google Gemini 2.5 Flash" />
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="Neon" />
  <img src="https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge" alt="License MIT" />
</p>

API REST em **Flask** que gera planos de treino com o **Google Gemini 2.5 Flash** e guarda cada
plano gerado em **PostgreSQL** (Neon) ou SQLite local.

É o serviço de IA do app **[HIPERTROF.IA](https://github.com/CaioSouza122/treino-app)**: o backend
FastAPI do app chama `POST /api/v1/treino` com o perfil do usuário e transforma o texto devolvido
em dias de treino (A, B, C...). A API é pensada para ser chamada **de servidor para servidor**,
autenticada por chave.

```
App mobile → backend FastAPI (treino-app) → POST /api/v1/treino (esta API) → Gemini
                                                    ↓
                                            Neon / SQLite (tabela treinos)
```

---

## Stack

| Camada | Tecnologia |
| --- | --- |
| Web | Flask 3, Gunicorn |
| Validação | Marshmallow 4 |
| Banco | SQLAlchemy (Flask-SQLAlchemy) + Alembic · PostgreSQL (Neon) ou SQLite |
| IA | `google-genai` (Gemini 2.5 Flash) |
| Segurança | Chave `X-API-KEY`, Flask-Limiter, Flask-CORS |
| Qualidade | Pytest, pytest-mock, Flake8, GitHub Actions |

---

## Estrutura

```text
API_Treino/
├── api_academia/          # Pacote da aplicação
│   ├── __init__.py        # create_app(): config, CORS, limiter, banco, rotas
│   ├── auth.py            # @require_api_key (cabeçalho X-API-KEY)
│   ├── config.py          # Variáveis de ambiente
│   ├── database.py        # Instância do SQLAlchemy
│   ├── limiter.py         # Limite de requisições por chave de API
│   ├── models.py          # Modelo Treino
│   ├── routes.py          # Endpoints /api/v1
│   ├── schemas.py         # Validação de entrada e formato de saída
│   └── services.py        # Prompt e chamada ao Gemini
├── migrations/            # Migrations do banco (Alembic)
├── tests/                 # Testes (Gemini sempre simulado)
├── app.py                 # Ponto de entrada (gunicorn app:app)
├── gunicorn.conf.py       # Workers, threads, timeout e porta de produção
├── render.yaml            # Blueprint de deploy no Render
├── Dockerfile             # Imagem de produção (opcional)
├── requirements.txt       # Dependências de produção
└── requirements-dev.txt   # + ferramentas de teste e lint
```

---

## Rodando localmente

Pré-requisitos: **Python 3.11+** e Git.

```bash
git clone https://github.com/CaioSouza122/API_Treino.git
cd API_Treino

python -m venv .venv
.\.venv\Scripts\Activate.ps1     # Windows (PowerShell)
source .venv/bin/activate        # Linux / Mac

pip install -r requirements-dev.txt
cp .env.example .env             # preencha GEMINI_API_KEY

alembic upgrade head             # cria/atualiza as tabelas
python app.py                    # http://localhost:5000
```

Com `FLASK_DEBUG=True` (como no `.env.example`), a chave `API_AUTH_KEY` é opcional. Em produção
ela é **obrigatória**: sem ela a API não inicia.

### Variáveis de ambiente

| Variável | Obrigatória | Descrição |
| --- | --- | --- |
| `GEMINI_API_KEY` | Sim | Chave do Google AI Studio. |
| `GEMINI_MODELOS` | Não | Modelos tentados em ordem, separados por vírgula. Padrão: `gemini-2.5-flash,gemini-3.5-flash-lite`. |
| `API_AUTH_KEY` | Em produção | Valor esperado no cabeçalho `X-API-KEY`. |
| `DATABASE_URL` | Não | Postgres do Neon. Vazio = SQLite local `api_academia.db`. |
| `FLASK_DEBUG` | Não | `True` só em desenvolvimento. Padrão: `False`. |
| `ALLOWED_ORIGINS` | Não | Origens de navegador para CORS, separadas por vírgula. Padrão: nenhuma. |
| `PORT` | Não | Porta do Gunicorn (o Render define). Padrão: `5000`. |
| `WEB_CONCURRENCY` / `GUNICORN_THREADS` | Não | Workers e threads do Gunicorn. Padrão: 2 e 4. |

### Comandos

| Comando | O que faz |
| --- | --- |
| `make install` | Instala dependências de produção e desenvolvimento |
| `make run` | Sobe o servidor de desenvolvimento |
| `make test` | Roda os testes (`pytest tests/`) |
| `make lint` | Roda o Flake8 (config em `.flake8`) |
| `alembic upgrade head` | Aplica as migrations pendentes |
| `alembic revision --autogenerate -m "..."` | Cria uma migration a partir dos models |

---

## Endpoints

Prefixo `/api/v1`. Todos, exceto `/` e `/health`, exigem o cabeçalho `X-API-KEY`.

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/` | Informações da API |
| `GET` | `/api/v1/health` | Health check (sem limite de requisições) |
| `POST` | `/api/v1/treino` | Gera um treino com o Gemini e salva |
| `GET` | `/api/v1/treinos?limit=50` | Treinos mais recentes (máx. 200) |
| `GET` | `/api/v1/treino/<id>` | Um treino por ID |
| `DELETE` | `/api/v1/treino/<id>` | Remove um treino |

### `POST /api/v1/treino`

```bash
curl -X POST http://localhost:5000/api/v1/treino \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: sua_chave" \
  -d '{
    "objetivo": "hipertrofia",
    "nivel": "intermediario",
    "altura": 178,
    "peso": 80,
    "idade": 28,
    "vezes_por_semana": 4,
    "tempo": 60
  }'
```

| Campo | Tipo | Regra |
| --- | --- | --- |
| `objetivo` | texto | Obrigatório, 3 a 255 caracteres |
| `nivel` | texto | `iniciante`, `intermediario` ou `avancado` (padrão `iniciante`) |
| `altura` | número | Opcional, 1 a 250 (cm) |
| `peso` | número | Opcional, 20 a 400 kg |
| `idade` | inteiro | Opcional, 10 a 100 |
| `vezes_por_semana` | inteiro | Opcional, 1 a 7 — define quantos treinos o plano terá |
| `tempo` | inteiro | Opcional, 10 a 300 minutos por sessão |

Se o Gemini estiver sobrecarregado (429/500/503), a API tenta de novo e depois passa para o modelo
reserva (`gemini-3.5-flash-lite`). Erros permanentes, como chave inválida, falham na hora.

Campos desconhecidos são recusados. O prompt pede ao Gemini um formato fixo, sem introdução,
com cada dia começando por `Treino A: <grupos musculares>`.

Resposta `201`:

```json
{
  "id": 1,
  "objetivo": "hipertrofia",
  "nivel": "intermediario",
  "treino_gerado": "Treino A: Peito e Tríceps\n- Supino reto — 4x8-10\n...",
  "criado_em": "2026-10-19T18:30:00Z"
}
```

### Erros

| Status | Quando | Corpo |
| --- | --- | --- |
| `400` | Entrada inválida | `{"erros_validacao": {"campo": ["mensagem"]}}` |
| `401` | `X-API-KEY` ausente ou errada | `{"erro": "...", "mensagem": "..."}` |
| `429` | Limite de requisições atingido | `{"erro": "...", "mensagem": "...", "detalhe": "..."}` |
| `502` | O Gemini falhou | `{"erro": "O serviço de IA está indisponível no momento."}` |
| `500` | Erro interno | `{"erro": "..."}` — o detalhe fica só no log do servidor |

### Limites de requisições

Contados **por chave de API** (ou por IP quando não há chave): 600 por hora no geral e
30 por minuto em `POST /treino`. Por trás do proxy do Render, todos os pedidos do backend chegam
do mesmo IP; contar por IP faria todos os usuários do app dividirem uma cota mínima.

---

## Testes e qualidade

```bash
make test     # 18 testes; o Gemini é sempre simulado (sem custo e sem rede)
make lint     # Flake8
```

O CI (GitHub Actions) roda o lint, confere se as migrations batem com os models e executa os
testes em todo push e pull request.

---

## Deploy no Render + Neon

1. **Neon:** crie um projeto e copie a *connection string* (`postgresql://...?sslmode=require`).
2. **Render:** *New → Blueprint* apontando para este repositório (usa o `render.yaml`), ou crie um
   *Web Service* Python com:
   - Build command: `pip install -r requirements.txt`
   - Start command: `alembic upgrade head && gunicorn app:app`
   - Health check path: `/api/v1/health`
3. Preencha no painel: `GEMINI_API_KEY`, `API_AUTH_KEY` (gere uma chave forte), `DATABASE_URL`
   (Neon) e `FLASK_DEBUG=False`. Deixe `ALLOWED_ORIGINS` vazio.
4. No backend do HIPERTROF.IA, use o mesmo valor de `API_AUTH_KEY` em `TREINO_API_KEY`.

A migration inicial só cria a tabela `treinos` se ela não existir, então um banco que já estava em
uso é adotado sem perder dados. O controle de versão fica na tabela `alembic_version_api_treino`,
separada da tabela do backend caso os dois usem o mesmo banco Neon.

> No plano gratuito o Render desliga o serviço quando fica parado. A primeira chamada depois disso
> leva ~20s para acordar o serviço, e o Gemini leva outros ~20s. O Gunicorn tem timeout de 120s.

---

## Segurança

- Segredos só em variáveis de ambiente (`.env` local, painel do Render em produção). O `.env` está
  no `.gitignore` e no `.dockerignore`.
- A chave é comparada em tempo constante (`hmac.compare_digest`).
- Respostas de erro não incluem texto de exceções.
- Acesso ao banco só pelo ORM (sem SQL montado com texto).
- CORS desligado por padrão.

---

## Licença

[MIT](LICENSE) · Desenvolvido por **Caio Souza**
