from shared.db import SessionLocal
from shared.models import Product

session = SessionLocal()
try:
    deleted = session.query(Product).delete()
    session.commit()
    print(f"✅ Удалено товаров: {deleted}")
except Exception as e:
    session.rollback()
    print(f"Ошибка: {e}")
finally:
    session.close()