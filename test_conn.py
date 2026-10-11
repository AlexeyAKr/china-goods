import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={
        "sslmode": "require",
        "prepare_threshold": None,  # Отключаем prepared statements для pooler
    },
)

try:
    with engine.connect() as conn:
        print("OK:", conn.execute(text("SELECT version()")).scalar())
except Exception as e:
    print("Ошибка:", type(e).__name__)
    print(e)