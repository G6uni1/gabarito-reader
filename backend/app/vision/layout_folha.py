"""
Layout dinâmico da folha de resposta.
As coordenadas são calculadas automaticamente com base
no número de questões — sem necessidade de calibração manual.
"""

# ─── Tamanho padrão da imagem processada ─────────────────────────────────────
LARGURA = 800
ALTURA = 1100

# ─── Cabeçalho ───────────────────────────────────────────────────────────────
CABECALHO_ALTURA = 200      # Espaço reservado para título, nome, QR Code

# ─── Rodapé ──────────────────────────────────────────────────────────────────
RODAPE_ALTURA = 60

# ─── Posições X das alternativas (fixas, independente do nº de questões) ─────
ALTERNATIVAS_X = {
    "A": 200,
    "B": 280,
    "C": 360,
    "D": 440,
    "E": 520,
}

# ─── Raio das bolinhas ────────────────────────────────────────────────────────
RAIO_BOLINHA = 14

# ─── Threshold de marcação ───────────────────────────────────────────────────
THRESHOLD_MARCACAO = 0.15

# ─── Total padrão (usado como fallback) ──────────────────────────────────────
TOTAL_QUESTOES = 25


def calcular_layout(total_questoes: int) -> dict:
    """
    Calcula dinamicamente o layout da grade de questões.

    A área disponível para questões é dividida igualmente
    entre todas as questões, independente de quantas forem.

    Retorna um dicionário com os parâmetros calculados.
    """
    area_disponivel = ALTURA - CABECALHO_ALTURA - RODAPE_ALTURA
    altura_por_questao = area_disponivel // total_questoes

    # Garante um mínimo razoável para não sobrepor as bolinhas
    altura_por_questao = max(altura_por_questao, RAIO_BOLINHA * 2 + 4)

    return {
        "questao_inicio_y": CABECALHO_ALTURA,
        "questao_altura": altura_por_questao,
        "total_questoes": total_questoes,
    }