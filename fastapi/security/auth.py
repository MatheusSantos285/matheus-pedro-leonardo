from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from security.jwt_handler import decode_access_token
from security.config import ADMIN_USERNAME

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_admin_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependencia que vai blindar os endpoints sensiveis (ex: /predict).
    Uso:
        @router.get("/rota-protegida")
        def rota(admin: str = Depends(get_current_admin_user)):
            ...
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nao foi possivel validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None or username != ADMIN_USERNAME:
            raise credentials_exception
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception