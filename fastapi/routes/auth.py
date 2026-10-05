from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session
from config.rate_limiter import limiter
from database.connection import get_session
from models.auth import TokenResponse
from models.db_models import User
from security.hash_password import HashPassword
from security.jwt_handler import create_access_token
from fastapi import Request

router = APIRouter(tags=["Authentication"])

@router.post("/auth/token", response_model=TokenResponse)
@limiter.limit("10/minute")  # Limite de taxa para mitigar ataques de força bruta
async def login(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_session)): # 1. Injetamos a sessão do banco
    """
    POST /auth/token: Recebe credenciais via formulário OAuth2, valida contra o
    banco de dados (comparando o hash bcrypt) e gera um token JWT.
    """
    # 2. Buscamos o usuário no banco (mitigando SQLi via ORM)
    user = session.exec(select(User).where(User.username == form_data.username)).first()

    # 3. Verificamos se o usuário existe E se a senha confere com o Hash
    if not user or not HashPassword.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",  # Mensagem genérica deliberada
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Geramos o token com as claims (adicionando a role se quiser usar para RBAC depois)
    access_token = create_access_token(data={"sub": user.username, "role": user.role})

    return TokenResponse(
        access_token=access_token,
        token_type="bearer"
    )