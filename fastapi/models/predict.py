from pydantic import BaseModel, Field, ConfigDict

class PredictRequest(BaseModel):
    # Definimos que o texto de entrada do ticket é obrigatório
    # Aplicamos validação de comprimento (min_length) com base na EDA de tickets reais
    text: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Texto do ticket de atendimento do cliente (10 a 1000 caracteres).",
        examples=["Meu pedido não chegou no prazo, preciso de ajuda.", "O produto que recebi está com defeito e quero trocar."]
    )

    # Rejeita requisições com campos extras maliciosos (como role="admin")
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "text": "Meu pedido não chegou no prazo, preciso de ajuda."
            }
        }
    )

class PredictResponse(BaseModel):
    input_text: str
    predicted_intent: str
    confidence: float = Field(..., ge=0.0, le=1.0) # Garantimos que a confiança esteja entre 0 e 1

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "input_text": "Meu pedido não chegou no prazo, preciso de ajuda.",
                "predicted_intent": "reclamacao_atraso_entrega",
                "confidence": 0.94
            }
        }
    )