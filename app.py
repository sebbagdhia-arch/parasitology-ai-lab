
import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import base64
import time
from gtts import gTTS

# --- 1. إعداد الصفحة ---
st.set_page_config(
    page_title="Laboratoire Parasitologie IA",
    page_icon="🔬",
    layout="centered"
)

# --- 2. دوال النظام ---

def speak_audio(text, lang='fr'):
    """تشغيل الصوت مع حساب مدة الانتظار المناسبة"""
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = "temp_audio.mp3"
        tts.save(filename)
        
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        
        # كود HTML لتشغيل الصوت مخفي
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
        
        # حساب مدة تقريبية للانتظار
        estimated_duration = (len(text) / 10) + 2
        return estimated_duration
    except:
        return 3

@st.cache_resource
def load_model_and_labels():
    """تحميل النموذج وتنظيف الأسماء"""
    model = None
    classes = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"]
    
    m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
    if m_path:
        model = tf.keras.models.load_model(m_path, compile=False)
    
    l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f), None)
    if l_path:
        cleaned_classes = []
        with open(l_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split(" ", 1)
                if len(parts) > 1 and parts[0].isdigit():
                    cleaned_classes.append(parts[1])
                else:
                    cleaned_classes.append(line.strip())
        classes = cleaned_classes
        
    return model, classes

# --- 3. التصميم (CSS) - النسخة المحسنة ---
st.markdown("""
    <style>
    /* خلفية متدرجة جميلة */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #F4F6F7 0%, #D4E6F1 100%);
        overflow: hidden; /* لمنع ظهور أشرطة التمرير بسبب الطفيليات */
    }
    
    /* 1. أنيميشن المجهر الراقص */
    @keyframes shake {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(5deg); }
        50% { transform: rotate(0eg); }
        75% { transform: rotate(-5deg); }
        100% { transform: rotate(0deg); }
    }
    
    .talking-microscope {
        animation: shake 2s infinite ease-in-out;
        cursor: pointer;
        transition: transform 0.3s;
    }
    .talking-microscope:hover {
        transform: scale(1.1);
    }

    /* 2. الطفيليات العائمة (أكثر وضوحاً وحركة) */
    .floating-parasite {
        position: fixed;
        z-index: 0;
        pointer-events: none;
        opacity: 0.6; /* جعلناها أوضح */
        animation-timing-function: linear;
        animation-iteration-count: infinite;
    }

    @keyframes floatUp {
        0% { transform: translateY(110vh) rotate(0deg) scale(0.8); }
        100% { transform: translateY(-10vh) rotate(360deg) scale(1.2); }
    }

    /* 3. تصميم الكاميرا الدائرية بالكامل (إزالة المربع) */
    div[data-testid="stCameraInput"] {
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* جعل الفيديو دائرياً وقص الزوائد */
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important;
        width: 300px !important;
        height: 300px !important;
        object-fit: cover;
        border: 8px solid #3498DB;
        box-shadow: 0 0 30px rgba(52, 152, 219, 0.5);
        clip-path: circle(50% at 50% 50%); /* قص حقيقي */
    }


/* تغيير شكل زر التصوير المزعج */
    div[data-testid="stCameraInput"] button {
        border-radius: 50px !important;
        background-color: #E74C3C !important;
        color: white !important;
        border: 2px solid white !important;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(231, 76, 60, 0.4);
    }
    div[data-testid="stCameraInput"] button:hover {
        background-color: #C0392B !important;
        transform: scale(1.05);
    }

    /* 4. البطاقة */
    .result-card {
        background: rgba(255, 255, 255, 0.90);
        backdrop-filter: blur(10px);
        border-radius: 25px;
        padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        text-align: center;
        border: 2px solid white;
        margin-top: 20px;
        animation: popIn 0.5s ease-out;
    }
    
    @keyframes popIn {
        0% { transform: scale(0.8); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    </style>
    
    <div class="floating-parasite" style="left: 5%; bottom: -10%; font-size: 50px; animation: floatUp 15s infinite;">🦠</div>
    <div class="floating-parasite" style="left: 15%; bottom: -20%; font-size: 30px; animation: floatUp 12s infinite; color: darkred;">🩸</div>
    <div class="floating-parasite" style="left: 25%; bottom: -50%; font-size: 60px; animation: floatUp 20s infinite;">🧫</div>
    <div class="floating-parasite" style="left: 35%; bottom: -15%; font-size: 40px; animation: floatUp 18s infinite; color: green;">🦠</div>
    <div class="floating-parasite" style="left: 50%; bottom: -30%; font-size: 70px; animation: floatUp 25s infinite;">🔬</div>
    <div class="floating-parasite" style="left: 65%; bottom: -10%; font-size: 45px; animation: floatUp 16s infinite; color: orange;">🦠</div>
    <div class="floating-parasite" style="left: 75%; bottom: -40%; font-size: 35px; animation: floatUp 14s infinite;">🩸</div>
    <div class="floating-parasite" style="left: 85%; bottom: -25%; font-size: 55px; animation: floatUp 22s infinite; color: purple;">🦠</div>
    <div class="floating-parasite" style="left: 95%; bottom: -5%; font-size: 25px; animation: floatUp 10s infinite;">🧫</div>

""", unsafe_allow_html=True)

# --- 4. المتغيرات والنصوص ---
if 'step' not in st.session_state:
    st.session_state.step = 0

microscope_url = "https://cdn-icons-png.flaticon.com/512/930/930263.png"

# النصوص
intro_script = "Salam alikoum la famille ! C'est moi, le microscope intelligent de Dhia et Mouhamed. On a trop galéré pour me créer, on est K.O ! S'il vous plaît, donnez-nous une note légendaire, genre 19 sur 20 ! Ma t'cassrouch rasskoum !"
title_script = "Le titre officiel est : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

# قاموس المعلومات
morphology_db = {
    "Amoeba": {"desc": "Forme irrégulière, pseudopodes.", "funny": "C'est une Amibe ! Elle bouge en mode ninja."},
    "Giardia": {"desc": "Forme de poire, 2 noyaux.", "funny": "Wesh ! C'est Giardia avec ses lunettes de soleil."},
    "Leishmania": {"desc": "Forme ovoïde, kinétoplaste.", "funny": "Leishmania détectée ! Petit mais costaud."},
    "Plasmodium": {"desc": "Forme en bague (Ring).", "funny": "Aïe aïe aïe ! Paludisme confirmé. Les moustiques ont gagné."},
    "Trypanosoma": {"desc": "Fusiforme, flagelle libre.", "funny": "C'est Trypanosoma ! Il court comme Mahrez !"},
    "Schistosoma": {"desc": "Oeuf à éperon (épine).", "funny": "Gros œuf piquant ! C'est la Bilharziose."},
    "Negative": {"desc": "Rien à signaler.", "funny": "Hamdoullah ! C'est propre, makach mard."}
}

# --- 5. التطبيق ---

st.markdown("<h1 style='text-align: center; color: #154360; text-shadow: 2px 2px 4px #aaa;'>🧪 Laboratoire IA : Dhia & Mohamed</h1>", unsafe_allow_html=True)


# === المرحلة 0: المجهر المتكلم ===
if st.session_state.step == 0:
    st.markdown("<h3 style='text-align: center;'>🔊 Cliquez sur le microscope</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # صورة المجهر المتحركة (CSS class added)
        st.markdown(f"""
            <div style="display: flex; justify-content: center;">
                <img src="{microscope_url}" class="talking-microscope" width="200">
            </div>
        """, unsafe_allow_html=True)
        
        # مسافة بسيطة
        st.write("") 
        
        if st.button("🎙 Démarrer (Click Ici)", use_container_width=True):
            wait_time = speak_audio(intro_script)
            with st.status("Le microscope parle...", expanded=True) as status:
                st.write("Initialisation de l'humour algérien...")
                time.sleep(wait_time)
                status.update(label="Terminé !", state="complete", expanded=False)
            st.session_state.step = 1
            st.rerun()

# === المرحلة 1: قراءة العنوان ===
elif st.session_state.step == 1:
    st.markdown("<h3 style='text-align: center;'>📜 Lecture du Titre</h3>", unsafe_allow_html=True)
    
    if st.button("🎓 Lire le titre officiel", type="primary", use_container_width=True):
        wait_time = speak_audio(title_script)
        with st.spinner("Lecture en cours..."):
            time.sleep(wait_time)
        st.session_state.step = 2
        st.rerun()

# === المرحلة 2: الكاميرا والنتيجة ===
elif st.session_state.step == 2:
    
    # تحميل الموديل
    model, class_names = load_model_and_labels()
    
    st.markdown("<h3 style='text-align: center; color: #C0392B;'>📸 Placez l'échantillon sous la caméra</h3>", unsafe_allow_html=True)
    
    # الكاميرا الدائرية
    img_file = st.camera_input("Scanner", label_visibility="hidden")
    
    if img_file:
        image = Image.open(img_file).convert("RGB")
        
        # --- التحليل (مع إصلاح الخطأ) ---
        label = "Inconnu"
        conf = 0
        
        if model:
            size = (224, 224)
            # التصحيح هنا: استخدام Image.LANCZOS بدلاً من Image.Resampling.LANCZOS لتجنب الأخطاء
            image_res = ImageOps.fit(image, size, method=Image.LANCZOS)
            img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
            data = np.expand_dims(img_array, axis=0)
            
            prediction = model.predict(data, verbose=0)
            idx = np.argmax(prediction)
            
            if idx < len(class_names):
                label = class_names[idx]
            
            conf = int(prediction[0][idx] * 100)
        else:
            # محاكاة في حالة عدم وجود الموديل
            time.sleep(1)
            label = "Giardia"
            conf = 95
            st.warning("Mode Simulation (Modèle introuvable)")

        clean_key = label.strip()
        info = morphology_db.get(clean_key, {"desc": "...", "funny": f"C'est {clean_key} !"})
        
        # --- عرض النتيجة ---
        st.markdown(f"""
        <div class="result-card">
            <h1 style="color: #2E86C1; font-size: 45px; margin:0;">{clean_key}</h1>
            <h3 style="color: #27AE60;">Confiance: {conf}%</h3>
            <hr style="border: 1px solid #ddd;">
            <p style="font-size: 20px;"><b>🔬 Morphologie:</b><br>{info['desc']}</p>
            <br>
            <p style="color: #C0392B; font-weight: bold; font-size: 22px;">🤖 {info['funny']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        final_text = f"Résultat : {clean_key}. {info['funny']}"
        speak_audio(final_text)

    # زر العودة
    st.write("---")
    if st.button("🔄 Nouvelle Analyse", use_container_width=True):
        st.session_state.step = 0
        st.rerun()
