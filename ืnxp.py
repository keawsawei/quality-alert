import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>

.block-container{
    padding-top:2rem;
    padding-bottom:2rem;
}

.card{
    background:white;
    border-radius:15px;
    padding:20px;
    border:1px solid #E5E7EB;
    box-shadow:0 2px 10px rgba(0,0,0,.08);
}

.result{
    background:#F8FAFC;
    border-radius:15px;
    padding:20px;
    border:1px solid #CBD5E1;
}

h1{
    color:#0F172A;
}

</style>
""",unsafe_allow_html=True)

st.title("🤖 AI ผู้ช่วยคนคัด")
st.caption("ถ่ายรูป ➜ วิเคราะห์ ➜ แสดงผลทันที")

left,right = st.columns([1,1])

with left:

    st.markdown("### 1️⃣ เลือกสิ่งที่ต้องการตรวจ")

    defect = st.selectbox(
        "",
        [
            "ไม่รู้ว่าปัญหาอะไร",
            "เลอะ / คราบ",
            "สีเหลื่อม",
            "เลือน / จาง",
            "การพิมพ์ตัน",
            "Pin Hole",
            "รอยขีด",
            "Barcode",
            "Print Mark",
            "อื่น ๆ"
        ]
    )

    st.markdown("---")

    st.markdown("### 2️⃣ ถ่ายรูป")

    uploaded = st.file_uploader(
        "",
        type=["jpg","jpeg","png"]
    )

    if uploaded:

        img = Image.open(uploaded)

        st.image(img,use_container_width=True)

        analyze = st.button(
            "🚀 ส่ง AI วิเคราะห์",
            use_container_width=True
        )

        if analyze:
            st.session_state.result=True

with right:

    st.markdown("### 🤖 ผลการวิเคราะห์")

    if st.session_state.get("result"):

        st.success("วิเคราะห์เสร็จแล้ว")

        st.metric(
            "สิ่งที่ตรวจ",
            defect
        )

        st.warning("""
ตัวอย่างผล

🔴 พบความผิดปกติ

ความมั่นใจ 88%

กรุณาเรียกหัวหน้าตรวจสอบ
""")

        st.button(
            "👨‍💼 เรียกหัวหน้า",
            use_container_width=True
        )

    else:

        st.info("รอส่งรูปเพื่อวิเคราะห์")
```
