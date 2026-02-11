import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import requests
from streamlit_lottie import st_lottie
from gtts import gTTS
import base64

# --- إعداد الصفحة ---
st.set_page_config(
    page_title="PFE: Exploration IA Parasitologie",
    page_icon="🔬",
    layout="wide"
)

# --- دالة الصوت (المجهر المتكلم) ---
def speak_french(text, key_id):
    tts = gTTS(text=text, lang='fr', slow=False)
    filename = f"audio_{key_id}.mp3"
    tts.save(filename)
    
    # تحويل الصوت ليعمل تلقائياً
    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        
    md = f"""
        <audio autoplay="true" style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
    """
    st.markdown(md, unsafe_allow_html=True)
    os.remove(filename) # تنظيف الملف بعد التشغيل

# --- تصميم CSS متقدم (خلفية متحركة + عدسة مجهر) ---
st.markdown("""
    <style>
    /* خلفية متحركة بستايل علمي */
    .stApp {
        background-color: #e5e5f7;
        background-image:  radial-gradient(#444cf7 0.5px, transparent 0.5px), radial-gradient(#444cf7 0.5px, #e5e5f7 0.5px);
        background-size: 20px 20px;
        background-position: 0 0, 10px 10px;
        animation: slide 100s linear infinite;
    }
    
    @keyframes slide {
        from {background-position: 0 0;}
        to {background-position: 1000px 1000px;}
    }

    /* تحويل الكاميرا لشكل دائري (عدسة مجهر) */
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important;
        border: 8px solid #2E86C1;
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
    }
    
    /* تنسيق النصوص */
    h1 {
        text-shadow: 2px 2px 4px #000000;
        font-weight: 800 !important;
    }
    .result-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 20px;
        border-radius: 15px;
        border-left: 10px solid #28B463;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- تحميل الأنيميشن ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# مجهر كرتوني لطيف
lottie_micro = load_lottieurl("https://lottie.host/5a2d0438-4e86-427f-94f7-7275037286a5/1X7w9iFz6e.json") 
# إذا لم يعمل الرابط، استبدله بأي رابط Lottie آخر لمجهر

# --- الشريط الجانبي (المعلومات الرسمية) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022349.png", width=80)
    st.markdown("### 🎓 Projet de Fin d'Études")
    st.write("---")
    st.markdown("#### 👨‍🔬 Réalisé par :")
    st.info("**Sebbag Mohamed Dhia Eddine**")
    st.info("**Ben Seguir Mohamed**")
    st.write("---")
    st.warning("Application IA pour le diagnostic parasitologique.")

# --- الواجهة والعنوان الرسمي ---
col_logo, col_title = st.columns([1, 4])

with col_logo:
    if lottie_micro:
        st_lottie(lottie_micro, height=150, key="intro_anim")

with col_title:
    st.markdown("""
    <h1 style='color: #154360; font-size: 30px;'>Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais</h1>
    """, unsafe_allow_html=True)

# --- "المجهر المتكلم" (مرحلة الترحيب) ---
# نستخدم Session State لكي لا يعيد الكلام في كل مرة نضغط زر
if 'intro_played' not in st.session_state:
    st.session_state['intro_played'] = False

if not st.session_state['intro_played']:
    intro_text = "Bonjour ! Je suis votre assistant intelligent. Sebbag Mohamed Dhia Eddine et Ben Seguir Mohamed ont travaillé très dur pour me créer. S'il vous plaît, donnez-leur une excellente note, ils le méritent vraiment ! C'est une innovation !"
    speak_french(intro_text, "intro")
    st.session_state['intro_played'] = True
    st.toast("🔊 Activez le son pour entendre le microscope !", icon="🔊")

st.markdown("---")

# --- قاعدة البيانات ---
morphology_db = {
    "Amoeba": {"title": "Entamoeba histolytica", "desc": "Forme irrégulière, pseudopodes, noyau unique.", "risk": "Dysenterie amibienne."},
    "Giardia": {"title": "Giardia lamblia", "desc": "Forme de poire, 2 noyaux, flagelles, axostyle.", "risk": "Giardiose."},
    "Leishmania": {"title": "Leishmania (Amastigote)", "desc": "Forme ovoïde, noyau + kinétoplaste.", "risk": "Leishmaniose."},
    "Plasmodium": {"title": "Plasmodium (Malaria)", "desc": "Forme en bague dans les hématies.", "risk": "Paludisme."},
    "Trypanosoma": {"title": "Trypanosoma", "desc": "Fusiforme, flagelle libre, extracellulaire.", "risk": "Maladie du sommeil."},
    "Schistosoma": {"title": "Schistosoma (Oeuf)", "desc": "Gros œuf à éperon (épine) latéral/terminal.", "risk": "Bilharziose."},
    "Negative": {"title": "Négatif / Rien à signaler", "desc": "Aucun parasite détecté.", "risk": "RAS."}
}

# --- تحميل النموذج ---
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

# --- الكاميرا والتحليل ---
if model:
    st.write("### 👁️ Vue Microscopique (Placez l'échantillon)")
    
    # الكاميرا ستظهر دائرية بسبب كود CSS في الأعلى
    img_file = st.camera_input("Capture")
    
    if img_file:
        image = Image.open(img_file).convert("RGB")
        
        # المعالجة
        size = (224, 224)
        image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
        data = np.expand_dims(img_array, axis=0)
        
        with st.spinner('🤔 Le microscope réfléchit...'):
            pred = model.predict(data, verbose=0)
            idx = np.argmax(pred)
            label = class_names[idx]
            conf = pred[0][idx]
            conf_percent = round(conf * 100, 1)

        # --- عرض النتيجة والمجهر المتكلم ---
        st.markdown(f"""
            <div class="result-card">
                <h2 style="color: #196F3D;">Diagnostic : {label}</h2>
                <h4>Confiance : {conf_percent}%</h4>
            </div>
        """, unsafe_allow_html=True)

        # المجهر يتحدث بالنتيجة
        if conf > 0.65:
            speech_text = f"J'ai trouvé {label} ! Je suis sûr à {conf_percent} pourcent. Regardez les détails ci-dessous."
            speak_french(speech_text, "result")
            
            # التفاصيل
            if label in morphology_db:
                info = morphology_db[label]
                st.info(f"**Description:** {info['desc']}")
                st.error(f"**Pathologie:** {info['risk']}")
        else:
            st.warning("Je ne vois pas bien... Image floue ?")
            speak_french("Je ne suis pas sûr. L'image est un peu floue, essayez encore.", "fail")

else:
    st.error("Erreur: Modèle IA introuvable.")    st.error("Erreur : Les fichiers 'keras_model.h5' et 'labels.txt' sont introuvables sur GitHub.")
