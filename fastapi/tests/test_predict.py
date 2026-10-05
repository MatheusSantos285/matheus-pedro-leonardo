import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from models.db_models import PredictionRecord, User

# =======================================================
# CENÁRIO 1: HAPPY PATH E VALIDAÇÃO ESTREITA
# =======================================================
def test_predict_sucesso_salva_no_banco(client: TestClient, session: Session, token_user_a: str):
    """Garante que a rota cria a predição e vincula corretamente ao dono do token."""
    payload = {
        "text": "Minha câmera Canon EOS não está ligando, preciso de suporte.",
        "customer_age": 32,
        "customer_gender": "Female",
        "ticket_priority": "High",
        "ticket_channel": "Chat",
        "product_purchased": "Canon EOS"
    }

    response = client.post(
        "/predict",
        json=payload,
        headers={"Authorization": f"Bearer {token_user_a}"}
    )

    # Validações de Resposta
    assert response.status_code == 200
    data = response.json()
    assert data["input_text"] == payload["text"]
    assert "confidence" in data

    # Verifica o banco de dados (Acesso DTO vs DAO)
    # Buscamos no banco para confirmar que a injeção SQLModel funcionou
    db_record = session.exec(select(PredictionRecord).where(PredictionRecord.input_text == payload["text"])).first()
    assert db_record is not None

    # Verifica se a predição foi amarrada ao ID do admin_a
    user_a = session.exec(select(User).where(User.username == "admin_a")).first()
    assert db_record.owner_id == user_a.id


# =======================================================
# CENÁRIO 2: BOPLA - MASS ASSIGNMENT DEFENSE
# =======================================================
def test_predict_rejeita_mass_assignment(client: TestClient, token_user_a: str):
    """
    Testa a vulnerabilidade de Mass Assignment (BOPLA).
    O atacante tenta injetar campos não mapeados (como tentar forçar a 'confidence' ou 'owner_id').
    O Pydantic com extra='forbid' deve barrar e retornar 422.
    """
    payload_malicioso = {
        "text": "Minha câmera não funciona.",
        "customer_age": 25,
        "customer_gender": "Male",
        "ticket_priority": "Low",
        "ticket_channel": "Email",
        "product_purchased": "GoPro Hero",
        "confidence": 0.99,  # TENTATIVA DE INJEÇÃO
        "owner_id": 999  # TENTATIVA DE INJEÇÃO DE BOLA
    }

    response = client.post(
        "/predict",
        json=payload_malicioso,
        headers={"Authorization": f"Bearer {token_user_a}"}
    )

    assert response.status_code == 422
    assert "Extra inputs are not permitted" in response.text  # Pydantic extra="forbid" funcionando


# =======================================================
# CENÁRIO 3: BOPLA - EXCESSIVE DATA EXPOSURE DEFENSE
# =======================================================
def test_predict_evita_exposicao_de_dados_sensiveis(client: TestClient, token_user_a: str):
    """
    Testa Excessive Data Exposure (BOPLA).
    O PredictResponse deve mascarar os IDs internos do banco de dados e retornar
    apenas o necessário.
    """
    payload = {
        "text": "Comprei um Nest Thermostat com problema.",
        "customer_age": 40,
        "customer_gender": "Male",
        "ticket_priority": "Critical",
        "ticket_channel": "Phone",
        "product_purchased": "Nest Thermostat"
    }

    response = client.post(
        "/predict",
        json=payload,
        headers={"Authorization": f"Bearer {token_user_a}"}
    )

    data = response.json()
    # Verifica se os campos internos DO BANCO vazaram para a resposta HTTP
    assert "owner_id" not in data
    assert "id" not in data
    assert "created_at" not in data


# =======================================================
# CENÁRIO 4: AUTENTICAÇÃO E AUSÊNCIA DE BOLA NO POST
# =======================================================
def test_predict_bloqueia_acesso_nao_autenticado(client: TestClient):
    """Bloqueia acesso sem Token JWT."""
    payload = {
        "text": "Reclamação genérica.",
        "customer_age": 30,
        "customer_gender": "Female",
        "ticket_priority": "Low",
        "ticket_channel": "Email",
        "product_purchased": "iPhone"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"