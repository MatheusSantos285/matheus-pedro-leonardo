from sqlmodel import create_engine, Session, SQLModel
from config.settings import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Gera a estrutura DDL de tabelas a partir dos modelos SQLModel mapeados."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Injetor de Dependência (Generator) para instanciar e finalizar a Sessão do Banco de Dados."""
    with Session(engine) as session:
        yield session