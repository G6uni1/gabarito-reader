from fastapi import APIRouter
from datetime import datetime
from app.config import settings
import os
from fastapi import UploadFile, File, HTTPException
from app.vision.preprocessamento import preprocessar_imagem
import shutil

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

@router.post("/testar-visao")
async def testar_visao(arquivo: UploadFile = File(...)):
    """
    Rota temporária para testar o pipeline de visão.
    Remove antes do deploy.
    """
    # Valida extensão
    extensoes_validas = {".jpg", ".jpeg", ".png"}
    extensao = os.path.splitext(arquivo.filename)[1].lower()
    if extensao not in extensoes_validas:
        raise HTTPException(400, "Formato inválido. Use JPG ou PNG.")

    # Salva temporariamente
    caminho_temp = f"uploads/temp_{arquivo.filename}"
    with open(caminho_temp, "wb") as f:
        shutil.copyfileobj(arquivo.file, f)

    # Processa
    imagem, status = preprocessar_imagem(caminho_temp)

    # Remove arquivo temporário
    os.remove(caminho_temp)

    if imagem is None:
        raise HTTPException(422, detail=status)

    return {
        "status": status,
        "shape": imagem.shape,
        "mensagem": "Imagem processada com sucesso"
    }