# 🏨 Golan Hotel — МОЛОЧНЫЙ СКЛАД (офлайн-версия)

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ======= КОТИК ФИНАЛ =======
st.markdown("""
<hr>
<div style="color:white;font-size:20px">
/\\_/\\  <br>
( •_•)  Выбери свой сырок бро!<br>
/>🍶<\
</div>
""", unsafe_allow_html=True)

TZ = ZoneInfo("Asia/Jerusalem")
TODAY = datetime.now(TZ).strftime("%d.%m.%Y")
st.set_page_config(page_title="🥛 Молочный склад — 🌿Golan Hotel🌿", layout="wide")

# ======= UI СТИЛЬ =======
st.markdown("""
<style>
html, body, [class*="css"]  { font-size: 20px !important; }
h1, h2, h3 { letter-spacing: .3px; color: white; }
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; }
button, .stButton>button {
  font-size: 18px !important; padding: .55rem .9rem !important;
  border-radius: 14px !important;
  background: white !important; color: black !important;
}
.g-badge, .g-chip, .g-card { color: white; }
.qty {
  font-size: 24px; font-weight: 800; padding: .1rem .6rem; border-radius: 12px;
  background: white; color:black; display:inline-block; min-width:72px; text-align:center;
}
input[type="text"] {
  background-color: white !important;
  color: black !important;
  font-weight: bold;
  font-size: 20px;
}
.stApp {
  background-color: black;
}
</style>
""", unsafe_allow_html=True)

# ======= СТЕЙТ =======
if "final_facts" not in st.session_state:
    st.session_state.final_facts = []
if "final_orders" not in st.session_state:
    st.session_state.final_orders = []

# ======= СПИСОК ПРОДУКТОВ =======
PRODUCTS = [
    "🧀 גבינה גאודה", "🧀 גבינה צהובה", "🧀 גבינה מוצרלה", "🧀 גבינה מוצרלה ארוך", "🐐 פרומעז",
    "🥯 גבינת שמנת", "🧄 גבינת שום", "🫒 גבינת זיתים", "🧀 גבינה לבנה", "🏠 קוטג׳", "🌿 רוקפור",
    "🧀 קממבר", "🧀 ברי", "🧀 מוצרלה טחון", "🍓 מעדנים תות", "🍑 מעדנים אֲפַרסֵק", "🥣 מעדנים יוגורט",
    "🍮 מעדנים פודינג", "🧂 בולגרית  5%", "🧂 בולגרית  24%", "🧀 מוצרלה בייבי", "🧀 כדורים מוצרלה",
    "🧀 צפתית", "🥣 יוגורט", "🧒 נעמה", "🧀 גבינה מגורדת", "🧀 גבינה מוצרלה מגורדת", "🍶 שמנת", "🌿 חממה",
    "🍶 שמנת מפוסטרת", "🥛 חלב", "🥚 ביצים קרטון", "🧀 רביולי גבינה", "🍠 רביולי בטטה", "🍤 מוצרלה מטוגנת",
    "🥞 בלינצ׳ס נוגה", "🍫 בלינצ׳ס שוקולד", "🍏 בלינצ׳ס תפוח"
]

# ======= ВВОД КОЛИЧЕСТВ =======
st.markdown(f"# 🥛 Молочный склад — Golan Hotel")
st.markdown(f"📅 **Дата: {TODAY}**")

st.subheader("📋 Учет продуктов")

for prod in PRODUCTS:
    size_type = "small" if "מעדנים" in prod else "big"
    step = 1 if size_type == "small" else 0.5

    with st.expander(prod):
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("**Фактический остаток**")
            if f"fact_{prod}" not in st.session_state:
                st.session_state[f"fact_{prod}"] = 0.0
            if st.button("➖", key=f"fact_minus_{prod}"):
                st.session_state[f"fact_{prod}"] = max(0.0, st.session_state[f"fact_{prod}"] - step)
            if st.button("➕", key=f"fact_plus_{prod}"):
                st.session_state[f"fact_{prod}"] += step
            st.text_input("Факт:", value=st.session_state[f"fact_{prod}"], key=f"fact_display_{prod}", disabled=True)
            if st.button("💾 Сохранить", key=f"fact_save_{prod}"):
                st.session_state.final_facts.append({"product": prod, "qty": st.session_state[f"fact_{prod}"]})
        with col2:
            st.markdown("**Заказать дополнительно**")
            if f"order_{prod}" not in st.session_state:
                st.session_state[f"order_{prod}"] = 0.0
            if st.button("➖", key=f"order_minus_{prod}"):
                st.session_state[f"order_{prod}"] = max(0.0, st.session_state[f"order_{prod}"] - step)
            if st.button("➕", key=f"order_plus_{prod}"):
                st.session_state[f"order_{prod}"] += step
            st.text_input("Заказ:", value=st.session_state[f"order_{prod}"], key=f"order_display_{prod}", disabled=True)
            if st.button("✅ Подтвердить", key=f"order_save_{prod}"):
                st.session_state.final_orders.append({"product": prod, "qty": st.session_state[f"order_{prod}"]})

# ======= ТАБЛИЦЫ =======
def make_df(entries):
    df = pd.DataFrame(entries)
    return df.groupby("product")["qty"].sum().reset_index()

st.subheader("📦 Сводные таблицы")

if st.session_state.final_facts:
    df1 = make_df(st.session_state.final_facts)
    st.markdown(f"### ✅ Инвентаризация (ספירת מלאי) — {TODAY}")
    st.dataframe(df1, use_container_width=True)
    st.download_button("⬇️ Скачать инвентаризацию CSV", data=df1.to_csv(index=False), file_name=f"inventory_{TODAY}.csv", mime="text/csv")

if st.session_state.final_orders:
    df2 = make_df(st.session_state.final_orders)
    st.markdown(f"### 📥 Заказ (הזמנה) — {TODAY}")
    st.dataframe(df2, use_container_width=True)
    st.download_button("⬇️ Скачать заказ CSV", data=df2.to_csv(index=False), file_name=f"order_{TODAY}.csv", mime="text/csv")

# ======= КОТИК ФИНАЛ =======
st.markdown("""
<hr>
<div style="color:white;font-size:20px">
/\\_/\\  <br>
( •_•)  спасибо!<br>
/>🍶   возвращайся за сырочком
</div>
""", unsafe_allow_html=True)
