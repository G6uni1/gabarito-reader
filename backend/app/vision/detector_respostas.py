import cv2
import numpy as np
from typing import Dict, Optional, Tuple

from app.vision.layout_folha import (
    ALTERNATIVAS_X,
    RAIO_BOLINHA,
    THRESHOLD_MARCACAO,
    TOTAL_QUESTOES,
    calcular_layout,
)


def calcular_y_questao(numero_questao: int, layout: dict) -> int:
    """
    Calcula a posição Y central de uma questão com base no layout dinâmico.
    numero_questao começa em 1.
    """
    return (
        layout["questao_inicio_y"]
        + (numero_questao - 1) * layout["questao_altura"]
        + layout["questao_altura"] // 2
    )


def extrair_roi_bolinha(
    imagem: np.ndarray,
    centro_x: int,
    centro_y: int,
    raio: int = RAIO_BOLINHA
) -> Optional[np.ndarray]:
    y1 = centro_y - raio
    y2 = centro_y + raio
    x1 = centro_x - raio
    x2 = centro_x + raio

    altura, largura = imagem.shape[:2]
    if y1 < 0 or y2 > altura or x1 < 0 or x2 > largura:
        return None

    return imagem[y1:y2, x1:x2]


def detectar_resposta_questao(
    imagem: np.ndarray,
    numero_questao: int,
    layout: dict,
) -> Tuple[Optional[str], Dict[str, float]]:
    """
    Detecta qual alternativa foi marcada em uma questão.
    Usa o layout dinâmico para calcular as coordenadas.
    """
    centro_y = calcular_y_questao(numero_questao, layout)
    proporcoes = {}
    marcadas = []

    for letra, centro_x in ALTERNATIVAS_X.items():
        roi = extrair_roi_bolinha(imagem, centro_x, centro_y)
        if roi is None:
            proporcoes[letra] = 0.0
            continue

        pixels_brancos = int(np.count_nonzero(roi))
        proporcao = pixels_brancos / roi.size
        proporcoes[letra] = round(proporcao, 4)

        if proporcao >= THRESHOLD_MARCACAO:
            marcadas.append(letra)

    if len(marcadas) == 1:
        return marcadas[0], proporcoes
    elif len(marcadas) == 0:
        return None, proporcoes
    else:
        mais_marcada = max(proporcoes, key=proporcoes.get)
        return mais_marcada, proporcoes


def detectar_todas_respostas(
    imagem: np.ndarray,
    total_questoes: int = TOTAL_QUESTOES,
) -> Dict:
    """
    Detecta as respostas de todas as questões.
    Calcula o layout dinamicamente com base em total_questoes.
    """
    # ← Aqui está a mágica: layout calculado na hora
    layout = calcular_layout(total_questoes)

    respostas = {}
    detalhes = {}
    questoes_invalidas = []

    for numero in range(1, total_questoes + 1):
        resposta, proporcoes = detectar_resposta_questao(imagem, numero, layout)
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