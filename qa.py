import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

APP_VERSION = "V9-CLEAN-MOBILE-2000"

DATA_FILE = Path("quality_alert.xlsx")
IMG_DIR = Path("images")
IMG_DIR.mkdir(exist_ok=True)

DEPTS = ["ตอก", "คัด", "กาว", "ขึ้นรูป"]

DEPT_ICONS = {
    "ตอก": "🔨",
    "คัด": "🔍",
    "กาว": "🔥",
    "ขึ้นรูป": "📦",
}

DEFECTS = {
    "ตอก": ["ตอกหลุด", "ตอกไม่ครบ", "ตอกเบี้ยว", "ตอกผิดตำแหน่ง", "อื่นๆ"],
    "คัด": ["พิมพ์เลื่อน", "สีผิด", "งานเปื้อน", "งานขาด", "รอยขีดข่วน", "อื่นๆ"],
    "กาว": ["กาวไม่ติด", "กาวล้น", "กาวเปื้อน", "ประกบเบี้ยว", "อื่นๆ"],
    "ขึ้นรูป": ["ขึ้นรูปเบี้ยว", "ล็อคไม่เข้า", "แตก/ฉีก", "ขนาดผิด", "อื่นๆ"],
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
        return "#ef233c", "สูง"
    if severity == "กลาง":
        return "#f59e0b", "กลาง"
    return "#22c55e", "ต่ำ"


def card_metric(title, value, icon, color):
    st.markdown(
        f"""
        <div class="metric-card" style="border-left-color:{color};">
            <div class="metric-icon" style="background:{color};">{icon}</div>
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
    dept = str(row.get("หน่วยงาน", ""))
    defect = str(row.get("อาการ", ""))
    qty = safe_int(row.get("จำนวน", 0))
    impact = str(row.get("หลุดถึง", ""))
    severity = str(row.get("ระดับ", ""))
    value = safe_int(row.get("มูลค่าป้องกัน", 0))
    note = str(row.get("รายละเอียด", "")).strip()
    img_path = str(row.get("รูปภาพ", "")).strip()

    color, sev_text = severity_color(severity)
    img64 = image_to_base64(img_path)

    if img64:
        img_html = f'<img class="work-img" src="data:image/jpeg;base64,{img64}" />'
    else:
        img_html = f'<div class="work-img empty-img">{DEPT_ICONS.get(dept, "📌")}</div>'

    note_html = ""
    if note:
        note_html = f'<div class="item-note">📝 {note}</div>'

    st.markdown(
        f"""
        <div class="item-card">
            <div class="item-head">
                <div class="time-badge" style="background:{color};">{time[:5]}</div>
                <div class="item-main">
                    <div class="item-title">{defect}</div>
                    <div class="item-line">{DEPT_ICONS.get(dept, "📌")} {dept} • {qty:,} ใบ • หลุดถึง {impact}</div>
                    <div class="item-line">👤 {reporter} • {date} • 💰 {value:,} บาท</div>
                    {note_html}
                </div>
                {img_html}
            </div>
            <div class="sev-pill" style="background:{color};">ระดับ {sev_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def rank_card(rank, name, dept, qty, cases):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
    st.markdown(
        f"""
        <div class="rank-card">
            <div class="rank-medal">{medal}</div>
            <div class="rank-avatar">👤</div>
            <div class="rank-info">
                <div class="rank-name">{name}</div>
                <div class="rank-sub">{DEPT_ICONS.get(dept, "📌")} {dept} • {cases:,} เคส</div>
            </div>
            <div class="rank-score">{qty:,}<span> ใบ</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def defect_card(rank, defect, qty, cases):
    st.markdown(
        f"""
        <div class="defect-card">
            <div class="defect-no">{rank}</div>
            <div class="defect-info">
                <div class="defect-name">{defect}</div>
                <div class="defect-sub">{cases:,} เคส</div>
            </div>
            <div class="defect-score">{qty:,} ใบ</div>
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
        radial-gradient(circle at top left, rgba(0, 102, 255, .16), transparent 28%),
        radial-gradient(circle at top right, rgba(239, 35, 60, .13), transparent 30%),
        linear-gradient(180deg, #f6f9ff 0%, #edf4ff 55%, #ffffff 100%);
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 760px;
    padding-top: 1.1rem;
    padding-bottom: 2rem;
}

.app-head {
    background: rgba(255,255,255,.82);
    border: 1px solid rgba(226,232,240,.95);
    border-radius: 28px;
    padding: 18px;
    box-shadow: 0 18px 46px rgba(15,23,42,.10);
    backdrop-filter: blur(16px);
    margin-bottom: 14px;
}

.brand-row {
    display: flex;
    align-items: center;
    gap: 14px;
}

.logo {
    width: 68px;
    height: 68px;
    border-radius: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(145deg, #ff3154, #e11d48);
    color: white;
    font-size: 38px;
    box-shadow: inset 0 3px 0 rgba(255,255,255,.28), 0 14px 32px rgba(225,29,72,.28);
}

.brand-title {
    font-size: 43px;
    font-weight: 1000;
    line-height: .92;
    color: #071f52;
    letter-spacing: -1.5px;
}

.brand-title span {
    color: #ef233c;
}

.brand-sub {
    font-size: 16px;
    font-weight: 900;
    color: #243b63;
    margin-top: 6px;
}

.step-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 9px;
    margin-top: 15px;
}

.step {
    background: linear-gradient(180deg, #ffffff, #f7fbff);
    border: 1px solid #dbeafe;
    border-radius: 18px;
    padding: 10px 6px;
    text-align: center;
    color: #0f172a;
    box-shadow: 0 8px 18px rgba(15,23,42,.05);
}

.step-icon {
    width: 42px;
    height: 42px;
    border-radius: 999px;
    margin: 0 auto 5px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    font-size: 22px;
}

.step-text {
    font-size: 13px;
    font-weight: 1000;
}

div[data-testid="stTabs"] button {
    font-size: 17px;
    font-weight: 1000;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: rgba(255,255,255,.88);
    border: 1px solid #dbeafe;
    border-radius: 18px;
    padding: 9px 14px;
    box-shadow: 0 7px 16px rgba(15,23,42,.05);
}

.form-shell {
    background: rgba(255,255,255,.92);
    border: 1px solid #e5e7eb;
    border-radius: 30px;
    overflow: hidden;
    box-shadow: 0 20px 50px rgba(15,23,42,.12);
    margin-top: 12px;
}

.form-top {
    background: linear-gradient(135deg, #ef233c, #dc2626);
    color: white;
    padding: 17px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.form-top-icon {
    width: 48px;
    height: 48px;
    border-radius: 16px;
    background: rgba(255,255,255,.18);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
}

.form-top-title {
    font-size: 24px;
    font-weight: 1000;
    line-height: 1.1;
}

.form-top-sub {
    font-size: 13px;
    font-weight: 800;
    opacity: .92;
}

.form-body {
    padding: 16px 16px 4px 16px;
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

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,.10) !important;
}

.stTextArea textarea {
    min-height: 72px !important;
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
    box-shadow: 0 8px 18px rgba(15,23,42,.04);
}

.stFormSubmitButton > button {
    background: linear-gradient(135deg, #ef233c, #dc2626 70%, #b91c1c) !important;
    color: white !important;
    height: 62px;
    border-radius: 18px !important;
    font-size: 22px !important;
    font-weight: 1000 !important;
    border: 0 !important;
    box-shadow: 0 16px 34px rgba(239,35,60,.30);
    margin-top: 8px;
}

.success-card {
    background: #ffffff;
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
    font-size: 25px;
    font-weight: 1000;
}

.section-title {
    font-size: 25px;
    font-weight: 1000;
    color: #0f172a;
    margin: 18px 0 12px 0;
}

.metric-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.metric-card {
    background: rgba(255,255,255,.92);
    border: 1px solid #e5e7eb;
    border-left: 7px solid;
    border-radius: 22px;
    padding: 15px;
    display: flex;
    gap: 12px;
    align-items: center;
    box-shadow: 0 12px 30px rgba(15,23,42,.07);
}

.metric-icon {
    min-width: 50px;
    width: 50px;
    height: 50px;
    border-radius: 17px;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 27px;
}

.metric-title {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
}

.metric-value {
    color: #0f172a;
    font-size: 25px;
    font-weight: 1000;
    line-height: 1.05;
    margin-top: 4px;
}

.item-card {
    position: relative;
    background: rgba(255,255,255,.92);
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 12px;
    box-shadow: 0 12px 30px rgba(15,23,42,.07);
    margin-bottom: 10px;
}

.item-head {
    display: grid;
    grid-template-columns: 58px 1fr 74px;
    gap: 10px;
    align-items: center;
}

.time-badge {
    min-height: 78px;
    color: white;
    border-radius: 16px;
    font-size: 14px;
    font-weight: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}

.item-title {
    color: #111827;
    font-size: 19px;
    font-weight: 1000;
}

.item-line {
    color: #475569;
    font-size: 13px;
    font-weight: 800;
    margin-top: 3px;
}

.item-note {
    color: #334155;
    background: #f8fafc;
    border-radius: 11px;
    padding: 5px 7px;
    font-size: 12px;
    font-weight: 750;
    margin-top: 5px;
}

.work-img {
    width: 68px;
    height: 68px;
    border-radius: 16px;
    object-fit: cover;
    border: 1px solid #e5e7eb;
}

.empty-img {
    background: linear-gradient(180deg, #f8fafc, #eef2ff);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 31px;
}

.sev-pill {
    position: absolute;
    right: 12px;
    top: 8px;
    color: white;
    border-radius: 999px;
    padding: 3px 9px;
    font-size: 11px;
    font-weight: 1000;
}

.rank-card,
.defect-card {
    background: rgba(255,255,255,.92);
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 13px;
    display: grid;
    align-items: center;
    gap: 10px;
    box-shadow: 0 12px 30px rgba(15,23,42,.07);
    margin-bottom: 10px;
}

.rank-card {
    grid-template-columns: 48px 44px 1fr auto;
}

.defect-card {
    grid-template-columns: 48px 1fr auto;
}

.rank-medal,
.defect-no {
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
.defect-name {
    color: #111827;
    font-size: 16px;
    font-weight: 1000;
}

.rank-sub,
.defect-sub {
    color: #64748b;
    font-size: 12px;
    font-weight: 800;
}

.rank-score {
    color: #16a34a;
    font-size: 21px;
    font-weight: 1000;
    text-align: right;
}

.rank-score span {
    color: #64748b;
    font-size: 12px;
}

.defect-score {
    color: #ef233c;
    font-size: 18px;
    font-weight: 1000;
    text-align: right;
}

.qr-box {
    background: rgba(255,255,255,.92);
    border: 1px solid #dbeafe;
    border-radius: 24px;
    padding: 15px;
    box-shadow: 0 12px 30px rgba(15,23,42,.06);
    margin-top: 14px;
}

.qr-title {
    color: #0f172a;
    font-size: 19px;
    font-weight: 1000;
    margin-bottom: 6px;
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
    .brand-title {
        font-size: 34px;
    }

    .logo {
        width: 58px;
        height: 58px;
        font-size: 32px;
    }

    .step-row {
        grid-template-columns: 1fr 1fr;
    }

    .metric-grid,
    .success-grid {
        grid-template-columns: 1fr;
    }

    .item-head {
        grid-template-columns: 54px 1fr 62px;
    }

    .work-img {
        width: 58px;
        height: 58px;
    }

    .rank-card {
        grid-template-columns: 43px 38px 1fr;
    }

    .rank-score {
        grid-column: 3;
        text-align: left;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f"""
<div class="app-head">
    <div style="color:#94a3b8;font-size:12px;font-weight:900;margin-bottom:8px;">{APP_VERSION}</div>
    <div class="brand-row">
        <div class="logo">🚨</div>
        <div>
            <div class="brand-title">QUALITY <span>ALERT</span></div>
            <div class="brand-sub">ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด</div>
        </div>
    </div>
    <div class="step-row">
        <div class="step"><div class="step-icon">📷</div><div class="step-text">ถ่ายรูป</div></div>
        <div class="step"><div class="step-icon">💬</div><div class="step-text">บอกอาการ</div></div>
        <div class="step"><div class="step-icon">#</div><div class="step-text">ใส่จำนวน</div></div>
        <div class="step"><div class="step-icon">📨</div><div class="step-text">ส่งแจ้งเตือน</div></div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

tab_alert, tab_latest, tab_dashboard, tab_qr = st.tabs(
    ["🚨 แจ้งปัญหา", "📋 รายการล่าสุด", "📊 Dashboard", "🔗 QR"]
)

with tab_alert:
    st.markdown('<div class="form-shell">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="form-top">
            <div class="form-top-icon">🚨</div>
            <div>
                <div class="form-top-title">แจ้งเตือนปัญหาคุณภาพ</div>
                <div class="form-top-sub">กรอกง่าย ใช้งานจริง ทุกปุ่มกดได้</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("alert_form", clear_on_submit=True):
        st.markdown('<div class="form-body">', unsafe_allow_html=True)

        reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")

        department = st.selectbox("🏭 หน่วยงาน", DEPTS, index=0)

        defect = st.selectbox("🔍 อาการที่พบ", DEFECTS[department])

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
            img_name = f"{now.strftime('%Y%m%d_%H%M%S')}_{department}.jpg"
            img_path = IMG_DIR / img_name
            with open(img_path, "wb") as f:
                f.write(final_image.getbuffer())

        damage_value = int(qty) * COST_PER_SHEET

        new_row = {
            "วันที่": now.strftime("%d/%m/%Y"),
            "เวลา": now.strftime("%H:%M:%S"),
            "ผู้แจ้ง": reporter.strip(),
            "หน่วยงาน": department,
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
                <div class="success-sub">ขอบคุณที่ช่วยป้องกันงานเสียก่อนส่งต่อ</div>
                <div class="success-grid">
                    <div class="success-box">
                        <div class="success-label">ป้องกันได้</div>
                        <div class="success-value">{int(qty):,} ใบ</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">มูลค่าป้องกัน</div>
                        <div class="success-value">{damage_value:,.0f} บาท</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">อันดับของคุณ</div>
                        <div class="success-value">{rank_text}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">หน่วยงาน</div>
                        <div class="success-value">{DEPT_ICONS.get(department, "📌")} {department}</div>
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
        df_dash["มูลค่าป้องกัน"] = pd.to_numeric(
            df_dash["มูลค่าป้องกัน"], errors="coerce"
        ).fillna(0)

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
        card_metric("แจ้งทั้งหมด", f"{total_cases:,} เคส", "🔔", "#ef233c")
        card_metric("ป้องกันได้", f"{total_qty:,} ใบ", "🛡️", "#22c55e")
        card_metric("ผู้มีส่วนร่วม", f"{total_reporters:,} คน", "👥", "#2563eb")
        card_metric("มูลค่าป้องกัน", f"{total_value:,} บาท", "💰", "#f59e0b")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🏆 Top 5 ผู้มีส่วนร่วม</div>', unsafe_allow_html=True)

        reporter_df = df_dash[["ผู้แจ้ง", "หน่วยงาน", "จำนวน"]].copy()
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

            top_dept = (
                reporter_df.groupby("ผู้แจ้ง")["หน่วยงาน"]
                .agg(lambda x: str(x.dropna().iloc[-1]) if len(x.dropna()) else "")
                .reset_index()
            )

            top = pd.merge(top_qty, top_case, on="ผู้แจ้ง", how="left")
            top = pd.merge(top, top_dept, on="ผู้แจ้ง", how="left")
            top["จำนวนใบ"] = pd.to_numeric(top["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
            top["จำนวนเคส"] = pd.to_numeric(top["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
            top = top.nlargest(5, "จำนวนใบ").reset_index(drop=True)

            for i, row in top.iterrows():
                rank_card(
                    i + 1,
                    str(row["ผู้แจ้ง"]),
                    str(row.get("หน่วยงาน", "")),
                    int(row["จำนวนใบ"]),
                    int(row["จำนวนเคส"]),
                )

        st.markdown('<div class="section-title">🔍 Top อาการ</div>', unsafe_allow_html=True)

        defect_df = df_dash[["อาการ", "จำนวน"]].copy()
        defect_df["อาการ"] = defect_df["อาการ"].astype(str).str.strip()
        defect_df = defect_df[defect_df["อาการ"] != ""]

        if defect_df.empty:
            st.info("ยังไม่มีข้อมูลอาการ")
        else:
            top_defect_qty = (
                defect_df.groupby("อาการ")["จำนวน"]
                .sum()
                .reset_index()
                .rename(columns={"จำนวน": "จำนวนใบ"})
            )

            top_defect_case = (
                defect_df.groupby("อาการ")
                .size()
                .reset_index(name="จำนวนเคส")
            )

            top_defect = pd.merge(top_defect_qty, top_defect_case, on="อาการ", how="left")
            top_defect["จำนวนใบ"] = pd.to_numeric(
                top_defect["จำนวนใบ"], errors="coerce"
            ).fillna(0).astype(int)
            top_defect["จำนวนเคส"] = pd.to_numeric(
                top_defect["จำนวนเคส"], errors="coerce"
            ).fillna(0).astype(int)
            top_defect = top_defect.nlargest(5, "จำนวนใบ").reset_index(drop=True)

            for i, row in top_defect.iterrows():
                defect_card(
                    i + 1,
                    str(row["อาการ"]),
                    int(row["จำนวนใบ"]),
                    int(row["จำนวนเคส"]),
                )

with tab_qr:
    st.markdown('<div class="qr-box">', unsafe_allow_html=True)
    st.markdown('<div class="qr-title">🔗 ลิงก์สำหรับทำ QR จุดเดียว</div>', unsafe_allow_html=True)
    base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"
    st.code(base_url)
    st.markdown(
        """
        <div class="help-card">
        ใช้ QR จุดเดียวพอ แล้วให้พนักงานเลือกหน่วยงานจาก Dropdown ในหน้าแจ้งปัญหา
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
