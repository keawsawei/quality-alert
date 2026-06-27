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
    max-width:760px;
}

.app-header{
    background:linear-gradient(135deg,#071B3A,#004AAD);
    color:white;
    padding:18px 24px;
    border-radius:0 0 18px 18px;
    margin-bottom:18px;
}

.app-header h1{
    font-size:26px;
    margin:0;
    font-weight:800;
}

.app-header p{
    margin:4px 0 0 0;
    opacity:.85;
}

.card{
    background:white;
    border-radius:16px;
    padding:18px;
    border:1px solid #E5E7EB;
    box-shadow:0 4px 16px rgba(15,23,42,.08);
    margin-bottom:16px;
}

.step-title{
    font-size:18px;
    font-weight:800;
    color:#0F172A;
    margin-bottom:14px;
}

.defect-grid{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
}

.defect-box{
    border:1px solid #D8E0EA;
    border-radius:10px;
    padding:12px;
    font-weight:700;
    background:#F8FAFC;
}

.result-ok{
    background:#ECFDF5;
    border:1px solid #BBF7D0;
    color:#166534;
    padding:16px;
    border-radius:14px;
    font-weight:800;
    text-align:center;
}

.result-bad{
    background:#FEF2F2;
    border:1px solid #FECACA;
    color:#991B1B;
    padding:16px;
    border-radius:14px;
    font-weight:800;
    text-align:center;
}

.note{
    background:#FFF7ED;
    border:1px solid #FED7AA;
    color:#9A3412;
    padding:14px;
    border-radius:12px;
    font-weight:700;
}

.stButton button{
    height:48px;
    border-radius:10px;
    font-weight:800;
}

img{
    border-radius:14px;
}

footer{visibility:hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
    <h1>🤖 AI ผู้ช่วยคนคัด</h1>
    <p>ถ่ายรูป / เลือกปัญหา / ส่งตรวจด้วย AI</p>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1], gap="medium")

defects = [
    "สีเหลื่อม", "หมึกเลอะ",
    "พิมพ์ตัน", "พิมพ์จาง",
    "Pin Hole", "รอยขีด",
    "Barcode", "Print Mark",
    "อื่น ๆ", "ไม่รู้ว่าปัญหาอะไร"
]

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">1. เลือกสิ่งที่ต้องการตรวจ</div>', unsafe_allow_html=True)

    defect = st.radio(
        "",
        defects,
        horizontal=False,
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">2. ถ่ายรูปงาน</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "อัปโหลดรูป JPG / PNG",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed"
    )

    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)

    analyze = st.button("🚀 ส่งตรวจด้วย AI", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">3. ผลการวิเคราะห์ (AI)</div>', unsafe_allow_html=True)

    if analyze and uploaded:
        st.markdown("""
        <div class="result-bad">
            🔴 พบความผิดปกติ<br>
            ความมั่นใจ 88%
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ตำแหน่งที่พบ")
        st.image(img, use_container_width=True)

        st.markdown("""
        <div class="card" style="box-shadow:none;">
            <b>รายละเอียด</b><br>
            • ประเภทที่ตรวจ : """ + defect + """<br>
            • สถานะ : พบจุดต้องสงสัย<br>
            • คำแนะนำ : ให้หัวหน้าตรวจสอบซ้ำ
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="note">
            💡 ตรวจสอบจากรูปก่อน Register และแรกกดของลูกค้าก่อนพิมพ์
        </div>
        """, unsafe_allow_html=True)

        st.button("👨‍💼 เรียกหัวหน้าตรวจ", use_container_width=True)

    elif analyze and not uploaded:
        st.warning("กรุณาอัปโหลดรูปก่อนส่งตรวจ")

    else:
        st.info("รอส่งรูปเพื่อวิเคราะห์")

    st.markdown('</div>', unsafe_allow_html=True)
