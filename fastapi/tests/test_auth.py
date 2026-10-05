import jwt
from fastapi.testclient import TestClient

# Importações apenas do necessário para validar o token gerado
from security.config import SECRET_KEY, ALGORITHM

# ====================================================================
# CENÁRIOS DE TESTE DE AUTENTICAÇÃO (APPSEC)
# Nota: A fixture 'client' é injetada automaticamente pelo conftest.py
# ====================================================================

def test_login_sucesso_gera_token_valido(client: TestClient):
    """Cenário 1: Happy Path. O usuário fornece credenciais corretas populadas no conftest."""
    response = client.post(
        "/auth/token",
        data={"username": "admin_a", "password": "senha123"}
    )

    # 1. Verifica se a requisição teve sucesso
    assert response.status_code == 200
    data = response.json()

    # 2. Verifica a estrutura do token
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # 3. Valida criptograficamente se o token foi assinado corretamente
    # e se a claim 'sub' contém o username esperado
    token = data["access_token"]
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "admin_a"


def test_login_senha_incorreta_retorna_401(client: TestClient):
    """
    Cenário 2: Broken Authentication.
    Senha errada deve ser bloqueada.
    """
    response = client.post(
        "/auth/token",
        data={"username": "admin_a", "password": "SenhaErrada!123"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas."


def test_login_usuario_inexistente_previne_enumeracao(client: TestClient):
    """
    Cenário 3: User Enumeration Defense.
    Se o usuário não existir, a mensagem de erro DEVE SER EXATAMENTE A MESMA
    do teste de senha incorreta.
    """
    response = client.post(
        "/auth/token",
        data={"username": "hacker_desconhecido", "password": "senha123"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas."


def test_login_campos_ausentes_retorna_422(client: TestClient):
    """
    Cenário 4: Validação de Entrada.
    Tentar fazer login sem enviar a senha (OAuth2 spec validation).
    """
    response = client.post(
        "/auth/token",
        data={"username": "admin_a"}  # Faltando o campo password
    )

    # O FastAPI (via OAuth2PasswordRequestForm) barra requisições malformadas na borda
    assert response.status_code == 422