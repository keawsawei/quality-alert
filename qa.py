import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

APP_VERSION = "V4-CLEAN-DASHBOARD"

DATA_FILE = Path("quality_alert.xlsx")
IMG_DIR = Path("images")
IMG_DIR.mkdir(exist_ok=True)

DEPTS = ["ตอก", "คัด", "กาว", "ขึ้นรูป"]

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


def make_rank_card(rank, title, qty, case, icon="🏆"):
    st.markdown(
        f"""
        <div class="rank-card">
            <div class="rank-left">
                <div class="rank-no">{rank}</div>
                <div>
                    <div class="rank-name">{icon} {title}</div>
                    <div class="rank-sub">{case:,} เคส</div>
                </div>
            </div>
            <div class="rank-value">{qty:,} ใบ</div>
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
    qty = int(pd.to_numeric(row.get("จำนวน", 0), errors="coerce") or 0)
    impact = str(row.get("หลุดถึง", ""))
    severity = str(row.get("ระดับ", ""))
    value = int(pd.to_numeric(row.get("มูลค่าป้องกัน", 0), errors="coerce") or 0)
    status = str(row.get("สถานะ", ""))

    st.markdown(
        f"""
        <div class="latest-card">
            <div class="latest-top">
                <b>{defect}</b>
                <span class="status-badge">{status}</span>
            </div>
            <div class="latest-line">{dept} | {qty:,} ใบ | หลุดถึง {impact} | ระดับ {severity}</div>
            <div class="latest-line">👤 {reporter} | 🕒 {date} {time} | 💰 {value:,} บาท</div>
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
    padding-top: 2rem;
    max-width: 760px;
}
.big-title {
    font-size: 44px;
    font-weight: 900;
    text-align: center;
}
.sub-title {
    font-size: 22px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 18px;
}
.dept-card {
    background: linear-gradient(135deg, #e8f1ff, #f5f9ff);
    border: 1px solid #d7e8ff;
    border-radius: 18px;
    padding: 16px;
    font-size: 22px;
    font-weight: 900;
    text-align: center;
    color: #0b4ea2;
    margin-bottom: 18px;
}
.success-card {
    background: #e9ffe9;
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    font-size: 22px;
    font-weight: 800;
    color: #15803d;
}
.stButton > button {
    width: 100%;
    height: 60px;
    font-size: 22px;
    font-weight: 900;
    border-radius: 14px;
    background: #ef233c;
    color: white;
}
.dash-title {
    font-size: 34px;
    font-weight: 950;
    margin: 22px 0 14px 0;
}
.section-title {
    font-size: 28px;
    font-weight: 950;
    margin: 34px 0 14px 0;
}
.metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 20px;
    padding: 18px 18px;
    box-shadow: 0 6px 20px rgba(15, 23, 42, 0.06);
    margin-bottom: 12px;
}
.metric-label {
    font-size: 16px;
    font-weight: 800;
    color: #64748b;
}
.metric-value {
    font-size: 38px;
    font-weight: 950;
    color: #0f172a;
    margin-top: 8px;
}
.rank-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 18px;
    padding: 14px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}
.rank-left {
    display: flex;
    align-items: center;
    gap: 14px;
}
.rank-no {
    width: 38px;
    height: 38px;
    border-radius: 999px;
    background: #eef2ff;
    color: #1e3a8a;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    font-weight: 950;
}
.rank-name {
    font-size: 20px;
    font-weight: 900;
    color: #111827;
}
.rank-sub {
    font-size: 14px;
    font-weight: 700;
    color: #64748b;
}
.rank-value {
    font-size: 24px;
    font-weight: 950;
    color: #dc2626;
}
.latest-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-left: 6px solid #ef233c;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 10px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
}
.latest-top {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    font-size: 20px;
    color: #111827;
}
.latest-line {
    font-size: 15px;
    color: #475569;
    margin-top: 5px;
    font-weight: 650;
}
.status-badge {
    background: #fee2e2;
    color: #991b1b;
    border-radius: 999px;
    padding: 4px 10px;
    font-size: 13px;
    font-weight: 900;
}
hr {
    margin-top: 28px;
    margin-bottom: 28px;
}
</style>
""",
    unsafe_allow_html=True,
)

st.caption(APP_VERSION)
st.markdown('<div class="big-title">🚨 QUALITY ALERT</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dept-card">📍 หน่วยงาน : {dept_qr}</div>', unsafe_allow_html=True)

with st.form("alert_form", clear_on_submit=True):
    reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")

    department = dept_qr
    st.caption(f"ระบบเลือกหน่วยงานจาก QR อัตโนมัติ: {department}")

    image = st.camera_input("📷 ถ่ายรูปหน้างาน")

    if image is None:
        image = st.file_uploader("หรือแนบรูปจากเครื่อง", type=["jpg", "jpeg", "png"])

    defect = st.selectbox("🔍 อาการที่พบ", DEFECTS[department])

    qty = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, step=1)

    impact = st.radio("⚠️ หากไม่พบ จะหลุดถึง", IMPACT_LEVELS, horizontal=True)

    severity = st.radio("🚦 ระดับความรุนแรง", SEVERITY_LIST, horizontal=True)

    note = st.text_area(
        "📝 รายละเอียดเพิ่มเติม",
        placeholder="เช่น จุดที่พบ / สาเหตุเบื้องต้น / วิธีป้องกัน",
    )

    submitted = st.form_submit_button("🚨 แจ้งปัญหาทันที")


if submitted:
    if not reporter.strip():
        st.error("กรุณาใส่ชื่อผู้แจ้ง")
        st.stop()

    now = datetime.now()
    img_path = ""

    if image is not None:
        img_name = f"{now.strftime('%Y%m%d_%H%M%S')}_{department}.jpg"
        img_path = IMG_DIR / img_name
        with open(img_path, "wb") as f:
            f.write(image.getbuffer())

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

    st.markdown(
        f"""
        <div class="success-card">
        ✅ แจ้งเตือนสำเร็จ<br>
        ขอบคุณที่ช่วยป้องกันงานเสีย<br><br>
        🛡️ คุณช่วยป้องกันได้ {int(qty):,} ใบ<br>
        💰 ประเมินมูลค่า {damage_value:,.0f} บาท
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.balloons()


st.divider()
st.markdown('<div class="dash-title">📊 DASHBOARD</div>', unsafe_allow_html=True)

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
        st.markdown(f'<div class="metric-card"><div class="metric-label">🚨 แจ้งทั้งหมด</div><div class="metric-value">{total_cases:,} เคส</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="metric-label">👤 ผู้มีส่วนร่วม</div><div class="metric-value">{total_reporters:,} คน</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">🛡️ ป้องกันได้</div><div class="metric-value">{total_qty:,} ใบ</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div class="metric-label">💰 มูลค่าป้องกัน</div><div class="metric-value">{total_value:,} บาท</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🏆 Top 5 ผู้แจ้ง</div>', unsafe_allow_html=True)

    reporter_df = df_dash[["ผู้แจ้ง", "จำนวน"]].copy()
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

        top_reporter = pd.merge(top_reporter_qty, top_reporter_case, on="ผู้แจ้ง", how="left")
        top_reporter["จำนวนใบ"] = pd.to_numeric(top_reporter["จำนวนใบ"], errors="coerce").fillna(0).astype(int)
        top_reporter["จำนวนเคส"] = pd.to_numeric(top_reporter["จำนวนเคส"], errors="coerce").fillna(0).astype(int)
        top_reporter = top_reporter.nlargest(5, "จำนวนใบ").reset_index(drop=True)

        for i, row in top_reporter.iterrows():
            make_rank_card(i + 1, row["ผู้แจ้ง"], int(row["จำนวนใบ"]), int(row["จำนวนเคส"]), "👤")

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
        top_defect = top_defect.nlargest(len(top_defect), "จำนวนใบ").reset_index(drop=True)

        for i, row in top_defect.iterrows():
            make_rank_card(i + 1, row["อาการ"], int(row["จำนวนใบ"]), int(row["จำนวนเคส"]), "🔎")

    st.markdown('<div class="section-title">📋 รายการล่าสุด</div>', unsafe_allow_html=True)

    latest_df = df_dash.tail(5).sort_index(ascending=False)
    for _, row in latest_df.iterrows():
        make_latest_card(row)


st.divider()
st.subheader("🔗 ลิงก์สำหรับทำ QR")

base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"

for dept in DEPTS:
    st.code(f"{base_url}/?dept={dept}")
