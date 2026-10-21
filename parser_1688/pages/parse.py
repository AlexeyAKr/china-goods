"""Страница «Спарсить с 1688» с автокатегориями и картинками."""
import os
import json
import streamlit as st
from parser_1688.core.apify_client import parse_1688, extract_sku
from parser_1688.core.calculator import calculate
from shared.db import SessionLocal
from shared.models import Category, Product

try:
    from openai import OpenAI
    PROXYAPI_KEY = os.getenv("PROXYAPI_KEY")
    if PROXYAPI_KEY:
        _ai_client = OpenAI(base_url=os.getenv("PROXYAPI_BASE_URL", "https://api.proxyapi.ru/v1"), api_key=PROXYAPI_KEY)
    else:
        _ai_client = None
except Exception:
    _ai_client = None

def _clean_and_categorize_with_ai(items: list[dict], categories: list[dict]) -> dict[int, dict]:
    if not _ai_client or not items:
        return {}
    system_prompt = (
        "Ты — профессиональный переводчик и категоризатор товаров. "
        "Твоя задача — перевести сырые китайские/кривые названия на естественный русский язык, "
        "сохранив их УНИКАЛЬНОСТЬ. НЕ используй общие фразы вроде 'Игрушка для детей' для разных товаров. "
        "Также определи правильную категорию из списка. Верни СТРОГО JSON-массив без пояснений."
    )
    user_prompt = (
        f"Список доступных категорий:\n{json.dumps(categories, ensure_ascii=False, indent=2)}\n\n"
        f"Товары для обработки:\n{json.dumps(items, ensure_ascii=False, indent=2)}\n\n"
        'Формат ответа (строго массив):\n'
        '[{"id": 123, "clean_name": "Уникальное русское название", "category_slug": "toys"}, ...]\n'
    )
    try:
        response = _ai_client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            temperature=0.2,
        )
        content = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content)
        return {item["id"]: item for item in data if "id" in item}
    except Exception as e:
        st.warning(f"⚠️ Ошибка ИИ: {e}")
        return {}

st.title("Спарсить с 1688")
st.caption("Введите ключевое слово — Apify соберёт товары, ИИ почистит названия, разложит по категориям и добавит фото.")

keyword = st.text_input("Ключевое слово на 1688", placeholder="например, robot или 机器人")
max_pages = st.number_input("Страниц (1 страница ≈ 50 товаров)", min_value=1, max_value=3, value=1)
do_ai_clean = st.checkbox("Почистить названия и распределить по категориям через ИИ", value=True)

if st.button("🚀 Спарсить и сохранить", type="primary"):
    if not keyword.strip():
        st.error("Введите ключевое слово")
        st.stop()

    session = SessionLocal()
    try:
        cats = session.query(Category).all()
        cat_data = [{"slug": c.slug, "name": c.name} for c in cats]
        cat_map = {c.slug: c.id for c in cats}
        default_cat_id = cat_map.get("home-kitchen")
    finally:
        session.close()

    with st.spinner(f"Apify ищет «{keyword}» на 1688..."):
        try:
            raw_items = parse_1688(keyword.strip(), max_pages=max_pages)
        except Exception as e:
            st.error(f"Ошибка Apify: {e}")
            st.stop()

    if not raw_items:
        st.warning("Ничего не найдено. Попробуйте другое слово.")
        st.stop()

    st.info(f"Получено товаров: {len(raw_items)}. Сохраняю в БД...")
    session = SessionLocal()
    saved_products = []
    try:
        for item in raw_items:
            title = (item.get("title") or "").strip()
            price_str = item.get("price")
            url = item.get("url", "")
            if not title or not price_str:
                continue
            sku = extract_sku(url)
            if sku and session.query(Product).filter(Product.sku_1688 == sku).first():
                continue
            try:
                price_cny = float(price_str)
                if price_cny > 5000: continue # Отсекаем оптовые коробки
            except (ValueError, TypeError):
                continue
            
            m = calculate(price_cny=price_cny, weight_kg=0.5, markup_percent=30)
            
            # ДОБАВЛЯЕМ СОХРАНЕНИЕ КАРТИНКИ
            img_url = item.get("imageUrl") or item.get("image") or item.get("picUrl")
            
            product = Product(
                name=title, category_id=default_cat_id, price_cny=price_cny, price_rub=m.price_rub,
                weight_kg=0.5, markup_percent=30, source_url=url, sku_1688=sku, 
                attributes={"raw_title": title, "image_url": img_url}
            )
            session.add(product)
            session.flush()
            saved_products.append({"id": product.id, "raw_name": title})
        session.commit()
    except Exception as e:
        session.rollback()
        st.error(f"Ошибка БД: {e}")
        st.stop()
    finally:
        session.close()

    st.success(f"✅ Сохранено товаров: {len(saved_products)}")

    if do_ai_clean and _ai_client and saved_products:
        batch_size = 5 
        updated_count = 0
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(0, len(saved_products), batch_size):
            batch = saved_products[i:i + batch_size]
            status_text.text(f"ИИ обрабатывает пачку {i//batch_size + 1}...")
            ai_results = _clean_and_categorize_with_ai(batch, cat_data)
            
            if ai_results:
                session = SessionLocal()
                try:
                    for prod_id, data in ai_results.items():
                        prod = session.get(Product, prod_id)
                        if prod:
                            prod.name = data.get("clean_name", prod.name)
                            slug = data.get("category_slug")
                            if slug and slug in cat_map:
                                prod.category_id = cat_map[slug]
                            updated_count += 1
                    session.commit()
                except Exception:
                    session.rollback()
                finally:
                    session.close()
            progress_bar.progress(min(1.0, (i + batch_size) / len(saved_products))
        
        status_text.empty()
        progress_bar.empty()
        st.success(f"✅ ИИ обновил названия и категории: {updated_count} товаров")

    st.balloons()
    st.info("Готово! Перейдите в раздел «Товары», чтобы увидеть результат.")