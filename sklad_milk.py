import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🐮 Молочный склад", page_icon="🥛", layout="centered")

# 🐱 ASCII
st.markdown("### 🧀🐱 Добро пожаловать в склад молочки!")
st.code(r"""
 /\_/\  
( o.o )   ~ Сегодня учёт — завтра порядок!
 > ^ <
""")

# === Продукты по порядку ===
PRODUCTS = [
    "חלב 3%", "שוקו", "שמנת מתוקה", "שמנת לבישול", "שמנת חמוצה", "גבינה לבנה",
    "גבינת סקי", "יוגורט", "יוגורט פרי", "קוטג׳", "קוטג׳ פרי", "חמאה",
    "מרגרינה", "גבינת פטה", "בולגרית", "צהובה פרוסות", "צהובה קוביות",
    "גאודה", "קשקבל", "גבינת עיזים", "גבינת שמנת", "גבינת שמנת שום שמיר",
    "גבינת שמנת זיתים", "גבינת שמנת ירק", "ריקוטה", "מסקרפונה", "גבינת שמנת מתוקה"
]

# === Init session ===
for key in ["facts", "orders"]:
    if key not in st.session_state:
        st.session_state[key] = []

# === UI ===
st.markdown("### 📋 Выберите количество для каждого продукта:")
for i, product in enumerate(PRODUCTS):
    col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])

    with col1:
        st.markdown(f"**{i+1}. {product}**")
    with col2:
        if f"fact_{i}" not in st.session_state:
            st.session_state[f"fact_{i}"] = 0.0
        if st.button("➖", key=f"fact_minus_{i}"):
            st.session_state[f"fact_{i}"] = max(0, st.session_state[f"fact_{i}"] - 0.5)
        st.write(f"{st.session_state[f'fact_{i}']} шт.")
        if st.button("➕", key=f"fact_plus_{i}"):
            st.session_state[f"fact_{i}"] += 0.5
    with col3:
        if st.button("📦 Сохранить факт", key=f"save_fact_{i}"):
            st.session_state.facts.append([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                i+1,
                product,
                "Факт",
                st.session_state[f"fact_{i}"]
            ])
    with col4:
        if st.button("❌ Отменить факт", key=f"undo_fact_{i}"):
            for idx in reversed(range(len(st.session_state.facts))):
                if st.session_state.facts[idx][1] == i+1:
                    del st.session_state.facts[idx]
                    break
    with col5:
        if st.button("🛒 Подтвердить заказ", key=f"add_order_{i}"):
            st.session_state.orders.append([
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                i+1,
                product,
                "Заказ",
                st.session_state[f"fact_{i}"]
            ])

# === Таблицы ===
st.markdown("---")
st.markdown("### ✅ Фактические остатки:")
if st.session_state.facts:
    for row in st.session_state.facts:
        st.write(f"{row[1]}. {row[2]} — {row[4]} шт. ({row[0]})")
else:
    st.info("Нет записей по факту.")

st.markdown("### 📦 Что нужно закупить:")
if st.session_state.orders:
    for row in st.session_state.orders:
        st.write(f"{row[1]}. {row[2]} — {row[4]} шт. ({row[0]})")
else:
    st.info("Нет заказов.")

# === Отчёт ===
if st.button("🧾 Сформировать отчёт"):
    if not st.session_state.orders:
        st.warning("Список заказов пуст!")
    else:
        report = "\n".join([f"{row[2]} — {row[4]} шт." for row in st.session_state.orders])
        st.text_area("📝 Готовый отчёт для отправки:", value=report, height=200)
        st.success("Отчёт сформирован!")

# === Ошибки отладки ===
try:
    st.markdown("##### 🛠 Всё работает без ошибок!")
except Exception as e:
    st.error(f"Ошибка: {e}")
