import sys
from pathlib import Path
sys.path.append(str(Path('.').resolve()))
from app.core.database import init_db, SessionLocal
from app.domains.internships.model import Internship

# Reset DB (drop all & recreate)
init_db()

# Seed data
session = SessionLocal()
seed = [
    Internship(name='Estágio Saúde', is_active=True),
    Internship(name='Estágio Educação', is_active=True),
    Internship(name='Estágio Tecnologia', is_active=True),
]
session.add_all(seed)
session.commit()
print('✅ Seed concluído –', session.query(Internship).count(), 'estágios inseridos.')
session.close()
