import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
.stApp{
    background:#F7FAFF;
}

.block-container{
    padding-top:0;
    max-width:560px;
}

.header{
    background:linear-gradient(135deg,#051B4D,#006CFF);
    color:white;
    border-radius:0 0 26px 26px;
    padding:22px;
    margin-bottom:24px;
    box-shadow:0 12px 28px rgba(0,80,255,.28);
}

.header h1{
    font-size:30px;
    margin:0;
    font-weight:900;
}

.header p{
    margin:6px 0 0 0;
    font-size:16px;
    opacity:.9;
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
    font-size:22px;
    font-weight:900;
    color:#08245C;
    margin-bottom:16px;
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
    padding:18px;
    margin-bottom:18px;
    box-shadow:0 8px 22px rgba(20,60,120,.08);
}

.selected{
    background:linear-gradient(135deg,#EAF3FF,#F3E8FF);
    border:2px solid #3B82F6;
    border-radius:16px;
    padding:14px;
    margin-top:12px;
    font-weight:900;
    color:#0647A8;
    text-align:center;
}

div[data-testid="stButton"] button{
    min-height:66px;
    border-radius:16px;
    font-weight:900;
    font-size:16px;
    border:1px solid #D8E7FF;
    box-shadow:0 5px 14px rgba(15,23,42,.06);
    transition:.2s;
}

div[data-testid="stButton"] button:hover{
    transform:translateY(-2px);
    border:2px solid #2563EB;
    box-shadow:0 10px 20px rgba(37,99,235,.18);
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

.result-ok{
    background:#ECFDF5;
    border:1px solid #86EFAC;
    color:#166534;
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

st.markdown("""
<div class="header">
    <h1>🤖 AI ผู้ช่วยคนคัด</h1>
    <p>ถ่ายรูป · ส่งตรวจ · ดูผลเลย</p>
</div>
""", unsafe_allow_html=True)

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
        📷 <b>ถ่ายรูป / อัปโหลดรูป</b><br>
        รองรับ JPG, PNG
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
        • ประเภทที่ตรวจ : {st.session_state.defect}<br>
        • สถานะ : พบจุดต้องสงสัย<br>
        • แนะนำ : เรียกหัวหน้าตรวจซ้ำ
    </div>
    """, unsafe_allow_html=True)

    st.button("👨‍💼 เรียกหัวหน้าตรวจ", use_container_width=True)

else:
    st.info("รอส่งรูปเพื่อวิเคราะห์")

st.markdown('</div>', unsafe_allow_html=True)
