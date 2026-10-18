import os
import re

from dotenv import load_dotenv
from apify_client import ApifyClient

from shared.db import SessionLocal
from shared.models import Product, Category
from parser_1688.core.calculator import calculate

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN не найден в .env")

DATASET_ID = "aC9lVeIfBDe4RZ2QU"  # замени на ID из последнего запуска

client = ApifyClient(APIFY_TOKEN)

print("Загружаю данные из Apify...")
items = list(client.dataset(DATASET_ID).iterate_items())
print(f"Найдено товаров: {len(items)}")

session = SessionLocal()
saved_count = 0
skipped_count = 0

try:
    category = session.query(Category).filter(Category.slug == "home-kitchen").first()

    for item in items:
        title = item.get("title", "").strip()
        price_str = item.get("price")
        url = item.get("url", "")

        if not title or not price_str:
            skipped_count += 1
            continue

        sku_match = re.search(r"offer/(\d+)\.html", url)
        sku = sku_match.group(1) if sku_match else None

        existing = session.query(Product).filter(Product.sku_1688 == sku).first()
        if existing:
            skipped_count += 1
            continue

        try:
            price_cny = float(price_str)
        except ValueError:
            skipped_count += 1
            continue

        m = calculate(price_cny=price_cny, weight_kg=0.5, markup_percent=30)

        product = Product(
            name=title,
            category_id=category.id if category else None,
            price_cny=price_cny,
            price_rub=m.price_rub,
            weight_kg=0.5,
            markup_percent=30,
            source_url=url,
            sku_1688=sku,
            attributes={"raw_title": title}
        )
        session.add(product)
        saved_count += 1

    session.commit()
    print(f"✅ Сохранено: {saved_count}")
    print(f"⏭ Пропущено: {skipped_count}")

except Exception as e:
    session.rollback()
    print(f"❌ Ошибка: {e}")
finally:
    session.close()