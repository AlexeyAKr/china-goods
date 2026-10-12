"""Заполняет таблицу products тестовыми товарами."""
from shared.db import SessionLocal
from shared.models import Category, Product
from parser_1688.core.calculator import calculate

PRODUCTS = [
    # (название, slug_категории, цена_cny, вес_кг, наценка_%)
    ("Наушники Bluetooth TWS",              "electronics",        85.0, 0.15, 40),
    ("Пауэрбанк 20000 mAh",                  "electronics",       120.0, 0.45, 35),
    ("Смарт-часы детские",                   "electronics",       150.0, 0.20, 45),
    ("Портативная колонка",                  "electronics",        95.0, 0.35, 40),

    ("Органайзер для кухни",                 "home-kitchen",       45.0, 0.30, 50),
    ("Кухонные весы электронные",            "home-kitchen",       38.0, 0.25, 45),
    ("LED-лента RGB 5м",                     "home-kitchen",       55.0, 0.20, 40),

    ("Гирлянда LED новогодняя",              "gifts-newyear",     100.0, 0.50, 30),
    ("Фигурка Снеговик светящаяся",          "gifts-newyear",      65.0, 0.40, 50),
    ("Ёлочные шары набор 12 шт",             "gifts-newyear",      80.0, 0.60, 45),

    ("Сумка женская кожаная",                "accessories-clothing", 180.0, 0.70, 50),
    ("Ремень мужской",                       "accessories-clothing", 55.0, 0.20, 55),

    ("Робот-игрушка интерактивный",          "toys",              220.0, 0.80, 45),
    ("Конструктор магнитный 100 деталей",    "toys",              140.0, 1.20, 40),
]


def main():
    session = SessionLocal()
    try:
        # slug → id категорий
        cat_map = {c.slug: c.id for c in session.query(Category).all()}
        existing_names = {row[0] for row in session.query(Product.name).all()}

        added = 0
        for name, cat_slug, price_cny, weight_kg, markup in PRODUCTS:
            if name in existing_names:
                print(f"  есть: {name}")
                continue

            cat_id = cat_map.get(cat_slug)
            if not cat_id:
                print(f"  нет категории {cat_slug} для {name}")
                continue

            m = calculate(price_cny=price_cny, weight_kg=weight_kg, markup_percent=markup)

            session.add(Product(
                name=name,
                category_id=cat_id,
                price_cny=price_cny,
                price_rub=m.price_rub,
                weight_kg=weight_kg,
                markup_percent=markup,
            ))
            added += 1
            print(f"  добавлен: {name} ({m.total_cost:.0f} ₽ → {m.retail_price:.0f} ₽)")

        session.commit()
        print(f"\nГотово. Добавлено: {added} из {len(PRODUCTS)}")
    finally:
        session.close()


if __name__ == "__main__":
    main()