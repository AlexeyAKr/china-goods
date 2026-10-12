import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from shared.config import CNY_RUB_RATE, DELIVERY_PER_KG

st.set_page_config(
    page_title="ChinaGoods — товары",
    page_icon="📦",
    layout="wide",
)

# === Sidebar: настройки расчёта ===
with st.sidebar:
    st.header("⚙️ Настройки расчёта")

    st.number_input(
        "Курс юаня (₽ за ¥)",
        min_value=1.0,
        max_value=100.0,
        value=CNY_RUB_RATE,
        step=0.1,
        format="%.2f",
        key="cny_rub_rate",
    )
    st.number_input(
        "Тариф доставки (₽/кг)",
        min_value=0.0,
        max_value=10000.0,
        value=DELIVERY_PER_KG,
        step=50.0,
        format="%.0f",
        key="delivery_per_kg",
    )

    st.caption("Цены в каталоге пересчитываются автоматически.")

# === Навигация ===
pg = st.navigation([
    st.Page("pages/products.py", title="Товары", icon="📦"),
    st.Page("pages/new_product.py", title="Новый товар", icon="➕"),
    st.Page("pages/product_detail.py", title="Карточка товара", icon="📝"),
])
pg.run()