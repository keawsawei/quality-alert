import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

APP_VERSION = "V6-MOBILE-APP-STYLE"

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


def get_severity_class(severity):
    severity = str(severity).strip()
    if severity == "สูง":
        return "sev-high"
    if severity == "กลาง":
        return "sev-mid"
    return "sev-low"


def safe_int(value):
    try:
        return int(pd.to_numeric(value, errors="coerce"))
    except Exception:
        return 0


def make_metric_card(label, value, icon, color_class):
    st.markdown(
        f"""
        <div class="metric-card {color_class}">
            <div class="metric-icon">{icon}</div>
            <div>
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_rank_card(rank, title, qty, case, dept="", is_top=False):
    medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else str(rank)
    top_class = "rank-card top-rank" if is_top else "rank-card"
    st.markdown(
        f"""
        <div class="{top_class}">
            <div class="rank-left">
                <div class="rank-medal">{medal}</div>
                <div>
                    <div class="rank-name">{title}</div>
                    <div class="rank-sub">{dept} • {case:,} เคส</div>
                </div>
            </div>
            <div class="rank-score">{qty:,}<span> ใบ</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_defect_card(rank, title, qty, case):
    st.markdown(
        f"""
        <div class="defect-card">
            <div class="defect-rank">{rank}</div>
            <div class="defect-info">
                <div class="defect-title">{title}</div>
                <div class="defect-sub">{case:,} เคส</div>
            </div>
            <div class="defect-qty">{qty:,} ใบ</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def make_latest_card(row):
    date = str(row.get("วันที่", ""))
    time = str(row.get("เวลา", ""))
    reporter = str(row.get("ผู้แจ้ง", ""))
    dept = str(row.get("หน่วยงาน", ""))
    defect = str(row.get("อาการ", ""))
    qty = safe_int(row.get("จำนวน", 0))
    impact = str(row.get("หลุดถึง", ""))
    severity = str(row.get("ระดับ", ""))
    value = safe_int(row.get("มูลค่าป้องกัน", 0))
    img_path = str(row.get("รูปภาพ", "")).strip()
    sev_class = get_severity_class(severity)
    dept_icon = DEPT_ICONS.get(dept, "📌")

    img_html = ""
    if img_path and Path(img_path).exists():
        img_html = f'<img class="latest-img" src="{img_path}" />'
    else:
        img_html = f'<div class="latest-img empty-img">{dept_icon}</div>'

    st.markdown(
        f"""
        <div class="latest-card {sev_class}">
            <div class="latest-time">{time}</div>
            <div class="latest-main">
                <div class="latest-title">{defect}</div>
                <div class="latest-detail">{qty:,} ใบ • หลุดถึง {impact}</div>
                <div class="latest-detail">โดย : {reporter} ({dept})</div>
                <div class="latest-detail">ระดับ {severity} • 💰 {value:,} บาท</div>
            </div>
            {img_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


dept_qr = st.query_params.get("dept", "ตอก")
if dept_qr not in DEPTS:
    dept_qr = "ตอก"

st.markdown(
    """
<style>
.block-container {
    padding-top: 1.2rem;
    max-width: 760px;
}
#MainMenu, footer, header {
    visibility: hidden;
}
.app-shell {
    background: #ffffff;
}
.hero {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 6px;
}
.hero-logo {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    background: linear-gradient(135deg, #ef233c, #ff6b6b);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 32px;
    box-shadow: 0 12px 28px rgba(239, 35, 60, 0.25);
}
.hero-title {
    font-size: 42px;
    line-height: 0.95;
    font-weight: 1000;
    color: #0b1f4d;
    letter-spacing: -1px;
}
.hero-title span {
    color: #ef233c;
}
.hero-sub {
    font-size: 17px;
    font-weight: 850;
    color: #23395d;
    margin-top: 4px;
}
.quick-tabs {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
    margin: 16px 0 18px 0;
}
.quick-tab {
    text-align: center;
    font-weight: 950;
    font-size: 14px;
    color: #0f172a;
}
.quick-icon {
    width: 38px;
    height: 38px;
    border-radius: 999px;
    margin: 0 auto 5px auto;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #eff6ff;
    border: 1px solid #dbeafe;
    font-size: 20px;
}
.dept-card {
    background: linear-gradient(135deg, #0f4ca8, #0b74ff);
    border-radius: 20px;
    padding: 15px 16px;
    font-size: 22px;
    font-weight: 950;
    text-align: center;
    color: #ffffff;
    margin-bottom: 18px;
    box-shadow: 0 10px 28px rgba(11, 116, 255, 0.24);
}
.form-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 22px;
    padding: 18px 18px 10px 18px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    margin-bottom: 22px;
}
.form-title {
    font-size: 24px;
    font-weight: 1000;
    color: #111827;
    margin-bottom: 4px;
}
.form-sub {
    font-size: 14px;
    font-weight: 750;
    color: #64748b;
    margin-bottom: 14px;
}
div[data-testid="stExpander"] {
    border-radius: 18px;
    border: 1px dashed #bfdbfe;
    background: #f8fbff;
}
.stButton > button,
.stFormSubmitButton > button {
    width: 100%;
    height: 60px;
    font-size: 22px;
    font-weight: 1000;
    border-radius: 16px;
    background: linear-gradient(135deg, #ef233c, #dc2626);
    color: white;
    border: 0;
    box-shadow: 0 12px 28px rgba(239, 35, 60, 0.28);
}
.success-card {
    background: #ffffff;
    border: 1px solid #dcfce7;
    border-radius: 24px;
    padding: 24px 18px;
    text-align: center;
    box-shadow: 0 14px 38px rgba(22, 163, 74, 0.12);
    margin-top: 16px;
}
.success-check {
    width: 96px;
    height: 96px;
    background: #22c55e;
    color: white;
    font-size: 58px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px auto;
    box-shadow: 0 12px 32px rgba(34, 197, 94, 0.3);
}
.success-title {
    font-size: 30px;
    font-weight: 1000;
    color: #111827;
}
.success-sub {
    font-size: 17px;
    font-weight: 750;
    color: #64748b;
    margin: 6px 0 18px 0;
}
.success-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.success-box {
    background: #f8fafc;
    border-radius: 18px;
    padding: 14px;
    border: 1px solid #e5e7eb;
}
.success-label {
    color: #64748b;
    font-size: 14px;
    font-weight: 850;
}
.success-value {
    color: #16a34a;
    font-size: 28px;
    font-weight: 1000;
    margin-top: 4px;
}
.dash-title {
    font-size: 34px;
    font-weight: 1000;
    color: #0f172a;
    margin: 28px 0 14px 0;
}
.section-title {
    font-size: 25px;
    font-weight: 1000;
    color: #0f172a;
    margin: 28px 0 12px 0;
}
.metric-card {
    border-radius: 20px;
    padding: 18px 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}
.metric-red { background: linear-gradient(135deg, #fff1f2, #ffffff); }
.metric-green { background: linear-gradient(135deg, #f0fdf4, #ffffff); }
.metric-yellow { background: linear-gradient(135deg, #fffbeb, #ffffff); }
.metric-blue { background: linear-gradient(135deg, #eff6ff, #ffffff); }
.metric-icon {
    width: 56px;
    height: 56px;
    border-radius: 18px;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    box-shadow: inset 0 0 0 1px #e5e7eb;
}
.metric-label {
    font-size: 15px;
    font-weight: 900;
    color: #64748b;
}
.metric-value {
    font-size: 32px;
    line-height: 1.05;
    font-weight: 1000;
    color: #0f172a;
    margin-top: 5px;
}
.latest-card {
    display: grid;
    grid-template-columns: 72px 1fr 92px;
    gap: 12px;
    align-items: center;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055);
}
.latest-time {
    height: 100%;
    min-height: 92px;
    color: white;
    font-size: 15px;
    font-weight: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
}
.sev-high .latest-time { background: #ef233c; }
.sev-mid .latest-time { background: #f59e0b; }
.sev-low .latest-time { background: #22c55e; }
.latest-main {
    padding: 12px 0;
}
.latest-title {
    font-size: 19px;
    font-weight: 1000;
    color: #111827;
}
.latest-detail {
    font-size: 14px;
    font-weight: 760;
    color: #475569;
    margin-top: 3px;
}
.latest-img {
    width: 78px;
    height: 78px;
    object-fit: cover;
    border-radius: 14px;
    margin-right: 10px;
}
.empty-img {
    background: #f1f5f9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
}
.rank-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 13px 15px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055);
}
.top-rank {
    background: linear-gradient(135deg, #fff7ed, #ffffff);
    border-color: #fed7aa;
}
.rank-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.rank-medal {
    width: 46px;
    height: 46px;
    border-radius: 999px;
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 1000;
}
.rank-name {
    font-size: 19px;
    font-weight: 1000;
    color: #111827;
}
.rank-sub {
    font-size: 14px;
    font-weight: 800;
    color: #64748b;
}
.rank-score {
    color: #16a34a;
    font-size: 25px;
    font-weight: 1000;
}
.rank-score span {
    font-size: 14px;
    color: #64748b;
}
.defect-card {
    display: grid;
    grid-template-columns: 46px 1fr auto;
    gap: 12px;
    align-items: center;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 13px 15px;
    margin-bottom: 10px;
    box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055);
}
.defect-rank {
    width: 42px;
    height: 42px;
    border-radius: 14px;
    background: #eff6ff;
    color: #1d4ed8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 1000;
    font-size: 18px;
}
.defect-title {
    font-size: 18px;
    font-weight: 1000;
    color: #111827;
}
.defect-sub {
    font-size: 13px;
    font-weight: 800;
    color: #64748b;
}
.defect-qty {
    font-size: 22px;
    font-weight: 1000;
    color: #ef233c;
}
.bottom-guide {
    background: linear-gradient(135deg, #eff6ff, #f8fafc);
    border: 1px solid #dbeafe;
    border-radius: 22px;
    padding: 16px;
    margin: 28px 0 18px 0;
}
.guide-title {
    font-size: 18px;
    font-weight: 1000;
    color: #0b1f4d;
    margin-bottom: 10px;
}
.guide-row {
    display: flex;
    justify-content: space-around;
    text-align: center;
    gap: 8px;
}
.guide-step {
    font-size: 13px;
    font-weight: 900;
    color: #1e3a8a;
}
.guide-icon {
    width: 44px;
    height: 44px;
    border-radius: 999px;
    background: white;
    border: 1px solid #bfdbfe;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    margin: 0 auto 5px auto;
}
.qr-box {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 12px;
}
hr {
    margin-top: 28px;
    margin-bottom: 28px;
}
@media (max-width: 640px) {
    .hero-title { font-size: 34px; }
    .quick-tabs { grid-template-columns: repeat(2, 1fr); }
    .latest-card { grid-template-columns: 58px 1fr 74px; }
    .latest-time { font-size: 13px; min-height: 86px; }
    .latest-img { width: 62px; height: 62px; }
    .metric-value { font-size: 28px; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.caption(APP_VERSION)

st.markdown(
    """
<div class="hero">
    <div class="hero-logo">🚨</div>
    <div>
        <div class="hero-title">QUALITY <span>ALERT</span></div>
        <div class="hero-sub">ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด</div>
    </div>
</div>
<div class="quick-tabs">
    <div class="quick-tab"><div class="quick-icon">📷</div>ถ่ายรูป</div>
    <div class="quick-tab"><div class="quick-icon">💬</div>บอกอาการ</div>
    <div class="quick-tab"><div class="quick-icon">#</div>ใส่จำนวน</div>
    <div class="quick-tab"><div class="quick-icon">📨</div>ส่งแจ้งเตือน</div>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown(
    f'<div class="dept-card">{DEPT_ICONS.get(dept_qr, "📍")} หน่วยงาน : {dept_qr}</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="form-card">
    <div class="form-title">📝 กรอกข้อมูลปัญหา</div>
    <div class="form-sub">กรอกเฉพาะข้อมูลจำเป็น แล้วส่งแจ้งเตือนได้ทันที</div>
</div>
""",
    unsafe_allow_html=True,
)

with st.form("alert_form", clear_on_submit=True):
    reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")

    department = dept_qr
    st.caption(f"ระบบเลือกหน่วยงานจาก QR อัตโนมัติ: {department}")

    defect = st.selectbox("🔍 อาการที่พบ", DEFECTS[department])

    qty = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, step=1)

    impact = st.radio("⚠️ หากไม่พบ จะหลุดถึง", IMPACT_LEVELS, horizontal=True)

    severity = st.radio("🚦 ระดับความรุนแรง", SEVERITY_LIST, horizontal=True)

    note = st.text_area(
        "📝 รายละเอียดเพิ่มเติม",
        placeholder="เช่น จุดที่พบ / สาเหตุเบื้องต้น / วิธีป้องกัน",
    )

    image = None
    upload_image = None

    with st.expander("📷 เพิ่มรูปภาพ / ถ่ายภาพประกอบ (ไม่บังคับ)", expanded=False):
        image = st.camera_input("📷 ถ่ายภาพ")
        upload_image = st.file_uploader(
            "หรือเลือกภาพจากเครื่อง",
            type=["jpg", "jpeg", "png"],
        )

    submitted = st.form_submit_button("🚨 ส่งแจ้งเตือน")


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
                    <div class="success-value">{department}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.balloons()


st.divider()
st.markdown('<div class="dash-title">📊 DASHBOARD หัวหน้างาน</div>', unsafe_allow_html=True)

df = load_data()

if df.empty:
    st.info("ยังไม่มีข้อมูล")
else:
    df_dash = df.copy()
    df_dash["จำนวน"] = pd.to_numeric(df_dash["จำนวน"], errors="coerce").fillna(0).astype(int)
    df_dash["มูลค่าป้องกัน"] = pd.to_numeric(df_dash["มูลค่าป้องกัน"], errors="coerce").fillna(0)

    total_cases = len(df_dash)
    total_qty = int(df_dash["จำนวน"].sum())
    total_reporters = (
        df_dash["ผู้แจ้ง"]
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )
    total_value = int(df_dash["มูลค่าป้องกัน"].sum())

    c1, c2 = st.columns(2)
    with c1:
        make_metric_card("แจ้งทั้งหมด", f"{total_cases:,} เคส", "🔔", "metric-red")
        make_metric_card("ป้องกันได้", f"{total_qty:,} ใบ", "🛡️", "metric-green")
    with c2:
        make_metric_card("ผู้มีส่วนร่วม", f"{total_reporters:,} คน", "👥", "metric-blue")
        make_metric_card("มูลค่าป้องกัน", f"{total_value:,} บาท", "💰", "metric-yellow")

    st.markdown('<div class="section-title">📌 รายการแจ้งเตือนล่าสุด</div>', unsafe_allow_html=True)
    latest_df = df_dash.tail(5).sort_index(ascending=False)
    for _, row in latest_df.iterrows():
        make_latest_card(row)

    st.markdown('<div class="section-title">🏆 Top 5 ผู้มีส่วนร่วม</div>', unsafe_allow_html=True)

    reporter_df = df_dash[["ผู้แจ้ง", "หน่วยงาน", "จำนวน"]].copy()
    reporter_df["ผู้แจ้ง"] = reporter_df["ผู้แจ้ง"].astype(str).str.strip()
    reporter_df = reporter_df[reporter_df["ผู้แจ้ง"] != ""]

    if reporter_df.empty:
        st.info("ยังไม่มีข้อมูลผู้แจ้ง")
    else:
        top_reporter_qty = (
            reporter_df.groupby("ผู้แจ้ง")["จำนวน"]
            .sum()
            .reset_index()
            .rename(columns={"จำนวน": "จำนวนใบ"})
        )

        top_reporter_case = (
            reporter_df.groupby("ผู้แจ้ง")
            .size()
            .reset_index(name="จำนวนเคส")
        )

        top_reporter_dept = (
            reporter_df.groupby("ผู้แจ้ง")["หน่วยงาน"]
            .agg(lambda x: str(x.dropna().iloc[-1]) if len(x.dropna()) else "")
            .reset_index()
        )

        top_reporter = pd.merge(top_reporter_qty, top_reporter_case, on="ผู้แจ้ง", how="left")
        top_reporter = pd.merge(top_reporter, top_reporter_dept, on="ผู้แจ้ง", how="left")
        top_reporter["จำนวนใบ"] = pd.to_numeric(top_reporter["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
        top_reporter["จำนวนเคส"] = pd.to_numeric(top_reporter["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
        top_reporter = top_reporter.nlargest(5, "จำนวนใบ").reset_index(drop=True)

        for i, row in top_reporter.iterrows():
            make_rank_card(
                i + 1,
                row["ผู้แจ้ง"],
                int(row["จำนวนใบ"]),
                int(row["จำนวนเคส"]),
                str(row.get("หน่วยงาน", "")),
                is_top=(i == 0),
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
        top_defect["จำนวนใบ"] = pd.to_numeric(top_defect["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
        top_defect["จำนวนเคส"] = pd.to_numeric(top_defect["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
        top_defect = top_defect.nlargest(5, "จำนวนใบ").reset_index(drop=True)

        for i, row in top_defect.iterrows():
            make_defect_card(i + 1, row["อาการ"], int(row["จำนวนใบ"]), int(row["จำนวนเคส"]))


st.markdown(
    """
<div class="bottom-guide">
    <div class="guide-title">วิธีใช้งานง่ายๆ</div>
    <div class="guide-row">
        <div class="guide-step"><div class="guide-icon">📱</div>สแกน QR</div>
        <div class="guide-step"><div class="guide-icon">📷</div>ถ่ายรูป</div>
        <div class="guide-step"><div class="guide-icon">📝</div>กรอกข้อมูล</div>
        <div class="guide-step"><div class="guide-icon">📨</div>ส่งแจ้งเตือน</div>
    </div>
</div>
""",
    unsafe_allow_html=True,
)

st.subheader("🔗 ลิงก์สำหรับทำ QR")

base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"

for dept in DEPTS:
    st.code(f"{base_url}/?dept={dept}")
