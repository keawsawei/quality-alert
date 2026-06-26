import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="AI ผู้ช่วยคนคัด",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI ผู้ช่วยคนคัด")
st.caption("ถ่ายรูป ➜ ส่ง AI ➜ ดูผล")

st.divider()

left, right = st.columns([1,1])

with left:

    st.subheader("1. เลือกสิ่งที่ต้องการตรวจ")

    defect = st.radio(
        "",
        [
            "🤷 ไม่รู้ว่าปัญหาอะไร",
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

    st.subheader("2. ถ่ายรูป")

    uploaded = st.file_uploader(
        "เลือกรูป",
        type=["jpg","jpeg","png"]
    )

    if uploaded:

        image = Image.open(uploaded)

        st.image(
            image,
            use_container_width=True
        )

        if st.button(
            "🚀 ส่ง AI วิเคราะห์",
            use_container_width=True
        ):
            st.session_state.run = True

with right:

    st.subheader("3. ผลการวิเคราะห์")

    if st.session_state.get("run"):

        st.success("✅ วิเคราะห์เสร็จแล้ว")

        st.markdown(f"""
### สิ่งที่ตรวจ

**{defect}**
""")

        st.info("""
AI กำลังวิเคราะห์จากภาพ...

เวอร์ชันแรกยังไม่ได้เชื่อม AI

ต่อไปจะเชื่อม OpenAI Vision
และฐานข้อมูล Defect ของบริษัท
""")

        st.warning("""
ผลลัพธ์ตัวอย่าง

• พบความผิดปกติ

• ความมั่นใจ 86%

• กรุณาให้หัวหน้าตรวจสอบอีกครั้ง
""")

    else:

        st.info("รอส่งรูปเพื่อวิเคราะห์")
