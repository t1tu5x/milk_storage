# -*- coding: utf-8 -*-
# 🏨 Golan Hotel — МОЛОЧНЫЙ СКЛАД (офлайн-версия без Google Sheets)

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Jerusalem")
st.set_page_config(page_title="🥛 Молочный склад — Golan Hotel", layout="wide")

# ======= СТИЛЬ =======
st.markdown("""
<style>
html, body, [class*="css"]  { font-size: 18px !important; }
h1, h2, h3 { letter-spacing: .3px; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; }
button, .stButton>button {
  font-size: 18px !important; padding: .55rem .9rem !important;
  border-radius: 14px !important;
}
.g-badge {
  display:inline-block; padding:.2rem .6rem; border-radius:12px;
  background:#f1f5f9; color:#0f172a; font-weight:600; margin-left:.4rem;
}
.g-chip {
  padding:.25rem .6rem; border-radius:999px; background:#eef2ff; color:#4338ca;
  font-size: 0.9rem; font-weight: 700; margin-left:.5rem;
}
.g-card {
  border:1px solid #e2e8f0; border-radius:16px; padding:12px 14px; margin-bottom:10px;
  background: #fff;
  box-shadow: 0 0 0 1px rgba(2,6,23,0.02), 0 8px 24px rgba(2,6,23,0.05);
}
.qty {
  font-size: 22px; font-weight: 800; padding: .1rem .6rem; border-radius: 12px;
  background: #ecfeff; color:#0e7490; display:inline-block; min-width:72px; text-align:center;
}
.kitty {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
}
</style>
""", unsafe_allow_html=True)

# ======= ASCII приветствие =======
st.markdown("""
# 🥛 Молочный склад — Golan Hotel
<span class="kitty">
/\\_/\\  ☆  привет!<br>
( o.o )  считаем сырки, йогурты и молочко по 0.5<br>
> ^ <
</span>
""", unsafe_allow_html=True)

# ======= СОСТОЯНИЕ =======
if "final_facts" not in st.session_state:
    st.session_state.final_facts = []
if "final_orders" not in st.session_state:
    st.session_state.final_orders = []

# ======= СПИСОК ПРОДУКТОВ =======
PRODUCTS = [
    "גבינה גאודה", "גבינה צהובה", "גבינה מוצרלה", "גבינה מוצרלה ארוך", "פרומעז",
    "גבינת שמנת", "גבינת שום", "גבינת זיתים", "גבינה לבנה", "קוטג׳", "רוקפור",
    "קממבר", "ברי", "מוצרלה טחון", "מעדנים תות", "מעדנים אֲפַרסֵק", "מעדנים יוגורט",
    "מעדנים פודינג", "בולגרית  5%", "בולגרית  24%", "מוצרלה בייבי", "כדורים מוצרלה",
    "צפתית", "יוגורט", "נעמה", "גבינה מגורדת", "גבינה מוצרלה מגורדת", "שמנת", "חממה",
    "שמנת מפוסטרת", "חלב", "ביצים קרטון", "רביולי גבינה", "רביולי בטטה", "מוצרלה מטוגנת",
    "בלינצ׳ס נוגה", "בלינצ׳ס שוקולד", "בלינצ׳ס תפוח"
]

# ======= ВВОД КОЛИЧЕСТВ =======
st.subheader("📋 Учет продуктов")
st.markdown("Нажимай кнопки ±0.5, чтобы изменить количество. После этого нажми сохранить.")

for prod in PRODUCTS:
    with st.expander(prod):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**Фактический остаток**")
            if f"fact_{prod}" not in st.session_state:
                st.session_state[f"fact_{prod}"] = 0.0
            if st.button(f"➖ 0.5", key=f"fact_minus_{prod}"):
                st.session_state[f"fact_{prod}"] = max(0.0, st.session_state[f"fact_{prod}"] - 0.5)
            if st.button(f"➕ 0.5", key=f"fact_plus_{prod}"):
                st.session_state[f"fact_{prod}"] += 0.5
            st.markdown(f"**Текущее значение:** `{st.session_state[f'fact_{prod}']}`")
            if st.button(f"💾 Сохранить факт", key=f"fact_save_{prod}"):
                st.session_state.final_facts.append({"product": prod, "qty": st.session_state[f"fact_{prod}"]})
        with col2:
            st.markdown("**Заказать дополнительно**")
            if f"order_{prod}" not in st.session_state:
                st.session_state[f"order_{prod}"] = 0.0
            if st.button(f"➖ 0.5", key=f"order_minus_{prod}"):
                st.session_state[f"order_{prod}"] = max(0.0, st.session_state[f"order_{prod}"] - 0.5)
            if st.button(f"➕ 0.5", key=f"order_plus_{prod}"):
                st.session_state[f"order_{prod}"] += 0.5
            st.markdown(f"**Текущее значение:** `{st.session_state[f'order_{prod}']}`")
            if st.button(f"✅ Подтвердить заказ", key=f"order_save_{prod}"):
                st.session_state.final_orders.append({"product": prod, "qty": st.session_state[f"order_{prod}"]})

# ======= ИТОГОВЫЕ ТАБЛИЦЫ =======
def make_df(entries):
    df = pd.DataFrame(entries)
    return df.groupby("product")["qty"].sum().reset_index()

st.subheader("📦 Сводные таблицы")
if st.session_state.final_facts:
    df1 = make_df(st.session_state.final_facts)
    st.markdown("### ✅ Инвентаризация")
    st.dataframe(df1)
if st.session_state.final_orders:
    df2 = make_df(st.session_state.final_orders)
    st.markdown("### 📥 Заказ")
    st.dataframe(df2)

# ======= КОТИК ФИНАЛЬНЫЙ =======
st.markdown("""
<hr>
<div class="kitty">
/\\_/\\  <br>
( •_•)  спасибо!<br>
/>🍶   возвращайся за сырочком
</div>
""", unsafe_allow_html=True)
