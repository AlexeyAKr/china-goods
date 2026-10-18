import json
import time
import os
from openai import OpenAI
from shared.db import SessionLocal
from shared.models import Product
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиента ProxyAPI
client = OpenAI(
    base_url=os.getenv("PROXYAPI_BASE_URL", "https://api.proxyapi.ru/v1"),
    api_key=os.getenv("PROXYAPI_KEY"),
)

def clean_names_with_proxyapi(items):
    system_prompt = (
        "Ты — профессиональный менеджер маркетплейсов. Твоя задача — очистить сырые названия товаров "
        "с китайского оптового сайта. Исправь слипшиеся слова (добавь пробелы), убери мусорные "
        "символы и переведи на естественный русский язык, подходящий для карточки товара на Авито. "
        "Верни результат СТРОГО в формате JSON-массива без пояснений."
    )
    
    user_prompt = f"Вот список товаров (JSON): {json.dumps(items, ensure_ascii=False)}\n"
    user_prompt += 'Верни строго JSON-массив такого вида: [{"id": 1, "clean_name": "Красивое название"}, ...]'

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        content = response.choices[0].message.content
        # Очищаем от markdown
        content = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content)
    except Exception as e:
        print(f"Ошибка запроса к ProxyAPI: {e}")
        return []

def main():
    session = SessionLocal()
    try:
        # Берем товары с SKU (спарсенные)
        products = session.query(Product).filter(Product.sku_1688.isnot(None)).all()
        print(f"Найдено товаров для обработки: {len(products)}")

        batch_size = 15  # GPT-4o-mini хорошо справляется с 15 товарами за раз
        total_updated = 0

        for i in range(0, len(products), batch_size):
            batch = products[i:i + batch_size]
            batch_items = [{"id": p.id, "raw_name": p.name} for p in batch]
            
            print(f"Обрабатываю пачку {i//batch_size + 1} (товаров: {len(batch)})...")
            
            cleaned_data = clean_names_with_proxyapi(batch_items)
            
            if cleaned_data:
                for item in cleaned_data:
                    prod_id = item.get("id")
                    new_name = item.get("clean_name")
                    if prod_id and new_name:
                        prod = session.query(Product).get(prod_id)
                        if prod:
                            prod.name = new_name
                            total_updated += 1
                
                session.commit()
                print(f"  ✅ Пачка обновлена.")
            else:
                print(f"  ⚠️ Модель не вернула данные для этой пачки.")
            
            time.sleep(1)

        print(f"\n🎉 Готово! Обновлено названий: {total_updated}")
        
    finally:
        session.close()

if __name__ == "__main__":
    main()