"""
Gera uma folha de resposta sintética para testes.
Execute: python gerar_folha_teste.py
"""
import cv2
import numpy as np
from app.vision.layout_folha import (
    LARGURA, ALTURA, ALTERNATIVAS_X, RAIO_BOLINHA, calcular_layout
)


def gerar_folha(respostas_gabarito: dict, caminho_saida: str = "uploads/folha_teste.png"):
    total_questoes = len(respostas_gabarito)
    layout = calcular_layout(total_questoes)
    questao_inicio_y = layout["questao_inicio_y"]
    questao_altura = layout["questao_altura"]

    folha = np.ones((ALTURA, LARGURA), dtype=np.uint8) * 255

    cv2.putText(folha, "GABARITO READER - FOLHA DE TESTE",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2)
    cv2.putText(folha, "Aluno: Teste",
                (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)
    cv2.line(folha, (30, 120), (LARGURA - 30, 120), 0, 2)

    for numero in range(1, total_questoes + 1):
        y = questao_inicio_y + (numero - 1) * questao_altura + questao_altura // 2

        cv2.putText(folha, f"{numero:2d}.",
                    (50, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)

        resposta_correta = respostas_gabarito.get(str(numero))
        for letra, x in ALTERNATIVAS_X.items():
            cv2.circle(folha, (x, y), RAIO_BOLINHA, 0, 1)
            if letra == resposta_correta:
                cv2.circle(folha, (x, y), RAIO_BOLINHA - 3, 0, -1)
            cv2.putText(folha, letra,
                        (x - 4, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)

    cv2.imwrite(caminho_saida, folha)
    print(f"✅ Folha gerada em: {caminho_saida}")
    return caminho_saida


if __name__ == "__main__":
    gabarito_teste = {
        "1": "A", "2": "C", "3": "B", "4": "E", "5": "D",
        "6": "A", "7": "B", "8": "C", "9": "D", "10": "E",
        "11": "C", "12": "A", "13": "B", "14": "D", "15": "E",
        "16": "B", "17": "C", "18": "A", "19": "E", "20": "D",
        "21": "A", "22": "B", "23": "C", "24": "D", "25": "E",
    }
    gerar_folha(gabarito_teste)