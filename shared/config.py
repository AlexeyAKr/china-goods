import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


DATABASE_URL = _get("DATABASE_URL")
GIGACHAT_CREDENTIALS = _get("GIGACHAT_CREDENTIALS")
GIGACHAT_SCOPE = _get("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
VK_TOKEN = _get("VK_TOKEN")
VK_GROUP_ID = _get("VK_GROUP_ID")
CNY_RUB_RATE = float(_get("CNY_RUB_RATE", "12.5"))
DELIVERY_PER_KG = float(_get("DELIVERY_PER_KG", "500"))