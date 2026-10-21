import json
from shared.db import SessionLocal
from shared.models import Product

session = SessionLocal()
try:
    p = session.query(Product).first()
    if p:
        print(f"Товар: {p.name}")
        print("Что лежит в attributes:")
        print(json.dumps(p.attributes, ensure_ascii=False, indent=2))
    else:
        print("В базе нет товаров")
finally:
    session.close()