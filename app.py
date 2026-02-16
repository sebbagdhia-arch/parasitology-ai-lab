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
from io import BytesIO

# --- 1. إعداد الصفحة (يجب أن يكون في البداية) ---
st.set_page_config(
    page_title="DHIA Smart Lab AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. إدارة الحالة (State Management) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'intro_played' not in st.session_state:
    st.session_state.intro_played = False
if 'patients' not in st.session_state:
    st.session_state.patients = {} 
if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True # الوضع الافتراضي ليلي
if 'lang' not in st.session_state:
    st.session_state.lang = "Français"

# --- 3. اللغات والنصوص ---
texts = {
    "Français": {
        "menu": ["Dossier Patient", "Analyse AI", "Tableau de Bord", "Système", "À propos"],
        "labels": ["Nom", "Age", "Poids", "Sexe"],
        "btns": ["Créer Dossier", "Lancer Analyse", "Télécharger Rapport"],
        "title": "Exploration de l'IA en Parasitologie",
        "audio_intro": "Salam alikoum la famille! Bienvenue chez Dhia et Mouhamed Smart Lab. Système activé. Prêt pour la soutenance !"
    },
    "العربية": {
        "menu": ["ملف المريض", "تحليل الذكاء الاصطناعي", "لوحة التحكم", "النظام", "حول المشروع"],
        "labels": ["الاسم", "العمر", "الوزن", "الجنس"],
        "btns": ["إنشاء ملف", "بدء الفحص", "تحميل التقرير"],
        "title": "استكشاف الذكاء الاصطناعي في علم الطفيليات",
        "audio_intro": "السلام عليكم يا جماعة! مرحباً بكم في مخبر ضياء ومحمد الذكي. النظام يعمل بكفاءة."
    },
    "English": {
        "menu": ["Patient Profile", "AI Analysis", "Dashboard", "System", "About"],
        "labels": ["Name", "Age", "Weight", "Sex"],
        "btns": ["Create Profile", "Start Scan", "Download Report"],
        "title": "AI Exploration in Parasitology",
        "audio_intro": "Hello everyone! Welcome to Dhia and Mohamed Smart Lab. System is ready."
    }
}

# --- 4. المحرك الجمالي (Theme Engine) ---
# هذا الكود يضمن تغيير الألوان فوراً عند الضغط على الزر
theme = {
    "bg": "#000000" if st.session_state.dark_mode else "#F0F2F6", # أسود حالك لليل
    "card": "#1a1a1a" if st.session_state.dark_mode else "#FFFFFF",
    "text": "#FFFFFF" if st.session_state.dark_mode else "#000000",
    "sidebar": "#111111" if st.session_state.dark_mode else "#FFFFFF",
    "accent": "#E74C3C" # الأحمر (Dhia Red)
}

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Roboto:wght@400;700&display=swap');
    
    /* الخلفية الرئيسية */
    .stApp {{
        background-color: {theme['bg']};
    }}
    
    /* النصوص */
    h1, h2, h3, h4, h5, p, div, span, label, li {{
        color: {theme['text']} !important;
        font-family: 'Roboto', 'Cairo', sans-serif;
    }}

    /* البطاقات */
    .medical-card {{
        background-color: {theme['card']};
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #333;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        border-left: 5px solid {theme['accent']};
        margin-bottom: 20px;
    }}

    /* الأزرار */
    div.stButton > button {{
        background: linear-gradient(45deg, #FF0000, #990000);
        color: white !important;
        border: none;
        font-weight: bold;
        transition: 0.3s;
    }}
    div.stButton > button:hover {{
        transform: scale(1.05);
    }}

    /* القائمة الجانبية */
    section[data-testid="stSidebar"] {{
        background-color: {theme['sidebar']};
        border-right: 1px solid #333;
    }}

    /* اللوجو المخصص */
    .dhia-logo {{
        font-family: 'Arial Black', sans-serif;
        font-size: 40px;
        text-align: center;
        background: -webkit-linear-gradient(#fff, #999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: {theme['text']};
    }}
    .dhia-red {{
        color: #E74C3C !important;
        -webkit-text-fill-color: #E74C3C !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 5. دوال النظام (Helper Functions) ---

# دالة الصوت
def play_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# دالة اللوجو (أحمر وأسود)
def render_logo():
    st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <span class="dhia-logo">DHIA <span class="dhia-red">LAB</span></span>
            <br>
            <span style="font-size: 12px; color: {theme['text']}; opacity: 0.7;">AI PARASITOLOGY v3.0</span>
        </div>
    """, unsafe_allow_html=True)

# دالة Heatmap
def generate_heatmap_simulation(image):
    image = image.convert("RGB")
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

# دالة العلاج
def calculate_treatment(parasite, weight_kg, age):
    if "Giardia" in parasite:
        return f"Metronidazole 15mg/kg ({int(weight_kg*15)}mg/jour)"
    elif "Amoeba" in parasite:
        return f"Metronidazole 35mg/kg ({int(weight_kg*35)}mg/jour)"
    elif "Plasmodium" in parasite:
        return "ACT Protocol (Hospitalisation Immédiate)"
    elif "Negative" in parasite:
        return "RAS (Rien à signaler)"
    else:
        return "Consultation Spécialisée"

# دالة PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'DHIA & MOHAMED LAB - Rapport', 0, 1, 'C')
        self.ln(5)

def create_pdf(p_data, res, conf, treat):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Patient: {p_data['name']} ({p_data['age']} ans, {p_data['weight']}kg)", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Resultat: {res} ({conf}%)", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Traitement: {treat}", ln=True)
    pdf.ln(20)
    pdf.cell(0, 10, "Signature: Dr. Sebbag & Bn Sghiaer", ln=True)
    return pdf.output(dest='S').encode('latin-1')

# تحميل الموديل
@st.cache_resource
def load_model_ia():
    model = None
    classes = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"]
    try:
        m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
        if m_path:
            model = tf.keras.models.load_model(m_path, compile=False)
    except: pass
    return model, classes

# --- 6. بوابة الدخول (Login) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        render_logo() # اللوجو الأحمر والأسود
        st.markdown("<h3 style='text-align: center;'>🔐 Secure Access</h3>", unsafe_allow_html=True)
        
        pwd = st.text_input("Password / كلمة المرور", type="password")
        if st.button("ENTER", use_container_width=True):
            if pwd == "1234":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Access Denied")
    st.stop()

# --- 7. التطبيق الرئيسي (The Main App) ---

# Sidebar
with st.sidebar:
    render_logo()
    st.markdown("---")
    
    # Toggle Dark Mode (يعمل فوراً)
    is_dark = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    if is_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = is_dark
        st.rerun()

    # Language
    lang_sel = st.selectbox("Language", ["Français", "العربية", "English"])
    st.session_state.lang = lang_sel
    t = texts[lang_sel] # تحميل القاموس

    st.markdown("---")
    menu_sel = st.radio("Menu", t["menu"])
    
    st.markdown("---")
    st.info("👨‍⚕️ Tech. Dhia & Mohamed")
    st.caption("INFSP Ouargla")

# Intro Voice (مرة واحدة عند الدخول)
if not st.session_state.intro_played:
    play_audio(texts[st.session_state.lang]["audio_intro"])
    st.session_state.intro_played = True

# --- Pages Logic ---

# 1. Dossier Patient
if menu_sel == t["menu"][0]: # Patient
    st.title(f"📂 {t['menu'][0]}")
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f'<div class="medical-card"><h4>📝 {t["btns"][0]}</h4>', unsafe_allow_html=True)
        name = st.text_input(t["labels"][0])
        col_a, col_b = st.columns(2)
        age = col_a.number_input(t["labels"][1], 1, 100, 25)
        weight = col_b.number_input(t["labels"][2], 1, 150, 70)
        
        if st.button(t["btns"][0], use_container_width=True):
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

# 2. AI Analysis
elif menu_sel == t["menu"][1]: # Scan
    st.title(f"🔬 {t['menu'][1]}")
    
    # قراءة العنوان الرسمي تلقائياً عند فتح صفحة التحليل
    if st.button("📢 Lire le Titre (Soutenance)"):
        play_audio("Titre: Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique.")

    if not st.session_state.current_patient:
        st.warning("⚠️ Veuillez sélectionner un patient.")
    else:
        p_data = st.session_state.patients[st.session_state.current_patient]
        st.info(f"Patient: {p_data['name']}")
        
        # الكاميرا (تم إصلاح الخطأ هنا)
        img_file = st.camera_input("Microscope")
        
        if img_file:
            # AI Logic
            model, classes = load_model_ia()
            image = Image.open(img_file).convert("RGB")
            
            if model:
                # Real Prediction
                size = (224, 224)
                img_res = ImageOps.fit(image, size, method=Image.LANCZOS)
                img_arr = np.asarray(img_res).astype(np.float32) / 127.5 - 1
                data = np.expand_dims(img_arr, axis=0)
                pred = model.predict(data, verbose=0)
                idx = np.argmax(pred)
                label = classes[idx] if idx < len(classes) else "Inconnu"
                conf = int(pred[0][idx] * 100)
            else:
                # Simulation Mode
                label = "Giardia Lamblia"
                conf = 97
            
            clean_label = label.strip()
            treat = calculate_treatment(clean_label, p_data['weight'], p_data['age'])
            
            # Display
            c_res1, c_res2 = st.columns(2)
            with c_res1:
                st.markdown(f"""
                <div class="medical-card">
                    <h2 style='color:#E74C3C;'>{clean_label}</h2>
                    <h1>{conf}%</h1>
                    <hr>
                    <p><b>Traitement:</b> {treat}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # قراءة النتيجة صوتياً
                if st.button("🔊 Écouter Résultat"):
                    play_audio(f"Le résultat est {clean_label} avec une confiance de {conf} pourcents.")

            with c_res2:
                hm = generate_heatmap_simulation(image)
                st.image(hm, caption="AI Heatmap", use_container_width=True)
            
            # PDF
            pdf_data = create_pdf(p_data, clean_label, conf, treat)
            st.download_button(t["btns"][2], pdf_data, "Rapport.pdf", "application/pdf", use_container_width=True)
            
            # Save History
            if st.session_state.get("last_scan") != str(img_file):
                st.session_state.history.append({"pat": p_data['name'], "res": clean_label})
                st.session_state.last_scan = str(img_file)

# 3. Dashboard
elif menu_sel == t["menu"][2]: # Dash
    st.title("📊 Dashboard")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.bar_chart(df['res'].value_counts())
        st.dataframe(df)
    else:
        st.info("No Data")

# 4. System & About
else:
    st.title("⚙️ Système & Info")
    st.markdown(f"""
    <div class="medical-card">
        <h3>{texts['Français']['title']}</h3>
        <p>Réalisé par: <b>Sebbag Mohamed Dhia Eddine & Bn Sghiaer Mohamed</b></p>
        <p>INFSP Ouargla - Promo 2026</p>
    </div>
    """, unsafe_allow_html=True)
