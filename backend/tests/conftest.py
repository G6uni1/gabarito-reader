import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.database import Base, get_db
from app.models.usuario import Usuario, PerfilUsuario
from app.services.auth_service import hash_senha, criar_token
from datetime import timedelta

# ─── Banco de dados em memória para testes ────────────────────────────────────

SQLALCHEMY_TEST_URL = "sqlite://"   # banco em memória — some após o teste

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine_test
)


@pytest.fixture(autouse=True)
def setup_banco():
    """Cria e destrói o banco para cada teste — isolamento garantido."""
    Base.metadata.create_all(bind=engine_test)
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db():
    """Sessão de banco para os testes."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """
    Cliente HTTP com banco de testes injetado.
    Sobrescreve a dependência get_db do FastAPI.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Fixtures de usuários prontos ─────────────────────────────────────────────

@pytest.fixture
def professor(db) -> Usuario:
    """Cria um professor no banco de testes."""
    usuario = Usuario(
        nome="Prof. Teste",
        email="professor@teste.com",
        senha_hash=hash_senha("senha123"),
        perfil=PerfilUsuario.PROFESSOR,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def aluno(db) -> Usuario:
    """Cria um aluno no banco de testes."""
    usuario = Usuario(
        nome="Aluno Teste",
        email="aluno@teste.com",
        senha_hash=hash_senha("senha123"),
        perfil=PerfilUsuario.ALUNO,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def token_professor(professor) -> str:
    """Gera um token JWT válido para o professor."""
    return criar_token(
        dados={"sub": str(professor.id)},
        expira_em=timedelta(hours=1)
    )


@pytest.fixture
def token_aluno(aluno) -> str:
    """Gera um token JWT válido para o aluno."""
    return criar_token(
        dados={"sub": str(aluno.id)},
        expira_em=timedelta(hours=1)
    )


@pytest.fixture
def headers_professor(token_professor) -> dict:
    return {"Authorization": f"Bearer {token_professor}"}


@pytest.fixture
def headers_aluno(token_aluno) -> dict:
    return {"Authorization": f"Bearer {token_aluno}"}