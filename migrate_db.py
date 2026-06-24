
"""
Script para limpar e reinicializar o banco de dados.
Execute apenas se tiver problemas de schema mismatch.
"""
import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

db_path = "neps.db"
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"✓ Banco de dados '{db_path}' removido")
    except Exception as e:
        print(f"✗ Erro ao remover '{db_path}': {e}")
        sys.exit(1)

try:
    from app.core.database import init_db, engine
    from sqlalchemy import text

    print("Inicializando banco de dados...")
    init_db()

    print("Verificando schema...")
    with engine.begin() as conn:

        result = conn.execute(text("PRAGMA table_info(internships)"))
        columns = {row[1] for row in result.fetchall()}
        if "region_id" in columns:
            print("✓ Coluna 'region_id' existe em 'internships'")
        else:
            print("✗ Coluna 'region_id' NÃO existe em 'internships'")
            sys.exit(1)

        result = conn.execute(text("PRAGMA table_info(students)"))
        columns = {row[1] for row in result.fetchall()}
        if "discipline_id" in columns:
            print("✓ Coluna 'discipline_id' existe em 'students'")
        else:
            print("✗ Coluna 'discipline_id' NÃO existe em 'students'")
            sys.exit(1)

    print("\n✓ Banco de dados reinicializado com sucesso!")

except Exception as e:
    print(f"✗ Erro durante inicialização: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
