"""Клиент для работы с Apify (парсинг 1688)."""
import os
import re

from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
ACTOR_ID = "songd/1688-search-scraper"


def parse_1688(keyword: str, max_pages: int = 1) -> list[dict]:
    """Запустить парсинг 1688 по ключевому слову.
    
    Returns:
        Список товаров (сырые данные из Apify)
    """
    if not APIFY_TOKEN:
        raise ValueError("APIFY_TOKEN не найден в .env")

    client = ApifyClient(APIFY_TOKEN)

    run_input = {
        "maxPages": max_pages,
        "searchArray": [{"keyword": keyword}],
    }

    run = client.actor(ACTOR_ID).call(run_input=run_input)
    items = list(client.dataset(run.default_dataset_id).iterate_items())
    return items


def extract_sku(url: str) -> str | None:
    """Извлекает артикул (ID) из ссылки 1688."""
    if not url:
        return None
    match = re.search(r"offer/(\d+)\.html", url)
    return match.group(1) if match else None
