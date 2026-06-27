import streamlit as st
from PIL import Image
from datetime import datetime

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
.stApp{
    background:linear-gradient(180deg,#F4F8FF,#FFFFFF);
}

.block-container{
    padding-top:0;
    max-width:560px;
}

.header{
    position:relative;
    overflow:hidden;
    background:
        radial-gradient(circle at 85% 25%, rgba(0,255,255,.35), transparent 22%),
        radial-gradient(circle at 95% 85%, rgba(168,85,247,.45), transparent 28%),
        linear-gradient(135deg,#061A4A,#005CFF);
    color:white;
    border-radius:0 0 28px 28px;
    padding:24px 22px 26px 22px;
    margin-bottom:22px;
    box-shadow:0 14px 32px rgba(0,80,255,.28);
}

.header-row{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
}

.header-left{
    display:flex;
    align-items:center;
    gap:12px;
}

.ai-big{
    width:62px;
    height:62px;
    border-radius:18px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:38px;
    background:rgba(255,255,255,.16);
    border:1px solid rgba(255,255,255,.25);
    box-shadow:inset 0 0 18px rgba(255,255,255,.12);
}

.camera-big{
    font-size:64px;
    filter:drop-shadow(0 10px 16px rgba(0,0,0,.25));
}

.header h1{
    font-size:28px;
    line-height:1.1;
    margin:0;
    font-weight:900;
}

.header p{
    margin:6px 0 0 0;
    font-size:15px;
    opacity:.92;
    font-weight:700;
}

.top-info{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
    margin-bottom:14px;
}

.info-box{
    background:white;
    border-radius:16px;
    border:1px solid #DCE8FA;
    padding:12px;
    box-shadow:0 6px 16px rgba(15,23,42,.06);
}

.info-label{
    font-size:12px;
    color:#64748B;
    font-weight:800;
}

.info-value{
    margin-top:4px;
    font-size:16px;
    color:#08245C;
    font-weight:900;
}

.divider{
    position:relative;
    height:1px;
    background:linear-gradient(90deg,transparent,#6CC7FF,#A855F7,transparent);
    margin:24px 0;
}

.divider:after{
    content:"✦";
    position:absolute;
    left:50%;
    top:-14px;
    transform:translateX(-50%);
    background:#F7FAFF;
    color:#3B82F6;
    padding:0 12px;
    font-size:20px;
}

.step-title{
    display:flex;
    align-items:center;
    gap:12px;
    font-size:21px;
    font-weight:900;
    color:#08245C;
    margin-bottom:14px;
}

.step-no{
    background:linear-gradient(135deg,#1685FF,#0057D9);
    color:white;
    border-radius:12px;
    padding:6px 12px;
    box-shadow:0 8px 18px rgba(0,100,255,.25);
}

.card{
    background:white;
    border-radius:20px;
    border:1px solid #E3ECFA;
    padding:16px;
    margin-bottom:16px;
    box-shadow:0 8px 22px rgba(20,60,120,.08);
}

.selected{
    background:linear-gradient(135deg,#FFF1F2,#FFE4E6);
    border:3px solid #EF4444;
    border-radius:16px;
    padding:13px;
    margin-top:12px;
    font-weight:900;
    color:#B91C1C;
    text-align:center;
    box-shadow:0 8px 18px rgba(239,68,68,.18);
}

div[data-testid="stButton"] button{
    min-height:64px;
    border-radius:16px;
    font-weight:900;
    font-size:15px;
    border:1px solid #D8E7FF;
    box-shadow:0 5px 14px rgba(15,23,42,.06);
    transition:.2s;
}

div[data-testid="stButton"] button:hover{
    transform:translateY(-2px);
    border:2px solid #EF4444;
    box-shadow:0 10px 20px rgba(239,68,68,.18);
}

.ai-btn button{
    height:62px!important;
    border:none!important;
    color:white!important;
    font-size:21px!important;
    background:linear-gradient(90deg,#16C784,#0094FF)!important;
    box-shadow:0 12px 26px rgba(0,150,255,.32)!important;
}

.upload-box{
    border:2px dashed #B9A7FF;
    border-radius:20px;
    background:linear-gradient(135deg,#FAF7FF,#F1F7FF);
    padding:18px;
    text-align:center;
    color:#5B21B6;
    font-weight:900;
}

.result-bad{
    background:#FEF2F2;
    border:1px solid #FCA5A5;
    color:#991B1B;
    padding:16px;
    border-radius:16px;
    text-align:center;
    font-weight:900;
    font-size:18px;
}

.note{
    background:#FFF7ED;
    border:1px solid #FDBA74;
    color:#9A3412;
    padding:14px;
    border-radius:14px;
    font-weight:800;
}

.small-muted{
    font-size:12px;
    color:#64748B;
    font-weight:700;
}

img{
    border-radius:16px;
}

footer{visibility:hidden;}
#MainMenu{visibility:hidden;}
header{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

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

# โครงสร้างฐานข้อมูลตัวอย่าง
# ต่อไปเอาตรงนี้ไปต่อกับ Excel / CSV / Database ได้
MASTER_PC = {
    "PC-1304": {
        "customer": "ลูกค้าตัวอย่าง A",
        "spec": "ตรวจสีเหลื่อม / Print Mark เข้มงวด",
        "standard": "ก่อน Register และแรกกดต้องตรวจซ้ำ"
    },
    "PC-2201": {
        "customer": "ลูกค้าตัวอย่าง B",
        "spec": "เน้น Barcode / พิมพ์จาง",
        "standard": "ห้าม Barcode ขาด"
    }
}

tab_ai, tab_dash, tab_db, tab_history = st.tabs([
    "🤖 ตรวจ AI",
    "📊 Dashboard",
    "🗂️ อัปเดตฐานข้อมูล",
    "🕘 ข้อมูลย้อนหลัง"
])

with tab_ai:

    st.markdown("""
    <div class="header">
        <div class="header-row">
            <div class="header-left">
                <div class="ai-big">🤖</div>
                <div>
                    <h1>AI ผู้ช่วยคนคัด</h1>
                    <p>ถ่ายรูป · ส่งตรวจ · ดูผลเลย</p>
                </div>
            </div>
            <div class="camera-big">📸</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ข้อมูลงาน")

    c1, c2 = st.columns(2)
    with c1:
        st.session_state.so = st.text_input("SO", value=st.session_state.so, placeholder="เช่น SO123456")
    with c2:
        st.session_state.pc = st.text_input("PC", value=st.session_state.pc, placeholder="เช่น PC-1304")

    st.session_state.reporter = st.text_input(
        "คนแจ้ง",
        value=st.session_state.reporter,
        placeholder="ชื่อคนแจ้ง / คนคัด"
    )

    pc_data = MASTER_PC.get(st.session_state.pc.strip())

    if pc_data:
        st.markdown(f"""
        <div class="top-info">
            <div class="info-box">
                <div class="info-label">ลูกค้า</div>
                <div class="info-value">{pc_data["customer"]}</div>
            </div>
            <div class="info-box">
                <div class="info-label">ข้อกำหนด PC</div>
                <div class="info-value">{pc_data["spec"]}</div>
            </div>
        </div>
        <div class="note">
            มาตรฐาน : {pc_data["standard"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("กรอก PC แล้วระบบจะดึงข้อกำหนดขึ้นอัตโนมัติ")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="step-title">
        <span class="step-no">1.</span>
        <span>เลือกสิ่งที่ต้องการตรวจ</span>
    </div>
    """, unsafe_allow_html=True)

    items = [
        ("💦", "สีเหลื่อม"),
        ("🟠", "หมึกเลอะ"),
        ("🔵", "พิมพ์ตัน"),
        ("▤", "พิมพ์จาง"),
        ("🟣", "Pin Hole"),
        ("╱╱", "รอยขีด"),
        ("▥", "Barcode"),
        ("⊕", "Print Mark"),
        ("•••", "อื่น ๆ"),
        ("❔", "ไม่รู้ว่าปัญหาอะไร"),
    ]

    for i in range(0, len(items), 2):
        c1, c2 = st.columns(2, gap="small")
        for col, item in zip([c1, c2], items[i:i+2]):
            icon, name = item
            with col:
                if st.button(f"{icon}  {name}", use_container_width=True, key=f"defect_{name}"):
                    st.session_state.defect = name
                    st.session_state.result = False

    st.markdown(
        f'<div class="selected">เลือกอยู่ : {st.session_state.defect}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="step-title">
        <span class="step-no" style="background:linear-gradient(135deg,#8B5CF6,#6D28D9);">2.</span>
        <span>ถ่ายรูปงาน</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "ถ่ายรูป / อัปโหลดรูป",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    img = None
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)
    else:
        st.markdown("""
        <div class="upload-box">
            📷<br>
            ถ่ายรูป / อัปโหลดรูป<br>
            <span class="small-muted">รองรับ JPG, PNG</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="step-title">
        <span class="step-no" style="background:linear-gradient(135deg,#22C55E,#06B6D4);">3.</span>
        <span>ส่งตรวจด้วย AI</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ai-btn">', unsafe_allow_html=True)
    analyze = st.button("🚀 ส่งตรวจด้วย AI", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if analyze:
        if uploaded:
            st.session_state.result = True
        else:
            st.warning("ถ่ายรูปก่อนหัวหน้า")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="step-title">
        <span class="step-no" style="background:linear-gradient(135deg,#F97316,#DC2626);">4.</span>
        <span>ผลการวิเคราะห์</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)

    if st.session_state.result and uploaded:
        now = datetime.now().strftime("%d/%m/%Y %H:%M")

        st.markdown("""
        <div class="result-bad">
            🔴 พบความผิดปกติ<br>
            ความมั่นใจ 88%
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### ตำแหน่งที่พบ")
        st.image(img, use_container_width=True)

        st.markdown(f"""
        <div class="note">
            รายละเอียด<br>
            • เวลา : {now}<br>
            • SO : {st.session_state.so or "-"}<br>
            • PC : {st.session_state.pc or "-"}<br>
            • คนแจ้ง : {st.session_state.reporter or "-"}<br>
            • ประเภทที่ตรวจ : {st.session_state.defect}<br>
            • สถานะ : พบจุดต้องสงสัย<br>
            • แนะนำ : เรียกหัวหน้าตรวจซ้ำ
        </div>
        """, unsafe_allow_html=True)

        st.button("👨‍💼 เรียกหัวหน้าตรวจ", use_container_width=True)

    else:
        st.info("รอส่งรูปเพื่อวิเคราะห์")

    st.markdown('</div>', unsafe_allow_html=True)

with tab_dash:
    st.markdown("## 📊 Dashboard")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.metric("งานตรวจวันนี้", "0")
    st.metric("พบปัญหา", "0")
    st.metric("รอหัวหน้าตรวจ", "0")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_db:
    st.markdown("## 🗂️ อัปเดตฐานข้อมูล")
    st.info("หน้านี้ไว้เพิ่ม Master SO / PC / ลูกค้า / ข้อกำหนดงาน")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.text_input("เพิ่ม PC")
    st.text_input("ชื่อลูกค้า")
    st.text_area("ข้อกำหนดของ PC")
    st.button("💾 บันทึกฐานข้อมูล", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_history:
    st.markdown("## 🕘 ข้อมูลย้อนหลัง")
    st.info("หน้านี้ไว้ค้นประวัติการตรวจย้อนหลัง")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.date_input("เลือกวันที่")
    st.text_input("ค้นหา SO / PC / คนแจ้ง")
    st.button("🔎 ค้นหา", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
