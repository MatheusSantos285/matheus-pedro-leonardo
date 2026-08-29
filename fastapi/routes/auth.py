from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

# from security.jwt_handler import create_access_token

router = APIRouter()

@router.post("/auth/token", tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    POST /auth/token: Autentica o administrador 'in-code' e emite o token JWT.
    """
    # Exemplo de validação in-code exigida no TP1:
    if form_data.username != "admin" or form_data.password != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_fake = f"jwt-token-para-usuario-{form_data.username}"

    return {
        "access_token": token_fake,
        "token_type": "bearer"
    }