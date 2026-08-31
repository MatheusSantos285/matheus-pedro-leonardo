from datetime import datetime, timedelta, timezone
import jwt

from security.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Gerador de JWT com as claims dadas. ('sub' + 'exp')
    Assinado com HS256
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    """
    Decodifica e valida o token (assinatura + expiracao).
    Lanca jwt.ExpiredSignatureError ou jwt.InvalidTokenError se invalido.
    """
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])