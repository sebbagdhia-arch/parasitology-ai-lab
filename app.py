
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
        
        # كود HTML لتشغيل الصوت
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
        
        # حساب مدة تقريبية: كل 12 حرف يستغرق ثانية تقريباً + 2 ثانية احتياط
        estimated_duration = (len(text) / 10) + 2
        return estimated_duration
    except:
        return 3 # مدة افتراضية في حال الخطأ

@st.cache_resource
def load_model_and_labels():
    """تحميل النموذج وتنظيف الأسماء من الأرقام"""
    model = None
    classes = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"] # افتراضي
    
    # البحث عن ملف الموديل
    m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
    if m_path:
        model = tf.keras.models.load_model(m_path, compile=False)
    
    # البحث عن ملف الأسماء وتنظيفه
    l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f), None)
    if l_path:
        cleaned_classes = []
        with open(l_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                # هذا السطر يحل مشكلة 6égative
                # يقوم بفصل الرقم عن الاسم (مثل '0 Giardia' تصبح 'Giardia')
                parts = line.strip().split(" ", 1)
                if len(parts) > 1 and parts[0].isdigit():
                    cleaned_classes.append(parts[1])
                else:
                    cleaned_classes.append(line.strip())
        classes = cleaned_classes
        
    return model, classes

# --- 3. التصميم (CSS) ---
st.markdown("""
    <style>
    /* 1. إجبار الخلفية الملونة (تدرج أزرق طبي) */
    .stApp {
        background: linear-gradient(180deg, #EBF5FB 0%, #D6EAF8 100%);
    }
    
    /* 2. الطفيليات العائمة (تم جعلها أوضح) */
    .floating-parasite {
        position: fixed;
        font-size: 45px;
        opacity: 0.25; /* زيادة الوضوح قليلاً */
        z-index: 0;
        animation: floatUp 20s infinite linear;
        pointer-events: none;
    }

    @keyframes floatUp {
        0% { transform: translateY(100vh) rotate(0deg); }
        100% { transform: translateY(-10vh) rotate(360deg); }
    }

    /* 3. تصميم الكاميرا الدائرية (عدسة المجهر) */
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important;
        border: 12px solid #2E86C1;
        box-shadow: 0 0 25px rgba(46, 134, 193, 0.6);
        width: 300px !important;
        height: 300px !important;
        object-fit: cover;
    }
    
    /* توسيط الكاميرا */
    div[data-testid="stCameraInput"] {
        display: flex;
        justify-content: center;
    }

    /* 4. البطاقة */
    .result-card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 6px solid #E74C3C;
        margin-top: 20px;
    }
    </style>
    
    <div class="floating-parasite" style="left: 10%; animation-duration: 15s;">🦠</div>
    <div class="floating-parasite" style="left: 85%; animation-duration: 22s; color: darkred;">🩸</div>

<div class="floating-parasite" style="left: 30%; animation-duration: 18s;">🧫</div>
    <div class="floating-parasite" style="left: 60%; animation-duration: 25s; color: green;">🦠</div>
    <div class="floating-parasite" style="left: 50%; animation-duration: 12s; font-size: 60px;">🔬</div>
""", unsafe_allow_html=True)

# --- 4. المتغيرات والنصوص ---
if 'step' not in st.session_state:
    st.session_state.step = 0

microscope_url = "https://cdn-icons-png.flaticon.com/512/930/930263.png"

# النص الطويل المضحك
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

st.markdown("<h1 style='text-align: center; color: #154360;'>🧪 Laboratoire IA : Dhia & Mohamed</h1>", unsafe_allow_html=True)

# === المرحلة 0: المجهر المتكلم ===
if st.session_state.step == 0:
    st.markdown("<h3 style='text-align: center;'>🔊 Cliquez sur le microscope</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # صورة المجهر
        st.image(microscope_url, width=180)
        
        if st.button("🎙 Démarrer (Click Ici)"):
            # تشغيل الصوت
            wait_time = speak_audio(intro_script)
            
            # إظهار رسالة انتظار وشريط تقدم وهمي لضمان اكتمال الصوت
            with st.status("Le microscope parle...", expanded=True) as status:
                st.write("Initialisation de l'humour algérien...")
                time.sleep(wait_time) # الانتظار هنا حسب طول الجملة
                status.update(label="Terminé !", state="complete", expanded=False)
            
            st.session_state.step = 1
            st.rerun()

# === المرحلة 1: قراءة العنوان ===
elif st.session_state.step == 1:
    st.markdown("<h3 style='text-align: center;'>📜 Lecture du Titre</h3>", unsafe_allow_html=True)
    
    if st.button("🎓 Lire le titre officiel"):
        wait_time = speak_audio(title_script)
        with st.spinner("Lecture en cours..."):
            time.sleep(wait_time)
        st.session_state.step = 2
        st.rerun()

# === المرحلة 2: الكاميرا والنتيجة ===
elif st.session_state.step == 2:
    st.info("Exploration du potentiel de l'IA pour l'examen parasitologique.")
    
    st.markdown("<h2 style='text-align: center; color: #C0392B;'>📸 Placez l'échantillon</h2>", unsafe_allow_html=True)
    
    # تحميل الموديل والأسماء (مع إصلاح الأرقام)
    model, class_names = load_model_and_labels()
    
    # الكاميرا
    img_file = st.camera_input("Scanner", label_visibility="hidden")
    
    if img_file:
        image = Image.open(img_file).convert("RGB")
        
        # --- التحليل ---
        label = "Inconnu"

conf = 0
        
if model:
    size = (224, 224)
    image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
    img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
    data = np.expand_dims(img_array, axis=0)

    prediction = model.predict(data, verbose=0)
    idx = np.argmax(prediction)

    # التأكد من صحة الفهرس
    if idx < len(class_names):
        label = class_names[idx]  # الاسم هنا سيكون نظيفاً بدون أرقام

    conf = int(prediction[0][idx] * 100)

else:
    # وضع المحاكاة إذا لم يوجد موديل
    time.sleep(1)
    label = "Giardia"  # مثال
    conf = 95
    st.warning("Mode Simulation (Modèle introuvable)")


# تنظيف إضافي للاسم لضمان التطابق مع القاموس
# مثلاً لو الاسم ما زال فيه مسافات زائدة
clean_key = label.strip()

# البحث عن جزء من الكلمة في القاموس (مثلا Negative matches Negative)
info = morphology_db.get(clean_key, {"desc": "...", "funny": f"C'est {clean_key} !"})

# --- عرض النتيجة ---
st.markdown(f"""
<div class="result-card">
    <h1 style="color: #2E86C1; font-size: 40px;">{clean_key}</h1>
    <h3 style="color: #27AE60;">Confiance: {conf}%</h3>
    <hr>
    <p style="font-size: 18px;"><b>🔬 Morphologie:</b> {info['desc']}</p>
    <br>
    <p style="color: #C0392B; font-weight: bold; font-size: 20px;">🤖 {info['funny']}</p>
</div>
""", unsafe_allow_html=True)

# الصوت النهائي
final_text = f"Résultat : {clean_key}. {info['funny']}"
speak_audio(final_text)

# زر العودة
st.write("---")
if st.button("🔄 Nouvelle Analyse"):
    st.session_state.step = 0
    st.rerun()
