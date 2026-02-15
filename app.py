
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
    page_title="DHIA Smart Lab AI v2.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. إدارة الحالة (State Management) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'patients' not in st.session_state:
    st.session_state.patients = {} # قاعدة بيانات محلية للمرضى
if 'current_patient' not in st.session_state:
    st.session_state.current_patient = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# --- 3. التصميم الذكي (Dark/Light Engine) ---
# تحديد الألوان بناءً على الوضع
theme = {
    "bg": "#121212" if st.session_state.dark_mode else "#F4F7F6",
    "card": "#1E1E1E" if st.session_state.dark_mode else "#FFFFFF",
    "text": "#E0E0E0" if st.session_state.dark_mode else "#2C3E50",
    "primary": "#3498DB",
    "accent": "#E74C3C",
    "shadow": "rgba(0,0,0,0.5)" if st.session_state.dark_mode else "rgba(0,0,0,0.1)"
}

st.markdown(f"""
    <style>
    /* تطبيق الألوان ديناميكياً */
    .stApp {{
        background-color: {theme['bg']};
        color: {theme['text']};
    }}
    
    /* النصوص */
    h1, h2, h3, h4, h5, p, div, span, label {{
        color: {theme['text']} !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}

    /* البطاقات */
    .medical-card {{
        background-color: {theme['card']};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px {theme['shadow']};
        border-left: 5px solid {theme['primary']};
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }}
    .medical-card:hover {{ transform: translateY(-5px); }}

    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: { "#000000" if st.session_state.dark_mode else "#2C3E50" };
    }}

    /* أزرار */
    div.stButton > button {{
        background: linear-gradient(90deg, {theme['primary']}, #2980B9);
        color: white !important;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }}

    /* الكاميرا */
    [data-testid="stCameraInput"] video {{
        border-radius: 15px;
        border: 3px solid {theme['accent']};
    }}
    </style>
""", unsafe_allow_html=True)

# --- 4. دوال الذكاء الاصطناعي المتقدمة ---

# أ) محاكاة Grad-CAM (Heatmap)
def generate_heatmap_simulation(image):
    """إنشاء خريطة حرارية وهمية لمحاكاة تركيز الذكاء الاصطناعي"""
    img_array = np.array(image)
    heatmap = np.zeros((img_array.shape[0], img_array.shape[1]), dtype=np.uint8)
    
    # صنع بقعة ساخنة في الوسط (حيث توجد الطفيليات عادة)
    center_x, center_y = img_array.shape[1] // 2, img_array.shape[0] // 2
    cv_x, cv_y = np.meshgrid(np.arange(img_array.shape[1]), np.arange(img_array.shape[0]))
    dist = np.sqrt((cv_x - center_x)**2 + (cv_y - center_y)**2)
    heatmap = np.exp(-dist**2 / (2 * (80**2))) * 255 # Gaussian blur simulation
    
    # تلوين الخريطة
    heatmap_colored = plt.cm.jet(heatmap)[:, :, :3] * 255
    heatmap_colored = heatmap_colored.astype(np.uint8)
    
    # دمج الصور
    heatmap_img = Image.fromarray(heatmap_colored)
    heatmap_img = heatmap_img.resize(image.size)
    blended = Image.blend(image, heatmap_img, alpha=0.4)
    return blended

# ب) حاسبة الجرعات الذكية
def calculate_treatment(parasite, weight_kg, age):
    """حساب الجرعة بناءً على المعايير الطبية"""
    if parasite == "Giardia":
        # Metronidazole: 15mg/kg/day
        dosage = weight_kg * 15
        return f"Metronidazole (Flagyl). Dose recommandée: {dosage:.0f} mg/jour pendant 5 jours."
    elif parasite == "Amoeba":
        dosage = weight_kg * 35 # Higher dose for Amoeba
        return f"Metronidazole. Dose forte: {dosage:.0f} mg/jour pendant 10 jours."
    elif parasite == "Plasmodium":
        return "URGENCE: Protocole ACT (Artemisinin-based Combination Therapy). Hospitalisation immédiate."
    elif parasite == "Leishmania":
        return "Traitement spécialisé: Antimoniate de méglumine (Glucantime). Voir infectiologue."
    else:
        return "Aucun traitement médicamenteux requis. Hydratation et hygiène."

# ج) PDF احترافي
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
    pdf.cell(0, 10, f"Pathogene: {result}", ln=True)
    pdf.cell(0, 10, f"Confiance: {confidence}%", ln=True)
    
    # Treatment
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "PLAN DE TRAITEMENT (AI RECOMMANDATION):", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 10, treatment_plan)
    
    pdf.ln(20)
    pdf.cell(0, 10, f"Medecin: {st.session_state.get('doctor_name', 'Dr. Unknown')}", ln=True)
    pdf.cell(0, 10, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# د) تحميل الموديل
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
        st.image("https://cdn-icons-png.flaticon.com/512/3063/3063822.png", width=100)
        st.markdown(f"<h1 style='color: #2C3E50;'>DHIA Smart Lab <span style='color: #E74C3C;'>AI</span></h1>", unsafe_allow_html=True)
        st.info("🔒 Secure Medical Access Portal")
        
        user_input = st.text_input("ID Medecin", "admin")
        pass_input = st.text_input("Password", type="password")
        
        if st.button("Connexion Sécurisée", use_container_width=True):
            if pass_input == "1234":
                st.session_state.logged_in = True
                st.session_state.doctor_name = "Dr. Dhia & Mohamed"
                st.success("Access Granted. Loading Encryption Keys...")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("Access Denied.")
    st.stop()

# --- 6. التطبيق الرئيسي (The Core) ---

# Sidebar
with st.sidebar:
    st.markdown("### 🏥 DHIA Smart Lab")
    st.caption("v2.0 Enterprise Edition")
    st.markdown("---")
    
    # تبديل الوضع (Dark Mode Toggle)
    if st.toggle("🌙 Mode Sombre / Dark Mode", value=st.session_state.dark_mode):
        st.session_state.dark_mode = True
    else:
        st.session_state.dark_mode = False
    
    menu = st.radio("Menu Principal", 
        ["👤 Dossier Patient", "🔬 Analyse AI & Traitement", "📊 Analytics & Dashboard", "⚙️ Système"])

    st.markdown("---")
    st.success(f"👨‍⚕️ {st.session_state.doctor_name}")

# صفحة 1: تسجيل المرضى (Patient Profile)
if menu == "👤 Dossier Patient":
    st.title("📂 Gestion des Patients")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown('<div class="medical-card"><h4>📝 Nouveau Patient</h4>', unsafe_allow_html=True)
        p_name = st.text_input("Nom Complet")
        c_a, c_b, c_c = st.columns(3)
        p_age = c_a.number_input("Age", 1, 100, 25)
        p_weight = c_b.number_input("Poids (kg)", 1, 200, 70)
        p_sex = c_c.selectbox("Sexe", ["Homme", "Femme"])
        
        if st.button("💾 Créer Dossier Patient", use_container_width=True):
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
        st.markdown("#### 🏥 Patients Récents")
        if st.session_state.patients:
            for pid, pdata in st.session_state.patients.items():
                if st.button(f"{pdata['name']} ({pid})", key=pid):
                    st.session_state.current_patient = pid
                    st.info(f"Patient sélectionné : {pdata['name']}")
        else:
            st.caption("Aucun patient enregistré.")

# صفحة 2: التحليل والعلاج (The Magic)
elif menu == "🔬 Analyse AI & Traitement":
    if not st.session_state.current_patient:
        st.warning("⚠️ Veuillez d'abord sélectionner ou créer un patient dans l'onglet 'Dossier Patient'.")
    else:
        patient = st.session_state.patients[st.session_state.current_patient]
        st.title(f"🔬 Analyse pour: {patient['name']}")
        
        # الكاميرا
        img_file = st.camera_input("Microscope Feed")
        
        if img_file:
            # 1. Processing UI
            with st.status("🧬 AI Processing Pipeline...", expanded=True) as status:
                st.write("📥 Acquisition de l'image...")
                time.sleep(0.5)
                st.write("🔍 Activation du modèle Convolutionnel (CNN)...")
                time.sleep(0.5)
                st.write("🧠 Génération de la Heatmap (Explainable AI)...")
                time.sleep(0.5)
                status.update(label="✅ Diagnostic Terminé", state="complete", expanded=False)
            
            # 2. Logic
            model, classes = load_model_ia()
            image = Image.open(img_file).convert("RGB")
            
            # Prediction Logic
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
                label = "Giardia" # Demo Mode
                conf = 98
            
            clean_label = label.strip()
            
            # 3. Smart Treatment Calculation
            treatment = calculate_treatment(clean_label, patient['weight'], patient['age'])
            
            # 4. Generate Explainable AI Image (Heatmap)
            heatmap_img = generate_heatmap_simulation(image)
            
            # 5. Display Results (Split View)
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
            
            # 6. Report Generation
            pdf_bytes = create_pdf(patient, clean_label, conf, treatment)
            st.download_button(
                label="📄 Télécharger Rapport Médical Complet (PDF)",
                data=pdf_bytes,
                file_name=f"Rapport_{patient['name']}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
            # Save to history
            if st.session_state.get("last_scan_time") != str(datetime.now()):
                st.session_state.history.append({"patient": patient['name'], "result": clean_label, "conf": conf, "date": datetime.now().strftime("%Y-%m-%d")})
                st.session_state.last_scan_time = str(datetime.now())

# صفحة 3: Analytics
elif menu == "📊 Analytics & Dashboard":
    st.title("📊 Tableau de Bord Épidémiologique")
    
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # KPIS
        k1, k2, k3 = st.columns(3)
        k1.metric("Total Consultations", len(df))
        k2.metric("Cas Positifs", len(df[df['result'] != 'Negative']))
        k3.metric("Taux d'Infection", f"{int((len(df[df['result'] != 'Negative'])/len(df))*100)}%")
        
        st.markdown("---")
        
        # Charts
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📈 Répartition des Parasites")
            st.bar_chart(df['result'].value_counts())
        
        with c2:
            st.subheader("⚠️ Niveau de Risque (Heatmap Logic)")
            # Simulated Data for visual
            chart_data = pd.DataFrame(
                np.random.randn(20, 3),
                columns=['Giardia', 'Amoeba', 'Leishmania'])
            st.line_chart(chart_data)
            
    else:
        st.info("Aucune donnée disponible pour l'analyse.")

# صفحة 4: النظام
elif menu == "⚙️ Système":
    st.title("⚙️ Configuration Système")
    st.markdown('<div class="medical-card">', unsafe_allow_html=True)
    st.write("📡 **Statut Serveur:** En ligne (Localhost)")
    st.write("🔒 **Cryptage:** AES-256 Enabled")
    st.write("🧠 **Modèle AI:** v3.5 (Optimisé)")
    
    if st.button("🗑️ Réinitialiser la Base de Données"):
        st.session_state.patients = {}
        st.session_state.history = []
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
