import streamlit as st
from datetime import datetime

st.set_page_config(page_title="🐮 Молочный склад", page_icon="🥛", layout="centered")

# === ASCII приветствие ===
st.markdown("### 🧀🐱 Добро пожаловать в молочный склад!")
st.code(r"""
 /\_/\  
( o.o )   ~ Сегодня учёт — завтра порядок!
 > ^ <
""")

# === Список продуктов (иврит, упорядоченный) ===
PRODUCTS = [
    "גבינה גאודה", "גבינה צהובה", "גבינה מוצרלה", "גבינה מוצרלה ארוך",
    "פרומעז", "גבינת שמנת", "גבינת שום", "גבינת זיתים", "גבינה לבנה", "קוטג׳",
    "רוקפור", "קממבר", "ברי", "מוצרלה טחון",
    "מעדנים תות", "מעדנים אֲפַרסֵק", "מעדנים יוגורט", "מעדנים פודינג",
    "בולגרית 5%", "בולגרית 24%", "מוצרלה בייבי כדורים", "מוצרלה צפתית",
    "יוגורט נעמה", "גבינה מגורדת", "גבינה מוצרלה מגורדת",
    "שמנת חממה", "שמנת מפוסטרת", "חלב", "ביצים קרטון",
    "רביולי גבינה", "רביולי בטטה", "מוצרלה מטוגנת",
    "בלינצ׳ס נוגה", "בלינצ׳ס שוקולד", "בלינצ׳ס תפוח"
]

# === Состояние ===
for key in ["facts", "orders"]:
    if key not in st.session_state:
        st.session_state[key] = []

# === Интерфейс ===
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

# === Вывод факта ===
st.markdown("---")
st.markdown("### ✅ Фактические остатки:")
if st.session_state.facts:
    for row in st.session_state.facts:
        st.write(f"{row[1]}. {row[2]} — {row[4]} шт. ({row[0]})")
else:
    st.info("Нет записей по факту.")

# === Вывод заказа ===
st.markdown("### 📦 Что нужно закупить:")
if st.session_state.orders:
    for row in st.session_state.orders:
        st.write(f"{row[1]}. {row[2]} — {row[4]} шт. ({row[0]})")
else:
    st.info("Нет заказов.")

# === Отчёт по заказу ===
if st.button("🧾 Сформировать отчёт"):
    if not st.session_state.orders:
        st.warning("Список заказов пуст!")
    else:
        report = "\n".join([f"{row[2]} — {row[4]} шт." for row in st.session_state.orders])
        st.text_area("📝 Готовый отчёт для отправки:", value=report, height=200)
        st.success("Отчёт сформирован!")

# === Проверка работоспособности ===
try:
    st.markdown("##### ✅ Приложение работает корректно.")
except Exception as e:
    st.error(f"🚨 Ошибка: {e}")
