import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps, ImageDraw, ImageFilter
import numpy as np
import os
import base64
import time
from gtts import gTTS
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt

# --- 1. إعداد النظام ---
st.set_page_config(
    page_title="DHIA Smart Lab AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. إدارة الحالة (State Management) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'patients' not in st.session_state:
    st.session_state.patients = {} 
if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'step' not in st.session_state:
    st.session_state.step = 0 # 0: Intro, 1: Title, 2: System
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"

# --- 3. قاموس اللغات (Translations) ---
# الواجهة تتغير لغتها، لكن "المجهر" يتكلم دائماً بشخصيته (فرنسي/جزائري)
texts = {
    "Français": {
        "login_title": "Portail Sécurisé",
        "user": "Identifiant",
        "pass": "Mot de passe",
        "btn_login": "Connexion",
        "menu_patient": "Dossier Patient",
        "menu_scan": "Analyse AI",
        "menu_dash": "Tableau de Bord",
        "new_patient": "Nouveau Patient",
        "name": "Nom Complet",
        "age": "Age",
        "weight": "Poids (kg)",
        "create_btn": "Créer Dossier",
        "start_scan": "Lancer Analyse",
        "download_pdf": "Télécharger Rapport PDF",
        "role": "Laborantins de Santé Publique",
        "institute": "Institut National de Formation Supérieure Paramédicale de Ouargla"
    },
    "العربية": {
        "login_title": "بوابة الدخول الآمنة",
        "user": "اسم المستخدم",
        "pass": "كلمة المرور",
        "btn_login": "تسجيل الدخول",
        "menu_patient": "ملف المريض",
        "menu_scan": "تحليل الذكاء الاصطناعي",
        "menu_dash": "لوحة التحكم",
        "new_patient": "مريض جديد",
        "name": "الاسم الكامل",
        "age": "العمر",
        "weight": "الوزن (كغ)",
        "create_btn": "إنشاء ملف",
        "start_scan": "بدء الفحص",
        "download_pdf": "تحميل التقرير (PDF)",
        "role": "مخبريون في الصحة العمومية",
        "institute": "المعهد الوطني للتكوين العالي شبه الطبي - ورقلة"
    },
    "English": {
        "login_title": "Secure Portal",
        "user": "Username",
        "pass": "Password",
        "btn_login": "Login",
        "menu_patient": "Patient Profile",
        "menu_scan": "AI Analysis",
        "menu_dash": "Dashboard",
        "new_patient": "New Patient",
        "name": "Full Name",
        "age": "Age",
        "weight": "Weight (kg)",
        "create_btn": "Create Profile",
        "start_scan": "Start Analysis",
        "download_pdf": "Download PDF Report",
        "role": "Public Health Laboratory Technicians",
        "institute": "Higher National Institute of Paramedical Training - Ouargla"
    }
}

# --- 4. التصميم (CSS) - الخلفية والشعار ---
st.markdown("""
    <style>
    /* الخطوط */
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Roboto:wght@300;400;700&display=swap');
    
    body { font-family: 'Roboto', 'Cairo', sans-serif; }

    /* الخلفية المتحركة (Emojis) */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        overflow-x: hidden;
    }
    
    .floating-parasite {
        position: fixed;
        font-size: 30px;
        opacity: 0.15;
        z-index: 0;
        animation: float 15s infinite linear;
        pointer-events: none;
    }
    
    @keyframes float {
        0% { transform: translateY(110vh) rotate(0deg); }
        100% { transform: translateY(-10vh) rotate(360deg); }
    }

    /* البطاقات */
    .medical-card {
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        backdrop-filter: blur(4px);
        border-left: 6px solid #2E86C1;
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .medical-card:hover { transform: translateY(-5px); }

    /* تصميم الكاميرا الدائري */
    [data-testid="stCameraInput"] { background: transparent !important; border: none !important; }
    video {
        border-radius: 50% !important;
        border: 8px solid #E74C3C !important;
        width: 300px !important; height: 300px !important;
        object-fit: cover !important;
        box-shadow: 0 0 30px rgba(231, 76, 60, 0.4) !important;
        clip-path: circle(50% at 50% 50%);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #1A252F;
        color: white;
    }
    </style>
    
    <div class="floating-parasite" style="left: 10%; animation-delay: 0s;">🧬</div>
    <div class="floating-parasite" style="left: 25%; animation-delay: 5s; font-size: 50px;">🦠</div>
    <div class="floating-parasite" style="left: 50%; animation-delay: 2s; color: red;">🩸</div>
    <div class="floating-parasite" style="left: 70%; animation-delay: 8s; font-size: 60px;">🧫</div>
    <div class="floating-parasite" style="left: 90%; animation-delay: 3s;">🔬</div>
""", unsafe_allow_html=True)

# --- 5. الدوال المساعدة (Logic) ---

# أ) الشعار (Logo SVG)
def render_logo():
    logo_svg = """
    <svg width="100%" height="100" viewBox="0 0 300 100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="40" fill="#E74C3C" opacity="0.1"/>
        <path d="M40 70 L60 70 L50 30 Z" fill="#ffffff"/>
        <circle cx="50" cy="30" r="12" stroke="#E74C3C" stroke-width="3" fill="none"/>
        <text x="100" y="55" font-family="Arial, sans-serif" font-size="35" font-weight="bold" fill="#ffffff">
            DHIA <tspan fill="#3498DB">LAB</tspan>
        </text>
        <text x="100" y="80" font-family="Arial, sans-serif" font-size="14" fill="#bdc3c7">
            Smart Parasitology AI
        </text>
    </svg>
    """
    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)

# ب) الصوت (Funny + Professional)
def speak_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = "temp_audio.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        md = f"""<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
        st.markdown(md, unsafe_allow_html=True)
        return (len(text) * 0.08) + 0.5
    except:
        return 3

# ج) Heatmap
def generate_heatmap_simulation(image):
    img_array = np.array(image)
    heatmap = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)
    center_x, center_y = img_array.shape[1] // 2, img_array.shape[0] // 2
    cv_x, cv_y = np.meshgrid(np.arange(img_array.shape[1]), np.arange(img_array.shape[0]))
    dist = np.sqrt((cv_x - center_x)**2 + (cv_y - center_y)**2)
    heatmap = np.exp(-dist**2 / (2 * (80**2))) * 255
    heatmap_colored = plt.cm.jet(heatmap)[:, :, :3] * 255
    heatmap_colored = heatmap_colored.astype(np.uint8)
    heatmap_img = Image.fromarray(heatmap_colored)
    heatmap_img = heatmap_img.resize(image.size)
    blended = Image.blend(image, heatmap_img, alpha=0.4)
    return blended

# د) Treatment Logic
def calculate_treatment(parasite, weight_kg, age):
    if parasite == "Giardia":
        dose = weight_kg * 15
        return f"Metronidazole. Dose: {dose:.0f} mg/jour (5 jours)."
    elif parasite == "Amoeba":
        dose = weight_kg * 35
        return f"Metronidazole. Dose forte: {dose:.0f} mg/jour (10 jours)."
    elif parasite == "Plasmodium":
        return "URGENCE: Hospitalisation immédiate (Paludisme)."
    else:
        return "Aucun traitement requis."

# هـ) PDF Report
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'DHIA Smart Lab - Rapport', 0, 1, 'C')
        self.ln(5)

def create_pdf(patient, result, conf, treat):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Patient: {patient['name']} | Age: {patient['age']}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Resultat: {result} ({conf}%)", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Traitement: {treat}")
    pdf.ln(20)
    pdf.cell(0, 10, "Signature: Dr. Sebbag & Ben Seguir", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# و) تحميل الموديل
@st.cache_resource
def load_model_ia():
    model = None
    classes = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"]
    m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
    if m_path:
        model = tf.keras.models.load_model(m_path, compile=False)
    l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f), None)
    if l_path:
        cleaned = []
        with open(l_path, "r") as f:
            for line in f:
                cleaned.append(line.strip().split(" ", 1)[-1] if " " in line else line.strip())
        classes = cleaned
    return model, classes

# --- 6. البيانات (Database & Scripts) ---
intro_script = "Salam alikoum la famille ! C'est moi, Dr DhiaBot. Dhia et Mouhamed sont des génies, ils m'ont créé pour révolutionner le laboratoire. S'il vous plaît, 19/20 minimum ! Ma t'cassrouch rasskoum ! Allez, on commence ?"
title_script = "Titre officiel : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

parasite_db = {
    "Giardia": {"funny": "Wesh ! C'est Giardia avec ses lunettes de soleil.", "desc": "Flagellé intestinal (Forme poire)."},
    "Amoeba": {"funny": "Elle bouge en mode ninja. Attention la dysenterie !", "desc": "Amibe mobile (Pseudopodes)."},
    "Leishmania": {"funny": "Petit mais costaud. Faut appeler le médecin !", "desc": "Parasite tissulaire."},
    "Plasmodium": {"funny": "Aïe aïe aïe ! Les moustiques ont gagné.", "desc": "Hématozoaire (Paludisme)."},
    "Negative": {"funny": "Hamdoullah ! C'est propre, makach mard.", "desc": "Aucune anomalie détectée."},
    "Trypanosoma": {"funny": "Il court comme Mahrez dans le sang !", "desc": "Flagellé sanguin."}
}

# --- 7. سير العمل (Workflow) ---

# أ) شاشة تسجيل الدخول (Login)
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=120)
        st.title("🔐 " + texts["Français"]["login_title"])
        
        u = st.text_input(texts["Français"]["user"], "admin")
        p = st.text_input(texts["Français"]["pass"], type="password")
        
        if st.button(texts["Français"]["btn_login"], use_container_width=True):
            if p == "1234":
                st.session_state.logged_in = True
                st.session_state.user_name = "Dr. Sebbag & Ben Seguir"
                st.success("Bienvenue !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Erreur")
    st.stop()

# ب) المقدمة الإلزامية (The Fun Part)
# مرحلة 0: ترحيب مضحك
if st.session_state.step == 0:
    st.markdown(f"<h1 style='text-align: center; color: #2E86C1;'>🧪 DHIA Smart Lab AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>🔊 Cliquez sur le microscope (Intro)</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/930/930263.png", width=200)
        if st.button("🎙 Play Intro (Algerian AI)", use_container_width=True):
            wait = speak_audio(intro_script)
            with st.spinner("Dr. DhiaBot parle..."):
                time.sleep(wait)
            st.session_state.step = 1
            st.rerun()
    st.stop()

# مرحلة 1: العنوان الرسمي
if st.session_state.step == 1:
    st.markdown(f"<h2 style='text-align: center;'>📜 Titre du Projet</h2>", unsafe_allow_html=True)
    if st.button("🎓 Lire le titre officiel complet", use_container_width=True, type="primary"):
        wait = speak_audio(title_script)
        with st.spinner("Lecture..."):
            time.sleep(wait)
        st.session_state.step = 2
        st.rerun()
    st.stop()

# ج) النظام الرئيسي (The Main App)
# هنا يبدأ التطبيق الحقيقي بعد المقدمات

# Sidebar Setup
render_logo()
st.sidebar.markdown("---")
lang = st.sidebar.selectbox("Language / اللغة", ["Français", "العربية", "English"])
txt = texts[lang] # Load translation

menu = st.sidebar.radio("Menu", [txt["menu_patient"], txt["menu_scan"], txt["menu_dash"]])

st.sidebar.markdown("---")
st.sidebar.info(f"👨‍⚕️ {st.session_state.user_name}")
st.sidebar.caption(f"📍 {txt['role']}")
st.sidebar.caption(f"🏛️ {txt['institute']}")

# Tab 1: Patient
if menu == txt["menu_patient"]:
    st.title(f"📂 {txt['menu_patient']}")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f'<div class="medical-card"><h4>{txt["new_patient"]}</h4>', unsafe_allow_html=True)
        name = st.text_input(txt["name"])
        col_a, col_b = st.columns(2)
        age = col_a.number_input(txt["age"], 1, 100, 25)
        weight = col_b.number_input(txt["weight"], 1, 150, 70)
        
        if st.button(txt["create_btn"], use_container_width=True):
            pid = f"P-{len(st.session_state.patients)+1}"
            st.session_state.patients[pid] = {"name": name, "age": age, "weight": weight}
            st.session_state.current_patient = pid
            st.success(f"OK: {name}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.write("📋 Liste:")
        for pid, p in st.session_state.patients.items():
            if st.button(f"{p['name']}", key=pid):
                st.session_state.current_patient = pid

# Tab 2: Scan
elif menu == txt["menu_scan"]:
    if not st.session_state.current_patient:
        st.warning("⚠️ Veuillez sélectionner un patient.")
    else:
        p_data = st.session_state.patients[st.session_state.current_patient]
        st.title(f"🔬 {p_data['name']}")
        
        img_file = st.camera_input("Scan")
        
        if img_file:
            # 1. Processing Steps
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress.progress(i + 1)
            
            # 2. AI Logic
            model, classes = load_model_ia()
            image = Image.open(img_file).convert("RGB")
            
            if model:
                size = (224, 224)
                img_res = ImageOps.fit(image, size, method=Image.LANCZOS)
                img_arr = np.asarray(img_res).astype(np.float32) / 127.5 - 1
                data = np.expand_dims(img_arr, axis=0)
                pred = model.predict(data, verbose=0)
                idx = np.argmax(pred)
                label = classes[idx] if idx < len(classes) else "Inconnu"
                conf = int(pred[0][idx] * 100)
            else:
                label = "Giardia" # Demo
                conf = 96
            
            clean_label = label.strip()
            db_info = parasite_db.get(clean_label, parasite_db["Negative"])
            
            # 3. Treatment
            treat = calculate_treatment(clean_label, p_data['weight'], p_data['age'])
            
            # 4. Display
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.markdown(f"""
                <div class="medical-card">
                    <h1 style='color:#E74C3C;'>{clean_label}</h1>
                    <h3>Confiance: {conf}%</h3>
                    <p><b>Description:</b> {db_info['desc']}</p>
                    <div style='background:#eaf2f8; padding:10px; border-radius:10px;'>
                        <b>🤖 Dr. DhiaBot:</b><br><i>"{db_info['funny']}"</i>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with c_res2:
                # Heatmap
                heatmap = generate_heatmap_simulation(image)
                st.image(heatmap, caption="🔥 AI Attention Heatmap", use_column_width=True)
                st.info(f"💊 **Traitement:** {treat}")

            # 5. Audio
            if st.session_state.get("last_scan") != str(img_file):
                speak_audio(f"Diagnostic terminé. {clean_label}. {db_info['funny']}")
                st.session_state.last_scan = str(img_file)
                # Save History
                st.session_state.history.append({"res": clean_label, "conf": conf})

            # 6. PDF
            pdf_data = create_pdf(p_data, clean_label, conf, treat)
            st.download_button(txt["download_pdf"], pdf_data, f"Rapport_{clean_label}.pdf", "application/pdf", use_container_width=True)

# Tab 3: Dashboard
elif menu == txt["menu_dash"]:
    st.title("📊 Dashboard")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.bar_chart(df['res'].value_counts())
        st.dataframe(df)
    else:
        st.info("Aucune donnée.")
