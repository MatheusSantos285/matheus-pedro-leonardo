from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from database.connection import get_session
from models.db_models import User, PredictionRecord
from models.predict import PredictRequest, PredictResponse
from security.auth import get_current_user

router = APIRouter()

@router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["AI Model Prediction"]
)
async def predict_intent(
        request: PredictRequest,  # Gate 1: Validação Estrita do Pydantic
        current_username: str = Depends(get_current_user),  # Gate 2: Autenticação JWT
        session: Session = Depends(get_session) # Gate 3: Persistência
):
    # 1. Recuperamos o usuário logado para obter o seu ID no banco
    user = session.exec(select(User).where(User.username == current_username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário do token não encontrado no banco.")

    input_text_lower = request.text.lower()

    # Motor de Regras Lógicas Provisório (Mock de IA) alinhado com as categorias do EDA:
    if any(keyword in input_text_lower for keyword in
           ["cancelar", "cancelamento", "excluir", "cancellation", "close my account"]):
        intent = "Cancellation request"
        confidence = 0.98
    elif any(keyword in input_text_lower for keyword in
             ["reembolso", "devolver", "estorno", "dinheiro", "refund", "return"]):
        intent = "Refund request"
        confidence = 0.96
    elif any(keyword in input_text_lower for keyword in
             ["cobrança", "fatura", "paguei", "preço", "boleto", "cartão", "billing", "invoice", "charge"]):
        intent = "Billing inquiry"
        confidence = 0.94
    elif any(keyword in input_text_lower for keyword in
             ["quebrou", "defeito", "bug", "erro", "funcionando", "parou", "broken", "technical", "defect"]):
        intent = "Technical issue"
        confidence = 0.95
    else:
        intent = "Product inquiry"
        confidence = 0.88

    # Regra de Ajuste Operacional baseada na severidade (vinda do Pydantic)
    # Se o ticket for Critical, elevamos a confiança do nosso classificador provisório
    if request.ticket_priority == "Critical" and confidence < 0.95:
        confidence = 0.97

    # 2. Persistência de Dados Segura (Mitigando Mass Assignment)
    # Atribuímos explicitamente cada campo ao modelo do Banco de Dados
    new_prediction = PredictionRecord(
        owner_id=user.id,  # Amarrado ao JWT!
        input_text=request.text,
        customer_age=request.customer_age,
        customer_gender=request.customer_gender,
        ticket_priority=request.ticket_priority,
        ticket_channel=request.ticket_channel,
        product_purchased=request.product_purchased,
        predicted_intent=intent,
        confidence=confidence
    )

    session.add(new_prediction)
    session.commit()

    # Retorna o payload estruturado exatamente como o PredictResponse espera
    return PredictResponse(
        input_text=request.text,
        predicted_intent=intent,
        confidence=confidence
    )