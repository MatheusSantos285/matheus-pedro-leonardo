from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class TokenResponse(BaseModel):
    """Contrato de resposta para a geração de tokens JWT bem-sucedida."""
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc...",
                "token_type": "bearer"
            }
        }
    )

class TokenData(BaseModel):
    """
    Contrato interno para validar as claims extraídas do payload de um JWT decodificado.
    Crucial para garantir que o 'sub' (subject) exista e esteja em formato válido.
    """
    username: Optional[str] = Field(default=None, alias="sub")

    # Impedimos a injeção de claims extras não mapeadas para mitigar Mass Assignment no Token
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True, # Permite passar tanto 'sub' quanto 'username' na inicialização
        json_schema_extra={
            "example": {
                "sub": "admin"
            }
        }
    )