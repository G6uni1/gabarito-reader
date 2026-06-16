"""
Script de teste do pipeline de visão computacional.
Execute: python testar_visao.py
"""
import cv2
import sys
from app.vision.preprocessamento import (
    carregar_imagem,
    redimensionar,
    para_cinza,
    aplicar_blur,
    detectar_bordas,
    encontrar_contorno_folha,
    corrigir_perspectiva,
    binarizar,
    LARGURA_PADRAO,
    ALTURA_PADRAO,
)


def testar_pipeline(caminho_imagem: str):
    print(f"Testando imagem: {caminho_imagem}")

    # Passo 1
    imagem = carregar_imagem(caminho_imagem)
    if imagem is None:
        print("❌ Erro ao carregar imagem")
        return
    print("✅ Imagem carregada")

    # Passo 2
    imagem = redimensionar(imagem)
    print(f"✅ Redimensionada para {imagem.shape[1]}x{imagem.shape[0]}")

    # Passo 3
    cinza = para_cinza(imagem)
    blur = aplicar_blur(cinza)
    bordas = detectar_bordas(blur)
    print("✅ Bordas detectadas")

    # Passo 4
    contorno = encontrar_contorno_folha(bordas)
    if contorno is not None:
        print("✅ Folha encontrada!")

        # Desenha o contorno na imagem original para visualizar
        imagem_com_contorno = imagem.copy()
        cv2.drawContours(imagem_com_contorno, [contorno], -1, (0, 255, 0), 3)
        cv2.imshow("Contorno detectado", imagem_com_contorno)

        # Corrige perspectiva
        corrigida = corrigir_perspectiva(imagem, contorno)
        cv2.imshow("Perspectiva corrigida", corrigida)

        # Binariza
        cinza_corrigida = para_cinza(corrigida)
        final = binarizar(cinza_corrigida)
    else:
        print("⚠️  Folha não encontrada — usando imagem original")
        final = binarizar(cinza)

    cv2.imshow("Imagem final (binarizada)", final)
    print("✅ Pipeline concluído")
    print("\nPressione qualquer tecla para fechar as janelas...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python testar_visao.py <caminho_da_imagem>")
        print("Exemplo: python testar_visao.py uploads/teste.jpg")
    else:
        testar_pipeline(sys.argv[1])