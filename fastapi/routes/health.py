from fastapi import APIRouter

router = APIRouter()

@router.get("/health", tags=["System Health"])
async def get_health():
    """
    GET /health: Verifica se a API está ativa e operando normalmente.
    """
    return {"status": "healthy", "service": "Customer Support AI API"}