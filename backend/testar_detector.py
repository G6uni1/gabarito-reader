"""
Testa o detector de respostas com visualização.
Execute: python testar_detector.py uploads/sua_foto.jpg
"""
import cv2
import sys
import numpy as np

from app.vision.preprocessamento import preprocessar_imagem, carregar_imagem, redimensionar
from app.vision.detector_respostas import detectar_todas_respostas, calcular_y_questao
from app.vision.layout_folha import ALTERNATIVAS_X, RAIO_BOLINHA


def visualizar_deteccao(caminho: str):
    # 1. Pré-processa a imagem
    imagem_binaria, status = preprocessar_imagem(caminho)
    if imagem_binaria is None:
        print(f"❌ Erro: {status}")
        return

    # 2. Detecta respostas
    resultado = detectar_todas_respostas(imagem_binaria)

    # 3. Exibe resultado no terminal
    print("\n" + "="*40)
    print("RESPOSTAS DETECTADAS:")
    print("="*40)
    for questao, resposta in resultado["respostas"].items():
        print(f"  Questão {questao:>2}: {resposta}")

    if resultado["questoes_invalidas"]:
        print(f"\n⚠️  Sem resposta: questões {resultado['questoes_invalidas']}")

    print(f"\nTotal detectadas: {resultado['total_detectadas']}")

    # 4. Cria imagem de debug colorida
    debug = cv2.cvtColor(imagem_binaria, cv2.COLOR_GRAY2BGR)

    for numero in range(1, 26):
        centro_y = calcular_y_questao(numero)
        resposta_detectada = resultado["respostas"].get(str(numero))

        for letra, centro_x in ALTERNATIVAS_X.items():
            # Verde se marcada, vermelho se não
            if letra == resposta_detectada:
                cor = (0, 255, 0)    # Verde — marcada
                espessura = 2
            else:
                cor = (0, 0, 255)    # Vermelho — não marcada
                espessura = 1

            cv2.circle(debug, (centro_x, centro_y), RAIO_BOLINHA, cor, espessura)
            cv2.putText(
                debug, letra,
                (centro_x - 5, centro_y + 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.3, cor, 1
            )

    cv2.imshow("Detecção de respostas (verde = marcada)", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python testar_detector.py <caminho_da_imagem>")
    else:
        visualizar_deteccao(sys.argv[1])