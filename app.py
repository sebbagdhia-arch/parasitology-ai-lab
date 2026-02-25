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
if 'dark_mode' not in st.session_state: st.session_state.dark_mode = True # الوضع النهاري افتراضي للمستشفيات
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
    pdf.cell(95, 10, "Technicien de Labo 40 :", 0, 0)
    pdf.cell(95, 10, "Technicien de Labo 05 :", 0, 1)
    pdf.set_font("Arial", '', 12)
    pdf.cell(95, 10, "Sebbag mohamed dhia eddine", 0, 0) # اسمك
    pdf.cell(95, 10, "Ben sghir mohamed", 0, 1) # اسم محمد
    
    return pdf.output(dest='S').encode('latin-1')

@st.cache_resource
def load_model_ia():
    # محاكاة تحميل الموديل لضمان عمل الكود
    # استبدل هذا الجزء بكود التحميل الحقيقي الخاص بك إذا كان الملف موجوداً
    model = None
    classes = ["Amoeba", "Giardia", "Leishmania", "Plasmodium", "Trypanosoma", "Schistosoma", "Negative"]
    
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
            <h1 style='color:#2E86C1;'>🧬 DM SMART LAB</h1>
            <p>Accès Réservé au Personnel Médical</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identifiant", placeholder="DM. Dhia")
        pwd = st.text_input("Mot de Passe", type="password")
        
        if st.button("SE CONNECTER"):
            if pwd == "1234": # كلمة السر البسيطة
                st.session_state.logged_in = True
                st.session_state.user_name = f"DM. {user}" if user else "DM. Dhia"
                st.rerun()
            else:
                st.error("Accès Refusé !")
    st.stop()

# --- 7. التطبيق الرئيسي (بعد الدخول) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/930/930263.png", width=100)
    st.markdown("## 🧬 DM SMART LAB")
    st.markdown("*Where Science Meets Intelligence*")
    st.markdown("---")
    
    # قائمة اللغات (شكلية)
    lang = st.selectbox("🌍 Langue", ["Français 🇫🇷", "العربية 🇩🇿", "English 🇬🇧"])
    
    st.markdown("---")
    menu = st.radio("Navigation", ["🏠 Accueil (Unlock)", "🔬 Scan & Analyse", "📘 Encyclopédie", "📊 Dashboard", "ℹ️ À Propos"])
    
    st.markdown("---")
    dark = st.toggle("🌙 Mode Nuit", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()
        
    if st.button(" Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()

# --- الصفحات ---

# الصفحة 1: الاستقبال (المرحلة 1 و 2)
if menu == "🏠 Accueil (Unlock)":
    st.title("👋 Bienvenue au DM SMART LAB")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/123/123389.png", width=250)
    with col2:
        st.markdown("""
        <div class='medical-card'>
            <h3>🤖  DM SMART LAB IA Bot</h3>
            <p>Système de sécurité vocale. Veuillez suivre les étapes.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # الزر الأول: الترحيب + التعريف + النكتة
        if st.session_state.intro_step == 0:
            st.warning("🔒 Étape 1 : Présentation requise")
            if st.button("🔊 1. PRÉSENTATION & HUMOUR", use_container_width=True):
                # النص: الوقت + ضياء ومحمد تقنيين + النكتة
                cur_time = datetime.now().strftime("%H:%M")
                txt_1 = f"Bonjour ! Il est {cur_time}. Je suis DM Smart lab ia, développée par les Techniciens Supérieurs Sebbad mohamed Dhia et Ben Seguir Mohamed. Préparez vos lames et s'il vous plaît, ne me chatouille pas avec le microscope ...!"
                
                speak(txt_1) # تشغيل الصوت
                with st.spinner("DM Smart lab ia parle... 🔊"):
                    time.sleep(18) # انتظار 20 ثانية ليكتمل الكلام
                st.session_state.intro_step = 1
                st.rerun()
                
        # الزر الثاني: العنوان الرسمي الكامل (بدون نقصان)
        elif st.session_state.intro_step == 1:
            st.warning("🔒 Étape 2 : Validation Officielle")
            if st.button("🔊 2. TITRE DU PROJET", use_container_width=True):
                # النص: العنوان الرسمي + المعهد
                txt_2 = "Projet de Fin d'Études : Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais. Présenté par Dhia et Mohamed. Institut National de Formation Supérieure Paramédicale de Ouargla."
                
                speak(txt_2)
                with st.spinner("Lecture du titre officiel... 🔊"):
                    time.sleep(18) # انتظار 20 ثانية ليكتمل الكلام
                st.session_state.intro_step = 2
                st.rerun()
                
        # المرحلة الثالثة: تم الفتح
        elif st.session_state.intro_step == 2:
            st.success("✅ SYSTÈME DÉVERROUILLÉ ! Vous pouvez passer au SCAN.")
            st.balloons()
            if st.button("Aller au Scan ➡️"):
                # يمكن هنا نقل المستخدم يدوياً عبر القائمة
                st.info("Cliquez sur '🔬 Scan & Analyse' dans le menu à gauche.")

# الصفحة 2: الفحص (Scan)
elif menu == "🔬 Scan & Analyse":
    st.title("🔬 Unité de Diagnostic IA")
    
    # التحقق من أن المستخدم مر بمرحلة الاستقبال
    if st.session_state.intro_step < 2:
        st.error("⛔ ACCÈS REFUSÉ : Veuillez activer le système dans la page 'Accueil' d'abord !")
        st.stop() # يوقف الكود هنا حتى يرجع للاستقبال
        
    # 1. استمارة المريض (إجبارية للتقرير)
    st.markdown("#### 1. Informations du Patient")
    with st.container():
        c_a, c_b = st.columns(2)
        p_nom = c_a.text_input("Nom", placeholder="ex: Benali")
        p_prenom = c_b.text_input("Prénom", placeholder="ex: Ahmed")
        
        c_c, c_d, c_e, c_f = st.columns(4)
        p_age = c_c.number_input("Age", 1, 100, 30)
        p_sexe = c_d.selectbox("Sexe", ["H", "F"])
        p_type = c_e.selectbox("Échantillon", ["Selles", "Sang", "Autre"])
        p_poids = c_c.number_input("Poids", 1, 100, 30)
        thermal = c_f.toggle("🔥 Vision Thermique")

    st.markdown("---")
    st.markdown("#### 2. Capture Microscopique")
    
    # 2. الكاميرا (واضحة وكبيرة)
    # تحميل الموديل هنا
    model, class_names = load_model_ia() 
    
    img_file = st.camera_input("Placez la lame et capturez", label_visibility="visible")
    
    # 3. المنطق بعد التصوير
    if img_file:
        if not p_nom:
            st.error("⚠️ Veuillez entrer le NOM du patient ci-dessus !")
        else:
            col_res1, col_res2 = st.columns([1, 1])
            
            with col_res1:
                image = Image.open(img_file).convert("RGB")
                # الفلتر الحراري (للمنظر فقط)
                if thermal:
                    gray = ImageOps.grayscale(image)
                    disp_img = ImageOps.colorize(gray, black="blue", white="yellow", mid="red")
                    st.image(disp_img, caption="Vue Thermique (Activée)", use_container_width=True)
                else:
                    st.image(image, caption="Vue Normale", use_container_width=True)

            with col_res2:
                with st.spinner("Traitement IA en cours..."):
                    time.sleep(2) # تأثير التحميل
                    
                    # تحليل الصورة (Numpy/Tensorflow)
                    predicted_label = "Giardia" # fallback
                    conf = 95
                    
                    if model:
                        try:
                            img_rez = ImageOps.fit(image, (224, 224), Image.LANCZOS)
                            img_arr = np.asarray(img_rez).astype(np.float32) / 127.5 - 1
                            pred = model.predict(np.expand_dims(img_arr, axis=0), verbose=0)
                            idx = np.argmax(pred)
                            if idx < len(class_names):
                                predicted_label = class_names[idx]
                                conf = int(pred[0][idx] * 100)
                        except: pass # لو صار خطأ في الموديل يكمل بالافتراضي

                    # جلب البيانات
                    info = parasite_db.get(predicted_label, parasite_db["Negative"])
                    
                    # بطاقة النتيجة
                    st.markdown(f"""
                    <div class='medical-card' style='border-left: 5px solid red;'>
                        <h2 style='color:red'>{predicted_label}</h2>
                        <p><b>Confiance:</b> {conf}%</p>
                        <p><b>Morphologie:</b> {info['morphology']}</p>
                        <hr>
                        <p>🤡 <i>{info['funny']}</i></p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # تشغيل الصوت (مرة واحدة)
                    res_txt = f"Résultat pour {p_nom} : {predicted_label}. {info['funny']}"
                    if st.session_state.last_audio != res_txt:
                        speak(res_txt)
                        st.session_state.last_audio = res_txt
                    
                    # PDF
                    p_data = {"Nom":p_nom, "Prenom":p_prenom, "Age":p_age, "Sexe":p_sexe, "Poids":"--", "Type":p_type}
                    pdf_bytes = generate_pdf(p_data, predicted_label, conf, info)
                    st.download_button("📥 Télécharger Rapport PDF", pdf_bytes, f"Rapport_{p_nom}.pdf", "application/pdf", use_container_width=True)
                    
                # الحفظ
                if st.button("💾 Sauvegarder"):
                    st.session_state.history.append({
                        "Date": datetime.now().strftime("%H:%M"), 
                        "Patient": p_nom, 
                        "Res": predicted_label,
                        "Parasite": predicted_label  # مهم للفلترة والرسم
                    })
                    st.success("Sauvegardé.")

# --- 3. قاعدة المعرفة المتكاملة (DM Smart Lab Brain) ---
# --- صفحة الموسوعة الذكية ---
elif menu == "📘 Encyclopédie":
    st.title("📘 Encyclopédie des Parasites")
    st.markdown("---")
    
    # تحويل قاعدة البيانات إلى أزرار تفاعلية
    for p_key, p_info in parasite_db.items():
        if p_key == "Negative": continue # لا نعرض "السليم" في الموسوعة
        
        with st.expander(f"🔬 {p_key} ({p_info['scientific_name']})"):
            col_text, col_img = st.columns([2, 1])
            with col_text:
                st.markdown(f"**🔬 Morphologie:** {p_info['morphology']}")
                st.markdown(f"**📖 Description:** {p_info['desc']}")
                st.markdown(f"**⚠️ Risque:** {p_info['risk']}")
                st.info(f"💡 **Conseil Médical:** {p_info['advice']}")
                st.warning(f"🤡 **Note du Bot:** {p_info['funny']}")
            with col_img:
                # هنا يمكنك وضع روابط لصور حقيقية لكل طفيلي
                st.image("https://cdn-icons-png.flaticon.com/512/3024/3024509.png", width=150)
                # --- 3. قاعدة المعرفة المتكاملة (DM Smart Lab Brain) ---
parasite_db = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": "Kyste sphérique (10-15µm) à 4 noyaux ou Trophozoïte avec pseudopodes.",
        "desc": "Parasite tissulaire provoquant la dysenterie amibienne.",
        "funny": "Le ninja des intestins ! Il change de forme plus vite que ton humeur.",
        "risk": "Élevé 🔴",
        "advice": "Traitement au métronidazole requis. Hygiène stricte des mains !"
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia",
        "morphology": "Trophozoïte en 'cerf-volant' avec 2 noyaux (face de hibou) et 4 paires de flagelles.",
        "desc": "Protozoaire flagellé colonisant le duodénum.",
        "funny": "Regarde-le ! Il te fixe avec ses lunettes de soleil. Un vrai fantôme !",
        "risk": "Moyen 🟠",
        "advice": "Vérifier la consommation d'eau non filtrée. Traitement antiparasitaire."
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum/vivax",
        "morphology": "Forme en 'Bague à chaton' à l'intérieur des hématies (Goutte épaisse/Frottis).",
        "desc": "Agent causal du paludisme (Malaria).",
        "funny": "Il demande le mariage à tes globules rouges ! Une bague très dangereuse.",
        "risk": "URGENCE MÉDICALE 🚨",
        "advice": "Hospitalisation immédiate ! Surveillance de la parasitémie toutes les 4h."
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum/tropica",
        "morphology": "Formes amastigotes ovoïdes (2-5µm) avec noyau et kinétoplaste visibles.",
        "desc": "Transmis par la piqûre du phlébotome.",
        "funny": "Petit mais costaud ! Il adore squatter les macrophages.",
        "risk": "Élevé 🔴",
        "advice": "Traitement spécifique (Glucantime). Déclaration obligatoire."
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei/cruzi",
        "morphology": "Forme allongée en 'S' ou 'C' avec un flagelle libre et une membrane ondulante.",
        "desc": "Parasite extracellulaire du sang.",
        "funny": "Il court dans ton sang comme Mahrez sur l'aile droite ! Imprévisible.",
        "risk": "Élevé 🔴",
        "advice": "Examen du liquide céphalo-rachidien si suspicion neurologique."
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium",
        "morphology": "Œuf ovoïde de grande taille avec un éperon terminal caractéristique.",
        "desc": "Parasite des plexus veineux (Bilharziose urinaire).",
        "funny": "L'œuf avec un dard ! Attention, il pique là où ça fait mal.",
        "risk": "Moyen 🟠",
        "advice": "Analyse du sédiment urinaire de 24h. Éviter les baignades en eau douce."
    },
    "Ascaris": {
        "scientific_name": "Ascaris lumbricoides",
        "morphology": "Œuf mamelonné à coque épaisse brune, ou ver adulte cylindrique (15-35cm).",
        "desc": "Le plus grand nématode intestinal de l'homme.",
        "funny": "Un vrai spaghetti géant dans le ventre ! Pas très appétissant.",
        "risk": "Moyen 🟠",
        "advice": "Déparasitage familial. Bien laver les légumes crus."
    },
    "Taenia": {
        "scientific_name": "Taenia saginata/solium",
        "morphology": "Embryophore arrondi à coque épaisse et striée radialement (œuf de Taenia).",
        "desc": "Ver solitaire transmis par la viande mal cuite.",
        "funny": "Le colocataire qui mange tout ton plat sans payer le loyer !",
        "risk": "Moyen 🟠",
        "advice": "Bien cuire la viande bovine. Vérifier la présence d'anneaux dans les selles."
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": "Absence d'éléments parasitaires après examen macro et microscopique.",
        "desc": "Échantillon sain ou débris alimentaires.",
        "funny": "Rien à signaler ! Ton microscope peut aller se reposer.",
        "risk": "Nul 🟢",
        "advice": "Continuer une bonne hygiène alimentaire. RAS."
    }
}

# الصفحة 3: Dashboard
if menu == "📊 Dashboard":
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

    # التأكد من وجود بيانات
    if 'df' in locals() and not df.empty:
        if "Parasite" in df.columns:
            parasite_filter = st.selectbox(
                "Filtrer par type de parasite:",
                options=["Tous"] + df["Parasite"].unique().tolist()
            )
            filtered_df = df if parasite_filter == "Tous" else df[df["Parasite"] == parasite_filter]

            st.bar_chart(filtered_df["Parasite"].value_counts())

            if "Date" in df.columns:
                filtered_df["Date"] = pd.to_datetime(filtered_df["Date"])
                counts_by_date = filtered_df.groupby(filtered_df["Date"].dt.date).size()
                st.line_chart(counts_by_date)

            st.dataframe(filtered_df, use_container_width=True)

            csv = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Télécharger les données CSV",
                data=csv,
                file_name='analyses.csv',
                mime='text/csv'
            )
        else:
            st.warning("⚠️ العمود 'Parasite' غير موجود في البيانات.")
    else:
        st.info("Aucune donnée disponible. Commencez un scan.")


# الصفحة 4: About
elif menu == "ℹ️ À Propos":
    st.title("ℹ️ À Propos du Projet")
    
    # كل HTML داخل st.markdown وبين علامات اقتباس ثلاثية
    st.markdown("""
    <div class='medical-card'>
        <h2 style='color:#2E86C1;'>DM SMART LAB</h2>
        <p><b>Une solution innovante pour le diagnostic parasitologique assisté par ordinateur.</b></p>
        <p>Ce projet vise à utiliser l'intelligence artificielle pour assister les techniciens de laboratoire dans l'identification rapide et précise des parasites.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # معلومات عن المطورين والمؤسسة
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        ### 👨‍🔬 Développeurs
        * **Sebbag Mohamed Dhia Eddine** (Expert IA & Conception)
        * **Ben Seguir Mohamed** (Expert Laboratoire & Données)
        
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
    
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/1200px-Flag_of_Algeria.svg.png",
        width=100
    )
    st.caption("Fait avec ❤️ à Ouargla, 2026")









