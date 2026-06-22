"""
Testes de integração das rotas de autenticação.
Usam o banco em memória e o cliente HTTP de teste.
"""
import pytest


class TestCadastro:
    def test_cadastro_sucesso(self, client):
        response = client.post("/api/v1/auth/cadastro", json={
            "nome": "Novo Usuário",
            "email": "novo@teste.com",
            "senha": "senha123",
            "perfil": "aluno"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "novo@teste.com"
        assert data["perfil"] == "aluno"
        assert "senha" not in data          # Senha nunca exposta
        assert "senha_hash" not in data     # Hash nunca exposto

    def test_cadastro_email_duplicado(self, client, aluno):
        response = client.post("/api/v1/auth/cadastro", json={
            "nome": "Outro",
            "email": aluno.email,           # Email já existe
            "senha": "senha123",
            "perfil": "aluno"
        })
        assert response.status_code == 400
        assert "já está cadastrado" in response.json()["detail"]

    def test_cadastro_email_invalido(self, client):
        response = client.post("/api/v1/auth/cadastro", json={
            "nome": "Teste",
            "email": "nao-e-um-email",
            "senha": "senha123",
            "perfil": "aluno"
        })
        assert response.status_code == 422  # Validation error


class TestLogin:
    def test_login_sucesso_professor(self, client, professor):
        response = client.post("/api/v1/auth/login", json={
            "email": professor.email,
            "senha": "senha123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["perfil"] == "professor"
        assert data["nome"] == professor.nome

    def test_login_senha_errada(self, client, professor):
        response = client.post("/api/v1/auth/login", json={
            "email": professor.email,
            "senha": "senha_errada"
        })
        assert response.status_code == 401

    def test_login_email_inexistente(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "naoexiste@teste.com",
            "senha": "senha123"
        })
        assert response.status_code == 401


class TestMeuPerfil:
    def test_me_autenticado(self, client, professor, headers_professor):
        response = client.get("/api/v1/auth/me", headers=headers_professor)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == professor.email

    def test_me_sem_token(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Sem credenciais

    def test_me_token_invalido(self, client):
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer token_invalido"}
        )
        assert response.status_code == 401