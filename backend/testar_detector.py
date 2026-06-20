"""
Testa o detector de respostas com visualização.
Execute: python testar_detector.py uploads/sua_foto.jpg
"""
import cv2
import sys

from app.vision.preprocessamento import preprocessar_imagem
from app.vision.detector_respostas import detectar_todas_respostas, calcular_y_questao
from app.vision.layout_folha import ALTERNATIVAS_X, RAIO_BOLINHA, calcular_layout

TOTAL_QUESTOES_TESTE = 25


def visualizar_deteccao(caminho: str):
    imagem_binaria, status = preprocessar_imagem(caminho)
    if imagem_binaria is None:
        print(f"❌ Erro: {status}")
        return

    resultado = detectar_todas_respostas(imagem_binaria, total_questoes=TOTAL_QUESTOES_TESTE)
    layout = calcular_layout(TOTAL_QUESTOES_TESTE)

    print("\n" + "="*40)
    print("RESPOSTAS DETECTADAS:")
    print("="*40)
    for questao, resposta in resultado["respostas"].items():
        print(f"  Questão {questao:>2}: {resposta}")

    if resultado["questoes_invalidas"]:
        print(f"\n⚠️  Sem resposta: questões {resultado['questoes_invalidas']}")

    print(f"\nTotal detectadas: {resultado['total_detectadas']}")

    debug = cv2.cvtColor(imagem_binaria, cv2.COLOR_GRAY2BGR)

    for numero in range(1, TOTAL_QUESTOES_TESTE + 1):
        centro_y = calcular_y_questao(numero, layout)   # ← layout passado corretamente
        resposta_detectada = resultado["respostas"].get(str(numero))

        for letra, centro_x in ALTERNATIVAS_X.items():
            cor = (0, 255, 0) if letra == resposta_detectada else (0, 0, 255)
            espessura = 2 if letra == resposta_detectada else 1
            cv2.circle(debug, (centro_x, centro_y), RAIO_BOLINHA, cor, espessura)
            cv2.putText(debug, letra,
                        (centro_x - 5, centro_y + 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.3, cor, 1)

    cv2.imshow("Detecção de respostas (verde = marcada)", debug)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python testar_detector.py <caminho_da_imagem>")
    else:
        visualizar_deteccao(sys.argv[1])