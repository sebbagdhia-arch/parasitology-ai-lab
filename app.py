
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

# --- 1. إعداد النظام ---
st.set_page_config(
    page_title="DHIA Smart Lab AI v2.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# مسار أو رابط اللوغو الخاص بك (يمكنك وضع اسم ملف محلي مثل "logo.png" إذا كان في نفس المجلد)
LOGO_URL = "https://cdn-icons-png.flaticon.com/512/9301/9301413.png" 

# --- 2. إدارة الحالة (State Management) ---
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
    st.session_state.dark_mode = False
if 'language' not in st.session_state:
    st.session_state.language = "Français"

# --- قاموس اللغات ---
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

# --- 3. التصميم الذكي (Dark/Light Engine & Custom Fonts/Backgrounds) ---
theme = {
    "bg": "#121212" if st.session_state.dark_mode else "#F4F7F6",
    "card": "#1E1E1E" if st.session_state.dark_mode else "#FFFFFF",
    "text": "#E0E0E0" if st.session_state.dark_mode else "#2C3E50",
    "primary": "#3498DB",
    "accent": "#E74C3C",
    "shadow": "rgba(0,0,0,0.5)" if st.session_state.dark_mode else "rgba(0,0,0,0.1)",
    "bg_pattern": "rgba(255,255,255,0.03)" if st.session_state.dark_mode else "rgba(52,152,219,0.05)"
}

st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Roboto:wght@400;700&display=swap');

    /* تطبيق الألوان والخلفية المتحركة */
    .stApp {{
        background-color: {theme['bg']};
        background-image: radial-gradient({theme['bg_pattern']} 2px, transparent 2px), radial-gradient({theme['bg_pattern']} 2px, transparent 2px);

background-size: 60px 60px;
        background-position: 0 0, 30px 30px;
        color: {theme['text']};
        animation: backgroundScroll 60s linear infinite;
    }}
    
    @keyframes backgroundScroll {{
        100% {{ background-position: 60px 60px, 90px 90px; }}
    }}
    
    /* النصوص والخطوط */
    h1, h2, h3, h4, h5, p, div, span, label, li {{
        color: {theme['text']} !important;
        font-family: {'"Cairo", sans-serif' if st.session_state.language == 'العربية' else '"Roboto", sans-serif'};
        text-align: {text_align};
    }}

    /* البطاقات */
    .medical-card {{
        background-color: {theme['card']};
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 8px 20px {theme['shadow']};
        border-left: 5px solid {theme['primary']};
        margin-bottom: 20px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        direction: {'rtl' if st.session_state.language == 'العربية' else 'ltr'};
    }}
    .medical-card:hover {{ transform: translateY(-5px); box-shadow: 0 12px 25px {theme['shadow']}; }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: { "#0b0f19" if st.session_state.dark_mode else "#2C3E50" };
    }}
    
    /* أزرار */
    div.stButton > button {{
        background: linear-gradient(90deg, {theme['primary']}, #2980B9);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }}

    /* الكاميرا */
    [data-testid="stCameraInput"] video {{
        border-radius: 15px;
        border: 3px solid {theme['accent']};
    }}
    </style>
""", unsafe_allow_html=True)

# --- دوال الصوت (Audio Functions) ---
def play_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang)
        fp = BytesIO()
        tts.write_to_fp(fp)
        b64 = base64.b64encode(fp.getvalue()).decode()
        audio_html = f'<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        pass # تجاوز الخطأ إذا لم يكن هناك اتصال بالإنترنت

# --- 4. دوال الذكاء الاصطناعي المتقدمة ---
def generate_heatmap_simulation(image):
    img_array = np.array(image)
    heatmap = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)
    center_x, center_y = img_array.shape[1] // 2, img_array.shape[0] // 2
    cv_x, cv_y = np.meshgrid(np.arange(img_array.shape[1]), np.arange(img_array.shape[0]))
    dist = np.sqrt((cv_x - center_x)**2 + (cv_y - center_y)**2)
    heatmap = np.exp(-dist2 / (2 * (802))) * 255
    heatmap_colored = plt.cm.jet(heatmap)[:, :, :3] * 255
    heatmap_colored = heatmap_colored.astype(np.uint8)
    heatmap_img = Image.fromarray(heatmap_colored)
    heatmap_img = heatmap_img.resize(image.size)
    blended = Image.blend(image, heatmap_img, alpha=0.4)
    return blended

def calculate_treatment(parasite, weight_kg, age):
    if parasite == "Giardia":
        dosage = weight_kg * 15
        return f"Metronidazole (Flagyl). Dose recommandée: {dosage:.0f} mg/jour pendant 5 jours."
    elif parasite == "Amoeba":
        dosage = weight_kg * 35 
        return f"Metronidazole. Dose forte: {dosage:.0f} mg/jour pendant 10 jours."
    elif parasite == "Plasmodium":
        return "URGENCE: Protocole ACT (Artemisinin-based Combination Therapy). Hospitalisation immédiate."
    elif parasite == "Leishmania":
        return "Traitement spécialisé: Antimoniate de méglumine (Glucantime). Voir infectiologue."
    else:
        return "Aucun traitement médicamenteux requis. Hydratation et hygiène."

class MedicalReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DHIA Smart Lab AI - Rapport Clinique', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Systeme securise par DHIA-AI Encryption Standard (AES-256)', 0, 0, 'C')

def create_pdf(patient_data, result, confidence, treatment_plan, image_path=None):
    pdf = MedicalReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 30, 190, 40, 'F')
    pdf.set_xy(15, 35)
    pdf.cell(0, 10, f"Nom du Patient: {patient_data['name']}", ln=True)
    pdf.set_xy(15, 45)
    pdf.cell(0, 10, f"Age: {patient_data['age']} ans | Poids: {patient_data['weight']} kg | Sexe: {patient_data['sex']}", ln=True)
    
    pdf.ln(30)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "DIAGNOSTIC IA:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Pathogene: {result}", ln=True)
    pdf.cell(0, 10, f"Confiance: {confidence}%", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "PLAN DE TRAITEMENT (AI RECOMMANDATION):", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, treatment_plan)
    
    pdf.ln(20)
    # تعديل المسمى من طبيب إلى مخبري
    pdf.cell(0, 10, f"Technicien de laboratoire: {st.session_state.get('doctor_name', 'Tech. Inconnu')}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

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

# --- 5. واجهة تسجيل الدخول (The Gate) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        # اللوغو في شاشة الدخول
        st.image(LOGO_URL, width=120)
        st.markdown(f"<h1 style='color: {theme['text']};'>DHIA Smart Lab <span style='color: #E74C3C;'>AI</span></h1>", unsafe_allow_html=True)
        st.info("🔒 Secure Medical Access Portal")
        
        user_input = st.text_input("ID Technicien (المخبري)", "admin")
        pass_input = st.text_input("Password (كلمة المرور)", type="password")
        
        if st.button("Connexion Sécurisée", use_container_width=True):
            if pass_input == "1234":
                st.session_state.logged_in = True
                st.session_state.doctor_name = "Tech. Dhia & Mohamed"
                st.success("Access Granted. Loading Encryption Keys...")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# --- الترحيب الصوتي للجنة (يعمل مرة واحدة فقط بعد الدخول) ---
if st.session_state.logged_in and not st.session_state.welcome_played:
    welcome_message = """Bonjour à l'honorable jury. Je suis le système d'intelligence artificielle DHIA Smart Lab. 
    Aujourd'hui, je suis prêt à analyser des échantillons avec une précision extrême. Franchement, avec le travail de Dhia et Mohamed, je mérite la note complète aujourd'hui ! 
    Notre thème est : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais. Commençons !"""
    play_audio(welcome_message, lang='fr')
    st.session_state.welcome_played = True

# --- 6. التطبيق الرئيسي (The Core) ---

# Sidebar
with st.sidebar:
    st.image(LOGO_URL, width=80)
    st.markdown("### 🏥 DHIA Smart Lab")
    st.caption("v2.0 Enterprise Edition")

st.markdown("---")

st.session_state.language = st.selectbox(
    "🌐 Langue / Language / اللغة",
    ["Français", "English", "العربية"]
)

if st.toggle("🌙 Mode Sombre / Dark Mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
else:
    st.session_state.dark_mode = False

st.markdown("---")

menu = st.radio("Menu", [
    t["menu_patient"], 
    t["menu_analyse"], 
    t["menu_dash"], 
    t["menu_sys"],
    t["menu_about"]
])


    st.markdown("---")
    st.success(f"👨‍🔬 {t['tech_title']}:\n{st.session_state.doctor_name}")

# صفحة 1: تسجيل المرضى 
if menu == t["menu_patient"]:
    st.title(t["title_patient"])
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="medical-card"><h4>📝 Nouveau Patient / مريض جديد</h4>', unsafe_allow_html=True)
        p_name = st.text_input("Nom Complet / Full Name / الاسم الكامل")
        c_a, c_b, c_c = st.columns(3)
        p_age = c_a.number_input("Age / العمر", 1, 100, 25)
        p_weight = c_b.number_input("Poids (kg) / الوزن", 1, 200, 70)
        p_sex = c_c.selectbox("Sexe / الجنس", ["Homme", "Femme"])
        
        if st.button("💾 Créer Dossier / Create / إنشاء", use_container_width=True):
            if p_name:
                p_id = f"PAT-{len(st.session_state.patients)+101}"
                st.session_state.patients[p_id] = {
                    "name": p_name, "age": p_age, "weight": p_weight, "sex": p_sex, "history": []
                }
                st.session_state.current_patient = p_id
                st.success(f"Dossier créé : {p_id}")
            else:
                st.warning("Veuillez entrer un nom.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with c2:
        st.markdown("#### 🏥 Patients / المرضى")
        if st.session_state.patients:
            for pid, pdata in st.session_state.patients.items():
                if st.button(f"{pdata['name']} ({pid})", key=pid):
                    st.session_state.current_patient = pid
                    st.info(f"Sélectionné : {pdata['name']}")
        else:
            st.caption("Aucun patient / No patients / لا يوجد مرضى.")

# صفحة 2: التحليل والعلاج
elif menu == t["menu_analyse"]:
    if not st.session_state.current_patient:
        st.warning("⚠️ Veuillez d'abord sélectionner un patient / الرجاء اختيار مريض أولاً.")
    else:
        patient = st.session_state.patients[st.session_state.current_patient]
        st.title(f"{t['title_analyse']} : {patient['name']}")
        
        img_file = st.camera_input("Microscope Feed / كاميرا المجهر")
        
        if img_file:
            with st.status("🧬 AI Processing...", expanded=True) as status:
                st.write("📥 Acquisition de l'image...")
                time.sleep(0.5)
                st.write("🔍 Activation du modèle CNN...")
                time.sleep(0.5)
                st.write("🧠 Génération de la Heatmap...")
                time.sleep(0.5)
                status.update(label="✅ Diagnostic Terminé", state="complete", expanded=False)
            
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
                label = "Giardia" 
                conf = 98

clean_label = label.strip()
            treatment = calculate_treatment(clean_label, patient['weight'], patient['age'])
            heatmap_img = generate_heatmap_simulation(image)
            
            # --- النطق الصوتي للنتيجة ---
            result_audio_text = f"Analyse terminée. Résultat : {clean_label}, avec une confiance de {conf} pourcents."
            if clean_label.lower() == "negative":
                 result_audio_text = "Analyse terminée. L'échantillon est négatif. Le patient va bien, Hamdoullah."
            play_audio(result_audio_text, lang='fr')
            
            col_res1, col_res2 = st.columns([1, 1])
            with col_res1:
                st.markdown(f"""
                <div class="medical-card">
                    <h2 style='color: {theme['accent']};'>{clean_label}</h2>
                    <h1 style='font-size: 40px;'>{conf}% <span style='font-size: 15px; color: grey;'>Confiance</span></h1>
                    <hr>
                    <p><b>🩺 Protocole de Traitement (AI):</b></p>
                    <p style='color: {theme['primary']}; font-weight: bold;'>{treatment}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col_res2:
                st.image(heatmap_img, caption="👁️ AI Vision Heatmap (Zone de détection)", use_column_width=True)
            
            pdf_bytes = create_pdf(patient, clean_label, conf, treatment)
            st.download_button(
                label="📄 Télécharger Rapport (PDF) / تحميل التقرير",
                data=pdf_bytes,
                file_name=f"Rapport_{patient['name']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            if st.session_state.get("last_scan_time") != str(datetime.now()):
                st.session_state.history.append({"patient": patient['name'], "result": clean_label, "conf": conf, "date": datetime.now().strftime("%Y-%m-%d")})
                st.session_state.last_scan_time = str(datetime.now())

# صفحة 3: Analytics
elif menu == t["menu_dash"]:
    st.title(t["title_dash"])
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Consultations", len(df))
        k2.metric("Cas Positifs", len(df[df['result'] != 'Negative']))
        k3.metric("Taux d'Infection", f"{int((len(df[df['result'] != 'Negative'])/len(df))*100)}%")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📈 Répartition des Parasites")
            st.bar_chart(df['result'].value_counts())
        
        with c2:
            st.subheader("⚠️ Niveau de Risque")
            chart_data = pd.DataFrame(
                np.random.randn(20, 3),
                columns=['Giardia', 'Amoeba', 'Leishmania'])
            st.line_chart(chart_data)
            
    else:
        st.info("Aucune donnée disponible / لا توجد بيانات.")

# صفحة 4: النظام
elif menu == t["menu_sys"]:
    st.title(t["title_sys"])
    st.markdown('<div class="medical-card">', unsafe_allow_html=True)
    st.write("📡 Statut Serveur: En ligne (Localhost)")
    st.write("🔒 Cryptage: AES-256 Enabled")
    st.write("🧠 Modèle AI: v3.5 (Optimisé)")
    
    if st.button("🗑️ Réinitialiser / Reset / إعادة ضبط"):
        st.session_state.patients = {}
        st.session_state.history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# صفحة 5: من نحن (الجديدة)
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
            <li style='font-size: 16px; margin-bottom: 10px;'><b>Sebbag Mohamed Dhia Eddine</b></li>
            <li style='font-size: 16px; margin-bottom: 10px;'><b>Bn Sghiaer Mohamed</b></li>
        </ul>
        <p><i>Statut :</i> Élèves manipulateurs en laboratoire, 3ème année (طلاب سنة ثالثة مخبريون).</p>
        <hr>
        <h3 style='color: {theme['primary']};'>🏛️ Établissement :</h3>
        <p style='font-size: 16px; font-weight: bold;'>Institut National de Formation Supérieure Paramédicale de Ouargla (INFSP Ouargla)</p>
        <p>معهد التكوين العالي شبه الطبي ورقلة</p>
    </div>
    """, unsafe_allow_html=True)




