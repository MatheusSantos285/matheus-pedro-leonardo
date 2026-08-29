from fastapi import APIRouter, Depends
from models.predict import PredictRequest, PredictResponse

# Ao desenvolver o sistema JWT com o Integrante 2, descomente a linha abaixo
# from security.dependencies import get_current_user

router = APIRouter()


@router.post(
    "/predict",
    response_model=PredictResponse,  # 🛡️ Garante que a resposta saia formatada pelo modelo
    tags=["AI Model Prediction"]
)
async def predict_intent(
        request: PredictRequest,  # 🛡️ Data Binding e validação do Pydantic na entrada
        # current_user: str = Depends(get_current_user)  # 🔑 Proteção JWT (Integrante 2)
):
    """
    POST /predict: Recebe o ticket de suporte, sanitiza o conteúdo via Pydantic e simula o modelo de IA.
    """
    # Lógica lógica simples (mock) solicitada no TP1
    input_text_lower = request.text.lower()

    if "cancelar" in input_text_lower or "cancelamento" in input_text_lower:
        intent = "cancelamento_servico"
    elif "atraso" in input_text_lower or "chegou" in input_text_lower or "entrega" in input_text_lower:
        intent = "reclamacao_logistica"
    else:
        intent = "duvida_geral"

    # Retorna o payload estruturado exatamente como o PredictResponse espera
    return PredictResponse(
        input_text=request.text,
        predicted_intent=intent,
        confidence=0.91
    )