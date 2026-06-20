import os
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.api.deps import get_professor_atual
from app.models.usuario import Usuario
from app.config import settings
from app.services.pipeline_service import executar_pipeline
from app.schemas.resultado import ResultadoResponse

router = APIRouter()

EXTENSOES_VALIDAS = {".jpg", ".jpeg", ".png"}
MAX_BYTES = settings.max_file_size_mb * 1024 * 1024  # Converte MB para bytes


@router.post("/gabarito/{prova_id}", response_model=ResultadoResponse, status_code=201)
async def processar_gabarito(
    prova_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    professor: Usuario = Depends(get_professor_atual),
):
    """
    Recebe a foto do gabarito preenchido e executa o pipeline completo:
    1. Identifica o aluno pelo QR Code
    2. Detecta as respostas marcadas
    3. Corrige automaticamente contra o gabarito oficial
    4. Salva e retorna o resultado
    """
    # ── Validar extensão ─────────────────────────────────────────────────────
    extensao = os.path.splitext(arquivo.filename or "")[1].lower()
    if extensao not in EXTENSOES_VALIDAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato inválido. Use: {', '.join(EXTENSOES_VALIDAS)}"
        )

    # ── Validar tamanho ──────────────────────────────────────────────────────
    conteudo = await arquivo.read()
    if len(conteudo) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Arquivo muito grande. Máximo: {settings.max_file_size_mb}MB"
        )

    # ── Executar pipeline ────────────────────────────────────────────────────
    resultado, erro, diagnostico = executar_pipeline(
        db=db,
        conteudo_bytes=conteudo,
        extensao=extensao,
        prova_id=prova_id,
    )

    if erro:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "erro": erro,
                "diagnostico": diagnostico,
            }
        )

    return resultado


@router.post("/gabarito/{prova_id}/diagnostico")
async def diagnosticar_gabarito(
    prova_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    professor: Usuario = Depends(get_professor_atual),
):
    """
    Versão de diagnóstico — executa o pipeline mas retorna
    detalhes internos em vez de só o resultado final.
    Útil para depurar problemas de detecção.
    """
    extensao = os.path.splitext(arquivo.filename or "")[1].lower()
    if extensao not in EXTENSOES_VALIDAS:
        raise HTTPException(400, detail="Formato inválido")

    conteudo = await arquivo.read()
    resultado, erro, diagnostico = executar_pipeline(
        db=db,
        conteudo_bytes=conteudo,
        extensao=extensao,
        prova_id=prova_id,
    )

    return {
        "sucesso": erro is None,
        "erro": erro,
        "diagnostico": diagnostico,
        "resultado_id": resultado.id if resultado else None,
        "nota": resultado.nota if resultado else None,
    }