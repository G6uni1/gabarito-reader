import os
import uuid
from typing import Tuple, Optional, Dict

import cv2
import numpy as np

from sqlalchemy.orm import Session

from app.config import settings
from app.vision.preprocessamento import preprocessar_imagem, carregar_imagem
from app.vision.leitor_qrcode import ler_qrcode_com_fallback
from app.vision.detector_respostas import detectar_todas_respostas
from app.services.correcao_service import gerar_resultado
from app.models.prova import Prova
from app.models.usuario import Usuario
from app.models.resultado import Resultado


class ErrosPipeline:
    """Centraliza as mensagens de erro do pipeline."""
    IMAGEM_INVALIDA = "Não foi possível processar a imagem enviada"
    ALUNO_NAO_IDENTIFICADO = "QR Code não encontrado ou inválido — não foi possível identificar o aluno"
    ALUNO_NAO_EXISTE = "O aluno identificado pelo QR Code não existe no sistema"
    PROVA_NAO_ENCONTRADA = "Prova não encontrada ou inativa"
    GABARITO_VAZIO = "Esta prova não possui gabarito cadastrado"


def salvar_upload_temporario(conteudo_bytes: bytes, extensao: str) -> str:
    """
    Salva o arquivo enviado em disco com nome único.
    Retorna o caminho do arquivo temporário.
    """
    nome_unico = f"{uuid.uuid4().hex}{extensao}"
    caminho = os.path.join(settings.upload_dir, f"temp_{nome_unico}")

    with open(caminho, "wb") as f:
        f.write(conteudo_bytes)

    return caminho


def remover_arquivo(caminho: str) -> None:
    """Remove arquivo do disco ignorando erros."""
    try:
        os.remove(caminho)
    except OSError:
        pass


def executar_pipeline(
    db: Session,
    conteudo_bytes: bytes,
    extensao: str,
    prova_id: int,
) -> Tuple[Optional[Resultado], Optional[str], Dict]:
    """
    Pipeline completo de correção automática.

    Retorna:
    - Resultado salvo (ou None em caso de erro)
    - Mensagem de erro (ou None se sucesso)
    - Dados de diagnóstico (útil para debug)
    """
    diagnostico = {
        "aluno_id": None,
        "total_questoes_detectadas": 0,
        "questoes_invalidas": [],
        "perspectiva_corrigida": False,
    }

    # ── Validar prova ────────────────────────────────────────────────────────
    prova = db.query(Prova).filter(
        Prova.id == prova_id,
        Prova.ativa == True
    ).first()

    if not prova:
        return None, ErrosPipeline.PROVA_NAO_ENCONTRADA, diagnostico

    # ── Salvar imagem temporariamente ────────────────────────────────────────
    caminho_temp = salvar_upload_temporario(conteudo_bytes, extensao)

    try:
        # ── Pré-processamento ────────────────────────────────────────────────
        imagem_original = carregar_imagem(caminho_temp)
        if imagem_original is None:
            return None, ErrosPipeline.IMAGEM_INVALIDA, diagnostico

        imagem_processada, status = preprocessar_imagem(caminho_temp)
        if imagem_processada is None:
            return None, ErrosPipeline.IMAGEM_INVALIDA, diagnostico

        # ── Identificar aluno pelo QR Code ───────────────────────────────────
        # Tenta na imagem original (melhor para QR Code) antes da binarização
        aluno_id = ler_qrcode_com_fallback(imagem_original)

        if aluno_id is None:
            return None, ErrosPipeline.ALUNO_NAO_IDENTIFICADO, diagnostico

        diagnostico["aluno_id"] = aluno_id

        # Verifica se o aluno existe no banco
        aluno = db.query(Usuario).filter(
            Usuario.id == aluno_id,
            Usuario.ativo == True
        ).first()

        if not aluno:
            return None, ErrosPipeline.ALUNO_NAO_EXISTE, diagnostico

        # ── Detectar respostas ───────────────────────────────────────────────
        resultado_deteccao = detectar_todas_respostas(
            imagem_processada,
            total_questoes=prova.total_questoes
        )

        diagnostico["total_questoes_detectadas"] = resultado_deteccao["total_detectadas"]
        diagnostico["questoes_invalidas"] = resultado_deteccao["questoes_invalidas"]

        # ── Corrigir e persistir ─────────────────────────────────────────────
        resultado = gerar_resultado(
            db=db,
            aluno_id=aluno_id,
            prova_id=prova_id,
            respostas_aluno=resultado_deteccao["respostas"],
        )

        return resultado, None, diagnostico

    finally:
        # Sempre remove o arquivo temporário, mesmo se ocorrer erro
        remover_arquivo(caminho_temp)