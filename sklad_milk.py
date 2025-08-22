# 🏨 Golan Hotel — МОЛОЧНЫЙ СКЛАД (офлайн-версия)

import streamlit as st

# СТИЛЬ

st.markdown("""
<style>
/* БАЗА: тёмный фон + белый текст */
html, body, [data-testid="stAppViewContainer"] {
  background:#000 !important; color:#fff !important;
}

/* Базовый размер шрифта (крупнее) */
html, body, [class*="css"] { font-size: 20px !important; }
.block-container { padding-top: 1.4rem; padding-bottom: 3rem; }

/* Заголовки и экспандеры */
h1, h2, h3 { letter-spacing: .3px; color:#fff; }
.st-expanderHeader { font-size: 22px !important; }

/* Кнопки — крупные и удобные */
button, .stButton>button {
  font-size: 20px !important;
  padding: .75rem 1.1rem !important;
  border-radius: 16px !important;
  width: 100% !important;
}

/* Инпуты: делаем читаемыми в disabled-состоянии */
.stTextInput input, .stNumberInput input {
  background:#111 !important; color:#fff !important; border:1px solid #666 !important;
}
.stTextInput input:disabled, .stNumberInput input:disabled {
  color:#fff !important; opacity:1 !important; background:#111 !important; border-color:#777 !important;
}

/* Таблицы (DataFrame) – белые шрифты */
[data-testid="stDataFrame"] * {
  color:#fff !important;
}
[data-testid="stDataFrame"] .st-emotion-cache-1y4p8pa { /* ячейки */
  background:#0b0b0b !important;
}
[data-testid="stDataFrame"] thead th, [data-testid="stDataFrame"] tbody td {
  border-color:#333 !important;
}

/* Плашка текущего количества */
.qty {
  font-size: 28px; font-weight: 900;
  padding: .25rem .8rem; border-radius: 14px;
  background: #111; color:#fff; display:inline-block;
  min-width: 90px; text-align:center; border:1px solid #555;
}

/* Мобильная адаптация: всё ЕЩЁ КРУПНЕЕ */
@media (max-width: 520px) {
  html, body, [class*="css"] { font-size: 22px !important; }
  .st-expanderHeader { font-size: 24px !important; }
  button, .stButton>button { font-size: 22px !important; padding: .9rem 1.2rem !important; }
  .qty { font-size: 32px; min-width: 110px; }
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<style>
/* Чёрный фон страницы */
html, body, [class*="css"] {
    background-color: black !important;
}

/* Белый текст по умолчанию */
h1, h2, h3, h4, h5, h6, p, span, div, label {
    color: white !important;
    font-size: 22px !important;
}

/* Текстовые и числовые поля — белый фон, чёрный текст */
input[type="text"], input[type="number"] {
    background-color: white !important;
    color: black !important;
    font-size: 22px !important;
}

/* Кнопки — белый фон, чёрный текст */
button[kind="primary"], .stButton>button, .stDownloadButton>button {
    background-color: white !important;
    color: black !important;
    font-size: 20px !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    border: none !important;
}

/* Hover эффект на кнопках */
button[kind="primary"]:hover, .stButton>button:hover, .stDownloadButton>button:hover {
    background-color: #e0e0e0 !important;
    color: black !important;
}

/* Expander блоки — чёрный фон, белый текст */
.st-expander {
    background-color: #111 !important;
    border: 1px solid white !important;
    border-radius: 10px !important;
}
.st-expander summary {
    color: white !important;
    font-size: 22px !important;
}
</style>
""", unsafe_allow_html=True)


import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo



# ======= КОТИК ФИНАЛ =======
st.markdown("""
<hr>
<div style="color:white;font-size:20px">
/\\_/\\  <br>
( •_•)  Выбери свой сырок и молочкобро!<br>
/>🧀<🍶🍶🍶🍶
</div>
""", unsafe_allow_html=True)

TZ = ZoneInfo("Asia/Jerusalem")
TODAY = datetime.now(TZ).strftime("%d.%m.%Y")
st.set_page_config(page_title="🥛 Молочный склад — 🌿Golan Hotel🌿", layout="wide")


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
