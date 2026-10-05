from sqlmodel import Session, select
from database.connection import engine, create_db_and_tables
from models.db_models import User, PredictionRecord
from security.config import ADMIN_PASSWORD
from security.hash_password import HashPassword

def seed_database():
    create_db_and_tables()  # Garante que as tabelas existam antes de inserir dados

    with Session(engine) as session:
        # Verifica se já existe dados para evitar duplicação no re-run
        if not session.exec(select(User)).first():
            print("Populando o banco de dados...")

            # 1. Criando os usuários
            user_admin = User(username="admin", hashed_password=HashPassword.hash_password(ADMIN_PASSWORD), role="admin")
            user_analyst = User(username="analyst_01", hashed_password=HashPassword.hash_password("hashed_senha_segura"), role="user")

            session.add_all([user_admin, user_analyst])
            session.commit()  # Commit para gerar os IDs
            session.refresh(user_admin)
            session.refresh(user_analyst)

            # 2. Criando predições associadas
            pred_1 = PredictionRecord(
                owner_id=user_admin.id,
                input_text="Minha fatura veio duplicada.",
                customer_age=30,
                customer_gender="Female",
                predicted_intent="Billing inquiry",
                confidence=0.96
            )

            pred_2 = PredictionRecord(
                owner_id=user_analyst.id,
                input_text="O produto quebrou no primeiro dia.",
                customer_age=45,
                customer_gender="Male",
                predicted_intent="Technical issue",
                confidence=0.98
            )

            session.add_all([pred_1, pred_2])
            session.commit()
            print("Usuários e predições inseridos com sucesso!")

        print("Banco de dados já populado.")
        return


if __name__ == "__main__":
    seed_database()