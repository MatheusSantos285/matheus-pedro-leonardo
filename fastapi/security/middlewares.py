from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Injeta cabeçalhos HTTP de segurança em todas as respostas (Defense in Depth).
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Força o uso de HTTPS
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Previne ataques de Clickjacking impedindo renderização em iframes
        response.headers["X-Frame-Options"] = "DENY"
        # Impede que o navegador faça MIME-sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        # Restringe a origem de scripts e recursos (CSP básico)
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response