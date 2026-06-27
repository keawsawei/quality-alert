import streamlit as st
from PIL import Image
from datetime import datetime

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="AI",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# DATA MOCK / โครงสร้างต่อฐานข้อมูล
# =========================
MASTER_PC = {
    "PC-1304": {
        "customer": "ลูกค้าตัวอย่าง A",
        "register": "ต้องเทียบ Register ก่อนเดินงาน",
        "print_mark": "Print Mark ต้องอยู่ในกรอบ",
        "barcode": "Barcode ต้องอ่านได้ครบ",
        "prompt": "ตรวจสีเหลื่อม หมึกเลอะ Print Mark และ Register เป็นหลัก"
    },
    "PC-2201": {
        "customer": "ลูกค้าตัวอย่าง B",
        "register": "ตรวจขอบซ้าย/ขวา",
        "print_mark": "ไม่เน้น",
        "barcode": "ห้าม Barcode ขาด/จาง",
        "prompt": "ตรวจ Barcode พิมพ์จาง Pin Hole และรอยขีด"
    },
}

DEFECTS = [
    {"icon": "💦", "name": "สีเหลื่อม", "class": "d-blue"},
    {"icon": "🟠", "name": "หมึกเลอะ", "class": "d-orange"},
    {"icon": "◉", "name": "พิมพ์ตัน", "class": "d-teal"},
    {"icon": "▤", "name": "พิมพ์จาง", "class": "d-purple"},
    {"icon": "●", "name": "Pin Hole", "class": "d-pink"},
    {"icon": "╱╱", "name": "รอยขีด", "class": "d-sky"},
    {"icon": "▥", "name": "Barcode", "class": "d-green"},
    {"icon": "⊕", "name": "Print Mark", "class": "d-amber"},
    {"icon": "•••", "name": "อื่น ๆ", "class": "d-gray"},
    {"icon": "?", "name": "ไม่รู้ว่าปัญหาอะไร", "class": "d-rose"},
]

# =========================
# SESSION
# =========================
if "page" not in st.session_state:
    st.session_state.page = "AI ตรวจงาน"

if "defect" not in st.session_state:
    st.session_state.defect = "สีเหลื่อม"

if "result" not in st.session_state:
    st.session_state.result = False

if "so" not in st.session_state:
    st.session_state.so = ""

if "pc" not in st.session_state:
    st.session_state.pc = ""

if "reporter" not in st.session_state:
    st.session_state.reporter = ""

# =========================
# CSS MOBILE FIRST
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700;800;900&display=swap');

*{
    font-family:'Noto Sans Thai',sans-serif;
    box-sizing:border-box;
}

html, body, .stApp{
    width:100%;
    overflow-x:hidden!important;
}

.stApp{
    background:
        radial-gradient(circle at 15% 0%, rgba(37,99,235,.13), transparent 26%),
        linear-gradient(180deg,#EEF6FF 0%,#FFFFFF 45%,#F8FBFF 100%);
}

.block-container{
    max-width:430px!important;
    padding-top:0!important;
    padding-left:8px!important;
    padding-right:8px!important;
    padding-bottom:20px!important;
}

#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}

/* ================= HEADER ================= */
.hero{
    position:relative;
    overflow:hidden;
    margin:0 -8px 0 -8px;
    padding:18px 12px 30px 12px;
    background:
        radial-gradient(circle at 12% 34%, rgba(56,189,248,.30), transparent 22%),
        radial-gradient(circle at 88% 48%, rgba(14,165,233,.32), transparent 25%),
        linear-gradient(135deg,#061331 0%,#082A69 48%,#0057D9 100%);
    color:white;
    box-shadow:0 12px 28px rgba(0,60,180,.22);
}

.hero:before{
    content:"";
    position:absolute;
    inset:0;
    opacity:.18;
    background-image:
        linear-gradient(90deg, transparent 0 72%, rgba(56,189,248,.45) 73%, transparent 74%),
        linear-gradient(0deg, transparent 0 68%, rgba(56,189,248,.18) 69%, transparent 70%);
    background-size:58px 30px;
    transform:skewX(-18deg);
    transform-origin:right;
}

/* ตัดแท่งขาว/แท่งแสงยาวออก */
.hero:after{
    display:none!important;
}

.hero-inner{
    position:relative;
    z-index:2;
}

.logo-wrap{
    display:flex;
    align-items:center;
    gap:10px;
}

.ai-logo{
    width:62px;
    height:62px;
    min-width:62px;
    border-radius:16px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:31px;
    font-weight:950;
    letter-spacing:-2px;
    color:white;
    background:
        radial-gradient(circle at 35% 25%, rgba(255,255,255,.36), transparent 20%),
        linear-gradient(135deg,#073B8E,#071A3E);
    border:2px solid rgba(56,189,248,.9);
    box-shadow:
        0 0 0 5px rgba(56,189,248,.10),
        0 0 22px rgba(56,189,248,.65),
        inset 0 0 18px rgba(56,189,248,.25);
}

.hero h1{
    margin:0;
    font-size:25px;
    line-height:1;
    font-weight:950;
    letter-spacing:-.5px;
    text-shadow:0 5px 16px rgba(0,0,0,.22);
}

.hero p{
    margin:7px 0 0 0;
    font-size:13px;
    font-weight:800;
    color:#BAE6FD;
}

.hero-time{
    position:absolute;
    right:10px;
    top:7px;
    z-index:3;
    font-size:10px;
    font-weight:900;
    color:#DFF6FF;
}

/* ================= NAV MOBILE ================= */
.nav-panel{
    position:relative;
    z-index:5;
    margin:-18px 0 12px 0;
    background:white;
    border:1px solid #E5EDF8;
    border-radius:14px;
    padding:6px;
    box-shadow:0 12px 24px rgba(15,23,42,.11);
}

div[data-testid="stButton"] button{
    border-radius:12px;
    font-weight:900;
    min-height:42px;
    transition:.15s ease;
    border:1px solid #E2E8F0;
    background:white;
    color:#0F172A;
}

div[data-testid="stButton"] button:hover{
    transform:none;
    border:2px solid #EF4444;
    box-shadow:0 7px 15px rgba(239,68,68,.14);
}

.nav-dash button,
.nav-ai button,
.nav-history button,
.nav-update button,
.nav-master button{
    min-height:40px!important;
    border-radius:10px!important;
    font-size:9px!important;
    font-weight:950!important;
    padding:2px!important;
}

.nav-dash button{background:linear-gradient(135deg,#EAF3FF,#FFFFFF)!important;color:#0B56D9!important;border:1px solid #93C5FD!important;}
.nav-ai button{background:linear-gradient(135deg,#ECFDF5,#FFFFFF)!important;color:#059669!important;border:1px solid #86EFAC!important;}
.nav-history button{background:linear-gradient(135deg,#F5F3FF,#FFFFFF)!important;color:#6D28D9!important;border:1px solid #C4B5FD!important;}
.nav-update button{background:linear-gradient(135deg,#FFF7ED,#FFFFFF)!important;color:#EA580C!important;border:1px solid #FDBA74!important;}
.nav-master button{background:linear-gradient(135deg,#FEF2F2,#FFFFFF)!important;color:#DC2626!important;border:1px solid #FCA5A5!important;}

.active-page button{
    border:2px solid #EF4444!important;
    box-shadow:0 6px 14px rgba(239,68,68,.18)!important;
}

/* ================= PANELS ================= */
.panel{
    background:white;
    border:1px solid #E4ECF7;
    border-radius:16px;
    padding:13px 10px 15px 10px;
    margin-bottom:10px;
    box-shadow:0 7px 18px rgba(15,23,42,.07);
}

.section-title{
    display:flex;
    align-items:center;
    gap:9px;
    color:#071E52;
    font-size:18px;
    font-weight:950;
    margin:0 0 10px 0;
}

.num{
    width:34px;
    height:34px;
    border-radius:10px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-weight:950;
    font-size:18px;
    background:linear-gradient(135deg,#22C55E,#06B6D4);
    box-shadow:0 6px 13px rgba(6,182,212,.20);
}

.thin-line{
    height:1px;
    background:linear-gradient(90deg,#16C784,rgba(14,165,233,.35),transparent);
    margin:0 0 14px 0;
}

/* ================= INPUT ================= */
.stTextInput label{
    font-size:12px!important;
    font-weight:800!important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"]{
    border-radius:11px!important;
    border:1px solid #D8E4F2!important;
    background:#FFFFFF!important;
    font-weight:800!important;
    min-height:42px!important;
}

/* ================= DEFECT BUTTONS ================= */
.defect-card button{
    min-height:82px!important;
    width:100%!important;
    border-radius:12px!important;
    padding:5px 1px!important;
    font-size:10px!important;
    line-height:1.18!important;
    font-weight:950!important;
    color:#0F172A!important;
    border:1px solid #DDE8F6!important;
    box-shadow:0 6px 14px rgba(15,23,42,.06)!important;
    white-space:pre-line!important;
}

.defect-card button:hover{
    border:2px solid #EF4444!important;
    transform:none!important;
    box-shadow:0 9px 18px rgba(239,68,68,.15)!important;
}

.defect-selected-wrap{
    position:relative;
}

.defect-selected-wrap button{
    border:2px solid #EF4444!important;
    box-shadow:0 10px 20px rgba(239,68,68,.18)!important;
}

.defect-selected-wrap:after{
    content:"✓";
    position:absolute;
    top:0;
    right:0;
    width:23px;
    height:23px;
    border-radius:0 9px 0 8px;
    background:#EF4444;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:950;
    font-size:15px;
    z-index:10;
    pointer-events:none;
}

.d-blue button{
    background:radial-gradient(circle at 25% 25%, rgba(59,130,246,.22), transparent 25%),linear-gradient(135deg,#EFF6FF,#FFFFFF)!important;
    border-color:#60A5FA!important;
}
.d-orange button{
    background:radial-gradient(circle at 25% 25%, rgba(249,115,22,.26), transparent 25%),linear-gradient(135deg,#FFF7ED,#FFFFFF)!important;
    border-color:#FB923C!important;
}
.d-teal button{
    background:radial-gradient(circle at 25% 25%, rgba(20,184,166,.26), transparent 25%),linear-gradient(135deg,#ECFEFF,#FFFFFF)!important;
    border-color:#22D3EE!important;
}
.d-purple button{
    background:radial-gradient(circle at 25% 25%, rgba(139,92,246,.24), transparent 25%),linear-gradient(135deg,#F5F3FF,#FFFFFF)!important;
    border-color:#A78BFA!important;
}
.d-pink button{
    background:radial-gradient(circle at 25% 25%, rgba(236,72,153,.24), transparent 25%),linear-gradient(135deg,#FFF1F2,#FFFFFF)!important;
    border-color:#F472B6!important;
}
.d-sky button{
    background:radial-gradient(circle at 25% 25%, rgba(14,165,233,.24), transparent 25%),linear-gradient(135deg,#EFF6FF,#FFFFFF)!important;
    border-color:#38BDF8!important;
}
.d-green button{
    background:radial-gradient(circle at 25% 25%, rgba(34,197,94,.24), transparent 25%),linear-gradient(135deg,#F0FDF4,#FFFFFF)!important;
    border-color:#4ADE80!important;
}
.d-amber button{
    background:radial-gradient(circle at 25% 25%, rgba(245,158,11,.24), transparent 25%),linear-gradient(135deg,#FFFBEB,#FFFFFF)!important;
    border-color:#F59E0B!important;
}
.d-gray button{
    background:radial-gradient(circle at 25% 25%, rgba(100,116,139,.16), transparent 25%),linear-gradient(135deg,#F8FAFC,#FFFFFF)!important;
    border-color:#CBD5E1!important;
}
.d-rose button{
    background:radial-gradient(circle at 25% 25%, rgba(244,63,94,.22), transparent 25%),linear-gradient(135deg,#FDF2F8,#FFFFFF)!important;
    border-color:#FB7185!important;
}

.selected-result{
    margin-top:10px;
    background:linear-gradient(135deg,#FFF1F2,#FFE4E6);
    border:2px solid #EF4444;
    color:#B91C1C;
    border-radius:12px;
    padding:8px;
    font-size:13px;
    font-weight:950;
    text-align:center;
}

/* ================= UPLOAD ================= */
.fake-upload{
    min-height:145px;
    border:2px dashed #9DBBFF;
    border-radius:14px;
    background:linear-gradient(135deg,#F8FBFF,#FFFFFF);
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    color:#1D4ED8;
    text-align:center;
    font-weight:950;
}

.fake-upload .cam{
    width:58px;
    height:58px;
    border-radius:50%;
    background:linear-gradient(135deg,#DBEAFE,#EEF2FF);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:30px;
    margin-bottom:9px;
}

.preview-box{
    min-height:145px;
    border:1px solid #E2E8F0;
    border-radius:14px;
    background:#F8FAFC;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#94A3B8;
    font-weight:800;
    text-align:center;
    padding:12px;
}

/* ================= RESULT ================= */
.gauge{
    width:118px;
    height:118px;
    border-radius:50%;
    background:conic-gradient(#22C55E 0 91%, #DCFCE7 91% 100%);
    display:flex;
    align-items:center;
    justify-content:center;
    margin:8px auto 12px auto;
}

.gauge-inner{
    width:88px;
    height:88px;
    border-radius:50%;
    background:white;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
    color:#15803D;
    font-weight:950;
}

.gauge-num{font-size:27px;line-height:1;}
.gauge-label{font-size:11px;color:#166534;}

.result-status{
    display:flex;
    align-items:flex-start;
    gap:10px;
    margin:10px 0;
}

.check{
    min-width:42px;
    width:42px;
    height:42px;
    border-radius:50%;
    background:#DCFCE7;
    color:#16A34A;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:25px;
    font-weight:950;
}

.result-status h3{
    color:#16A34A;
    font-size:20px;
    margin:0;
    font-weight:950;
}

.result-status p{
    margin:5px 0 0 0;
    color:#64748B;
    font-weight:800;
    font-size:12px;
}

.ai-image-box{
    border-radius:14px;
    background:#F3F6FB;
    border:1px solid #E2E8F0;
    display:flex;
    align-items:center;
    justify-content:center;
    min-height:115px;
    color:#94A3B8;
    font-weight:800;
    text-align:center;
}

.save-btn button{
    background:linear-gradient(90deg,#16C784,#22C55E)!important;
    color:white!important;
    border:none!important;
    font-size:16px!important;
}

.send-btn button{
    background:linear-gradient(90deg,#2563EB,#006CFF)!important;
    color:white!important;
    border:none!important;
    font-size:16px!important;
}

.analyze-btn button{
    background:linear-gradient(90deg,#16C784,#0094FF)!important;
    color:white!important;
    border:none!important;
    font-size:17px!important;
    min-height:52px!important;
}

/* ================= DASHBOARD ================= */
.kpi{
    border-radius:14px;
    padding:13px;
    border:1px solid #E2E8F0;
    font-weight:950;
    box-shadow:0 7px 17px rgba(15,23,42,.06);
}

.kpi small{
    display:block;
    color:#64748B;
    margin-bottom:6px;
    font-size:11px;
}

.kpi strong{
    font-size:28px;
    color:#071E52;
}

.kpi1{background:linear-gradient(135deg,#EAF3FF,#FFFFFF);border-color:#93C5FD;}
.kpi2{background:linear-gradient(135deg,#ECFDF5,#FFFFFF);border-color:#86EFAC;}
.kpi3{background:linear-gradient(135deg,#FEF2F2,#FFFFFF);border-color:#FCA5A5;}
.kpi4{background:linear-gradient(135deg,#F5F3FF,#FFFFFF);border-color:#C4B5FD;}
</style>
""", unsafe_allow_html=True)

# =========================
# HEADER
# =========================
now_time = datetime.now().strftime("%H:%M น.")
st.markdown(f"""
<div class="hero">
    <div class="hero-time">⏱ {now_time}</div>
    <div class="hero-inner">
        <div class="logo-wrap">
            <div class="ai-logo">AI</div>
            <div>
                <h1>AI ผู้ช่วยคนคัด</h1>
                <p>ถ่ายรูป · ส่งตรวจ · ดูผลเลย</p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# =========================
# NAV
# =========================
st.markdown('<div class="nav-panel">', unsafe_allow_html=True)
nav_cols = st.columns(5)

navs = [
    ("📊", "nav-dash", "Dashboard"),
    ("🔍 AI", "nav-ai", "AI ตรวจงาน"),
    ("🕘", "nav-history", "ประวัติ"),
    ("🟠", "nav-update", "อัปเดตข้อมูล"),
    ("⚙️", "nav-master", "มาสเตอร์"),
]

for col, (label, css, page) in zip(nav_cols, navs):
    with col:
        st.markdown(f'<div class="{css} {"active-page" if st.session_state.page == page else ""}">', unsafe_allow_html=True)
        if st.button(label, use_container_width=True, key=f"nav_{page}"):
            st.session_state.page = page
            st.session_state.result = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# =========================
# DASHBOARD
# =========================
if st.session_state.page == "Dashboard":
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">1</div>Dashboard วันนี้</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="kpi kpi1"><small>งานตรวจวันนี้</small><strong>0</strong></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="kpi kpi2"><small>ผ่าน</small><strong>0</strong></div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown('<div class="kpi kpi3"><small>พบปัญหา</small><strong>0</strong></div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="kpi kpi4"><small>รอหัวหน้า</small><strong>0</strong></div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">2</div>รายการล่าสุด</div>
        <div class="thin-line"></div>
        <div class="preview-box">ยังไม่มีข้อมูลวันนี้</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# AI PAGE
# =========================
elif st.session_state.page == "AI ตรวจงาน":

    # 1 DATA
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">1</div>ข้อมูลงาน</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    st.session_state.so = st.text_input("SO", value=st.session_state.so, placeholder="ค้นหา SO")
    st.session_state.pc = st.text_input("PC", value=st.session_state.pc, placeholder="ค้นหา PC")
    st.session_state.reporter = st.text_input("คนแจ้ง", value=st.session_state.reporter, placeholder="ชื่อคนแจ้ง")

    st.markdown("</div>", unsafe_allow_html=True)

    # 2 DEFECT
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">2</div>เลือกอาการ</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    for row_start in range(0, len(DEFECTS), 2):
        cols = st.columns(2, gap="small")
        for col, idx in zip(cols, range(row_start, min(row_start + 2, len(DEFECTS)))):
            d = DEFECTS[idx]
            selected = st.session_state.defect == d["name"]
            selected_css = "defect-selected-wrap" if selected else ""
            label = f"{d['icon']}\n\n{d['name']}"
            with col:
                st.markdown(
                    f'<div class="defect-card {d["class"]} {selected_css}">',
                    unsafe_allow_html=True
                )
                if st.button(label, key=f"select_{idx}", use_container_width=True):
                    st.session_state.defect = d["name"]
                    st.session_state.result = False
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="selected-result">✓ เลือกอยู่ : {st.session_state.defect}</div>',
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 3 UPLOAD
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">3</div>ถ่ายรูปงาน</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="fake-upload">
        <div class="cam">📷</div>
        แตะเพื่อถ่ายรูป<br>
        <span style="font-size:13px;color:#64748B;">หรือเลือกจากแกลเลอรี · JPG, PNG</span>
    </div>
    """, unsafe_allow_html=True)

    uploaded = st.file_uploader("ถ่ายรูป / อัปโหลด", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)
    else:
        img = None
        st.markdown('<div class="preview-box">จะแสดงรูปที่ถ่ายที่นี่</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 4 RESULT
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">4</div>ผลการวิเคราะห์ (AI)</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
    if st.button("🚀 ส่งตรวจด้วย AI", use_container_width=True, key="analyze_btn"):
        if uploaded:
            st.session_state.result = True
        else:
            st.warning("ถ่ายรูปก่อน")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.result and uploaded:
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.markdown("""
        <div class="gauge">
            <div class="gauge-inner">
                <div class="gauge-num">91%</div>
                <div class="gauge-label">ความมั่นใจ</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-status">
            <div class="check">✓</div>
            <div>
                <h3>ไม่พบความผิดปกติ</h3>
                <p>คุณภาพงาน : ผ่านมาตรฐาน</p>
                <p>SO : {st.session_state.so or "-"} / PC : {st.session_state.pc or "-"}</p>
                <p>คนแจ้ง : {st.session_state.reporter or "-"}</p>
                <p>ประเภทที่ตรวจ : {st.session_state.defect}</p>
                <p>เวลา : {now}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ai-image-box">ภาพผลการวิเคราะห์</div>', unsafe_allow_html=True)

        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        st.button("💾 บันทึกผลการตรวจ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        st.button("👤 ส่งงานต่อ / เรียกหัวหน้าตรวจ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-box">รอส่งรูปเพื่อวิเคราะห์</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# HISTORY
# =========================
elif st.session_state.page == "ประวัติ":
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">1</div>ข้อมูลย้อนหลัง</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    st.date_input("วันที่")
    st.text_input("ค้นหา SO / PC")
    st.selectbox("สถานะ", ["ทั้งหมด", "ผ่าน", "พบปัญหา", "รอหัวหน้า"])

    st.button("🔎 ค้นหา", use_container_width=True)
    st.button("📤 Export Excel", use_container_width=True)
    st.markdown('<div class="preview-box">ยังไม่มีข้อมูลย้อนหลัง</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# UPDATE DATA
# =========================
elif st.session_state.page == "อัปเดตข้อมูล":
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">1</div>อัปเดตข้อมูล</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    st.text_input("SO")
    st.text_input("PC")
    st.text_input("ลูกค้า")
    st.text_area("ข้อกำหนด")
    st.text_area("Prompt AI")
    st.button("💾 บันทึกข้อมูล", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# MASTER
# =========================
elif st.session_state.page == "มาสเตอร์":
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">1</div>มาสเตอร์</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    st.info("เก็บ Master PC / ลูกค้า / Register / Print Mark / Barcode / Prompt AI")
    st.text_input("PC")
    st.text_input("ลูกค้า")
    st.text_area("Register")
    st.text_area("Print Mark")
    st.text_area("Barcode")
    st.text_area("Prompt AI")
    st.button("💾 บันทึก Master", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
