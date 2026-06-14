import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

APP_VERSION = "V10-APP-UI-MACHINE-CATEGORY"

DATA_FILE = Path("quality_alert.xlsx")
IMG_DIR = Path("images")
IMG_DIR.mkdir(exist_ok=True)

MACHINES = [
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
]

PROBLEM_CATEGORIES = [
    "กระดาษ",
    "การพิมพ์",
    "Slot",
    "Rotary-Diecut",
    "คัด",
    "กาว",
    "ตอก",
    "อื่นๆ",
]

AREAS = [
    "คัด",
    "กาว",
    "ตอก",
    "ขึ้นรูป",
    "อื่นๆ",
]

DEFECTS = {
    "กระดาษ": [
        "กระดาษยับ",
        "กระดาษโก่ง",
        "กระดาษชื้น",
        "กระดาษแตก",
        "กระดาษสีผิด",
        "กระดาษขาด",
        "อื่นๆ",
    ],
    "การพิมพ์": [
        "พิมพ์เลื่อน",
        "สีเพี้ยน",
        "สีจาง",
        "สีเข้ม",
        "หมึกเปื้อน",
        "Register ไม่ตรง",
        "พิมพ์ไม่ครบ",
        "อื่นๆ",
    ],
    "Slot": [
        "Slot เบี้ยว",
        "Slot ลึกเกิน",
        "Slot ตื้นเกิน",
        "Slot ขาด",
        "Slot ไม่ตรงตำแหน่ง",
        "อื่นๆ",
    ],
    "Rotary-Diecut": [
        "Diecut ไม่ขาด",
        "Diecut ขาดเกิน",
        "บากแตก",
        "บากเบี้ยว",
        "ล็อคไม่เข้า",
        "รอยกดไม่ชัด",
        "อื่นๆ",
    ],
    "คัด": [
        "งานเปื้อน",
        "งานขาด",
        "รอยขีดข่วน",
        "พิมพ์เลื่อน",
        "คัดปน",
        "อื่นๆ",
    ],
    "กาว": [
        "กาวไม่ติด",
        "กาวล้น",
        "กาวเปื้อน",
        "ประกบเบี้ยว",
        "กาวแห้ง",
        "อื่นๆ",
    ],
    "ตอก": [
        "ตอกหลุด",
        "ตอกไม่ครบ",
        "ตอกเบี้ยว",
        "ตอกผิดตำแหน่ง",
        "ตอกทะลุ",
        "อื่นๆ",
    ],
    "อื่นๆ": ["อื่นๆ"],
}

IMPACT_LEVELS = ["คัด", "กาว", "ขึ้นรูป", "ลูกค้า"]
SEVERITY_LIST = ["ต่ำ", "กลาง", "สูง"]
COST_PER_SHEET = 2.5


def load_data():
    if DATA_FILE.exists():
        try:
            df = pd.read_excel(DATA_FILE)
        except Exception:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    required_cols = {
        "วันที่": "",
        "เวลา": "",
        "ผู้แจ้ง": "",
        "เครื่อง": "",
        "หมวดปัญหา": "",
        "จุดที่พบ": "",
        "หน่วยงาน": "",
        "อาการ": "",
        "จำนวน": 0,
        "หลุดถึง": "",
        "ระดับ": "",
        "มูลค่าป้องกัน": 0,
        "รูปภาพ": "",
        "รายละเอียด": "",
        "สถานะ": "Open",
    }

    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default

    # migrate old department data
    if "หน่วยงาน" in df.columns:
        df["จุดที่พบ"] = df["จุดที่พบ"].astype(str).replace("nan", "")
        old_area_mask = df["จุดที่พบ"].astype(str).str.strip() == ""
        df.loc[old_area_mask, "จุดที่พบ"] = df.loc[old_area_mask, "หน่วยงาน"]

    df["เครื่อง"] = df["เครื่อง"].astype(str).replace("nan", "").replace("", "ไม่ระบุ")
    df["หมวดปัญหา"] = df["หมวดปัญหา"].astype(str).replace("nan", "").replace("", "อื่นๆ")
    df["จุดที่พบ"] = df["จุดที่พบ"].astype(str).replace("nan", "").replace("", "อื่นๆ")

    df["จำนวน"] = pd.to_numeric(df["จำนวน"], errors="coerce").fillna(0).astype(int)
    df["มูลค่าป้องกัน"] = pd.to_numeric(df["มูลค่าป้องกัน"], errors="coerce").fillna(0)

    mask = df["มูลค่าป้องกัน"] <= 0
    df.loc[mask, "มูลค่าป้องกัน"] = df.loc[mask, "จำนวน"] * COST_PER_SHEET

    return df


def save_data(df):
    df.to_excel(DATA_FILE, index=False)


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


def severity_color(severity):
    severity = str(severity).strip()
    if severity == "สูง":
        return "#ff2f4d", "สูง"
    if severity == "กลาง":
        return "#ffb020", "กลาง"
    return "#20c767", "ต่ำ"


def category_icon(cat):
    return {
        "กระดาษ": "📄",
        "การพิมพ์": "🎨",
        "Slot": "✂️",
        "Rotary-Diecut": "⚙️",
        "คัด": "🔍",
        "กาว": "🔥",
        "ตอก": "🔨",
        "อื่นๆ": "📌",
    }.get(cat, "📌")


def metric_card(title, value, icon, color):
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{color};">
            <div class="metric-icon">{icon}</div>
            <div>
                <div class="metric-title">{title}</div>
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
    machine = str(row.get("เครื่อง", "ไม่ระบุ"))
    category = str(row.get("หมวดปัญหา", "อื่นๆ"))
    area = str(row.get("จุดที่พบ", "อื่นๆ"))
    defect = str(row.get("อาการ", ""))
    qty = safe_int(row.get("จำนวน", 0))
    impact = str(row.get("หลุดถึง", ""))
    severity = str(row.get("ระดับ", ""))
    value = safe_int(row.get("มูลค่าป้องกัน", 0))
    img_path = str(row.get("รูปภาพ", "")).strip()

    color, sev_text = severity_color(severity)
    img64 = image_to_base64(img_path)

    if img64:
        img_html = f'<img class="thumb" src="data:image/jpeg;base64,{img64}" />'
    else:
        img_html = f'<div class="thumb empty-thumb">{category_icon(category)}</div>'

    st.markdown(
        f"""
        <div class="list-card">
            <div class="list-bar" style="background:{color};">{time[:5]}</div>
            <div class="list-content">
                <div class="list-top">
                    <div>
                        <div class="list-title">{defect}</div>
                        <div class="list-sub">{machine} • {category_icon(category)} {category} • จุด {area}</div>
                    </div>
                    <div class="qty-badge">{qty:,} ใบ</div>
                </div>
                <div class="list-foot">👤 {reporter} • หลุดถึง {impact} • 💰 {value:,} บาท</div>
            </div>
            {img_html}
            <div class="sev-chip" style="background:{color};">ระดับ {sev_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rank_card(rank, name, machine, qty, cases):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    st.markdown(
        f"""
        <div class="rank-card">
            <div class="rank-medal">{medal}</div>
            <div class="rank-avatar">👤</div>
            <div class="rank-info">
                <div class="rank-name">{name}</div>
                <div class="rank-sub">{machine} • {cases:,} เคส</div>
            </div>
            <div class="rank-score">{qty:,}<span> ใบ</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def simple_rank(title, sub, score, color="#ff2f4d", no="1"):
    st.markdown(
        f"""
        <div class="simple-rank">
            <div class="simple-no" style="background:{color};">{no}</div>
            <div>
                <div class="simple-title">{title}</div>
                <div class="simple-sub">{sub}</div>
            </div>
            <div class="simple-score">{score}</div>
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
        radial-gradient(circle at top left, rgba(29, 78, 216, .22), transparent 32%),
        radial-gradient(circle at top right, rgba(255, 47, 77, .16), transparent 32%),
        linear-gradient(180deg, #f4f8ff 0%, #edf5ff 54%, #ffffff 100%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 760px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.app-frame {
    background: rgba(255, 255, 255, .78);
    border: 1px solid rgba(255,255,255,.95);
    border-radius: 32px;
    padding: 16px;
    box-shadow: 0 28px 70px rgba(15, 23, 42, .14);
    backdrop-filter: blur(18px);
}

.hero {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 14px;
}

.logo {
    width: 68px;
    height: 68px;
    border-radius: 24px;
    background: linear-gradient(145deg, #ff3154, #e11d48);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 38px;
    box-shadow: inset 0 4px 0 rgba(255,255,255,.25), 0 18px 38px rgba(225, 29, 72, .30);
}

.brand-title {
    font-size: 41px;
    line-height: .92;
    font-weight: 1000;
    color: #071f52;
    letter-spacing: -1.5px;
}

.brand-title span {
    color: #ff2f4d;
}

.brand-sub {
    margin-top: 6px;
    font-size: 15px;
    font-weight: 900;
    color: #263b60;
}

.top-actions {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 9px;
}

.action {
    background: linear-gradient(180deg, #ffffff, #f7fbff);
    border: 1px solid #dbeafe;
    border-radius: 19px;
    text-align: center;
    padding: 10px 5px;
    box-shadow: 0 10px 22px rgba(15,23,42,.055);
}

.action-icon {
    width: 42px;
    height: 42px;
    margin: 0 auto 6px auto;
    border-radius: 999px;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.action-text {
    color: #0f172a;
    font-size: 13px;
    font-weight: 1000;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 7px;
    margin-top: 14px;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: rgba(255,255,255,.86);
    border: 1px solid #dbeafe;
    border-radius: 999px;
    padding: 8px 11px;
    box-shadow: 0 8px 17px rgba(15,23,42,.05);
}

div[data-testid="stTabs"] button {
    font-size: 15px;
    font-weight: 1000;
}

.form-phone {
    background: #ffffff;
    border-radius: 30px;
    overflow: hidden;
    margin-top: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 24px 55px rgba(15,23,42,.13);
}

.phone-top {
    background: linear-gradient(135deg, #ff2f4d, #d91f3d);
    padding: 18px;
    color: white;
    display: flex;
    gap: 12px;
    align-items: center;
}

.phone-icon {
    width: 48px;
    height: 48px;
    border-radius: 17px;
    background: rgba(255,255,255,.20);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}

.phone-title {
    font-size: 24px;
    line-height: 1.1;
    font-weight: 1000;
}

.phone-sub {
    font-size: 13px;
    font-weight: 800;
    opacity: .94;
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
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #f8fafc !important;
    border: 1px solid #dbeafe !important;
    border-radius: 16px !important;
    min-height: 46px;
}

.stRadio > div {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 7px 10px;
}

div[data-testid="stExpander"] {
    border-radius: 18px !important;
    border: 1px dashed #93c5fd !important;
    background: linear-gradient(180deg, #ffffff, #f8fbff) !important;
}

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #ff3154, #dc2626 75%, #b91c1c) !important;
    color: white !important;
    height: 62px;
    border-radius: 18px !important;
    font-size: 22px !important;
    font-weight: 1000 !important;
    border: 0 !important;
    box-shadow: 0 16px 36px rgba(239,35,60,.32);
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
    box-shadow: 0 14px 30px rgba(34,197,94,.30);
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

.list-card {
    position: relative;
    display: grid;
    grid-template-columns: 58px 1fr 72px;
    gap: 10px;
    align-items: center;
    background: rgba(255,255,255,.94);
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 11px;
    box-shadow: 0 13px 31px rgba(15,23,42,.075);
    margin-bottom: 10px;
}

.list-bar {
    min-height: 82px;
    color: white;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.list-top {
    display: flex;
    justify-content: space-between;
    gap: 8px;
}

.list-title {
    color: #111827;
    font-size: 18px;
    font-weight: 1000;
}

.list-sub,
.list-foot {
    color: #475569;
    font-size: 13px;
    font-weight: 800;
    margin-top: 3px;
}

.qty-badge {
    color: #16a34a;
    font-size: 16px;
    font-weight: 1000;
    white-space: nowrap;
}

.thumb {
    width: 66px;
    height: 66px;
    border-radius: 16px;
    object-fit: cover;
    border: 1px solid #e5e7eb;
}

.empty-thumb {
    background: linear-gradient(180deg, #f8fafc, #eef2ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
}

.sev-chip {
    position: absolute;
    right: 12px;
    top: 7px;
    color: white;
    border-radius: 999px;
    padding: 3px 8px;
    font-size: 11px;
    font-weight: 1000;
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
    box-shadow: 0 13px 31px rgba(15,23,42,.075);
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

.metric-title {
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
.simple-rank {
    background: rgba(255,255,255,.94);
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 13px;
    display: grid;
    align-items: center;
    gap: 10px;
    box-shadow: 0 13px 31px rgba(15,23,42,.075);
    margin-bottom: 10px;
}

.rank-card {
    grid-template-columns: 48px 42px 1fr auto;
}

.rank-medal {
    width: 43px;
    height: 43px;
    border-radius: 999px;
    background: #fff7ed;
    border: 1px solid #fed7aa;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 1000;
}

.rank-avatar {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    background: #e0f2fe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
}

.rank-name,
.simple-title {
    color: #111827;
    font-size: 16px;
    font-weight: 1000;
}

.rank-sub,
.simple-sub {
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
}

.rank-score,
.simple-score {
    color: #16a34a;
    font-size: 20px;
    font-weight: 1000;
    text-align: right;
}

.rank-score span {
    color: #64748b;
    font-size: 12px;
}

.simple-rank {
    grid-template-columns: 44px 1fr auto;
}

.simple-no {
    color: white;
    width: 38px;
    height: 38px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 1000;
}

.qr-box {
    background: rgba(255,255,255,.94);
    border: 1px solid #dbeafe;
    border-radius: 24px;
    padding: 15px;
    box-shadow: 0 13px 31px rgba(15,23,42,.075);
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

@media (max-width: 640px) {
    .brand-title { font-size: 34px; }
    .logo { width: 58px; height: 58px; font-size: 32px; }
    .top-actions { grid-template-columns: 1fr 1fr; }
    .metric-grid, .success-grid { grid-template-columns: 1fr; }
    .list-card { grid-template-columns: 54px 1fr 62px; }
    .thumb { width: 58px; height: 58px; }
    .rank-card { grid-template-columns: 43px 38px 1fr; }
    .rank-score { grid-column: 3; text-align: left; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="app-frame">', unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="color:#94a3b8;font-size:12px;font-weight:900;margin-bottom:8px;">{APP_VERSION}</div>
    <div class="hero">
        <div class="logo">🚨</div>
        <div>
            <div class="brand-title">QUALITY <span>ALERT</span></div>
            <div class="brand-sub">ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด</div>
        </div>
    </div>
    <div class="top-actions">
        <div class="action"><div class="action-icon">🏭</div><div class="action-text">เลือกเครื่อง</div></div>
        <div class="action"><div class="action-icon">📂</div><div class="action-text">หมวดปัญหา</div></div>
        <div class="action"><div class="action-icon">🔍</div><div class="action-text">อาการ</div></div>
        <div class="action"><div class="action-icon">📨</div><div class="action-text">ส่งแจ้งเตือน</div></div>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

tab_alert, tab_latest, tab_dashboard, tab_qr = st.tabs(
    ["🚨 แจ้งปัญหา", "📋 ล่าสุด", "📊 Dashboard", "🔗 QR"]
)

with tab_alert:
    st.markdown('<div class="form-phone">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="phone-top">
            <div class="phone-icon">🚨</div>
            <div>
                <div class="phone-title">แจ้งเตือนปัญหาคุณภาพ</div>
                <div class="phone-sub">เลือกเครื่อง → หมวดปัญหา → อาการ → ส่ง</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("alert_form", clear_on_submit=True):
        st.markdown('<div class="form-body">', unsafe_allow_html=True)

        reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")

        machine = st.selectbox("🏭 เครื่อง", MACHINES, index=0)

        category = st.selectbox("📂 หมวดปัญหา", PROBLEM_CATEGORIES, index=0)

        area = st.selectbox("📍 จุดที่พบ", AREAS, index=0)

        defect = st.selectbox("🔍 อาการที่พบ", DEFECTS[category])

        qty = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, step=1)

        impact = st.radio("⚠️ ถ้าไม่เจอจะหลุดถึง", IMPACT_LEVELS, horizontal=True)

        severity = st.radio("🚦 ระดับความรุนแรง", SEVERITY_LIST, horizontal=True)

        note = st.text_area(
            "📝 รายละเอียดเพิ่มเติม",
            placeholder="เช่น จุดที่พบ / สาเหตุคร่าวๆ / วิธีป้องกันเบื้องต้น",
        )

        image = None
        upload_image = None

        with st.expander("📷 เพิ่มรูปภาพ / ถ่ายภาพประกอบ (ไม่บังคับ)", expanded=False):
            image = st.camera_input("📷 แตะเพื่อถ่ายภาพ")
            upload_image = st.file_uploader(
                "หรือเลือกภาพจากเครื่อง",
                type=["jpg", "jpeg", "png"],
            )

        submitted = st.form_submit_button("🚨 ส่งแจ้งเตือน")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        if not reporter.strip():
            st.error("กรุณาใส่ชื่อผู้แจ้ง")
            st.stop()

        now = datetime.now()
        img_path = ""

        final_image = image if image is not None else upload_image

        if final_image is not None:
            img_name = f"{now.strftime('%Y%m%d_%H%M%S')}_{machine}.jpg"
            img_path = IMG_DIR / img_name
            with open(img_path, "wb") as f:
                f.write(final_image.getbuffer())

        damage_value = int(qty) * COST_PER_SHEET

        new_row = {
            "วันที่": now.strftime("%d/%m/%Y"),
            "เวลา": now.strftime("%H:%M:%S"),
            "ผู้แจ้ง": reporter.strip(),
            "เครื่อง": machine,
            "หมวดปัญหา": category,
            "จุดที่พบ": area,
            "หน่วยงาน": area,
            "อาการ": defect,
            "จำนวน": int(qty),
            "หลุดถึง": impact,
            "ระดับ": severity,
            "มูลค่าป้องกัน": damage_value,
            "รูปภาพ": str(img_path),
            "รายละเอียด": note,
            "สถานะ": "Open",
        }

        df = load_data()
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        save_data(df)

        reporter_df = df[df["ผู้แจ้ง"].astype(str).str.strip() != ""].copy()
        reporter_df["ผู้แจ้ง"] = reporter_df["ผู้แจ้ง"].astype(str).str.strip()
        rank_text = "-"

        if not reporter_df.empty:
            rank_df = (
                reporter_df.groupby("ผู้แจ้ง")["จำนวน"]
                .sum()
                .reset_index()
                .rename(columns={"จำนวน": "จำนวนใบ"})
                .sort_values("จำนวนใบ", ascending=False)
                .reset_index(drop=True)
            )
            hit = rank_df.index[rank_df["ผู้แจ้ง"] == reporter.strip()].tolist()
            if hit:
                rank_text = f"#{hit[0] + 1}"

        st.markdown(
            f"""
            <div class="success-card">
                <div class="success-check">✓</div>
                <div class="success-title">แจ้งเตือนสำเร็จ!</div>
                <div class="success-sub">บันทึกข้อมูลแล้ว ขอบคุณที่ช่วยป้องกันงานเสีย</div>
                <div class="success-grid">
                    <div class="success-box">
                        <div class="success-label">เครื่อง</div>
                        <div class="success-value">{machine}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">หมวดปัญหา</div>
                        <div class="success-value">{category_icon(category)} {category}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">ป้องกันได้</div>
                        <div class="success-value">{int(qty):,} ใบ</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">อันดับของคุณ</div>
                        <div class="success-value">{rank_text}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.balloons()

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
    st.markdown('<div class="section-title">📊 Dashboard หัวหน้างาน</div>', unsafe_allow_html=True)
    df = load_data()

    if df.empty:
        st.info("ยังไม่มีข้อมูล")
    else:
        df_dash = df.copy()
        df_dash["จำนวน"] = pd.to_numeric(df_dash["จำนวน"], errors="coerce").fillna(0).astype(int)
        df_dash["มูลค่าป้องกัน"] = pd.to_numeric(df_dash["มูลค่าป้องกัน"], errors="coerce").fillna(0)

        total_cases = len(df_dash)
        total_qty = int(df_dash["จำนวน"].sum())
        total_value = int(df_dash["มูลค่าป้องกัน"].sum())
        total_reporters = (
            df_dash["ผู้แจ้ง"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
        )

        st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
        metric_card("แจ้งทั้งหมด", f"{total_cases:,} เคส", "🔔", "#ff2f4d")
        metric_card("ป้องกันได้", f"{total_qty:,} ใบ", "🛡️", "#20c767")
        metric_card("ผู้มีส่วนร่วม", f"{total_reporters:,} คน", "👥", "#2563eb")
        metric_card("มูลค่าป้องกัน", f"{total_value:,} บาท", "💰", "#ffb020")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🏭 Top เครื่องที่พบปัญหา</div>', unsafe_allow_html=True)
        machine_df = df_dash[["เครื่อง", "จำนวน"]].copy()
        machine_df["เครื่อง"] = machine_df["เครื่อง"].astype(str).str.strip().replace("", "ไม่ระบุ")
        machine_qty = machine_df.groupby("เครื่อง")["จำนวน"].sum().reset_index().rename(columns={"จำนวน": "จำนวนใบ"})
        machine_case = machine_df.groupby("เครื่อง").size().reset_index(name="จำนวนเคส")
        machine_top = pd.merge(machine_qty, machine_case, on="เครื่อง", how="left")
        machine_top["จำนวนใบ"] = pd.to_numeric(machine_top["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
        machine_top = machine_top.nlargest(5, "จำนวนใบ").reset_index(drop=True)
        for i, row in machine_top.iterrows():
            simple_rank(str(row["เครื่อง"]), f"{int(row['จำนวนเคส']):,} เคส", f"{int(row['จำนวนใบ']):,} ใบ", "#2563eb", str(i + 1))

        st.markdown('<div class="section-title">📂 Top หมวดปัญหา</div>', unsafe_allow_html=True)
        cat_df = df_dash[["หมวดปัญหา", "จำนวน"]].copy()
        cat_df["หมวดปัญหา"] = cat_df["หมวดปัญหา"].astype(str).str.strip().replace("", "อื่นๆ")
        cat_qty = cat_df.groupby("หมวดปัญหา")["จำนวน"].sum().reset_index().rename(columns={"จำนวน": "จำนวนใบ"})
        cat_case = cat_df.groupby("หมวดปัญหา").size().reset_index(name="จำนวนเคส")
        cat_top = pd.merge(cat_qty, cat_case, on="หมวดปัญหา", how="left")
        cat_top["จำนวนใบ"] = pd.to_numeric(cat_top["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
        cat_top = cat_top.nlargest(5, "จำนวนใบ").reset_index(drop=True)
        for i, row in cat_top.iterrows():
            simple_rank(f"{category_icon(row['หมวดปัญหา'])} {row['หมวดปัญหา']}", f"{int(row['จำนวนเคส']):,} เคส", f"{int(row['จำนวนใบ']):,} ใบ", "#ff2f4d", str(i + 1))

        st.markdown('<div class="section-title">🏆 Top 5 ผู้มีส่วนร่วม</div>', unsafe_allow_html=True)

        reporter_df = df_dash[["ผู้แจ้ง", "เครื่อง", "จำนวน"]].copy()
        reporter_df["ผู้แจ้ง"] = reporter_df["ผู้แจ้ง"].astype(str).str.strip()
        reporter_df = reporter_df[reporter_df["ผู้แจ้ง"] != ""]

        if reporter_df.empty:
            st.info("ยังไม่มีข้อมูลผู้แจ้ง")
        else:
            top_qty = (
                reporter_df.groupby("ผู้แจ้ง")["จำนวน"]
                .sum()
                .reset_index()
                .rename(columns={"จำนวน": "จำนวนใบ"})
            )

            top_case = reporter_df.groupby("ผู้แจ้ง").size().reset_index(name="จำนวนเคส")

            top_machine = (
                reporter_df.groupby("ผู้แจ้ง")["เครื่อง"]
                .agg(lambda x: str(x.dropna().iloc[-1]) if len(x.dropna()) else "")
                .reset_index()
            )

            top = pd.merge(top_qty, top_case, on="ผู้แจ้ง", how="left")
            top = pd.merge(top, top_machine, on="ผู้แจ้ง", how="left")
            top["จำนวนใบ"] = pd.to_numeric(top["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
            top["จำนวนเคส"] = pd.to_numeric(top["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
            top = top.nlargest(5, "จำนวนใบ").reset_index(drop=True)

            for i, row in top.iterrows():
                rank_card(
                    i + 1,
                    str(row["ผู้แจ้ง"]),
                    str(row.get("เครื่อง", "")),
                    int(row["จำนวนใบ"]),
                    int(row["จำนวนเคส"]),
                )

with tab_qr:
    st.markdown('<div class="qr-box">', unsafe_allow_html=True)
    st.markdown('<div style="font-size:20px;font-weight:1000;color:#0f172a;margin-bottom:8px;">🔗 ลิงก์สำหรับทำ QR จุดเดียว</div>', unsafe_allow_html=True)
    base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"
    st.code(base_url)
    st.markdown(
        """
        <div class="help-card">
        ใช้ QR จุดเดียว เปิดมาเลือกเครื่อง / หมวดปัญหา / จุดที่พบ จาก Dropdown ได้เลย
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
