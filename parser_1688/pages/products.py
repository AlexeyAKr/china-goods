import streamlit as st

from parser_1688.core.calculator import calculate
from shared.db import SessionLocal
from shared.models import Product

st.title("Товары")
st.caption("Каталог товаров из Китая с расчётом маржи.")

session = SessionLocal()
try:
    total = session.query(Product).count()
    st.metric("Всего товаров", total)

    if total == 0:
        st.info("Пока нет товаров. Добавь первый в разделе «Новый товар».")
    else:
        products = session.query(Product).order_by(Product.created_at.desc()).all()
        for p in products:
            m = calculate(
                price_cny=p.price_cny or 0,
                weight_kg=p.weight_kg or 0,
                markup_percent=p.markup_percent or 30,
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