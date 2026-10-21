import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

st.set_page_config(
    page_title="ChinaGoods — товары",
    page_icon="📦",
    layout="wide",
)

pg = st.navigation([
    st.Page("pages/products.py", title="Товары", icon="📦"),
    st.Page("pages/parse.py", title="Спарсить с 1688", icon="🔎"),
    st.Page("pages/new_product.py", title="Новый товар", icon="➕"),
    st.Page("pages/product_detail.py", title="Карточка товара", icon="📝"),
])
pg.run()