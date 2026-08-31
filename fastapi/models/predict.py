from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

# 1. ENUMS ESTREITOS BASEADOS NAS CATEGORIAS REAIS DO EDA
class CustomerGenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class TicketPriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class TicketChannelEnum(str, Enum):
    EMAIL = "Email"
    CHAT = "Chat"
    PHONE = "Phone"
    SOCIAL_MEDIA = "Social media"

class ProductPurchasedEnum(str, Enum):
    # Simplificado com alguns dos produtos reais mapeados na  univariada
    CANON_EOS = "Canon EOS"
    GOPRO_HERO = "GoPro Hero"
    NEST_THERMOSTAT = "Nest Thermostat"
    AMAZON_ECHO = "Amazon Echo"
    IPHONE = "iPhone"
    # O Pydantic rejeitará qualquer produto fora desta lista restrita!

class PredictRequest(BaseModel):
    # Definimos que o texto de entrada do ticket é obrigatório
    # Aplicamos validação de comprimento (min_length) com base na EDA de tickets reais
    text: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        description="Texto descritivo da queixa do suporte do cliente."
    )

    # Campo demográfico validado com as barreiras lógicas do EDA (18 a 70 anos)
    customer_age: int = Field(
        ...,
        ge=18,
        le=70,
        description="Idade do cliente (conforme limites reais validados no EDA)."
    )

    # Variáveis categóricas restritas pelos Enums para impedir Fuzzing
    customer_gender: CustomerGenderEnum
    ticket_priority: TicketPriorityEnum
    ticket_channel: TicketChannelEnum
    product_purchased: ProductPurchasedEnum

    # Bloqueio estrito de parâmetros invisíveis/não mapeados (Mass Assignment)
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "text": "Minha câmera Canon EOS não está ligando, preciso de ajuda com o suporte técnico.",
                "customer_age": 32,
                "customer_gender": "Female",
                "ticket_priority": "High",
                "ticket_channel": "Chat",
                "product_purchased": "Canon EOS"
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