import cv2
import numpy as np
from typing import Dict, Optional, Tuple

from app.vision.layout_folha import (
    QUESTAO_INICIO_Y,
    QUESTAO_ALTURA,
    QUESTAO_MARGEM,
    ALTERNATIVAS_X,
    RAIO_BOLINHA,
    THRESHOLD_MARCACAO,
    TOTAL_QUESTOES,
)


def calcular_y_questao(numero_questao: int) -> int:
    """
    Calcula a posição Y central de uma questão.
    numero_questao começa em 1.
    """
    return QUESTAO_INICIO_Y + (numero_questao - 1) * QUESTAO_ALTURA + QUESTAO_ALTURA // 2


def extrair_roi_bolinha(
    imagem: np.ndarray,
    centro_x: int,
    centro_y: int,
    raio: int = RAIO_BOLINHA
) -> Optional[np.ndarray]:
    """
    Extrai a região de interesse ao redor de uma bolinha.
    Retorna None se a região estiver fora dos limites da imagem.
    """
    y1 = centro_y - raio
    y2 = centro_y + raio
    x1 = centro_x - raio
    x2 = centro_x + raio

    # Verifica se está dentro dos limites
    altura, largura = imagem.shape[:2]
    if y1 < 0 or y2 > altura or x1 < 0 or x2 > largura:
        return None

    return imagem[y1:y2, x1:x2]


def esta_marcada(roi: np.ndarray, threshold: float = THRESHOLD_MARCACAO) -> bool:
    """
    Verifica se uma bolinha está marcada.
    Conta pixels brancos (255) e compara com o total.
    """
    if roi is None:
        return False

    total_pixels = roi.size
    pixels_brancos = np.count_nonzero(roi)
    proporcao = pixels_brancos / total_pixels

    return proporcao >= threshold


def detectar_resposta_questao(
    imagem: np.ndarray,
    numero_questao: int
) -> Tuple[Optional[str], Dict[str, float]]:
    """
    Detecta qual alternativa foi marcada em uma questão.

    Retorna:
    - letra da alternativa marcada (ou None se nenhuma/múltiplas)
    - dicionário com proporção de preenchimento de cada alternativa
    """
    centro_y = calcular_y_questao(numero_questao)
    proporcoes = {}
    marcadas = []

    for letra, centro_x in ALTERNATIVAS_X.items():
        roi = extrair_roi_bolinha(imagem, centro_x, centro_y)
        if roi is None:
            proporcoes[letra] = 0.0
            continue

        total_pixels = roi.size
        pixels_brancos = int(np.count_nonzero(roi))
        proporcao = pixels_brancos / total_pixels
        proporcoes[letra] = round(proporcao, 4)

        if proporcao >= THRESHOLD_MARCACAO:
            marcadas.append(letra)

    # Resultado da detecção
    if len(marcadas) == 1:
        return marcadas[0], proporcoes        # ✅ Uma resposta clara
    elif len(marcadas) == 0:
        return None, proporcoes               # ⚠️ Nenhuma marcada
    else:
        # Múltiplas marcadas — retorna a com maior preenchimento
        mais_marcada = max(proporcoes, key=proporcoes.get)
        return mais_marcada, proporcoes


def detectar_todas_respostas(
    imagem: np.ndarray,
    total_questoes: int = TOTAL_QUESTOES
) -> Dict:
    """
    Detecta as respostas de todas as questões.

    Retorna um dicionário com:
    - respostas: {"1": "A", "2": "C", ...}
    - detalhes: proporções de cada alternativa por questão
    - questoes_invalidas: questões sem resposta ou com múltiplas
    """
    respostas = {}
    detalhes = {}
    questoes_invalidas = []

    for numero in range(1, total_questoes + 1):
        resposta, proporcoes = detectar_resposta_questao(imagem, numero)
        detalhes[str(numero)] = proporcoes

        if resposta is not None:
            respostas[str(numero)] = resposta
        else:
            questoes_invalidas.append(numero)

    return {
        "respostas": respostas,
        "detalhes": detalhes,
        "questoes_invalidas": questoes_invalidas,
        "total_detectadas": len(respostas),
    }