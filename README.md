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
│       ├── course/                  # Curso
│       ├── internship_field/           # UBS + Região
│       ├── room/                    # Sala + RoomSchedule + RoomTimeTable + TimeTableStudent
│       ├── student/                 # Aluno
│       └── internship/              # Vaga de Estágio + Registro + Documentos
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

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_URL` | URL do banco de dados |
| `APP_NAME` | Nome exibido na UI |
| `APP_VERSION` | Versão da API |
| `SECRET_KEY` | Chave secreta |
| `ALGORITHM` | Algoritmo para gerar os tokens  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Tempo para o token expirar |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Dias para o token de refresh expirar  |

---

## Criar secret_key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Testes

```bash
pytest tests/ -v
```

---


Documentação completa em `/docs` (Swagger UI) ou `/redoc`.
