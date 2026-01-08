import streamlit as st
import time
import random
from streamlit_mic_recorder import mic_recorder
import google.generativeai as genai  # เพิ่มอันนี้

# --- ตั้งค่า Gemini AI ---
# นำ API Key จากหน้า Google AI Studio (Free tier) มาใส่ตรงนี้ครับ
GENAI_API_KEY = st.secrets["GEMINI_API_KEY"] 
genai.configure(api_key=GENAI_API_KEY)

# --- CSS ชุดแต่งองค์ทรงเครื่อง (Theme: Pink Mochi World 🌸) ---
def local_css():
    st.markdown("""
    <style>
        /* 1. นำเข้าฟอนต์ Mali (สำหรับภาษาไทย/อังกฤษแนวน่ารัก) และ Prompt (สำรอง) */
        @import url('https://fonts.googleapis.com/css2?family=Mali:wght@400;600;700&family=Prompt:wght@400;600&display&family=Pridi:wght@400;600&display&family=Playpen Sans Thai:wght@400;600&display=swap');
        
        /* 2. กำหนดฟอนต์หลักเป็น Mali เพื่อความคิ้วท์ */
        html, body, [class*="css"], p, div, span, label, button, input { 
            font-family: 'Mali', 'Prompt', cursive !important; 
            color: #FF1493 !important; /* สีตัวอักษรชมพูเข้ม */
        }
        
        /* พื้นหลัง: สีชมพูอ่อนมีจุด Polka Dot จางๆ */
        .stApp { 
            background-color: #FFF0F5; 
            background-image: radial-gradient(#FF69B4 0.5px, transparent 0.5px), radial-gradient(#FF69B4 0.5px, #FFF0F5 0.5px);
            background-size: 20px 20px;
            background-position: 0 0, 10px 10px;
        }

        /* --- หัวข้อใหญ่ (H1) เด้งดึ๋ง --- */
        h1 {
            color: #FF1493 !important;
            text-shadow: 4px 4px 0px #FFB6C1; /* เงาหนาๆ เหมือนสติ๊กเกอร์ */
            font-family: 'Playpen Sans Thai', cursive !important;
            animation: bounce 2s infinite ease-in-out;
            text-align: center;
            font-weight: 700;
            padding-bottom: 10px;
        }
        
        /* Animation: เด้งดึ๋ง */
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        /* --- กล่องข้อความ (Glass Header) --- */
        .glass-header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            padding: 15px;
            border: 3px dashed #FF69B4; /* เส้นประสีชมพู */
            text-align: center;
            box-shadow: 0 8px 16px rgba(255, 105, 180, 0.2);
            margin-bottom: 25px;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.27, 1.55); /* เด้งแบบเยลลี่ */
        }
        
        /* เอาเมาส์ชี้แล้วกล่องจะหมุนนิดนึง */
        .glass-header:hover {
            transform: scale(1.05) rotate(-2deg);
            border-color: #FF1493;
        }
        
        .glass-header h3 {
            margin: 0;
            font-weight: 700;
            color: #FF1493 !important;
            font-size: 22px;
            font-family: 'Playpen Sans Thai', cursive !important;
        }

        /* --- ปรับแต่งปุ่มอัดเสียงและอัปโหลด --- */
        /* ซ่อน label เดิมของตัวอัปโหลดไฟล์ */
        [data-testid="stFileUploader"] label { display: none; }
        [data-testid="stFileUploader"] { margin-top: -10px; }

        /* ปุ่มกดทั่วไป (Button Styles) */
        .stButton>button { 
            background: linear-gradient(180deg, #FFB6C1 0%, #FF69B4 100%) !important;
            color: white !important; 
            border-radius: 50px !important;
            border: 3px solid white !important;
            box-shadow: 0 4px 0px #FF1493; /* เงาแข็งด้านล่างแบบปุ่มเกม */
            font-size: 18px !important;
            font-weight: bold !important;
            transition: all 0.1s;
        }
        /* เวลากดปุ่ม ปุ่มจะยุบลง */
        .stButton>button:active {
            transform: translateY(4px);
            box-shadow: 0 0 0 #FF1493;
        }
        .stButton>button:hover {
            filter: brightness(1.1);
        }

        /* --- การ์ดผลลัพธ์ (Result Card) --- */
        .result-card { 
            background-color: #FFFFFF; 
            padding: 20px; 
            border-radius: 30px; 
            box-shadow: 0 10px 30px rgba(255, 105, 180, 0.3); 
            text-align: center; 
            border: 5px solid #FFC0CB; 
            margin-top: 20px;
            animation: popUp 0.6s cubic-bezier(0.68, -0.55, 0.27, 1.55);
        }
        @keyframes popUp { from { transform: scale(0); opacity: 0; } to { transform: scale(1); opacity: 1; } }

        .emotion-text { font-size: 26px; color: #FF1493; font-weight: bold; margin-top: 10px; }

        /* --- เอฟเฟกต์ตกแต่ง (Floating Items) --- */
        .floating-item { position: fixed; z-index: 0; opacity: 0.6; animation: float 6s ease-in-out infinite; }
        @keyframes float { 0% { transform: translateY(0px) rotate(0deg); } 50% { transform: translateY(-20px) rotate(10deg); } 100% { transform: translateY(0px) rotate(0deg); } }

    </style>
    
    <div class="floating-item" style="top: 10%; left: 5%; font-size: 40px;">☁️</div>
    <div class="floating-item" style="top: 20%; right: 10%; font-size: 30px; animation-delay: 1s;">🍓</div>
    <div class="floating-item" style="bottom: 15%; left: 10%; font-size: 35px; animation-delay: 2s;">🎀</div>
    <div class="floating-item" style="bottom: 30%; right: 5%; font-size: 40px; animation-delay: 3s;">🌸</div>
    """, unsafe_allow_html=True)

def predict_emotion(audio_bytes):
    try:
        # เลือกใช้โมเดล Flash เพื่อความเร็วและรองรับเสียง
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = """
        คุณคือน้องแมวชื่อ Mochi เป็น AI ผู้เชี่ยวชาญด้านอารมณ์
        1. ฟังเสียงที่แนบมานี้อย่างตั้งใจ
        2. วิเคราะห์อารมณ์ (เช่น สุข, เศร้า, โกรธ, ตื่นเต้น, เหนื่อย)
        3. ตอบสั้นๆ โดยบรรทัดแรกระบุ "Emoji อารมณ์" และบรรทัดที่สองบอก "ความรู้สึก" 
           เช่น: 💖✨ / งุ้ยยย อารมณ์ดีจังเลยน้าา
        """
        
        # ส่งข้อมูลเสียงไปวิเคราะห์ (สมมติเป็นไฟล์ mp3/wav ตามที่หน้าเว็บรับมา)
        response = model.generate_content([
            prompt,
            {'mime_type': 'audio/wav', 'data': audio_bytes}
        ])
        
        # แยก Emoji และข้อความออกจากกันเพื่อเอาไปใส่ใน UI เดิมของคุณ
        res_text = response.text.split('/')
        icon = res_text[0].strip() if len(res_text) > 1 else "🐱"
        msg = res_text[-1].strip()
        
        return {"text": msg, "icon": icon}
    except Exception as e:
        return {"text": f"งื้อออ หูแมวขัดข้อง: {e}", "icon": "❌"}

def main():
    local_css()
    
    # Header: แมวเด้งดึ๋ง
    st.markdown('<div style="text-align: center;"><img src="https://i.pinimg.com/originals/f9/42/5e/f9425ec6e73ca64317310db4a3f3e05c.gif" width="130" style="border-radius: 50%; border: 5px solid #FF1493; box-shadow: 0 5px 15px rgba(255,20,147,0.4);"></div>', unsafe_allow_html=True)
    st.markdown("<h1>🎀 น้อง Voice Mochi 🎀</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #FF69B4 !important;'>~ ส่งเสียงหวานๆ มาคุยกับเค้าหน่อยยย ~</p>", unsafe_allow_html=True)

    st.write("") 

    col1, col2 = st.columns(2)

    with col1:
        # กล่องซ้าย
        st.markdown('<div class="glass-header"><h3>🎤 อัดเสียงสดๆ จิ้มเลย!</h3></div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            # Widget อัดเสียง
            audio_record = mic_recorder(
                start_prompt="🔴 จิ้มอัดเสียง",
                stop_prompt="⏹ จิ้มหยุด",
                key='recorder',
            )
        
        if audio_record:
            st.audio(audio_record['bytes'])

    with col2:
        # กล่องขวา
        st.markdown('<div class="glass-header"><h3>📁ส่งไฟล์มาเลยงับ</h3></div>', unsafe_allow_html=True)
        
        # Widget อัปโหลด
        uploaded_file = st.file_uploader("เลือกไฟล์ WAV/MP3", type=['wav', 'mp3'])
        if uploaded_file:
            st.audio(uploaded_file)

    # Logic ประมวลผล
    audio_to_process = None
    if audio_record:
        audio_to_process = audio_record['bytes']
    elif uploaded_file:
        uploaded_file.seek(0)
        audio_to_process = uploaded_file.read()

    if audio_to_process:
        st.markdown("---") 
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            process_btn = st.button('✨ วิเคราะห์อารมณ์วิเศษ! ✨')

        if process_btn:
            with st.spinner('กำลังฟังอย่างตั้งใจ... ดุ๊กดิ๊กๆ 🐾'):
                result = predict_emotion(audio_to_process)
            
            # การ์ดผลลัพธ์
            st.markdown(f"""
            <div class="result-card">
                <div style="font-size: 70px; animation: bounce 1s infinite;">{result['icon']}</div>
                <div class="emotion-text">{result['text']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if "โกรธ" not in result['text']:
                st.balloons()

if __name__ == "__main__":
    main()