from fastapi import APIRouter

from app.api.v1 import saude, provas, auth, resultados


router = APIRouter()

router.include_router(saude.router, prefix="/saude", tags=["Saúde"])
router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
router.include_router(provas.router, prefix="/provas", tags=["Provas"])
router.include_router(resultados.router, prefix="/resultados", tags=["Resultados"])