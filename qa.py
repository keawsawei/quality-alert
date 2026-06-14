import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="wide")

APP_VERSION = "V8-POSTER-STYLE-APP"

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

DEPT_COLORS = {
    "ตอก": "#1463d9",
    "คัด": "#21a35b",
    "กาว": "#f5a400",
    "ขึ้นรูป": "#7c3aed",
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


def img_to_base64(path):
    try:
        p = Path(path)
        if not p.exists():
            return ""
        data = p.read_bytes()
        return base64.b64encode(data).decode("utf-8")
    except Exception:
        return ""


def severity_class(severity):
    if str(severity).strip() == "สูง":
        return "sev-red"
    if str(severity).strip() == "กลาง":
        return "sev-yellow"
    return "sev-green"


def make_latest_card(row):
    date = str(row.get("วันที่", ""))
    time = str(row.get("เวลา", ""))
    reporter = str(row.get("ผู้แจ้ง", ""))
    dept = str(row.get("หน่วยงาน", ""))
    defect = str(row.get("อาการ", ""))
    qty = safe_int(row.get("จำนวน", 0))
    impact = str(row.get("หลุดถึง", ""))
    severity = str(row.get("ระดับ", ""))
    img_path = str(row.get("รูปภาพ", "")).strip()
    cls = severity_class(severity)

    img64 = img_to_base64(img_path)
    if img64:
        img_html = f'<img class="alert-photo" src="data:image/jpeg;base64,{img64}">'
    else:
        img_html = f'<div class="alert-photo no-photo">{DEPT_ICONS.get(dept, "📌")}</div>'

    st.markdown(
        f"""
        <div class="alert-row">
            <div class="time-pill {cls}">{time[:5]}</div>
            <div class="alert-body">
                <div class="alert-name">{defect}</div>
                <div class="alert-desc">{qty:,} ใบ</div>
                <div class="alert-meta">โดย : {reporter} ({dept})</div>
                <div class="alert-meta">หลุดถึง {impact} • ระดับ {severity}</div>
            </div>
            {img_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_rank_card(rank, name, dept, qty, case):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else str(rank)
    st.markdown(
        f"""
        <div class="rank-row">
            <div class="medal">{medal}</div>
            <div class="avatar">👤</div>
            <div class="rank-info">
                <div class="rank-name">{name}</div>
                <div class="rank-sub">{dept} • {case:,} เคส</div>
            </div>
            <div class="rank-score">{qty:,}<span> ใบ</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_dept_button(label):
    color = DEPT_COLORS.get(label, "#1463d9")
    icon = DEPT_ICONS.get(label, "📌")
    st.markdown(
        f"""
        <div class="dept-btn" style="background:{color};">
            <div class="dept-icon">{icon}</div>
            <div>{label}</div>
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
    background: #ffffff;
}

#MainMenu, footer, header {
    visibility: hidden;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

.version {
    color:#94a3b8;
    font-size:12px;
    font-weight:800;
    margin-bottom:4px;
}

.header-wrap {
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:18px;
    margin-bottom:18px;
}

.brand {
    display:flex;
    align-items:center;
    gap:14px;
}

.logo-box {
    width:72px;
    height:72px;
    border-radius:21px;
    background:linear-gradient(145deg,#ff2345,#f43f5e);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:42px;
    color:white;
    box-shadow:0 16px 32px rgba(239,35,60,.22);
}

.brand-title {
    font-size:54px;
    line-height:.92;
    font-weight:1000;
    letter-spacing:-2px;
    color:#08245c;
}

.brand-title span {
    color:#ef233c;
}

.brand-sub {
    margin-top:6px;
    color:#112b59;
    font-size:18px;
    font-weight:900;
}

.top-menu {
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:18px;
    padding:14px 18px;
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:18px;
    min-width:430px;
    box-shadow:0 8px 25px rgba(15,23,42,.06);
}

.menu-item {
    display:flex;
    align-items:center;
    justify-content:center;
    gap:8px;
    color:#111827;
    font-size:16px;
    font-weight:950;
    white-space:nowrap;
}

.menu-icon {
    width:38px;
    height:38px;
    border-radius:999px;
    border:2px solid #111827;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}

.step-bar {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:18px;
    margin:6px 0 14px 0;
}

.step-pill {
    background:#063f94;
    color:white;
    border-radius:9px;
    text-align:center;
    padding:8px;
    font-size:16px;
    font-weight:1000;
    box-shadow:0 8px 20px rgba(6,63,148,.18);
}

.main-grid {
    display:grid;
    grid-template-columns:1fr 1.05fr 1fr;
    gap:18px;
    align-items:start;
    margin-top:14px;
}

.panel {
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:22px;
    box-shadow:0 14px 35px rgba(15,23,42,.08);
    overflow:hidden;
}

.panel-head-blue {
    background:#063f94;
    color:white;
    padding:13px 18px;
    font-size:18px;
    font-weight:1000;
}

.panel-head-purple {
    background:linear-gradient(135deg,#6d28d9,#9333ea);
    color:white;
    padding:13px 18px;
    font-size:18px;
    font-weight:1000;
}

.panel-head-green {
    background:linear-gradient(135deg,#0f9f60,#16a34a);
    color:white;
    padding:13px 18px;
    font-size:18px;
    font-weight:1000;
}

.panel-body {
    padding:16px;
}

.form-phone {
    border:8px solid #111827;
    border-radius:36px;
    overflow:hidden;
    background:white;
    box-shadow:0 20px 45px rgba(0,0,0,.20);
}

.phone-head {
    background:linear-gradient(135deg,#ef233c,#f43f5e);
    color:white;
    padding:18px;
    display:flex;
    align-items:center;
    gap:10px;
}

.phone-logo {
    width:42px;
    height:42px;
    border-radius:13px;
    background:rgba(255,255,255,.22);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
}

.phone-title {
    font-size:22px;
    line-height:1.15;
    font-weight:1000;
}

.phone-sub {
    font-size:13px;
    opacity:.9;
    font-weight:800;
}

.form-inner {
    padding:16px;
}

label, .stRadio label {
    font-weight:900 !important;
    color:#111827 !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background:#f8fafc !important;
    border:1px solid #e5e7eb !important;
    border-radius:12px !important;
    min-height:42px;
}

.stTextArea textarea {
    min-height:70px !important;
}

.stFormSubmitButton > button {
    background:linear-gradient(135deg,#ef233c,#dc2626) !important;
    color:white !important;
    height:58px;
    border-radius:14px !important;
    font-size:20px !important;
    font-weight:1000 !important;
    border:0 !important;
    box-shadow:0 12px 26px rgba(239,35,60,.26);
}

div[data-testid="stExpander"] {
    border-radius:16px !important;
    border:1px dashed #cbd5e1 !important;
    background:#ffffff !important;
}

.dept-btn-grid {
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:10px;
    margin:8px 0 10px 0;
}

.dept-btn {
    color:white;
    border-radius:14px;
    padding:12px 8px;
    text-align:center;
    font-weight:1000;
    box-shadow:0 10px 22px rgba(15,23,42,.12);
}

.dept-icon {
    font-size:26px;
    line-height:1;
    margin-bottom:5px;
}

.alert-row {
    display:grid;
    grid-template-columns:62px 1fr 86px;
    gap:12px;
    align-items:center;
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:16px;
    overflow:hidden;
    margin-bottom:11px;
    box-shadow:0 8px 20px rgba(15,23,42,.06);
}

.time-pill {
    color:white;
    font-size:13px;
    font-weight:1000;
    min-height:92px;
    display:flex;
    align-items:center;
    justify-content:center;
}

.sev-red { background:#ef233c; }
.sev-yellow { background:#f59e0b; }
.sev-green { background:#22c55e; }

.alert-body {
    padding:10px 0;
}

.alert-name {
    font-size:17px;
    font-weight:1000;
    color:#111827;
}

.alert-desc {
    font-size:17px;
    font-weight:950;
    color:#111827;
}

.alert-meta {
    font-size:13px;
    font-weight:750;
    color:#475569;
}

.alert-photo {
    width:76px;
    height:76px;
    border-radius:12px;
    object-fit:cover;
    margin-right:10px;
}

.no-photo {
    background:#f1f5f9;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:32px;
}

.metric-big {
    border-radius:15px;
    padding:18px;
    margin-bottom:12px;
    border:1px solid #e5e7eb;
}

.metric-red {
    background:#fff1f2;
}

.metric-green {
    background:#ecfdf5;
}

.metric-yellow {
    background:#fffbeb;
}

.metric-label {
    font-size:15px;
    font-weight:900;
    color:#475569;
}

.metric-value {
    display:flex;
    align-items:center;
    justify-content:space-between;
    color:#111827;
    font-size:42px;
    font-weight:1000;
    line-height:1.05;
}

.metric-value small {
    font-size:18px;
    color:#111827;
}

.metric-emoji {
    font-size:46px;
}

.chart-box {
    background:#ffffff;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:14px;
    margin-top:12px;
}

.chart-title {
    font-size:14px;
    color:#111827;
    font-weight:900;
    margin-bottom:8px;
}

.fake-chart {
    height:105px;
    background:
        linear-gradient(to right, #e5e7eb 1px, transparent 1px),
        linear-gradient(to bottom, #e5e7eb 1px, transparent 1px);
    background-size:42px 26px;
    border-radius:10px;
    position:relative;
}

.fake-line {
    position:absolute;
    left:18px;
    right:18px;
    bottom:22px;
    height:50px;
    border-bottom:4px solid #1463d9;
    transform:skewY(-11deg);
}

.rank-row {
    display:grid;
    grid-template-columns:44px 42px 1fr auto;
    gap:10px;
    align-items:center;
    background:white;
    border:1px solid #e5e7eb;
    border-radius:16px;
    padding:12px;
    margin-bottom:11px;
    box-shadow:0 8px 20px rgba(15,23,42,.05);
}

.medal {
    width:38px;
    height:38px;
    border-radius:999px;
    background:#fff7ed;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:22px;
    font-weight:1000;
}

.avatar {
    width:38px;
    height:38px;
    border-radius:999px;
    background:#e0f2fe;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:22px;
}

.rank-name {
    font-size:15px;
    font-weight:1000;
    color:#111827;
}

.rank-sub {
    font-size:12px;
    font-weight:750;
    color:#64748b;
}

.rank-score {
    color:#16a34a;
    font-size:20px;
    font-weight:1000;
    text-align:right;
}

.rank-score span {
    font-size:12px;
    color:#64748b;
}

.reward-box {
    background:#f5f3ff;
    border:1px solid #ede9fe;
    border-radius:16px;
    padding:16px;
    display:flex;
    gap:12px;
    align-items:center;
    margin-top:12px;
}

.reward-icon {
    font-size:48px;
}

.reward-title {
    font-size:17px;
    font-weight:1000;
    color:#111827;
}

.reward-text {
    font-size:13px;
    font-weight:750;
    color:#475569;
}

.success-card {
    background:white;
    border:1px solid #dcfce7;
    border-radius:24px;
    padding:22px;
    text-align:center;
    box-shadow:0 18px 40px rgba(22,163,74,.15);
    margin:18px 0;
}

.success-check {
    width:90px;
    height:90px;
    margin:0 auto 12px auto;
    border-radius:999px;
    background:#22c55e;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:58px;
    font-weight:1000;
}

.success-title {
    font-size:30px;
    font-weight:1000;
    color:#111827;
}

.success-sub {
    color:#475569;
    font-size:16px;
    font-weight:800;
    margin:4px 0 14px 0;
}

.success-grid {
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:10px;
}

.success-box {
    background:#f8fafc;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:13px;
}

.success-label {
    font-size:13px;
    font-weight:850;
    color:#64748b;
}

.success-value {
    font-size:25px;
    font-weight:1000;
    color:#16a34a;
}

.bottom-strip {
    margin-top:18px;
    display:grid;
    grid-template-columns:1fr 1fr 1fr;
    gap:16px;
    background:#eff6ff;
    border-radius:22px;
    padding:18px;
    border:1px solid #dbeafe;
}

.bottom-title {
    font-size:18px;
    font-weight:1000;
    color:#0b1f4d;
    margin-bottom:8px;
}

.bullet {
    font-size:13px;
    font-weight:800;
    color:#1f2937;
    margin-bottom:4px;
}

.flow {
    display:flex;
    align-items:center;
    justify-content:space-around;
    gap:8px;
}

.flow-step {
    text-align:center;
    font-size:13px;
    color:#0b1f4d;
    font-weight:900;
}

.flow-icon {
    width:50px;
    height:50px;
    border-radius:999px;
    background:white;
    border:1px solid #bfdbfe;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:24px;
    margin:0 auto 6px auto;
}

.qr-code-box {
    background:white;
    border-radius:14px;
    border:1px solid #bfdbfe;
    padding:10px;
    text-align:center;
}

.qr-code-box code {
    white-space:normal !important;
}

@media (max-width: 980px) {
    .header-wrap {
        flex-direction:column;
        align-items:flex-start;
    }

    .top-menu {
        width:100%;
        min-width:0;
        grid-template-columns:repeat(2,1fr);
    }

    .step-bar {
        grid-template-columns:repeat(2,1fr);
    }

    .main-grid {
        grid-template-columns:1fr;
    }

    .bottom-strip {
        grid-template-columns:1fr;
    }

    .brand-title {
        font-size:42px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(f'<div class="version">{APP_VERSION}</div>', unsafe_allow_html=True)

st.markdown(
    """
<div class="header-wrap">
    <div class="brand">
        <div class="logo-box">🚨</div>
        <div>
            <div class="brand-title">QUALITY <span>ALERT</span></div>
            <div class="brand-sub">ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด</div>
        </div>
    </div>
    <div class="top-menu">
        <div class="menu-item"><div class="menu-icon">📷</div>ถ่ายรูป</div>
        <div class="menu-item"><div class="menu-icon">💬</div>บอกอาการ</div>
        <div class="menu-item"><div class="menu-icon">#</div>ใส่จำนวน</div>
        <div class="menu-item"><div class="menu-icon">📨</div>ส่งแจ้งเตือน</div>
    </div>
</div>

<div class="step-bar">
    <div class="step-pill">1. เปิดลิงก์ QR CODE</div>
    <div class="step-pill">2. กรอกข้อมูลปัญหา</div>
    <div class="step-pill">3. อัปโหลดรูปภาพ</div>
    <div class="step-pill">4. ส่งสำเร็จ</div>
</div>
""",
    unsafe_allow_html=True,
)

df = load_data()

with st.container():
    c_left, c_mid, c_right = st.columns([1, 1.05, 1])

    with c_left:
        st.markdown('<div class="panel"><div class="panel-head-blue">👥 DASHBOARD หัวหน้างาน</div><div class="panel-body">', unsafe_allow_html=True)

        if df.empty:
            st.info("ยังไม่มีข้อมูล")
        else:
            today_count = len(df)
            st.markdown(
                f"""
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <div style="font-size:18px;font-weight:1000;color:#111827;">รายการแจ้งเตือนล่าสุด</div>
                    <div style="background:#ef233c;color:white;border-radius:10px;padding:5px 12px;font-weight:1000;">{today_count} เคส</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            latest_df = df.tail(5).sort_index(ascending=False)
            for _, row in latest_df.iterrows():
                make_latest_card(row)

        st.markdown('</div></div>', unsafe_allow_html=True)

    with c_mid:
        st.markdown('<div class="form-phone">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="phone-head">
                <div class="phone-logo">🚨</div>
                <div>
                    <div class="phone-title">QUALITY ALERT</div>
                    <div class="phone-sub">แจ้งเตือนปัญหาคุณภาพ</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("alert_form", clear_on_submit=True):
            st.markdown('<div class="form-inner">', unsafe_allow_html=True)

            reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")

            department = st.selectbox("🏭 หน่วยงาน", DEPTS, index=0)

            st.markdown('<div class="dept-btn-grid">', unsafe_allow_html=True)
            for d in DEPTS:
                make_dept_button(d)
            st.markdown('</div>', unsafe_allow_html=True)

            defect = st.selectbox("🔍 อาการที่พบ", DEFECTS[department])

            qty = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, step=1)

            impact = st.radio("⚠️ ถ้าไม่เจอจะหลุดถึง", IMPACT_LEVELS, horizontal=True)

            severity = st.radio("🚦 ระดับความรุนแรง", SEVERITY_LIST, horizontal=True)

            note = st.text_area("📝 รายละเอียดเพิ่มเติม", placeholder="เช่น จุดที่พบ / สาเหตุคร่าวๆ เป็นต้น")

            image = None
            upload_image = None

            with st.expander("📷 รูปภาพประกอบ (ถ่ายหน้างาน)", expanded=False):
                image = st.camera_input("📷 แตะเพื่อถ่ายรูป")
                upload_image = st.file_uploader("หรือเลือกจากแกลเลอรี่", type=["jpg", "jpeg", "png"])

            submitted = st.form_submit_button("🚨 แจ้งเตือนทันที")

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

            df_save = load_data()
            df_save = pd.concat([df_save, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df_save)

            reporter_df = df_save[df_save["ผู้แจ้ง"].astype(str).str.strip() != ""].copy()
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

    with c_right:
        st.markdown('<div class="panel"><div class="panel-head-purple">📊 REPORT สรุปภาพรวม</div><div class="panel-body">', unsafe_allow_html=True)

        if df.empty:
            total_cases = 0
            total_qty = 0
            total_value = 0
        else:
            total_cases = len(df)
            total_qty = int(pd.to_numeric(df["จำนวน"], errors="coerce").fillna(0).sum())
            total_value = int(pd.to_numeric(df["มูลค่าป้องกัน"], errors="coerce").fillna(0).sum())

        st.markdown(
            f"""
            <div class="metric-big metric-red">
                <div class="metric-label">แจ้งเตือนทั้งหมด</div>
                <div class="metric-value">{total_cases:,} <small>เคส</small><div class="metric-emoji">🔔</div></div>
            </div>
            <div class="metric-big metric-green">
                <div class="metric-label">ป้องกันงานเสียได้</div>
                <div class="metric-value">{total_qty:,} <small>ใบ</small><div class="metric-emoji">🛡️</div></div>
            </div>
            <div class="metric-big metric-yellow">
                <div class="metric-label">ประเมินมูลค่าความเสียหาย</div>
                <div class="metric-value">{total_value:,} <small>บาท</small><div class="metric-emoji">💰</div></div>
            </div>
            <div class="chart-box">
                <div class="chart-title">กราฟแนวโน้มการแจ้งเตือน</div>
                <div class="fake-chart"><div class="fake-line"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown('<br>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><div class="panel-head-green">🏆 TOP 5 ผู้มีส่วนร่วม</div><div class="panel-body">', unsafe_allow_html=True)

        if df.empty:
            st.info("ยังไม่มีข้อมูล")
        else:
            reporter_df = df[["ผู้แจ้ง", "หน่วยงาน", "จำนวน"]].copy()
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
                    make_rank_card(
                        i + 1,
                        row["ผู้แจ้ง"],
                        row["หน่วยงาน"],
                        int(row["จำนวนใบ"]),
                        int(row["จำนวนเคส"]),
                    )

        st.markdown(
            """
            <div class="reward-box">
                <div class="reward-icon">🎁</div>
                <div>
                    <div class="reward-title">รางวัลประจำเดือน</div>
                    <div class="reward-text">ผู้มีส่วนร่วมสูงสุด 3 อันดับแรก รับรางวัลตามเงื่อนไขหน่วยงาน</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown(
    """
<div class="bottom-strip">
    <div>
        <div class="bottom-title">ประโยชน์ที่ได้รับ</div>
        <div class="bullet">✅ พบปัญหาเร็ว ป้องกันก่อนเสีย</div>
        <div class="bullet">✅ ลดของเสีย ลดต้นทุน</div>
        <div class="bullet">✅ สร้างจิตสำนึกคุณภาพให้ทุกคน</div>
        <div class="bullet">✅ ข้อมูลจริงจากหน้างาน นำไปปรับปรุงได้ตรงจุด</div>
    </div>
    <div>
        <div class="bottom-title">วิธีใช้งานง่ายๆ</div>
        <div class="flow">
            <div class="flow-step"><div class="flow-icon">📱</div>เปิดลิงก์</div>
            <div class="flow-step"><div class="flow-icon">📷</div>ถ่ายรูป</div>
            <div class="flow-step"><div class="flow-icon">📝</div>กรอกข้อมูล</div>
            <div class="flow-step"><div class="flow-icon">📨</div>ส่งแจ้งเตือน</div>
        </div>
    </div>
    <div>
        <div class="bottom-title">ติด QR CODE ทุกจุดงาน</div>
        <div class="qr-code-box">
            <code>https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app</code>
        </div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)
