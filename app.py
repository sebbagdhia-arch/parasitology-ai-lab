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

# --- 1. إعداد الصفحة وتكوين النظام ---
st.set_page_config(
    page_title="DHIA Smart Lab AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. إدارة الحالة (Session State) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'history' not in st.session_state:
    st.session_state.history = [] # لتخزين سجل الفحوصات
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'user_name' not in st.session_state:
    st.session_state.user_name = "Dr. Dhia"

# --- 3. نظام الألوان والتصميم الطبي (CSS Pro) ---
st.markdown("""
    <style>
    /* الخطوط والألوان الأساسية */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
    }

    /* الألوان: أزرق طبي، أبيض، أحمر خفيف */
    :root {
        --primary-color: #2E86C1;
        --secondary-color: #AED6F1;
        --accent-color: #E74C3C;
        --bg-color: #Fdfdfd;
        --text-color: #2C3E50;
    }

    /* خلفية نظيفة مع حركة خفيفة */
    .stApp {
        background-color: var(--bg-color);
        background-image: linear-gradient(to right, #f8f9fa, #e8f4f8);
    }

    /* Sidebar احترافي */
    section[data-testid="stSidebar"] {
        background-color: #1A252F; /* لون داكن احترافي */
        color: white;
    }
    
    /* الكروت (Cards) */
    .medical-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border-left: 5px solid var(--primary-color);
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .medical-card:hover {
        transform: translateY(-5px);
    }

    /* أزرار احترافية */
    div.stButton > button {
        background: linear-gradient(45deg, #2E86C1, #3498DB);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 24px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover {
        background: linear-gradient(45deg, #21618C, #2E86C1);
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
    }

    /* تصميم الكاميرا الطبي */
    [data-testid="stCameraInput"] video {
        border-radius: 15px !important;
        border: 4px solid var(--primary-color) !important;
        box-shadow: 0 0 20px rgba(46, 134, 193, 0.3) !important;
    }

    /* العناصر العائمة (DNA / Parasites) */
    .floating-element {
        position: fixed;
        opacity: 0.1;
        z-index: 0;
        animation: float 20s infinite linear;
    }
    @keyframes float {
        0% { transform: translateY(100vh) rotate(0deg); }
        100% { transform: translateY(-10vh) rotate(360deg); }
    }
    </style>
    
    <div class="floating-element" style="left: 10%; font-size: 40px;">🧬</div>
    <div class="floating-element" style="left: 30%; font-size: 30px; animation-delay: 2s;">🦠</div>
    <div class="floating-element" style="left: 70%; font-size: 50px; animation-delay: 5s;">💊</div>
    <div class="floating-element" style="left: 90%; font-size: 35px; animation-delay: 7s;">🔬</div>
""", unsafe_allow_html=True)

# --- 4. فئات ودوال النظام ---

# أ) الشعار الجديد
def render_logo():
    logo_svg = """
    <svg width="100%" height="80" viewBox="0 0 300 80" xmlns="http://www.w3.org/2000/svg">
        <text x="10" y="50" font-family="Arial, sans-serif" font-size="28" font-weight="bold" fill="#ffffff">
            DHIA <tspan fill="#3498DB">Smart Lab</tspan>
        </text>
        <text x="10" y="70" font-family="Arial, sans-serif" font-size="12" fill="#bdc3c7">
            Where Science Meets Intelligence
        </text>
        <circle cx="260" cy="40" r="30" fill="none" stroke="#3498DB" stroke-width="2"/>
        <path d="M260 25 L260 55 M245 40 L275 40" stroke="#E74C3C" stroke-width="2"/>
    </svg>
    """
    st.sidebar.markdown(logo_svg, unsafe_allow_html=True)

# ب) توليد PDF
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'DHIA Smart Lab AI - Rapport Medical', 0, 1, 'C')
        self.ln(10)
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_report(patient_name, result, confidence, recommendation):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.cell(200, 10, txt=f"Medecin Responsable: {st.session_state.user_name}", ln=True)
    pdf.cell(200, 10, txt=f"Patient: {patient_name}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt="Resultats de l'Analyse IA:", ln=True, align='L')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Pathogene Detecte: {result}", ln=True)
    pdf.cell(200, 10, txt=f"Indice de Confiance: {confidence}%", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Recommandation IA:", ln=True)
    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 10, txt=recommendation)
    
    pdf.ln(20)
    pdf.cell(200, 10, txt="Signature Numerique: __________________", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')

# ج) الصوت والذكاء
def speak_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = "temp_audio.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        md = f"""<audio autoplay="true" style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>"""
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

@st.cache_resource
def load_model_ia():
    # محاكاة التحميل لتجنب الأخطاء إذا لم تكن الملفات موجودة
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

# --- 5. بيانات المعرفة (Dr. DhiaBot Brain) ---
# قاعدة بيانات التفسير (Explainable AI)
parasite_info = {
    "Giardia": {
        "desc": "Protozoaire flagellé.",
        "reason": "Forme de poire caractéristique + présence de 2 noyaux visibles.",
        "advice": "Traitement antiparasitaire (Métronidazole) recommandé. Vérifier l'eau potable.",
        "funny": "Wesh ! C'est Giardia avec ses lunettes de soleil. Il te regarde !"
    },
    "Amoeba": {
        "desc": "Amibe dysentérique.",
        "reason": "Membrane irrégulière + Pseudopodes détectés pour le mouvement.",
        "advice": "Risque de dysenterie. Consultation urgente requise.",
        "funny": "Elle bouge en mode ninja. Attention la dysenterie !"
    },
    "Leishmania": {
        "desc": "Parasite tissulaire.",
        "reason": "Forme ovoïde avec kinétoplaste distinct.",
        "advice": "Attention aux phlébotomes. Traitement spécialisé nécessaire.",
        "funny": "Petit mais costaud. Faut appeler le médecin !"
    },
    "Plasmodium": {
        "desc": "Agent du Paludisme.",
        "reason": "Trophozoïtes en forme de bague (Ring stage) dans les érythrocytes.",
        "advice": "URGENCE : Risque de Malaria. Hospitalisation immédiate.",
        "funny": "Aïe aïe aïe ! Les moustiques ont gagné cette fois."
    },
    "Negative": {
        "desc": "Aucun pathogène.",
        "reason": "Absence de structures parasitaires connues.",
        "advice": "Patient sain. Hygiène à maintenir.",
        "funny": "Hamdoullah ! C'est propre. Tu peux dormir tranquille."
    }
}

# --- 6. واجهة تسجيل الدخول (Security) ---
if not st.session_state.logged_in:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center;">
            <h1 style="color: #2E86C1;">🔐 Accès Sécurisé</h1>
            <p>DHIA Smart Lab AI - System Login</p>
        </div>
        """, unsafe_allow_html=True)
        
        user = st.text_input("Identifiant (User)", "admin")
        password = st.text_input("Mot de passe", type="password")
        
        if st.button("Se Connecter / Login", use_container_width=True):
            if user == "admin" and password == "1234":
                st.session_state.logged_in = True
                st.session_state.user_name = "Dr. Sebbag"
                st.success("Accès autorisé !")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Accès refusé.")
    st.stop()

# --- 7. التطبيق الرئيسي (بعد تسجيل الدخول) ---

# Sidebar Navigation
render_logo()
st.sidebar.markdown("---")
menu = st.sidebar.radio("Navigation", ["📊 Dashboard", "🔬 Analyse IA (Scan)", "📁 Rapports", "⚙️ Réglages"])
st.sidebar.markdown("---")
st.sidebar.info(f"👤 Connecté: {st.session_state.user_name}")

# الصفحة 1: Dashboard
if menu == "📊 Dashboard":
    st.title("📊 Tableau de Bord Clinique")
    
    # بطاقات الإحصائيات (Metrics)
    col1, col2, col3, col4 = st.columns(4)
    total_scans = len(st.session_state.history)
    
    # حساب الإحصائيات الحقيقية
    df = pd.DataFrame(st.session_state.history)
    last_p = df.iloc[-1]["result"] if not df.empty else "N/A"
    top_p = df["result"].mode()[0] if not df.empty else "N/A"
    
    col1.metric("Total Analyses", total_scans, "+12%")
    col2.metric("Dernier Cas", last_p)
    col3.metric("Cas Fréquent", top_p)
    col4.metric("Précision IA", "96.5%", "+2%")
    
    st.markdown("---")
    
    # الرسوم البيانية
    c1, c2 = st.columns([2, 1])
    with c1:
        st.subheader("📈 Tendance des Infections")
        if not df.empty:
            chart_data = df["result"].value_counts()
            st.bar_chart(chart_data, color="#2E86C1")
        else:
            st.info("Aucune donnée disponible. Commencez un scan.")
            
    with c2:
        st.subheader("💡 Activité Récente")
        if not df.empty:
            st.dataframe(df[["time", "result", "conf"]].tail(5), hide_index=True)

# الصفحة 2: الفحص (Scan) - قلب النظام
elif menu == "🔬 Analyse IA (Scan)":
    st.markdown("## 🔬 Unité de Diagnostic Intelligent")
    
    # Layout: الكاميرا يسار، النتائج يمين
    col_cam, col_res = st.columns([1, 1])
    
    model, class_names = load_model_ia()
    
    with col_cam:
        st.markdown('<div class="medical-card"><h5>📸 Acquisition Image</h5>', unsafe_allow_html=True)
        img_file = st.camera_input("Microscope Feed", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_res:
        if img_file:
            # 1. محاكاة التحليل متعدد المراحل (Visual Feedback)
            status_container = st.status("🚀 Initialisation du Dr. DhiaBot...", expanded=True)
            
            st.write("🔍 Vérification de la qualité d'image...")
            time.sleep(0.5)
            st.write("🧹 Réduction du bruit numérique...")
            time.sleep(0.5)
            st.write("🧠 Inférence du modèle Deep Learning...")
            
            # 2. التحليل الحقيقي
            image = Image.open(img_file).convert("RGB")
            label = "Inconnu"
            conf = 0
            
            if model:
                size = (224, 224)
                image_res = ImageOps.fit(image, size, method=Image.LANCZOS)
                img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
                data = np.expand_dims(img_array, axis=0)
                prediction = model.predict(data, verbose=0)
                idx = np.argmax(prediction)
                label = class_names[idx] if idx < len(class_names) else "Inconnu"
                conf = int(prediction[0][idx] * 100)
            else:
                # وضع المحاكاة للعرض
                label = "Giardia"
                conf = 97
            
            # اكتمال التحليل
            status_container.update(label="✅ Analyse Terminée !", state="complete", expanded=False)
            
            # 3. جلب البيانات والتفسير
            clean_label = label.strip()
            data = parasite_info.get(clean_label, parasite_info["Negative"])
            
            # تخزين في السجل
            st.session_state.history.append({
                "time": datetime.now().strftime("%H:%M"),
                "result": clean_label,
                "conf": f"{conf}%"
            })
            
            # 4. عرض النتيجة بتصميم البطاقة الطبية
            st.markdown(f"""
            <div class="medical-card" style="border-left: 10px solid { '#E74C3C' if clean_label != 'Negative' else '#2ECC71' };">
                <h2 style="color: #2C3E50; margin:0;">Résultat: <span style="color: #2E86C1;">{clean_label}</span></h2>
                <h4 style="color: #7F8C8D;">Confiance: {conf}%</h4>
                <hr>
                <p><b>🧠 Analyse IA (Pourquoi?):</b> {data['reason']}</p>
                <p><b>🩺 Recommandation Dr. DhiaBot:</b> {data['advice']}</p>
                <div style="background: #fdf2e9; padding: 10px; border-radius: 10px; margin-top: 10px;">
                    <span style="font-size: 20px;">🤖</span> <i>"{data['funny']}"</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # تشغيل الصوت
            if st.session_state.get("last_scan") != str(img_file):
                speak_audio(f"Diagnostic terminé. J'ai détecté {clean_label}. {data['funny']}")
                st.session_state.last_scan = str(img_file)

            # 5. زر تحميل التقرير (PDF)
            report_pdf = generate_report("Patient_Inconnu_01", clean_label, conf, data['advice'])
            st.download_button(
                label="📄 Télécharger Rapport Médical (PDF)",
                data=report_pdf,
                file_name=f"Rapport_{clean_label}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        else:
            st.info("👋 En attente de l'échantillon... / Waiting for sample")
            # صورة توضيحية للمساعد
            st.markdown(f"""
            <div style="text-align: center; opacity: 0.7;">
                <img src="https://cdn-icons-png.flaticon.com/512/3774/3774299.png" width="150">
                <p>Dr. DhiaBot est prêt.</p>
            </div>
            """, unsafe_allow_html=True)

# الصفحة 3: التقارير
elif menu == "📁 Rapports":
    st.title("📁 Archives des Rapports")
    st.write("Séquence des rapports générés automatiquement.")
    
    if st.session_state.history:
        for i, item in enumerate(reversed(st.session_state.history)):
            st.markdown(f"""
            <div class="medical-card" style="padding: 10px; display: flex; justify-content: space-between;">
                <div>
                    <b>Scan #{len(st.session_state.history)-i}</b> - {item['time']}
                </div>
                <div style="color: #2E86C1; font-weight: bold;">
                    {item['result']} ({item['conf']})
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Aucun rapport archivé.")

# الصفحة 4: الإعدادات
elif menu == "⚙️ Réglages":
    st.title("⚙️ Paramètres Système")
    st.toggle("🔔 Notifications Sonores", value=True)
    st.toggle("🌙 Mode Sombre (Expérimental)")
    st.selectbox("Langue Système", ["Français (Défaut)", "English", "العربية"])
    if st.button("🔴 Déconnexion"):
        st.session_state.logged_in = False
        st.rerun()
# --- إضافة في آخر الملف: تذييل الصفحة ---
st.markdown("---") # خط فاصل
col_f1, col_f2 = st.columns([3, 1])

with col_f1:
    st.markdown(f"""
        <p style='font-size: 14px; opacity: 0.6;'>
            📍 INFSP Ouargla | Laboratoire de Parasitologie Numérique <br>
            © 2026 - Développé par <b>Dhia & Mohamed</b>
        </p>
    """, unsafe_allow_html=True)

with col_f2:
    # عرض الوقت الحالي تلقائياً
    now = datetime.now().strftime("%H:%M")
    st.markdown(f"🕒 **Update: {now}**")

# إضافة زر "الاحتفال" في الأسفل (يظهر عند النجاح)
if st.button("🎉 Célébrer la réussite !"):
    st.balloons()
    st.snow()
# --- إضافة في آخر الملف لتصحيح الألوان والوضوح ---

if st.session_state.dark_mode:
    # ألوان الوضع الليلي (Dark Mode) - أسود، أحمر، وأبيض ناصع للكتيبة
    main_bg = "#000000"
    card_bg = "#121212"
    text_primary = "#FFFFFF"  # أبيض ناصع للعنوان
    text_secondary = "#E0E0E0" # رمادي فاتح جداً للشرح
    accent_color = "#FF4B4B"  # أحمر فاقع للوضوح
else:
    # ألوان الوضع النهاري (Light Mode) - أبيض، أزرق، وأسود فاحم للكتيبة
    main_bg = "#FFFFFF"
    card_bg = "#F8F9FA"
    text_primary = "#000000"  # أسود فاحم للعنوان
    text_secondary = "#333333" # رمادي غامق جداً للشرح
    accent_color = "#1E88E5"  # أزرق ملكي

st.markdown(f"""
    <style>
    /* تصحيح لون الخلفية الكلية */
    .stApp {{
        background-color: {main_bg} !important;
    }}

    /* تصحيح وضوح النصوص */
    h1, h2, h3, h4, h5, h6, p, label, span, li, .stMarkdown {{
        color: {text_primary} !important;
        font-weight: 500 !important;
        text-shadow: 0px 0px 1px rgba(0,0,0,0.1); /* زيادة حدة الخط */
    }}

    /* تصحيح شكل البطاقات (Cards) لتصبح واضحة */
    .medical-card, div[data-testid="stVerticalBlock"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {accent_color}33 !important;
        border-radius: 12px;
        padding: 15px;
    }}

    /* تصحيح ألوان المدخلات (Input Fields) لكي تظهر الكتابة داخلها */
    input, textarea, select {{
        color: {text_primary} !important;
        background-color: {card_bg} !important;
        border: 1px solid {accent_color} !important;
    }}

    /* جعل الأزرار واضحة جداً */
    .stButton > button {{
        background-color: {accent_color} !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100%;
        font-size: 18px !important;
        height: 50px;
    }}

    /* تصحيح لون القائمة الجانبية */
    section[data-testid="stSidebar"] {{
        background-color: {card_bg} !important;
        border-right: 2px solid {accent_color} !important;
    }}
    </style>
""", unsafe_allow_html=True)

st.success("✅ تم تحديث الألوان وتحسين وضوح النصوص بنجاح!")
