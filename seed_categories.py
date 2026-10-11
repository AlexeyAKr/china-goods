"""Заполняет таблицу categories базовым списком."""
from shared.db import SessionLocal
from shared.models import Category

CATEGORIES = [
    ("Электроника и гаджеты", "electronics"),
    ("Товары для дома и кухни", "home-kitchen"),
    ("Подарки и новогодний декор", "gifts-newyear"),
    ("Аксессуары и одежда", "accessories-clothing"),
    ("Игрушки", "toys"),
    ("Красота и здоровье", "beauty-health"),
    ("Спорт и отдых", "sport-outdoor"),
    ("Автотовары", "auto"),
]

session = SessionLocal()
try:
    existing = {c.slug for c in session.query(Category).all()}
    added = 0
    for name, slug in CATEGORIES:
        if slug in existing:
            print(f"  уже есть: {name}")
            continue
        session.add(Category(name=name, slug=slug))
        added += 1
        print(f"  добавлена: {name}")
    session.commit()
    print(f"\nГотово. Добавлено: {added} из {len(CATEGORIES)}")
finally:
    session.close()