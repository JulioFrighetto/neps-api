import os
import sys

db_path = "neps.db"
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Banco de dados '{db_path}' removido com sucesso")
else:
    print(f"Banco de dados '{db_path}' não encontrado")

# Now reinit
from app.core.database import init_db
print("Reinicializando banco de dados...")
init_db()
print("Banco de dados reinicializado com sucesso!")
