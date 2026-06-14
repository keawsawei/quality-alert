import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="QUALITY ALERT",
    page_icon="🚨",
    layout="centered"
)

DATA_FILE = Path("quality_alert.xlsx")
IMG_DIR = Path("images")
IMG_DIR.mkdir(exist_ok=True)

DEPTS = ["ตอก", "คัด", "กาว", "ขึ้นรูป"]
DEFECTS = [
    "ตอกหลุด",
    "ตอกไม่ครบ",
    "กาวไม่ติด",
    "กาวล้น",
    "ขึ้นรูปเบี้ยว",
    "พิมพ์เลื่อน",
    "สีผิด",
    "งานขาด",
    "งานเปื้อน",
    "อื่นๆ"
]
IMPACT_LEVELS = ["คัด", "กาว", "ขึ้นรูป", "ลูกค้า"]
SEVERITY_LIST = ["ต่ำ", "กลาง", "สูง"]

COST_PER_SHEET = 2.5


# =========================
# LOAD DATA
# =========================
def load_data():
    if DATA_FILE.exists():
        try:
            return pd.read_excel(DATA_FILE)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def save_data(df):
    df.to_excel(DATA_FILE, index=False)


# =========================
# QR PARAM
# =========================
dept_qr = st.query_params.get("dept", "ตอก")

if dept_qr not in DEPTS:
    dept_qr = "ตอก"


# =========================
# HEADER
# =========================
st.markdown("""
# 🚨 QUALITY ALERT
### ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด
""")

st.info(f"📍 หน่วยงานจาก QR: **{dept_qr}**")


# =========================
# FORM
# =========================
with st.form("alert_form", clear_on_submit=True):

    reporter = st.text_input(
        "👤 ผู้แจ้ง",
        placeholder="ใส่ชื่อผู้แจ้ง"
    )

    department = st.selectbox(
        "🏭 หน่วยงาน",
        DEPTS,
        index=DEPTS.index(dept_qr)
    )

    image = st.file_uploader(
        "📸 แนบรูปภาพ",
        type=["jpg", "jpeg", "png"]
    )

    defect = st.selectbox(
        "🔍 อาการที่พบ",
        DEFECTS
    )

    qty = st.number_input(
        "🔢 จำนวนที่พบ / ใบ",
        min_value=1,
        step=1
    )

    impact = st.radio(
        "⚠️ หากไม่พบ จะหลุดถึง",
        IMPACT_LEVELS,
        horizontal=True
    )

    severity = st.radio(
        "🚦 ระดับความรุนแรง",
        SEVERITY_LIST,
        horizontal=True
    )

    note = st.text_area(
        "📝 รายละเอียดเพิ่มเติม",
        placeholder="เช่น จุดที่พบ / สาเหตุเบื้องต้น / วิธีป้องกัน"
    )

    submitted = st.form_submit_button("🚨 ส่งแจ้งเตือน")


# =========================
# SUBMIT
# =========================
if submitted:

    if not reporter.strip():
        st.error("กรุณาใส่ชื่อผู้แจ้ง")
        st.stop()

    now = datetime.now()
    img_path = ""

    if image is not None:
        ext = image.name.split(".")[-1]
        img_name = f"{now.strftime('%Y%m%d_%H%M%S')}_{department}.{ext}"
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
        "สถานะ": "Open"
    }

    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_data(df)

    st.success("✅ แจ้งเตือนสำเร็จ บันทึกลง Excel แล้ว")
    st.balloons()


# =========================
# DASHBOARD
# =========================
st.divider()
st.subheader("📊 DASHBOARD")

df = load_data()

if df.empty:
    st.info("ยังไม่มีข้อมูล")
else:
    total_cases = len(df)
    total_qty = df["จำนวน"].sum()
    total_reporters = df["ผู้แจ้ง"].nunique()
    total_value = df["มูลค่าป้องกัน"].sum()

    c1, c2 = st.columns(2)
    c1.metric("🚨 แจ้งทั้งหมด", f"{total_cases} เคส")
    c2.metric("🛡️ ป้องกันได้", f"{total_qty:,.0f} ใบ")

    c3, c4 = st.columns(2)
    c3.metric("👤 ผู้มีส่วนร่วม", f"{total_reporters} คน")
    c4.metric("💰 มูลค่าป้องกัน", f"{total_value:,.0f} บาท")

    st.divider()

    st.write("### 🏆 Top 5 ผู้แจ้ง")
    top_reporter = (
        df.groupby("ผู้แจ้ง")
        .agg(
            จำนวนใบ=("จำนวน", "sum"),
            จำนวนเคส=("ผู้แจ้ง", "count")
        )
        .sort_values("จำนวนใบ", ascending=False)
        .reset_index()
        .head(5)
    )
    st.dataframe(top_reporter, use_container_width=True)

    st.write("### 🔍 Top อาการ")
    top_defect = (
        df.groupby("อาการ")
        .agg(
            จำนวนใบ=("จำนวน", "sum"),
            จำนวนเคส=("อาการ", "count")
        )
        .sort_values("จำนวนใบ", ascending=False)
        .reset_index()
    )
    st.dataframe(top_defect, use_container_width=True)

    st.write("### ⚠️ หลุดถึงจุดไหน")
    impact_df = (
        df.groupby("หลุดถึง")
        .agg(
            จำนวนใบ=("จำนวน", "sum"),
            จำนวนเคส=("หลุดถึง", "count")
        )
        .sort_values("จำนวนใบ", ascending=False)
        .reset_index()
    )
    st.dataframe(impact_df, use_container_width=True)

    st.write("### 📋 รายการล่าสุด")
    st.dataframe(
        df.tail(10).sort_index(ascending=False),
        use_container_width=True
    )


# =========================
# QR LINK
# =========================
st.divider()
st.subheader("🔗 ลิงก์สำหรับทำ QR")

base_url = "http://localhost:8501"

for dept in DEPTS:
    st.code(f"{base_url}/?dept={dept}")