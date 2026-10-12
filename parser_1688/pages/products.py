import io

import streamlit as st

from parser_1688.core.calculator import calculate
from shared.config import CNY_RUB_RATE, DELIVERY_PER_KG
from shared.db import SessionLocal
from shared.models import Category, Product

st.title("Товары")
st.caption("Каталог товаров из Китая с расчётом маржи.")

# Текущие курс и тариф (из sidebar, если заданы)
rate = st.session_state.get("cny_rub_rate", CNY_RUB_RATE)
delivery = st.session_state.get("delivery_per_kg", DELIVERY_PER_KG)

session = SessionLocal()
try:
    # Фильтры
    col1, col2 = st.columns([2, 3])
    with col1:
        categories = session.query(Category).order_by(Category.name).all()
        cat_options = {"Все категории": None}
        cat_options.update({c.name: c.id for c in categories})
        selected_cat_name = st.selectbox("Категория", list(cat_options.keys()))
        selected_cat_id = cat_options[selected_cat_name]

    with col2:
        search = st.text_input("Поиск по названию", "")

    # Запрос с фильтрами
    query = session.query(Product)
    if selected_cat_id is not None:
        query = query.filter(Product.category_id == selected_cat_id)
    if search.strip():
        query = query.filter(Product.name.ilike(f"%{search.strip()}%"))

    products = query.order_by(Product.created_at.desc()).all()
    total_all = session.query(Product).count()

    st.metric("Найдено товаров", f"{len(products)} из {total_all}")

    if not products:
        if total_all == 0:
            st.info("Пока нет товаров. Добавь первый в разделе «Новый товар».")
        else:
            st.warning("По выбранным фильтрам ничего не найдено.")
    else:
        # Кнопка экспорта CSV
        rows = []
        for p in products:
            m = calculate(
                price_cny=p.price_cny or 0,
                weight_kg=p.weight_kg or 0,
                markup_percent=p.markup_percent or 30,
                rate=rate,
                delivery_per_kg=delivery,
            )
            rows.append({
                "id": p.id,
                "name": p.name,
                "category": p.category.name if p.category else "",
                "price_cny": p.price_cny or 0,
                "weight_kg": p.weight_kg or 0,
                "markup_percent": p.markup_percent or 0,
                "cost_item_rub": m.price_rub,
                "cost_delivery_rub": m.delivery_cost,
                "total_cost_rub": m.total_cost,
                "retail_price_rub": m.retail_price,
                "margin_rub": m.margin_rub,
                "source_url": p.source_url or "",
            })

        csv_buffer = io.StringIO()
        headers = list(rows[0].keys())
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

        # Карточки товаров
        for p in products:
            m = calculate(
                price_cny=p.price_cny or 0,
                weight_kg=p.weight_kg or 0,
                markup_percent=p.markup_percent or 30,
                rate=rate,
                delivery_per_kg=delivery,
            )
            with st.container(border=True):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
                with col1:
                    st.subheader(p.name)
                    cat = p.category.name if p.category else "—"
                    st.caption(f"Категория: {cat}")
                with col2:
                    st.metric("Себестоимость", f"{m.total_cost:.0f} ₽")
                with col3:
                    st.metric("Розничная", f"{m.retail_price:.0f} ₽")
                with col4:
                    st.metric("Маржа", f"{m.margin_rub:.0f} ₽")
finally:
    session.close()