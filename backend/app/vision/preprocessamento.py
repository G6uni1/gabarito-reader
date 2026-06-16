import cv2
import numpy as np
from typing import Optional, Tuple


# Tamanho padrão da imagem após normalização
LARGURA_PADRAO = 800
ALTURA_PADRAO = 1100


def carregar_imagem(caminho: str) -> Optional[np.ndarray]:
    """
    Carrega uma imagem do disco.
    Retorna None se o arquivo não existir ou não for imagem válida.
    """
    imagem = cv2.imread(caminho)
    if imagem is None:
        return None
    return imagem


def redimensionar(imagem: np.ndarray, largura: int = LARGURA_PADRAO) -> np.ndarray:
    """
    Redimensiona mantendo a proporção original.
    Padroniza o tamanho para acelerar o processamento.
    """
    altura_original, largura_original = imagem.shape[:2]
    proporcao = largura / largura_original
    nova_altura = int(altura_original * proporcao)
    return cv2.resize(imagem, (largura, nova_altura))


def para_cinza(imagem: np.ndarray) -> np.ndarray:
    """Converte imagem colorida para escala de cinza."""
    return cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)


def aplicar_blur(imagem_cinza: np.ndarray) -> np.ndarray:
    """
    Aplica desfoque gaussiano para reduzir ruído.
    O kernel (5, 5) define o tamanho da área de suavização.
    Valores maiores = mais suavização.
    """
    return cv2.GaussianBlur(imagem_cinza, (5, 5), 0)


def detectar_bordas(imagem_blur: np.ndarray) -> np.ndarray:
    """
    Algoritmo Canny — detecta bordas na imagem.
    threshold1=75: bordas fracas abaixo disso são ignoradas
    threshold2=200: bordas fortes acima disso são sempre incluídas
    """
    return cv2.Canny(imagem_blur, threshold1=75, threshold2=200)


def encontrar_contorno_folha(bordas: np.ndarray) -> Optional[np.ndarray]:
    """
    Encontra o maior contorno retangular — provavelmente a folha.
    Retorna os 4 cantos do retângulo ou None se não encontrar.
    """
    # Encontra todos os contornos na imagem de bordas
    contornos, _ = cv2.findContours(
        bordas,
        cv2.RETR_EXTERNAL,      # Apenas contornos externos
        cv2.CHAIN_APPROX_SIMPLE # Comprime segmentos em pontos finais
    )

    if not contornos:
        return None

    # Ordena por área (maior primeiro) — a folha é o maior objeto
    contornos = sorted(contornos, key=cv2.contourArea, reverse=True)

    for contorno in contornos[:5]:  # Verifica os 5 maiores
        # Aproxima o contorno a um polígono
        perimetro = cv2.arcLength(contorno, True)
        aproximacao = cv2.approxPolyDP(contorno, 0.02 * perimetro, True)

        # Se tem 4 lados, é provavelmente nossa folha
        if len(aproximacao) == 4:
            return aproximacao

    return None


def ordenar_pontos(pontos: np.ndarray) -> np.ndarray:
    """
    Ordena os 4 cantos na ordem: top-left, top-right, bottom-right, bottom-left.
    Necessário para a correção de perspectiva funcionar corretamente.
    """
    pontos = pontos.reshape(4, 2).astype(np.float32)
    resultado = np.zeros((4, 2), dtype=np.float32)

    soma = pontos.sum(axis=1)
    resultado[0] = pontos[np.argmin(soma)]   # Top-left: menor soma (x+y)
    resultado[2] = pontos[np.argmax(soma)]   # Bottom-right: maior soma (x+y)

    diferenca = np.diff(pontos, axis=1)
    resultado[1] = pontos[np.argmin(diferenca)]  # Top-right: menor diferença (y-x)
    resultado[3] = pontos[np.argmax(diferenca)]  # Bottom-left: maior diferença (y-x)

    return resultado


def corrigir_perspectiva(
    imagem: np.ndarray,
    pontos: np.ndarray,
    largura: int = LARGURA_PADRAO,
    altura: int = ALTURA_PADRAO
) -> np.ndarray:
    """
    Aplica transformação de perspectiva.
    Transforma o trapézio da foto em um retângulo perfeito.
    """
    pontos_ordenados = ordenar_pontos(pontos)

    # Destino: retângulo perfeito com o tamanho padrão
    destino = np.array([
        [0, 0],
        [largura - 1, 0],
        [largura - 1, altura - 1],
        [0, altura - 1]
    ], dtype=np.float32)

    # Calcula a matriz de transformação
    matriz = cv2.getPerspectiveTransform(pontos_ordenados, destino)

    # Aplica a transformação
    return cv2.warpPerspective(imagem, matriz, (largura, altura))


def binarizar(imagem_cinza: np.ndarray) -> np.ndarray:
    """
    Converte para preto e branco usando threshold adaptativo.
    Melhor que threshold fixo para variações de iluminação.
    """
    return cv2.adaptiveThreshold(
        imagem_cinza,
        255,                              # Valor máximo (branco)
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,   # Usa média ponderada gaussiana
        cv2.THRESH_BINARY_INV,            # Inverte: marcações ficam brancas
        blockSize=11,                     # Tamanho da área de análise
        C=2                               # Constante subtraída da média
    )


def preprocessar_imagem(caminho: str) -> Tuple[Optional[np.ndarray], str]:
    """
    Pipeline completo de pré-processamento.
    Retorna (imagem_processada, mensagem_status).
    """
    # 1. Carregar
    imagem = carregar_imagem(caminho)
    if imagem is None:
        return None, "Erro: não foi possível carregar a imagem"

    # 2. Redimensionar
    imagem = redimensionar(imagem)

    # 3. Pipeline de detecção
    cinza = para_cinza(imagem)
    blur = aplicar_blur(cinza)
    bordas = detectar_bordas(blur)

    # 4. Encontrar a folha
    contorno = encontrar_contorno_folha(bordas)

    if contorno is not None:
        # 5a. Corrigir perspectiva se encontrou a folha
        imagem_corrigida = corrigir_perspectiva(imagem, contorno)
        cinza_corrigida = para_cinza(imagem_corrigida)
    else:
        # 5b. Se não encontrou, usa a imagem como está (fallback)
        cinza_corrigida = cinza

    # 6. Binarizar
    imagem_final = binarizar(cinza_corrigida)

    return imagem_final, "ok"