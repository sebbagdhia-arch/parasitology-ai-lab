
import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import base64
import time
from gtts import gTTS

# --- 1. إعداد الصفحة وتكوينها ---
st.set_page_config(
    page_title="PFE Dhia & Mohamed",
    page_icon="🔬",
    layout="centered"
)

# --- 2. إدارة الحالة (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- 3. دوال مساعدة (الصوت وتحميل النموذج) ---
def speak_audio(text, lang='fr'):
    """دالة لتشغيل الصوت دون إيقاف التطبيق"""
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
    except Exception as e:
        st.error(f"Erreur Audio: {e}")

@st.cache_resource
def load_model_ia():
    """تحميل النموذج أو استخدام وضع المحاكاة إذا لم يوجد ملف"""
    # محاولة البحث عن ملف الموديل
    model_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
    
    if model_path:
        model = tf.keras.models.load_model(model_path, compile=False)
        # محاولة قراءة ملف التصنيفات
        try:
            with open("labels.txt", "r") as f:
                class_names = [line.strip() for line in f.readlines()]
        except:
            class_names = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"]
        return model, class_names
    else:
        return None, None

# --- 4. التصميم (CSS) - هنا قمنا بإصلاح شكل الكاميرا والمجهر ---
st.markdown("""
    <style>
    /* استيراد خط جميل */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }

    /* خلفية التطبيق */
    .stApp {
        background: linear-gradient(to bottom, #E3F2FD, #FFFFFF);
    }

    /* 1. جعل الكاميرا دائرية (Fix Camera Shape) */
    [data-testid="stCameraInput"] {
        width: 100% !important;
        text-align: center;
    }
    
    [data-testid="stCameraInput"] video {
        border-radius: 50% !important;  /* جعل الفيديو دائري */
        border: 8px solid #2874A6;      /* إطار أزرق مثل المجهر */
        box-shadow: 0 0 20px rgba(40, 116, 166, 0.6);
        width: 320px !important;        /* تثبيت العرض */
        height: 320px !important;       /* تثبيت الطول */
        object-fit: cover;              /* تغطية كاملة للدائرة */
        mask-image: radial-gradient(circle, white 100%, black 100%);
    }

    /* 2. تحسين الأزرار */
    .stButton>button {
        background-color: #2874A6;
        color: white;
        border-radius: 30px;
        padding: 10px 25px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #1A5276;
        transform: scale(1.05);
    }

    /* 3. الطفيليات العائمة (الخلفية) */
    .floating-parasite {
        position: fixed;
        font-size: 35px;
        opacity: 0.15; /* شفافية خفيفة جداً لكي لا تزعج */
        z-index: 0;
        animation: floatUp 15s infinite linear;
    }

    @keyframes floatUp {
        0% { transform: translateY(100vh) rotate(0deg); }
        100% { transform: translateY(-10vh) rotate(360deg); }
    }

    /* 4. كارت النتيجة */
    .result-card {
        background-color: white;
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 5px solid #E74C3C;
        animation: fadeIn 1s;

dhia, [12/02/2026 20:48]
}
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* صورة المجهر التفاعلي */
    .microscope-img {
        transition: transform 0.3s;
        cursor: pointer;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    .microscope-img:hover {
        transform: scale(1.1) rotate(5deg);
    }
    </style>
    
    <div class="floating-parasite" style="left: 10%; animation-duration: 12s;">🦠</div>
    <div class="floating-parasite" style="left: 80%; animation-duration: 18s; font-size: 50px;">🩸</div>
    <div class="floating-parasite" style="left: 40%; animation-duration: 25s;">🧫</div>
    <div class="floating-parasite" style="left: 60%; animation-duration: 15s; color: green;">🦠</div>
""", unsafe_allow_html=True)

# --- 5. النصوص والبيانات ---
# رابط صورة مجهر واضحة جداً (مختبر)
microscope_url = "https://cdn-icons-png.flaticon.com/512/930/930263.png"

funny_script = "Salam alikoum la famille ! C'est moi, le microscope intelligent de Dhia et Mouhamed. On a trop galéré pour me créer, on est K.O ! S'il vous plaît, donnez-nous une note légendaire, genre 19 sur 20 ! Ma t'cassrouch rasskoum !"
full_title = "Le titre officiel est : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

morphology_db = {
    "Amoeba": {"desc": "Forme irrégulière, pseudopodes.", "funny": "C'est une Amibe ! Elle bouge en mode ninja."},
    "Giardia": {"desc": "Forme de poire, 2 noyaux.", "funny": "Wesh ! C'est Giardia avec ses lunettes de soleil."},
    "Leishmania": {"desc": "Forme ovoïde, kinétoplaste.", "funny": "Leishmania détectée ! Petit mais costaud."},
    "Plasmodium": {"desc": "Forme en bague (Ring).", "funny": "Aïe aïe aïe ! Paludisme confirmé. Les moustiques ont gagné."},
    "Trypanosoma": {"desc": "Fusiforme, flagelle libre.", "funny": "C'est Trypanosoma ! Il court comme Mahrez !"},
    "Schistosoma": {"desc": "Oeuf à éperon (épine).", "funny": "Gros œuf piquant ! C'est la Bilharziose."},
    "Negative": {"desc": "Rien à signaler.", "funny": "Hamdoullah ! C'est propre. Tu peux dormir tranquille."}
}

# --- 6. منطق التطبيق (Logic) ---

# العنوان الرئيسي
st.markdown("<h1 style='text-align: center; color: #154360;'>🧪 Laboratoire IA : Dhia & Mohamed</h1>", unsafe_allow_html=True)

# == المرحلة 0: الترحيب ==
if st.session_state.step == 0:
    st.markdown("<h3 style='text-align: center; color: #555;'>🔊 Cliquez sur le microscope pour commencer</h3>", unsafe_allow_html=True)
    
    # عرض المجهر كصورة قابلة للنقر (عن طريق زر مخفي فوقها تقريباً أو تحتها)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<img src="{microscope_url}" width="200" class="microscope-img">', unsafe_allow_html=True)
        st.write("") # مسافة
        if st.button("🎙 Activer le Microscope (Click Me)"):
            speak_audio(funny_script)
            with st.spinner("Le microscope parle..."):
                time.sleep(11) # وقت لإنهاء الكلام
            st.session_state.step = 1
            st.rerun()

# == المرحلة 1: العنوان الرسمي ==
elif st.session_state.step == 1:
    st.markdown("<h3 style='text-align: center; color: #555;'>📜 Présentation du Titre</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<img src="{microscope_url}" width="120" class="microscope-img" style="opacity:0.7;">', unsafe_allow_html=True)
        if st.button("🎓 Lire le Titre Officiel"):
            speak_audio(full_title)
            with st.spinner("Lecture en cours..."):
                time.sleep(10)
            st.session_state.step = 2
            st.rerun()

# == المرحلة 2: الكشف (الكاميرا) ==
elif st.session_state.step == 2:
    st.info(f"📝 {full_title}")
    
    st.markdown("<h2 style='text-align: center; color: #E74C3C;'>📸 Placez l'échantillon sous la lentille</h2>", unsafe_allow_html=True)
    
    # تحميل النموذج
    model, class_names = load_model_ia()

dhia, [12/02/2026 20:48]
# الكاميرا
    img_file = st.camera_input("Scanner", label_visibility="hidden")

    if img_file:
        # عرض صورة التحميل
        with st.spinner('Analyse intelligente en cours...'):
            image = Image.open(img_file).convert("RGB")
            
            # --- إذا كان النموذج موجوداً نستخدمه ---
            if model:
                size = (224, 224)
                image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
                img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
                data = np.expand_dims(img_array, axis=0)
                
                prediction = model.predict(data, verbose=0)
                idx = np.argmax(prediction)
                label = class_names[idx] if idx < len(class_names) else "Inconnu"
                conf = int(prediction[0][idx] * 100)
            
            # --- وضع المحاكاة (للتجربة فقط إذا لم يكن النموذج جاهزاً) ---
            else:
                time.sleep(2) # تمثيل وقت المعالجة
                label = "Giardia" # نتيجة تجريبية
                conf = 98
                st.warning("⚠️ Mode Simulation (Modèle introuvable)")

            # جلب النصوص
            # تنظيف الاسم من أي أرقام أو مسافات زائدة للمطابقة مع القاموس
            clean_label = label.split()[0] if " " in label else label
            info = morphology_db.get(clean_label, {"desc": "Non identifié", "funny": f"C'est quoi ça ? ({label})"})

            # عرض النتيجة بتصميم جميل
            st.markdown(f"""
            <div class="result-card">
                <h1 style="color: #2E86C1; margin-bottom: 0;">{label}</h1>
                <h3 style="color: #28B463; margin-top: 0;">Certitude: {conf}%</h3>
                <div style="background: #F4F6F7; padding: 10px; border-radius: 10px; margin: 15px 0;">
                    <p style="font-size: 18px;"><b>🔬 Morphologie:</b> {info['desc']}</p>
                </div>
                <p style="color: #CB4335; font-size: 20px; font-weight: bold; font-style: italic;">
                    🤖 "{info['funny']}"
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # الصوت النهائي
            if conf > 60:
                speak_audio(f"{label} détecté à {conf} pourcent. {info['funny']}")
            else:
                speak_audio("L'image est floue, je ne vois rien. Refais la photo !")

    # زر إعادة البدء
    st.write("---")
    if st.button("🔄 Nouvelle Analyse"):
        st.session_state.step = 0
        st.rerun()

