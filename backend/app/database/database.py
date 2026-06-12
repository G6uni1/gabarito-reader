from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Motor de conexão com o banco
# O argumento extra é necessário apenas para SQLite
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}  # Apenas para SQLite
)

# Fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base que todos os modelos vão herdar
Base = declarative_base()


# Dependência do FastAPI — fornece uma sessão por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db        # Entrega a sessão para a rota
    finally:
        db.close()      # Garante que a sessão sempre fecha