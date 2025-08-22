# -*- coding: utf-8 -*-
# 🏨 Golan Hotel — МОЛОЧНЫЙ СКЛАД (офлайн-версия без Google API)
# Ввод только кнопками ±0.5, временное хранилище, отмена последней записи,
# сводные таблицы + кнопки скачивания TXT/CSV. Заглушки upload_to_drive/save_to_sheet.

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from collections import defaultdict

import streamlit as st
import pandas as pd

# ====== БАЗОВЫЕ НАСТРОЙКИ ======
TZ = ZoneInfo("Asia/Jerusalem")
PAGE_TITLE = "🥛 Молочный склад — Golan Hotel"
st.set_page_config(page_title=PAGE_TITLE, layout="wide")

# ====== ЗАГЛУШКИ ДЛЯ БЕЗОПАСНОСТИ ======
def upload_to_drive(*args, **kwargs):
    # no-op: убрали Drive
    return None

def save_to_sheet(*args, **kwargs):
    # no-op: убрали Sheets
    return None

# ====== СТИЛЬ (мобила/крупные элементы/няшный вайб) ======
st.markdown("""
<style>
html, body, [class*="css"]  { font-size: 18px !important; }
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
.kitty { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace; }
</style>
""", unsafe_allow_html=True)

# ====== ASCII-кошки ======
st.markdown(
f"""
# {PAGE_TITLE}  
<span class="kitty">
/\\_/\\  ☆  привет!<br>
( o.o )  считаем сырки, йогурты и молочко по 0.5<br>
> ^ <
</span>
""",
unsafe_allow_html=True
)
st.caption("Кликай только «➕/➖ 0.5». Чтобы записать — жми «💾 Сохранить факт» или «✅ Подтвердить заказ». Отменить можно только **последнюю** запись по товару до формирования таблиц.")

# ====== СПИСОК ПРОДУКТОВ (иврит, строго заданный порядок) ======
PRODUCTS = [
    "גבינה גאודה",
    "גבינה צהובה",
    "גבינה מוצרלה",
    "גבינה מוצרלה ארוך",
    "פרומעז",
    "גבינת שמנת",
    "גבינת שום",
    "גבינת זיתים",
    "גבינה לבנה",
    "קוטג׳",
    "רוקפור",
    "קממבר",
    "ברי",
    "מוצרלה טחון",
    "מעדנים תות",
    "מעדנים אֲפַרסֵק",
    "מעדנים יוגורט",
    "מעדנים פודינג",
    "בולגרית  5%",
    "בולגרית  24%",
    "מוצרלה בייבי",
    "כדורים מוצרלה",
    "צפתית",
    "יוגורט",
    "נעמה",
    "גבינה מגורדת",
    "גבינה מוצרלה מגורדת",
    "שמנת",
    "חממה",
    "שמנת מפוסטרת",
    "חלב",
    "ביצים קרטון",
    "רביולי גבינה",
    "רביולי בטטה",
    "מוצרלה מטוגנת",
    "בלינצ׳ס נוגה",
    "בלינצ׳ס שוקולד",
    "בלינצ׳ס תפוח",
]

# Эмодзи под настроение
EMOJI = {
    "חלב": "🥛", "יוגורט": "🥛", "קוטג׳": "🥣", "גבינה": "🧀", "ביצים": "🥚",
    "רביולי": "🥟", "בלינצ׳ס": "🥞", "מעדנים": "🍮", "אֲפַרסֵק": "🍑", "תות": "🍓",
}
def emoji_for(name: str) -> str:
    for k, v in EMOJI.items():
        if k in name:
            return v
    return "🧀"

# ====== SESSION STATE ======
def _init_state():
    if "temp_facts" not in st.session_state:   # временные записи фактов
        st.session_state.temp_facts = []       # dict(timestamp, product, size, qty)
    if "temp_orders" not in st.session_state:  # временные записи заказов
        st.session_state.temp_orders = []
    if "counters" not in st.session_state:     # {'product_key': {'fact':0.0,'order':0.0,'size':'big'}}
        st.session_state.counters = {}
    if "finalized_facts" not in st.session_state:
        st.session_state.finalized_facts = False
    if "finalized_orders" not in st.session_state:
        st.session_state.finalized_orders = False

_init_state()

def pkey(name: str) -> str:
    return name.replace(" ", "_").replace("'", "_").replace("״", "_")

def now():
    dt = datetime.now(TZ)
    return dt, dt.strftime("%Y-%m-%d %H:%M")

def add05(x: float) -> float:
    return round((x + 0.5) * 2) / 2.0

def sub05(x: float) -> float:
    y = round((x - 0.5) * 2) / 2.0
    return max(0.0, y)

# ====== Сайдбар ======
with st.sidebar:
    st.header("⚙️ Управление")
    if st.button("🧽 Новая сессия (очистить всё)", type="primary"):
        for k in ("temp_facts", "temp_orders", "counters", "finalized_facts", "finalized_orders"):
            if k in st.session_state:
                del st.session_state[k]
        _init_state()
        st.experimental_rerun()

    show_debug = st.checkbox("Показать отладку", value=False)

# ====== КОМПОНЕНТ ТОВАРА ======
def product_block(name: str):
    key = pkey(name)
    if key not in st.session_state.counters:
        st.session_state.counters[key] = {"fact": 0.0, "order": 0.0, "size": "big"}

    em = emoji_for(name)
    st.markdown(f'<div class="g-card"><h3>{em} {name}<span class="g-badge">milk</span></h3>', unsafe_allow_html=True)

    # Размер (по умолчанию — big)
    opt = st.segmented_control(
        "Размер единицы",
        options=["Большой", "Маленький"],
        default="Большой",
        key=f"{key}_size_seg",
    )
    size = "big" if opt == "Большой" else "small"
    st.session_state.counters[key]["size"] = size

    c1, c2 = st.columns(2)

    # ===== ФАКТ =====
    with c1:
        st.markdown("**Фактический остаток**  <span class='g-chip'>±0.5</span>", unsafe_allow_html=True)
        bb1, bb2, bb3, bb4 = st.columns([1,1,2,2])
        if bb1.button("➖ 0.5", key=f"{key}_fact_minus", disabled=st.session_state.finalized_facts):
            st.session_state.counters[key]["fact"] = sub05(st.session_state.counters[key]["fact"])
        if bb2.button("➕ 0.5", key=f"{key}_fact_plus", disabled=st.session_state.finalized_facts):
            st.session_state.counters[key]["fact"] = add05(st.session_state.counters[key]["fact"])
        bb3.markdown(f"<div class='qty'>{st.session_state.counters[key]['fact']:.1f}</div>", unsafe_allow_html=True)
        if bb4.button("🔄 Сброс", key=f"{key}_fact_reset", disabled=st.session_state.finalized_facts):
            st.session_state.counters[key]["fact"] = 0.0

        a1, a2 = st.columns([2,2])
        if a1.button("💾 Сохранить факт", key=f"{key}_fact_save", disabled=st.session_state.finalized_facts):
            qty = float(st.session_state.counters[key]["fact"])
            if qty <= 0:
                st.warning("Введите количество (хотя бы 0.5) перед сохранением.")
            else:
                _, ts_str = now()
                st.session_state.temp_facts.append({
                    "timestamp": ts_str,
                    "product": name,
                    "size": size,
                    "qty": qty,
                })
                st.success(f"Сохранено: {qty:.1f} шт. — {name} ({size})")
                st.session_state.counters[key]["fact"] = 0.0

        if a2.button("↩️ Отменить факт", key=f"{key}_fact_undo", disabled=st.session_state.finalized_facts):
            for i in range(len(st.session_state.temp_facts)-1, -1, -1):
                if st.session_state.temp_facts[i]["product"] == name:
                    removed = st.session_state.temp_facts.pop(i)
                    st.warning(f"Удалено: {removed['qty']:.1f} шт. — {name} ({removed['size']})")
                    break
            else:
                st.info("Для этого товара нет временных записей.")

    # ===== ЗАКАЗ =====
    with c2:
        st.markdown("**Требуется закупить**  <span class='g-chip'>±0.5</span>", unsafe_allow_html=True)
        cc1, cc2, cc3, cc4 = st.columns([1,1,2,2])
        if cc1.button("➖ 0.5", key=f"{key}_order_minus", disabled=st.session_state.finalized_orders):
            st.session_state.counters[key]["order"] = sub05(st.session_state.counters[key]["order"])
        if cc2.button("➕ 0.5", key=f"{key}_order_plus", disabled=st.session_state.finalized_orders):
            st.session_state.counters[key]["order"] = add05(st.session_state.counters[key]["order"])
        cc3.markdown(f"<div class='qty'>{st.session_state.counters[key]['order']:.1f}</div>", unsafe_allow_html=True)
        if cc4.button("🔄 Сброс", key=f"{key}_order_reset", disabled=st.session_state.finalized_orders):
            st.session_state.counters[key]["order"] = 0.0

        b1, b2 = st.columns([2,2])
        if b1.button("✅ Подтвердить заказ", key=f"{key}_order_save", disabled=st.session_state.finalized_orders):
            qty = float(st.session_state.counters[key]["order"])
            if qty <= 0:
                st.warning("Введите количество (хотя бы 0.5) перед подтверждением заказа.")
            else:
                _, ts_str = now()
                st.session_state.temp_orders.append({
                    "timestamp": ts_str,
                    "product": name,
                    "size": size,
                    "qty": qty,
                })
                st.success(f"Добавлено в заказ: {qty:.1f} шт. — {name} ({size})")
                st.session_state.counters[key]["order"] = 0.0

        if b2.button("↩️ Отменить заказ", key=f"{key}_order_undo", disabled=st.session_state.finalized_orders):
            for i in range(len(st.session_state.temp_orders)-1, -1, -1):
                if st.session_state.temp_orders[i]["product"] == name:
                    removed = st.session_state.temp_orders.pop(i)
                    st.warning(f"Удалено из заказа: {removed['qty']:.1f} шт. — {name} ({removed['size']})")
                    break
            else:
                st.info("Для этого товара нет временных записей по заказу.")

    st.markdown("</div>", unsafe_allow_html=True)  # g-card end

# ====== РЕНДЕР ВСЕГО СПИСКА ======
for prod in PRODUCTS:
    product_block(prod)

st.divider()

# ====== ВСПОМОГАТЕЛЬНЫЕ ======
def aggregate_rows(rows: list[dict]) -> pd.DataFrame:
    """Группировка по продукту+размеру с суммой qty."""
    if not rows:
        return pd.DataFrame(columns=["Продукт", "Размер", "Количество"])
    df = pd.DataFrame(rows)
    g = df.groupby(["product", "size"], as_index=False)["qty"].sum()
    g = g.rename(columns={"product": "Продукт", "size": "Размер", "qty": "Количество"})
    g["Количество"] = g["Количество"].map(lambda x: f"{x:.1f}")
    return g

def df_to_txt_lines(df: pd.DataFrame, title: str) -> str:
    now_str = datetime.now(TZ).strftime("%Y-%m-%d %H:%M")
    lines = [f"{title} — {now_str}", "-"*28]
    for _, r in df.iterrows():
        lines.append(f"{r['Продукт']} ({r['Размер']}): {r['Количество']} шт.")
    return "\n".join(lines) + "\n"

def make_downloads(df: pd.DataFrame, base_name: str, title: str):
    ts = datetime.now(TZ).strftime("%Y%m%d_%H%M%S")
    csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
    txt_bytes = df_to_txt_lines(df, title).encode("utf-8")

    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "⬇️ Скачать CSV",
            data=csv_bytes,
            file_name=f"{base_name}_{ts}.csv",
            mime="text/csv",
            use_container_width=True
        )
    with c2:
        st.download_button(
            "⬇️ Скачать TXT",
            data=txt_bytes,
            file_name=f"{base_name}_{ts}.txt",
            mime="text/plain",
            use_container_width=True
        )

# ====== СВОДНЫЕ КНОПКИ/ТАБЛИЦЫ ======
st.subheader("🧾 Сводные таблицы")

colA, colB = st.columns(2)

with colA:
    st.markdown("### 📦 Инвентаризация")
    if st.session_state.temp_facts:
        st.dataframe(pd.DataFrame(st.session_state.temp_facts), use_container_width=True, height=220)
        if st.button("📦 Сформировать инвентаризацию", type="primary", disabled=st.session_state.finalized_facts):
            st.session_state.finalized_facts = True
    else:
        st.info("Пока нет временных записей по остаткам.")

    if st.session_state.finalized_facts:
        agg_f = aggregate_rows(st.session_state.temp_facts)
        st.success("Готово! Ниже — сводная таблица инвентаризации.")
        st.dataframe(agg_f, use_container_width=True, height=280)
        make_downloads(agg_f, base_name="stock", title="Инвентаризация")

with colB:
    st.markdown("### 🧾 Заказ на закуп")
    if st.session_state.temp_orders:
        st.dataframe(pd.DataFrame(st.session_state.temp_orders), use_container_width=True, height=220)
        if st.button("🧾 Сформировать заказ", type="primary", disabled=st.session_state.finalized_orders):
            st.session_state.finalized_orders = True
    else:
        st.info("Пока нет временных записей по заказу.")

    if st.session_state.finalized_orders:
        agg_o = aggregate_rows(st.session_state.temp_orders)
        st.success("Готово! Ниже — сводная таблица заказа.")
        st.dataframe(agg_o, use_container_width=True, height=280)
        make_downloads(agg_o, base_name="order", title="Заказ")

# ====== ОТЛАДКА ======
if show_debug:
    st.divider()
    st.subheader("🪲 DEBUG")
    st.write("finalized_facts:", st.session_state.finalized_facts,
             "finalized_orders:", st.session_state.finalized_orders)
    st.write("temp_facts:", st.session_state.temp_facts)
    st.write("temp_orders:", st.session_state.temp_orders)
    st.write("counters (live):", st.session_state.counters)

# Финальный котик
st.markdown("""
<hr>
<div class="kitty">
/\\_/\\  <br>
( •_•)  спасибо!<br>
/>🍶   возвращайся за сырочком
</div>
""", unsafe_allow_html=True)
