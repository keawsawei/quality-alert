import streamlit as st
from PIL import Image
from datetime import datetime

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="AI",
    layout="wide",
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
    {"icon":"💦", "name":"สีเหลื่อม", "class":"d-blue"},
    {"icon":"🟠", "name":"หมึกเลอะ", "class":"d-orange"},
    {"icon":"◉", "name":"พิมพ์ตัน", "class":"d-teal"},
    {"icon":"▤", "name":"พิมพ์จาง", "class":"d-purple"},
    {"icon":"●", "name":"Pin Hole", "class":"d-pink"},
    {"icon":"╱╱", "name":"รอยขีด", "class":"d-sky"},
    {"icon":"▥", "name":"Barcode", "class":"d-green"},
    {"icon":"⊕", "name":"Print Mark", "class":"d-amber"},
    {"icon":"•••", "name":"อื่น ๆ", "class":"d-gray"},
    {"icon":"?", "name":"ไม่รู้ว่าปัญหาอะไร", "class":"d-rose"},
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
# CSS
# =========================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700;800;900&display=swap');

*{
    font-family:'Noto Sans Thai',sans-serif;
}

.stApp{
    background:
        radial-gradient(circle at 12% 0%, rgba(37,99,235,.12), transparent 25%),
        radial-gradient(circle at 90% 8%, rgba(14,165,233,.12), transparent 26%),
        linear-gradient(180deg,#F2F7FF 0%,#FFFFFF 48%,#F8FBFF 100%);
}

.block-container{
    padding-top:0!important;
    padding-left:1.2rem!important;
    padding-right:1.2rem!important;
    max-width:1180px;
}

#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}

/* ================= HEADER ================= */
.hero{
    position:relative;
    overflow:hidden;
    margin:0 -1.2rem 0 -1.2rem;
    padding:30px 30px 42px 30px;
    background:
        radial-gradient(circle at 12% 34%, rgba(56,189,248,.24), transparent 20%),
        radial-gradient(circle at 82% 42%, rgba(14,165,233,.38), transparent 22%),
        linear-gradient(135deg,#061331 0%,#082A69 48%,#0057D9 100%);
    color:white;
    box-shadow:0 16px 42px rgba(0,60,180,.25);
}

.hero:before{
    content:"";
    position:absolute;
    inset:0;
    opacity:.25;
    background-image:
        linear-gradient(90deg, transparent 0 72%, rgba(56,189,248,.46) 73%, transparent 74%),
        linear-gradient(0deg, transparent 0 68%, rgba(56,189,248,.20) 69%, transparent 70%);
    background-size:88px 42px;
    transform:skewX(-18deg);
    transform-origin:right;
}

.hero:after{
    content:"";
    position:absolute;
    right:16px;
    top:28px;
    width:420px;
    height:120px;
    background:
        linear-gradient(90deg,transparent,rgba(56,189,248,.70),transparent),
        linear-gradient(180deg,transparent,rgba(37,99,235,.45),transparent);
    filter:blur(2px);
    clip-path:polygon(10% 45%,90% 45%,90% 52%,10% 52%);
}

.hero-inner{
    position:relative;
    z-index:2;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:20px;
}

.logo-wrap{
    display:flex;
    align-items:center;
    gap:22px;
}

.ai-logo{
    width:112px;
    height:112px;
    border-radius:26px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:54px;
    font-weight:950;
    letter-spacing:-4px;
    color:white;
    background:
        radial-gradient(circle at 35% 25%, rgba(255,255,255,.38), transparent 20%),
        linear-gradient(135deg,#073B8E,#071A3E);
    border:3px solid rgba(56,189,248,.9);
    box-shadow:
        0 0 0 8px rgba(56,189,248,.10),
        0 0 30px rgba(56,189,248,.72),
        inset 0 0 24px rgba(56,189,248,.30);
}

.hero h1{
    margin:0;
    font-size:52px;
    line-height:1;
    font-weight:950;
    letter-spacing:-1.4px;
    text-shadow:0 6px 20px rgba(0,0,0,.25);
}

.hero p{
    margin:12px 0 0 0;
    font-size:22px;
    font-weight:800;
    color:#BAE6FD;
}

.hero-time{
    position:absolute;
    right:26px;
    top:14px;
    z-index:3;
    font-size:13px;
    font-weight:900;
    color:#DFF6FF;
}

/* ================= NAV ================= */
.nav-panel{
    position:relative;
    z-index:5;
    margin:-24px auto 18px auto;
    background:white;
    border:1px solid #E5EDF8;
    border-radius:18px;
    padding:10px;
    box-shadow:0 16px 32px rgba(15,23,42,.12);
}

div[data-testid="stButton"] button{
    border-radius:14px;
    font-weight:900;
    min-height:50px;
    transition:.18s ease;
    border:1px solid #E2E8F0;
    background:white;
    color:#0F172A;
}

div[data-testid="stButton"] button:hover{
    transform:translateY(-2px);
    border:2px solid #EF4444;
    box-shadow:0 12px 22px rgba(239,68,68,.16);
}

.nav-dash button,
.nav-ai button,
.nav-history button,
.nav-update button,
.nav-master button{
    min-height:54px!important;
    border-radius:14px!important;
    font-size:14px!important;
    font-weight:950!important;
}

.nav-dash button{background:linear-gradient(135deg,#EAF3FF,#FFFFFF)!important;color:#0B56D9!important;border:1px solid #93C5FD!important;}
.nav-ai button{background:linear-gradient(135deg,#ECFDF5,#FFFFFF)!important;color:#059669!important;border:1px solid #86EFAC!important;}
.nav-history button{background:linear-gradient(135deg,#F5F3FF,#FFFFFF)!important;color:#6D28D9!important;border:1px solid #C4B5FD!important;}
.nav-update button{background:linear-gradient(135deg,#FFF7ED,#FFFFFF)!important;color:#EA580C!important;border:1px solid #FDBA74!important;}
.nav-master button{background:linear-gradient(135deg,#FEF2F2,#FFFFFF)!important;color:#DC2626!important;border:1px solid #FCA5A5!important;}

.active-page{
    border-bottom:0!important;
}

.active-page button{
    border:3px solid #EF4444!important;
    box-shadow:0 8px 18px rgba(239,68,68,.18)!important;
    transform:translateY(-1px);
}

/* ================= PANELS ================= */
.panel{
    background:white;
    border:1px solid #E4ECF7;
    border-radius:18px;
    padding:18px 22px 22px 22px;
    margin-bottom:14px;
    box-shadow:0 8px 24px rgba(15,23,42,.07);
}

.section-title{
    display:flex;
    align-items:center;
    gap:14px;
    color:#071E52;
    font-size:25px;
    font-weight:950;
    margin:0 0 12px 0;
}

.num{
    width:44px;
    height:44px;
    border-radius:12px;
    display:flex;
    align-items:center;
    justify-content:center;
    color:white;
    font-weight:950;
    font-size:23px;
    background:linear-gradient(135deg,#22C55E,#06B6D4);
    box-shadow:0 8px 16px rgba(6,182,212,.20);
}

.thin-line{
    height:1px;
    background:linear-gradient(90deg,#16C784,rgba(14,165,233,.35),transparent);
    margin:0 0 18px 0;
}

/* ================= INPUT ================= */
.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"]{
    border-radius:12px!important;
    border:1px solid #D8E4F2!important;
    background:#FFFFFF!important;
    font-weight:800!important;
}

.info-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:14px;
    margin-top:14px;
}

.info-card{
    border-radius:14px;
    padding:14px;
    min-height:76px;
    border:1px solid #E2E8F0;
    font-weight:900;
}

.info-card small{
    display:block;
    color:#64748B;
    font-size:12px;
    margin-bottom:5px;
}

.info-blue{background:linear-gradient(135deg,#EAF3FF,#FFFFFF);color:#0B56D9;border-color:#BFDBFE;}
.info-cyan{background:linear-gradient(135deg,#ECFEFF,#FFFFFF);color:#0891B2;border-color:#A5F3FC;}
.info-purple{background:linear-gradient(135deg,#F5F3FF,#FFFFFF);color:#7C3AED;border-color:#DDD6FE;}
.info-pink{background:linear-gradient(135deg,#FFF1F2,#FFFFFF);color:#DB2777;border-color:#FBCFE8;}

/* ================= DEFECT BUTTONS ================= */
.defect-card button{
    min-height:124px!important;
    width:100%!important;
    border-radius:16px!important;
    padding:10px 6px!important;
    font-size:17px!important;
    line-height:1.2!important;
    font-weight:950!important;
    color:#0F172A!important;
    border:1px solid #DDE8F6!important;
    box-shadow:0 6px 16px rgba(15,23,42,.05)!important;
    white-space:pre-line!important;
}

.defect-card button:hover{
    border:2px solid #EF4444!important;
    transform:translateY(-2px)!important;
    box-shadow:0 12px 24px rgba(239,68,68,.18)!important;
}

.defect-selected-wrap{
    position:relative;
}

.defect-selected-wrap button{
    border:3px solid #EF4444!important;
    box-shadow:0 12px 26px rgba(239,68,68,.20)!important;
    transform:translateY(-2px)!important;
}

.defect-selected-wrap:after{
    content:"✓";
    position:absolute;
    top:0;
    right:0;
    width:34px;
    height:34px;
    border-radius:0 14px 0 12px;
    background:#EF4444;
    color:white;
    display:flex;
    align-items:center;
    justify-content:center;
    font-weight:950;
    font-size:22px;
    z-index:10;
    pointer-events:none;
}

.d-blue button{background:linear-gradient(135deg,#EFF6FF,#FFFFFF)!important;border-color:#93C5FD!important;}
.d-orange button{background:linear-gradient(135deg,#FFF7ED,#FFFFFF)!important;border-color:#FDBA74!important;}
.d-teal button{background:linear-gradient(135deg,#ECFEFF,#FFFFFF)!important;border-color:#67E8F9!important;}
.d-purple button{background:linear-gradient(135deg,#F5F3FF,#FFFFFF)!important;border-color:#C4B5FD!important;}
.d-pink button{background:linear-gradient(135deg,#FFF1F2,#FFFFFF)!important;border-color:#F9A8D4!important;}
.d-sky button{background:linear-gradient(135deg,#EFF6FF,#FFFFFF)!important;border-color:#93C5FD!important;}
.d-green button{background:linear-gradient(135deg,#F0FDF4,#FFFFFF)!important;border-color:#86EFAC!important;}
.d-amber button{background:linear-gradient(135deg,#FFFBEB,#FFFFFF)!important;border-color:#FCD34D!important;}
.d-gray button{background:linear-gradient(135deg,#F8FAFC,#FFFFFF)!important;border-color:#CBD5E1!important;}
.d-rose button{background:linear-gradient(135deg,#FDF2F8,#FFFFFF)!important;border-color:#F9A8D4!important;}

.selected-result{
    margin-top:14px;
    background:linear-gradient(135deg,#FFF1F2,#FFE4E6);
    border:2px solid #EF4444;
    color:#B91C1C;
    border-radius:14px;
    padding:12px 14px;
    font-size:17px;
    font-weight:950;
    text-align:center;
}

/* ================= UPLOAD ================= */
.upload-grid{
    display:grid;
    grid-template-columns:1.2fr 1fr;
    gap:18px;
}

.fake-upload{
    min-height:185px;
    border:2px dashed #9DBBFF;
    border-radius:16px;
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
    width:74px;
    height:74px;
    border-radius:50%;
    background:linear-gradient(135deg,#DBEAFE,#EEF2FF);
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:36px;
    margin-bottom:12px;
}

.preview-box{
    min-height:185px;
    border:1px solid #E2E8F0;
    border-radius:16px;
    background:#F8FAFC;
    display:flex;
    align-items:center;
    justify-content:center;
    color:#94A3B8;
    font-weight:800;
    text-align:center;
}

/* ================= RESULT ================= */
.result-grid{
    display:grid;
    grid-template-columns:.75fr 1.4fr 1fr;
    gap:18px;
    align-items:stretch;
}

.gauge{
    width:142px;
    height:142px;
    border-radius:50%;
    background:conic-gradient(#22C55E 0 91%, #DCFCE7 91% 100%);
    display:flex;
    align-items:center;
    justify-content:center;
    margin:auto;
}

.gauge-inner{
    width:106px;
    height:106px;
    border-radius:50%;
    background:white;
    display:flex;
    align-items:center;
    justify-content:center;
    flex-direction:column;
    color:#15803D;
    font-weight:950;
}

.gauge-num{font-size:32px;line-height:1;}
.gauge-label{font-size:12px;color:#166534;}

.result-status{
    display:flex;
    align-items:center;
    gap:14px;
    height:100%;
}

.check{
    min-width:54px;
    width:54px;
    height:54px;
    border-radius:50%;
    background:#DCFCE7;
    color:#16A34A;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:32px;
    font-weight:950;
}

.result-status h3{
    color:#16A34A;
    font-size:28px;
    margin:0;
    font-weight:950;
}

.result-status p{
    margin:8px 0 0 0;
    color:#64748B;
    font-weight:800;
}

.ai-image-box{
    border-radius:14px;
    background:#F3F6FB;
    border:1px solid #E2E8F0;
    display:flex;
    align-items:center;
    justify-content:center;
    min-height:130px;
    color:#94A3B8;
    font-weight:800;
    text-align:center;
}

.action-grid{
    display:grid;
    grid-template-columns:1fr 1.2fr;
    gap:18px;
    margin-top:16px;
}

.save-btn button{
    background:linear-gradient(90deg,#16C784,#22C55E)!important;
    color:white!important;
    border:none!important;
    font-size:19px!important;
}

.send-btn button{
    background:linear-gradient(90deg,#2563EB,#006CFF)!important;
    color:white!important;
    border:none!important;
    font-size:19px!important;
}

.analyze-btn button{
    background:linear-gradient(90deg,#16C784,#0094FF)!important;
    color:white!important;
    border:none!important;
    font-size:20px!important;
    min-height:58px!important;
}

/* ================= DASHBOARD ================= */
.kpi-grid{
    display:grid;
    grid-template-columns:repeat(4,1fr);
    gap:16px;
}

.kpi{
    border-radius:18px;
    padding:18px;
    border:1px solid #E2E8F0;
    font-weight:950;
    box-shadow:0 8px 20px rgba(15,23,42,.06);
}

.kpi small{
    display:block;
    color:#64748B;
    margin-bottom:8px;
}

.kpi strong{
    font-size:38px;
    color:#071E52;
}

.kpi1{background:linear-gradient(135deg,#EAF3FF,#FFFFFF);border-color:#93C5FD;}
.kpi2{background:linear-gradient(135deg,#ECFDF5,#FFFFFF);border-color:#86EFAC;}
.kpi3{background:linear-gradient(135deg,#FEF2F2,#FFFFFF);border-color:#FCA5A5;}
.kpi4{background:linear-gradient(135deg,#F5F3FF,#FFFFFF);border-color:#C4B5FD;}

/* ================= RESPONSIVE ================= */
@media (max-width:900px){
    .block-container{
        padding-left:.55rem!important;
        padding-right:.55rem!important;
    }

    .hero{
        margin:0 -.55rem 0 -.55rem;
        padding:22px 14px 36px 14px;
    }

    .ai-logo{
        width:72px;
        height:72px;
        border-radius:18px;
        font-size:36px;
        letter-spacing:-3px;
    }

    .logo-wrap{
        gap:12px;
    }

    .hero h1{
        font-size:28px;
    }

    .hero p{
        font-size:14px;
        margin-top:7px;
    }

    .hero-time{
        font-size:11px;
        right:12px;
        top:8px;
    }

    .nav-panel{
        margin:-20px auto 14px auto;
        padding:7px;
        border-radius:14px;
    }

    .nav-dash button,
    .nav-ai button,
    .nav-history button,
    .nav-update button,
    .nav-master button{
        min-height:42px!important;
        font-size:10px!important;
        padding:3px!important;
        border-radius:10px!important;
    }

    .panel{
        padding:14px 12px 16px 12px;
        border-radius:16px;
    }

    .section-title{
        font-size:18px;
        gap:9px;
        margin-bottom:10px;
    }

    .num{
        width:34px;
        height:34px;
        font-size:18px;
        border-radius:10px;
    }

    .info-grid{
        grid-template-columns:repeat(2,1fr);
        gap:10px;
    }

    .info-card{
        min-height:66px;
        padding:10px;
        font-size:13px;
    }

    .defect-card button{
        min-height:84px!important;
        font-size:11px!important;
        border-radius:11px!important;
        padding:6px 2px!important;
    }

    .defect-selected-wrap:after{
        width:24px;
        height:24px;
        font-size:16px;
        border-radius:0 9px 0 8px;
    }

    .selected-result{
        font-size:14px;
        padding:9px;
    }

    .fake-upload,
    .preview-box{
        min-height:150px;
    }

    .result-grid{
        grid-template-columns:1fr;
    }

    .result-status h3{
        font-size:22px;
    }

    .kpi-grid{
        grid-template-columns:repeat(2,1fr);
        gap:10px;
    }

    .kpi strong{
        font-size:30px;
    }

    .action-grid{
        grid-template-columns:1fr;
    }
}
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
    ("📊 Dashboard", "nav-dash", "Dashboard"),
    ("🔍 AI ตรวจงาน", "nav-ai", "AI ตรวจงาน"),
    ("🕘 ประวัติ", "nav-history", "ประวัติ"),
    ("🟠 อัปเดต", "nav-update", "อัปเดตข้อมูล"),
    ("⚙️ มาสเตอร์", "nav-master", "มาสเตอร์"),
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
        <div class="kpi-grid">
            <div class="kpi kpi1"><small>งานตรวจวันนี้</small><strong>0</strong></div>
            <div class="kpi kpi2"><small>ผ่าน</small><strong>0</strong></div>
            <div class="kpi kpi3"><small>พบปัญหา</small><strong>0</strong></div>
            <div class="kpi kpi4"><small>รอหัวหน้า</small><strong>0</strong></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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

    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.so = st.text_input("SO", value=st.session_state.so, placeholder="ค้นหา SO")
    with c2:
        st.session_state.pc = st.text_input("PC", value=st.session_state.pc, placeholder="ค้นหา PC")
    with c3:
        st.session_state.reporter = st.text_input("คนแจ้ง", value=st.session_state.reporter, placeholder="ชื่อคนแจ้ง")

    pc_data = MASTER_PC.get(st.session_state.pc.strip())

    customer = pc_data["customer"] if pc_data else "-"
    register = pc_data["register"] if pc_data else "-"
    print_mark = pc_data["print_mark"] if pc_data else "-"
    barcode = pc_data["barcode"] if pc_data else "-"

    st.markdown(f"""
        <div class="info-grid">
            <div class="info-card info-blue"><small>ลูกค้า</small>{customer}</div>
            <div class="info-card info-cyan"><small>Register</small>{register}</div>
            <div class="info-card info-purple"><small>Print Mark</small>{print_mark}</div>
            <div class="info-card info-pink"><small>Barcode</small>{barcode}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2 DEFECT
    st.markdown("""
    <div class="panel">
        <div class="section-title"><div class="num">2</div>เลือกสิ่งที่ต้องการตรวจ</div>
        <div class="thin-line"></div>
    """, unsafe_allow_html=True)

    for row_start in range(0, len(DEFECTS), 5):
        cols = st.columns(5, gap="small")
        for col, idx in zip(cols, range(row_start, row_start + 5)):
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

    up1, up2 = st.columns([1.2, 1])
    with up1:
        st.markdown("""
        <div class="fake-upload">
            <div class="cam">📷</div>
            แตะเพื่อถ่ายรูป<br>
            <span style="font-size:14px;color:#64748B;">หรือเลือกจากแกลเลอรี · JPG, PNG</span>
        </div>
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader("ถ่ายรูป / อัปโหลด", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    with up2:
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
        st.markdown(f"""
        <div class="result-grid">
            <div class="gauge">
                <div class="gauge-inner">
                    <div class="gauge-num">91%</div>
                    <div class="gauge-label">ความมั่นใจ</div>
                </div>
            </div>
            <div class="result-status">
                <div class="check">✓</div>
                <div>
                    <h3>ไม่พบความผิดปกติ</h3>
                    <p>คุณภาพงาน : ผ่านมาตรฐาน</p>
                    <p>SO : {st.session_state.so or "-"} / PC : {st.session_state.pc or "-"} / คนแจ้ง : {st.session_state.reporter or "-"}</p>
                    <p>ประเภทที่ตรวจ : {st.session_state.defect} / เวลา : {now}</p>
                </div>
            </div>
            <div class="ai-image-box">ภาพผลการวิเคราะห์</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="action-grid">', unsafe_allow_html=True)
        b1, b2 = st.columns([1, 1.2])
        with b1:
            st.markdown('<div class="save-btn">', unsafe_allow_html=True)
            st.button("💾 บันทึกผลการตรวจ", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with b2:
            st.markdown('<div class="send-btn">', unsafe_allow_html=True)
            st.button("👤 ส่งงานต่อ / เรียกหัวหน้าตรวจ", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
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

    c1, c2, c3 = st.columns(3)
    with c1:
        st.date_input("วันที่")
    with c2:
        st.text_input("ค้นหา SO / PC")
    with c3:
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

    c1, c2 = st.columns(2)
    with c1:
        st.text_input("SO")
        st.text_input("PC")
        st.text_input("ลูกค้า")
    with c2:
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
