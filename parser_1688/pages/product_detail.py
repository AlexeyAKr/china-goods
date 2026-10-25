import streamlit as st

from parser_1688.core.calculator import calculate
from shared.config import CNY_RUB_RATE, DELIVERY_PER_KG
from shared.db import SessionLocal
from shared.models import Category, Product

st.title("Карточка товара")

rate = st.session_state.get("cny_rub_rate", CNY_RUB_RATE)
delivery = st.session_state.get("delivery_per_kg", DELIVERY_PER_KG)

raw_id = st.session_state.get("selected_product_id")
if not raw_id:
    st.info("Выберите товар в разделе «Товары».")
    st.stop()

try:
    product_id = int(raw_id)
except (TypeError, ValueError):
    st.error("Некорректный ID товара.")
    st.stop()

session = SessionLocal()
try:
    product = session.query(Product).filter(Product.id == product_id).first()
    if not product:
        st.error(f"Товар с id={product_id} не найден.")
        st.stop()
        
    st.write("DEBUG: Код дошел до картинки")
    img_url = product.attributes.get("image_url") if product.attributes else None
    if img_url:
        col_img, _ = st.columns([1, 2])
        with col_img:
            st.image(img_url, use_container_width=True)
    else:
        st.info("Изображение отсутствует")
            
        
    categories = session.query(Category).order_by(Category.name).all()
    cat_options = {c.name: c.id for c in categories}
    cat_names = list(cat_options.keys())
    current_cat_name = product.category.name if product.category else cat_names[0]

    with st.form("edit_product"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Название товара *", value=product.name)
            category_name = st.selectbox(
                "Категория *",
                cat_names,
                index=cat_names.index(current_cat_name) if current_cat_name in cat_names else 0,
            )
            source_url = st.text_input("Ссылка на 1688", value=product.source_url or "")

        with col2:
            price_cny = st.number_input(
                "Цена в юанях (¥) *",
                min_value=0.0, step=1.0, value=float(product.price_cny or 0),
            )
            weight_kg = st.number_input(
                "Вес (кг) *",
                min_value=0.0, step=0.1, value=float(product.weight_kg or 0),
            )
            markup = st.number_input(
                "Наценка (%)",
                min_value=0.0, step=5.0, value=float(product.markup_percent or 30),
            )

        m = calculate(
            price_cny=price_cny,
            weight_kg=weight_kg,
            markup_percent=markup,
            rate=rate,
            delivery_per_kg=delivery,
        )

        st.divider()
        st.subheader("Расчёт")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Себестоимость товара", f"{m.price_rub:.0f} ₽")
        c2.metric("Доставка", f"{m.delivery_cost:.0f} ₽")
        c3.metric("Итого", f"{m.total_cost:.0f} ₽")
        c4.metric("Розничная", f"{m.retail_price:.0f} ₽")
        st.metric("Маржа", f"{m.margin_rub:.0f} ₽ ({m.margin_percent:.0f}%)")

        col_save, col_delete = st.columns([3, 1])
        with col_save:
            saved = st.form_submit_button("💾 Сохранить изменения", type="primary")
        with col_delete:
            deleted = st.form_submit_button("🗑 Удалить")

        if saved:
            if not name.strip():
                st.error("Введи название товара.")
            else:
                product.name = name.strip()
                product.category_id = cat_options[category_name]
                product.source_url = source_url or None
                product.price_cny = price_cny
                product.price_rub = m.price_rub
                product.weight_kg = weight_kg
                product.markup_percent = markup
                session.commit()
                st.success("Изменения сохранены.")

        if deleted:
            session.delete(product)
            session.commit()
            st.session_state.pop("selected_product_id", None)
            st.success(f"Товар «{product.name}» удалён.")
            st.switch_page("pages/products.py")
finally:
    session.close()

if st.button("← Назад к списку"):
    st.switch_page("pages/products.py")