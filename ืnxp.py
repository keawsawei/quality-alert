import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="🤖",
    layout="centered"
)

st.markdown("""
<style>
.block-container{
    padding-top:0;
    max-width:520px;
}

.header{
    background:linear-gradient(135deg,#061B3A,#0057D9);
    color:white;
    padding:18px;
    border-radius:0 0 18px 18px;
    margin-bottom:14px;
}

.header h1{
    font-size:24px;
    margin:0;
    font-weight:900;
}

.header p{
    margin:4px 0 0 0;
    font-size:13px;
    opacity:.9;
}

.card{
    background:white;
    border:1px solid #E5E7EB;
    border-radius:16px;
    padding:14px;
    margin-bottom:14px;
    box-shadow:0 4px 14px rgba(15,23,42,.08);
}

.step{
    font-size:16px;
    font-weight:900;
    margin-bottom:10px;
    color:#0F172A;
}

div[data-testid="stButton"] button{
    height:58px;
    border-radius:12px;
    font-weight:800;
    border:1px solid #D7E3F5;
    background:#F8FAFC;
}

div[data-testid="stButton"] button:hover{
    border:2px solid #0066FF;
    background:#EEF6FF;
    color:#0057D9;
}

.selected{
    background:#EAF3FF;
    border:2px solid #0066FF;
    border-radius:12px;
    padding:12px;
    font-weight:900;
    color:#0057D9;
    margin-bottom:10px;
}

.result-bad{
    background:#FEF2F2;
    border:1px solid #FCA5A5;
    color:#991B1B;
    padding:14px;
    border-radius:14px;
    text-align:center;
    font-weight:900;
}

.result-ok{
    background:#ECFDF5;
    border:1px solid #86EFAC;
    color:#166534;
    padding:14px;
    border-radius:14px;
    text-align:center;
    font-weight:900;
}

.note{
    background:#FFF7ED;
    border:1px solid #FDBA74;
    color:#9A3412;
    padding:12px;
    border-radius:12px;
    font-weight:700;
}

img{
    border-radius:14px;
}

footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

if "defect" not in st.session_state:
    st.session_state.defect = "สีเหลื่อม"

if "result" not in st.session_state:
    st.session_state.result = False

st.markdown("""
<div class="header">
    <h1>🤖 AI ผู้ช่วยคนคัด</h1>
    <p>ถ่ายรูป / เลือกจุดตรวจ / ดูผลทันที</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="step">1. เลือกสิ่งที่ต้องการตรวจ</div>', unsafe_allow_html=True)

items = [
    ("🧩", "สีเหลื่อม"),
    ("🕷️", "หมึกเลอะ"),
    ("⚫", "พิมพ์ตัน"),
    ("▤", "พิมพ์จาง"),
    ("●", "Pin Hole"),
    ("╱╱", "รอยขีด"),
    ("▥", "Barcode"),
    ("⊕", "Print Mark"),
    ("•••", "อื่น ๆ"),
    ("?", "ไม่รู้ว่าปัญหาอะไร"),
]

for i in range(0, len(items), 2):
    c1, c2 = st.columns(2)
    for col, item in zip([c1, c2], items[i:i+2]):
        icon, name = item
        with col:
            if st.button(f"{icon}  {name}", use_container_width=True, key=name):
                st.session_state.defect = name
                st.session_state.result = False

st.markdown(
    f'<div class="selected">เลือกอยู่ : {st.session_state.defect}</div>',
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="step">2. ถ่ายรูปงาน</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "ถ่ายรูป / เลือกรูปจากกล้อง",
    type=["jpg", "jpeg", "png"],
    label_visibility="collapsed"
)

img = None
if uploaded:
    img = Image.open(uploaded)
    st.image(img, use_container_width=True)

if st.button("🚀 ส่งตรวจด้วย AI", use_container_width=True):
    if uploaded:
        st.session_state.result = True
    else:
        st.warning("ถ่ายรูปก่อนหัวหน้า")

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="step">3. ผลการวิเคราะห์ (AI)</div>', unsafe_allow_html=True)

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
