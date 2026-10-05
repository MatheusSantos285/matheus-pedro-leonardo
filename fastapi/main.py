from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select

# 1. Configurações e Conexão
from database.connection import engine, create_db_and_tables
from security.hash_password import HashPassword
from models.db_models import User, PredictionRecord

# 2. Importação das Rotas
from routes.health import router as health_router
from routes.auth import router as auth_router
from routes.predict import router as predict_router
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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