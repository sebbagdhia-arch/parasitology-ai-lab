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
    layout="wide"
)

# --- دالة الصوت (النطق) ---
def speak_dz(text, key_id):
    try:
        # نستخدم الفرنسية كلغة أساسية
        tts = gTTS(text=text, lang='fr', slow=False)
        filename = f"audio_{key_id}.mp3"
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
        # تنظيف
        os.remove(filename)
    except:
        pass

# --- CSS المجنون (خلفية طفيليات + كاميرا مجهر) ---
st.markdown("""
    <style>
    /* 1. خلفية الطفيليات المتحركة */
    @keyframes float {
        0% { transform: translateY(0px) rotate(0deg); opacity: 0.2; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 0.5; }
        100% { transform: translateY(0px) rotate(360deg); opacity: 0.2; }
    }
    
    .stApp {
        background-color: #f0f8ff;
        background-image: url("https://cdn-icons-png.flaticon.com/512/822/822102.png"); /* أيقونة فيروس باهتة */
        background-blend-mode: overlay;
        background-size: 100px 100px;
    }
    
    /* 2. تحويل الكاميرا لعدسة مجهر حقيقية */
    div[data-testid="stCameraInput"] {
        text-align: center;
        margin: auto;
    }
    
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important; /* دائرة كاملة */
        border: 10px solid #333;
        box-shadow: inset 0 0 50px #000; /* تأثير الظل الداخلي للعدسة */
        width: 300px !important;
        height: 300px !important;
        object-fit: cover;
    }
    
    /* إضافة خطوط التصويب (Crosshair) فوق الكاميرا */
    div[data-testid="stCameraInput"]::after {
        content: "+";
        font-size: 100px;
        color: rgba(255, 0, 0, 0.3);
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -60%);
        pointer-events: none;
    }

    /* 3. تصميم بطاقة النتيجة */
    .fun-card {
        background: white;
        border: 4px solid #2E86C1;
        border-radius: 20px;
        padding: 20px;
        text-align: center;
        box-shadow: 5px 5px 0px #2E86C1;
        animation: pop 0.5s ease-out;
    }
    @keyframes pop {
        0% { transform: scale(0); }
        80% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    </style>
""", unsafe_allow_html=True)

# --- تحميل أنيميشن المجهر (شخصية كرتونية) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        return r.json() if r.status_code == 200 else None
    except: return None

# هذا رابط لمجهر أو عالم كرتوني متحرك
lottie_character = load_lottieurl("https://lottie.host/625a6662-811c-4f81-9b68-80414436940d/D3f3j5gq2X.json")

# --- الشريط الجانبي (معلومات جدية) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3022/3022349.png", width=80)
    st.markdown("### 🇩🇿 Projet PFE 2026")
    st.write("---")
    st.info("**Sebbag Mohamed Dhia Eddine**")
    st.info("**Ben Seguir Mohamed**")
    st.write("---")
    st.caption("Application intelligente pour le diagnostic.")

# --- الواجهة الرئيسية ---
col_anim, col_text = st.columns([1, 3])

with col_anim:
    if lottie_character:
        st_lottie(lottie_character, height=200)

with col_text:
    st.markdown("""
    <h1 style='color: #1B4F72;'>Exploration IA & Parasitologie</h1>
    <h3 style='color: #E74C3C;'>Dhia & Mouhamed (Les Boss du Labo)</h3>
    """, unsafe_allow_html=True)

# --- السيناريو المضحك (Intro) ---
if 'intro_done' not in st.session_state:
    st.session_state['intro_done'] = False

if not st.session_state['intro_done']:
    # النص الجزائري/الفرنسي المضحك
    # نكتب الفرنسية بطريقة تجعل النطق يضحك
    text_intro = "Salam alikom l'équipe ! C'est moi, le microscope intelligent de Dhia et Mouhamed. Écoutez bien les profs, le projet est harba ! C'est du lourd. Donnez-nous une bonne note, genre 18 ou 19, ma tcassrouch rasskoum ! Allez, testez-moi !"
    speak_dz(text_intro, "welcome")
    st.session_state['intro_done'] = True
    st.toast("🔊 ارفع الصوت ! المجهر يتحدث !", icon="😂")

st.write("---")

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

# --- القاموس (الخصائص + جملة مضحكة لكل طفيلي) ---
morphology_db = {
    "Amoeba": {
        "desc": "Forme irrégulière, pseudopodes.", 
        "funny": "Ayaaa ! C'est une Amibe ! Elle bouge comme un ninja. Attention à la dysenterie sahbi !"},
    "Giardia": {
        "desc": "Forme de poire, 2 noyaux.", 
        "funny": "Regarde sa tête ! On dirait un petit fantôme avec des lunettes. C'est Giardia !"},
    "Leishmania": {
        "desc": "Forme ovoïde, kinétoplaste.", 
        "funny": "Oulala, Leishmania ! C'est petit mais c'est méchant. Faut traiter ça vite fait !"},
    "Plasmodium": {
        "desc": "Forme en bague (Ring).", 
        "funny": "Aïe aïe aïe ! Paludisme détecté ! Les moustiques ont fait des dégâts mon frère."},
    "Trypanosoma": {
        "desc": "Fusiforme, flagelle libre.", 
        "funny": "Wesh ! C'est Trypanosoma ! Ça court dans le sang comme Usain Bolt."},
    "Schistosoma": {
        "desc": "Oeuf à éperon (épine).", 
        "funny": "Gros œuf en vue ! Regarde l'épine sur le côté, c'est Schistosoma. Pas bon du tout !"},
    "Negative": {
        "desc": "Rien à signaler.", 
        "funny": "Hamdoullah ! Y'a rien du tout. Le patient est propre, c'est clean !"}
}

# --- منطقة الكاميرا (العدسة) ---
if model:
    st.markdown("<h3 style='text-align: center;'>📸 Visez la lentille ici</h3>", unsafe_allow_html=True)
    
    # الكاميرا ستظهر دائرية ومعدلة بالـ CSS
    img_file = st.camera_input("Placez l'échantillon", label_visibility="hidden")
    
    if img_file:
        image = Image.open(img_file).convert("RGB")
        
        # بروسيسينغ
        size = (224, 224)
        image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
        data = np.expand_dims(img_array, axis=0)
        
        with st.spinner('⏳ Attends, je calcule... (Dkika berk)'):
            pred = model.predict(data, verbose=0)
            idx = np.argmax(pred)
            label = class_names[idx]
            conf = pred[0][idx]
            conf_percent = int(conf * 100)

        # --- النتيجة والعرض ---
        col_res1, col_res2 = st.columns([2, 1])
        
        info = morphology_db.get(label, {"desc": "Inconnu", "funny": f"C'est {label} !"})
        
        with col_res1:
            st.markdown(f"""
                <div class="fun-card">
                    <h1 style="color: #2E86C1;">{label}</h1>
                    <h2 style="color: #28B463;">Probabilité: {conf_percent}%</h2>
                    <p style="font-size: 18px;"><b>🔬 Caractéristiques:</b> {info['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with col_res2:
            st.image(image, caption="Votre Capture", width=150)

        # --- الكلام المضحك عند النتيجة ---
        if conf > 0.65:
            # دمجنا النتيجة + النسبة + الجملة المضحكة
            speech = f"J'ai trouvé {label} à {conf_percent} pourcent ! {info['funny']}"
            speak_dz(speech, "res")
        else:
            st.warning("الصورة غير واضحة")
            speak_dz("Oh mon frère, l'image est floue ! Je vois walou. Refais la photo stp.", "flou")

else:
    st.error("Wesh ? Les fichiers du modèle sont où ?")
