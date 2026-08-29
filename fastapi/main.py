from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importação dos roteadores de cada rota (definidos na pasta /routes)
from routes.health import router as health_router
from routes.auth import router as auth_router
from routes.predict import router as predict_router

# Inicialização da aplicação com metadados para o Swagger UI
app = FastAPI(
    title="Customer Support AI - Secure API",
    description=(
        "API base para o TP1 de Análise e Segurança de Agentes de IA. "
        "Contém infraestrutura de segurança com validação estrita (Pydantic), "
        "criptografia stateless (JWT) e controle de acesso baseado em administrador in-code."
    ),
    version="1.0.0"
)

# Configuração de CORS (Cross-Origin Resource Sharing)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro das rotas modulares na aplicação principal
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(predict_router)

@app.get("/")
async def root():
    """
    Rota raiz para conveniência e redirecionamento amigável para a documentação.
    """
    return {
        "message": "API de Atendimento ao Cliente ativa!",
        "docs": "Acesse http://127.0.0.1:8000/docs para interagir com os endpoints."
    }
