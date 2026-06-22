import json
import pytest
from app.models.prova import Prova
from app.models.gabarito import Gabarito
from app.services.correcao_service import gerar_resultado


GABARITO_OFICIAL = {
    "1": "A", "2": "B", "3": "C", "4": "D", "5": "E"
}


@pytest.fixture
def prova_com_gabarito(db, professor):
    """Cria uma prova com gabarito no banco de testes."""
    prova = Prova(
        titulo="Prova Fixture",
        total_questoes=5,
        professor_id=professor.id,
    )
    db.add(prova)
    db.commit()
    db.refresh(prova)

    for numero, resposta in GABARITO_OFICIAL.items():
        db.add(Gabarito(
            prova_id=prova.id,
            questao_numero=int(numero),
            resposta_correta=resposta,
        ))
    db.commit()
    return prova


class TestGerарResultado:
    def test_gabarito_perfeito(self, db, aluno, prova_com_gabarito):
        resultado = gerar_resultado(
            db=db,
            aluno_id=aluno.id,
            prova_id=prova_com_gabarito.id,
            respostas_aluno=GABARITO_OFICIAL
        )
        assert resultado.nota == 10.0
        assert resultado.total_acertos == 5
        assert resultado.editado_professor is False

    def test_gabarito_zerado(self, db, aluno, prova_com_gabarito):
        respostas_erradas = {"1": "E", "2": "A", "3": "B", "4": "C", "5": "D"}
        resultado = gerar_resultado(
            db=db,
            aluno_id=aluno.id,
            prova_id=prova_com_gabarito.id,
            respostas_aluno=respostas_erradas
        )
        assert resultado.nota == 0.0
        assert resultado.total_acertos == 0

    def test_respostas_salvas_corretamente(self, db, aluno, prova_com_gabarito):
        resultado = gerar_resultado(
            db=db,
            aluno_id=aluno.id,
            prova_id=prova_com_gabarito.id,
            respostas_aluno=GABARITO_OFICIAL
        )
        respostas_salvas = json.loads(resultado.respostas_json)
        assert respostas_salvas == GABARITO_OFICIAL


class TestResultadosAPI:
    def test_aluno_ve_proprios_resultados(
        self, client, db, aluno, professor,
        headers_aluno, headers_professor, prova_com_gabarito
    ):
        # Professor cria resultado para o aluno
        gerar_resultado(
            db=db,
            aluno_id=aluno.id,
            prova_id=prova_com_gabarito.id,
            respostas_aluno=GABARITO_OFICIAL
        )

        response = client.get("/api/v1/resultados", headers=headers_aluno)
        assert response.status_code == 200
        resultados = response.json()
        assert len(resultados) == 1
        assert resultados[0]["aluno_id"] == aluno.id

    def test_professor_edita_nota(
        self, client, db, aluno, professor,
        headers_professor, prova_com_gabarito
    ):
        resultado = gerar_resultado(
            db=db,
            aluno_id=aluno.id,
            prova_id=prova_com_gabarito.id,
            respostas_aluno={"1": "E"}  # Tudo errado
        )
        assert resultado.nota == 0.0

        response = client.put(
            f"/api/v1/resultados/{resultado.id}",
            json={"nova_nota": 5.0},
            headers=headers_professor
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nota"] == 5.0
        assert data["editado_professor"] is True