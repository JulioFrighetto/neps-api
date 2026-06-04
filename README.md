# NEPS API

API REST para gestão de estágios pelo NEPS.

---

## Tecnologias

<p align="left">
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python 3.12">
  </a>

  <a href="https://pypi.org/project/fastapi/0.111.0/">
    <img src="https://img.shields.io/badge/FastAPI-0.111.0-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  </a>

  <a href="https://pypi.org/project/SQLAlchemy/2.0.30/">
    <img src="https://img.shields.io/badge/SQLAlchemy-2.0.30-red?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  </a>

  <a href="https://pypi.org/project/pydantic/2.7.1/">
    <img src="https://img.shields.io/badge/Pydantic-2.7.1-E92063?logo=pydantic&logoColor=white" alt="Pydantic">
  </a>

  <a href="https://pypi.org/project/uvicorn/0.29.0/">
    <img src="https://img.shields.io/badge/Uvicorn-0.29.0-4051B5?logo=uvicorn&logoColor=white" alt="Uvicorn">
  </a>
</p>

## Estrutura do projeto

```
NEPS-API/
├── app/
│   ├── main.py                      # Entry point — registra routers e cria tabelas
│   ├── core/
│   │   ├── database.py              # Engine, SessionLocal, Base, get_db
│   │   ├── models.py                # Registry central de modelos (garante create_all)
│   │   └── settings.py              # Configurações via Pydantic Settings / .env
│   └── domains/
│       ├── education_institute/   # Instituição de Ensino
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── repository.py
│       │   └── router.py
│       ├── discipline/                  # Curso
│       ├── room/                    # Sala + RoomSchedule + RoomTimeTable + TimeTableStudent
│       └── student/                 # Aluno
├── tests/
│   └── test_domains.py
├── .env
└── requirements.txt
```

## Setup

```bash
# 1. Criar e ativar virtualenv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar a API
uvicorn app.main:app --reload

# 4. Acessar a documentação interativa
open http://localhost:8000/docs
```

---

## Variáveis de ambiente (`.env`)

| Variável                      | Padrão                                            | Descrição |
| ----------------------------- | ------------------------------------------------- | --------- |
| `DATABASE_URL`                | URL do banco de dados                             |
| `APP_NAME`                    | Nome exibido na UI                                |
| `APP_VERSION`                 | Versão da API                                     |
| `SECRET_KEY`                  | Chave secreta                                     |
| `ALGORITHM`                   | Algoritmo para gerar os tokens                    |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo para o token expirar                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Dias para o token de refresh expirar              |
| `RESET_TOKEN_EXPIRE_MINUTES`  | Tempo para o link de redefinição expirar          |
| `FRONTEND_URL`                | URL do frontend para montar o link do e-mail      |
| `SMTP_HOST`                   | Servidor SMTP para envio dos e-mails              |
| `SMTP_PORT`                   | Porta SMTP                                        |
| `SMTP_USERNAME`               | Usuário SMTP                                      |
| `SMTP_PASSWORD`               | Senha SMTP                                        |
| `SMTP_FROM`                   | E-mail remetente                                  |
| `SMTP_FROM_NAME`              | Nome exibido como remetente                       |
| `SMTP_USE_TLS`                | Usa TLS no envio                                  |
| `SMTP_USE_SSL`                | Usa SSL no envio                                  |
| `CORS_ORIGINS`                | Lista JSON com as origens permitidas no navegador |

Exemplo de `.env`:

```env
DATABASE_URL="sqlite:///./neps.db"
APP_NAME="Neps API"
APP_VERSION="0.1.0"
DEBUG=true
SECRET_KEY="coloque_uma_chave_forte_aqui"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
RESET_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL="http://localhost:5173"
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="alexdonay@gmail.com"
SMTP_PASSWORD="sua_senha_de_app_do_gmail"
SMTP_FROM="alexdonay@gmail.com"
SMTP_FROM_NAME="NEPS API"
SMTP_USE_TLS=true
SMTP_USE_SSL=false
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:8000","http://127.0.0.1:3000","http://127.0.0.1:5173","http://127.0.0.1:8000"]
```

Se você for enviar pelo Gmail, use senha de app na `SMTP_PASSWORD`.

Fluxo de recuperação de senha:

1. `POST /api/v1/auth/reset-password` com o `email` do usuário.
1. O backend envia um e-mail com link para `FRONTEND_URL/reset-password?token=...`.
1. O frontend envia `POST /api/v1/auth/reset-password/confirm` com `reset_token` e `new_password`.

---

## Criar secret_key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Rodar seed

```bash
python.exe -c "from app.core.database import Base, engine, seed_admin; Base.metadata.create_all(bind=engine); seed_admin(); print('seed_admin executed')"
```

---

## Testes

```bash
pytest tests/ -v
```

---

Documentação completa em `/docs` (Swagger UI) ou `/redoc`.

Para a tela de histórico do período, consulte [docs/history-period.md](docs/history-period.md).
