import streamlit as st
import datetime

st.set_page_config(page_title="🧀 Молочный склад", layout="wide")

# 🐱 ASCII-КОТ
st.markdown("### Добро пожаловать на склад молочки! 🧀🐱")
st.code(r"""
 /\_/\  
( o.o ) 
 > ^ <
""")

# 📦 Продукты
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

# Инициализация session_state
if "fact" not in st.session_state:
    st.session_state.fact = []
if "order" not in st.session_state:
    st.session_state.order = []

st.markdown("## 📋 Учёт факта и заказа")

for product in PRODUCTS:
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f"**{product}**")
    with col2:
        if st.button("➕ Факт", key=f"fact_{product}"):
            st.session_state.fact.append((str(datetime.date.today()), product, 1))
    with col3:
        if st.button("➕ Заказ", key=f"order_{product}"):
            st.session_state.order.append((str(datetime.date.today()), product, 1))
    with col4:
        if st.button("🗑 Удалить последнее", key=f"del_{product}"):
            if st.session_state.fact and st.session_state.fact[-1][1] == product:
                st.session_state.fact.pop()
            elif st.session_state.order and st.session_state.order[-1][1] == product:
                st.session_state.order.pop()

st.divider()

# 📊 Таблицы
st.markdown("### ✅ Фактический остаток")
st.table(st.session_state.fact)

st.markdown("### 📦 Заказ")
st.table(st.session_state.order)
