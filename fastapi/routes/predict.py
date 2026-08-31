from fastapi import APIRouter, Depends
from models.predict import PredictRequest, PredictResponse

from security.auth import get_current_admin_user

router = APIRouter()

@router.post(
    "/predict",
    response_model=PredictResponse,
    tags=["AI Model Prediction"]
)
async def predict_intent(
        request: PredictRequest,  # Data Binding e validação do Pydantic na entrada
        current_admin: str = Depends(get_current_admin_user)  # Proteção JWT
):
    """
    POST /predict: Recebe o ticket de suporte completo, sanitiza o conteúdo via Pydantic
    e simula a predição da intenção (Ticket Type) com base nas regras extraídas do EDA.
    """
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

    # Retorna o payload estruturado exatamente como o PredictResponse espera
    return PredictResponse(
        input_text=request.text,
        predicted_intent=intent,
        confidence=confidence
    )