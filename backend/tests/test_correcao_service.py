"""
Testes unitários do serviço de correção.
Não precisam de banco — testam lógica pura.
"""
import pytest
from app.services.correcao_service import (
    comparar_respostas,
    calcular_nota,
)


class TestCalcularNota:
    def test_nota_maxima(self):
        assert calcular_nota(25, 25) == 10.0

    def test_nota_zero(self):
        assert calcular_nota(0, 25) == 0.0

    def test_nota_proporcional(self):
        assert calcular_nota(20, 25) == 8.0
        assert calcular_nota(10, 25) == 4.0
        assert calcular_nota(5, 25) == 2.0

    def test_nota_arredondada(self):
        # 1/3 de 10 = 3.33... → deve arredondar para 2 casas
        nota = calcular_nota(1, 3)
        assert nota == 3.33

    def test_total_questoes_zero(self):
        # Divisão por zero não deve acontecer
        assert calcular_nota(0, 0) == 0.0


class TestCompararRespostas:
    def setup_method(self):
        """Gabarito base para os testes."""
        self.gabarito = {
            "1": "A", "2": "B", "3": "C", "4": "D", "5": "E"
        }

    def test_todas_corretas(self):
        respostas = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}
        acertos, total, lista_acertos, lista_erros = comparar_respostas(
            respostas, self.gabarito
        )
        assert acertos == 5
        assert total == 5
        assert len(lista_acertos) == 5
        assert len(lista_erros) == 0

    def test_todas_erradas(self):
        respostas = {"1": "B", "2": "C", "3": "D", "4": "E", "5": "A"}
        acertos, total, lista_acertos, lista_erros = comparar_respostas(
            respostas, self.gabarito
        )
        assert acertos == 0
        assert total == 5
        assert len(lista_erros) == 5

    def test_parcialmente_corretas(self):
        respostas = {"1": "A", "2": "B", "3": "X", "4": "X", "5": "X"}
        acertos, _, lista_acertos, lista_erros = comparar_respostas(
            respostas, self.gabarito
        )
        assert acertos == 2
        assert "1" in lista_acertos
        assert "2" in lista_acertos
        assert "3" in lista_erros

    def test_questao_sem_resposta_conta_como_erro(self):
        respostas = {"1": "A"}  # Só respondeu 1 de 5
        acertos, total, _, lista_erros = comparar_respostas(
            respostas, self.gabarito
        )
        assert acertos == 1
        assert total == 5
        assert len(lista_erros) == 4

    def test_case_insensitive(self):
        """Letra minúscula deve ser aceita como correta."""
        respostas = {"1": "a", "2": "b", "3": "c", "4": "d", "5": "e"}
        acertos, _, _, _ = comparar_respostas(respostas, self.gabarito)
        assert acertos == 5