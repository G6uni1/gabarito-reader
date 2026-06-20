import io
import qrcode
import cv2
import numpy as np
from typing import Tuple

from app.vision.leitor_qrcode import gerar_conteudo_qrcode
from app.vision.layout_folha import (
    LARGURA, ALTURA, QUESTAO_INICIO_Y,
    QUESTAO_ALTURA, ALTERNATIVAS_X, RAIO_BOLINHA
)


def gerar_qrcode_imagem(aluno_id: int, tamanho: int = 120) -> np.ndarray:
    """
    Gera a imagem do QR Code para um aluno específico.
    Retorna como array numpy para ser inserido na folha.
    """
    conteudo = gerar_conteudo_qrcode(aluno_id)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Alta correção de erros
        box_size=4,
        border=2,
    )
    qr.add_data(conteudo)
    qr.make(fit=True)

    img_pil = qr.make_image(fill_color="black", back_color="white")

    # Converte PIL → numpy para uso com OpenCV
    img_bytes = io.BytesIO()
    img_pil.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    img_array = np.frombuffer(img_bytes.getvalue(), dtype=np.uint8)
    img_qr = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)

    # Redimensiona para o tamanho desejado
    return cv2.resize(img_qr, (tamanho, tamanho))


def gerar_folha_aluno(
    aluno_id: int,
    aluno_nome: str,
    prova_id: int,
    prova_titulo: str,
    total_questoes: int = 25,
) -> np.ndarray:
    """
    Gera a folha de resposta personalizada para um aluno.
    Inclui QR Code com o ID do aluno para identificação automática.
    """
    # Fundo branco
    folha = np.ones((ALTURA, LARGURA), dtype=np.uint8) * 255

    # ─── Cabeçalho ──────────────────────────────────────────────────────────
    cv2.putText(folha, "GABARITO READER",
                (50, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.9, 0, 2)

    cv2.putText(folha, f"Prova: {prova_titulo}",
                (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

    cv2.putText(folha, f"Aluno: {aluno_nome}",
                (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

    cv2.putText(folha, f"ID Aluno: {aluno_id} | Prova ID: {prova_id}",
                (50, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 128, 1)

    # ─── QR Code (canto superior direito) ───────────────────────────────────
    qr_img = gerar_qrcode_imagem(aluno_id, tamanho=120)
    qr_x = LARGURA - 150
    qr_y = 20
    folha[qr_y:qr_y + 120, qr_x:qr_x + 120] = qr_img

    cv2.putText(folha, "ID do Aluno",
                (qr_x + 10, qr_y + 135), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)

    # ─── Linha separadora ────────────────────────────────────────────────────
    cv2.line(folha, (30, 160), (LARGURA - 30, 160), 0, 2)

    # ─── Cabeçalho das colunas ───────────────────────────────────────────────
    cv2.putText(folha, "Nº",
                (55, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)

    for letra, x in ALTERNATIVAS_X.items():
        cv2.putText(folha, letra,
                    (x - 4, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)

    # ─── Questões ────────────────────────────────────────────────────────────
    for numero in range(1, total_questoes + 1):
        y = QUESTAO_INICIO_Y + (numero - 1) * QUESTAO_ALTURA + QUESTAO_ALTURA // 2

        # Número da questão
        cv2.putText(folha, f"{numero:2d}.",
                    (45, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)

        # Bolinhas de alternativas
        for letra, x in ALTERNATIVAS_X.items():
            cv2.circle(folha, (x, y), RAIO_BOLINHA, 0, 1)
            cv2.putText(folha, letra,
                        (x - 4, y + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)

    # ─── Rodapé ─────────────────────────────────────────────────────────────
    cv2.line(folha, (30, ALTURA - 40), (LARGURA - 30, ALTURA - 40), 0, 1)
    cv2.putText(folha, "Use caneta preta. Preencha completamente a bolinha.",
                (50, ALTURA - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, 0, 1)

    return folha


def salvar_folha(folha: np.ndarray, caminho: str) -> bool:
    """Salva a folha gerada em disco."""
    return cv2.imwrite(caminho, folha)