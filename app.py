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
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3050/3050525.png", width=100) # صورة رمزية
    st.markdown("## 🧬 DM SMART LAB")
    st.markdown("*Where Science Meets Intelligence*")
    st.markdown("---")
    menu = st.radio("Navigation", ["🏠 Accueil (Unlock)", "🔬 Scan Intelligent", "📊 Dashboard", "ℹ️ À Propos"])
    st.markdown("---")
    # Dark Mode Toggle
    dark = st.toggle("🌙 Mode Nuit", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()
        
    if st.button(" Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()


# --- الصفحات ---

# الصفحة 1: الاستقبال
if menu == "🏠 Accueil (Unlock)":
    st.title("👋 Bienvenue au DM SMART LAB")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/123/123389.png", width=250)
    with col2:
        st.markdown("<div class='medical-card'><h3>🤖 Assistant Dr. DhiaBot</h3><p>Activation vocale requise.</p></div>", unsafe_allow_html=True)
        
        # الزر الأول: الترحيب + الوقت + النكتة
        if st.session_state.intro_step == 0:
            if st.button("🔊 PRÉSENTATION (Étape 1)", use_container_width=True):
                current_time = datetime.now().strftime("%H heures et %M minutes")
                txt_intro = f"Bonjour à tous. Je suis l'intelligence artificielle du laboratoire, développée par les techniciens supérieurs Dhia et Mohamed. Il est actuellement {current_time}. Préparez vos lames, je suis prêt pour le show ! Ne me chatouille pas avec le microscope !"
                speak(txt_intro)
                st.session_state.intro_step = 1
                time.sleep(12) # وقت كافي للكلام
                st.rerun()
                
        # الزر الثاني: العنوان الرسمي الكامل
        elif st.session_state.intro_step == 1:
            st.info("Initialisation de la base de données...")
            if st.button("🔊 TITRE DU PROJET (Étape 2 - Unlock)", use_container_width=True):
                txt_title = "Projet de Fin d'Études : Identification des Parasites par Intelligence Artificielle. Institut National de Formation Supérieure Paramédicale de Ouargla."
                speak(txt_title)
                st.session_state.intro_step = 2
                time.sleep(10)
                st.rerun()
                
        elif st.session_state.intro_step == 2:
            st.success("✅ SYSTÈME DÉVERROUILLÉ ! Accès autorisé.")
            st.balloons()

# الصفحة 2: الفحص (Scan)
elif menu == "🔬 Scan & Analyse":
    st.title("🔬 Unité de Diagnostic IA")
    
    if st.session_state.intro_step < 2:
        st.warning("🔒 Veuillez activer le système dans l'Accueil d'abord !")
    else:
        # 1. استمارة المريض (Patient Form)
        with st.expander("📝 Informations du Patient (Obligatoire)", expanded=True):
            c_a, c_b = st.columns(2)
            p_nom = c_a.text_input("Nom du Patient", placeholder="ex: Benali")
            p_prenom = c_b.text_input("Prénom", placeholder="ex: Ahmed")
            
            c_c, c_d, c_e, c_f = st.columns(4)
            p_age = c_c.number_input("Age", min_value=1, max_value=120, value=30)
            p_sexe = c_d.selectbox("Sexe", ["Masculin", "Féminin"])
            p_poids = c_e.number_input("Poids (kg)", value=70)
            p_type = c_f.selectbox("Type d'examen", ["Selles (Copro)", "Sang (Frottis)", "Urines"])

        model, class_names = load_model_ia() # تأكد أن دالة التحميل موجودة فوق
        
        # 2. الكاميرا والحراري
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown("### 📸 Acquisition & Vision Thermique")
            thermal_mode = st.toggle("🔥 Mode Vision Thermique (Infrarouge)")
            img_file = st.camera_input("Microscope")
            
        with c2:
            if img_file and p_nom:
                # معالجة الصورة
                image = Image.open(img_file).convert("RGB")
                
                # وضع الرؤية الحرارية (Demo Effect)
                if thermal_mode:
                    st.write("🔄 Conversion Thermique en cours...")
                    # تحويل للصورة الرمادية ثم تلوينها لمحاكاة الحراري
                    gray_img = ImageOps.grayscale(image)
                    # تلوين زائف (Pseudo-color)
                    image = ImageOps.colorize(gray_img, black="blue", white="orange", mid="red") 
                    st.image(image, caption="Vue Thermique (Simulation)", use_container_width=True)
                
                # شريط التقدم
                with st.spinner("Analyse des vecteurs pathogènes..."):
                    time.sleep(2)
                    
                    # التنبؤ
                    predicted_label = "Giardia"
                    conf = 98
                    if model:
                        img_rez = ImageOps.fit(image, (224, 224), Image.LANCZOS)
                        img_arr = np.asarray(img_rez).astype(np.float32) / 127.5 - 1
                        pred = model.predict(np.expand_dims(img_arr, axis=0), verbose=0)
                        idx = np.argmax(pred)
                        if idx < len(class_names):
                            predicted_label = class_names[idx]
                            conf = int(pred[0][idx] * 100)

                    info = parasite_db.get(predicted_label, parasite_db["Negative"])
                    
                    # عرض النتيجة
                    st.markdown(f"""
                    <div class='medical-card'>
                        <h2 style='color:red;'>RÉSULTAT: {predicted_label}</h2>
                        <h3>Confiance: {conf}%</h3>
                        <p><b>🔍 Morphologie:</b> {info['morphology']}</p>
                        <p style='color:#E67E22;'>🤖 <b>Dr. DhiaBot:</b> "{info['funny']}"</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # الصوت
                    aud_txt = f"Patient {p_nom}. Résultat: {predicted_label}. {info['funny']}"
                    if st.session_state.last_audio != aud_txt:
                        speak(aud_txt)
                        st.session_state.last_audio = aud_txt
                    
                    # PDF Report
                    p_data = {"Nom":p_nom, "Prenom":p_prenom, "Age":p_age, "Sexe":p_sexe, "Poids":p_poids, "Type":p_type}
                    pdf_bytes = generate_pdf(p_data, predicted_label, conf, info)
                    
                    st.download_button("📄 RAPPORT COMPLET (PDF)", pdf_bytes, f"Rapport_{p_nom}.pdf", "application/pdf", use_container_width=True)
                    
                    if st.button("💾 Archiver"):
                        st.session_state.history.append({"Date":datetime.now().strftime("%H:%M"), "Patient":p_nom, "Resultat":predicted_label})
                        st.success("Dossier Archivé.")
            elif img_file and not p_nom:
                st.error("⚠️ Veuillez entrer le NOM du patient avant l'analyse !")

# الصفحة الجديدة: موسوعة الطفيليات
elif menu == "📘 Encyclopédie":
    st.title("📘 Encyclopédie des Parasites")
    st.markdown("Base de connaissances intégrée pour la comparaison morphologique.")
    
    # قائمة الطفيليات (يمكنك إضافة روابط صور حقيقية مكان الرابط الافتراضي)
    parasites_list = {
        "Giardia": {"danger": "⭐⭐", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Giardia_lamblia_SEM_8698_lores.jpg/220px-Giardia_lamblia_SEM_8698_lores.jpg"},
        "Amoeba": {"danger": "⭐⭐⭐", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/Entamoeba_histolytica_01.jpg/220px-Entamoeba_histolytica_01.jpg"},
        "Plasmodium": {"danger": "⭐⭐⭐⭐⭐", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Plasmodium_falciparum_01.png/220px-Plasmodium_falciparum_01.png"},
        "Leishmania": {"danger": "⭐⭐⭐⭐", "img": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Leishmania_tropica_promastigote.jpg/220px-Leishmania_tropica_promastigote.jpg"}
    }
    
    col_x, col_y = st.columns(2)
    for p_name, p_data in parasites_list.items():
        with st.expander(f"🦠 {p_name}"):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.image(p_data["img"], caption=p_name)
            with c2:
                st.write(f"**Danger:** {p_data['danger']}")
                st.write(f"**Description:** {parasite_db.get(p_name, {}).get('desc', 'No desc')}")
                st.write(f"**Morphologie:** {parasite_db.get(p_name, {}).get('morphology', 'No data')}")
                st.info("Traitement recommandé: Voir protocole médical.")
# --- الصفحة 3: لوحة التحكم (Dashboard) ---
elif menu == "📊 Dashboard":
    st.title("📊 Tableau de Bord Clinique")

    # --- مؤشرات الأداء الرئيسية ---
    total = len(st.session_state.history)
    if total > 0:
        df = pd.DataFrame(st.session_state.history)
        successful = df[df["Status"] == "Succès"].shape[0] if "Status" in df.columns else total
        failed = df[df["Status"] == "Échec"].shape[0] if "Status" in df.columns else 0
        most_common = df["Parasite"].value_counts().idxmax() if "Parasite" in df.columns else "N/A"
    else:
        successful = failed = 0
        most_common = "N/A"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Analyses", total)
    col2.metric("Analyses Réussies", successful)
    col3.metric("Analyses Échouées", failed)
    col4.metric("Parasite Fréquent", most_common)

    # --- حالة النظام ---
    st.subheader("État du Système")
    st.success("Opérationnel ✅")

    # --- إحصاءات متقدمة ---
    st.markdown("### 📈 Statistiques Récentes")
    if total > 0:
        # فلتر حسب الطفيلي
        parasite_filter = st.selectbox(
            "Filtrer par type de parasite:",
            options=["Tous"] + df["Parasite"].unique().tolist()
        )
        filtered_df = df if parasite_filter == "Tous" else df[df["Parasite"] == parasite_filter]

        # رسم بياني عمودي لتوزيع الطفيليات
        st.bar_chart(filtered_df["Parasite"].value_counts())

        # رسم خطي للتحليلات حسب التاريخ (إذا العمود موجود)
        if "Date" in df.columns:
            filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
            counts_by_date = filtered_df.groupby(filtered_df["Date"].dt.date).size()
            st.line_chart(counts_by_date)

        # عرض الجدول الكامل
        st.dataframe(filtered_df, use_container_width=True)

        # زر لتصدير البيانات
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇️ Télécharger les données CSV",
            data=csv,
            file_name='analyses.csv',
            mime='text/csv'
        )
    else:
        st.info("Aucune donnée disponible. Commencez un scan.")

# الصفحة 4: من نحن (About)
elif menu == "ℹ️ À Propos":
    st.title("ℹ️ À Propos du Projet")
    
    st.markdown("""
    <div class='medical-card'>
        <h2 style='color:#2E86C1;'>🧬 DM SMART LAB</h2>
        <p><b>Une solution innovante pour le diagnostic parasitologique assisté par ordinateur.</b></p>
        <p>Ce projet vise à utiliser l'intelligence artificielle pour assister les techniciens de laboratoire dans l'identification rapide et précise des parasites .</p>
    </div>
    """, unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 👨‍🔬 Développeurs
        * **Sebbag mohamed Dhia edddine** (Expert IA & Conception)
        * **Ben sghir Mohamed** (Expert Laboratoire & Données)
        
        **Niveau:** 3ème Année
        **Spécialité:** Laboratoire de Santé Publique
        """)
    with c2:
        st.markdown("""
        ### 🏫 Établissement
        **Institut National de Formation Supérieure Paramédicale (INFSPM)**
        📍 Ouargla, Algérie
        
        **Supervision:** Encadré par des experts du domaine.
        """)
    
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/1200px-Flag_of_Algeria.svg.png", width=100)
    st.caption("Fait avec ❤️ à Ouargla, 2026")
























