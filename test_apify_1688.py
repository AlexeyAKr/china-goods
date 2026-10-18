import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
if not APIFY_TOKEN:
    raise ValueError("APIFY_TOKEN не найден в .env")

client = ApifyClient(APIFY_TOKEN)

run_input = {
    "maxPages": 1,
    "searchArray": [
        {"keyword": "новогодние гирлянды"}
    ]
}

print("Запускаю парсер 1688 на Apify... Это займет 1-2 минуты.")
run = client.actor("songd/1688-search-scraper").call(run_input=run_input)

print(f"Парсинг завершен! Данные: https://console.apify.com/storage/datasets/{run.default_dataset_id}")

print("\n--- Первые 3 товара из выдачи ---")
count = 0
for item in client.dataset(run.default_dataset_id).iterate_items():
    print(f"\nНазвание: {item.get('title')}")
    print(f"Цена (юани): {item.get('price')}")
    print(f"Ссылка: {item.get('url')}")
    print(f"MOQ: {item.get('minOrderQuantity')}")
    count += 1
    if count >= 3:
        break