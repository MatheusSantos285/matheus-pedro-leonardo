from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config.rate_limiter import limiter
from routes.health import router as health_router
from routes.auth import router as auth_router
from routes.predict import router as predict_router
from security.middlewares import SecurityHeadersMiddleware
from sqlite_database import seed_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Iniciando a API: Verificando Banco de Dados...")
    seed_database()
    yield
    print("Desligando a API de forma segura...")

# Inicialização da aplicação
app = FastAPI(
    title="Customer Support AI - Secure API",
    description="API com infraestrutura de segurança: Validação Pydantic, JWT e SQLite (SQLModel).",
    version="2.0.0",
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. CORS com Allowlist Explícita
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://seu-front-end-confiavel.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 2. Injeção dos Cabeçalhos de Segurança
app.add_middleware(SecurityHeadersMiddleware)

# Registro das Rotas Modulares
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)

@app.get("/")
async def root():
    return {
        "message": "API de Atendimento ao Cliente ativa!",
        "docs": "Acesse http://127.0.0.1:8000/docs para testar os endpoints."
    }