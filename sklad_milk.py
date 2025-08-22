# filename: sklad_milk.py
# 🏨 Отель Голан — МОЛОЧНЫЙ СКЛАД (Streamlit + Google Sheets + Google Drive)
# Новое: выгружаем TXT в Google Drive по путям:
#   golan_hotel/store_milk/order_lists   (заказы)
#   golan_hotel/store_milk/inventariz    (инвентаризация)

import os
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Tuple
from collections import defaultdict

import streamlit as st

# ====== НАСТРОЙКА СТРАНИЦЫ ======
st.set_page_config(page_title="🏨 Отель Голан — Молочный склад", page_icon="🥛", layout="wide")

TZ = ZoneInfo("Asia/Jerusalem")
ORDERS_DIR = "/mnt/data/milk_orders"
STOCKS_DIR = "/mnt/data/milk_stocks"
os.makedirs(ORDERS_DIR, exist_ok=True)
os.makedirs(STOCKS_DIR, exist_ok=True)

# ====== СПИСОК ПРОДУКТОВ (ПОРЯДОК СОХРАНЁН) ======
PRODUCTS: List[str] = [
    "גבינה גאודה","גבינה צהובה","גבינה מוצרלה","גבינה מוצרלה ארוך","פרומעז","גבינת שמנת","גבינת שום","גבינת זיתים",
    "גבינה לבנה","קוטג׳","רוקפור","קממבר","ברי","מוצרלה טחון","מעדנים תות","מעדנים אֲפַרסֵק","מעדנים יוגורט","מעדנים פודינג",
    "בולגרית  5%","בולגרית  24%","מוצרלה בייבי","כדורים מוצרלה","צפתית","יוגורט","נעמה","גבינה מגורדת","גבינה מוצרלה מגורדת",
    "שמנת","חממה","שמנת מפוסטרת","חלב","ביצים קרטון","רביולי גבינה","רביולי בטטה","מוצרלה מטוגנת","בלינצ׳ס נוגה","בלינצ׳ס שוקולד",
    "בלינצ׳ס תפוח","מלאווח",
]

# ====== ЭМОДЗИ ======
def pick_emoji(n: str) -> str:
    if any(k in n for k in ["גבינה","צפתית","גאודה","ברי","קממבר","רוקפור","בולגרית","מוצרלה"]): return "🧀"
    if any(k in n for k in ["קוטג","לבנה","נעמה","יוגורט"]): return "🥣"
    if "שמנת" in n or "חלב" in n: return "🥛"
    if "חמאה" in n or "חממה" in n: return "🧈"
    if "ביצים" in n: return "🥚"
    if any(k in n for k in ["רביולי","מלאווח","בלינצ","מטוגנת","פודינג","מעדנים"]): return "🥟"
    return "🧀"

# ====== Google Credentials (общие) ======
def get_gcp_credentials():
    from google.oauth2.service_account import Credentials
    if "gcp_service_account" not in st.secrets:
        raise RuntimeError("Не найден [gcp_service_account] в secrets.toml")
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/drive.file",
    ]
    return Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)

# ====== Google Sheets ======
FACTS_HEADERS  = ["timestamp_iso", "date_il", "product_he", "size", "quantity_units"]
ORDERS_HEADERS = ["timestamp_iso", "date_il", "product_he", "size", "quantity_units"]

def open_spreadsheet():
    import gspread
    creds = get_gcp_credentials()
    if "sheets" not in st.secrets or "milk_sheet_id" not in st.secrets["sheets"]:
        raise RuntimeError("Не найден sheets.milk_sheet_id в secrets.toml")
    client = gspread.authorize(creds)
    return client.open_by_key(st.secrets["sheets"]["milk_sheet_id"])

def ensure_worksheet(spread, title: str, headers: List[str]):
    try:
        ws = spread.worksheet(title)
    except Exception:
        ws = spread.add_worksheet(title=title, rows=2000, cols=max(10, len(headers)))
        ws.append_row(headers)
        return ws
    values = ws.get_all_values()
    if not values:
        ws.append_row(headers)
    else:
        current = values[0]
        if len(current) < len(headers) or any((h.strip() != (current[i].strip() if i < len(current) else "")) for i, h in enumerate(headers)):
            ws.delete_rows(1)
            ws.insert_row(headers, 1)
    return ws

def append_records(ws, rows: List[List]):
    if rows: ws.append_rows(rows, value_input_option="USER_ENTERED")

# ====== Google Drive ======
def get_drive_service():
    from googleapiclient.discovery import build
    creds = get_gcp_credentials()
    return build("drive", "v3", credentials=creds, cache_discovery=False)

def drive_find_folder_by_name(name: str, parent_id: str | None, service) -> str | None:
    # Ищем папку с заданным именем и родителем (если задан)
    q = ["mimeType='application/vnd.google-apps.folder'", "trashed=false", f"name='{name}'"]
    if parent_id:
        q.append(f"'{parent_id}' in parents")
    query = " and ".join(q)
    resp = service.files().list(q=query, spaces="drive", fields="files(id,name,parents)", pageSize=10).execute()
    files = resp.get("files", [])
    return files[0]["id"] if files else None

def drive_ensure_folder(name: str, parent_id: str | None, service) -> str:
    fid = drive_find_folder_by_name(name, parent_id, service)
    if fid: return fid
    body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id: body["parents"] = [parent_id]
    return service.files().create(body=body, fields="id").execute()["id"]

def drive_resolve_target_folders(service):
    # 1) если в secrets заданы точные ID — используем их
    order_id = st.secrets.get("drive", {}).get("order_lists_id")
    inv_id   = st.secrets.get("drive", {}).get("inventariz_id")
    if order_id and inv_id:
        return order_id, inv_id

    # 2) иначе — строим/находим путь golan_hotel/store_milk/{order_lists,inventariz}
    golan_id      = drive_ensure_folder("golan_hotel", None, service)
    store_milk_id = drive_ensure_folder("store_milk", golan_id, service)
    order_id      = drive_ensure_folder("order_lists", store_milk_id, service)
    inv_id        = drive_ensure_folder("inventariz",  store_milk_id, service)
    return order_id, inv_id

def drive_upload_txt(local_path: str, folder_id: str, service) -> str:
    from googleapiclient.http import MediaFileUpload
    file_name = os.path.basename(local_path)
    file_metadata = {"name": file_name, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype="text/plain", resumable=False)
    created = service.files().create(body=file_metadata, media_body=media, fields="id,webViewLink").execute()
    return created.get("webViewLink", "")

# ====== SESSION STATE ======
def init_state():
    for key in ["temp_facts","temp_orders","undo_facts","undo_orders"]:
        if key not in st.session_state: st.session_state[key] = []
    if "drive_targets" not in st.session_state:
        st.session_state.drive_targets = None  # кэш (order_folder_id, inventariz_folder_id)
init_state()

# ====== ВСПОМОГАТЕЛЬНЫЕ ======
def now_il():
    dt = datetime.now(TZ)
    return dt.isoformat(timespec="seconds"), dt.strftime("%Y-%m-%d %H:%M")

def parse_qty(text: str) -> Tuple[bool, float]:
    try:
        text = (text or "").strip()
        if text == "": return False, 0.0
        return True, float(text.replace(",", "."))
    except Exception:
        return False, 0.0

def badge(size: str) -> str:
    return "🅱️" if size == "big" else "🅂"

def line_for_txt(name_he: str, size: str, qty: float) -> str:
    return f"{pick_emoji(name_he)} {badge(size)} {name_he} — {qty:g}"

def aggregate(rows: List[Dict]) -> List[Dict]:
    acc = defaultdict(float)
    for r in rows:
        acc[(r["product_he"], r["size"])] += float(r["quantity_units"])
    prod_index = {p: i for i, p in enumerate(PRODUCTS)}
    out = [{"product_he": p, "size": s, "quantity_units": q} for (p, s), q in acc.items()]
    out.sort(key=lambda d: (prod_index.get(d["product_he"], 10**9), 0 if d["size"]=="big" else 1))
    return out

# ====== РЕНДЕР БЛОКА ПРОДУКТА ======
def render_product_block(name_he: str):
    st.markdown(f"### {pick_emoji(name_he)} **{name_he}**")
    c1, c2, c3 = st.columns([1.2, 1, 1], vertical_alignment="center")
    with c1:
        size = st.selectbox("Размер", options=["big","small"], index=0, key=f"size_{name_he}",
                            help="По умолчанию big. Выбери small при необходимости.")
    with c2:
        qty_text = st.text_input("Фактический остаток (шт., 0.5 ок)", value="", placeholder="напр. 1.5", key=f"fact_{name_he}")
        if st.button("💾 Сохранить факт", key=f"save_fact_{name_he}"):
            ok, qty = parse_qty(qty_text)
            if not ok: st.warning("Введите число для факта."); return
            ts_iso, ts_human = now_il()
            rec = {"timestamp_iso": ts_iso,"date_il": ts_human,"product_he": name_he,"size": size,"quantity_units": qty}
            st.session_state.temp_facts.append(rec); st.session_state.undo_facts.append(rec)
            st.success("Добавлено событие факта."); st.rerun()
    with c3:
        need_text = st.text_input("Требуется закупить (шт.)", value="", placeholder="напр. 2", key=f"need_{name_he}")
        if st.button("✅ Подтвердить заказ", key=f"add_order_{name_he}"):
            ok, qty = parse_qty(need_text)
            if not ok: st.warning("Введите число для заказа."); return
            ts_iso, ts_human = now_il()
            rec = {"timestamp_iso": ts_iso,"date_il": ts_human,"product_he": name_he,"size": size,"quantity_units": qty}
            st.session_state.temp_orders.append(rec); st.session_state.undo_orders.append(rec)
            st.success("Добавлено событие заказа."); st.rerun()
    st.divider()

# ====== UI ======
st.markdown("""
# 🥛 Молочный склад — Отель Голан
Интерфейс на русском, названия — **на иврите**.  
1) Выбери **Размер** (по умолчанию *big*).  
2) Введи число и нажми **«Сохранить факт»** или **«Подтвердить заказ»** — события копятся, своды суммируются.  
3) Внизу можно **отменить последнее**, **сформировать Заказ** или **Инвентаризацию** (TXT + Google Sheets + Google Drive).
""")

for name_he in PRODUCTS:
    render_product_block(name_he)

# ====== ЛОГИ + ОТМЕНА ======
st.subheader("🧾 События — Фактические остатки (лог)")
st.dataframe(st.session_state.temp_facts, use_container_width=True, hide_index=True) if st.session_state.temp_facts else st.info("Лог фактов пуст.")
if st.button("↩️ Отменить последнее событие (факт)"):
    if st.session_state.undo_facts:
        last = st.session_state.undo_facts.pop()
        for i in range(len(st.session_state.temp_facts)-1, -1, -1):
            if st.session_state.temp_facts[i] == last: st.session_state.temp_facts.pop(i); break
        st.success("Отменено последнее событие факта."); st.rerun()
    else: st.warning("Нечего отменять.")

st.subheader("🧾 События — Заказ (лог)")
st.dataframe(st.session_state.temp_orders, use_container_width=True, hide_index=True) if st.session_state.temp_orders else st.info("Лог заказов пуст.")
if st.button("↩️ Отменить последнее событие (заказ)"):
    if st.session_state.undo_orders:
        last = st.session_state.undo_orders.pop()
        for i in range(len(st.session_state.temp_orders)-1, -1, -1):
            if st.session_state.temp_orders[i] == last: st.session_state.temp_orders.pop(i); break
        st.success("Отменено последнее событие заказа."); st.rerun()
    else: st.warning("Нечего отменять.")

st.divider()

# ====== СВОДЫ ======
facts_agg  = aggregate(st.session_state.temp_facts)
orders_agg = aggregate(st.session_state.temp_orders)

st.subheader("📦 Свод по остаткам (агрегировано)")
st.dataframe(facts_agg, use_container_width=True, hide_index=True) if facts_agg else st.info("Свод фактов пуст.")

st.subheader("🧾 Свод по заказу (агрегировано)")
st.dataframe(orders_agg, use_container_width=True, hide_index=True) if orders_agg else st.info("Свод заказа пуст.")

# ====== TXT Генерация ======
def save_orders_txt(rows_agg: List[Dict]) -> str:
    if not rows_agg: return ""
    _, ts_human = now_il()
    fname = os.path.join(ORDERS_DIR, f"order_{ts_human.replace(':','-').replace(' ','_')}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("🧾 Заказ (молочный склад) — " + ts_human + "\n")
        for r in rows_agg: f.write(line_for_txt(r["product_he"], r["size"], r["quantity_units"]) + "\n")
    return fname

def save_stocks_txt(rows_agg: List[Dict]) -> str:
    if not rows_agg: return ""
    _, ts_human = now_il()
    fname = os.path.join(STOCKS_DIR, f"stock_{ts_human.replace(':','-').replace(' ','_')}.txt")
    with open(fname, "w", encoding="utf-8") as f:
        f.write("📦 Инвентаризация (молочный склад) — " + ts_human + "\n")
        for r in rows_agg: f.write(line_for_txt(r["product_he"], r["size"], r["quantity_units"]) + "\n")
    return fname

# ====== Папки Drive (кэшируем, чтобы не искать каждый раз) ======
def resolve_drive_targets():
    if st.session_state.drive_targets: return st.session_state.drive_targets
    service = get_drive_service()
    order_id, inv_id = drive_resolve_target_folders(service)
    st.session_state.drive_targets = (order_id, inv_id)
    return st.session_state.drive_targets

# ====== КНОПКИ ФИНАЛЬНЫХ ДЕЙСТВИЙ ======
colA, colB = st.columns(2)

with colA:
    if st.button("🧾 Сформировать заказ (TXT + Sheets + Drive)"):
        if not orders_agg: st.warning("Свод заказа пуст.")
        else:
            # TXT
            path = save_orders_txt(orders_agg)
            if path:
                st.success(f"Заказ сохранён: {os.path.basename(path)}")
                with open(path, "rb") as f:
                    st.download_button("⬇️ Скачать заказ (.txt)", data=f.read(),
                                       file_name=os.path.basename(path), mime="text/plain")
            # Google Sheets — сохраняем события (подробно)
            try:
                spread = open_spreadsheet()
                ws = ensure_worksheet(spread, "orders", ORDERS_HEADERS)
                rows = [[r["timestamp_iso"], r["date_il"], r["product_he"], r["size"], r["quantity_units"]]
                        for r in st.session_state.temp_orders]
                append_records(ws, rows)
                st.success("Заказ (события) сохранён в Google Sheets (лист 'orders').")
            except Exception as e:
                st.error(f"Ошибка записи в Google Sheets: {e}")
            # Google Drive
            try:
                order_folder_id, _ = resolve_drive_targets()
                link = drive_upload_txt(path, order_folder_id, get_drive_service())
                if link: st.success(f"Заказ загружен в Google Drive (order_lists). Открыть: {link}")
            except Exception as e:
                st.error(f"Ошибка загрузки в Google Drive: {e}")

with colB:
    if st.button("📦 Инвентаризация (TXT + Sheets + Drive)"):
        if not facts_agg: st.warning("Свод фактов пуст.")
        else:
            # TXT
            path = save_stocks_txt(facts_agg)
            if path:
                st.success(f"Инвентаризация сохранена: {os.path.basename(path)}")
                with open(path, "rb") as f:
                    st.download_button("⬇️ Скачать инвентаризацию (.txt)", data=f.read(),
                                       file_name=os.path.basename(path), mime="text/plain")
            # Google Sheets — сохраняем события
            try:
                spread = open_spreadsheet()
                ws = ensure_worksheet(spread, "facts", FACTS_HEADERS)
                rows = [[r["timestamp_iso"], r["date_il"], r["product_he"], r["size"], r["quantity_units"]]
                        for r in st.session_state.temp_facts]
                append_records(ws, rows)
                st.success("Инвентаризация (события) сохранена в Google Sheets (лист 'facts').")
            except Exception as e:
                st.error(f"Ошибка записи в Google Sheets: {e}")
            # Google Drive
            try:
                _, inventariz_folder_id = resolve_drive_targets()
                link = drive_upload_txt(path, inventariz_folder_id, get_drive_service())
                if link: st.success(f"Инвентаризация загружена в Google Drive (inventariz). Открыть: {link}")
            except Exception as e:
                st.error(f"Ошибка загрузки в Google Drive: {e}")

st.divider()
st.caption("Секреты: [sheets.milk_sheet_id], [gcp_service_account], опционально [drive.order_lists_id] и [drive.inventariz_id]. Таймзона: Asia/Jerusalem.")
