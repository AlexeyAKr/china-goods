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

session = SessionLocal()
try:
    categories = session.query(Category).order_by(Category.name).all()
    cat_options = {"Все категории": None}
    cat_options.update({c.name: c.id for c in categories})
    total_all = session.query(Product).count()
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
            "image_url": p.attributes.get("image_url") if p.attributes else None,
        }
        for p in products_raw
    ]
finally:
    session.close()

col1, col2 = st.columns([2, 3])
with col1:
    selected_cat_name = st.selectbox("Категория", list(cat_options.keys()))
    selected_cat_id = cat_options[selected_cat_name]
with col2:
    search = st.text_input("Поиск по названию", "")

filtered = products
if selected_cat_id is not None:
    filtered = [p for p in filtered if p["category_id"] == selected_cat_id]
if search.strip():
    needle = search.strip().lower()
    filtered = [p for p in filtered if needle in p["name"].lower()]

st.metric("Найдено товаров", f"{len(filtered)} из {total_all}")

if not filtered:
    st.info("Пока нет товаров. Добавь первый в разделе «Новый товар».")
    st.stop()

rows = []
for p in filtered:
    m = calculate(price_cny=p["price_cny"], weight_kg=p["weight_kg"], markup_percent=p["markup_percent"], rate=rate, delivery_per_kg=delivery)
    rows.append({**p, "_m": m})

csv_buffer = io.StringIO()
headers = ["id", "name", "category_name", "price_cny", "weight_kg", "markup_percent"]
csv_buffer.write(";".join(headers) + "\n")
for r in rows:
    csv_buffer.write(";".join(str(r[h]) for h in headers) + "\n")

st.download_button(label="📥 Скачать CSV", data=csv_buffer.getvalue().encode("utf-8-sig"), file_name="china_goods_catalog.csv", mime="text/csv")
st.divider()

# === Карточки ===
for r in rows:
    m = r["_m"]
    with st.container(border=True):
        col_img, col_info = st.columns([1, 5])
        with col_img:
            img_url = r.get("image_url")
            if img_url:
                st.image(img_url, use_container_width=True)
            else:
                st.caption("📷 Нет фото")
        with col_info:
            col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
            with col1:
                st.subheader(r["name"])
                st.caption(f"Категория: {r['category_name']}")
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