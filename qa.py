import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64
import requests
import json
from io import StringIO

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

APP_VERSION = "V19-FIX-DETAIL-CAMERA-UI"

SHEET_ID = "1cCKqj56MBas_v5c2dR1ryCNa9c4YulxtsKPbsz-7PUY"
SHEET_GID = "0"
GOOGLE_SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={SHEET_GID}"
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbzoB7Isb-v-J4JgvkYBfiI7wJJlOPQx-flS1aCzGOxyOUMa4HnEzyxfCJdBhdbCQRLR/exec"

IMG_DIR = Path("images")
IMG_DIR.mkdir(exist_ok=True)

MACHINES = [
    "ลูกฟูก",
    "F115-IBIS",
    "F84-EVOL",
    "F84-EVOL2",
    "F96",
    "F96/2",
    "F110",
    "F130",
    "4FP96",
    "ASAHI",
    "BOBST",
    "งานคัด",
    "งานกาว",
    "งานตอก",
    "ขึ้นรูป",
]

PROBLEMS = [
    "กระดาษพอง-ล่อน",
    "กระดาษยับ",
    "กระดาษไม่เต็มลอน",
    "พิมพ์เลื่อน",
    "พิมพ์เลอะ,ตัน,เบลอ",
    "พิมพ์ไม่ติด",
    "ร่องกาวเบี้ยว",
    "ร่องกาวชิด-ห่าง",
    "กล่องฝาเกย-ห่าง,ขึ้นรูปไม่ได้",
    "Slot ลึก",
    "กาวเลอะ",
    "กาวไม่ติด",
    "ทับรอยแตกนอก",
    "ทับรอยแตกใน",
    "เศษ Rotary-Diecut ตัดไม่ขาด",
    "กระดาษเปื้อน",
    "ชำรุดจากจัดส่ง",
    "อื่นๆ (พิมพ์เพิ่มเติมได้)",
]

SEVERITY_LIST = ["ต่ำ", "กลาง", "สูง"]
COST_PER_SHEET = 2.5


def fix_thai_text(value):
    """แก้ภาษาไทยเพี้ยนแบบ à¸ จาก CSV encoding ของ Google Sheet"""
    if pd.isna(value):
        return ""

    text = str(value).replace("nan", "").replace("None", "").strip()

    # ถ้าเป็น mojibake เช่น à¸à¸£ ให้ถอดกลับเป็น UTF-8
    if "à¸" in text or "à¹" in text or "Â" in text:
        try:
            text = text.encode("latin1").decode("utf-8")
        except Exception:
            pass

    return text.strip()


def load_data():
    required_cols = [
        "วันที่",
        "เวลา",
        "ผู้แจ้ง",
        "เครื่อง/จุดงาน",
        "ปัญหาที่พบ",
        "จำนวน",
        "ระดับ",
        "ขนาดเหตุการณ์",
        "คะแนน",
        "มูลค่าป้องกัน",
        "รูปภาพ",
        "สถานะ",
    ]

    try:
        response = requests.get(GOOGLE_SHEET_CSV_URL, timeout=10)
        response.raise_for_status()

        # สำคัญ: บังคับ UTF-8 ไม่งั้นภาษาไทยจะกลายเป็น à¸...
        csv_text = response.content.decode("utf-8-sig", errors="replace").strip()

        if not csv_text:
            df = pd.DataFrame(columns=required_cols)
        else:
            df = pd.read_csv(StringIO(csv_text), dtype=str, encoding="utf-8")

    except Exception:
        df = pd.DataFrame(columns=required_cols)

    # ล้างชื่อหัวตาราง กันช่องว่าง / BOM / อักขระแปลก
    df.columns = [fix_thai_text(c).replace("\ufeff", "") for c in df.columns]

    # ถ้าหัวคอลัมน์อ่านเพี้ยน ให้อิงตามตำแหน่ง A-L ของชีตแทน
    must_have = {"วันที่", "เวลา", "ผู้แจ้ง", "เครื่อง/จุดงาน", "ปัญหาที่พบ", "คะแนน"}
    if not must_have.issubset(set(df.columns)):
        df = df.iloc[:, :12].copy()
        df.columns = required_cols[:len(df.columns)]

    # เติมคอลัมน์ที่ขาด
    for col in required_cols:
        if col not in df.columns:
            df[col] = ""

    df = df[required_cols].copy()

    # ล้างข้อความ + ซ่อมภาษาไทยเพี้ยนทุกช่อง
    text_cols = [
        "วันที่",
        "เวลา",
        "ผู้แจ้ง",
        "เครื่อง/จุดงาน",
        "ปัญหาที่พบ",
        "ระดับ",
        "ขนาดเหตุการณ์",
        "รูปภาพ",
        "สถานะ",
    ]
    for col in text_cols:
        df[col] = df[col].apply(fix_thai_text)

    df["เครื่อง/จุดงาน"] = df["เครื่อง/จุดงาน"].replace("", "ไม่ระบุ")
    df["ปัญหาที่พบ"] = df["ปัญหาที่พบ"].replace("", "ไม่ระบุ")
    df["สถานะ"] = df["สถานะ"].replace("", "Open")

    # แปลงตัวเลข
    df["จำนวน"] = pd.to_numeric(df["จำนวน"], errors="coerce").fillna(0).astype(int)
    df["คะแนน"] = pd.to_numeric(df["คะแนน"], errors="coerce").fillna(0).astype(int)
    df["มูลค่าป้องกัน"] = pd.to_numeric(df["มูลค่าป้องกัน"], errors="coerce").fillna(0)

    # แก้ข้อมูลเก่า ถ้าไม่มีคะแนนแต่มีข้อมูลจริง ให้คะแนนเริ่มต้น 1
    has_real_data = (
        df["ผู้แจ้ง"].astype(str).str.strip().ne("")
        | df["เครื่อง/จุดงาน"].astype(str).str.strip().ne("ไม่ระบุ")
        | df["ปัญหาที่พบ"].astype(str).str.strip().ne("ไม่ระบุ")
    )
    df.loc[(df["คะแนน"] <= 0) & has_real_data, "คะแนน"] = 1

    # ถ้ามูลค่าป้องกันว่าง ให้คิดจากจำนวนใบ
    mask_value = df["มูลค่าป้องกัน"] <= 0
    df.loc[mask_value, "มูลค่าป้องกัน"] = df.loc[mask_value, "จำนวน"] * COST_PER_SHEET

    missing_size = df["ขนาดเหตุการณ์"].astype(str).str.strip() == ""
    df.loc[missing_size, "ขนาดเหตุการณ์"] = df.loc[missing_size, "จำนวน"].apply(get_event_size)

    return df


def save_to_google_sheet(row):
    payload = {
        "date": row["วันที่"],
        "time": row["เวลา"],
        "reporter": row["ผู้แจ้ง"],
        "machine": row["เครื่อง/จุดงาน"],
        "problem": row["ปัญหาที่พบ"],
        "qty": row["จำนวน"],
        "severity": row["ระดับ"],
        "event_size": row["ขนาดเหตุการณ์"],
        "score": row["คะแนน"],
        "value": row["มูลค่าป้องกัน"],
        "image": row["รูปภาพ"],
    }

    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            data=json.dumps(payload, ensure_ascii=False),
            headers={"Content-Type": "application/json"},
            timeout=15,
        )
        response.raise_for_status()
        return True, ""

    except Exception as e:
        return False, str(e)

def safe_int(value):
    try:
        value = pd.to_numeric(value, errors="coerce")
        if pd.isna(value):
            return 0
        return int(value)
    except Exception:
        return 0


def image_to_base64(path):
    try:
        p = Path(str(path))
        if not p.exists():
            return ""
        return base64.b64encode(p.read_bytes()).decode("utf-8")
    except Exception:
        return ""


def severity_style(severity):
    severity = str(severity).strip()
    if "สูง" in severity or "Critical" in severity:
        return "#ef233c", "🚑", "ระดับสูง"
    if "กลาง" in severity or "Attention" in severity:
        return "#f59e0b", "🚔", "ระดับกลาง"
    return "#22c55e", "💡", "ระดับต่ำ"


def get_event_size(qty):
    qty = safe_int(qty)
    if qty <= 50:
        return "🔹 น้อย"
    if qty <= 200:
        return "🔸 ปานกลาง"
    if qty <= 500:
        return "🔶 มาก"
    return "🔥 วิกฤต"


def metric_card(label, value, icon, color):
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{color};">
            <div class="metric-icon">{icon}</div>
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def latest_card(row):
    date = str(row.get("วันที่", ""))
    time = str(row.get("เวลา", ""))
    reporter = str(row.get("ผู้แจ้ง", ""))
    machine = str(row.get("เครื่อง/จุดงาน", "ไม่ระบุ"))
    problem = str(row.get("ปัญหาที่พบ", row.get("อาการ", "")))
    qty = safe_int(row.get("จำนวน", 0))
    severity = str(row.get("ระดับ", ""))
    value = safe_int(row.get("มูลค่าป้องกัน", 0))
    score = safe_int(row.get("คะแนน", 0))
    event_size = str(row.get("ขนาดเหตุการณ์", get_event_size(qty)))
    img_path = str(row.get("รูปภาพ", "")).strip()

    color, icon, severity_text = severity_style(severity)
    img64 = image_to_base64(img_path)

    if img64:
        img_html = f'<img class="thumb" src="data:image/jpeg;base64,{img64}" />'
    else:
        img_html = f'<div class="thumb empty-thumb">{icon}</div>'

    st.markdown(
        f"""
        <div class="latest-card">
            <div class="time-box" style="background:{color};">{time[:5]}</div>
            <div class="latest-main">
                <div class="latest-title">{icon} {severity_text}</div>
                <div class="latest-sub"><b>{problem}</b> • {machine}</div>
                <div class="latest-sub">{event_size} • {qty:,} ใบ</div>
                <div class="latest-sub">👤 {reporter} • {date} • 🏆 {score} คะแนน</div>
            </div>
            {img_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def rank_card(rank, name, qty, cases):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    st.markdown(
        f"""
        <div class="rank-card">
            <div class="rank-medal">{medal}</div>
            <div class="rank-info">
                <div class="rank-name">{name}</div>
                <div class="rank-sub">อ้างอิง {cases:,}</div>
            </div>
            <div class="rank-score">{qty:,}<span></span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def problem_card(rank, problem, qty, cases):
    st.markdown(
        f"""
        <div class="problem-card">
            <div class="problem-no">{rank}</div>
            <div>
                <div class="problem-name">{problem}</div>
                <div class="problem-sub">{cases:,} เคส</div>
            </div>
            <div class="problem-score">{qty:,} ใบ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700;800;900&display=swap');

* {
    font-family: 'Noto Sans Thai', sans-serif !important;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(37, 99, 235, .18), transparent 34%),
        radial-gradient(circle at top right, rgba(236, 72, 153, .13), transparent 34%),
        radial-gradient(circle at bottom right, rgba(34, 197, 94, .10), transparent 30%),
        linear-gradient(180deg, #f8fbff 0%, #eef5ff 48%, #fff7fb 100%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 720px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.app-header {
    background:
        linear-gradient(135deg, rgba(255,255,255,.96), rgba(248,250,252,.90));
    border: 1px solid rgba(226, 232, 240, .95);
    border-radius: 32px;
    padding: 20px;
    box-shadow: 0 26px 70px rgba(15, 23, 42, .13);
    margin-bottom: 14px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo {
    width: 66px;
    height: 66px;
    border-radius: 24px;
    background: linear-gradient(145deg, #082f7a, #2563eb 58%, #ef233c);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 36px;
    box-shadow: 0 14px 32px rgba(7, 31, 82, .25);
}

.title {
    font-size: 40px;
    line-height: .92;
    font-weight: 1000;
    color: #071f52;
    letter-spacing: -1.3px;
}

.title span {
    color: #ef233c;
}

.subtitle {
    margin-top: 6px;
    color: #334155;
    font-size: 15px;
    font-weight: 850;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px;
    margin-top: 10px;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: rgba(255,255,255,.90);
    border: 1px solid #dbeafe;
    border-radius: 999px;
    padding: 8px 12px;
    box-shadow: 0 7px 16px rgba(15, 23, 42, .05);
}

div[data-testid="stTabs"] button {
    font-size: 15px;
    font-weight: 1000;
}

.form-card {
    background: rgba(255,255,255,.96);
    border: 1px solid rgba(226,232,240,.95);
    border-radius: 32px;
    overflow: hidden;
    box-shadow: 0 26px 70px rgba(15, 23, 42, .13);
    margin-top: 12px;
}

.form-top {
    background: linear-gradient(135deg, #082f7a, #2563eb 62%, #ef233c);
    color: white;
    padding: 18px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.form-icon {
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: rgba(255,255,255,.16);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}

.form-title {
    font-size: 24px;
    line-height: 1.1;
    font-weight: 1000;
}

.form-sub {
    font-size: 13px;
    font-weight: 800;
    opacity: .9;
}

.form-body {
    padding: 16px 16px 5px 16px;
}

label {
    font-weight: 900 !important;
    color: #111827 !important;
}

.stTextInput input,
.stNumberInput input,
.stSelectbox div[data-baseweb="select"] > div {
    background: #f8fafc !important;
    border: 1px solid #dbeafe !important;
    border-radius: 16px !important;
    min-height: 48px;
}

.stRadio > div {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 7px 10px;
}



/* แยกปุ่มอัปโหลดให้ไม่ทับกัน */
div[data-testid="stFileUploader"] {
    background: linear-gradient(180deg, #ffffff, #f8fbff) !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 20px !important;
    padding: 12px !important;
    margin-bottom: 10px !important;
}

div[data-testid="stFileUploader"] section {
    background: #f1f5f9 !important;
    border: 1px dashed #93c5fd !important;
    border-radius: 18px !important;
    padding: 14px !important;
}

div[data-testid="stFileUploader"] button {
    border-radius: 14px !important;
    font-weight: 1000 !important;
}

div[data-testid="stExpander"] {
    border-radius: 18px !important;
    border: 1px dashed #93c5fd !important;
    background: linear-gradient(180deg, #ffffff, #f8fbff) !important;
}

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #ef233c, #dc2626 75%, #b91c1c) !important;
    color: white !important;
    height: 64px;
    border-radius: 19px !important;
    font-size: 22px !important;
    font-weight: 1000 !important;
    border: 0 !important;
    box-shadow: 0 16px 36px rgba(239, 35, 60, .30);
    margin-top: 8px;
}

.success-card {
    background: white;
    border: 1px solid #bbf7d0;
    border-radius: 28px;
    padding: 22px 17px;
    text-align: center;
    box-shadow: 0 18px 42px rgba(22,163,74,.14);
    margin: 14px 0;
}

.success-check {
    width: 92px;
    height: 92px;
    margin: 0 auto 12px auto;
    border-radius: 999px;
    background: linear-gradient(145deg, #22c55e, #16a34a);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 58px;
    font-weight: 1000;
}

.success-title {
    font-size: 29px;
    font-weight: 1000;
    color: #111827;
}

.success-sub {
    color: #64748b;
    font-size: 15px;
    font-weight: 850;
    margin: 4px 0 14px 0;
}

.success-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.success-box {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 13px;
}

.success-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
}

.success-value {
    color: #16a34a;
    font-size: 24px;
    font-weight: 1000;
}

.section-title {
    font-size: 24px;
    font-weight: 1000;
    color: #0f172a;
    margin: 18px 0 12px 0;
}

.latest-card {
    background: rgba(255,255,255,.94);
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 11px;
    display: grid;
    grid-template-columns: 58px 1fr 70px;
    gap: 10px;
    align-items: center;
    box-shadow: 0 13px 31px rgba(15, 23, 42, .075);
    margin-bottom: 10px;
}

.time-box {
    min-height: 76px;
    border-radius: 16px;
    color: white;
    font-size: 14px;
    font-weight: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.latest-title {
    color: #111827;
    font-size: 18px;
    font-weight: 1000;
}

.latest-sub {
    color: #475569;
    font-size: 13px;
    font-weight: 800;
    margin-top: 3px;
}

.thumb {
    width: 64px;
    height: 64px;
    border-radius: 16px;
    object-fit: cover;
    border: 1px solid #e5e7eb;
}

.empty-thumb {
    background: #f8fafc;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}

.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.metric-card {
    background: rgba(255,255,255,.94);
    border: 1px solid #e5e7eb;
    border-left: 7px solid var(--accent);
    border-radius: 22px;
    padding: 14px;
    display: flex;
    gap: 11px;
    align-items: center;
    box-shadow: 0 13px 31px rgba(15, 23, 42, .075);
}

.metric-icon {
    min-width: 48px;
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: var(--accent);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
}

.metric-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
}

.metric-value {
    color: #0f172a;
    font-size: 23px;
    font-weight: 1000;
    line-height: 1.08;
    margin-top: 4px;
}

.rank-card,
.problem-card {
    background: rgba(255,255,255,.94);
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 13px;
    display: grid;
    align-items: center;
    gap: 10px;
    box-shadow: 0 13px 31px rgba(15, 23, 42, .075);
    margin-bottom: 10px;
}

.rank-card {
    grid-template-columns: 48px 1fr auto;
}

.problem-card {
    grid-template-columns: 44px 1fr auto;
}

.rank-medal,
.problem-no {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 19px;
    font-weight: 1000;
}

.rank-name,
.problem-name {
    color: #111827;
    font-size: 16px;
    font-weight: 1000;
}

.rank-sub,
.problem-sub {
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
}

.rank-score {
    color: #16a34a;
    font-size: 20px;
    font-weight: 1000;
    text-align: right;
}

.rank-score span {
    color: #64748b;
    font-size: 12px;
}

.problem-score {
    color: #ef233c;
    font-size: 18px;
    font-weight: 1000;
    text-align: right;
}

.qr-box {
    background: rgba(255,255,255,.94);
    border: 1px solid #dbeafe;
    border-radius: 24px;
    padding: 15px;
    box-shadow: 0 13px 31px rgba(15, 23, 42, .075);
    margin-top: 12px;
}

.help-card {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 18px;
    padding: 13px;
    color: #1e3a8a;
    font-size: 14px;
    font-weight: 850;
    margin-top: 12px;
}

.mini-label {
    color: #0f172a;
    font-size: 15px;
    font-weight: 1000;
    margin: 10px 0 7px 2px;
}

div[data-testid="stFileUploader"] section {
    background: #f8fafc !important;
    border: 1px solid #dbeafe !important;
    border-radius: 18px !important;
    padding: 10px !important;
}

div[data-testid="stFileUploader"] button {
    border-radius: 999px !important;
    font-weight: 1000 !important;
}

textarea {
    background: #f8fafc !important;
    border: 1px solid #dbeafe !important;
    border-radius: 16px !important;
}

@media (max-width: 640px) {
    .title {
        font-size: 34px;
    }
    .logo {
        width: 58px;
        height: 58px;
        font-size: 32px;
    }
    .metric-grid,
    .success-grid {
        grid-template-columns: 1fr;
    }
    .latest-card {
        grid-template-columns: 54px 1fr 62px;
    }
    .thumb {
        width: 58px;
        height: 58px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="app-header">
    <div style="color:#94a3b8;font-size:12px;font-weight:900;margin-bottom:8px;">{APP_VERSION}</div>
    <div class="brand">
        <div class="logo">🚨</div>
        <div>
            <div class="title">QUALITY <span>ALERT</span></div>
            <div class="subtitle">แจ้งง่าย เห็นเร็ว ป้องกันก่อนเสีย</div>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

tab_alert, tab_latest, tab_dashboard, tab_qr = st.tabs(
    ["🚨 แจ้งปัญหา", "📋 ล่าสุด", "📊 แดชบอร์ด", "🔗 คิวอาร์"]
)

with tab_alert:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="form-top">
            <div class="form-icon">🚨</div>
            <div>
                <div class="form-title">แจ้งปัญหาหน้างาน</div>
                <div class="form-sub">เจออะไร • กี่ใบ • รุนแรงแค่ไหน</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("alert_form", clear_on_submit=True):
        st.markdown('<div class="form-body">', unsafe_allow_html=True)

        reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")

        machine = st.selectbox("🏭 เครื่อง/จุดงาน/จุดงาน", MACHINES, index=0)

        problem_select = st.selectbox("🔍 ปัญหาที่พบ", PROBLEMS, index=0)

        detail_problem = st.text_area(
            "✍️ อาการของเสียเพิ่มเติม",
            placeholder="เช่น ตอกเบี้ยว / ลวดตอกหัก, งอ / จุดอื่นๆ พิมพ์เพิ่มได้",
            height=92,
        )

        qty = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, step=1)

        severity = st.radio("🚦 ความรุนแรง", SEVERITY_LIST, horizontal=True)

        st.markdown('<div class="mini-label">📁 อัปโหลดภาพ (ไม่บังคับ)</div>', unsafe_allow_html=True)
        upload_image = st.file_uploader(
            "อัปโหลดภาพ",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed",
        )

        image = None
        with st.expander("📷 ถ่ายภาพ", expanded=False):
            image = st.camera_input("ถ่ายภาพ", label_visibility="collapsed")

        submitted = st.form_submit_button("🚨 ส่งแจ้งเตือน")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not reporter.strip():
            st.error("กรุณาใส่ชื่อผู้แจ้ง")
            st.stop()

        detail_problem = detail_problem.strip()
        if problem_select == "อื่นๆ (พิมพ์เพิ่มเติมได้)":
            problem = detail_problem
        else:
            problem = problem_select
            if detail_problem:
                problem = f"{problem_select} / {detail_problem}"

        if not problem.strip():
            st.error("กรุณาระบุปัญหาที่พบ")
            st.stop()

        now = datetime.now()
        img_path = ""

        final_image = image if image is not None else upload_image

        if final_image is not None:
            safe_machine = machine.replace("/", "-")
            img_name = f"{now.strftime('%Y%m%d_%H%M%S')}_{safe_machine}.jpg"
            img_path = IMG_DIR / img_name
            with open(img_path, "wb") as f:
                f.write(final_image.getbuffer())

        damage_value = int(qty) * COST_PER_SHEET

        score = 1
        if final_image is not None:
            score += 1
        if "กลาง" in severity:
            score += 1
        elif "สูง" in severity:
            score += 2

        event_size = get_event_size(qty)

        new_row = {
            "วันที่": now.strftime("%d/%m/%Y"),
            "เวลา": now.strftime("%H:%M:%S"),
            "ผู้แจ้ง": reporter.strip(),
            "เครื่อง/จุดงาน": machine,
            "ปัญหาที่พบ": problem,
            "อาการ": problem,
            "จำนวน": int(qty),
            "ระดับ": severity,
            "มูลค่าป้องกัน": damage_value,
            "รูปภาพ": str(img_path),
            "สถานะ": "เปิดเคส",
            "คะแนน": score,
            "ขนาดเหตุการณ์": event_size,
        }

        df_before = load_data()
        ok, err = save_to_google_sheet(new_row)

        if not ok:
            st.error(f"บันทึกลง Google Sheet ไม่สำเร็จ: {err}")
            st.stop()

        df = pd.concat([df_before, pd.DataFrame([new_row])], ignore_index=True)

        reporter_df = df[df["ผู้แจ้ง"].astype(str).str.strip() != ""].copy()
        reporter_df["ผู้แจ้ง"] = reporter_df["ผู้แจ้ง"].astype(str).str.strip()
        reporter_df["คะแนน"] = pd.to_numeric(reporter_df["คะแนน"], errors="coerce").fillna(0).astype(int)
        rank_text = "-"
        total_my_score = score

        if not reporter_df.empty:
            rank_df = (
                reporter_df.groupby("ผู้แจ้ง")["คะแนน"]
                .sum()
                .reset_index()
                .rename(columns={"คะแนน": "คะแนนรวม"})
                .sort_values("คะแนนรวม", ascending=False)
                .reset_index(drop=True)
            )
            hit = rank_df.index[rank_df["ผู้แจ้ง"] == reporter.strip()].tolist()
            if hit:
                rank_text = f"#{hit[0] + 1}"
                total_my_score = int(rank_df.loc[hit[0], "คะแนนรวม"])

        alert_color, alert_icon, alert_name = severity_style(severity)
        if "สูง" in severity:
            alert_message = "รับเรื่องแล้ว กรุณาตรวจสอบหน้างานทันที"
        elif "กลาง" in severity:
            alert_message = "รับทราบแล้ว โปรดเฝ้าระวังและติดตาม"
        else:
            alert_message = "รับข้อมูลเรียบร้อย ขอบคุณที่ช่วยป้องกันปัญหา"

        st.markdown(
            f"""
            <div class="success-card">
                <div class="success-check" style="background:{alert_color};">{alert_icon}</div>
                <div class="success-title">{alert_name}</div>
                <div class="success-sub">{alert_message}</div>
                <div class="success-grid">
                    <div class="success-box">
                        <div class="success-label">ปัญหา</div>
                        <div class="success-value">{problem}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">เครื่อง/จุดงาน</div>
                        <div class="success-value">{machine}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">ขนาดเหตุการณ์</div>
                        <div class="success-value">{event_size}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">คะแนนสะสม</div>
                        <div class="success-value">+{score} / {total_my_score}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.balloons()
        st.toast("✅ ส่งแจ้งเตือนสำเร็จ", icon="🚨")

with tab_latest:
    st.markdown('<div class="section-title">📋 รายการแจ้งเตือนล่าสุด</div>', unsafe_allow_html=True)
    df = load_data()

    if df.empty:
        st.info("ยังไม่มีข้อมูล")
    else:
        latest_df = df.tail(10).sort_index(ascending=False)
        for _, row in latest_df.iterrows():
            latest_card(row)

with tab_dashboard:
    st.markdown('<div class="section-title">📊 แดชบอร์ดหัวหน้างาน</div>', unsafe_allow_html=True)
    df = load_data()

    if df.empty:
        st.info("ยังไม่มีข้อมูล")
    else:
        df_dash = df.copy()
        df_dash["จำนวน"] = pd.to_numeric(df_dash["จำนวน"], errors="coerce").fillna(0).astype(int)
        df_dash["มูลค่าป้องกัน"] = pd.to_numeric(
            df_dash["มูลค่าป้องกัน"], errors="coerce"
        ).fillna(0)

        total_cases = len(df_dash)
        total_qty = int(df_dash["จำนวน"].sum())
        total_value = int(df_dash["มูลค่าป้องกัน"].sum())
        total_score = int(pd.to_numeric(df_dash["คะแนน"], errors="coerce").fillna(0).sum())
        total_reporters = (
            df_dash["ผู้แจ้ง"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        metric_card("แจ้งทั้งหมด", f"{total_cases:,} เคส", "🔔", "#ef233c")
        metric_card("ป้องกันได้", f"{total_qty:,} ใบ", "🛡️", "#22c55e")
        metric_card("ผู้มีส่วนร่วม", f"{total_reporters:,} คน", "👥", "#2563eb")
        metric_card("คะแนนรวม", f"{total_score:,} คะแนน", "🏆", "#f59e0b")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🏆 ผู้มีส่วนร่วมสูงสุด</div>', unsafe_allow_html=True)

        reporter_df = df_dash[["ผู้แจ้ง", "คะแนน"]].copy()
        reporter_df["ผู้แจ้ง"] = reporter_df["ผู้แจ้ง"].astype(str).str.strip()
        reporter_df["คะแนน"] = pd.to_numeric(reporter_df["คะแนน"], errors="coerce").fillna(0).astype(int)
        reporter_df = reporter_df[reporter_df["ผู้แจ้ง"] != ""]

        if reporter_df.empty:
            st.info("ยังไม่มีข้อมูลผู้แจ้ง")
        else:
            top_case = reporter_df.groupby("ผู้แจ้ง").size().reset_index(name="จำนวนเคส")
            top_score = (
                reporter_df.groupby("ผู้แจ้ง")["คะแนน"]
                .sum()
                .reset_index()
                .rename(columns={"คะแนน": "คะแนนรวม"})
            )
            top = pd.merge(top_case, top_score, on="ผู้แจ้ง", how="left")
            top["จำนวนเคส"] = pd.to_numeric(top["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
            top["คะแนนรวม"] = pd.to_numeric(top["คะแนนรวม"], errors="coerce").fillna(0).astype(int)
            top = top.nlargest(5, "จำนวนเคส").reset_index(drop=True)

            for i, row in top.iterrows():
                rank_card(
                    i + 1,
                    str(row["ผู้แจ้ง"]),
                    int(row["จำนวนเคส"]),
                    int(row["คะแนนรวม"]),
                )

        st.markdown('<div class="section-title">🚨 คะแนนความรุนแรงสูงสุด</div>', unsafe_allow_html=True)

        if reporter_df.empty:
            st.info("ยังไม่มีข้อมูลคะแนน")
        else:
            critical_top = (
                reporter_df.groupby("ผู้แจ้ง")["คะแนน"]
                .sum()
                .reset_index()
                .rename(columns={"คะแนน": "คะแนนรวม"})
            )
            critical_case = reporter_df.groupby("ผู้แจ้ง").size().reset_index(name="จำนวนเคส")
            critical_top = pd.merge(critical_top, critical_case, on="ผู้แจ้ง", how="left")
            critical_top["คะแนนรวม"] = pd.to_numeric(critical_top["คะแนนรวม"], errors="coerce").fillna(0).astype(int)
            critical_top["จำนวนเคส"] = pd.to_numeric(critical_top["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
            critical_top = critical_top.nlargest(5, "คะแนนรวม").reset_index(drop=True)

            for i, row in critical_top.iterrows():
                rank_card(
                    i + 1,
                    str(row["ผู้แจ้ง"]),
                    int(row["คะแนนรวม"]),
                    int(row["จำนวนเคส"]),
                )

        st.markdown('<div class="section-title">🔍 Top ปัญหาที่พบ</div>', unsafe_allow_html=True)

        problem_df = df_dash[["ปัญหาที่พบ", "จำนวน"]].copy()
        problem_df["ปัญหาที่พบ"] = problem_df["ปัญหาที่พบ"].astype(str).str.strip()
        problem_df = problem_df[problem_df["ปัญหาที่พบ"] != ""]

        if problem_df.empty:
            st.info("ยังไม่มีข้อมูลปัญหา")
        else:
            problem_qty = (
                problem_df.groupby("ปัญหาที่พบ")["จำนวน"]
                .sum()
                .reset_index()
                .rename(columns={"จำนวน": "จำนวนใบ"})
            )

            problem_case = (
                problem_df.groupby("ปัญหาที่พบ")
                .size()
                .reset_index(name="จำนวนเคส")
            )

            problem_top = pd.merge(problem_qty, problem_case, on="ปัญหาที่พบ", how="left")
            problem_top["จำนวนใบ"] = pd.to_numeric(
                problem_top["จำนวนใบ"], errors="coerce"
            ).fillna(0).astype(int)
            problem_top["จำนวนเคส"] = pd.to_numeric(
                problem_top["จำนวนเคส"], errors="coerce"
            ).fillna(0).astype(int)
            problem_top = problem_top.nlargest(5, "จำนวนใบ").reset_index(drop=True)

            for i, row in problem_top.iterrows():
                problem_card(
                    i + 1,
                    str(row["ปัญหาที่พบ"]),
                    int(row["จำนวนใบ"]),
                    int(row["จำนวนเคส"]),
                )

with tab_qr:
    st.markdown('<div class="qr-box">', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:20px;font-weight:1000;color:#0f172a;margin-bottom:8px;">🔗 ลิงก์สำหรับทำคิวอาร์จุดเดียว</div>',
        unsafe_allow_html=True,
    )
    base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"
    st.code(base_url)
    st.markdown(
        """
        <div class="help-card">
        ใช้ QR จุดเดียว เปิดมาเลือกเครื่อง/จุดงาน / ปัญหา / จำนวน / ความรุนแรง แล้วส่งได้ทันที บันทึกลง Google Sheet และเก็บคะแนนให้อัตโนมัติ
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
