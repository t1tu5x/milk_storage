# 🏨 sklad_milk.py — финальная версия
# Интерфейс: только кнопки "+/-" по 0.5, без ручного ввода
# Возможность "отменить" последнюю операцию (факт/заказ) до формирования отчёта
# Сохранение в TXT, Google Sheets, Google Drive

import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo
import os
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === Константы ===
TZ = ZoneInfo("Asia/Jerusalem")
FACTS_HEADERS = ["timestamp_iso", "date_il", "product_he", "size", "quantity_units"]
ORDERS_HEADERS = FACTS_HEADERS
PRODUCTS = ["גבינה צהובה", "מוצרלה", "שמנת", "יוגורט", "חלב"]  # ← вставь свои

# === Streamlit config ===
st.set_page_config(page_title="🥛 Молочный склад", layout="wide")
st.title("🥛 Молочный склад — Отель Голан")

# === Session state ===
def init_state():
    if "facts" not in st.session_state:
        st.session_state.facts = []
    if "orders" not in st.session_state:
        st.session_state.orders = []
    if "counters" not in st.session_state:
        st.session_state.counters = {}
init_state()

# === Время ===
def now():
    dt = datetime.now(TZ)
    return dt.isoformat(), dt.strftime("%Y-%m-%d %H:%M")

# === Google Auth ===
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
])

drive = build("drive", "v3", credentials=creds)

# === Google Drive helpers ===
def upload_to_drive(folder_id, filepath):
    file_metadata = {"name": os.path.basename(filepath), "parents": [folder_id]}
    media = MediaFileUpload(filepath, mimetype="text/plain")
    drive.files().create(body=file_metadata, media_body=media, fields="id").execute()

# === Sheets helpers ===
def save_to_sheet(sheet_name, rows):
    try:
        ws = sheet.worksheet(sheet_name)
    except:
        ws = sheet.add_worksheet(title=sheet_name, rows=1000, cols=10)
        ws.append_row(FACTS_HEADERS)
    ws.append_rows(rows)

# === UI: блок продукта ===
def product_block(name):
    st.markdown(f"### 🧀 {name}")
    key_base = name.replace(" ", "_")
    size = st.radio("Размер:", ["big", "small"], horizontal=True, key=f"{key_base}_size")

    if key_base not in st.session_state.counters:
        st.session_state.counters[key_base] = {"fact": 0.0, "order": 0.0}

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Фактический остаток:**")
        if st.button("➖", key=f"{key_base}_fact_minus"):
            st.session_state.counters[key_base]["fact"] = max(0.0, st.session_state.counters[key_base]["fact"] - 0.5)
        st.write(f"**{st.session_state.counters[key_base]['fact']} шт.**")
        if st.button("➕", key=f"{key_base}_fact_plus"):
            st.session_state.counters[key_base]["fact"] += 0.5
        if st.button("💾 Сохранить факт", key=f"{key_base}_fact_save"):
            ts_iso, date = now()
            qty = st.session_state.counters[key_base]["fact"]
            st.session_state.facts.append([ts_iso, date, name, size, qty])
            st.success(f"Сохранено: {qty} шт. {name} ({size})")
        if st.button("↩️ Отменить факт", key=f"{key_base}_fact_undo"):
            for i in range(len(st.session_state.facts)-1, -1, -1):
                if st.session_state.facts[i][2] == name:
                    st.session_state.facts.pop(i)
                    st.warning(f"Удалена последняя запись по {name}")
                    break

    with col2:
        st.markdown("**Требуется закупить:**")
        if st.button("➖", key=f"{key_base}_order_minus"):
            st.session_state.counters[key_base]["order"] = max(0.0, st.session_state.counters[key_base]["order"] - 0.5)
        st.write(f"**{st.session_state.counters[key_base]['order']} шт.**")
        if st.button("➕", key=f"{key_base}_order_plus"):
            st.session_state.counters[key_base]["order"] += 0.5
        if st.button("✅ Подтвердить заказ", key=f"{key_base}_order_save"):
            ts_iso, date = now()
            qty = st.session_state.counters[key_base]["order"]
            st.session_state.orders.append([ts_iso, date, name, size, qty])
            st.success(f"Добавлено в заказ: {qty} шт. {name} ({size})")
        if st.button("↩️ Отменить заказ", key=f"{key_base}_order_undo"):
            for i in range(len(st.session_state.orders)-1, -1, -1):
                if st.session_state.orders[i][2] == name:
                    st.session_state.orders.pop(i)
                    st.warning(f"Удалена последняя запись заказа по {name}")
                    break
    st.divider()

# === UI: список товаров ===
for name in PRODUCTS:
    product_block(name)

# === Своды ===
st.subheader("🧾 Свод по инвентаризации")
if st.session_state.facts:
    st.dataframe(st.session_state.facts)
    if st.button("📦 Сформировать инвентаризацию"):
        filename = f"stock_{datetime.now(TZ).strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join("milk_stocks", filename)
        os.makedirs("milk_stocks", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            for row in st.session_state.facts:
                f.write(f"{row[2]} ({row[3]}): {row[4]} шт.\n")
        upload_to_drive(st.secrets["drive"]["inventariz_id"], filepath)
        save_to_sheet("facts", st.session_state.facts)
        st.success(f"Инвентаризация сохранена и загружена: {filename}")
else:
    st.info("Нет записей по остаткам")

st.subheader("🧾 Свод по заказу")
if st.session_state.orders:
    st.dataframe(st.session_state.orders)
    if st.button("🧾 Сформировать заказ"):
        filename = f"order_{datetime.now(TZ).strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join("milk_orders", filename)
        os.makedirs("milk_orders", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            for row in st.session_state.orders:
                f.write(f"{row[2]} ({row[3]}): {row[4]} шт.\n")
        upload_to_drive(st.secrets["drive"]["order_lists_id"], filepath)
        save_to_sheet("orders", st.session_state.orders)
        st.success(f"Заказ сохранён и загружен: {filename}")
else:
    st.info("Нет записей по заказу")
