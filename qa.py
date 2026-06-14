import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import base64

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

APP_VERSION = "V12-SIMPLE-ALERT"

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

PROBLEMS = [
    "พิมพ์เลื่อน",
    "สีเพี้ยน",
    "หมึกเปื้อน",
    "Register ไม่ตรง",
    "กาวไม่ติด",
    "กาวล้น",
    "ประกบเบี้ยว",
    "ตอกหลุด",
    "ตอกไม่ครบ",
    "ตอกเบี้ยว",
    "ล็อคไม่เข้า",
    "บากแตก",
    "Diecut ไม่ขาด",
    "กระดาษยับ",
    "กระดาษแตก",
    "งานเปื้อน",
    "งานขาด",
    "อื่นๆ",
]

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
        "ปัญหาที่พบ": "",
        "อาการ": "",
        "จำนวน": 0,
        "ระดับ": "",
        "มูลค่าป้องกัน": 0,
        "รูปภาพ": "",
        "สถานะ": "Open",
    }

    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default

    # migrate old data
    if "ปัญหาที่พบ" in df.columns and "อาการ" in df.columns:
        mask = df["ปัญหาที่พบ"].astype(str).str.strip().isin(["", "nan", "None"])
        df.loc[mask, "ปัญหาที่พบ"] = df.loc[mask, "อาการ"]

    if "เครื่อง" in df.columns:
        df["เครื่อง"] = df["เครื่อง"].astype(str).replace("nan", "").replace("", "ไม่ระบุ")

    df["ปัญหาที่พบ"] = df["ปัญหาที่พบ"].astype(str).replace("nan", "").replace("", "ไม่ระบุ")
    df["จำนวน"] = pd.to_numeric(df["จำนวน"], errors="coerce").fillna(0).astype(int)
    df["มูลค่าป้องกัน"] = pd.to_numeric(df["มูลค่าป้องกัน"], errors="coerce").fillna(0)

    mask_value = df["มูลค่าป้องกัน"] <= 0
    df.loc[mask_value, "มูลค่าป้องกัน"] = df.loc[mask_value, "จำนวน"] * COST_PER_SHEET

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


def severity_style(severity):
    severity = str(severity).strip()
    if severity == "สูง":
        return "#ef233c", "🔴"
    if severity == "กลาง":
        return "#f59e0b", "🟡"
    return "#22c55e", "🟢"


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
    machine = str(row.get("เครื่อง", "ไม่ระบุ"))
    problem = str(row.get("ปัญหาที่พบ", row.get("อาการ", "")))
    qty = safe_int(row.get("จำนวน", 0))
    severity = str(row.get("ระดับ", ""))
    value = safe_int(row.get("มูลค่าป้องกัน", 0))
    img_path = str(row.get("รูปภาพ", "")).strip()

    color, icon = severity_style(severity)
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
                <div class="latest-title">{icon} {problem}</div>
                <div class="latest-sub">{machine} • {qty:,} ใบ</div>
                <div class="latest-sub">👤 {reporter} • {date} • 💰 {value:,} บาท</div>
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
                <div class="rank-sub">{cases:,} เคส</div>
            </div>
            <div class="rank-score">{qty:,}<span> ใบ</span></div>
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
        radial-gradient(circle at top left, rgba(15, 31, 82, .13), transparent 30%),
        radial-gradient(circle at top right, rgba(239, 35, 60, .12), transparent 32%),
        linear-gradient(180deg, #f7faff 0%, #edf4ff 50%, #ffffff 100%);
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
    background: rgba(255,255,255,.88);
    border: 1px solid #e5e7eb;
    border-radius: 28px;
    padding: 18px;
    box-shadow: 0 18px 46px rgba(15, 23, 42, .09);
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
    border-radius: 22px;
    background: linear-gradient(145deg, #071f52, #123a7a);
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
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 30px;
    overflow: hidden;
    box-shadow: 0 22px 55px rgba(15, 23, 42, .12);
    margin-top: 12px;
}

.form-top {
    background: linear-gradient(135deg, #071f52, #123a7a);
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
    ["🚨 แจ้งปัญหา", "📋 ล่าสุด", "📊 Dashboard", "🔗 QR"]
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

        machine = st.selectbox("🏭 เครื่อง", MACHINES, index=0)

        problem_select = st.selectbox("🔍 ปัญหาที่พบ", PROBLEMS, index=0)

        custom_problem = ""
        if problem_select == "อื่นๆ":
            custom_problem = st.text_input("✍️ ระบุปัญหา", placeholder="พิมพ์ปัญหาที่พบ")

        qty = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, step=1)

        severity = st.radio("🚦 ความรุนแรง", SEVERITY_LIST, horizontal=True)

        image = None
        upload_image = None

        with st.expander("📷 เพิ่มรูปภาพ (ไม่บังคับ)", expanded=False):
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

        problem = custom_problem.strip() if problem_select == "อื่นๆ" else problem_select

        if not problem:
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

        new_row = {
            "วันที่": now.strftime("%d/%m/%Y"),
            "เวลา": now.strftime("%H:%M:%S"),
            "ผู้แจ้ง": reporter.strip(),
            "เครื่อง": machine,
            "ปัญหาที่พบ": problem,
            "อาการ": problem,
            "จำนวน": int(qty),
            "ระดับ": severity,
            "มูลค่าป้องกัน": damage_value,
            "รูปภาพ": str(img_path),
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
                        <div class="success-label">ปัญหา</div>
                        <div class="success-value">{problem}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">เครื่อง</div>
                        <div class="success-value">{machine}</div>
                    </div>
                    <div class="success-box">
                        <div class="success-label">จำนวน</div>
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
        metric_card("แจ้งทั้งหมด", f"{total_cases:,} เคส", "🔔", "#ef233c")
        metric_card("ป้องกันได้", f"{total_qty:,} ใบ", "🛡️", "#22c55e")
        metric_card("ผู้มีส่วนร่วม", f"{total_reporters:,} คน", "👥", "#2563eb")
        metric_card("มูลค่าป้องกัน", f"{total_value:,} บาท", "💰", "#f59e0b")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">🏆 Top 5 ผู้แจ้ง</div>', unsafe_allow_html=True)

        reporter_df = df_dash[["ผู้แจ้ง", "จำนวน"]].copy()
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

            top = pd.merge(top_qty, top_case, on="ผู้แจ้ง", how="left")
            top["จำนวนใบ"] = pd.to_numeric(top["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
            top["จำนวนเคส"] = pd.to_numeric(top["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
            top = top.nlargest(5, "จำนวนใบ").reset_index(drop=True)

            for i, row in top.iterrows():
                rank_card(
                    i + 1,
                    str(row["ผู้แจ้ง"]),
                    int(row["จำนวนใบ"]),
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
        '<div style="font-size:20px;font-weight:1000;color:#0f172a;margin-bottom:8px;">🔗 ลิงก์สำหรับทำ QR จุดเดียว</div>',
        unsafe_allow_html=True,
    )
    base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"
    st.code(base_url)
    st.markdown(
        """
        <div class="help-card">
        ใช้ QR จุดเดียว เปิดมาเลือกเครื่อง / ปัญหาที่พบ / จำนวน / ความรุนแรง แล้วส่งได้ทันที
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)
