"""
Gera uma folha de resposta sintética para testes.
Execute: python gerar_folha_teste.py
"""
import cv2
import numpy as np
from app.vision.layout_folha import (
    LARGURA, ALTURA, QUESTAO_INICIO_Y,
    QUESTAO_ALTURA, ALTERNATIVAS_X, RAIO_BOLINHA
)

def gerar_folha(respostas_gabarito: dict, caminho_saida: str = "uploads/folha_teste.png"):
    """
    Gera uma folha com as respostas fornecidas já marcadas.
    respostas_gabarito = {"1": "A", "2": "C", ...}
    """
    # Fundo branco
    folha = np.ones((ALTURA, LARGURA), dtype=np.uint8) * 255

    # Cabeçalho
    cv2.putText(folha, "GABARITO READER - FOLHA DE TESTE",
                (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2)
    cv2.putText(folha, "Aluno: Teste",
                (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, 0, 1)

    # Linha separadora
    cv2.line(folha, (30, 120), (LARGURA - 30, 120), 0, 2)

    # Questões
    for numero in range(1, 26):
        y = QUESTAO_INICIO_Y + (numero - 1) * QUESTAO_ALTURA + QUESTAO_ALTURA // 2

        # Número da questão
        cv2.putText(folha, f"{numero:2d}.",
                    (50, y + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0, 1)

        # Bolinhas
        resposta_correta = respostas_gabarito.get(str(numero))
        for letra, x in ALTERNATIVAS_X.items():
            cv2.circle(folha, (x, y), RAIO_BOLINHA, 0, 1)  # Círculo vazio

            if letra == resposta_correta:
                cv2.circle(folha, (x, y), RAIO_BOLINHA - 3, 0, -1)  # Preenchido

            cv2.putText(folha, letra,
                        (x - 4, y + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 0, 1)

    cv2.imwrite(caminho_saida, folha)
    print(f"✅ Folha gerada em: {caminho_saida}")
    return caminho_saida


if __name__ == "__main__":
    # Gabarito de exemplo
    gabarito_teste = {
        "1": "A", "2": "C", "3": "B", "4": "E", "5": "D",
        "6": "A", "7": "B", "8": "C", "9": "D", "10": "E",
        "11": "C", "12": "A", "13": "B", "14": "D", "15": "E",
        "16": "B", "17": "C", "18": "A", "19": "E", "20": "D",
        "21": "A", "22": "B", "23": "C", "24": "D", "25": "E",
    }
    gerar_folha(gabarito_teste)