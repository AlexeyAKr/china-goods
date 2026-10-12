import io

import streamlit as st

from parser_1688.core.calculator import calculate
from shared.config import CNY_RUB_RATE, DELIVERY_PER_KG
from shared.db import SessionLocal
from shared.models import Category, Product

st.title("Товары")
st.caption("Каталог товаров из Китая с расчётом маржи.")

rate = st.session_state.get("cny_rub_rate", CNY_RUB_RATE)
delivery = st.session_state.get("delivery_per_kg", DELIVERY_PER_KG)

# === Чтение данных ===
session = SessionLocal()
try:
    categories = session.query(Category).order_by(Category.name).all()
    cat_options = {"Все категории": None}
    cat_options.update({c.name: c.id for c in categories})

    total_all = session.query(Product).count()

    # Забираем всё как list of dict — чтобы не держать сессию открытой
    products_raw = session.query(Product).order_by(Product.created_at.desc()).all()
    products = [
        {
            "id": p.id,
            "name": p.name,
            "category_name": p.category.name if p.category else "—",
            "category_id": p.category_id,
            "price_cny": p.price_cny or 0,
            "weight_kg": p.weight_kg or 0,
            "markup_percent": p.markup_percent or 0,
            "source_url": p.source_url or "",
        }
        for p in products_raw
    ]
finally:
    session.close()

# === Фильтры ===
col1, col2 = st.columns([2, 3])
with col1:
    selected_cat_name = st.selectbox("Категория", list(cat_options.keys()))
    selected_cat_id = cat_options[selected_cat_name]

with col2:
    search = st.text_input("Поиск по названию", "")

# === Фильтрация в Python ===
filtered = products
if selected_cat_id is not None:
    filtered = [p for p in filtered if p["category_id"] == selected_cat_id]
if search.strip():
    needle = search.strip().lower()
    filtered = [p for p in filtered if needle in p["name"].lower()]

st.metric("Найдено товаров", f"{len(filtered)} из {total_all}")

if not filtered:
    if total_all == 0:
        st.info("Пока нет товаров. Добавь первый в разделе «Новый товар».")
    else:
        st.warning("По выбранным фильтрам ничего не найдено.")
    st.stop()

# === Расчёт + экспорт ===
rows = []
for p in filtered:
    m = calculate(
        price_cny=p["price_cny"],
        weight_kg=p["weight_kg"],
        markup_percent=p["markup_percent"],
        rate=rate,
        delivery_per_kg=delivery,
    )
    rows.append({
        "id": p["id"],
        "name": p["name"],
        "category": p["category_name"],
        "price_cny": p["price_cny"],
        "weight_kg": p["weight_kg"],
        "markup_percent": p["markup_percent"],
        "cost_item_rub": m.price_rub,
        "cost_delivery_rub": m.delivery_cost,
        "total_cost_rub": m.total_cost,
        "retail_price_rub": m.retail_price,
        "margin_rub": m.margin_rub,
        "source_url": p["source_url"],
        "_m": m,
    })

csv_buffer = io.StringIO()
headers = [k for k in rows[0].keys() if not k.startswith("_")]
csv_buffer.write(";".join(headers) + "\n")
for r in rows:
    csv_buffer.write(";".join(str(r[h]) for h in headers) + "\n")

st.download_button(
    label="📥 Скачать CSV",
    data=csv_buffer.getvalue().encode("utf-8-sig"),
    file_name="china_goods_catalog.csv",
    mime="text/csv",
)

st.divider()

# === Карточки ===
for r in rows:
    m = r["_m"]
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
        with col1:
            st.subheader(r["name"])
            st.caption(f"Категория: {r['category']}")
        with col2:
            st.metric("Себестоимость", f"{m.total_cost:.0f} ₽")
        with col3:
            st.metric("Розничная", f"{m.retail_price:.0f} ₽")
        with col4:
            st.metric("Маржа", f"{m.margin_rub:.0f} ₽")
        with col5:
            if st.button("Открыть", key=f"open_{r['id']}"):
                st.session_state["selected_product_id"] = r["id"]
                st.switch_page("pages/product_detail.py")