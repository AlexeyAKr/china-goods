import streamlit as st

from parser_1688.core.calculator import calculate
from shared.db import SessionLocal
from shared.models import Category, Product

st.title("Новый товар")
st.caption("Введи данные вручную — расчёт маржи выполнится автоматически.")

session = SessionLocal()
try:
    categories = session.query(Category).order_by(Category.name).all()
    cat_options = {c.name: c.id for c in categories}
finally:
    session.close()

if not cat_options:
    st.error("Нет категорий в БД. Запусти seed_categories.py.")
    st.stop()

with st.form("new_product", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Название товара *")
        category_name = st.selectbox("Категория *", list(cat_options.keys()))
        source_url = st.text_input("Ссылка на 1688 (опционально)")

    with col2:
        price_cny = st.number_input("Цена в юанях (¥) *", min_value=0.0, step=1.0, value=100.0)
        weight_kg = st.number_input("Вес (кг) *", min_value=0.0, step=0.1, value=0.5)
        markup = st.number_input("Наценка (%)", min_value=0.0, step=5.0, value=30.0)

    m = calculate(price_cny=price_cny, weight_kg=weight_kg, markup_percent=markup)

    st.divider()
    st.subheader("Расчёт")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Себестоимость товара", f"{m.price_rub:.0f} ₽")
    c2.metric("Доставка", f"{m.delivery_cost:.0f} ₽")
    c3.metric("Итого", f"{m.total_cost:.0f} ₽")
    c4.metric("Розничная", f"{m.retail_price:.0f} ₽")

    st.metric("Маржа", f"{m.margin_rub:.0f} ₽ ({m.margin_percent:.0f}%)")

    submitted = st.form_submit_button("Сохранить товар", type="primary")

    if submitted:
        if not name.strip():
            st.error("Введи название товара.")
        else:
            session = SessionLocal()
            try:
                product = Product(
                    name=name.strip(),
                    category_id=cat_options[category_name],
                    price_cny=price_cny,
                    price_rub=m.price_rub,
                    weight_kg=weight_kg,
                    markup_percent=markup,
                    source_url=source_url or None,
                )
                session.add(product)
                session.commit()
                st.success(f"Товар «{name}» сохранён (id={product.id}).")
            except Exception as e:
                session.rollback()
                st.error(f"Ошибка: {e}")
            finally:
                session.close()