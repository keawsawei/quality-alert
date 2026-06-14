import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="QUALITY ALERT", page_icon="🚨", layout="centered")

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

    df["มูลค่าป้องกัน"] = pd.to_numeric(
        df["มูลค่าป้องกัน"], errors="coerce"
    ).fillna(0)

    mask = df["มูลค่าป้องกัน"] <= 0
    df.loc[mask, "มูลค่าป้องกัน"] = df.loc[mask, "จำนวน"] * COST_PER_SHEET

    return df


def save_data(df):
    df.to_excel(DATA_FILE, index=False)


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
    background: #e8f1ff;
    border-radius: 14px;
    padding: 16px;
    font-size: 22px;
    font-weight: 800;
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
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">🚨 QUALITY ALERT</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">ทุกคนคือ QA ป้องกันก่อนเสีย ส่งก่อนรอด</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="dept-card">📍 หน่วยงาน : {dept_qr}</div>',
    unsafe_allow_html=True,
)

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
st.subheader("📊 DASHBOARD")

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
    c1.metric("🚨 แจ้งทั้งหมด", f"{total_cases} เคส")
    c2.metric("🛡️ ป้องกันได้", f"{total_qty:,} ใบ")

    c3, c4 = st.columns(2)
    c3.metric("👤 ผู้มีส่วนร่วม", f"{total_reporters} คน")
    c4.metric("💰 มูลค่าป้องกัน", f"{total_value:,} บาท")

    st.write("### 🏆 Top 5 ผู้แจ้ง")

    reporter_df = df_dash.copy()
    reporter_df["ผู้แจ้ง"] = reporter_df["ผู้แจ้ง"].astype(str).str.strip()
    reporter_df = reporter_df[reporter_df["ผู้แจ้ง"] != ""]

    if reporter_df.empty:
        st.info("ยังไม่มีข้อมูลผู้แจ้ง")
    else:
        top_reporter = reporter_df.groupby("ผู้แจ้ง", as_index=False)["จำนวน"].sum()
        case_count = reporter_df.groupby("ผู้แจ้ง", as_index=False).size()

        top_reporter = top_reporter.merge(case_count, on="ผู้แจ้ง", how="left")
        top_reporter = top_reporter.rename(
            columns={
                "จำนวน": "จำนวนใบ",
                "size": "จำนวนเคส",
            }
        )

        if "จำนวนใบ" not in top_reporter.columns:
            top_reporter["จำนวนใบ"] = 0

        if "จำนวนเคส" not in top_reporter.columns:
            top_reporter["จำนวนเคส"] = 0

        top_reporter = top_reporter.sort_values(
            by="จำนวนใบ",
            ascending=False,
        ).head(5)

        top_reporter["จำนวนใบ"] = pd.to_numeric(
            top_reporter["จำนวนใบ"], errors="coerce"
        ).fillna(0).astype(int)

        top_reporter["จำนวนเคส"] = pd.to_numeric(
            top_reporter["จำนวนเคส"], errors="coerce"
        ).fillna(0).astype(int)

        st.dataframe(
            top_reporter[["ผู้แจ้ง", "จำนวนใบ", "จำนวนเคส"]],
            use_container_width=True,
            hide_index=True,
        )

    st.write("### 🔍 Top อาการ")

    defect_df = df_dash.copy()
    defect_df["อาการ"] = defect_df["อาการ"].astype(str).str.strip()
    defect_df = defect_df[defect_df["อาการ"] != ""]

    if defect_df.empty:
        st.info("ยังไม่มีข้อมูลอาการ")
    else:
        top_defect = defect_df.groupby("อาการ", as_index=False)["จำนวน"].sum()
        defect_case = defect_df.groupby("อาการ", as_index=False).size()

        top_defect = top_defect.merge(defect_case, on="อาการ", how="left")
        top_defect = top_defect.rename(
            columns={
                "จำนวน": "จำนวนใบ",
                "size": "จำนวนเคส",
            }
        )

        if "จำนวนใบ" not in top_defect.columns:
            top_defect["จำนวนใบ"] = 0

        if "จำนวนเคส" not in top_defect.columns:
            top_defect["จำนวนเคส"] = 0

        top_defect = top_defect.sort_values(
            by="จำนวนใบ",
            ascending=False,
        )

        top_defect["จำนวนใบ"] = pd.to_numeric(
            top_defect["จำนวนใบ"], errors="coerce"
        ).fillna(0).astype(int)

        top_defect["จำนวนเคส"] = pd.to_numeric(
            top_defect["จำนวนเคส"], errors="coerce"
        ).fillna(0).astype(int)

        st.dataframe(
            top_defect[["อาการ", "จำนวนใบ", "จำนวนเคส"]],
            use_container_width=True,
            hide_index=True,
        )

    st.write("### 📋 รายการล่าสุด")

    show_cols = [
        "วันที่",
        "เวลา",
        "ผู้แจ้ง",
        "หน่วยงาน",
        "อาการ",
        "จำนวน",
        "หลุดถึง",
        "ระดับ",
        "มูลค่าป้องกัน",
        "สถานะ",
    ]

    show_cols = [col for col in show_cols if col in df_dash.columns]

    latest_df = df_dash[show_cols].tail(10).sort_index(ascending=False)
    st.dataframe(latest_df, use_container_width=True, hide_index=True)


st.divider()
st.subheader("🔗 ลิงก์สำหรับทำ QR")

base_url = "https://quality-alert-9j5j2cx7n5ddb6qsr7wd3j.streamlit.app"

for dept in DEPTS:
    st.code(f"{base_url}/?dept={dept}")
