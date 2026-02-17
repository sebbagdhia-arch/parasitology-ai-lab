import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import base64
import time
from gtts import gTTS
import pandas as pd
from datetime import datetime
from fpdf import FPDF


# إعداد الصفحة
st.set_page_config(
    page_title="DM Smart Lab AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# لوقو متحرك احترافي
st.markdown("""
<style>

/* خلفية متحركة */
body {
    background: linear-gradient(270deg, #ff0000, #ffffff, #ff0000);
    background-size: 600% 600%;
    animation: bgMove 10s ease infinite;
}

@keyframes bgMove {
    0% {background-position:0% 50%;}
    50% {background-position:100% 50%;}
    100% {background-position:0% 50%;}
}

/* حاوية اللوقو */
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 180px;
    perspective: 1000px;
}

/* اللوقو */
.logo {
    font-size: 80px;
    font-weight: bold;
    font-family: Arial, sans-serif;
    display: flex;
    gap: 20px;
    transform-style: preserve-3d;
    animation: rotate3D 4s infinite linear;
}

/* دوران 3D */
@keyframes rotate3D {
    0% { transform: rotateY(0deg); }
    100% { transform: rotateY(360deg); }
}

/* الحرف الأول */
.letter1 {
    color: red;
    text-shadow: 0 0 15px red;
    animation: swap1 2s infinite, glow 1.5s infinite alternate;
}

/* الحرف الثاني */
.letter2 {
    color: white;
    background: red;
    padding: 8px 18px;
    border-radius: 12px;
    box-shadow: 0 0 20px red;
    animation: swap2 2s infinite, glow 1.5s infinite alternate;
}

/* تبادل المكان */
@keyframes swap1 {
    0% { transform: translateX(0); }
    50% { transform: translateX(100px); }
    100% { transform: translateX(0); }
}

@keyframes swap2 {
    0% { transform: translateX(0); }
    50% { transform: translateX(-100px); }
    100% { transform: translateX(0); }
}

/* وميض */
@keyframes glow {
    from { opacity: 0.6; }
    to { opacity: 1; }
}

</style>

<!-- صوت -->
<audio id="logoSound" autoplay loop>
  <source src="https://www.soundjay.com/buttons/sounds/button-16.mp3" type="audio/mpeg">
</audio>

<!-- اللوقو -->
<div class="logo-container">
    <div class="logo">
        <span class="letter1">D</span>
        <span class="letter2">M</span>
    </div>
</div>

""", unsafe_allow_html=True)

# --- 2. إدارة الحالة (Session State Management) ---
# التأكد من أن المتغيرات موجودة لعدم حدوث أخطاء
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'intro_step' not in st.session_state: st.session_state.intro_step = 0 # 0=Start, 1=Funny, 2=Official/Unlock
if 'history' not in st.session_state: st.session_state.history = []
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = False # الوضع النهاري افتراضي للمستشفيات
if 'last_audio' not in st.session_state: st.session_state.last_audio = ""

# --- 3. قاعدة المعرفة والفكاهة (Dr. DhiaBot Brain) ---
# هنا نضع المعلومات العلمية + النكت التي طلبتها
parasite_db = {
    "Amoeba": {
        "morphology": "Pseudopodes (Pieds artificiels)",
        "desc": "Amibe dysentérique pathogène.",
        "funny": "Elle bouge en mode ninja ! Attention la dysenterie.",
        "risk": "Élevé"
    },
    "Giardia": {
        "morphology": "Forme de poire / 2 noyaux visibles",
        "desc": "Protozoaire flagellé intestinal.",
        "funny": "On dirait un fantôme avec des lunettes de soleil !",
        "risk": "Moyen"
    },
    "Leishmania": {
        "morphology": "Présence de Kinétoplaste",
        "desc": "Parasite transmis par le phlébotome.",
        "funny": "Petit mais costaud ! Faut appeler le médecin.",
        "risk": "Élevé"
    },
    "Plasmodium": {
        "morphology": "Ring form (Forme de bague) dans les GR",
        "desc": "Agent responsable du Paludisme (Malaria).",
        "funny": "Il se cache dans les globules rouges. Les moustiques ont gagné.",
        "risk": "URGENCE"
    },
    "Trypanosoma": {
        "morphology": "Flagelle libre et ondulant",
        "desc": "Parasite sanguin mobile.",
        "funny": "Il court comme Mahrez dans le sang !",
        "risk": "Élevé"
    },
    "Schistosoma": {
        "morphology": "Œuf avec éperon terminal ou latéral",
        "desc": "Ver hématophage (Bilharziose).",
        "funny": "Gros œuf piquant ! Aïe aïe aïe.",
        "risk": "Moyen"
    },
    "Negative": {
        "morphology": "Aucune structure parasitaire",
        "desc": "Échantillon sain.",
        "funny": "Hamdoullah ! C'est propre, tu peux dormir tranquille.",
        "risk": "Nul"
    }
}

# --- 4. التصميم السحري (CSS Magic) ---
# هذا الكود هو المسؤول عن الخلفية المتحركة وشكل المستشفى
def apply_css():
    # إعدادات الألوان بناءً على الوضع الليلي أو النهاري
    if st.session_state.get("dark_mode", False):
        bg_color = "#0f172a"
        text_color = "#e5e7eb"
        card_bg = "#1e293b"
        pattern_color = "rgba(255,255,255,0.08)"
        sidebar_bg = "#020617"
        sidebar_input_border = "#334155"
    else:
        bg_color = "#f8fafc"
        text_color = "#0f172a"
        card_bg = "#ffffff"
        pattern_color = "rgba(15,23,42,0.08)"
        sidebar_bg = "#f0f2f6"
        sidebar_input_border = "#cbd5e1"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"], p, span, label, div {{
        font-family: 'Poppins', sans-serif;
        color: {text_color} !important;
    }}

    h1, h2, h3, h4, h5, h6 {{
        color: {text_color} !important;
    }}

    /* الخلفية */
    .stApp {{
        background-color: {bg_color};
        background-image:
        radial-gradient({pattern_color} 1px, transparent 1px);
        background-size: 35px 35px;
    }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg};
    }}

    section[data-testid="stSidebar"] * {{
        color: {text_color} !important;
        font-weight: 500;
    }}

    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] textarea,
    section[data-testid="stSidebar"] select {{
        background-color: {sidebar_bg} !important;
        color: {text_color} !important;
        border: 1px solid {sidebar_input_border};
    }}

    /* العناصر العائمة */
    .floating-parasite {{
        position: fixed;
        opacity: 0.25;
        z-index: 0;
        animation: float 18s linear infinite;
        font-size: 48px;
        pointer-events: none;
    }}

    @keyframes float {{
        from {{ transform: translateY(110vh) rotate(0deg); }}
        to {{ transform: translateY(-15vh) rotate(360deg); }}
    }}

    /* البطاقات */
    .medical-card {{
        background-color: {card_bg};
        border-radius: 18px;
        padding: 22px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-left: 6px solid #2563eb;
        margin-bottom: 18px;
        position: relative;
        z-index: 2;
    }}

    /* الأزرار */
    div.stButton > button {{
        background: linear-gradient(90deg,#2563eb,#1e40af);
        color: white !important;
        border-radius: 10px;
        padding: 10px 22px;
        font-weight: 600;
    }}

    div.stButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(37,99,235,0.5);
    }}
    </style>

    <div class="floating-parasite" style="left:5%">🦠</div>
    <div class="floating-parasite" style="left:25%;animation-delay:3s">🧬</div>
    <div class="floating-parasite" style="left:55%;animation-delay:6s">🔬</div>
    <div class="floating-parasite" style="left:80%;animation-delay:1s">🩸</div>
    """, unsafe_allow_html=True)


# تفعيل CSS
apply_css()
# --- 5. الوظائف المحدثة (Functions) ---

def speak(text):
    """تحويل النص إلى صوت وتشغيله"""
    try:
        tts = gTTS(text=text, lang='fr')
        filename = f"audio_{int(time.time())}.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
        os.remove(filename)
    except: pass

def generate_pdf(p_info, result, conf, details):
    """توليد تقرير PDF ببيانات المريض والتقنيين"""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(0, 10, "DM SMART LAB - RAPPORT D'ANALYSE", 0, 1, 'C')
    pdf.ln(5)
    
    # Info Patient
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " INFORMATION PATIENT", 1, 1, 'L', 1)
    
    pdf.set_font("Arial", '', 12)
    pdf.ln(2)
    pdf.cell(95, 10, f"Nom: {p_info['Nom']}", 0, 0)
    pdf.cell(95, 10, f"Prenom: {p_info['Prenom']}", 0, 1)
    pdf.cell(60, 10, f"Age: {p_info['Age']} ans", 0, 0)
    pdf.cell(60, 10, f"Sexe: {p_info['Sexe']}", 0, 0)
    pdf.cell(70, 10, f"Poids: {p_info['Poids']} kg", 0, 1)
    pdf.cell(0, 10, f"Type d'echantillon: {p_info['Type']}", 0, 1)
    pdf.ln(5)
    
    # Resultat
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, " RESULTAT MICROSCOPIQUE IA", 1, 1, 'L', 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(255, 0, 0) # Red color for result
    pdf.cell(0, 10, f"PATHOGENE: {result}", 0, 1, 'C')
    pdf.set_text_color(0, 0, 0) # Reset color
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Confiance du Modele: {conf}%", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.multi_cell(0, 10, f"Morphologie: {details['morphology']}")
    pdf.multi_cell(0, 10, f"Interpretation: {details['desc']}")
    pdf.multi_cell(0, 10, f"Recommendation: {details['advice'] if 'advice' in details else 'Consulter un médecin.'}")
    
    pdf.ln(20)
    
    # Footer / Signatures
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, f"Fait le: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(95, 10, "Technicien de Labo 1:", 0, 0)
    pdf.cell(95, 10, "Technicien de Labo 2:", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 10, "DHIA", 0, 0) # اسمك
    pdf.cell(95, 10, "MOHAMED", 0, 1) # اسم محمد
    
    return pdf.output(dest='S').encode('latin-1')

@st.cache_resource
def load_model_ia():
    # محاكاة تحميل الموديل لضمان عمل الكود
    # استبدل هذا الجزء بكود التحميل الحقيقي الخاص بك إذا كان الملف موجوداً
    model = None
    classes = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Trypanosoma", "Schistosoma", "Negative"]
    
    # محاولة تحميل الموديل الحقيقي
    try:
        files = os.listdir()
        h5 = next((f for f in files if f.endswith(".h5")), None)
        if h5: model = tf.keras.models.load_model(h5, compile=False)
    except: pass
    
    return model, classes

# --- 6. واجهة تسجيل الدخول (Login) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div class='medical-card' style='text-align: center;'>
            <h1 style='color:#2E86C1;'>🧬 DHIA SMART LAB</h1>
            <p>Accès Réservé au Personnel Médical</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identifiant", placeholder="Dr. Dhia")
        pwd = st.text_input("Mot de Passe", type="password")
        
        if st.button("SE CONNECTER"):
            if pwd == "1234": # كلمة السر البسيطة
                st.session_state.logged_in = True
                st.session_state.user_name = f"Dr. {user}" if user else "Dr. Dhia"
                st.rerun()
            else:
                st.error("Accès Refusé !")
    st.stop()

# --- 7. التطبيق الرئيسي (بعد الدخول) ---

# --- 1. إعداد الصفحة ---
st.set_page_config(
    page_title="DM SMART LAB",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. إدارة الحالة (Session State) ---
if 'intro_step' not in st.session_state:
    st.session_state.intro_step = 0
if 'history' not in st.session_state:
    st.session_state.history = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'last_audio' not in st.session_state:
    st.session_state.last_audio = ""

# --- 3. الدوال المساعدة ---

# دالة نطق النص (Text to Speech)
def speak(text):
    try:
        tts = gTTS(text=text, lang='fr')
        # الحفظ في ذاكرة مؤقتة لعدم إنشاء ملفات كثيرة
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur Audio: {e}")

# دالة تحميل الموديل (وهمية لتعمل الواجهة بدون ملف الموديل الحقيقي)
# ملاحظة: استبدل هذا الجزء بكود تحميل الموديل الحقيقي .h5 لاحقاً
@st.cache_resource
def load_model_ia():
    # هذا مجرد تمثيل لعدم وجود ملف الموديل الآن
    model = "FakeModel" 
    class_names = ["Giardia", "Amoeba", "Plasmodium", "Leishmania", "Negative"]
    return model, class_names

# قاعدة بيانات المعلومات
parasite_db = {
    "Giardia": {"morphology": "Forme de poire, flagellé", "funny": "Il vous sourit sous le microscope ! 🤡", "desc": "Parasite intestinal flagellé."},
    "Amoeba": {"morphology": "Irrégulier, pseudopodes", "funny": "Le métamorphe du monde microscopique.", "desc": "Protozoaire pouvant causer la dysenterie."},
    "Plasmodium": {"morphology": "Anneau dans GR", "funny": "Le passager clandestin des moustiques.", "desc": "Agent responsable du paludisme."},
    "Leishmania": {"morphology": "Petit, rond/ovale", "funny": "Ne le laissez pas laisser sa marque !", "desc": "Transmis par les phlébotomes."},
    "Negative": {"morphology": "Aucun parasite", "funny": "Rien à signaler, le patient est clean !", "desc": "Échantillon sain."}
}

# دالة توليد PDF (وهمية للتحميل)
def generate_pdf(patient_data, result, conf, info):
    # إنشاء ملف نصي بسيط بدلاً من PDF معقد لتجنب مكتبات إضافية في هذا المثال
    text_content = f"""
    RAPPORT MÉDICAL - DM SMART LAB
    ------------------------------
    Date: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    Patient: {patient_data['Nom']} {patient_data['Prenom']}
    Age: {patient_data['Age']} | Sexe: {patient_data['Sexe']}
    Type: {patient_data['Type']}
    
    RÉSULTAT: {result}
    Confiance IA: {conf}%
    Morphologie: {info['morphology']}
    
    Validé par: Dr. DhiaBot 🤖
    """
    return text_content.encode('utf-8')

# --- 4. الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3050/3050525.png", width=100)
    st.markdown("## 🧬 DM SMART LAB")
    st.markdown("*Where Science Meets Intelligence*")
    st.markdown("---")
    
    lang = st.selectbox("🌍 Langue", ["Français 🇫🇷", "العربية 🇩🇿", "English 🇬🇧"])
    
    st.markdown("---")
    # القائمة الرئيسية
    menu = st.radio("Navigation", ["🏠 Accueil (Unlock)", "🔬 Scan & Analyse", "📘 Encyclopédie", "📊 Dashboard", "ℹ️ À Propos"])
    
    st.markdown("---")
    dark = st.toggle("🌙 Mode Nuit", value=st.session_state.dark_mode)
    if dark:
        st.markdown("""
        <style>
        .stApp { background-color: #1E1E1E; color: white; }
        .medical-card { background-color: #333; color: white; border: 1px solid #555; }

</style>
        """, unsafe_allow_html=True)
    
    # زر إعادة التشغيل (Logout وهمي)
    if st.button("🔴 Déconnexion"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# CSS مخصص للبطاقات
st.markdown("""
<style>
.medical-card {
    background-color: #f0f2f6;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #2E86C1;
    margin-bottom: 20px;
    color: black;
}
</style>
""", unsafe_allow_html=True)

# --- 5. منطق الصفحات ---

# === الصفحة 1: الاستقبال (Accueil) ===
if menu == "🏠 Accueil (Unlock)":
    st.title("👋 Bienvenue au DM SMART LAB")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/123/123389.png", width=250)
    with col2:
        st.markdown("""
        <div class='medical-card'>
            <h3>🤖 Assistant Dr. DhiaBot</h3>
            <p>Système de sécurité vocale. Veuillez suivre les étapes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # الخطوة 1: التعريف والنكتة
        if st.session_state.intro_step == 0:
            st.warning("🔒 Étape 1 : Présentation requise")
            if st.button("🔊 1. PRÉSENTATION & HUMOUR", use_container_width=True):
                cur_time = datetime.now().strftime("%H:%M")
                txt_1 = f"Bonjour ! Il est {cur_time}. Je suis l'IA du laboratoire, développée par les Techniciens Supérieurs Dhia et Mohamed. Préparez vos lames... et s'il vous plaît, ne me chatouillez pas avec le microscope !"
                
                speak(txt_1) 
                with st.spinner("Dr. DhiaBot parle... 🔊"):
                    time.sleep(16) # زيادة الوقت لضمان انتهاء الكلام
                st.session_state.intro_step = 1
                st.rerun()
                
        # الخطوة 2: العنوان الرسمي
        elif st.session_state.intro_step == 1:
            st.warning("🔒 Étape 2 : Validation Officielle")
            if st.button("🔊 2. TITRE DU PROJET", use_container_width=True):
                txt_2 = "Projet de Fin d'Études : Identification des Parasites par Intelligence Artificielle. Présenté par Dhia et Mohamed. Institut National de Formation Supérieure Paramédicale de Ouargla."
                
                speak(txt_2)
                with st.spinner("Lecture du titre officiel... 🔊"):
                    time.sleep(15) # زيادة الوقت لضمان انتهاء الكلام
                st.session_state.intro_step = 2
                st.rerun()
                
        # الخطوة 3: مفتوح
        elif st.session_state.intro_step == 2:
            st.success("✅ SYSTÈME DÉVERROUILLÉ ! Vous pouvez passer au SCAN.")
            st.balloons()
            if st.button("Aller au Scan ➡️"):
                st.info("Veuillez cliquer sur '🔬 Scan & Analyse' dans le menu latéral.")

# === الصفحة 2: الفحص (Scan) ===
elif menu == "🔬 Scan & Analyse":
    st.title("🔬 Unité de Diagnostic IA")
    
    # حماية الدخول
    if st.session_state.intro_step < 2:
        st.error("⛔️ ACCÈS REFUSÉ : Veuillez activer le système dans la page 'Accueil' d'abord !")
        st.stop()
        
    # 1. إدخال بيانات المريض
    st.markdown("#### 1. Informations du Patient")
    with st.container():
        c_a, c_b = st.columns(2)
        p_nom = c_a.text_input("Nom", placeholder="ex: Benali")
        p_prenom = c_b.text_input("Prénom", placeholder="ex: Ahmed")
        
        c_c, c_d, c_e, c_f = st.columns(4)
        p_age = c_c.number_input("Age", 1, 100, 30)
        p_sexe = c_d.selectbox("Sexe", ["H", "F"])
        p_type = c_e.selectbox("Échantillon", ["Selles", "Sang", "Autre"])
        thermal = c_f.toggle("🔥 Vision Thermique")

    st.markdown("---")
    st.markdown("#### 2. Capture Microscopique")
    
    model, class_names = load_model_ia()

img_file = st.camera_input(
    "Placez la lame et capturez",
    label_visibility="visible"
)

if img_file and not p_nom:

    st.error("⚠️ Veuillez entrer le NOM du patient ci-dessus !")

elif img_file and p_nom:

    col_res1, col_res2 = st.columns([1, 1])

    with col_res1:
        image = Image.open(img_file).convert("RGB")

        if thermal:
            gray = ImageOps.grayscale(image)
            disp_img = ImageOps.colorize(
                gray,
                black="blue",
                white="yellow",
                mid="red"
            )
            st.image(
                disp_img,
                caption="Vue Thermique (Activée)",
                use_container_width=True
            )
        else:
            st.image(
                image,
                caption="Vue Normale",
                use_container_width=True
            )

    with col_res2:
  with st.spinner("Traitement IA en cours..."):

    pass  # ضع هنا كود المعالجة لاحقًا

    time.sleep(2)  # محاكاة وقت المعالجة

    # محاكاة التنبؤ (يجب ربط الموديل الحقيقي هنا)
    # اختيار نتيجة عشوائية للمعاينة فقط
    import random
    predicted_label = random.choice(class_names)
    conf = random.randint(75, 99)

    # جلب المعلومات من قاعدة البيانات
    info = parasite_db.get(predicted_label, parasite_db["Negative"])

    # عرض النتيجة
    st.markdown(f"""
    <div class='medical-card' style='border-left: 5px solid red; padding:10px;'>
        <h2 style='color:red'>{predicted_label}</h2>
        <p><b>Confiance:</b> {conf}%</p>
        <p><b>Morphologie:</b> {info['morphology']}</p>
        <hr>
        <p>🤡 <i>{info['funny']}</i></p>
    </div>
    """, unsafe_allow_html=True)

    # الصوت
    res_txt = f"Résultat pour {p_nom} : {predicted_label}. {info['funny']}"
    if st.session_state.last_audio != res_txt:
        speak(res_txt)
        st.session_state.last_audio = res_txt

    # حفظ في السجل
    if st.button("💾 Sauvegarder dans la base"):
        st.session_state.history.append({
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Patient": p_nom,
            "Parasite": predicted_label,
            "Status": "Succès"
        })
        st.success("Données sauvegardées avec succès.")

    # تحميل PDF
    p_data = {
        "Nom": p_nom,
        "Prenom": p_prenom,
        "Age": p_age,
        "Sexe": p_sexe,
        "Type": p_type
    }
    pdf_bytes = generate_pdf(p_data, predicted_label, conf, info)
    st.download_button(
        "📥 Télécharger Rapport",
        pdf_bytes,
        f"Rapport_{p_nom}.txt",
        "text/plain",
        use_container_width=True
    )

# === الصفحة 3: الموسوعة (Encyclopédie) ===
elif menu == "📘 Encyclopédie":
    st.title("📘 Encyclopédie des Parasites")
    parasites_list = {
        "Giardia": {"danger": "⭐️⭐️", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Giardia_lamblia_SEM_8698_lores.jpg/220px-Giardia_lamblia_SEM_8698_lores.jpg"},
        "Amoeba": {"danger": "⭐️⭐️⭐️", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Entamoeba_histolytica_01.jpg/220px-Entamoeba_histolytica_01.jpg"},
        "Plasmodium": {"danger": "⭐️⭐️⭐️⭐️⭐️", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Plasmodium_falciparum_01.png/220px-Plasmodium_falciparum_01.png"},
        "Leishmania": {"danger": "⭐️⭐️⭐️⭐️", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Leishmania_tropica_promastigote.jpg/220px-Leishmania_tropica_promastigote.jpg"}

}
    col_x, col_y = st.columns(2)
    for p_name, p_data in parasites_list.items():
        with st.expander(f"🦠 {p_name}"):
            c1, c2 = st.columns([1, 2])
            with c1: st.image(p_data["img"])
            with c2:
                st.write(f"Danger: {p_data['danger']}")
                st.write(f"Desc: {parasite_db.get(p_name, {}).get('desc', '')}")

# === الصفحة 4: لوحة التحكم (Dashboard) ===
elif menu == "📊 Dashboard":
    st.title("📊 Tableau de Bord Clinique")

    if len(st.session_state.history) > 0:
        # إنشاء DataFrame
        df = pd.DataFrame(st.session_state.history)
        
        # التأكد من الأعمدة
        if "Parasite" not in df.columns and "Res" in df.columns:
            df["Parasite"] = df["Res"]
        if "Status" not in df.columns:
            df["Status"] = "Succès"

        # الإحصائيات العامة
        total = len(df)
        successful = df[df["Status"] == "Succès"].shape[0]
        failed = df[df["Status"] == "Échec"].shape[0]
        most_common = df["Parasite"].value_counts().idxmax() if "Parasite" in df.columns and not df["Parasite"].empty else "N/A"

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Analyses", total)
        col2.metric("Analyses Réussies", successful)
        col3.metric("Analyses Échouées", failed)
        col4.metric("Parasite Fréquent", most_common)

        st.markdown("---")
        st.subheader("📈 Statistiques & Filtres")

        # الفلاتر والرسوم
        if "Parasite" in df.columns:
            parasite_filter = st.selectbox(
                "Filtrer par type:",
                options=["Tous"] + df["Parasite"].unique().tolist()
            )
            filtered_df = df if parasite_filter == "Tous" else df[df["Parasite"] == parasite_filter]
            
            st.bar_chart(filtered_df["Parasite"].value_counts())
            st.dataframe(filtered_df, use_container_width=True)
            
            csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Télécharger CSV", csv, "analyses.csv", "text/csv")
    else:
        st.info("Aucune donnée disponible. Commencez un scan pour voir les statistiques.")

# === الصفحة 5: من نحن (About) ===
elif menu == "ℹ️ À Propos":
    st.title("ℹ️ À Propos du Projet")
    
    st.markdown("""
    <div class='medical-card'>
        <h2 style='color:#2E86C1;'>🧬 DM SMART LAB</h2>
        <p><b>Une solution innovante pour le diagnostic parasitologique assisté par intelligence artificielle.</b></p>
        <p>Ce projet exploite la vision par ordinateur pour assister les techniciens de laboratoire dans l'identification rapide des parasites.</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 👨‍🔬 Développeurs
        * Sebbag Mohamed Dhia Eddine (Expert IA & Conception)
        * Ben Sghir Mohamed (Expert Laboratoire & Données)
        
        Niveau: 3ème Année  
        Spécialité: Laboratoire de Santé Publique
        """)
    with c2:
        st.markdown("""
        ### 🏫 Établissement
        Institut National de Formation Supérieure Paramédicale (INFSPM) 📍 Ouargla, Algérie
        
        *Sous la supervision d'experts en parasitologie et technologie.*
        """)
    
    st.markdown("---")
    # تم تغيير الصورة إلى أيقونة مجهر
    st.image("https://cdn-icons-png.flaticon.com/512/931/931628.png", width=150)
    st.caption("Fait avec ❤️ à Ouargla, 2026")




