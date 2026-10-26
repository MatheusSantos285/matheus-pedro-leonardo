from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone

class User(SQLModel, table=True):
    """Modelo da Tabela de Usuários"""
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    role: str = Field(default="user")


class PredictionRecord(SQLModel, table=True):
    """Modelo da Tabela de Predicts"""
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id", index=True)  # Vínculo com o Usuário

    # Campos demográficos e da requisição
    input_text: str
    customer_age: int
    customer_gender: str

    ticket_priority: str
    ticket_channel: str
    product_purchased: str

    # Resultados da IA
    predicted_intent: str
    confidence: float
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())