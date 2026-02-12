import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import requests
from gtts import gTTS
import base64
import time

# --- إعداد الصفحة ---
st.set_page_config(
    page_title="PFE IA Parasitologie | Dhia & Mouhamed",
    page_icon="🔬",
    layout="centered"
)

# --- إدارة المراحل (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- دالة الصوت (النطق) ---
def speak_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = "audio_temp.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
        # لا نحذف الملف فوراً لتجنب قطع الصوت
    except:
        pass

# --- CSS (خلفية طفيليات متحركة + تصميم الكاميرا والمجهر) ---
st.markdown("""
    <style>
    /* 1. خلفية الطفيليات العائمة (Floating Parasites) */
    .stApp {
        background-color: #f0f8ff;
        overflow: hidden;
    }
    
    /* إنشاء عناصر طفيليات متحركة في الخلفية */
    .floating-parasite {
        position: fixed;
        color: rgba(0,0,0,0.1); /* شفافية */
        font-size: 40px;
        animation: float 15s infinite linear;
        z-index: 0;
        pointer-events: none;
    }
    
    @keyframes float {
        0% { transform: translateY(110vh) rotate(0deg); opacity: 0.3; }
        100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
    }

    /* 2. جعل الكاميرا دائرية (عدسة) */
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important;
        border: 10px solid #2874A6;
        box-shadow: 0 0 30px rgba(40, 116, 166, 0.5);
        width: 300px !important;
        height: 300px !important;
        object-fit: cover;
        margin: auto;
        display: block;
    }

    /* 3. تصميم المجهر (زر شفاف فوق الصورة) */
    .microscope-container {
        position: relative;
        display: inline-block;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .microscope-container:active {
        transform: scale(0.95);
    }
    
    /* 4. تنسيق بطاقة النتيجة */
    .result-card {
        background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
        padding: 20px;
        border-radius: 20px;
        border-left: 10px solid #28B463;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        margin-top: 20px;
        position: relative;
        z-index: 1;
    }
    
    /* تنسيق العناوين */
    h1, h2, h3 { z-index: 1; position: relative; }
    </style>
    
    <div class="floating-parasite" style="left: 10%; animation-duration: 12s;">🦠</div>
    <div class="floating-parasite" style="left: 30%; animation-duration: 18s; color: red;">🩸</div>
    <div class="floating-parasite" style="left: 70%; animation-duration: 15s; font-size: 60px;">🐛</div>
    <div class="floating-parasite" style="left: 50%; animation-duration: 20s;">🧫</div>
    <div class="floating-parasite" style="left: 85%; animation-duration: 10s; color: green;">🦠</div>
    <div class="floating-parasite" style="left: 20%; animation-duration: 25s; font-size: 50px;">🔬</div>
""", unsafe_allow_html=True)

# --- رابط صورة المجهر (اونلاين لضمان العمل) ---
# استخدمنا رابط مباشر لصورة مجهر كرتوني ثلاثي الأبعاد لنتجنب خطأ الملف المفقود
microscope_url = "https://cdn-icons-png.flaticon.com/512/2821/2821012.png" 

# --- النصوص ---
funny_script = "Salam alikoum la famille ! C'est moi, le microscope intelligent de Dhia et Mouhamed. On a trop galéré pour me créer, on est K.O ! S'il vous plaît, donnez-nous une note légendaire, genre 19 sur 20 ! Ma t'cassrouch rasskoum ! Allez, cliquez encore !"
full_title = "Le titre officiel est : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

# --- الواجهة الرئيسية ---

# 1. العنوان والأسماء (دائماً ظاهرين)
st.markdown("<h1 style='text-align: center; color: #154360;'>🧪 Laboratoire IA : Dhia & Mouhamed</h1>", unsafe_allow_html=True)

# --- المراحل ---

# المرحلة 0: المجهر يرحب
if st.session_state.step == 0:
    st.markdown("<h3 style='text-align: center;'>🔊 Cliquez sur le microscope pour commencer</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # عرض صورة المجهر كزر
        if st.button("🎙️ Écouter le message (Click 1)"):
            speak_audio(funny_script)
            time.sleep(10) # انتظار انتهاء الكلام
            st.session_state.step = 1
            st.rerun()
            
    # عرض صورة المجهر الكبيرة
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="{microscope_url}" width="200" class="microscope-container">
        </div>
    """, unsafe_allow_html=True)

# المرحلة 1: قراءة العنوان
elif st.session_state.step == 1:
    st.markdown("<h3 style='text-align: center;'>📜 Lecture du Titre Officiel</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎓 Lire le Titre (Click 2)"):
            speak_audio(full_title)
            time.sleep(10)
            st.session_state.step = 2
            st.rerun()
            
    st.markdown(f"""
        <div style="text-align: center;">
            <img src="{microscope_url}" width="150" style="opacity: 0.8;">
        </div>
    """, unsafe_allow_html=True)

# المرحلة 2: الكاميرا والتحليل
elif st.session_state.step == 2:
    st.markdown(f"<h5 style='text-align: center; color: #566573;'>{full_title}</h5>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #E74C3C;'>📸 Placez votre échantillon</h2>", unsafe_allow_html=True)
    
    # تحميل النموذج
    @st.cache_resource
    def load_model_ia():
        m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
        l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f.lower()), None)
        if m_path and l_path:
            model = tf.keras.models.load_model(m_path, compile=False)
            with open(l_path, "r", encoding="utf-8") as f:
                classes = [line.strip().split(" ", 1)[-1] for line in f.readlines()]
            return model, classes
        return None, None

    model, class_names = load_model_ia()

    # القاموس المضحك (محدث)
    morphology_db = {
        "Amoeba": {
            "desc": "Forme irrégulière, pseudopodes.",
            "funny": "C'est une Amibe ! Elle bouge en mode ninja. Attention la dysenterie !"},
        "Giardia": {
            "desc": "Forme de poire, 2 noyaux.",
            "funny": "Wesh ! C'est Giardia avec ses lunettes de soleil. Il te regarde !"},
        "Leishmania": {
            "desc": "Forme ovoïde, kinétoplaste.",
            "funny": "Leishmania détectée ! Petit mais costaud. Faut appeler le médecin !"},
        "Plasmodium": {
            "desc": "Forme en bague (Ring).",
            "funny": "Aïe aïe aïe ! Paludisme confirmé. Les moustiques ont gagné cette fois."},
        "Trypanosoma": {
            "desc": "Fusiforme, flagelle libre.",
            "funny": "C'est Trypanosoma ! Il court aussi vite que Mahrez dans le sang !"},
        "Schistosoma": {
            "desc": "Oeuf à éperon (épine).",
            "funny": "Gros œuf piquant ! C'est la Bilharziose. C'est du sérieux mon frère."},
        "Negative": {
            "desc": "Rien à signaler.",
            "funny": "Hamdoullah ! C'est propre. Tu peux dormir tranquille, makach mard."}
    }

    if model:
        # الكاميرا
        img_file = st.camera_input("Scanner")
        
        if img_file:
            image = Image.open(img_file).convert("RGB")
            
            # معالجة
            size = (224, 224)
            image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
            data = np.expand_dims(img_array, axis=0)
            
            # توقع
            with st.spinner('Le microscope réfléchit...'):
                prediction = model.predict(data, verbose=0)
                idx = np.argmax(prediction)
                label = class_names[idx]
                conf = int(prediction[0][idx] * 100)
            
            # جلب المعلومات
            info = morphology_db.get(label, {"desc": "...", "funny": f"C'est {label} !"})
            
            # عرض النتيجة
            st.markdown(f"""
            <div class="result-card">
                <h1 style="color: #2E86C1;">{label}</h1>
                <h2 style="color: #28B463;">Probabilité: {conf}%</h2>
                <p><b>🔬 Caractéristiques:</b> {info['desc']}</p>
                <hr>
                <p style="color: #E74C3C; font-size: 18px;"><b>🤖 Le Microscope dit :</b> "{info['funny']}"</p>
            </div>
            """, unsafe_allow_html=True)
            
            # نطق النتيجة
            voice_text = f"J'ai trouvé {label} à {conf} pourcent ! {info['funny']}"
            if conf > 60:
                speak_audio(voice_text)
            else:
                st.warning("Image floue")
                speak_audio("Je ne vois rien, c'est flou. Refais la photo !")

    # زر العودة
    if st.button("🔄 Recommencer"):
        st.session_state.step = 0
        st.rerun()
