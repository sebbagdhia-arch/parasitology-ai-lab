import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import base64
import time
from gtts import gTTS
import pandas as pd

# إعداد الصفحة
st.set_page_config(
    page_title="Laboratoire Parasitologie IA",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# عرض الشعار
render_logo()

# تهيئة سجل الفحوصات (للوحة التحكم)
if 'history' not in st.session_state:
    st.session_state.history = []

if 'step' not in st.session_state:
    st.session_state.step = 0

# --- 2. الشعار الخاص (Logo SVG) ---
def render_logo():
    logo_svg = """
<svg width="100%" height="80" viewBox="0 0 300 80" xmlns="http://www.w3.org/2000/svg">
    <circle cx="40" cy="40" r="35" fill="#E74C3C" opacity="0.1"/>
    <path d="M30 60 L50 60 L40 20 Z" fill="#000000"/>
    <circle cx="40" cy="20" r="10" stroke="#E74C3C" stroke-width="3" fill="none"/>
    <rect x="25" y="60" width="30" height="5" fill="#E74C3C"/>
    
    <text x="80" y="50" font-family="Arial, sans-serif" font-size="35" font-weight="bold" fill="#000000">
        DHIA <tspan fill="#E74C3C">LAB</tspan>
    </text>
</svg>
"""
    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)


# --- 3. قاموس اللغات (واجهة المستخدم فقط) ---
# الكلام الصوتي (السيناريو) يبقى كما هو
languages = {
    "Français": {
        "nav_home": "Accueil & Analyse",
        "nav_dash": "Tableau de Bord",
        "nav_about": "À propos",
        "start_btn": "Démarrer (Click Ici)",
        "read_title": "Lire le titre officiel",
        "camera_title": "Placez l'échantillon",
        "analyzing": "Analyse en cours...",
        "confidence": "Indice de Confiance",
        "body_loc": "Zone d'infection",
        "restart": "Nouvelle Analyse",
        "about_names": "Réalisé par : Sebbag Mohamed Dhia Eddine & Ben Seguir Mohamed",
        "about_level": "Niveau : 3ème Année - Laborantin de Santé Publique",
        "about_institute": "Institut : Institut National de Formation Supérieure Paramédicale de Ouargla (INSPM)",
        "about_desc": "Ce projet utilise l'intelligence artificielle (CNN) pour automatiser la détection des parasites intestinaux à l'état frais."
    },
    "العربية": {
        "nav_home": "الرئيسية والتحليل",
        "nav_dash": "لوحة المعلومات",
        "nav_about": "حول المشروع",
        "start_btn": "ابدأ العرض",
        "read_title": "قراءة العنوان الرسمي",
        "camera_title": "ضع العينة تحت الكاميرا",
        "analyzing": "جاري التحليل...",
        "confidence": "مؤشر الثقة",
        "body_loc": "مكان الإصابة",
        "restart": "تحليل جديد",
        "about_names": "إعداد: سباق محمد ضياء الدين & بن صغير محمد",
        "about_level": "المستوى: سنة ثالثة - مخبري في الصحة العمومية",
        "about_institute": "المعهد: المعهد الوطني للتكوين العالي شبه الطبي - ورقلة",
        "about_desc": "هذا المشروع يستخدم الذكاء الاصطناعي لأتمتة الكشف عن الطفيليات المعوية في الفحص المجهري المباشر."
    },
    "English": {
        "nav_home": "Home & Analysis",
        "nav_dash": "Dashboard",
        "nav_about": "About Us",
        "start_btn": "Start Presentation",
        "read_title": "Read Official Title",
        "camera_title": "Place Sample",
        "analyzing": "Analyzing...",
        "confidence": "Confidence Score",
        "body_loc": "Infection Zone",
        "restart": "New Analysis",
        "about_names": "Created by: Sebbag Mohamed Dhia Eddine & Ben Seguir Mohamed",
        "about_level": "Level: 3rd Year - Public Health Laboratory Technician",
        "about_institute": "Institute: Higher National Institute of Paramedical Training - Ouargla",
        "about_desc": "This project uses Artificial Intelligence (CNN) to automate the detection of intestinal parasites in fresh stool examination."
    }
}

# --- 4. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    render_logo() # الشعار
    st.markdown("---")
    
    # اختيار اللغة
    selected_lang = st.selectbox("🌍 Langue / اللغة", ["Français", "العربية", "English"])
    txt = languages[selected_lang]
    
    st.markdown("---")
    
    # التنقل
    page = st.radio("Navigation", [txt["nav_home"], txt["nav_dash"], txt["nav_about"]])
    
    st.markdown("---")
    # الوضع الليلي (Toggle) - تحويل CSS
    dark_mode = st.toggle("🌙 Dark Mode", value=False)

# --- 5. دوال النظام (الصوت والموديل) - كما هي ---
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
        estimated_duration = (len(text) * 0.08) + 0.5
        return estimated_duration
    except:
        return 2

@st.cache_resource
def load_model_and_labels():
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

# --- 6. التصميم (CSS) - يدعم الوضع الليلي ---
# تحديد الألوان بناء على الوضع
bg_color = "#1E1E1E" if dark_mode else "#F4F6F7"
text_color = "#FFFFFF" if dark_mode else "#154360"
card_bg = "rgba(40, 40, 40, 0.9)" if dark_mode else "rgba(255, 255, 255, 0.9)"

st.markdown(f"""
    <style>
    .stApp {{
        background: {bg_color};
        background-image: { "none" if dark_mode else "radial-gradient(circle at 50% 50%, #F4F6F7 0%, #D4E6F1 100%)" };
        color: {text_color};
    }}
    
    /* Animation du Microscope */
    @keyframes shake {{
        0% {{ transform: rotate(0deg); }}
        25% {{ transform: rotate(5deg); }}
        50% {{ transform: rotate(0deg); }}
        75% {{ transform: rotate(-5deg); }}
        100% {{ transform: rotate(0deg); }}
    }}
    .talking-microscope {{
        animation: shake 2s infinite ease-in-out;
        cursor: pointer;
        transition: transform 0.3s;
    }}
    .talking-microscope:hover {{ transform: scale(1.1); }}

    /* Floating Parasites */
    .floating-parasite {{
        position: fixed; z-index: 0; pointer-events: none; opacity: 0.6;
        color: { "#555" if dark_mode else "#000" }; /* طفيليات غامقة في الوضع الليلي */
    }}
    @keyframes floatUp {{
        0% {{ transform: translateY(110vh) rotate(0deg) scale(0.8); }}
        100% {{ transform: translateY(-10vh) rotate(360deg) scale(1.2); }}
    }}

    /* Camera Design */
    [data-testid="stCameraInput"] {{ border: none !important; background: transparent !important; }}
    [data-testid="stCameraInput"] > div {{ background-color: transparent !important; border: none !important; }}
    video {{
        border-radius: 50% !important;
        width: 300px !important; height: 300px !important;
        object-fit: cover !important;
        border: 8px solid { "#E74C3C" if dark_mode else "#3498DB" } !important;
        box-shadow: 0 0 30px { "rgba(231, 76, 60, 0.5)" if dark_mode else "rgba(52, 152, 219, 0.5)" } !important;
        clip-path: circle(50% at 50% 50%);
    }}

    /* Result Card */
    .result-card {{
        background: {card_bg};
        backdrop-filter: blur(10px);
        border-radius: 25px; padding: 25px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        text-align: center;
        border: 2px solid { "#E74C3C" if dark_mode else "white" };
        margin-top: 20px; position: relative; z-index: 1;
        animation: popIn 0.5s ease-out;
    }}
    @keyframes popIn {{ 0% {{ transform: scale(0.8); opacity: 0; }} 100% {{ transform: scale(1); opacity: 1; }} }}
    
    /* Stats Card (Dashboard) */
    .stat-box {{
        background: {card_bg};
        padding: 20px; border-radius: 15px;
        text-align: center; border-bottom: 5px solid #E74C3C;
    }}
    </style>
    
    <div class="floating-parasite" style="left: 5%; bottom: -10%; font-size: 50px; animation: floatUp 15s infinite linear;">🦠</div>
    <div class="floating-parasite" style="left: 15%; bottom: -20%; font-size: 30px; animation: floatUp 12s infinite linear; color: darkred;">🩸</div>
    <div class="floating-parasite" style="left: 50%; bottom: -30%; font-size: 70px; animation: floatUp 25s infinite linear;">🔬</div>
    <div class="floating-parasite" style="left: 85%; bottom: -25%; font-size: 55px; animation: floatUp 22s infinite linear; color: purple;">🦠</div>
""", unsafe_allow_html=True)

# --- النصوص والبيانات ---
intro_script = "Salam alikoum la famille ! C'est moi, le microscope intelligent de Dhia et Mouhamed. On a trop galéré pour me créer, on est K.O ! S'il vous plaît, donnez-nous une note légendaire, genre 19 sur 20 ! Ma t'cassrouch rasskoum !"
title_script = "Le titre officiel est : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

morphology_db = {
    "Amoeba": {"desc": "Forme irrégulière, pseudopodes.", "funny": "C'est une Amibe ! Elle bouge en mode ninja.", "loc": "Intestin (Gros intestin)"},
    "Giardia": {"desc": "Forme de poire, 2 noyaux.", "funny": "Wesh ! C'est Giardia avec ses lunettes de soleil.", "loc": "Intestin (Grêle)"},
    "Leishmania": {"desc": "Forme ovoïde, kinétoplaste.", "funny": "Leishmania détectée ! Petit mais costaud.", "loc": "Peau / Viscères"},
    "Plasmodium": {"desc": "Forme en bague (Ring).", "funny": "Aïe aïe aïe ! Paludisme confirmé.", "loc": "Sang (Globules rouges)"},
    "Trypanosoma": {"desc": "Fusiforme, flagelle libre.", "funny": "C'est Trypanosoma ! Il court comme Mahrez !", "loc": "Sang / Lymphe"},
    "Schistosoma": {"desc": "Oeuf à éperon (épine).", "funny": "Gros œuf piquant ! C'est la Bilharziose.", "loc": "Vessie / Intestin"},
    "Negative": {"desc": "Rien à signaler.", "funny": "Hamdoullah ! C'est propre, makach mard.", "loc": "Corps Sain"}
}

microscope_url = "https://cdn-icons-png.flaticon.com/512/930/930263.png"

# --- منطق الصفحات ---

# 1. صفحة About
if page == txt["nav_about"]:
    st.title(txt["nav_about"])
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.image(microscope_url, width=150)
    with col_b:
        st.markdown(f"### {txt['about_names']}")
        st.markdown(f"**{txt['about_level']}**")
        st.info(txt['about_institute'])
        st.write(txt['about_desc'])

# 2. صفحة Dashboard
elif page == txt["nav_dash"]:
    st.title(f"📊 {txt['nav_dash']}")
    
    if len(st.session_state.history) > 0:
        # إحصائيات
        total = len(st.session_state.history)
        df = pd.DataFrame(st.session_state.history, columns=["Parasite"])
        counts = df["Parasite"].value_counts()
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='stat-box'><h3>Total Scans</h3><h1>{total}</h1></div>", unsafe_allow_html=True)
        with c2:
            top_p = counts.idxmax()
            st.markdown(f"<div class='stat-box'><h3>Top Détection</h3><h1>{top_p}</h1></div>", unsafe_allow_html=True)
        
        st.write("---")
        st.subheader("Répartition / توزيع النتائج")
        st.bar_chart(counts, color="#E74C3C")
    else:
        st.warning("Aucune donnée disponible. Faites un scan d'abord ! / لا توجد بيانات، قم بالفحص أولاً")

# 3. الصفحة الرئيسية (التطبيق)
else:
    st.markdown(f"<h1 style='text-align: center; position: relative; z-index: 1;'>🧪 PFE : Dhia & Mohamed</h1>", unsafe_allow_html=True)

    # === المرحلة 0: المجهر المتكلم ===
    if st.session_state.step == 0:
        st.markdown(f"<h3 style='text-align: center; position: relative; z-index: 1;'>🔊 {txt['start_btn']}</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(f"""
                <div style="display: flex; justify-content: center; position: relative; z-index: 1;">
                    <img src="{microscope_url}" class="talking-microscope" width="200">
                </div>
            """, unsafe_allow_html=True)
            st.write("") 
            if st.button("🎙 Play", use_container_width=True):
                wait_time = speak_audio(intro_script)
                with st.status("...", expanded=True) as status:
                    time.sleep(wait_time)
                    status.update(label="OK", state="complete", expanded=False)
                st.session_state.step = 1
                st.rerun()

    # === المرحلة 1: العنوان ===
    elif st.session_state.step == 1:
        st.markdown(f"<h3 style='text-align: center; position: relative; z-index: 1;'>📜 {txt['read_title']}</h3>", unsafe_allow_html=True)
        if st.button("🎓 Lecture", type="primary", use_container_width=True):
            wait_time = speak_audio(title_script)
            with st.spinner("..."):
                time.sleep(wait_time)
            st.session_state.step = 2
            st.rerun()

    # === المرحلة 2: الكاميرا والتحليل ===
    elif st.session_state.step == 2:
        model, class_names = load_model_and_labels()
        st.markdown(f"<h3 style='text-align: center; color: #E74C3C; position: relative; z-index: 1;'>📸 {txt['camera_title']}</h3>", unsafe_allow_html=True)
        
        img_file = st.camera_input("Scanner", label_visibility="hidden")
        
        if img_file:
            # شريط التقدم (Progress Bar)
            progress_text = txt['analyzing']
            my_bar = st.progress(0, text=progress_text)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            
            image = Image.open(img_file).convert("RGB")
            
            # التحليل
            label = "Inconnu"
            conf = 0
            if model:
                size = (224, 224)
                image_res = ImageOps.fit(image, size, method=Image.LANCZOS)
                img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
                data = np.expand_dims(img_array, axis=0)
                prediction = model.predict(data, verbose=0)
                idx = np.argmax(prediction)
                if idx < len(class_names):
                    label = class_names[idx]
                conf = int(prediction[0][idx] * 100)
            else:
                label = "Giardia" # Simulation
                conf = 96
            
            # تسجيل النتيجة في Dashboard
            st.session_state.history.append(label)
            
            clean_key = label.strip()
            info = morphology_db.get(clean_key, {"desc": "...", "funny": f"C'est {clean_key} !", "loc": "?"})
            
            # عرض البطاقة
            st.markdown(f"""
            <div class="result-card">
                <h1 style="color: #E74C3C; font-size: 45px; margin:0;">{clean_key}</h1>
                <hr style="border: 1px solid #ddd;">
                <p style="font-size: 18px;"><b>📍 {txt['body_loc']}:</b> {info['loc']}</p>
                <p style="font-size: 18px;"><b>🔬 Morphologie:</b> {info['desc']}</p>
                <br>
                <p style="color: #E74C3C; font-weight: bold; font-size: 22px;">🤖 {info['funny']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # عداد الثقة (Confidence Meter)
            st.write("")
            st.markdown(f"**{txt['confidence']}: {conf}%**")
            st.progress(conf)
            
            # صورة توضيحية (Placeholder logic using standard images via Streamlit if desired, here keeping clean)
            # You can add 

            # [Image of X]
            # here if you want external images

            final_text = f"Résultat : {clean_key}. {info['funny']}"
            speak_audio(final_text)

            st.write("---")
            if st.button(f"🔄 {txt['restart']}", use_container_width=True):
                st.session_state.step = 0
                st.rerun()







