import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import requests
from streamlit_lottie import st_lottie
from gtts import gTTS
import base64
import time

# --- إعداد الصفحة ---
st.set_page_config(
    page_title="PFE: Dhia & Mouhamed",
    page_icon="🦠",
    layout="centered"
)

# --- إدارة المراحل (Session State) ---
# 0: البداية (كلام مضحك)
# 1: قراءة العنوان الرسمي
# 2: فتح الكاميرا
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- دالة الصوت ---
def speak_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = "temp_audio.mp3"
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
        os.remove(filename)
    except:
        pass

# --- CSS (خلفية طفيليات متحركة + كروية الكاميرا) ---
st.markdown("""
    <style>
    /* خلفية طفيليات متحركة وغير مزعجة */
    .stApp {
        background-color: #f4f8fb;
        background-image: url("https://cdn-icons-png.flaticon.com/512/2821/2821012.png"); /* أيقونة ميكروب */
        background-size: 80px 80px;
        background-blend-mode: soft-light;
        animation: floatBackground 20s linear infinite;
    }
    
    @keyframes floatBackground {
        0% { background-position: 0 0; }
        100% { background-position: 500px 500px; }
    }

    /* الكاميرا الدائرية (عدسة مجهر) */
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important;
        border: 8px solid #34495E;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        width: 280px !important;
        height: 280px !important;
        object-fit: cover;
    }

    /* زر التحدث الكبير */
    .stButton button {
        background-color: #E74C3C;
        color: white;
        font-size: 20px;
        border-radius: 50px;
        padding: 10px 30px;
        border: none;
        box-shadow: 0 4px 0 #C0392B;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #C0392B;
        transform: translateY(2px);
    }
    </style>
""", unsafe_allow_html=True)

# --- تحميل الشخصية (المجهر المتكلم) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# روبوت لطيف يمثل المجهر
lottie_robot = load_lottieurl("https://lottie.host/5a2d0438-4e86-427f-94f7-7275037286a5/1X7w9iFz6e.json")

# --- النصوص (السيناريو) ---
script_funny = "Salam alikoum la famille ! C'est moi, le microscope intelligent. Dhia et Mouhamed ont passé des nuits blanches pour me fabriquer. S'il vous plaît, donnez-nous 19 sur 20 ! On a charbonné dur ! Ma t'cassrouch rasskoum !"
script_title = "Le titre du projet est : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

# --- الواجهة التفاعلية ---

# 1. العنوان والأسماء (دائماً ظاهرين)
st.markdown("<h1 style='text-align: center; color: #1B4F72;'>🔬 PFE : Dhia & Mouhamed</h1>", unsafe_allow_html=True)
st.write("---")

# 2. عرض المجهر (الشخصية)
col_mid, col_img, col_mid2 = st.columns([1, 2, 1])
with col_img:
    if lottie_robot:
        st_lottie(lottie_robot, height=250, key="robot")

# 3. المنطق المتسلسل (المراحل)
if st.session_state.step == 0:
    st.info(" اضغط على الزر أدناه ليقدم المجهر نفسه 👇")
    if st.button("🎤 Écouter le Microscope (Click 1)"):
        speak_audio(script_funny)
        time.sleep(8) # انتظار انتهاء الكلام
        st.session_state.step = 1
        st.rerun()

elif st.session_state.step == 1:
    st.success("الآن، دعنا نسمع العنوان الرسمي للمشروع 👇")
    if st.button("📜 Lire le Titre Officiel (Click 2)"):
        speak_audio(script_title)
        time.sleep(8)
        st.session_state.step = 2
        st.rerun()

elif st.session_state.step == 2:
    # --- هنا يبدأ عمل الكاميرا والذكاء الاصطناعي ---
    st.markdown("### 📸 الكاميرا جاهزة الآن!")
    
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
    
    # القاموس
    morphology_db = {
        "Amoeba": {"desc": "Forme irrégulière, pseudopodes.", "funny": "Attention ! C'est une Amibe, elle se cache !"},
        "Giardia": {"desc": "Forme de poire, 2 noyaux.", "funny": "C'est Giardia avec ses lunettes !"},
        "Leishmania": {"desc": "Forme ovoïde, kinétoplaste.", "funny": "Leishmania détectée ! Petit mais dangereux."},
        "Plasmodium": {"desc": "Forme en bague (Ring).", "funny": "Aïe ! Paludisme (Malaria). Faut traiter ça."},
        "Trypanosoma": {"desc": "Fusiforme, flagelle libre.", "funny": "Trypanosoma ! Ça nage vite dans le sang."},
        "Schistosoma": {"desc": "Oeuf à éperon (épine).", "funny": "Gros œuf de Bilharziose ! Regarde l'épine."},
        "Negative": {"desc": "Rien à signaler.", "funny": "C'est propre ! Hamdoullah, pas de maladie."}
    }

    if model:
        # الكاميرا الدائرية
        img_file = st.camera_input("Scanner", label_visibility="collapsed")
        
        if img_file:
            image = Image.open(img_file).convert("RGB")
            
            # معالجة
            size = (224, 224)
            image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
            data = np.expand_dims(img_array, axis=0)
            
            # توقع
            prediction = model.predict(data, verbose=0)
            idx = np.argmax(prediction)
            label = class_names[idx]
            conf = prediction[0][idx]
            conf_percent = int(conf * 100)
            
            # عرض النتيجة
            info = morphology_db.get(label, {"desc": "?", "funny": ""})
            
            st.markdown(f"""
            <div style="background: white; padding: 20px; border-radius: 15px; text-align: center; border: 4px solid #2E86C1;">
                <h2 style="color: #E74C3C;">{label}</h2>
                <h3>Probabilité: {conf_percent}%</h3>
                <p>{info['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # نطق النتيجة
            if conf > 0.65:
                speech = f"Résultat : {label}. Je suis sûr à {conf_percent} pourcent. {info['funny']}"
                speak_audio(speech)
            else:
                st.warning("Image floue")
                speak_audio("Je ne vois rien. C'est flou !")

    # زر لإعادة التشغيل من البداية
    if st.button("🔄 Recommencer la présentation"):
        st.session_state.step = 0
        st.rerun()
