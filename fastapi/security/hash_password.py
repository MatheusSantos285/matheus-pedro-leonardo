import bcrypt

class HashPassword:
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera o hash da senha em texto plano."""
        # O bcrypt exige que a string seja convertida para bytes antes do hash
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pwd_bytes, salt)

        # Retornamos decodificado como string para o SQLModel salvar no SQLite
        return hashed_password.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Compara a senha em texto plano com o hash armazenado."""
        # Convertendo ambas as strings de volta para bytes para a comparação
        pwd_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')

        return bcrypt.checkpw(pwd_bytes, hash_bytes)