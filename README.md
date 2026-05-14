# NEPS API

API REST para gestão de estágios pelo NEPS.

---

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
│       ├── education_institution/   # Instituição de Ensino
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── repository.py
│       │   └── router.py
│       ├── course/                  # Curso
│       ├── health_center/           # UBS + Região
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
