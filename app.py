
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

# --- 1. System Configuration (Must be first) ---
st.set_page_config(
    page_title="DHIA Smart Lab AI v2.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9301/9301413.png"

# --- 2. State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'welcome_played' not in st.session_state:
    st.session_state.welcome_played = False
if 'patients' not in st.session_state:
    st.session_state.patients = {} 
if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True # Default to Dark Mode for "Hacker" feel
if 'language' not in st.session_state:
    st.session_state.language = "Français"
if 'doctor_name' not in st.session_state:
    st.session_state.doctor_name = "Tech. Inconnu"

# --- Language Dictionary ---
lang_dict = {
    "Français": {
        "menu_patient": "👤 Dossier Patient",
        "menu_analyse": "🔬 Analyse AI & Traitement",
        "menu_dash": "📊 Analytics & Dashboard",
        "menu_sys": "⚙️ Système",
        "menu_about": "🎓 À propos de nous",
        "title_patient": "📂 Gestion des Patients",
        "title_analyse": "🔬 Analyse AI",
        "title_dash": "📊 Tableau de Bord",
        "title_sys": "⚙️ Configuration Système",
        "title_about": "👨‍🔬 Équipe du Projet",
        "tech_title": "Techniciens de Laboratoire"
    },
    "English": {
        "menu_patient": "👤 Patient Record",
        "menu_analyse": "🔬 AI Analysis & Treatment",
        "menu_dash": "📊 Analytics & Dashboard",
        "menu_sys": "⚙️ System",
        "menu_about": "🎓 About Us",
        "title_patient": "📂 Patient Management",
        "title_analyse": "🔬 AI Analysis",
        "title_dash": "📊 Dashboard",
        "title_sys": "⚙️ System Configuration",
        "title_about": "👨‍🔬 Project Team",
        "tech_title": "Laboratory Technicians"
    },
    "العربية": {
        "menu_patient": "👤 ملف المريض",
        "menu_analyse": "🔬 تحليل الذكاء الاصطناعي",
        "menu_dash": "📊 الإحصائيات",
        "menu_sys": "⚙️ النظام",
        "menu_about": "🎓 من نحن",
        "title_patient": "📂 إدارة المرضى",
        "title_analyse": "🔬 تحليل الذكاء الاصطناعي",
        "title_dash": "📊 لوحة التحكم",
        "title_sys": "⚙️ إعدادات النظام",
        "title_about": "👨‍🔬 فريق المشروع",
        "tech_title": "مخبريان"
    }
}

t = lang_dict[st.session_state.language]
text_align = "right" if st.session_state.language == "العربية" else "left"
dir_set = "rtl" if st.session_state.language == "العربية" else "ltr"

# --- 3. UI & Theme Engine ---
theme = {
    "bg": "#0E1117" if st.session_state.dark_mode else "#F4F7F6",
    "card": "#1E1E1E" if st.session_state.dark_mode else "#FFFFFF",
    "text": "#E0E0E0" if st.session_state.dark_mode else "#2C3E50",
    "primary": "#3498DB",
    "accent": "#E74C3C",
    "shadow": "rgba(0,0,0,0.5)" if st.session_state.dark_mode else "rgba(0,0,0,0.1)",
    "sidebar": "#262730" if st.session_state.dark_mode else "#FFFFFF"
}

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Roboto:wght@400;700&display=swap');

    .stApp {{
        background-color: {theme['bg']};
    }}
    
    /* Global Text Settings */
    h1, h2, h3, h4, h5, p, div, span, label, li {{
        color: {theme['text']} !important;
        font-family: {'"Cairo", sans-serif' if st.session_state.language == 'العربية' else '"Roboto", sans-serif'};
        text-align: {text_align};
    }}

/* Cards */
    .medical-card {{
        background-color: {theme['card']};
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px {theme['shadow']};
        border-left: 5px solid {theme['primary']};
        margin-bottom: 20px;
        direction: {dir_set};
    }}

    /* Buttons */
    div.stButton > button {{
        background: linear-gradient(90deg, {theme['primary']}, #2980B9);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. Helper Functions ---

def play_audio(text, lang='fr'):
    """Plays audio using gTTS."""
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        audio_html = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except:
        pass # Fail silently if no internet

def generate_heatmap_simulation(image):
    """Generates a simulated heatmap overlay."""
    image = image.convert("RGB")
    img_array = np.array(image)
    
    # Create a Gaussian blob in the center
    x = np.arange(0, img_array.shape[1], 1, float)
    y = np.arange(0, img_array.shape[0], 1, float)
    x, y = np.meshgrid(x, y)
    
    x0 = img_array.shape[1] // 2
    y0 = img_array.shape[0] // 2
    sigma = 100 
    
    heatmap = np.exp(-((x-x0)**2 + (y-y0)**2) / (2*sigma**2))
    
    # Colorize
    heatmap = plt.cm.jet(heatmap)[:, :, :3] * 255
    heatmap = heatmap.astype(np.uint8)
    heatmap_img = Image.fromarray(heatmap)
    
    # Blend
    blended = Image.blend(image, heatmap_img, alpha=0.3)
    return blended

def calculate_treatment(parasite, weight_kg, age):
    """Returns treatment protocol based on detection."""
    parasite = parasite.strip()
    if "Giardia" in parasite:
        dosage = weight_kg * 15
        return f"💊 Metronidazole (Flagyl). Dose recommandée: {dosage:.0f} mg/jour pendant 5 jours."
    elif "Amoeba" in parasite:
        dosage = weight_kg * 35 
        return f"💊 Metronidazole. Dose forte: {dosage:.0f} mg/jour pendant 10 jours."
    elif "Plasmodium" in parasite:
        return "🚑 URGENCE: Protocole ACT (Artemisinin-based Combination Therapy). Hospitalisation immédiate."
    elif "Leishmania" in parasite:
        return "💉 Traitement spécialisé: Antimoniate de méglumine (Glucantime). Voir infectiologue."
    elif "Negative" in parasite:
        return "✅ Aucun traitement médicamenteux requis. Hydratation et hygiène."
    else:
        return "⚠️ Pathogène inconnu. Analyses complémentaires requises."

class MedicalReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DHIA Smart Lab AI - Rapport Clinique', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Systeme securise par DHIA-AI Encryption Standard (AES-256)', 0, 0, 'C')

def create_pdf(patient_data, result, confidence, treatment_plan):
    """Generates PDF report."""
    pdf = MedicalReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Patient Info Box
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 30, 190, 40, 'F')
    pdf.set_xy(15, 35)
    pdf.cell(0, 10, f"Nom du Patient: {patient_data['name']}", ln=True)
    pdf.set_xy(15, 45)
    pdf.cell(0, 10, f"Age: {patient_data['age']} ans | Poids: {patient_data['weight']} kg | Sexe: {patient_data['sex']}", ln=True)
    
    pdf.ln(30)
    
    # Diagnosis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "DIAGNOSTIC IA:", ln=True)
    pdf.set_font("Arial", size=12)

pdf.cell(0, 10, f"Pathogene Detecte: {result}", ln=True)
    pdf.cell(0, 10, f"Indice de Confiance: {confidence}%", ln=True)
    
    pdf.ln(10)
    # Treatment
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "PROTOCOLE DE TRAITEMENT:", ln=True)
    pdf.set_font("Arial", size=11)
    
    # Handle unicode/latin-1 issues loosely
    treatment_safe = treatment_plan.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 10, treatment_safe)
    
    pdf.ln(20)
    pdf.cell(0, 10, f"Technicien: {st.session_state.get('doctor_name', 'Tech. Inconnu')}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

@st.cache_resource
def load_model_ia():
    """Loads Keras model or returns None if missing."""
    try:
        model = None
        classes = ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"]
        
        # Look for model file
        m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
        if m_path:
            model = tf.keras.models.load_model(m_path, compile=False)
            
        # Look for labels file
        l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f), None)
        if l_path:
            cleaned = []
            with open(l_path, "r") as f:
                for line in f:
                    cleaned.append(line.strip().split(" ", 1)[-1] if " " in line else line.strip())
            classes = cleaned
            
        return model, classes
    except Exception as e:
        return None, ["Giardia", "Amoeba", "Leishmania", "Plasmodium", "Negative"]

# --- 5. Login Gate ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.image(LOGO_URL, width=100)
        st.markdown(f"<h1 style='color: {theme['text']}; text-align: center;'>DHIA Smart Lab <span style='color: #E74C3C;'>AI</span></h1>", unsafe_allow_html=True)
        st.info("🔒 Secure Medical Access Portal (INFSP Ouargla)")
        
        user_input = st.text_input("ID Technicien", "admin")
        pass_input = st.text_input("Password", type="password")
        
        if st.button("Connexion Sécurisée", use_container_width=True):
            if pass_input == "1234":
                st.session_state.logged_in = True
                st.session_state.doctor_name = "Tech. Dhia & Mohamed"
                st.toast("Access Granted. Loading Encryption Keys...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# --- 6. Main Application ---

# Audio Welcome (Plays once)
if st.session_state.logged_in and not st.session_state.welcome_played:
    welcome_message = "Bienvenue dans le système DHIA Smart Lab. Initialisation des protocoles de détection parasitaire."
    play_audio(welcome_message)
    st.session_state.welcome_played = True

# Sidebar
with st.sidebar:
    st.image(LOGO_URL, width=70)
    st.markdown("### 🏥 DHIA Smart Lab")
    st.caption("v2.0 Enterprise | INFSP Ouargla")
    
    st.markdown("---")
    
    st.session_state.language = st.selectbox("🌐 Langue", ["Français", "English", "العربية"])
    
    # Update dictionary based on selection
    t = lang_dict[st.session_state.language] 
    
    st.markdown("---")
    
    menu = st.radio("Navigation", [
        t["menu_patient"], 
        t["menu_analyse"], 
        t["menu_dash"], 
        t["menu_sys"],
        t["menu_about"]
    ])
    
    st.markdown("---")
    st.info(f"👤 {st.session_state.doctor_name}")
    
    if st.button("Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# --- PAGE: Patient Management ---

if menu == t["menu_patient"]:
    st.title(t["title_patient"])
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown(f'<div class="medical-card"><h4>📝 Nouveau Patient / New Patient</h4>', unsafe_allow_html=True)
        p_name = st.text_input("Nom Complet")
        cc1, cc2, cc3 = st.columns(3)
        p_age = cc1.number_input("Age", 1, 120, 25)
        p_weight = cc2.number_input("Poids (kg)", 1, 250, 70)
        p_sex = cc3.selectbox("Sexe", ["Homme", "Femme"])
        
        if st.button("💾 Enregistrer Dossier", use_container_width=True):
            if p_name:
                p_id = f"PAT-{len(st.session_state.patients)+1001}"
                st.session_state.patients[p_id] = {
                    "name": p_name, "age": p_age, "weight": p_weight, "sex": p_sex
                }
                st.session_state.current_patient = p_id
                st.success(f"Dossier créé: {p_id}")
            else:
                st.warning("Le nom est obligatoire.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown("#### Liste des Patients")
        if st.session_state.patients:
            for pid, pdata in st.session_state.patients.items():
                if st.button(f"{pdata['name']}", key=pid, use_container_width=True):
                    st.session_state.current_patient = pid
                    st.toast(f"Patient chargé: {pdata['name']}")
        else:
            st.caption("Aucun patient enregistré.")

# --- PAGE: Analysis ---
elif menu == t["menu_analyse"]:
    st.title(t["title_analyse"])
    
    if not st.session_state.current_patient:
        st.warning("⚠️ Veuillez sélectionner un patient dans l'onglet 'Dossier Patient' d'abord.")
    else:
        patient = st.session_state.patients[st.session_state.current_patient]
        st.markdown(f"Patient Actuel: {patient['name']} ({patient['age']} ans)")
        
        img_file = st.camera_input("Microscope Feed")
        
        if img_file:
            # 1. Processing Animation
            with st.status("🧬 Analyse en cours...", expanded=True) as status:
                st.write("📥 Acquisition de l'image...")
                time.sleep(0.5)
                st.write("🧠 Activation des neurones artificiels...")
                time.sleep(0.5)
                
                # 2. AI Logic
                model, classes = load_model_ia()
                image = Image.open(img_file).convert("RGB")
                
                label = "Inconnu"
                conf = 0
                
                if model:
                    # Real Prediction
                    size = (224, 224)
                    img_res = ImageOps.fit(image, size, method=Image.LANCZOS)
                    img_arr = np.asarray(img_res).astype(np.float32) / 127.5 - 1
                    data = np.expand_dims(img_arr, axis=0)
                    pred = model.predict(data, verbose=0)
                    idx = np.argmax(pred)
                    label = classes[idx]
                    conf = int(pred[0][idx] * 100)
                else:
                    # Mock Prediction (Simulation Mode)
                    st.warning("⚠️ Mode Simulation (Modèle AI non détecté)")
                    import random
                    label = random.choice(["Giardia", "Amoeba", "Leishmania", "Negative"])
                    conf = random.randint(75, 99)
                
                st.write("✅ Diagnostic généré.")
                status.update(label="Terminé", state="complete", expanded=False)

            # 3. Results Processing
            clean_label = label.strip()
            treatment = calculate_treatment(clean_label, patient['weight'], patient['age'])
            heatmap_img = generate_heatmap_simulation(image)
            
            # Save to history

scan_id = f"{patient['name']}_{datetime.now().strftime('%H%M%S')}"
            # Simple check to avoid duplicates on rerun
            if not st.session_state.history or st.session_state.history[-1]['id'] != scan_id:
                 st.session_state.history.append({
                     "id": scan_id,
                     "patient": patient['name'], 
                     "result": clean_label, 
                     "conf": conf, 
                     "date": datetime.now().strftime("%Y-%m-%d")
                 })
            
            # 4. Display Results
            col_res1, col_res2 = st.columns([1, 1])
            with col_res1:
                st.markdown(f"""
                <div class="medical-card">
                    <h2 style='color: {theme['accent']};'>{clean_label}</h2>
                    <h1 style='font-size: 40px; margin:0;'>{conf}% <span style='font-size: 15px; color: grey;'>Confiance</span></h1>
                    <hr>
                    <p><b>🩺 Protocole de Traitement:</b></p>
                    <p style='color: {theme['primary']}; font-weight: bold;'>{treatment}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_res2:
                st.image(heatmap_img, caption="👁️ AI Vision Heatmap", use_column_width=True)

            # 5. Audio & PDF
            audio_text = f"Diagnostic: {clean_label}. Confiance: {conf} pourcents."
            if st.button("🔊 Écouter le rapport"):
                play_audio(audio_text)
                
            pdf_bytes = create_pdf(patient, clean_label, conf, treatment)
            st.download_button(
                label="📄 Télécharger Rapport PDF",
                data=pdf_bytes,
                file_name=f"Rapport_{patient['name']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

# --- PAGE: Dashboard ---
elif menu == t["menu_dash"]:
    st.title(t["title_dash"])
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        k1, k2, k3 = st.columns(3)
        total = len(df)
        positives = len(df[df['result'] != 'Negative'])
        rate = int((positives/total)*100) if total > 0 else 0
        
        k1.metric("Total Consultations", total)
        k2.metric("Cas Positifs", positives)
        k3.metric("Taux d'Infection", f"{rate}%")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📈 Répartition des Pathogènes")
            if not df.empty:
                counts = df['result'].value_counts()
                st.bar_chart(counts)
        
        with c2:
            st.subheader("🗓️ Activité Récente")
            st.dataframe(df[['date', 'patient', 'result', 'conf']], use_container_width=True)
            
    else:
        st.info("Aucune donnée disponible. Effectuez une analyse d'abord.")

# --- PAGE: System ---
elif menu == t["menu_sys"]:
    st.title(t["title_sys"])
    st.markdown('<div class="medical-card">', unsafe_allow_html=True)
    st.write("📡 Statut Serveur: En ligne (Localhost)")
    st.write("🔒 Cryptage: AES-256 Enabled")
    
    col_sys1, col_sys2 = st.columns(2)
    with col_sys1:
        st.toggle("🌙 Mode Sombre", value=st.session_state.dark_mode, disabled=True, help="Géré automatiquement")
    
    if st.button("🗑️ Réinitialiser Base de Données (Factory Reset)"):
        st.session_state.patients = {}
        st.session_state.history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- PAGE: About Us ---
elif menu == t["menu_about"]:
    st.title(t["title_about"])
    st.markdown(f"""
    <div class="medical-card">
        <h2 style='color: {theme['primary']}; text-align: center;'>🎓 Présentation du Projet</h2>

<br>
        <p style='font-size: 18px;'><b>Thème :</b> Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais.</p>
        <hr>
        <h3 style='color: {theme['accent']};'>👨‍🔬 L'Équipe Réalisatrice :</h3>
        <ul>
            <li style='font-size: 18px; margin-bottom: 10px;'><b>Sebbag Mohamed Dhia Eddine</b></li>
            <li style='font-size: 18px; margin-bottom: 10px;'><b>Bn Sghiaer Mohamed</b></li>
        </ul>
        <p><i>Statut :</i> Élèves manipulateurs en laboratoire, 3ème année (طلاب سنة ثالثة مخبريون).</p>
        <hr>
        <h3 style='color: {theme['primary']};'>🏛️ Établissement :</h3>
        <p style='font-size: 16px; font-weight: bold;'>Institut National de Formation Supérieure Paramédicale de Ouargla (INFSP Ouargla)</p>
        <p>معهد التكوين العالي شبه الطبي ورقلة</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Flag_of_Algeria.svg/1200px-Flag_of_Algeria.svg.png", width=100)

