# -*- coding: utf-8 -*-
# 🏨 Golan Hotel — МОЛОЧНЫЙ СКЛАД (Streamlit)

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ======= НАСТРОЙКИ СТРАНИЦЫ =======
st.set_page_config(page_title="🥛 Молочный склад — Golan Hotel", layout="wide")

TZ = ZoneInfo("Asia/Jerusalem")
today_str = datetime.now(TZ).strftime("%d.%m.%Y")

# ======= CSS: ТЕМНАЯ ТЕМА =======
st.markdown("""
<style>
body, [data-testid="stAppViewContainer"] {
  background-color: #000000;
  color: white;
}
h1, h2, h3, .stButton>button {
  color: white;
}
.stTextInput>div>input {
  color: black !important;
  background-color: white !important;
  font-size: 20px !important;
}
.stButton>button {
  font-size: 20px !important;
  padding: .6rem .9rem !important;
  border-radius: 12px !important;
}
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; }
.st-expanderHeader {
  font-size: 22px !important;
}
.fullscreen-btn {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #444;
  color: white;
  padding: 8px 12px;
  border-radius: 10px;
  z-index: 1000;
  cursor: pointer;
}
</style>
""", unsafe_allow_html=True)

# ======= КОТ ИНТРО =======
st.markdown("""
<hr>
<div style="color:white;font-size:20px">
/\\_/\\  <br>
( •_•)  Выбери свой сырок и молочко, бро!<br>
/>🧀<🍶🍶🍶
</div>
""", unsafe_allow_html=True)

# ======= ПРОДУКТЫ =======
PRODUCTS = {
    "גבינה גאודה 🧀": "gauda",
    "מעדנים תות 🍓": "dessert_strawberry",
    "מעדנים יוגורט 🍦": "dessert_yogurt",
    "צפתית 🧀": "tsfatit",
    "חלב 🥛": "milk",
}

# ======= СОСТОЯНИЕ =======
if "final_facts" not in st.session_state:
    st.session_state.final_facts = []
if "final_orders" not in st.session_state:
    st.session_state.final_orders = []

st.title("🥛 Молочный склад — Golan Hotel")
st.markdown(f"📅 **Дата: {today_str}**")

st.subheader("📋 Учет продуктов")

for prod_label, prod_key in PRODUCTS.items():
    default_type = "small" if "מעדנים" in prod_label else "big"
    with st.expander(prod_label):
        size = st.radio("Размер упаковки", ["small", "big"], index=0 if default_type == "small" else 1, key=f"size_{prod_key}")
        step = 1 if size == "small" else 0.5

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Фактический остаток**")
            if f"fact_{prod_key}" not in st.session_state:
                st.session_state[f"fact_{prod_key}"] = 0.0
            if st.button(f"➖ {step}", key=f"fact_minus_{prod_key}"):
                st.session_state[f"fact_{prod_key}"] = max(0.0, st.session_state[f"fact_{prod_key}"] - step)
            if st.button(f"➕ {step}", key=f"fact_plus_{prod_key}"):
                st.session_state[f"fact_{prod_key}"] += step
            st.text_input("Факт:", value=st.session_state[f"fact_{prod_key}"], disabled=True, key=f"fact_display_{prod_key}")
            if st.button("📂 Сохранить факт", key=f"save_fact_{prod_key}"):
                st.session_state.final_facts.append({"product": prod_label, "qty": st.session_state[f"fact_{prod_key}"]})

        with col2:
            st.markdown("**Заказать дополнительно**")
            if f"order_{prod_key}" not in st.session_state:
                st.session_state[f"order_{prod_key}"] = 0.0
            if st.button(f"➖ {step}", key=f"order_minus_{prod_key}"):
                st.session_state[f"order_{prod_key}"] = max(0.0, st.session_state[f"order_{prod_key}"] - step)
            if st.button(f"➕ {step}", key=f"order_plus_{prod_key}"):
                st.session_state[f"order_{prod_key}"] += step
            st.text_input("Заказ:", value=st.session_state[f"order_{prod_key}"], disabled=True, key=f"order_display_{prod_key}")
            if st.button("✅ Подтвердить заказ", key=f"save_order_{prod_key}"):
                st.session_state.final_orders.append({"product": prod_label, "qty": st.session_state[f"order_{prod_key}"]})

# ======= ТАБЛИЦЫ =======
def make_df(entries):
    df = pd.DataFrame(entries)
    return df.groupby("product")["qty"].sum().reset_index()

st.subheader("📦 Сводные таблицы")

if st.session_state.final_facts:
    df1 = make_df(st.session_state.final_facts)
    st.markdown(f"### ✅ Инвентаризация — {today_str}")
    st.dataframe(df1)
    csv1 = df1.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Скачать CSV (Инвентаризация)", data=csv1, file_name=f"inventariz_{today_str}.csv", mime="text/csv")

if st.session_state.final_orders:
    df2 = make_df(st.session_state.final_orders)
    st.markdown(f"### 📥 Закуп — {today_str}")
    st.dataframe(df2)
    csv2 = df2.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Скачать CSV (Закуп)", data=csv2, file_name=f"zakup_{today_str}.csv", mime="text/csv")

st.markdown("""
<button class="fullscreen-btn" onclick="document.documentElement.requestFullscreen()">🖥️ На весь экран</button>
""", unsafe_allow_html=True)

st.markdown("""
---
<span style="font-family:monospace">
/\\_/\\<br>
( •_•)  спасибо за работу<br>
/>🍶   приходи за молочком!
</span>
""", unsafe_allow_html=True)
