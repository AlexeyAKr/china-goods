from shared import models  # noqa: F401 — регистрирует модели
from shared.db import Base, engine

print("Создаю таблицы...")
Base.metadata.create_all(bind=engine)
print("✅ Готово. Таблицы:")
for table in Base.metadata.tables:
    print(f"  - {table}")