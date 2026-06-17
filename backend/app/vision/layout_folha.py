"""
Define as coordenadas fixas do layout da folha de resposta.
Altere aqui se mudar o design da folha.
"""

# Tamanho padrão da imagem processada
LARGURA = 800
ALTURA = 1100

# ─── Área do cabeçalho ───────────────────────────────────────────────────────
CABECALHO_ALTURA = 180      # Primeiros 180px são cabeçalho (nome, QR Code)

# ─── Grade de questões ───────────────────────────────────────────────────────
QUESTAO_INICIO_Y = 200      # Y onde começa a primeira questão
QUESTAO_ALTURA = 36         # Altura de cada linha de questão
QUESTAO_MARGEM = 2          # Margem interna da célula

# ─── Posições X das alternativas ────────────────────────────────────────────
# Cada alternativa é uma coluna com centro em X:
ALTERNATIVAS_X = {
    "A": 200,
    "B": 280,
    "C": 360,
    "D": 440,
    "E": 520,
}

# Raio do círculo de cada alternativa (em pixels)
RAIO_BOLINHA = 14

# Limiar: percentual mínimo de pixels brancos para considerar marcado
# 0.15 = se 15% dos pixels dentro do círculo forem brancos, está marcado
THRESHOLD_MARCACAO = 0.15

# Número de questões (vem do config, mas definimos o padrão aqui também)
TOTAL_QUESTOES = 25