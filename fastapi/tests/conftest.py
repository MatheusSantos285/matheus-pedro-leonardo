import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool

from main import app
from database.connection import get_session
from models.db_models import User, PredictionRecord
from security.hash_password import HashPassword
from security.jwt_handler import create_access_token


# ==========================================
# 1. FIXTURE DE BANCO DE DADOS EM MEMÓRIA
# ==========================================
@pytest.fixture(name="session")
def session_fixture():
    """Cria um banco SQLite isolado para a suíte de testes."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Povoa dados essenciais para os testes de Autorização (BOLA)
        user_a = User(username="admin_a", hashed_password=HashPassword.hash_password("senha123"), role="admin")
        user_b = User(username="admin_b", hashed_password=HashPassword.hash_password("senha123"), role="admin")

        session.add_all([user_a, user_b])
        session.commit()

        yield session


# ==========================================
# 2. FIXTURE DO CLIENTE FASTAPI COM OVERRIDE
# ==========================================
@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Sobrescreve a dependência de banco de dados para usar a sessão em memória."""

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ==========================================
# 3. FIXTURES DE TOKENS AUTENTICADOS
# ==========================================
@pytest.fixture(name="token_user_a")
def token_user_a_fixture():
    """Gera um JWT válido para o Usuário A."""
    return create_access_token(data={"sub": "admin_a"})


@pytest.fixture(name="token_user_b")
def token_user_b_fixture():
    """Gera um JWT válido para o Usuário B (útil para testar BOLA)."""
    return create_access_token(data={"sub": "admin_b"})