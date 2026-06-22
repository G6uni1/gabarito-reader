from app.vision.layout_folha import calcular_layout, ALTURA, CABECALHO_ALTURA, RODAPE_ALTURA


class TestCalcularLayout:
    def test_layout_25_questoes(self):
        layout = calcular_layout(25)
        assert layout["total_questoes"] == 25
        assert layout["questao_inicio_y"] == CABECALHO_ALTURA
        assert layout["questao_altura"] > 0

    def test_layout_5_questoes(self):
        layout = calcular_layout(5)
        # Com menos questões, cada uma ocupa mais espaço
        layout_25 = calcular_layout(25)
        assert layout["questao_altura"] >= layout_25["questao_altura"]

    def test_layout_nao_ultrapassa_altura(self):
        """As questões não devem ultrapassar a altura total da folha."""
        for total in [5, 10, 25, 40]:
            layout = calcular_layout(total)
            altura_total_questoes = layout["questao_altura"] * total
            area_disponivel = ALTURA - CABECALHO_ALTURA - RODAPE_ALTURA
            assert altura_total_questoes <= area_disponivel + layout["questao_altura"]

    def test_altura_minima_garantida(self):
        """Bolinhas não devem se sobrepor mesmo com muitas questões."""
        layout = calcular_layout(50)
        assert layout["questao_altura"] >= 32  # RAIO_BOLINHA * 2 + 4