import streamlit as st
from PIL import Image
from datetime import datetime

st.set_page_config(page_title="AI ผู้ช่วยคนคัด", page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

APP_VERSION = "ถ่ายรูป • เลือกอาการ • ส่ง AI ตรวจ"

DEFECTS = [
    {"icon":"💦","name":"สีเหลื่อม","class":"d-blue"},
    {"icon":"🟠","name":"หมึกเลอะ","class":"d-orange"},
    {"icon":"◉","name":"พิมพ์ตัน","class":"d-teal"},
    {"icon":"▤","name":"พิมพ์จาง","class":"d-purple"},
    {"icon":"●","name":"Pin Hole","class":"d-pink"},
    {"icon":"╱╱","name":"รอยขีด","class":"d-sky"},
    {"icon":"▥","name":"Barcode","class":"d-green"},
    {"icon":"⊕","name":"Print Mark","class":"d-amber"},
    {"icon":"•••","name":"อื่น ๆ","class":"d-gray"},
    {"icon":"?","name":"ไม่รู้ว่าปัญหาอะไร","class":"d-rose"},
]

for k, v in {"defect":"สีเหลื่อม", "result":False, "so":"", "pc":"", "reporter":""}.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@400;600;700;800;900&display=swap');
*{font-family:'Noto Sans Thai',sans-serif!important;box-sizing:border-box!important;}
html,body,.stApp{width:100%;overflow-x:hidden!important;}
.stApp{background:radial-gradient(circle at top left,rgba(37,99,235,.18),transparent 34%),radial-gradient(circle at top right,rgba(14,165,233,.15),transparent 34%),linear-gradient(180deg,#f8fbff 0%,#eef5ff 48%,#fff 100%);}
#MainMenu,footer,header{visibility:hidden;}
.block-container{max-width:720px;padding-top:1rem;padding-bottom:2rem;}
.app-header{position:relative;overflow:hidden;background:radial-gradient(circle at 12% 18%,rgba(255,255,255,.26),transparent 18%),radial-gradient(circle at 92% 8%,rgba(56,189,248,.32),transparent 23%),linear-gradient(135deg,#071f52 0%,#1554d1 62%,#06b6d4 100%);border:1px solid rgba(255,255,255,.38);border-radius:34px;padding:22px;box-shadow:0 30px 80px rgba(15,23,42,.20);margin-bottom:14px;color:white;}
.app-header:before{content:"";position:absolute;inset:-80px -120px auto auto;width:300px;height:300px;border-radius:999px;background:rgba(255,255,255,.13);}
.app-header:after{content:"";position:absolute;left:22px;right:22px;bottom:0;height:3px;border-radius:999px 999px 0 0;background:linear-gradient(90deg,#38bdf8,#fff,#22c55e);opacity:.82;}
.hero-top{position:relative;z-index:2;display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:14px;}
.hero-tagline{color:rgba(255,255,255,.92);font-size:13px;font-weight:1000;}
.hero-badge{background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.30);color:#fff;border-radius:999px;padding:7px 11px;font-size:11px;font-weight:1000;white-space:nowrap;}
.brand{position:relative;z-index:2;display:flex;align-items:center;gap:16px;}
.logo{width:76px;height:76px;border-radius:26px;background:radial-gradient(circle at 28% 24%,rgba(255,255,255,.35),transparent 28%),linear-gradient(145deg,#0f2f77,#2563eb 54%,#06b6d4);display:flex;align-items:center;justify-content:center;color:white;font-size:38px;font-weight:1000;letter-spacing:-3px;box-shadow:0 18px 42px rgba(0,0,0,.24);}
.title{font-size:39px;line-height:.9;font-weight:1000;color:#fff;letter-spacing:-1.3px;text-shadow:0 4px 18px rgba(0,0,0,.20);}
.subtitle{margin-top:8px;color:rgba(255,255,255,.94);font-size:15px;font-weight:1000;}
.hero-pills{position:relative;z-index:2;display:flex;flex-wrap:wrap;gap:8px;margin-top:16px;}
.hero-pill{background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.25);color:#fff;border-radius:999px;padding:8px 12px;font-size:12px;font-weight:1000;}
.hero-action{position:relative;z-index:2;margin-top:14px;background:rgba(255,255,255,.92);color:#0f2f77;border-radius:18px;padding:12px 14px;font-size:14px;font-weight:1000;box-shadow:0 12px 28px rgba(0,0,0,.12);}
div[data-testid="stTabs"] [data-baseweb="tab-list"]{gap:8px;margin-top:10px;overflow-x:auto;}
div[data-testid="stTabs"] [data-baseweb="tab"]{background:rgba(255,255,255,.90);border:1px solid #dbeafe;border-radius:999px;padding:8px 12px;box-shadow:0 7px 16px rgba(15,23,42,.05);}
div[data-testid="stTabs"] button{font-size:14px;font-weight:1000;}
.form-card{background:rgba(255,255,255,.96);border:1px solid rgba(226,232,240,.95);border-radius:32px;overflow:hidden;box-shadow:0 26px 70px rgba(15,23,42,.13);margin-top:12px;}
.form-top{background:linear-gradient(135deg,#082f7a,#2563eb 62%,#06b6d4);color:white;padding:18px;display:flex;align-items:center;gap:12px;}
.form-icon{width:48px;height:48px;border-radius:16px;background:rgba(255,255,255,.16);display:flex;align-items:center;justify-content:center;font-size:28px;}
.form-title{font-size:23px;line-height:1.1;font-weight:1000;}.form-sub{font-size:13px;font-weight:800;opacity:.9;}.form-body{padding:16px;}
.step-title{font-size:18px;font-weight:1000;color:#0f172a;margin:6px 0 10px 0;}.thin-line{height:1px;background:linear-gradient(90deg,#22c55e,#38bdf8,transparent);margin:5px 0 14px 0;}
label{font-weight:900!important;color:#111827!important;}.stTextInput input,.stNumberInput input,.stSelectbox div[data-baseweb="select"]>div,textarea{background:#f8fafc!important;border:1px solid #dbeafe!important;border-radius:16px!important;min-height:48px;font-weight:800!important;}
.defect-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0 10px 0;}
.defect-tile{position:relative;border-radius:18px;padding:13px 7px;min-height:92px;text-align:center;border:2px solid transparent;box-shadow:0 10px 26px rgba(15,23,42,.08);font-weight:1000;}
.defect-icon{font-size:28px;line-height:1;margin-bottom:9px;}.defect-name{color:#0f172a;font-size:14px;font-weight:1000;line-height:1.2;}
.defect-selected{border-color:#ef233c!important;box-shadow:0 16px 32px rgba(239,35,60,.22);}.defect-selected:after{content:"✓";position:absolute;right:0;top:0;width:30px;height:30px;border-radius:0 16px 0 12px;background:#ef233c;color:#fff;font-size:18px;font-weight:1000;display:flex;align-items:center;justify-content:center;}
.d-blue{background:radial-gradient(circle at 25% 20%,rgba(59,130,246,.24),transparent 26%),linear-gradient(135deg,#eff6ff,#fff);}.d-orange{background:radial-gradient(circle at 25% 20%,rgba(249,115,22,.28),transparent 26%),linear-gradient(135deg,#fff7ed,#fff);}.d-teal{background:radial-gradient(circle at 25% 20%,rgba(20,184,166,.28),transparent 26%),linear-gradient(135deg,#ecfeff,#fff);}.d-purple{background:radial-gradient(circle at 25% 20%,rgba(139,92,246,.26),transparent 26%),linear-gradient(135deg,#f5f3ff,#fff);}.d-pink{background:radial-gradient(circle at 25% 20%,rgba(236,72,153,.25),transparent 26%),linear-gradient(135deg,#fff1f2,#fff);}.d-sky{background:radial-gradient(circle at 25% 20%,rgba(14,165,233,.25),transparent 26%),linear-gradient(135deg,#eff6ff,#fff);}.d-green{background:radial-gradient(circle at 25% 20%,rgba(34,197,94,.25),transparent 26%),linear-gradient(135deg,#f0fdf4,#fff);}.d-amber{background:radial-gradient(circle at 25% 20%,rgba(245,158,11,.25),transparent 26%),linear-gradient(135deg,#fffbeb,#fff);}.d-gray{background:radial-gradient(circle at 25% 20%,rgba(100,116,139,.15),transparent 26%),linear-gradient(135deg,#f8fafc,#fff);}.d-rose{background:radial-gradient(circle at 25% 20%,rgba(244,63,94,.24),transparent 26%),linear-gradient(135deg,#fdf2f8,#fff);}
.selected-result{margin-top:10px;background:linear-gradient(135deg,#fff1f2,#ffe4e6);border:2px solid #ef233c;color:#b91c1c;border-radius:16px;padding:10px;font-size:14px;font-weight:1000;text-align:center;}
.upload-head{background:linear-gradient(135deg,#eff6ff,#fff);border:1px solid #bfdbfe;border-radius:20px;padding:14px 16px;margin:12px 0 8px 0;box-shadow:0 10px 26px rgba(37,99,235,.08);}.upload-title{color:#0f172a;font-size:16px;font-weight:1000;margin-bottom:3px;}.upload-sub{color:#64748b;font-size:12px;font-weight:800;}
div[data-testid="stFileUploader"]{background:transparent!important;padding:0!important;margin-bottom:12px!important;}div[data-testid="stFileUploader"] section{background:#fff!important;border:2px dashed #93c5fd!important;border-radius:20px!important;padding:18px!important;min-height:86px!important;}div[data-testid="stFileUploader"] button{border-radius:14px!important;min-height:44px!important;min-width:112px!important;padding:0 18px!important;font-weight:1000!important;white-space:nowrap!important;}div[data-testid="stFileUploader"] small{display:none!important;}
div[data-testid="stButton"] button{border-radius:18px!important;min-height:52px!important;font-weight:1000!important;}.analyze-btn button{background:linear-gradient(135deg,#16c784,#0094ff)!important;color:white!important;border:0!important;font-size:18px!important;box-shadow:0 16px 36px rgba(0,148,255,.25);}.save-btn button{background:linear-gradient(135deg,#22c55e,#16a34a)!important;color:white!important;border:0!important;}.send-btn button{background:linear-gradient(135deg,#2563eb,#1554d1)!important;color:white!important;border:0!important;}
.result-card{background:white;border:1px solid #bbf7d0;border-radius:28px;padding:18px 15px;text-align:center;box-shadow:0 18px 42px rgba(22,163,74,.14);margin:14px 0;}.gauge{width:108px;height:108px;margin:0 auto 12px auto;border-radius:999px;background:conic-gradient(#22c55e 0 91%,#dcfce7 91% 100%);display:flex;align-items:center;justify-content:center;}.gauge-inner{width:82px;height:82px;border-radius:999px;background:white;display:flex;align-items:center;justify-content:center;flex-direction:column;color:#16a34a;font-weight:1000;}.gauge-num{font-size:25px;line-height:1;}.gauge-label{font-size:10px;}.result-title{font-size:24px;font-weight:1000;color:#16a34a;}.result-sub{color:#64748b;font-size:13px;font-weight:850;margin:4px 0 12px 0;}.result-box{background:#f8fafc;border:1px solid #e5e7eb;border-radius:16px;padding:11px;margin-bottom:8px;text-align:left;font-size:13px;font-weight:850;color:#334155;}.preview-box{min-height:115px;border:1px solid #e2e8f0;border-radius:18px;background:#f8fafc;color:#94a3b8;display:flex;align-items:center;justify-content:center;text-align:center;padding:13px;font-weight:900;}
.metric-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;}.metric-card{background:rgba(255,255,255,.94);border:1px solid #e5e7eb;border-left:7px solid var(--accent);border-radius:22px;padding:14px;display:flex;gap:11px;align-items:center;box-shadow:0 13px 31px rgba(15,23,42,.075);}.metric-icon{min-width:44px;width:44px;height:44px;border-radius:15px;background:var(--accent);color:white;display:flex;align-items:center;justify-content:center;font-size:23px;}.metric-label{color:#64748b;font-size:12px;font-weight:900;}.metric-value{color:#0f172a;font-size:22px;font-weight:1000;line-height:1.08;margin-top:4px;}.latest-card{background:rgba(255,255,255,.94);border:1px solid #e5e7eb;border-radius:22px;padding:12px;box-shadow:0 13px 31px rgba(15,23,42,.075);margin-bottom:10px;}
@media(max-width:640px){.block-container{max-width:100%;padding-left:.7rem;padding-right:.7rem;}.app-header{padding:18px;border-radius:28px;}.logo{width:58px;height:58px;font-size:31px;border-radius:20px;}.title{font-size:32px;}.subtitle{font-size:13px;}.hero-tagline{font-size:11px;line-height:1.25;}.hero-badge{font-size:10px;padding:6px 9px;}.hero-action{font-size:13px;}.defect-grid{grid-template-columns:1fr 1fr;}.metric-grid{grid-template-columns:1fr 1fr;}}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="app-header">
  <div class="hero-top"><div class="hero-tagline">🤖 {APP_VERSION}</div><div class="hero-badge">MOBILE READY</div></div>
  <div class="brand"><div class="logo">AI</div><div><div class="title">AI <span>CHECK</span></div><div class="subtitle">ช่วยคนคัดตรวจงานเบื้องต้น</div></div></div>
  <div class="hero-pills"><div class="hero-pill">📱 มือถือ</div><div class="hero-pill">⚡ เร็ว</div><div class="hero-pill">✅ ชัด</div></div>
  <div class="hero-action">ยึดโครงมือถือแบบ QUALITY ALERT แต่ปรับมาใช้กับ NXP.py</div>
</div>
""", unsafe_allow_html=True)

tab_ai, tab_dashboard, tab_history, tab_update, tab_master = st.tabs(["🔍 AI ตรวจงาน", "📊 Dashboard", "🕘 ประวัติ", "🟠 อัปเดต", "⚙️ Master"])

with tab_ai:
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    st.markdown('<div class="form-top"><div class="form-icon">🔍</div><div><div class="form-title">AI ตรวจงาน</div><div class="form-sub">กรอกข้อมูลงาน เลือกอาการ แล้วถ่ายรูป</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="form-body">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">1. ข้อมูลงาน</div><div class="thin-line"></div>', unsafe_allow_html=True)
    st.session_state.so = st.text_input("SO", value=st.session_state.so, placeholder="ค้นหา SO")
    st.session_state.pc = st.text_input("PC", value=st.session_state.pc, placeholder="ค้นหา PC")
    st.session_state.reporter = st.text_input("คนแจ้ง", value=st.session_state.reporter, placeholder="ชื่อคนแจ้ง")
    st.markdown('<div class="step-title">2. เลือกอาการ</div><div class="thin-line"></div>', unsafe_allow_html=True)
    names = [d["name"] for d in DEFECTS]
    current_index = names.index(st.session_state.defect) if st.session_state.defect in names else 0
    picked = st.selectbox("เลือกอาการ", names, index=current_index, key="defect_select")
    st.session_state.defect = picked
    st.markdown('<div class="defect-grid">', unsafe_allow_html=True)
    for d in DEFECTS:
        selected = st.session_state.defect == d["name"]
        st.markdown(f'<div class="defect-tile {d["class"]} {"defect-selected" if selected else ""}"><div class="defect-icon">{d["icon"]}</div><div class="defect-name">{d["name"]}</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="selected-result">✓ เลือกอยู่ : {st.session_state.defect}</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">3. ถ่ายรูปงาน</div><div class="thin-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-head"><div class="upload-title">📁 ถ่ายรูป / อัปโหลดรูป</div><div class="upload-sub">กดเลือกไฟล์ หรือใช้มือถือถ่ายรูปจากปุ่มนี้ได้เลย</div></div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(label="", type=["jpg", "jpeg", "png"], accept_multiple_files=False, label_visibility="collapsed")
    img = None
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True)
    else:
        st.markdown('<div class="preview-box">จะแสดงรูปที่ถ่ายที่นี่</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">4. ผลการวิเคราะห์</div><div class="thin-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="analyze-btn">', unsafe_allow_html=True)
    analyze = st.button("🚀 ส่งตรวจด้วย AI", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if analyze:
        if uploaded:
            st.session_state.result = True
        else:
            st.warning("ถ่ายรูปก่อน")
    if st.session_state.result and uploaded:
        now = datetime.now().strftime("%d/%m/%Y %H:%M")
        st.markdown(f'<div class="result-card"><div class="gauge"><div class="gauge-inner"><div class="gauge-num">91%</div><div class="gauge-label">มั่นใจ</div></div></div><div class="result-title">ไม่พบความผิดปกติ</div><div class="result-sub">คุณภาพงาน : ผ่านมาตรฐาน</div><div class="result-box">SO : {st.session_state.so or "-"}<br>PC : {st.session_state.pc or "-"}<br>คนแจ้ง : {st.session_state.reporter or "-"}<br>ประเภทที่ตรวจ : {st.session_state.defect}<br>เวลา : {now}</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        st.button("💾 บันทึกผลการตรวจ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div class="send-btn">', unsafe_allow_html=True)
        st.button("👤 ส่งงานต่อ / เรียกหัวหน้าตรวจ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="preview-box">รอส่งรูปเพื่อวิเคราะห์</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with tab_dashboard:
    st.markdown('<div class="step-title">📊 Dashboard วันนี้</div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    st.markdown('<div class="metric-card" style="--accent:#2563eb;"><div class="metric-icon">📷</div><div><div class="metric-label">งานตรวจวันนี้</div><div class="metric-value">0</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-card" style="--accent:#22c55e;"><div class="metric-icon">✅</div><div><div class="metric-label">ผ่าน</div><div class="metric-value">0</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-card" style="--accent:#ef233c;"><div class="metric-icon">🔴</div><div><div class="metric-label">พบปัญหา</div><div class="metric-value">0</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="metric-card" style="--accent:#f59e0b;"><div class="metric-icon">👤</div><div><div class="metric-label">รอหัวหน้า</div><div class="metric-value">0</div></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">📋 รายการล่าสุด</div>', unsafe_allow_html=True)
    st.markdown('<div class="latest-card">ยังไม่มีข้อมูลวันนี้</div>', unsafe_allow_html=True)

with tab_history:
    st.markdown('<div class="form-card"><div class="form-body">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">ค้นหาข้อมูลย้อนหลัง</div><div class="thin-line"></div>', unsafe_allow_html=True)
    st.date_input("วันที่")
    st.text_input("ค้นหา SO / PC")
    st.selectbox("สถานะ", ["ทั้งหมด", "ผ่าน", "พบปัญหา", "รอหัวหน้า"])
    st.button("🔎 ค้นหา", use_container_width=True)
    st.button("📤 Export Excel", use_container_width=True)
    st.markdown('<div class="preview-box">ยังไม่มีข้อมูลย้อนหลัง</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with tab_update:
    st.markdown('<div class="form-card"><div class="form-body">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">อัปเดตข้อมูล</div><div class="thin-line"></div>', unsafe_allow_html=True)
    st.text_input("SO")
    st.text_input("PC")
    st.text_input("ลูกค้า")
    st.text_area("ข้อกำหนด")
    st.text_area("Prompt AI")
    st.button("💾 บันทึกข้อมูล", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with tab_master:
    st.markdown('<div class="form-card"><div class="form-body">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Master</div><div class="thin-line"></div>', unsafe_allow_html=True)
    st.info("เก็บ Master PC / ลูกค้า / Register / Print Mark / Barcode / Prompt AI")
    st.text_input("PC")
    st.text_input("ลูกค้า")
    st.text_area("Register")
    st.text_area("Print Mark")
    st.text_area("Barcode")
    st.text_area("Prompt AI")
    st.button("💾 บันทึก Master", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
