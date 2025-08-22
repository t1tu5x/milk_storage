# -*- coding: utf-8 -*-
# 🏨 Golan Hotel — МОЛОЧНЫЙ СКЛАД (Streamlit Offline Version)

import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

# ======= НАСТРОЙКИ СТРАНИЦЫ =======
st.set_page_config(page_title="🥛 Молочный склад — Golan Hotel", layout="wide")

TZ = ZoneInfo("Asia/Jerusalem")
today_str = datetime.now(TZ).strftime("%d.%m.%Y")

# ======= CSS: ТЁМНАЯ ТЕМА И КНОПКИ =======
st.markdown("""
<style>
/* 🔲 Тёмный фон, белый текст */
html, body, [data-testid="stAppViewContainer"] {
  background:#000 !important; color:#fff !important;
}

/* 📱 Крупный шрифт по умолчанию */
html, body, [class*="css"] {
  font-size: 20px !important;
}
.block-container {
  padding-top: 1.4rem; padding-bottom: 3rem;
}

/* 🧾 Заголовки */
h1, h2, h3 { letter-spacing: .3px; color:#fff; }
.st-expanderHeader { font-size: 22px !important; }

/* 🔘 Кнопки — удобные и широкие */
button, .stButton>button {
  font-size: 20px !important;
  padding: .75rem 1.1rem !important;
  border-radius: 16px !important;
  width: 100% !important;
}

/* ✍️ Инпуты: делаем читаемыми */
.stTextInput input, .stNumberInput input {
  background:#111 !important;
  color:#fff !important;
  border:1px solid #666 !important;
}
.stTextInput input:disabled, .stNumberInput input:disabled {
  color:#fff !important;
  background:#111 !important;
  border-color:#777 !important;
  opacity: 1 !important;
}

/* 📊 Таблицы (DataFrame) — светлые строки на тёмном фоне */
[data-testid="stDataFrame"] * {
  color:#fff !important;
}
[data-testid="stDataFrame"] .st-emotion-cache-1y4p8pa {
  background:#0b0b0b !important;
}
[data-testid="stDataFrame"] thead th, [data-testid="stDataFrame"] tbody td {
  border-color:#333 !important;
}

/* 🔢 Красивая плашка количества */
.qty {
  font-size: 28px; font-weight: 900;
  padding: .25rem .8rem; border-radius: 14px;
  background: #111; color:#fff; display:inline-block;
  min-width: 90px; text-align:center; border:1px solid #555;
}

/* 🖥 Кнопка "на весь экран" */
.fullscreen-btn {
  position: fixed; top: 18px; right: 18px;
  background: #333; color: #fff; padding: 10px 14px;
  border-radius: 12px; z-index: 1000; cursor: pointer;
  border:1px solid #555;
}

/* 📱 Ещё крупнее на телефоне */
@media (max-width: 520px) {
  html, body, [class*="css"] {
    font-size: 22px !important;
  }
  .st-expanderHeader {
    font-size: 24px !important;
  }
  button, .stButton>button {
    font-size: 22px !important;
    padding: .9rem 1.2rem !important;
  }
  .qty {
    font-size: 32px;
    min-width: 110px;
  }
}
</style>
""", unsafe_allow_html=True)


# ======= ПРИВЕТСТВИЕ =======
st.markdown(f"""
# 🥛 מַחְסָן חָלָב — 🌿 Golan Hotel 🌿

<span style="font-family:monospace">
/\\_/\\ ☆ привет👨🏻‍🍳!<br>
( o.o ) Сегодня: <b>{today_str}</b><br>
> 🥕 < считай сырки, йогурты и молочко
</span>
""", unsafe_allow_html=True)

# ======= ДАННЫЕ ПРОДУКТОВ С ЭМОДЗИ =======
PRODUCTS = {
    "גבינה גאודה 🧀": "gauda",
    "גבינה צהובה 🧀": "yellow_cheese",
    "גבינה מוצרלה 🧀": "mozzarella",
    "גבינה מוצרלה ארוך 🧀": "mozzarella_long",
    "פרומעז 🐐": "fromage",
    "גבינת שמנת 🍶": "cream_cheese",
    "גבינת שום 🧄": "garlic_cheese",
    "גבינת זיתים 🫒": "olive_cheese",
    "גבינה לבנה 🥛": "white_cheese",
    "קוטג׳ 🧂": "cottage",
    "רוקפור 💙": "roquefort",
    "קממבר 🧀": "camembert",
    "ברי 🧀": "brie",
    "מוצרלה טחון 🧀": "grated_mozzarella",
    "מעדנים תות 🍓": "dessert_strawberry",
    "מעדנים אֲפַרסֵק 🍑": "dessert_peach",
    "מעדנים יוגורט 🍦": "dessert_yogurt",
    "מעדנים פודינג 🍮": "dessert_pudding",
    "בולגרית  5% 🧂": "bulgarian_5",
    "בולגרית  24% 🧂": "bulgarian_24",
    "מוצרלה בייבי 👶": "mozzarella_baby",
    "כדורים מוצרלה 🧆": "mozzarella_balls",
    "צפתית 🧀": "tsfatit",
    "יוגורט 🍶": "yogurt",
    "נעמה 🧀": "naama",
    "גבינה מגורדת 🧀": "grated_cheese",
    "גבינה מוצרלה מגורדת 🧀": "mozzarella_grated",
    "שמנת 🥣": "cream",
    "חממה 🌿": "greenhouse",
    "שמנת מפוסטרת 🥛": "pasteurized_cream",
    "חלב 🥛": "milk",
    "ביצים קרטון 🥚": "eggs_carton",
    "רביולי גבינה 🍝": "ravioli_cheese",
    "רביולי בטטה 🍠": "ravioli_sweetpotato",
    "מוצרלה מטוגנת 🍤": "mozzarella_fried",
    "בלינצ׳ס נוגה 🥞": "blintz_noga",
    "בלינצ׳ס שוקולד 🍫": "blintz_choco",
    "בלינצ׳ס תפוח 🍏": "blintz_apple"
}

# ======= СОСТОЯНИЕ =======
if "final_facts" not in st.session_state:
    st.session_state.final_facts = []
if "final_orders" not in st.session_state:
    st.session_state.final_orders = []

# ======= ВВОД КОЛИЧЕСТВ =======
st.subheader("📋 Учет остатков и закупок")

for prod_label, prod_key in PRODUCTS.items():
    with st.expander(prod_label):
        col1, col2 = st.columns(2)

        # --- Фактический остаток ---
        with col1:
            st.markdown("**Фактический остаток**")
            if f"fact_{prod_key}" not in st.session_state:
                st.session_state[f"fact_{prod_key}"] = 0.0
            if st.button("➖ 0.5", key=f"fact_minus_{prod_key}"):
                st.session_state[f"fact_{prod_key}"] = max(0.0, st.session_state[f"fact_{prod_key}"] - 0.5)
            if st.button("➕ 0.5", key=f"fact_plus_{prod_key}"):
                st.session_state[f"fact_{prod_key}"] += 0.5
            st.text_input("Факт:", value=st.session_state[f"fact_{prod_key}"], disabled=True, key=f"fact_display_{prod_key}")
            if st.button("💾 Сохранить факт", key=f"save_fact_{prod_key}"):
                st.session_state.final_facts.append({"product": prod_label, "qty": st.session_state[f"fact_{prod_key}"]})

        # --- Заказ ---
        with col2:
            st.markdown("**Заказать дополнительно**")
            if f"order_{prod_key}" not in st.session_state:
                st.session_state[f"order_{prod_key}"] = 0.0
            if st.button("➖ 0.5", key=f"order_minus_{prod_key}"):
                st.session_state[f"order_{prod_key}"] = max(0.0, st.session_state[f"order_{prod_key}"] - 0.5)
            if st.button("➕ 0.5", key=f"order_plus_{prod_key}"):
                st.session_state[f"order_{prod_key}"] += 0.5
            st.text_input("Заказ:", value=st.session_state[f"order_{prod_key}"], disabled=True, key=f"order_display_{prod_key}")
            if st.button("✅ Подтвердить заказ", key=f"save_order_{prod_key}"):
                st.session_state.final_orders.append({"product": prod_label, "qty": st.session_state[f"order_{prod_key}"]})

# ======= СОЗДАНИЕ ТАБЛИЦ =======
def make_df(entries):
    df = pd.DataFrame(entries)
    return df.groupby("product")["qty"].sum().reset_index()

st.subheader("📦 Сводные таблицы")

# ======= ИНВЕНТАРИЗАЦИЯ =======
if st.session_state.final_facts:
    df1 = make_df(st.session_state.final_facts)
    st.markdown(f"### ✅ Инвентаризация (ספירת מלאי) — {today_str}")
    st.dataframe(df1)
    csv1 = df1.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Скачать CSV (Инвентаризация)", data=csv1, file_name=f"inventariz_{today_str}.csv", mime="text/csv")

# ======= ЗАКУП =======
if st.session_state.final_orders:
    df2 = make_df(st.session_state.final_orders)
    st.markdown(f"### 📥 Закуп (הזמנה) — {today_str}")
    st.dataframe(df2)
    csv2 = df2.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Скачать CSV (Закуп)", data=csv2, file_name=f"zakup_{today_str}.csv", mime="text/csv")

# ======= КНОПКА НА ВЕСЬ ЭКРАН =======
st.markdown("""
<button class="fullscreen-btn" onclick="document.documentElement.requestFullscreen()">🖥️ На весь экран</button>
""", unsafe_allow_html=True)

# ======= ASCII КОТИК =======
st.markdown("""
---
<span style="font-family:monospace">
/\\_/\\<br>
( •_•)  спасибо за работу<br>
/>🍶   приходи за молочком!
</span>
""", unsafe_allow_html=True)
