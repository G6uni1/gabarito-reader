import pytest


GABARITO_5 = {"1": "A", "2": "B", "3": "C", "4": "D", "5": "E"}


class TestCriarProva:
    def test_professor_cria_prova(self, client, headers_professor):
        response = client.post("/api/v1/provas", json={
            "titulo": "Prova de Matemática",
            "total_questoes": 5,
            "gabarito": GABARITO_5
        }, headers=headers_professor)
        assert response.status_code == 201
        data = response.json()
        assert data["titulo"] == "Prova de Matemática"
        assert data["total_questoes"] == 5

    def test_aluno_nao_pode_criar_prova(self, client, headers_aluno):
        response = client.post("/api/v1/provas", json={
            "titulo": "Tentativa",
            "total_questoes": 5,
            "gabarito": GABARITO_5
        }, headers=headers_aluno)
        assert response.status_code == 403

    def test_gabarito_incompleto_rejeitado(self, client, headers_professor):
        response = client.post("/api/v1/provas", json={
            "titulo": "Prova",
            "total_questoes": 5,
            "gabarito": {"1": "A"}  # Só 1 de 5
        }, headers=headers_professor)
        assert response.status_code == 400

    def test_resposta_invalida_rejeitada(self, client, headers_professor):
        response = client.post("/api/v1/provas", json={
            "titulo": "Prova",
            "total_questoes": 1,
            "gabarito": {"1": "Z"}  # Z não é válido
        }, headers=headers_professor)
        assert response.status_code == 422


class TestListarProvas:
    def test_usuario_autenticado_lista_provas(self, client, headers_aluno, headers_professor):
        # Cria uma prova
        client.post("/api/v1/provas", json={
            "titulo": "Prova Teste",
            "total_questoes": 5,
            "gabarito": GABARITO_5
        }, headers=headers_professor)

        # Aluno consegue listar
        response = client.get("/api/v1/provas", headers=headers_aluno)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_sem_autenticacao_nao_lista(self, client):
        response = client.get("/api/v1/provas")
        assert response.status_code == 403