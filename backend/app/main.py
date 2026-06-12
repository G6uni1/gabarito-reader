from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database.database import engine, Base
import app.models  # Garante que os modelos são carregados antes do create_all

# Cria todas as tabelas no banco ao iniciar (se não existirem)
Base.metadata.create_all(bind=engine)

# Criação da instância principal da aplicação
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de leitura e correção automática de gabaritos",
    docs_url="/docs",       # Documentação Swagger (automática!)
    redoc_url="/redoc",     # Documentação alternativa
)

# Configuração do CORS
# Permite que o frontend React (rodando em outra porta) acesse a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Porta padrão do Vite (React)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rota raiz — só para confirmar que a API está viva
@app.get("/")
def raiz():
    return {
        "projeto": settings.app_name,
        "versao": settings.app_version,
        "docs": "/docs",
    }


# Importação dos roteadores (vamos criar a seguir)
from app.api.v1 import router as router_v1
app.include_router(router_v1, prefix="/api/v1")