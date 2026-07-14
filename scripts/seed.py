"""Script de seed para inicializar o banco de dados (SQLite ou Postgres).

Em Postgres, aplica as migrations do Alembic (alembic/versions). Em SQLite,
usa create_all (dev/teste). Em ambos os casos, garante a existência do
usuário admin inicial — as credenciais vêm de ADMIN_NAME / ADMIN_EMAIL /
ADMIN_PASSWORD no .env (ou dos valores padrão de desenvolvimento, se não
definidos).

Uso (rodar a partir da raiz do projeto, com o venv ativado):

    python scripts/seed.py

Em produção, configure DATABASE_URL apontando para o Postgres e defina
ADMIN_EMAIL / ADMIN_PASSWORD no .env antes de rodar este comando.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import IS_SQLITE, init_db  # noqa: E402
from app.core.settings import settings  # noqa: E402

def main() -> None:
    print(f"Conectando em: {settings.DATABASE_URL}")

    init_db()
    print("Migrations aplicadas." if not IS_SQLITE else "Tabelas criadas/verificadas.")
    print(f"Usuário admin garantido: {settings.ADMIN_EMAIL}")

    if settings.ADMIN_PASSWORD == "secret123":
        print(
            "\n[ATENÇÃO] O admin foi criado com a senha padrão de desenvolvimento "
            "('secret123'). Defina ADMIN_PASSWORD (e ADMIN_EMAIL) no .env antes de "
            "rodar em produção, ou troque a senha pelo endpoint de reset assim que "
            "possível."
        )

if __name__ == "__main__":
    main()
