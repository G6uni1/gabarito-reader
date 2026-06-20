import cv2
import numpy as np
from typing import Optional

PREFIXO_ALUNO = "GABARITO_ALUNO:"

# Detector nativo do OpenCV — não precisa de DLL externa
detector = cv2.QRCodeDetector()


def gerar_conteudo_qrcode(aluno_id: int) -> str:
    return f"{PREFIXO_ALUNO}{aluno_id}"


def ler_qrcode(imagem: np.ndarray) -> Optional[str]:
    """Lê QR Code usando o detector nativo do OpenCV."""
    conteudo, _, _ = detector.detectAndDecode(imagem)
    if conteudo:
        return conteudo
    return None


def extrair_aluno_id(imagem: np.ndarray) -> Optional[int]:
    conteudo = ler_qrcode(imagem)
    if conteudo is None:
        return None
    if not conteudo.startswith(PREFIXO_ALUNO):
        return None
    try:
        return int(conteudo.replace(PREFIXO_ALUNO, ""))
    except ValueError:
        return None


def ler_qrcode_com_fallback(imagem: np.ndarray) -> Optional[int]:
    """Tenta ler o QR Code com pré-processamentos progressivos."""
    # Tentativa 1: imagem original
    aluno_id = extrair_aluno_id(imagem)
    if aluno_id is not None:
        return aluno_id

    # Tentativa 2: converter para cinza
    if len(imagem.shape) == 3:
        cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
        aluno_id = extrair_aluno_id(cinza)
        if aluno_id is not None:
            return aluno_id

    # Tentativa 3: aumentar contraste
    equalizada = cv2.equalizeHist(
        cinza if len(imagem.shape) == 3 else imagem
    )
    aluno_id = extrair_aluno_id(equalizada)
    return aluno_id