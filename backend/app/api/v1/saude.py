from fastapi import APIRouter
from datetime import datetime

from app.config import settings

router = APIRouter()


@router.get("")
def verificar_saude():
    """
    Verifica se a API está funcionando corretamente.
    Útil para monitoramento em produção.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "versao": settings.app_version,
        "total_questoes_configurado": settings.total_questoes,
    }