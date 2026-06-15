import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="Quality Alert",
    page_icon="🚨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700;800&display=swap');

* {
    font-family: 'Noto Sans Thai', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #f8fbff 0%, #eef4ff 45%, #fff7fb 100%);
}

.block-container {
    padding: 1rem 1rem 5.5rem;
    max-width: 460px;
}

/* Hide Streamlit UI */
#MainMenu, footer, header {
    visibility: hidden;
}

.hero {
    background: linear-gradient(135deg, #12326f, #2563eb 45%, #f43f5e);
    border-radius: 28px;
    padding: 24px;
    color: white;
    box-shadow: 0 18px 40px rgba(37, 99, 235, .25);
    margin-bottom: 18px;
}

.app-badge {
    display: inline-block;
    background: rgba(255,255,255,.16);
    border: 1px solid rgba(255,255,255,.25);
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 18px;
}

.hero-row {
    display: flex;
    align-items: center;
    gap: 16px;
}

.logo {
    width: 74px;
    height: 74px;
    border-radius: 24px;
    display: grid;
    place-items: center;
    font-size: 38px;
    background: linear-gradient(145deg, #1d4ed8, #ec4899);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.25);
}

.title {
    font-size: 32px;
    font-weight: 900;
    line-height: 1;
    margin: 0;
}

.title span {
    color: #ff3b5f;
}

.subtitle {
    font-size: 15px;
    font-weight: 700;
    margin-top: 8px;
    opacity: .95;
}

.kpi-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}

.kpi-card {
    background: rgba(255,255,255,.84);
    border: 1px solid rgba(226,232,240,.9);
    border-radius: 22px;
    padding: 18px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, .07);
}

.kpi-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 700;
}

.kpi-value {
    color: #0f172a;
    font-size: 28px;
    font-weight: 900;
    margin-top: 4px;
}

.section-title {
    color: #0f172a;
    font-size: 22px;
    font-weight: 900;
    margin: 18px 0 12px;
}

.alert-card {
    background: rgba(255,255,255,.92);
    border: 1px solid #e5e7eb;
    border-radius: 24px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 12px 28px rgba(15, 23, 42, .07);
}

.alert-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.severity {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-weight: 900;
    font-size: 16px;
    color: #0f172a;
}

.dot {
    width: 12px;
    height: 12px;
    border-radius: 999px;
    display: inline-block;
}

.red { background: #ef4444; }
.orange { background: #f97316; }
.green { background: #22c55e; }
.blue { background: #2563eb; }

.time {
    font-size: 14px;
    font-weight: 800;
    color: #64748b;
}

.problem {
    font-size: 18px;
    font-weight: 900;
    color: #0f172a;
    margin-top: 10px;
}

.meta {
    color: #475569;
    font-size: 14px;
    font-weight: 700;
    margin-top: 6px;
}

.status {
    display: inline-block;
    margin-top: 12px;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 800;
}

.status-red {
    background: #ffe4e9;
    color: #e11d48;
}

.status-orange {
    background: #ffedd5;
    color: #ea580c;
}

.status-green {
    background: #dcfce7;
    color: #16a34a;
}

.form-card {
    background: rgba(255,255,255,.94);
    border: 1px solid #e5e7eb;
    border-radius: 26px;
    padding: 20px;
    box-shadow: 0 14px 34px rgba(15, 23, 42, .08);
}

.stTextInput input,
.stSelectbox div[data-baseweb="select"] > div,
.stNumberInput input,
.stTextArea textarea {
    border-radius: 16px !important;
    border: 1px solid #dbeafe !important;
    background: #fbfdff !important;
}

.stButton > button {
    width: 100%;
    border-radius: 18px;
    border: none;
    padding: 14px 18px;
    font-weight: 900;
    background: linear-gradient(135deg, #2563eb, #ec4899);
    color: white;
    box-shadow: 0 12px 28px rgba(236, 72, 153, .28);
}

.nav {
    position: fixed;
    left: 50%;
    bottom: 14px;
    transform: translateX(-50%);
    width: min(430px, calc(100% - 24px));
    background: rgba(255,255,255,.92);
    backdrop-filter: blur(18px);
    border: 1px solid #e5e7eb;
    border-radius: 26px;
    padding: 10px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    box-shadow: 0 18px 40px rgba(15,23,42,.16);
    z-index: 999;
}

.nav-item {
    text-align: center;
    padding: 8px 4px;
    border-radius: 18px;
    color: #64748b;
    font-size: 11px;
    font-weight: 800;
}

.nav-item.active {
    background: linear-gradient(135deg, #2563eb, #ec4899);
    color: white;
}

.nav-icon {
    font-size: 20px;
    display: block;
    margin-bottom: 2px;
}
</style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "ล่าสุด"

def set_page(name):
    st.session_state.page = name

alerts = [
    {
        "time": "08:51",
        "severity": "ระดับสูง",
        "color": "red",
        "problem": "กาวไม่ติด",
        "machine": "งานขาว",
        "amount": "250 ใบ",
        "person": "ประวิต",
        "status": "กำลังดำเนินการ",
        "status_class": "status-red"
    },
    {
        "time": "08:49",
        "severity": "ระดับสูง",
        "color": "orange",
        "problem": "พิมพ์ไม่ติด",
        "machine": "งานนอก",
        "amount": "25 ใบ",
        "person": "กำลัง",
        "status": "รอตรวจสอบ",
        "status_class": "status-orange"
    },
    {
        "time": "08:45",
        "severity": "ระดับสูง",
        "color": "red",
        "problem": "กระดาษพอง-ล่อน",
        "machine": "ลูกฟูก",
        "amount": "200 ใบ",
        "person": "เขียว",
        "status": "กำลังดำเนินการ",
        "status_class": "status-red"
    },
    {
        "time": "08:30",
        "severity": "ระดับกลาง",
        "color": "green",
        "problem": "หมึกเลอะ",
        "machine": "งานพิมพ์",
        "amount": "10 ใบ",
        "person": "สมชาย",
        "status": "เสร็จสิ้น",
        "status_class": "status-green"
    },
]

st.markdown("""
<div class="hero">
    <div class="app-badge">V18-FIX-THAI-UPLOAD-UI</div>
    <div class="hero-row">
        <div class="logo">🚨</div>
        <div>
            <h1 class="title">QUALITY <span>ALERT</span></h1>
            <div class="subtitle">แจ้งง่าย เห็นเร็ว ป้องกันก่อนเสีย</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kpi-grid">
    <div class="kpi-card">
        <div class="kpi-label">แจ้งวันนี้</div>
        <div class="kpi-value">24</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-label">ระดับสูง</div>
        <div class="kpi-value">8</div>
    </div>
</div>
""", unsafe_allow_html=True)

cols = st.columns(4)
with cols[0]:
    if st.button("🚨 แจ้ง", key="nav_report"):
        set_page("แจ้ง")
with cols[1]:
    if st.button("📋 ล่าสุด", key="nav_latest"):
        set_page("ล่าสุด")
with cols[2]:
    if st.button("📊 สรุป", key="nav_dashboard"):
        set_page("แดชบอร์ด")
with cols[3]:
    if st.button("🔗 QR", key="nav_qr"):
        set_page("คิวอาร์")

page = st.session_state.page

if page == "แจ้ง":
    st.markdown('<div class="section-title">🚨 แจ้งปัญหาหน้างาน</div>', unsafe_allow_html=True)
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    reporter = st.text_input("👤 ผู้แจ้ง", placeholder="ใส่ชื่อผู้แจ้ง")
    machine = st.selectbox("🏭 เครื่อง / จุดงาน", ["ลูกฟูก", "งานขาว", "งานนอก", "งานพิมพ์", "งานเคลือบ"])
    problem = st.selectbox("🔍 ปัญหาที่พบ", ["กระดาษพอง-ล่อน", "พิมพ์ไม่ติด", "กาวไม่ติด", "สีเพี้ยน", "หมึกเลอะ"])
    amount = st.number_input("🔢 จำนวนที่พบ / ใบ", min_value=1, value=1, step=1)
    severity = st.selectbox("⚠️ ระดับความรุนแรง", ["ระดับสูง", "ระดับกลาง", "ระดับต่ำ"])
    detail = st.text_area("📝 รายละเอียดเพิ่มเติม", placeholder="อธิบายรายละเอียดเพิ่มเติม...", max_chars=200)
    image = st.file_uploader("📷 แนบรูปภาพ", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if st.button("ส่งแจ้งปัญหา"):
        st.success("บันทึกการแจ้งปัญหาเรียบร้อยแล้ว")

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "ล่าสุด":
    st.markdown('<div class="section-title">📋 รายการแจ้งเตือนล่าสุด</div>', unsafe_allow_html=True)

    for item in alerts:
        st.markdown(f"""
        <div class="alert-card">
            <div class="alert-top">
                <div class="severity">
                    <span class="dot {item["color"]}"></span>
                    {item["severity"]}
                </div>
                <div class="time">{item["time"]} น.</div>
            </div>
            <div class="problem">{item["problem"]}</div>
            <div class="meta">🏭 {item["machine"]} · 📦 {item["amount"]}</div>
            <div class="meta">👤 {item["person"]} · {datetime.now().strftime("%d/%m/%Y")} · 🏆 3 คะแนน</div>
            <div class="status {item["status_class"]}">{item["status"]}</div>
        </div>
        """, unsafe_allow_html=True)

elif page == "แดชบอร์ด":
    st.markdown('<div class="section-title">📊 แดชบอร์ด</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="kpi-grid">
        <div class="kpi-card">
            <div class="kpi-label">ทั้งหมดเดือนนี้</div>
            <div class="kpi-value">128</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">แก้ไขแล้ว</div>
            <div class="kpi-value">91</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.bar_chart({
        "จำนวนแจ้ง": [18, 25, 14, 32, 24, 15],
    })

elif page == "คิวอาร์":
    st.markdown('<div class="section-title">🔗 คิวอาร์สำหรับแจ้งปัญหา</div>', unsafe_allow_html=True)
    st.info("นำลิงก์หน้านี้ไปสร้าง QR Code สำหรับติดที่หน้างานได้เลย")
    st.code("https://your-quality-alert-app.streamlit.app")

st.markdown(f"""
<div class="nav">
    <div class="nav-item {'active' if page == 'แจ้ง' else ''}">
        <span class="nav-icon">🚨</span>แจ้ง
    </div>
    <div class="nav-item {'active' if page == 'ล่าสุด' else ''}">
        <span class="nav-icon">📋</span>ล่าสุด
    </div>
    <div class="nav-item {'active' if page == 'แดชบอร์ด' else ''}">
        <span class="nav-icon">📊</span>สรุป
    </div>
    <div class="nav-item {'active' if page == 'คิวอาร์' else ''}">
        <span class="nav-icon">🔗</span>QR
    </div>
</div>
""", unsafe_allow_html=True)
