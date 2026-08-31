import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from models.auth import TokenResponse
from security.jwt_handler import create_access_token

router = APIRouter(tags=["Authentication"])

@router.post("/auth/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    POST /auth/token: Recebe credenciais via formulário OAuth2, valida contra os
    segredos do .env e gera um token JWT criptográfico assinado via PyJWT.
    """
    # Carrega as credenciais administrativas seguras mapeadas no .env
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "admin")

    # Validação restrita das credenciais
    if form_data.username != admin_user or form_data.password != admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas de administrador.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": form_data.username})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )