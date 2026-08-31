import os
from dotenv import load_dotenv

load_dotenv()

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin")

SECRET_KEY = os.getenv("SECRET_KEY", "chave-hiper-misteriosa-pro-tp1")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60