# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║                  DM SMART LAB AI v7.5 - ULTIMATE FIXED EDITION                 ║
# ║            Diagnostic Parasitologique par Intelligence Artificielle              ║
# ║                                                                                ║
# ║  Développé par:                                                                ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)                       ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                          ║
# ║                                                                                ║
# ║  INFSPM - Ouargla, Algérie 🇩🇿                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════════╝

import streamlit as st
import numpy as np
import pandas as pd
import time
import os
import base64
import hashlib
import random
import json
import io
import sqlite3
import math
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
from datetime import datetime, timedelta
from fpdf import FPDF
from contextlib import contextmanager

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    import plotly.express as px
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# ============================================
#  PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI v7.5",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
#  CONSTANTS
# ============================================
APP_VERSION = "7.5.0"
SECRET_KEY = "dm_smart_lab_2026_ultra_secret"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)

ROLES = {
    "admin": {"level": 3, "icon": "👑",
              "label": {"fr": "Administrateur", "ar": "مدير النظام", "en": "Administrator"}},
    "technician": {"level": 2, "icon": "🔬",
                   "label": {"fr": "Technicien", "ar": "تقني مخبر", "en": "Technician"}},
    "viewer": {"level": 1, "icon": "👁️",
               "label": {"fr": "Observateur", "ar": "مراقب", "en": "Viewer"}}
}

AUTHORS = {
    "dev1": {
        "name": "Sebbag Mohamed Dhia Eddine",
        "role": {"fr": "Expert IA & Conception", "ar": "خبير ذكاء اصطناعي و تصميم", "en": "AI & Design Expert"}
    },
    "dev2": {
        "name": "Ben Sghir Mohamed",
        "role": {"fr": "Expert Laboratoire & Données", "ar": "خبير مخبر و بيانات", "en": "Laboratory & Data Expert"}
    }
}

INSTITUTION = {
    "name": {
        "fr": "Institut National de Formation Supérieure Paramédicale",
        "ar": "المعهد الوطني للتكوين العالي شبه الطبي",
        "en": "National Institute of Higher Paramedical Training"
    },
    "short": "INFSPM",
    "city": "Ouargla",
    "country": {"fr": "Algérie", "ar": "الجزائر", "en": "Algeria"},
    "year": 2026
}

PROJECT_TITLE = {
    "fr": "Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais",
    "ar": "استكشاف إمكانيات الذكاء الاصطناعي للقراءة الآلية للفحص الطفيلي المباشر",
    "en": "Exploring AI potential for automatic reading of fresh parasitological examination"
}

NEON = {
    "cyan": "#00f5ff", "magenta": "#ff00ff", "green": "#00ff88",
    "orange": "#ff6600", "red": "#ff0040", "blue": "#0066ff",
    "purple": "#9933ff", "yellow": "#ffff00", "pink": "#ff69b4"
}

MICROSCOPE_TYPES = [
    "Microscope Optique", "Microscope Binoculaire", "Microscope Inversé",
    "Microscope à Fluorescence", "Microscope Contraste de Phase",
    "Microscope Fond Noir", "Microscope Numérique", "Microscope Confocal"
]

MAGNIFICATIONS = ["x4", "x10", "x20", "x40", "x60", "x100 (Immersion)"]

PREPARATION_TYPES = [
    "État Frais (Direct)", "Coloration au Lugol", "MIF", "Concentration Ritchie",
    "Kato-Katz", "Coloration MGG", "Coloration Giemsa", "Ziehl-Neelsen Modifié",
    "Coloration Trichrome", "Goutte Épaisse", "Frottis Mince", "Scotch-Test (Graham)",
    "Technique Baermann", "Flottation Willis", "Technique Knott"
]

SAMPLES = {
    "fr": ["Selles", "Sang (Frottis)", "Sang (Goutte épaisse)", "Urines", "LCR",
           "Biopsie Cutanée", "Crachat", "Autre"],
    "ar": ["براز", "دم (لطاخة)", "دم (قطرة سميكة)", "بول", "سائل دماغي شوكي",
           "خزعة جلدية", "بلغم", "أخرى"],
    "en": ["Stool", "Blood (Smear)", "Blood (Thick drop)", "Urine", "CSF",
           "Skin Biopsy", "Sputum", "Other"]
}


# ============================================
#  COMPLETE TRANSLATION SYSTEM
# ============================================
TR = {
    "fr": {
        "app_title": "DM Smart Lab AI",
        "login_title": "Connexion Sécurisée",
        "login_subtitle": "Système d'Authentification Professionnel",
        "username": "Identifiant",
        "password": "Mot de Passe",
        "connect": "SE CONNECTER",
        "logout": "Déconnexion",
        "home": "Accueil",
        "scan": "Scan & Analyse",
        "encyclopedia": "Encyclopédie",
        "dashboard": "Tableau de Bord",
        "quiz": "Quiz Médical",
        "chatbot": "DM Bot",
        "compare": "Comparaison",
        "admin": "Administration",
        "about": "À Propos",
        "greeting_morning": "Bonjour",
        "greeting_afternoon": "Bon après-midi",
        "greeting_evening": "Bonsoir",
        "welcome_btn": "🎙️ Message de Bienvenue",
        "intro_btn": "🤖 Présentation du Système",
        "stop_voice": "🔇 Arrêter",
        "patient_info": "Informations du Patient",
        "patient_name": "Nom du Patient",
        "patient_firstname": "Prénom",
        "age": "Âge",
        "sex": "Sexe",
        "male": "Homme",
        "female": "Femme",
        "weight": "Poids (kg)",
        "sample_type": "Type d'Échantillon",
        "lab_info": "Informations du Laboratoire",
        "microscope": "Microscope",
        "magnification": "Grossissement",
        "preparation": "Préparation",
        "technician": "Technicien",
        "notes": "Notes / Observations",
        "image_capture": "Capture Microscopique",
        "take_photo": "📸 Prendre une Photo (Caméra)",
        "upload_file": "📁 Importer un fichier",
        "camera_hint": "Placez l'oculaire du microscope devant la caméra",
        "result": "Résultat",
        "confidence": "Confiance",
        "risk": "Risque",
        "morphology": "Morphologie",
        "description": "Description",
        "advice": "Conseil Médical",
        "extra_tests": "Examens complémentaires suggérés",
        "diagnostic_keys": "Clés Diagnostiques",
        "lifecycle": "Cycle de Vie",
        "all_probabilities": "Toutes les probabilités",
        "download_pdf": "📥 Télécharger PDF",
        "save_db": "💾 Sauvegarder",
        "new_analysis": "🔄 Nouvelle Analyse",
        "listen": "🔊 Écouter",
        "total_analyses": "Total Analyses",
        "reliable": "Fiables",
        "to_verify": "À Vérifier",
        "most_frequent": "Plus Fréquent",
        "avg_confidence": "Confiance Moy.",
        "parasite_distribution": "Distribution des Parasites",
        "confidence_levels": "Niveaux de Confiance",
        "trends": "Tendances (30 jours)",
        "history": "Historique Complet",
        "validate": "Valider",
        "export_csv": "⬇️ CSV",
        "export_json": "⬇️ JSON",
        "start_quiz": "🎮 Démarrer le Quiz",
        "next_question": "➡️ Question Suivante",
        "restart": "🔄 Recommencer",
        "leaderboard": "🏆 Classement",
        "score_excellent": "Excellent ! Vous maîtrisez la parasitologie !",
        "score_good": "Bien joué ! Continuez à apprendre !",
        "score_average": "Pas mal ! Révisez encore un peu !",
        "score_low": "Courage ! La parasitologie s'apprend avec la pratique !",
        "search": "Rechercher...",
        "no_data": "Aucune donnée disponible",
        "no_results": "Aucun résultat trouvé",
        "dark_mode": "Mode Nuit",
        "language": "Langue",
        "daily_tip": "Conseil du Jour",
        "users_mgmt": "Gestion des Utilisateurs",
        "activity_log": "Journal d'Activité",
        "system_info": "Système",
        "create_user": "Créer un Utilisateur",
        "change_pwd": "Changer le Mot de Passe",
        "image1": "Image 1 (Avant)",
        "image2": "Image 2 (Après)",
        "compare_btn": "🔍 Comparer les Images",
        "similarity": "Similarité",
        "filter_comparison": "Comparaison des Filtres",
        "pixel_diff": "Différence Pixel à Pixel",
        "name_required": "⚠️ Le nom du patient est obligatoire !",
        "saved_ok": "✅ Résultat sauvegardé !",
        "demo_mode": "Mode démonstration (aucun modèle IA chargé)",
        "low_conf_warn": "⚠️ Confiance faible. Vérification manuelle recommandée !",
        "voice_welcome": "Bienvenue dans DM Smart Lab AI ! Nous sommes ravis de vous accueillir dans ce système d'intelligence artificielle dédié au diagnostic parasitologique. Ce système a été conçu pour assister les professionnels de santé dans l'identification rapide et précise des parasites.",
        "voice_intro": "Je suis DM Smart Lab AI, version 7 point 5, système de diagnostic parasitologique par intelligence artificielle. J'ai été développé par deux techniciens supérieurs de l'Institut National de Formation Supérieure Paramédicale de Ouargla. Sebbag Mohamed Dhia Eddine, expert en intelligence artificielle et conception, et Ben Sghir Mohamed, expert en laboratoire et données. Ensemble, nous repoussons les limites de la parasitologie moderne !",
        "quick_overview": "Aperçu Rapide",
        "where_science": "Où la Science Rencontre l'Intelligence",
        "system_desc": "Système de diagnostic parasitologique assisté par IA",
        "dev_team": "Équipe de Développement",
        "institution": "Établissement",
        "technologies": "Technologies Utilisées",
        "chat_welcome": "👋 Bonjour ! Je suis **DM Bot** 🤖, votre assistant parasitologique intelligent.\n\nJe peux vous aider avec :\n- 🦠 **Parasites** : Amoeba, Giardia, Plasmodium, Leishmania, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Oxyure, Cryptosporidium...\n- 🔬 **Techniques** : Microscopie, Colorations, Concentration, EPS...\n- 💊 **Traitements** : Protocoles thérapeutiques\n- 🩺 **Cas cliniques** : Diagnostic différentiel\n\n💡 Tapez un mot-clé pour commencer !",
        "chat_placeholder": "Posez votre question sur les parasites...",
        "chat_not_found": "🤖 Je n'ai pas trouvé de réponse exacte. Essayez avec un mot-clé comme : **amoeba**, **giardia**, **plasmodium**, **microscope**, **coloration**, **traitement**, **concentration**, **toxoplasma**, **ascaris**, **taenia**, **oxyure** ou tapez **aide** pour voir tout ce que je connais !",
        "clear_chat": "🗑️ Effacer le chat",
        "quick_questions": "Questions rapides :",
    },
    "ar": {
        "app_title": "مختبر DM الذكي",
        "login_title": "تسجيل الدخول الآمن",
        "login_subtitle": "نظام المصادقة المهني",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "connect": "تسجيل الدخول",
        "logout": "تسجيل الخروج",
        "home": "الرئيسية",
        "scan": "مسح و تحليل",
        "encyclopedia": "الموسوعة",
        "dashboard": "لوحة التحكم",
        "quiz": "اختبار طبي",
        "chatbot": "DM بوت",
        "compare": "المقارنة",
        "admin": "الإدارة",
        "about": "حول المشروع",
        "greeting_morning": "صباح الخير",
        "greeting_afternoon": "مساء الخير",
        "greeting_evening": "مساء الخير",
        "welcome_btn": "🎙️ رسالة ترحيبية",
        "intro_btn": "🤖 تقديم النظام",
        "stop_voice": "🔇 إيقاف",
        "patient_info": "معلومات المريض",
        "patient_name": "اسم المريض",
        "patient_firstname": "الاسم الأول",
        "age": "العمر",
        "sex": "الجنس",
        "male": "ذكر",
        "female": "أنثى",
        "weight": "الوزن (كغ)",
        "sample_type": "نوع العينة",
        "lab_info": "معلومات المخبر",
        "microscope": "المجهر",
        "magnification": "التكبير",
        "preparation": "نوع التحضير",
        "technician": "التقني",
        "notes": "ملاحظات",
        "image_capture": "التقاط مجهري",
        "take_photo": "📸 التقاط صورة (الكاميرا)",
        "upload_file": "📁 استيراد ملف",
        "camera_hint": "ضع عدسة المجهر أمام الكاميرا",
        "result": "النتيجة",
        "confidence": "نسبة الثقة",
        "risk": "مستوى الخطر",
        "morphology": "المورفولوجيا",
        "description": "الوصف",
        "advice": "النصيحة الطبية",
        "extra_tests": "فحوصات إضافية مقترحة",
        "diagnostic_keys": "مفاتيح التشخيص",
        "lifecycle": "دورة الحياة",
        "all_probabilities": "جميع الاحتمالات",
        "download_pdf": "📥 تحميل PDF",
        "save_db": "💾 حفظ",
        "new_analysis": "🔄 تحليل جديد",
        "listen": "🔊 استماع",
        "total_analyses": "مجموع التحاليل",
        "reliable": "موثوقة",
        "to_verify": "للتحقق",
        "most_frequent": "الأكثر شيوعاً",
        "avg_confidence": "متوسط الثقة",
        "parasite_distribution": "توزيع الطفيليات",
        "confidence_levels": "مستويات الثقة",
        "trends": "الاتجاهات (30 يوم)",
        "history": "السجل الكامل",
        "validate": "مصادقة",
        "export_csv": "⬇️ CSV",
        "export_json": "⬇️ JSON",
        "start_quiz": "🎮 بدء الاختبار",
        "next_question": "➡️ السؤال التالي",
        "restart": "🔄 إعادة",
        "leaderboard": "🏆 الترتيب",
        "score_excellent": "ممتاز ! أنت خبير في علم الطفيليات !",
        "score_good": "أحسنت ! واصل التعلم !",
        "score_average": "لا بأس ! راجع قليلاً !",
        "score_low": "شجاعة ! علم الطفيليات يُتعلم بالممارسة !",
        "search": "بحث...",
        "no_data": "لا توجد بيانات",
        "no_results": "لا توجد نتائج",
        "dark_mode": "الوضع الليلي",
        "language": "اللغة",
        "daily_tip": "نصيحة اليوم",
        "users_mgmt": "إدارة المستخدمين",
        "activity_log": "سجل النشاط",
        "system_info": "النظام",
        "create_user": "إنشاء مستخدم",
        "change_pwd": "تغيير كلمة المرور",
        "image1": "الصورة 1 (قبل)",
        "image2": "الصورة 2 (بعد)",
        "compare_btn": "🔍 مقارنة الصور",
        "similarity": "التشابه",
        "filter_comparison": "مقارنة الفلاتر",
        "pixel_diff": "الفرق بكسل ببكسل",
        "name_required": "⚠️ اسم المريض مطلوب !",
        "saved_ok": "✅ تم الحفظ بنجاح !",
        "demo_mode": "وضع تجريبي (لا يوجد نموذج ذكاء اصطناعي)",
        "low_conf_warn": "⚠️ ثقة منخفضة. يُنصح بالتحقق اليدوي !",
        "voice_welcome": "مرحباً بكم في مختبر DM الذكي! نحن سعداء باستقبالكم في هذا النظام المخصص للتشخيص الطفيلي بالذكاء الاصطناعي. هذا النظام مصمم لمساعدة المهنيين الصحيين في التعرف السريع والدقيق على الطفيليات.",
        "voice_intro": "أنا مختبر DM الذكي، النسخة 7.5، نظام تشخيص طفيلي بالذكاء الاصطناعي. تم تطويري من طرف تقنيين ساميين من المعهد الوطني للتكوين العالي شبه الطبي بورقلة. صباغ محمد ضياء الدين، خبير في الذكاء الاصطناعي والتصميم. وبن صغير محمد، خبير في المخبر والبيانات. معاً، ندفع حدود علم الطفيليات الحديث!",
        "quick_overview": "نظرة سريعة",
        "where_science": "حيث يلتقي العلم بالذكاء",
        "system_desc": "نظام تشخيص طفيلي بالذكاء الاصطناعي",
        "dev_team": "فريق التطوير",
        "institution": "المؤسسة",
        "technologies": "التقنيات المستخدمة",
        "chat_welcome": "👋 مرحباً! أنا **DM Bot** 🤖، مساعدك الذكي في علم الطفيليات.\n\nأستطيع مساعدتك في:\n- 🦠 **الطفيليات**: الأميبا، الجيارديا، البلازموديوم، الليشمانيا، التريبانوسوما، البلهارسيا، الأسكاريس...\n- 🔬 **التقنيات**: المجهر، التلوينات، التركيز، فحص البراز...\n- 💊 **العلاجات**: البروتوكولات العلاجية\n- 🩺 **حالات سريرية**: التشخيص التفريقي\n\n💡 اكتب كلمة مفتاحية للبدء!",
        "chat_placeholder": "اطرح سؤالك عن الطفيليات...",
        "chat_not_found": "🤖 لم أجد إجابة دقيقة. جرب كلمة مفتاحية مثل: **amoeba**، **giardia**، **plasmodium**، **microscope**، **مساعدة** أو اكتب **aide** لرؤية كل ما أعرفه!",
        "clear_chat": "🗑️ مسح المحادثة",
        "quick_questions": "أسئلة سريعة:",
    },
    "en": {
        "app_title": "DM Smart Lab AI",
        "login_title": "Secure Login",
        "login_subtitle": "Professional Authentication System",
        "username": "Username",
        "password": "Password",
        "connect": "LOG IN",
        "logout": "Logout",
        "home": "Home",
        "scan": "Scan & Analysis",
        "encyclopedia": "Encyclopedia",
        "dashboard": "Dashboard",
        "quiz": "Medical Quiz",
        "chatbot": "DM Bot",
        "compare": "Comparison",
        "admin": "Administration",
        "about": "About",
        "greeting_morning": "Good morning",
        "greeting_afternoon": "Good afternoon",
        "greeting_evening": "Good evening",
        "welcome_btn": "🎙️ Welcome Message",
        "intro_btn": "🤖 System Introduction",
        "stop_voice": "🔇 Stop",
        "patient_info": "Patient Information",
        "patient_name": "Patient Name",
        "patient_firstname": "First Name",
        "age": "Age",
        "sex": "Sex",
        "male": "Male",
        "female": "Female",
        "weight": "Weight (kg)",
        "sample_type": "Sample Type",
        "lab_info": "Laboratory Information",
        "microscope": "Microscope",
        "magnification": "Magnification",
        "preparation": "Preparation",
        "technician": "Technician",
        "notes": "Notes / Observations",
        "image_capture": "Microscopic Capture",
        "take_photo": "📸 Take a Photo (Camera)",
        "upload_file": "📁 Upload a file",
        "camera_hint": "Place the microscope eyepiece in front of the camera",
        "result": "Result",
        "confidence": "Confidence",
        "risk": "Risk Level",
        "morphology": "Morphology",
        "description": "Description",
        "advice": "Medical Advice",
        "extra_tests": "Suggested Additional Tests",
        "diagnostic_keys": "Diagnostic Keys",
        "lifecycle": "Life Cycle",
        "all_probabilities": "All Probabilities",
        "download_pdf": "📥 Download PDF",
        "save_db": "💾 Save",
        "new_analysis": "🔄 New Analysis",
        "listen": "🔊 Listen",
        "total_analyses": "Total Analyses",
        "reliable": "Reliable",
        "to_verify": "To Verify",
        "most_frequent": "Most Frequent",
        "avg_confidence": "Avg. Confidence",
        "parasite_distribution": "Parasite Distribution",
        "confidence_levels": "Confidence Levels",
        "trends": "Trends (30 days)",
        "history": "Complete History",
        "validate": "Validate",
        "export_csv": "⬇️ CSV",
        "export_json": "⬇️ JSON",
        "start_quiz": "🎮 Start Quiz",
        "next_question": "➡️ Next Question",
        "restart": "🔄 Restart",
        "leaderboard": "🏆 Leaderboard",
        "score_excellent": "Excellent! You master parasitology!",
        "score_good": "Well done! Keep learning!",
        "score_average": "Not bad! Review a bit more!",
        "score_low": "Courage! Parasitology is learned through practice!",
        "search": "Search...",
        "no_data": "No data available",
        "no_results": "No results found",
        "dark_mode": "Dark Mode",
        "language": "Language",
        "daily_tip": "Daily Tip",
        "users_mgmt": "Users Management",
        "activity_log": "Activity Log",
        "system_info": "System",
        "create_user": "Create User",
        "change_pwd": "Change Password",
        "image1": "Image 1 (Before)",
        "image2": "Image 2 (After)",
        "compare_btn": "🔍 Compare Images",
        "similarity": "Similarity",
        "filter_comparison": "Filter Comparison",
        "pixel_diff": "Pixel-by-Pixel Difference",
        "name_required": "⚠️ Patient name is required!",
        "saved_ok": "✅ Result saved!",
        "demo_mode": "Demo mode (no AI model loaded)",
        "low_conf_warn": "⚠️ Low confidence. Manual verification recommended!",
        "voice_welcome": "Welcome to DM Smart Lab AI! We are delighted to have you in this artificial intelligence system dedicated to parasitological diagnosis. This system is designed to help healthcare professionals in the rapid and accurate identification of parasites.",
        "voice_intro": "I am DM Smart Lab AI, version 7 point 5, a parasitological diagnosis system powered by artificial intelligence. I was developed by two senior technicians from the National Institute of Higher Paramedical Training in Ouargla, Algeria. Sebbag Mohamed Dhia Eddine, AI and Design Expert, and Ben Sghir Mohamed, Laboratory and Data Expert. Together, we push the boundaries of modern parasitology!",
        "quick_overview": "Quick Overview",
        "where_science": "Where Science Meets Intelligence",
        "system_desc": "AI-powered parasitological diagnosis system",
        "dev_team": "Development Team",
        "institution": "Institution",
        "technologies": "Technologies Used",
        "chat_welcome": "👋 Hello! I'm **DM Bot** 🤖, your intelligent parasitology assistant.\n\nI can help you with:\n- 🦠 **Parasites**: Amoeba, Giardia, Plasmodium, Leishmania, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Pinworm, Cryptosporidium...\n- 🔬 **Techniques**: Microscopy, Staining, Concentration, Stool exam...\n- 💊 **Treatments**: Therapeutic protocols\n- 🩺 **Clinical cases**: Differential diagnosis\n\n💡 Type a keyword to start!",
        "chat_placeholder": "Ask your question about parasites...",
        "chat_not_found": "🤖 I couldn't find an exact answer. Try a keyword like: **amoeba**, **giardia**, **plasmodium**, **microscope**, **staining**, **treatment**, **concentration**, **toxoplasma**, **ascaris**, **taenia**, **pinworm** or type **help** to see everything I know!",
        "clear_chat": "🗑️ Clear chat",
        "quick_questions": "Quick questions:",
    }
}


def t(key):
    """Get translation for current language"""
    lang = st.session_state.get("lang", "fr")
    return TR.get(lang, TR["fr"]).get(key, TR["fr"].get(key, key))


def tl(d):
    """Get value from a multilingual dict"""
    if not isinstance(d, dict):
        return str(d)
    lang = st.session_state.get("lang", "fr")
    return d.get(lang, d.get("fr", str(d)))


def get_greeting():
    h = datetime.now().hour
    if h < 12:
        return t("greeting_morning")
    elif h < 18:
        return t("greeting_afternoon")
    return t("greeting_evening")


# ============================================
#  DATABASE
# ============================================
DB_PATH = "dm_smartlab.db"


@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    with get_db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL, full_name TEXT NOT NULL,
            role TEXT DEFAULT 'viewer', speciality TEXT DEFAULT 'Laboratoire',
            is_active INTEGER DEFAULT 1, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP, login_count INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0, locked_until TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL, patient_firstname TEXT, patient_age INTEGER,
            patient_sex TEXT, patient_weight REAL, sample_type TEXT,
            microscope_type TEXT, magnification TEXT, preparation_type TEXT,
            technician1 TEXT, technician2 TEXT, notes TEXT,
            parasite_detected TEXT NOT NULL, confidence REAL NOT NULL,
            risk_level TEXT, is_reliable INTEGER, all_predictions TEXT,
            image_hash TEXT, is_demo INTEGER DEFAULT 0,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            validated INTEGER DEFAULT 0, validated_by TEXT, validation_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT,
            action TEXT NOT NULL, details TEXT, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, username TEXT,
            score INTEGER NOT NULL, total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL, category TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        _make_defaults(c)


def _hp(pw):
    if HAS_BCRYPT:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    return hashlib.sha256((pw + SECRET_KEY).encode()).hexdigest()


def _vp(pw, h):
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(pw.encode(), h.encode())
        except Exception:
            pass
    return hashlib.sha256((pw + SECRET_KEY).encode()).hexdigest() == h


def _make_defaults(c):
    for u, p, n, r, s in [
        ("admin", "admin2026", "Administrateur Système", "admin", "Administration"),
        ("dhia", "dhia2026", "Sebbag Mohamed Dhia Eddine", "admin", "IA & Conception"),
        ("mohamed", "mohamed2026", "Ben Sghir Mohamed", "technician", "Laboratoire"),
        ("demo", "demo123", "Utilisateur Démo", "viewer", "Démonstration"),
        ("tech1", "tech2026", "Technicien Labo 1", "technician", "Parasitologie"),
    ]:
        if not c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            c.execute("INSERT INTO users(username,password_hash,full_name,role,speciality) VALUES(?,?,?,?,?)",
                      (u, _hp(p), n, r, s))


def db_login(u, p):
    with get_db() as c:
        row = c.execute("SELECT * FROM users WHERE username=? AND is_active=1", (u,)).fetchone()
        if not row:
            return None
        if row["locked_until"]:
            try:
                if datetime.now() < datetime.fromisoformat(row["locked_until"]):
                    return {"error": "locked"}
                c.execute("UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?", (row["id"],))
            except Exception:
                pass
        if _vp(p, row["password_hash"]):
            c.execute("UPDATE users SET last_login=?,login_count=login_count+1,failed_attempts=0,locked_until=NULL WHERE id=?",
                      (datetime.now().isoformat(), row["id"]))
            return dict(row)
        na = row["failed_attempts"] + 1
        lk = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat() if na >= MAX_LOGIN_ATTEMPTS else None
        c.execute("UPDATE users SET failed_attempts=?,locked_until=? WHERE id=?", (na, lk, row["id"]))
        return {"error": "wrong", "left": MAX_LOGIN_ATTEMPTS - na}


def db_create_user(u, p, n, r="viewer", s=""):
    with get_db() as c:
        if c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            return False
        c.execute("INSERT INTO users(username,password_hash,full_name,role,speciality) VALUES(?,?,?,?,?)",
                  (u, _hp(p), n, r, s))
        return True


def db_users():
    with get_db() as c:
        return [dict(r) for r in c.execute(
            "SELECT id,username,full_name,role,is_active,last_login,login_count,speciality FROM users").fetchall()]


def db_toggle(uid, active):
    with get_db() as c:
        c.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, uid))


def db_chpw(uid, pw):
    with get_db() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (_hp(pw), uid))


def db_save_analysis(uid, d):
    with get_db() as c:
        c.execute("""INSERT INTO analyses(user_id,patient_name,patient_firstname,patient_age,patient_sex,
            patient_weight,sample_type,microscope_type,magnification,preparation_type,technician1,technician2,
            notes,parasite_detected,confidence,risk_level,is_reliable,all_predictions,image_hash,is_demo)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (uid, d.get("pn", ""), d.get("pf", ""), d.get("pa", 0), d.get("ps", ""),
                   d.get("pw", 0), d.get("st", ""), d.get("mt", ""), d.get("mg", ""),
                   d.get("pt", ""), d.get("t1", ""), d.get("t2", ""), d.get("nt", ""),
                   d.get("label", "Negative"), d.get("conf", 0), d.get("risk", "none"),
                   d.get("rel", 0), json.dumps(d.get("preds", {})), d.get("hash", ""),
                   d.get("demo", 0)))
        return c.execute("SELECT last_insert_rowid()").fetchone()[0]


def db_analyses(uid=None, lim=500):
    with get_db() as c:
        q = "SELECT a.*,u.full_name as analyst FROM analyses a JOIN users u ON a.user_id=u.id"
        if uid:
            q += f" WHERE a.user_id=?"
            rows = c.execute(q + " ORDER BY a.analysis_date DESC LIMIT ?", (uid, lim)).fetchall()
        else:
            rows = c.execute(q + " ORDER BY a.analysis_date DESC LIMIT ?", (lim,)).fetchall()
        return [dict(r) for r in rows]


def db_stats(uid=None):
    with get_db() as c:
        w = "WHERE user_id=?" if uid else ""
        p = (uid,) if uid else ()
        tot = c.execute(f"SELECT COUNT(*) FROM analyses {w}", p).fetchone()[0]
        rel = c.execute(f"SELECT COUNT(*) FROM analyses {w} {'AND' if w else 'WHERE'} is_reliable=1", p).fetchone()[0]
        para = c.execute(f"SELECT parasite_detected,COUNT(*) as n FROM analyses {w} GROUP BY parasite_detected ORDER BY n DESC", p).fetchall()
        avg = c.execute(f"SELECT AVG(confidence) FROM analyses {w}", p).fetchone()[0] or 0
        return {"total": tot, "reliable": rel, "verify": tot - rel,
                "parasites": [dict(x) for x in para], "avg": round(avg, 1),
                "top": para[0]["parasite_detected"] if para else "N/A"}


def db_trends(days=30):
    with get_db() as c:
        return [dict(r) for r in c.execute("""
            SELECT DATE(analysis_date) as day,parasite_detected,COUNT(*) as count,AVG(confidence) as avg_conf
            FROM analyses WHERE analysis_date>=date('now',?) GROUP BY day,parasite_detected ORDER BY day
        """, (f"-{days} days",)).fetchall()]


def db_log(uid, uname, action, details=""):
    try:
        with get_db() as c:
            c.execute("INSERT INTO activity_log(user_id,username,action,details) VALUES(?,?,?,?)",
                      (uid, uname, action, details))
    except Exception:
        pass


def db_logs(lim=300):
    with get_db() as c:
        return [dict(r) for r in c.execute("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (lim,)).fetchall()]


def db_quiz_save(uid, un, sc, tot, pct, cat="general"):
    with get_db() as c:
        c.execute("INSERT INTO quiz_scores(user_id,username,score,total_questions,percentage,category) VALUES(?,?,?,?,?,?)",
                  (uid, un, sc, tot, pct, cat))


def db_leaderboard(lim=20):
    with get_db() as c:
        return [dict(r) for r in c.execute(
            "SELECT username,score,total_questions,percentage,timestamp FROM quiz_scores ORDER BY percentage DESC,timestamp ASC LIMIT ?",
            (lim,)).fetchall()]


def db_validate(aid, who):
    with get_db() as c:
        c.execute("UPDATE analyses SET validated=1,validated_by=?,validation_date=? WHERE id=?",
                  (who, datetime.now().isoformat(), aid))


init_database()


# ============================================
#  PARASITE DATABASE (Full multilingual)
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "sci": "Entamoeba histolytica",
        "morph": {"fr": "Kyste sphérique (10-15μm) à 4 noyaux, corps chromatoïde en cigare. Trophozoïte (20-40μm) avec pseudopodes digitiformes et hématies phagocytées.",
                  "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 أنوية، جسم كروماتيني على شكل سيجار. الطور النشط (20-40 ميكرومتر) مع أقدام كاذبة وكريات حمراء مبتلعة.",
                  "en": "Spherical cyst (10-15μm) with 4 nuclei, cigar-shaped chromatoid body. Trophozoite (20-40μm) with pseudopods and phagocytosed RBCs."},
        "desc": {"fr": "Protozoaire responsable de l'amibiase intestinale et extra-intestinale. Transmission féco-orale.",
                 "ar": "طفيلي أولي مسؤول عن الأميبيا المعوية والخارج معوية. الانتقال عبر الفم-البراز.",
                 "en": "Protozoan causing intestinal and extra-intestinal amebiasis. Fecal-oral transmission."},
        "funny": {"fr": "Le ninja des intestins ! Il mange des globules rouges au petit-déjeuner !",
                  "ar": "نينجا الأمعاء! يأكل كريات الدم الحمراء في الفطور!",
                  "en": "The intestinal ninja! Eats red blood cells for breakfast!"},
        "risk": "high",
        "risk_d": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {"fr": "Métronidazole 500mg x3/j (7-10j) + Amoebicide de contact (Intetrix). Contrôle EPS J15/J30.",
                   "ar": "ميترونيدازول 500 ملغ ×3/يوم (7-10 أيام) + أميبيسيد تلامسي. مراقبة EPS ي15/ي30.",
                   "en": "Metronidazole 500mg x3/d (7-10d) + Contact amoebicide (Intetrix). Follow-up D15/D30."},
        "tests": ["Sérologie amibienne", "Échographie hépatique", "NFS+CRP", "PCR Entamoeba", "Scanner abdominal"],
        "color": "#ff0040", "icon": "🔴",
        "cycle": {"fr": "Kyste ingéré → Excystation → Trophozoïte → Invasion tissulaire → Enkystement → Émission",
                  "ar": "كيس مبتلع → انفكاس → طور نشط → غزو أنسجة → تكيس → إخراج",
                  "en": "Ingested cyst → Excystation → Trophozoite → Tissue invasion → Encystation → Emission"},
        "keys": {"fr": "• E. histolytica vs E. dispar: seule histolytica phagocyte les hématies\n• Kyste 4 noyaux (vs E. coli 8)\n• Corps chromatoïdes en cigare\n• Mobilité directionnelle",
                 "ar": "• E. histolytica مقابل E. dispar: فقط histolytica تبتلع الكريات\n• كيس 4 أنوية (مقابل 8 لـ E. coli)\n• أجسام كروماتينية سيجارية\n• حركة اتجاهية",
                 "en": "• E. histolytica vs E. dispar: only histolytica phagocytoses RBCs\n• 4 nuclei cyst (vs E. coli 8)\n• Cigar chromatoid bodies\n• Directional motility"}
    },
    "Giardia": {
        "sci": "Giardia lamblia (intestinalis)",
        "morph": {"fr": "Trophozoïte piriforme en 'cerf-volant' (12-15μm), 2 noyaux (face de hibou), disque adhésif, 4 paires de flagelles. Kyste ovoïde (8-12μm) à 4 noyaux.",
                  "ar": "الطور النشط كمثري 'طائرة ورقية' (12-15μm)، نواتان (وجه البومة)، قرص لاصق، 4 أزواج أسواط. كيس بيضاوي (8-12μm) بـ 4 أنوية.",
                  "en": "Pear-shaped 'kite' trophozoite (12-15μm), 2 nuclei (owl face), adhesive disk, 4 flagella pairs. Ovoid cyst (8-12μm) with 4 nuclei."},
        "desc": {"fr": "Flagellé du duodénum. Diarrhée graisseuse chronique, malabsorption. Transmission hydrique.",
                 "ar": "سوطي الاثني عشر. إسهال دهني مزمن، سوء امتصاص. انتقال عبر الماء.",
                 "en": "Duodenal flagellate. Chronic greasy diarrhea, malabsorption. Waterborne."},
        "funny": {"fr": "Il te fixe avec ses lunettes de soleil ! Un touriste qui refuse de partir !",
                  "ar": "ينظر إليك بنظارته الشمسية! سائح يرفض المغادرة!",
                  "en": "It stares at you with sunglasses! A tourist who refuses to leave!"},
        "risk": "medium", "risk_d": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {"fr": "Métronidazole 250mg x3/j (5j) OU Tinidazole 2g dose unique.",
                   "ar": "ميترونيدازول 250ملغ ×3/يوم (5 أيام) أو تينيدازول 2غ جرعة واحدة.",
                   "en": "Metronidazole 250mg x3/d (5d) OR Tinidazole 2g single dose."},
        "tests": ["Ag Giardia ELISA", "Test malabsorption", "EPS x3", "PCR Giardia"],
        "color": "#ff9500", "icon": "🟠",
        "cycle": {"fr": "Kyste ingéré → Excystation duodénale → Trophozoïte → Adhésion → Multiplication → Enkystement",
                  "ar": "كيس مبتلع → انفكاس → طور نشط → التصاق → تكاثر → تكيس",
                  "en": "Ingested cyst → Duodenal excystation → Trophozoite → Adhesion → Multiplication → Encystation"},
        "keys": {"fr": "• Forme cerf-volant pathognomonique\n• 2 noyaux = face de hibou\n• Disque adhésif au Lugol\n• Mobilité 'feuille morte'",
                 "ar": "• شكل طائرة ورقية مميز\n• نواتان = وجه البومة\n• القرص اللاصق باللوغول\n• حركة 'ورقة ميتة'",
                 "en": "• Pathognomonic kite shape\n• 2 nuclei = owl face\n• Adhesive disk on Lugol\n• 'Falling leaf' motility"}
    },
    "Leishmania": {
        "sci": "Leishmania infantum / major / tropica",
        "morph": {"fr": "Amastigotes ovoïdes (2-5μm) intracellulaires dans macrophages. Noyau + kinétoplaste (MGG).",
                  "ar": "أماستيغوت بيضاوية (2-5μm) داخل البلاعم. نواة + كينيتوبلاست (MGG).",
                  "en": "Ovoid amastigotes (2-5μm) intracellular in macrophages. Nucleus + kinetoplast (MGG)."},
        "desc": {"fr": "Transmis par phlébotome. Cutanée ou viscérale. Algérie: L. infantum (nord), L. major (sud).",
                 "ar": "ينتقل عبر ذبابة الرمل. جلدية أو حشوية. الجزائر: L. infantum (شمال)، L. major (جنوب).",
                 "en": "Sandfly-transmitted. Cutaneous or visceral. Algeria: L. infantum (north), L. major (south)."},
        "funny": {"fr": "Petit mais costaud ! Il squatte les macrophages !",
                  "ar": "صغير لكن قوي! يحتل البلاعم!",
                  "en": "Small but tough! Squats in macrophages!"},
        "risk": "high", "risk_d": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {"fr": "Cutanée: Glucantime IM. Viscérale: Amphotéricine B liposomale. MDO en Algérie.",
                   "ar": "جلدية: غلوكانتيم عضلياً. حشوية: أمفوتيريسين ب. تبليغ إجباري.",
                   "en": "Cutaneous: Glucantime IM. Visceral: Liposomal Amphotericin B. Notifiable."},
        "tests": ["IDR Monténégro", "Sérologie", "Ponction médullaire", "Biopsie+MGG", "PCR Leishmania", "NFS"],
        "color": "#ff0040", "icon": "🔴",
        "cycle": {"fr": "Piqûre phlébotome → Promastigotes → Phagocytose → Amastigotes → Multiplication → Lyse",
                  "ar": "لدغة ذبابة رمل → بروماستيغوت → بلعمة → أماستيغوت → تكاثر → تحلل",
                  "en": "Sandfly bite → Promastigotes → Phagocytosis → Amastigotes → Multiplication → Lysis"},
        "keys": {"fr": "• Amastigotes 2-5μm intracellulaires\n• Noyau + kinétoplaste MGG\n• Culture NNN\n• PCR = gold standard",
                 "ar": "• أماستيغوت 2-5μm داخل خلوية\n• نواة + كينيتوبلاست MGG\n• زراعة NNN\n• PCR المعيار الذهبي",
                 "en": "• 2-5μm intracellular amastigotes\n• Nucleus+kinetoplast MGG\n• NNN culture\n• PCR=gold standard"}
    },
    "Plasmodium": {
        "sci": "Plasmodium falciparum / vivax / ovale / malariae",
        "morph": {"fr": "P. falciparum: anneau 'bague à chaton', gamétocytes en banane. P. vivax: trophozoïte amiboïde, granulations Schüffner.",
                  "ar": "P. falciparum: حلقة 'خاتم'، خلايا جنسية موزية. P. vivax: طور نشط أميبي، حبيبات شوفنر.",
                  "en": "P. falciparum: signet ring, banana gametocytes. P. vivax: amoeboid trophozoite, Schüffner dots."},
        "desc": {"fr": "🚨 URGENCE MÉDICALE ! Paludisme. P. falciparum = le plus mortel. Anophèle femelle.",
                 "ar": "🚨 حالة طوارئ طبية! ملاريا. P. falciparum = الأكثر فتكاً. أنثى الأنوفيل.",
                 "en": "🚨 MEDICAL EMERGENCY! Malaria. P. falciparum = most lethal. Female Anopheles."},
        "funny": {"fr": "Il demande le mariage à tes globules ! Gamétocytes en banane = le clown du microscope !",
                  "ar": "يطلب الزواج من كرياتك! خلايا جنسية موزية = مهرج المجهر!",
                  "en": "Proposes to your blood cells! Banana gametocytes = microscope clown!"},
        "risk": "critical", "risk_d": {"fr": "🚨 URGENCE", "ar": "🚨 طوارئ", "en": "🚨 EMERGENCY"},
        "advice": {"fr": "HOSPITALISATION ! ACT. Quinine IV si grave. Parasitémie /4-6h.",
                   "ar": "دخول المستشفى! ACT. كينين وريدي إذا خطير. طفيليات الدم كل 4-6 ساعات.",
                   "en": "HOSPITALIZATION! ACT. IV Quinine if severe. Parasitemia /4-6h."},
        "tests": ["TDR Paludisme", "Frottis+GE URGENCE", "Parasitémie quantitative", "NFS", "Bilan hépato-rénal", "Glycémie"],
        "color": "#7f1d1d", "icon": "🚨",
        "cycle": {"fr": "Piqûre anophèle → Sporozoïtes → Hépatocytes → Mérozoïtes → Hématies → Gamétocytes",
                  "ar": "لدغة الأنوفيل → سبوروزويت → خلايا كبدية → ميروزويت → كريات حمراء → خلايا جنسية",
                  "en": "Anopheles bite → Sporozoites → Hepatocytes → Merozoites → RBCs → Gametocytes"},
        "keys": {"fr": "• URGENCE <2h\n• Frottis: espèce\n• GE: 10x sensible\n• >2% = grave\n• Banane = P. falciparum",
                 "ar": "• طوارئ <2 ساعة\n• لطاخة: النوع\n• GE: أكثر حساسية 10x\n• >2% = خطير\n• موز = P. falciparum",
                 "en": "• URGENT <2h\n• Smear: species\n• TD: 10x sensitive\n• >2%=severe\n• Banana=P. falciparum"}
    },
    "Trypanosoma": {
        "sci": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "morph": {"fr": "Forme S/C (15-30μm), flagelle libre, membrane ondulante, kinétoplaste postérieur.",
                  "ar": "شكل S/C (15-30μm)، سوط حر، غشاء متموج، كينيتوبلاست خلفي.",
                  "en": "S/C shape (15-30μm), free flagellum, undulating membrane, posterior kinetoplast."},
        "desc": {"fr": "Maladie du sommeil (tsé-tsé) ou Chagas (triatome). Phase hémolymphatique puis neurologique.",
                 "ar": "مرض النوم (تسي تسي) أو شاغاس (بق ثلاثي). مرحلة دموية ثم عصبية.",
                 "en": "Sleeping sickness (tsetse) or Chagas (triatomine). Hemolymphatic then neurological phase."},
        "funny": {"fr": "Il court avec sa membrane ondulante ! La tsé-tsé = le pire taxi !",
                  "ar": "يركض بغشائه المتموج! ذبابة تسي تسي = أسوأ تاكسي!",
                  "en": "Runs with its undulating membrane! Tsetse = worst taxi!"},
        "risk": "high", "risk_d": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {"fr": "Phase 1: Pentamidine. Phase 2: NECT/Mélarsoprol. PL obligatoire.",
                   "ar": "المرحلة 1: بنتاميدين. المرحلة 2: NECT. بزل قطني إجباري.",
                   "en": "Phase 1: Pentamidine. Phase 2: NECT/Melarsoprol. LP mandatory."},
        "tests": ["Ponction lombaire", "Sérologie CATT", "IgM", "Suc ganglionnaire", "NFS"],
        "color": "#ff0040", "icon": "🔴",
        "cycle": {"fr": "Piqûre tsé-tsé → Trypomastigotes → Sang → Phase 1 → BHE → Phase 2 neurologique",
                  "ar": "لدغة تسي تسي → تريبوماستيغوت → دم → مرحلة 1 → حاجز دماغي → مرحلة 2 عصبية",
                  "en": "Tsetse bite → Trypomastigotes → Blood → Phase 1 → BBB → Phase 2 neurological"},
        "keys": {"fr": "• Forme S/C + membrane ondulante\n• Kinétoplaste postérieur\n• IgM très élevée\n• PL staging",
                 "ar": "• شكل S/C + غشاء متموج\n• كينيتوبلاست خلفي\n• IgM مرتفع جداً\n• تصنيف بالبزل القطني",
                 "en": "• S/C+undulating membrane\n• Posterior kinetoplast\n• Very high IgM\n• LP staging"}
    },
    "Schistosoma": {
        "sci": "Schistosoma haematobium / mansoni / japonicum",
        "morph": {"fr": "Œuf ovoïde (115-170μm): éperon terminal (S. haematobium) ou latéral (S. mansoni). Miracidium mobile.",
                  "ar": "بيضة بيضاوية (115-170μm): شوكة طرفية (S. haematobium) أو جانبية (S. mansoni). ميراسيديوم متحرك.",
                  "en": "Ovoid egg (115-170μm): terminal spine (S. haematobium) or lateral (S. mansoni). Motile miracidium."},
        "desc": {"fr": "Bilharziose. S. haematobium: uro-génitale. S. mansoni: hépato-intestinale.",
                 "ar": "البلهارسيا. S. haematobium: بولي تناسلي. S. mansoni: كبدي معوي.",
                 "en": "Schistosomiasis. S. haematobium: urogenital. S. mansoni: hepato-intestinal."},
        "funny": {"fr": "L'œuf avec un dard ! Les cercaires = micro-torpilles !",
                  "ar": "البيضة ذات الشوكة! السركاريا = طوربيدات صغيرة!",
                  "en": "Egg with a stinger! Cercariae = micro-torpedoes!"},
        "risk": "medium", "risk_d": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {"fr": "Praziquantel 40mg/kg dose unique. S. haematobium: urines de midi.",
                   "ar": "برازيكوانتيل 40ملغ/كغ جرعة واحدة. S. haematobium: بول الظهيرة.",
                   "en": "Praziquantel 40mg/kg single dose. S. haematobium: midday urine."},
        "tests": ["ECBU midi", "Sérologie", "Écho vésicale/hépatique", "NFS+éosinophilie", "Biopsie rectale"],
        "color": "#ff9500", "icon": "🟠",
        "cycle": {"fr": "Œuf → Miracidium → Mollusque → Cercaire → Pénétration cutanée → Vers adultes → Ponte",
                  "ar": "بيضة → ميراسيديوم → رخويات → سركاريا → اختراق الجلد → ديدان بالغة → وضع البيض",
                  "en": "Egg → Miracidium → Snail → Cercaria → Skin penetration → Adult worms → Egg laying"},
        "keys": {"fr": "• S.h: éperon TERMINAL, urines MIDI\n• S.m: éperon LATÉRAL, selles\n• Miracidium vivant\n• Éosinophilie élevée",
                 "ar": "• S.h: شوكة طرفية، بول الظهيرة\n• S.m: شوكة جانبية، براز\n• ميراسيديوم حي\n• فرط الحمضات",
                 "en": "• S.h: TERMINAL spine, MIDDAY urine\n• S.m: LATERAL spine, stool\n• Living miracidium\n• High eosinophilia"}
    },
    "Negative": {
        "sci": "N/A",
        "morph": {"fr": "Absence d'éléments parasitaires. Flore bactérienne normale.",
                  "ar": "غياب العناصر الطفيلية. فلورا بكتيرية طبيعية.",
                  "en": "No parasitic elements. Normal bacterial flora."},
        "desc": {"fr": "Échantillon négatif. Un seul négatif n'exclut pas (sensibilité ~50-60%). Répéter x3.",
                 "ar": "عينة سلبية. فحص واحد سلبي لا يستبعد (حساسية ~50-60%). كرر ×3.",
                 "en": "Negative sample. Single negative doesn't exclude (~50-60% sensitivity). Repeat x3."},
        "funny": {"fr": "Rien à signaler ! Mais les parasites sont des maîtres du cache-cache !",
                  "ar": "لا شيء يُذكر! لكن الطفيليات أساتذة في الاختباء!",
                  "en": "Nothing to report! But parasites are hide-and-seek masters!"},
        "risk": "none", "risk_d": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {"fr": "RAS. Répéter x3 si suspicion clinique.",
                   "ar": "لا شيء. كرر ×3 إذا كان هناك اشتباه.",
                   "en": "Clear. Repeat x3 if clinical suspicion."},
        "tests": ["Répéter EPS x3", "Sérologie ciblée", "NFS (éosinophilie?)"],
        "color": "#00ff88", "icon": "🟢",
        "cycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "keys": {"fr": "• Direct+Lugol négatif\n• Concentration négative\n• Répéter x3",
                 "ar": "• مباشر+لوغول سلبي\n• تركيز سلبي\n• كرر ×3",
                 "en": "• Direct+Lugol negative\n• Concentration negative\n• Repeat x3"}
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())


# ============================================
#  ENHANCED QUIZ (60+ questions)
# ============================================
def mq(fr, ar, en):
    return {"fr": fr, "ar": ar, "en": en}


QUIZ_QUESTIONS = [
    {"q": mq("Quel parasite présente une 'bague à chaton' dans les hématies?", "أي طفيلي يظهر شكل 'الخاتم' في كريات الدم الحمراء؟", "Which parasite shows a 'signet ring' in RBCs?"),
     "opts": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "ans": 1, "cat": "Hématozoaires",
     "expl": mq("Plasmodium: bague à chaton au stade trophozoïte jeune.", "البلازموديوم: شكل الخاتم في مرحلة الطور النشط.", "Plasmodium: signet ring at young trophozoite stage.")},
    {"q": mq("Le kyste mature de Giardia possède combien de noyaux?", "كم عدد أنوية كيس الجيارديا الناضج؟", "How many nuclei does a mature Giardia cyst have?"),
     "opts": ["2", "4", "6", "8"], "ans": 1, "cat": "Protozoaires",
     "expl": mq("4 noyaux. Le trophozoïte en a 2.", "4 أنوية. الطور النشط له نواتان.", "4 nuclei. Trophozoite has 2.")},
    {"q": mq("Quel parasite est transmis par le phlébotome?", "أي طفيلي ينتقل عبر ذبابة الرمل؟", "Which parasite is sandfly-transmitted?"),
     "opts": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "ans": 2, "cat": "Vecteurs",
     "expl": mq("Leishmania = phlébotome.", "ليشمانيا = ذبابة الرمل.", "Leishmania = sandfly.")},
    {"q": mq("L'éperon terminal caractérise:", "الشوكة الطرفية تميز:", "Terminal spine characterizes:"),
     "opts": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "ans": 1, "cat": "Helminthes",
     "expl": mq("S. haematobium=terminal, S. mansoni=latéral.", "S. haematobium=طرفية, S. mansoni=جانبية.", "S. haematobium=terminal, S. mansoni=lateral.")},
    {"q": mq("Examen urgent suspicion paludisme?", "الفحص الطارئ عند الاشتباه بالملاريا؟", "Urgent exam for malaria?"),
     "opts": ["Coproculture", "ECBU", "Goutte épaisse+Frottis", "Sérologie"], "ans": 2, "cat": "Diagnostic",
     "expl": mq("GE+Frottis = référence urgente.", "قطرة سميكة+لطاخة = المرجع.", "TD+Smear = urgent reference.")},
    {"q": mq("E. histolytica se distingue par:", "يتميز E. histolytica بـ:", "E. histolytica distinguished by:"),
     "opts": ["Flagelles", "Hématies phagocytées", "Membrane ondulante", "Kinétoplaste"], "ans": 1, "cat": "Morphologie",
     "expl": mq("Hématies phagocytées = pathogénicité.", "الكريات المبتلعة = معيار المرضية.", "Phagocytosed RBCs = pathogenicity.")},
    {"q": mq("Chagas est causée par:", "مرض شاغاس يسببه:", "Chagas is caused by:"),
     "opts": ["T. b. gambiense", "T. cruzi", "L. donovani", "P. vivax"], "ans": 1, "cat": "Protozoaires",
     "expl": mq("T. cruzi transmis par triatomes.", "T. cruzi عبر البق الثلاثي.", "T. cruzi by triatomines.")},
    {"q": mq("Colorant pour amastigotes Leishmania?", "ملون أماستيغوت الليشمانيا؟", "Stain for Leishmania amastigotes?"),
     "opts": ["Ziehl-Neelsen", "Gram", "MGG/Giemsa", "Lugol"], "ans": 2, "cat": "Techniques",
     "expl": mq("MGG = noyau + kinétoplaste.", "MGG = نواة + كينيتوبلاست.", "MGG = nucleus + kinetoplast.")},
    {"q": mq("Traitement référence bilharziose?", "العلاج المرجعي للبلهارسيا؟", "Reference treatment schistosomiasis?"),
     "opts": ["Chloroquine", "Métronidazole", "Praziquantel", "Albendazole"], "ans": 2, "cat": "Thérapeutique",
     "expl": mq("Praziquantel = choix n°1.", "برازيكوانتيل = الخيار الأول.", "Praziquantel = 1st choice.")},
    {"q": mq("'Face de hibou' observée chez:", "'وجه البومة' عند:", "'Owl face' observed in:"),
     "opts": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "ans": 1, "cat": "Morphologie",
     "expl": mq("2 noyaux symétriques Giardia.", "نواتان متماثلتان للجيارديا.", "2 symmetrical Giardia nuclei.")},
    {"q": mq("Technique de Ritchie:", "تقنية ريتشي:", "Ritchie technique:"),
     "opts": ["Coloration", "Concentration diphasique", "Culture", "Sérologie"], "ans": 1, "cat": "Techniques",
     "expl": mq("Formol-éther = concentration.", "فورمول-إيثر = تركيز.", "Formalin-ether = concentration.")},
    {"q": mq("Le Lugol met en évidence:", "اللوغول يُظهر:", "Lugol highlights:"),
     "opts": ["Flagelles", "Noyaux des kystes", "Hématies", "Bactéries"], "ans": 1, "cat": "Techniques",
     "expl": mq("Iode colore glycogène et noyaux.", "اليود يلون الغليكوجين والأنوية.", "Iodine stains glycogen+nuclei.")},
    {"q": mq("x100 nécessite:", "العدسة x100 تحتاج:", "x100 requires:"),
     "opts": ["Eau", "Huile d'immersion", "Alcool", "Sérum"], "ans": 1, "cat": "Microscopie",
     "expl": mq("Huile augmente indice réfraction.", "الزيت يزيد معامل الانكسار.", "Oil increases refractive index.")},
    {"q": mq("Scotch-test Graham recherche:", "اختبار غراهام يبحث عن:", "Graham test looks for:"),
     "opts": ["Giardia", "Enterobius", "Ascaris", "Taenia"], "ans": 1, "cat": "Techniques",
     "expl": mq("Œufs d'oxyure péri-anaux.", "بيض الأكسيور حول الشرج.", "Pinworm eggs perianal.")},
    {"q": mq("Coloration Cryptosporidium?", "تلوين الكريبتوسبوريديوم؟", "Cryptosporidium staining?"),
     "opts": ["Lugol", "Ziehl-Neelsen modifié", "MGG", "Gram"], "ans": 1, "cat": "Techniques",
     "expl": mq("ZN modifié = oocystes roses.", "ZN معدل = أكياس بيضية وردية.", "Modified ZN = pink oocysts.")},
    {"q": mq("Œuf d'Ascaris:", "بيضة الأسكاريس:", "Ascaris egg:"),
     "opts": ["Avec éperon", "Mamelonné", "Operculé", "En citron"], "ans": 1, "cat": "Helminthes",
     "expl": mq("Ovoïde, mamelonné, coque épaisse.", "بيضاوي، حُلَيمي، قشرة سميكة.", "Ovoid, mammillated, thick shell.")},
    {"q": mq("Scolex T. solium possède:", "رأس T. solium يحتوي:", "T. solium scolex has:"),
     "opts": ["Ventouses seules", "Crochets seuls", "Ventouses+crochets", "Bothridies"], "ans": 2, "cat": "Helminthes",
     "expl": mq("Armé = ventouses + crochets.", "مسلحة = ممصات + خطاطيف.", "Armed = suckers + hooks.")},
    {"q": mq("Éosinophilie sanguine oriente vers:", "فرط الحمضات يوجه نحو:", "Eosinophilia points to:"),
     "opts": ["Bactéries", "Helminthiase", "Virose", "Paludisme"], "ans": 1, "cat": "Diagnostic",
     "expl": mq("Éosinophilie = helminthiase.", "فرط الحمضات = ديدان.", "Eosinophilia = helminthiasis.")},
    {"q": mq("Cysticercose causée par:", "الكيسات المذنبة يسببها:", "Cysticercosis caused by:"),
     "opts": ["T. saginata adulte", "Larve T. solium", "Echinococcus", "Ascaris"], "ans": 1, "cat": "Helminthes",
     "expl": mq("Cysticerque T. solium.", "كيسة مذنبة T. solium.", "T. solium cysticercus.")},
    {"q": mq("Leishmaniose cutanée sud Algérie:", "ليشمانيا جلدية جنوب الجزائر:", "Southern Algeria cutaneous leish:"),
     "opts": ["L. infantum", "L. major", "L. tropica", "L. braziliensis"], "ans": 1, "cat": "Épidémiologie",
     "expl": mq("L. major = sud, zoonotique.", "L. major = جنوب، حيوانية.", "L. major = south, zoonotic.")},
    {"q": mq("Vecteur du paludisme?", "ناقل الملاريا؟", "Malaria vector?"),
     "opts": ["Aedes", "Culex", "Anopheles", "Simulium"], "ans": 2, "cat": "Épidémiologie",
     "expl": mq("Anophèle femelle.", "أنثى الأنوفيل.", "Female Anopheles.")},
    {"q": mq("Kyste hydatique dû à:", "الكيس العداري يسببه:", "Hydatid cyst caused by:"),
     "opts": ["T. saginata", "E. granulosus", "Fasciola", "Toxocara"], "ans": 1, "cat": "Helminthes",
     "expl": mq("Echinococcus granulosus (chien).", "Echinococcus granulosus (كلب).", "Echinococcus granulosus (dog).")},
    {"q": mq("Corps chromatoïde 'cigare':", "جسم كروماتيني 'سيجار':", "'Cigar' chromatoid body:"),
     "opts": ["E. histolytica", "E. coli", "Giardia", "Balantidium"], "ans": 0, "cat": "Morphologie",
     "expl": mq("E. histolytica=cigare, E. coli=pointu.", "E. histolytica=سيجار, E. coli=مدبب.", "E. histolytica=cigar, E. coli=pointed.")},
    {"q": mq("Protozoaire macro+micronoyau?", "طفيلي بنواة كبيرة وصغيرة؟", "Protozoan macro+micronucleus?"),
     "opts": ["Giardia", "Balantidium coli", "Trichomonas", "Entamoeba"], "ans": 1, "cat": "Morphologie",
     "expl": mq("Seul cilié pathogène humain.", "الهدبي الممرض الوحيد.", "Only pathogenic human ciliate.")},
    {"q": mq("Membrane ondulante:", "الغشاء المتموج:", "Undulating membrane:"),
     "opts": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "ans": 1, "cat": "Morphologie",
     "expl": mq("Trypanosoma = membrane ondulante.", "تريبانوسوما = غشاء متموج.", "Trypanosoma = undulating membrane.")},
    {"q": mq("Gamétocyte 'banane':", "خلية جنسية 'موز':", "'Banana' gametocyte:"),
     "opts": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "ans": 1, "cat": "Hématozoaires",
     "expl": mq("Pathognomonique P. falciparum.", "مميز لـ P. falciparum.", "Pathognomonic P. falciparum.")},
    {"q": mq("Kyste E. coli: noyaux?", "كيس E. coli: أنوية؟", "E. coli cyst: nuclei?"),
     "opts": ["4", "6", "8", "12"], "ans": 2, "cat": "Morphologie",
     "expl": mq("E. coli=8, E. histolytica=4.", "E. coli=8, E. histolytica=4.", "E. coli=8, E. histolytica=4.")},
    {"q": mq("Métronidazole inefficace contre:", "ميترونيدازول غير فعال ضد:", "Metronidazole ineffective against:"),
     "opts": ["E. histolytica", "Giardia", "Helminthes", "Trichomonas"], "ans": 2, "cat": "Thérapeutique",
     "expl": mq("Anti-protozoaire, pas anti-helminthique.", "مضاد أوليات، ليس مضاد ديدان.", "Anti-protozoal, not anti-helminthic.")},
    {"q": mq("Albendazole est:", "الألبندازول:", "Albendazole is:"),
     "opts": ["Anti-protozoaire", "Anti-helminthique", "Antibiotique", "Antifongique"], "ans": 1, "cat": "Thérapeutique",
     "expl": mq("Large spectre helminthes.", "واسع الطيف ضد الديدان.", "Broad spectrum anti-helminthic.")},
    {"q": mq("Paludisme grave:", "ملاريا خطيرة:", "Severe malaria:"),
     "opts": ["Chloroquine", "Artésunate IV", "Métronidazole", "Praziquantel"], "ans": 1, "cat": "Thérapeutique",
     "expl": mq("Artésunate IV = 1ère ligne OMS.", "أرتيسونات وريدي = الخط الأول.", "IV Artesunate = WHO 1st line.")},
    {"q": mq("Fièvre+frissons retour Afrique?", "حمى+قشعريرة بعد العودة من إفريقيا؟", "Fever+chills returning from Africa?"),
     "opts": ["Amibiase", "Paludisme", "Bilharziose", "Giardiose"], "ans": 1, "cat": "Cas clinique",
     "expl": mq("Paludisme jusqu'à preuve du contraire.", "ملاريا حتى يثبت العكس.", "Malaria until proven otherwise.")},
    {"q": mq("Hématurie+baignade eau douce:", "بيلة دموية+سباحة ماء عذب:", "Hematuria+freshwater swimming:"),
     "opts": ["Giardiose", "Paludisme", "Bilharziose urinaire", "Amibiase"], "ans": 2, "cat": "Cas clinique",
     "expl": mq("S. haematobium.", "S. haematobium.", "S. haematobium.")},
    {"q": mq("Diarrhée graisseuse enfant:", "إسهال دهني عند طفل:", "Greasy diarrhea child:"),
     "opts": ["Amibiase", "Giardiose", "Cryptosporidiose", "Salmonellose"], "ans": 1, "cat": "Cas clinique",
     "expl": mq("Giardia = malabsorption fréquente.", "الجيارديا = سوء امتصاص شائع.", "Giardia = common malabsorption.")},
    {"q": mq("Ulcère indolore retour Sahara:", "قرحة غير مؤلمة بعد الصحراء:", "Painless ulcer from Sahara:"),
     "opts": ["Leishmaniose cutanée", "Furoncle", "Anthrax", "Mycose"], "ans": 0, "cat": "Cas clinique",
     "expl": mq("Clou de Biskra = L. major.", "حبة بسكرة = L. major.", "Biskra button = L. major.")},
    {"q": mq("Bilharziose: contamination par:", "البلهارسيا: العدوى عبر:", "Schistosomiasis: contamination by:"),
     "opts": ["Ingestion eau", "Contact cutané eau douce", "Piqûre insecte", "Voie aérienne"], "ans": 1, "cat": "Épidémiologie",
     "expl": mq("Cercaires pénètrent la peau.", "السركاريا تخترق الجلد.", "Cercariae penetrate skin.")},
    {"q": mq("GE vs Frottis mince:", "القطرة السميكة مقابل اللطاخة:", "Thick drop vs Thin smear:"),
     "opts": ["Même sensibilité", "GE 10x plus sensible", "FM plus sensible", "Incomparable"], "ans": 1, "cat": "Techniques",
     "expl": mq("GE = 10x plus sensible.", "GE = أكثر حساسية 10x.", "TD = 10x more sensitive.")},
    {"q": mq("S. haematobium: échantillon?", "S. haematobium: العينة؟", "S. haematobium: sample?"),
     "opts": ["Selles matin", "Urines midi", "Sang nocturne", "LCR"], "ans": 1, "cat": "Techniques",
     "expl": mq("Pic excrétion = midi.", "ذروة الإخراج = الظهيرة.", "Peak excretion = midday.")},
    {"q": mq("Toxoplasma: hôte définitif?", "التوكسوبلازما: المضيف النهائي؟", "Toxoplasma: definitive host?"),
     "opts": ["Homme", "Chat", "Chien", "Moustique"], "ans": 1, "cat": "Épidémiologie",
     "expl": mq("Chat = cycle sexué.", "القط = الدورة الجنسية.", "Cat = sexual cycle.")},
    {"q": mq("Willis utilise:", "تقنية ويليس تستخدم:", "Willis uses:"),
     "opts": ["Formol-éther", "NaCl saturé (flottation)", "Acide-alcool", "Lugol"], "ans": 1, "cat": "Techniques",
     "expl": mq("Flottation NaCl saturé.", "تعويم في NaCl مشبع.", "Saturated NaCl flotation.")},
    {"q": mq("Hypnozoïtes chez:", "هيبنوزويت عند:", "Hypnozoites in:"),
     "opts": ["P. falciparum", "P. vivax", "P. malariae", "Aucun"], "ans": 1, "cat": "Hématozoaires",
     "expl": mq("P. vivax et P. ovale → rechutes.", "P. vivax و P. ovale → انتكاسات.", "P. vivax & P. ovale → relapses.")},
    {"q": mq("Niclosamide agit sur:", "نيكلوساميد يعمل على:", "Niclosamide acts on:"),
     "opts": ["Nématodes", "Cestodes", "Trématodes", "Protozoaires"], "ans": 1, "cat": "Thérapeutique",
     "expl": mq("Spécifique cestodes.", "خاص بالشريطيات.", "Specific for cestodes.")},
    {"q": mq("Ivermectine: indication?", "إيفرمكتين: الاستعمال؟", "Ivermectin: indication?"),
     "opts": ["Filarioses/strongyloïdose", "Paludisme", "Amibiase", "Giardiose"], "ans": 0, "cat": "Thérapeutique",
     "expl": mq("Référence filarioses.", "المرجع للفيلاريا.", "Reference for filariasis.")},
    {"q": mq("Test CATT diagnostique:", "اختبار CATT يشخص:", "CATT test diagnoses:"),
     "opts": ["Paludisme", "Leishmaniose", "Trypanosomiase", "Toxoplasmose"], "ans": 2, "cat": "Diagnostic",
     "expl": mq("Card Agglutination Test Trypanosomiasis.", "اختبار التراص البطاقي.", "Card Agglutination Test.")},
    {"q": mq("Plus grand protozoaire humain:", "أكبر طفيلي أولي بشري:", "Largest human protozoan:"),
     "opts": ["Giardia", "Balantidium coli", "Entamoeba", "Trichomonas"], "ans": 1, "cat": "Morphologie",
     "expl": mq("Balantidium ≤200μm.", "Balantidium حتى 200μm.", "Balantidium up to 200μm.")},
    {"q": mq("Fasciola hepatica: localisation?", "Fasciola hepatica: الموضع؟", "Fasciola hepatica: location?"),
     "opts": ["Intestin", "Côlon", "Voies biliaires", "Poumons"], "ans": 2, "cat": "Helminthes",
     "expl": mq("Grande douve = voies biliaires.", "المتورقة = القنوات الصفراوية.", "Liver fluke = bile ducts.")},
    {"q": mq("Strongyloides: particularité?", "Strongyloides: خاصية؟", "Strongyloides: peculiarity?"),
     "opts": ["Pas de cycle externe", "Auto-infestation", "2 hôtes nécessaires", "Aérienne"], "ans": 1, "cat": "Helminthes",
     "expl": mq("Auto-infestation endogène.", "عدوى ذاتية داخلية.", "Endogenous auto-infection.")},
    {"q": mq("Somnolence+adénopathies cervicales:", "نعاس+تضخم عقد عنقية:", "Drowsiness+cervical lymphadenopathy:"),
     "opts": ["Paludisme", "Leishmaniose", "Trypanosomiase", "Toxoplasmose"], "ans": 2, "cat": "Cas clinique",
     "expl": mq("Maladie du sommeil = THA.", "مرض النوم = THA.", "Sleeping sickness = HAT.")},
]


# ============================================
#  ENHANCED CHATBOT (DM Bot)
# ============================================
CHAT_KB = {}
# Build from parasite DB
for pname, pdata in PARASITE_DB.items():
    if pname == "Negative":
        continue
    key = pname.lower().split("(")[0].strip().split(" ")[0].lower()
    CHAT_KB[key] = {
        "fr": f"🔬 **{pname}** ({pdata['sci']})\n\n**Morphologie:** {tl(pdata['morph']) if isinstance(pdata['morph'], str) else pdata['morph'].get('fr','')}\n\n**Description:** {pdata['desc'].get('fr','')}\n\n**Traitement:** {pdata['advice'].get('fr','')}\n\n**Examens:** {', '.join(pdata.get('tests',[]))}\n\n🤖 {pdata['funny'].get('fr','')}",
        "ar": f"🔬 **{pname}** ({pdata['sci']})\n\n**المورفولوجيا:** {pdata['morph'].get('ar','')}\n\n**الوصف:** {pdata['desc'].get('ar','')}\n\n**العلاج:** {pdata['advice'].get('ar','')}\n\n🤖 {pdata['funny'].get('ar','')}",
        "en": f"🔬 **{pname}** ({pdata['sci']})\n\n**Morphology:** {pdata['morph'].get('en','')}\n\n**Description:** {pdata['desc'].get('en','')}\n\n**Treatment:** {pdata['advice'].get('en','')}\n\n🤖 {pdata['funny'].get('en','')}"
    }
    # Add scientific name as alias
    sci_key = pdata["sci"].lower().split("/")[0].strip().split(" ")[-1]
    if sci_key not in CHAT_KB:
        CHAT_KB[sci_key] = CHAT_KB[key]

# Add extra knowledge
CHAT_KB.update({
    "amibe": CHAT_KB.get("amoeba", {}),
    "malaria": CHAT_KB.get("plasmodium", {}),
    "paludisme": CHAT_KB.get("plasmodium", {}),
    "ملاريا": CHAT_KB.get("plasmodium", {}),
    "bilharziose": CHAT_KB.get("schistosoma", {}),
    "بلهارسيا": CHAT_KB.get("schistosoma", {}),
    "microscope": {
        "fr": "🔬 **Microscopie:**\n\n• **x10:** Repérage\n• **x40:** Œufs/kystes\n• **x100 (immersion):** Plasmodium, Leishmania\n\n💡 Nettoyer l'objectif x100 après l'huile!\n\n**Types:** Optique, Fluorescence, Contraste de phase, Fond noir, Confocal",
        "ar": "🔬 **المجهرية:**\n\n• **x10:** استطلاع\n• **x40:** بيض/أكياس\n• **x100 (غمر):** بلازموديوم، ليشمانيا\n\n💡 نظف العدسة x100 بعد الزيت!",
        "en": "🔬 **Microscopy:**\n\n• **x10:** Survey\n• **x40:** Eggs/cysts\n• **x100 (immersion):** Plasmodium, Leishmania\n\n💡 Clean x100 after oil!"
    },
    "coloration": {
        "fr": "🎨 **Colorations:**\n\n• **Lugol:** Noyaux kystes, glycogène\n• **MGG/Giemsa:** Parasites sanguins\n• **Ziehl-Neelsen modifié:** Cryptosporidium\n• **Trichrome:** Parasites intestinaux\n• **Hématoxyline ferrique:** Amibes\n\n💡 Lugol frais chaque semaine!",
        "ar": "🎨 **التلوينات:**\n\n• **لوغول:** أنوية الأكياس\n• **MGG/جيمزا:** طفيليات الدم\n• **ZN معدل:** كريبتوسبوريديوم\n• **تريكروم:** طفيليات معوية",
        "en": "🎨 **Staining:**\n\n• **Lugol:** Cyst nuclei\n• **MGG/Giemsa:** Blood parasites\n• **Modified ZN:** Cryptosporidium\n• **Trichrome:** Intestinal parasites"
    },
    "concentration": {
        "fr": "🧪 **Techniques concentration:**\n\n• **Ritchie (Formol-éther):** RÉFÉRENCE\n• **Willis (NaCl saturé):** Flottation\n• **Kato-Katz:** Semi-quantitatif\n• **Baermann:** Larves Strongyloides\n• **MIF:** Fixation+coloration",
        "ar": "🧪 **تقنيات التركيز:**\n\n• **ريتشي:** المرجع\n• **ويليس:** تعويم\n• **كاتو-كاتز:** شبه كمي\n• **بيرمان:** يرقات",
        "en": "🧪 **Concentration:**\n\n• **Ritchie:** REFERENCE\n• **Willis:** Flotation\n• **Kato-Katz:** Semi-quantitative\n• **Baermann:** Strongyloides larvae"
    },
    "selle": {
        "fr": "💩 **EPS Complet:**\n\n1. **Macroscopique:** Consistance, couleur, sang, mucus\n2. **Direct:** NaCl 0.9% + Lugol\n3. **Concentration:** Ritchie/Willis\n\n⚠️ Examiner dans 30 min!\n⚠️ Répéter x3!\n\n💡 Selles liquides→trophozoïtes, Formées→kystes",
        "ar": "💩 **فحص البراز:**\n\n1. عياني\n2. مباشر: NaCl + لوغول\n3. تركيز: ريتشي/ويليس\n\n⚠️ فحص خلال 30 دقيقة!\n⚠️ كرر ×3!",
        "en": "💩 **Complete Stool Exam:**\n\n1. Macroscopic\n2. Direct: NaCl + Lugol\n3. Concentration: Ritchie/Willis\n\n⚠️ Examine within 30 min!\n⚠️ Repeat x3!"
    },
    "hygiene": {
        "fr": "🧼 **Prévention:**\n\n✅ Lavage mains 30s\n✅ Eau potable\n✅ Cuisson viande >65°C\n✅ Moustiquaires\n✅ Éviter eaux stagnantes\n✅ Lavage fruits/légumes\n\n💡 80% des parasitoses sont évitables!",
        "ar": "🧼 **الوقاية:**\n\n✅ غسل اليدين 30 ثانية\n✅ ماء صالح للشرب\n✅ طهي اللحم >65°C\n✅ ناموسيات\n✅ تجنب المياه الراكدة\n\n💡 80% من الطفيليات يمكن الوقاية منها!",
        "en": "🧼 **Prevention:**\n\n✅ Handwashing 30s\n✅ Safe water\n✅ Cook meat >65°C\n✅ Mosquito nets\n✅ Avoid stagnant water\n\n💡 80% of parasitoses are preventable!"
    },
    "traitement": {
        "fr": "💊 **Traitements:**\n\n• **Métronidazole:** Amoeba+Giardia+Trichomonas\n• **Albendazole:** Helminthes large spectre\n• **Praziquantel:** Schistosoma+Cestodes\n• **Artésunate/ACT:** Paludisme\n• **Glucantime:** Leishmaniose cutanée\n• **Ivermectine:** Filarioses\n• **Niclosamide:** Ténias",
        "ar": "💊 **العلاجات:**\n\n• **ميترونيدازول:** أميبا+جيارديا\n• **ألبندازول:** ديدان\n• **برازيكوانتيل:** بلهارسيا+شريطيات\n• **أرتيسونات:** ملاريا\n• **غلوكانتيم:** ليشمانيا جلدية",
        "en": "💊 **Treatments:**\n\n• **Metronidazole:** Amoeba+Giardia+Trichomonas\n• **Albendazole:** Broad spectrum helminths\n• **Praziquantel:** Schistosoma+Cestodes\n• **Artesunate/ACT:** Malaria\n• **Glucantime:** Cutaneous Leishmania"
    },
    "toxoplasma": {
        "fr": "🔬 **Toxoplasma gondii**\n\n• Tachyzoïte en arc (4-8μm)\n• Hôte définitif: **Chat**\n• ⚠️ DANGER femme enceinte séronégative!\n• Diagnostic: Sérologie IgG/IgM, avidité\n• Prévention: Cuisson viande, lavage crudités, éviter litière",
        "ar": "🔬 **توكسوبلازما**\n\nالمضيف النهائي: القط\n⚠️ خطر على الحامل!\nالتشخيص: مصلية IgG/IgM",
        "en": "🔬 **Toxoplasma gondii**\n\n• Definitive host: **Cat**\n• ⚠️ DANGER seronegative pregnant!\n• Diagnosis: IgG/IgM serology"
    },
    "ascaris": {
        "fr": "🔬 **Ascaris lumbricoides**\n\n• Ver rond 15-35cm!\n• Œuf mamelonné 60-70μm\n• Cycle: Migration hépato-pulmonaire\n• Syndrome Löffler: Toux+éosinophilie\n• Traitement: Albendazole 400mg",
        "ar": "🔬 **الأسكاريس**\n\nدودة 15-35 سم!\nبيضة حُلَيمية\nالعلاج: ألبندازول 400 ملغ",
        "en": "🔬 **Ascaris lumbricoides**\n\n• Round worm 15-35cm!\n• Mammillated egg 60-70μm\n• Treatment: Albendazole 400mg"
    },
    "taenia": {
        "fr": "🔬 **Taenia**\n\n• **T. saginata:** Bœuf, inerme\n• **T. solium:** Porc, armé → cysticercose!\n• Diagnostic: Anneaux dans selles\n• Traitement: Praziquantel/Niclosamide",
        "ar": "🔬 **الشريطية**\n\nT. saginata: بقر\nT. solium: خنزير → كيسات مذنبة!\nالعلاج: برازيكوانتيل",
        "en": "🔬 **Taenia**\n\n• T. saginata: Beef\n• T. solium: Pork → cysticercosis!\n• Treatment: Praziquantel"
    },
    "oxyure": {
        "fr": "🔬 **Oxyure (Enterobius)**\n\n• Ver blanc ~1cm\n• Prurit anal nocturne enfant\n• Scotch-test MATIN avant toilette!\n• Traitement: Flubendazole + traiter TOUTE la famille!",
        "ar": "🔬 **الأكسيور**\n\nدودة بيضاء ~1سم\nحكة شرجية ليلية\nاختبار غراهام صباحاً!\nعلاج كل العائلة!",
        "en": "🔬 **Pinworm (Enterobius)**\n\n• White worm ~1cm\n• Nocturnal anal pruritus in children\n• Graham test MORNING!\n• Treat WHOLE family!"
    },
    "cryptosporidium": {
        "fr": "🔬 **Cryptosporidium**\n\n• Oocyste 4-6μm (très petit!)\n• ZN modifié = rose sur vert\n• Diarrhée immunodéprimé (VIH)\n• Traitement: Nitazoxanide",
        "ar": "🔬 **كريبتوسبوريديوم**\n\nكيس 4-6μm\nZN معدل\nإسهال عند ناقصي المناعة\nنيتازوكسانيد",
        "en": "🔬 **Cryptosporidium**\n\n• Oocyst 4-6μm\n• Modified ZN\n• Diarrhea in immunocompromised\n• Nitazoxanide"
    },
    "bonjour": {"fr": "👋 Bonjour! Comment puis-je vous aider?", "ar": "👋 مرحباً! كيف أقدر أساعدك؟", "en": "👋 Hello! How can I help?"},
    "salut": {"fr": "Salut! 😊 Posez votre question!", "ar": "مرحباً! 😊", "en": "Hi! 😊"},
    "مرحبا": {"fr": "مرحباً!", "ar": "مرحباً! 😊 اكتب اسم أي طفيلي!", "en": "Hello!"},
    "hello": {"fr": "Hello!", "ar": "مرحباً!", "en": "Hello! 😊 Type any parasite name!"},
    "merci": {"fr": "De rien! 😊", "ar": "عفواً! 😊", "en": "You're welcome! 😊"},
    "شكرا": {"fr": "عفواً!", "ar": "عفواً! 😊", "en": "Welcome!"},
    "aide": {
        "fr": "📚 **Je connais:**\n\n🦠 Parasites: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Toxoplasma, Ascaris, Taenia, Oxyure, Cryptosporidium, Balantidium, Fasciola, Strongyloides, Trichomonas...\n\n🔬 Techniques: microscope, coloration, concentration, selle\n\n💊 Traitements: traitement\n\n🧼 Prévention: hygiene\n\n💡 Tapez un mot-clé!",
        "ar": "📚 **أعرف:**\n\n🦠 الطفيليات: الأميبا، الجيارديا، البلازموديوم، الليشمانيا، التريبانوسوما، البلهارسيا، التوكسوبلازما، الأسكاريس...\n\n🔬 التقنيات: microscope, coloration, concentration\n\n💊 العلاجات: traitement\n\n💡 اكتب كلمة مفتاحية!",
        "en": "📚 **I know:**\n\n🦠 Parasites: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Toxoplasma, Ascaris, Taenia, Pinworm, Cryptosporidium...\n\n🔬 Techniques: microscope, staining, concentration\n\n💊 Treatments: treatment\n\n💡 Type a keyword!"
    },
    "help": {"fr": "Tapez 'aide'!", "ar": "اكتب 'مساعدة'!", "en": "📚 Type any parasite name or technique!"},
    "مساعدة": {"fr": "اكتب كلمة!", "ar": "📚 اكتب اسم أي طفيلي أو تقنية!", "en": "Type a keyword!"},
})


def chatbot_reply(msg):
    lang = st.session_state.get("lang", "fr")
    low = msg.lower().strip()

    # Direct match
    for key, resp in CHAT_KB.items():
        if key in low:
            if isinstance(resp, dict):
                return resp.get(lang, resp.get("fr", str(resp)))
            return str(resp)

    # Fuzzy match parasites
    for pname, pdata in PARASITE_DB.items():
        if pname == "Negative":
            continue
        checks = [pname.lower(), pdata["sci"].lower()]
        for check in checks:
            for word in check.split():
                if len(word) > 3 and word in low:
                    entry = CHAT_KB.get(pname.lower().split("(")[0].strip().split(" ")[0].lower())
                    if entry:
                        return entry.get(lang, entry.get("fr", ""))

    return t("chat_not_found")


# ============================================
#  DAILY TIPS
# ============================================
TIPS = {
    "fr": [
        "💡 Examiner les selles dans les 30 min pour voir les trophozoïtes mobiles.",
        "💡 Le Lugol met en évidence les noyaux des kystes. Fraîchement préparé!",
        "💡 Frottis mince: angle 45° pour monocouche parfaite.",
        "💡 Goutte épaisse = 10x plus sensible que frottis mince.",
        "💡 Urines de midi pour S. haematobium (pic d'excrétion).",
        "💡 Répéter EPS x3 à quelques jours d'intervalle.",
        "💡 Métronidazole = Amoeba + Giardia + Trichomonas !",
        "💡 ZN modifié indispensable pour Cryptosporidium.",
        "💡 1ère GE négative ne suffit pas. Répéter à 6-12h.",
        "💡 Éosinophilie = helminthiase. Toujours vérifier!",
        "💡 E. coli 8 noyaux vs E. histolytica 4 noyaux.",
        "💡 Selles liquides → trophozoïtes. Formées → kystes.",
        "💡 PCR = gold standard identification espèce Leishmania.",
        "💡 Scotch-test Graham: le MATIN avant la toilette!",
    ],
    "ar": [
        "💡 افحص البراز خلال 30 دقيقة لرؤية الأطوار النشطة المتحركة.",
        "💡 اللوغول يُظهر أنوية الأكياس. تحضير طازج!",
        "💡 القطرة السميكة أكثر حساسية 10 مرات من اللطاخة.",
        "💡 بول الظهيرة لـ S. haematobium.",
        "💡 كرر EPS ×3 بفاصل عدة أيام.",
        "💡 ميترونيدازول = أميبا + جيارديا + تريكوموناس!",
        "💡 فرط الحمضات = ديدان طفيلية محتملة.",
        "💡 E. coli = 8 أنوية مقابل E. histolytica = 4.",
        "💡 براز سائل → أطوار نشطة. متماسك → أكياس.",
    ],
    "en": [
        "💡 Examine stool within 30 min to see motile trophozoites.",
        "💡 Lugol highlights cyst nuclei. Freshly prepared!",
        "💡 Thick drop = 10x more sensitive than thin smear.",
        "💡 Midday urine for S. haematobium.",
        "💡 Repeat stool exam x3 at intervals.",
        "💡 Metronidazole = Amoeba + Giardia + Trichomonas!",
        "💡 Eosinophilia = probable helminthiasis.",
        "💡 E. coli = 8 nuclei vs E. histolytica = 4.",
        "💡 Liquid stool → trophozoites. Formed → cysts.",
    ]
}

# ============================================
#  SESSION STATE
# ============================================
DEFAULTS = {
    "logged_in": False, "user_id": None, "user_name": "", "user_role": "viewer",
    "user_full_name": "", "dark_mode": True, "lang": "fr",
    "demo_seed": None, "heatmap_seed": None,
    "quiz_state": {"current": 0, "score": 0, "answered": [], "active": False},
    "chat_history": [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================
#  UTILITY FUNCTIONS
# ============================================
def has_role(lvl):
    return ROLES.get(st.session_state.get("user_role", "viewer"), {}).get("level", 0) >= lvl


def risk_color(lv):
    return {"critical": "#ff0040", "high": "#ff3366", "medium": "#ff9500", "low": "#00e676", "none": "#00ff88"}.get(lv, "#888")


def risk_pct(lv):
    return {"critical": 100, "high": 80, "medium": 50, "low": 25, "none": 0}.get(lv, 0)


def speak_js(text, lc=None):
    if lc is None:
        lc = st.session_state.get("lang", "fr")
    safe = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    jl = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(lc, "fr-FR")
    st.markdown(f"""<script>try{{window.speechSynthesis.cancel();var m=new SpeechSynthesisUtterance('{safe}');m.lang='{jl}';m.rate=0.9;window.speechSynthesis.speak(m);}}catch(e){{}}</script>""", unsafe_allow_html=True)


def stop_js():
    st.markdown("""<script>try{window.speechSynthesis.cancel();}catch(e){}</script>""", unsafe_allow_html=True)


# ============================================
#  AI ENGINE
# ============================================
@st.cache_resource(show_spinner=False)
def load_model():
    m, mn, mt = None, None, None
    try:
        import tensorflow as tf
        for ext in [".keras", ".h5"]:
            ff = [f for f in os.listdir(".") if f.endswith(ext) and os.path.isfile(f)]
            if ff:
                mn = ff[0]; m = tf.keras.models.load_model(mn, compile=False); mt = "keras"; break
        if m is None:
            ff = [f for f in os.listdir(".") if f.endswith(".tflite") and os.path.isfile(f)]
            if ff:
                mn = ff[0]; m = tf.lite.Interpreter(model_path=mn); m.allocate_tensors(); mt = "tflite"
    except Exception:
        pass
    return m, mn, mt


def predict(model, mt, img, seed=None):
    res = {"label": "Negative", "conf": 0, "preds": {}, "rel": False, "demo": False, "risk": "none"}
    rm = {"Plasmodium": "critical", "Amoeba (E. histolytica)": "high", "Leishmania": "high",
          "Trypanosoma": "high", "Giardia": "medium", "Schistosoma": "medium", "Negative": "none"}
    if model is None:
        res["demo"] = True
        if seed is None: seed = random.randint(0, 999999)
        rng = random.Random(seed)
        lb = rng.choice(CLASS_NAMES); cf = rng.randint(55, 98)
        ap = {}; rem = 100.0 - cf
        for c in CLASS_NAMES:
            ap[c] = float(cf) if c == lb else round(rng.uniform(0, rem / max(1, len(CLASS_NAMES) - 1)), 1)
        res.update({"label": lb, "conf": cf, "preds": ap, "rel": cf >= CONFIDENCE_THRESHOLD, "risk": rm.get(lb, "none")})
        return res
    try:
        import tensorflow as tf
        im = ImageOps.fit(img.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
        arr = np.expand_dims(np.asarray(im).astype(np.float32) / 127.5 - 1.0, 0)
        if mt == "tflite":
            inp, out = model.get_input_details(), model.get_output_details()
            model.set_tensor(inp[0]['index'], arr); model.invoke(); pr = model.get_tensor(out[0]['index'])[0]
        else:
            pr = model.predict(arr, verbose=0)[0]
        ix = int(np.argmax(pr)); cf = int(pr[ix] * 100)
        lb = CLASS_NAMES[ix] if ix < len(CLASS_NAMES) else "Negative"
        ap = {CLASS_NAMES[i]: round(float(pr[i]) * 100, 1) for i in range(min(len(pr), len(CLASS_NAMES)))}
        res.update({"label": lb, "conf": cf, "preds": ap, "rel": cf >= CONFIDENCE_THRESHOLD, "risk": rm.get(lb, "none")})
    except Exception as e:
        st.error(f"Error: {e}")
    return res


# ============================================
#  IMAGE PROCESSING
# ============================================
def gen_heatmap(img, seed=None):
    im = img.copy().convert("RGB"); w, h = im.size
    if seed is None: seed = hash(im.tobytes()[:1000]) % 1000000
    rng = random.Random(seed)
    ea = np.array(ImageOps.grayscale(im).filter(ImageFilter.FIND_EDGES))
    bs, mx, bx, by = 32, 0, w // 2, h // 2
    for y in range(0, h - bs, bs // 2):
        for x in range(0, w - bs, bs // 2):
            s = np.mean(ea[y:y + bs, x:x + bs])
            if s > mx: mx, bx, by = s, x + bs // 2, y + bs // 2
    bx = max(50, min(w - 50, bx + rng.randint(-w // 10, w // 10)))
    by = max(50, min(h - 50, by + rng.randint(-h // 10, h // 10)))
    hm = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(hm)
    mr = min(w, h) // 3
    for r in range(mr, 0, -2):
        a = max(0, min(200, int(200 * (1 - r / mr)))); rat = r / mr
        c = (0, 255, 100, a // 4) if rat > 0.65 else (255, 255, 0, a // 2) if rat > 0.35 else (255, 0, 60, a)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=c)
    return Image.alpha_composite(im.convert('RGBA'), hm).convert('RGB')


def thermal(img):
    return ImageOps.colorize(ImageOps.grayscale(ImageEnhance.Contrast(img).enhance(1.5)).filter(ImageFilter.GaussianBlur(1)),
                             black="navy", white="yellow", mid="red")


def edges(img):
    return ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)


def enhanced(img):
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(img).enhance(2.0)).enhance(2.0)


def negative(img):
    return ImageOps.invert(img.convert("RGB"))


def emboss(img):
    return img.filter(ImageFilter.EMBOSS)


def adjust(img, br=1.0, co=1.0, sa=1.0):
    r = img.copy()
    if br != 1.0: r = ImageEnhance.Brightness(r).enhance(br)
    if co != 1.0: r = ImageEnhance.Contrast(r).enhance(co)
    if sa != 1.0: r = ImageEnhance.Color(r).enhance(sa)
    return r


def zoom(img, lv):
    if lv <= 1.0: return img
    w, h = img.size; nw, nh = int(w / lv), int(h / lv)
    l, t = (w - nw) // 2, (h - nh) // 2
    return img.crop((l, t, l + nw, t + nh)).resize((w, h), Image.LANCZOS)


def compare_imgs(i1, i2):
    a1 = np.array(i1.convert("RGB").resize((128, 128))).astype(float)
    a2 = np.array(i2.convert("RGB").resize((128, 128))).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    m1, m2, s1, s2 = np.mean(a1), np.mean(a2), np.std(a1), np.std(a2)
    s12 = np.mean((a1 - m1) * (a2 - m2))
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * m1 * m2 + c1) * (2 * s12 + c2)) / ((m1 ** 2 + m2 ** 2 + c1) * (s1 ** 2 + s2 ** 2 + c2))
    return {"mse": round(mse, 2), "ssim": round(float(ssim), 4), "sim": round(float(ssim) * 100, 1)}


def pixel_diff(i1, i2):
    """Generate pixel difference image"""
    a1 = np.array(i1.convert("RGB").resize((256, 256))).astype(float)
    a2 = np.array(i2.convert("RGB").resize((256, 256))).astype(float)
    diff = np.abs(a1 - a2).astype(np.uint8)
    # Amplify difference
    diff = np.clip(diff * 3, 0, 255).astype(np.uint8)
    return Image.fromarray(diff)


def histogram(img):
    r, g, b = img.convert("RGB").split()
    return {"red": list(r.histogram()), "green": list(g.histogram()), "blue": list(b.histogram())}


# ============================================
#  PDF
# ============================================
def _sp(text):
    if not text: return ""
    reps = {'é':'e','è':'e','ê':'e','ë':'e','à':'a','â':'a','ù':'u','û':'u','ü':'u',
            'ô':'o','ö':'o','î':'i','ï':'i','ç':'c','É':'E','È':'E','Ê':'E','À':'A',
            'Ù':'U','Ô':'O','Î':'I','Ç':'C','→':'->','°':'o','µ':'u','×':'x',
            '🔴':'[!]','🟠':'[!]','🟢':'[OK]','🚨':'[!!!]'}
    for o, r in reps.items(): text = text.replace(o, r)
    return ''.join(c if ord(c) < 256 else '?' for c in text)


class PDF(FPDF):
    def header(self):
        self.set_fill_color(0,40,100); self.rect(0,0,210,3,'F')
        self.set_fill_color(0,200,255); self.rect(0,3,210,1,'F'); self.ln(6)
        self.set_font("Arial","B",12); self.set_text_color(0,60,150)
        self.cell(0,8,f"DM SMART LAB AI v{APP_VERSION}",0,0,"L")
        self.set_font("Arial","",8); self.set_text_color(100,100,100)
        self.cell(0,8,datetime.now().strftime("%d/%m/%Y %H:%M"),0,1,"R")
        self.line(10,18,200,18); self.ln(6)
    def footer(self):
        self.set_y(-15); self.set_font("Arial","I",7); self.set_text_color(150,150,150)
        self.cell(0,4,_sp("AVERTISSEMENT: Rapport IA - Validation professionnelle requise"),0,0,"C")
    def section(self,title,color=(0,60,150)):
        self.set_fill_color(*color); self.set_text_color(255,255,255)
        self.set_font("Arial","B",10); self.cell(0,7,f"  {_sp(title)}",0,1,"L",True)
        self.ln(2); self.set_text_color(0,0,0)
    def field(self,label,val):
        self.set_font("Arial","B",9); self.set_text_color(80,80,80); self.cell(50,6,_sp(label),0,0)
        self.set_font("Arial","",9); self.set_text_color(0,0,0); self.cell(0,6,_sp(str(val)),0,1)


def make_pdf(pat, lab, result, lbl):
    pdf = PDF(); pdf.alias_nb_pages(); pdf.add_page(); pdf.set_auto_page_break(True,20)
    pdf.set_font("Arial","B",16); pdf.set_text_color(0,60,150)
    pdf.cell(0,12,"RAPPORT D'ANALYSE PARASITOLOGIQUE",0,1,"C")
    rid = hashlib.md5(f"{pat.get('Nom','')}{datetime.now().isoformat()}".encode()).hexdigest()[:10].upper()
    pdf.set_font("Arial","",8); pdf.cell(0,5,f"Ref: DM-{rid}",0,1,"R"); pdf.ln(3)
    pdf.section("PATIENT"); [pdf.field(f"{k}:",v) for k,v in pat.items()]; pdf.ln(2)
    pdf.section("LABORATOIRE",(0,100,80)); [pdf.field(f"{k}:",v) for k,v in lab.items() if v]; pdf.ln(2)
    pdf.section("RESULTAT IA",(180,0,0)); pdf.ln(2)
    cf = result.get("conf",0)
    if lbl=="Negative": pdf.set_fill_color(220,255,220); pdf.set_text_color(0,128,0)
    else: pdf.set_fill_color(255,220,220); pdf.set_text_color(200,0,0)
    pdf.set_font("Arial","B",14); pdf.cell(0,10,f"  {_sp(lbl)} - {cf}%",1,1,"C",True)
    pdf.set_text_color(0,0,0); pdf.ln(3)
    info = PARASITE_DB.get(lbl, PARASITE_DB["Negative"])
    pdf.set_font("Arial","",9)
    pdf.multi_cell(0,5,_sp(f"Morphologie: {info['morph'].get('fr','')}"))
    pdf.multi_cell(0,5,_sp(f"Conseil: {info['advice'].get('fr','')}"))
    if HAS_QRCODE:
        try:
            qr = qrcode.QRCode(box_size=3,border=1); qr.add_data(f"DM|{lbl}|{cf}%|{rid}")
            qr.make(fit=True); qp = f"_qr_{rid}.png"; qr.make_image().save(qp)
            pdf.image(qp,x=170,y=pdf.get_y(),w=28)
            try: os.remove(qp)
            except: pass
        except: pass
    pdf.ln(5); pdf.section("SIGNATURES",(80,80,80)); pdf.ln(2)
    pdf.set_font("Arial","",8)
    pdf.cell(95,5,"Signature: ___________________",0,0)
    pdf.cell(95,5,"Signature: ___________________",0,1)
    return pdf.output(dest='S').encode('latin-1')


# ============================================
#  CSS THEME
# ============================================
def apply_css():
    dm = st.session_state.get("dark_mode", True)
    rtl = st.session_state.get("lang") == "ar"
    d = "rtl" if rtl else "ltr"
    if dm:
        bg, cbg, tx, pr, mu = "#030614", "rgba(10,15,46,0.85)", "#e0e8ff", "#00f5ff", "#6b7fa0"
        ac, ac2, sbg = "#ff00ff", "#00ff88", "#020410"
        btn, brd, ibg = "linear-gradient(135deg,#00f5ff,#0066ff)", "rgba(0,245,255,0.15)", "rgba(10,15,46,0.6)"
        tmpl = "plotly_dark"
    else:
        bg, cbg, tx, pr, mu = "#f0f4f8", "rgba(255,255,255,0.95)", "#1a202c", "#0066ff", "#64748b"
        ac, ac2, sbg = "#9933ff", "#00cc66", "#f8fafc"
        btn, brd, ibg = "linear-gradient(135deg,#0066ff,#0044cc)", "rgba(0,100,255,0.15)", "rgba(255,255,255,0.9)"
        tmpl = "plotly_white"
    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;600&family=Tajawal:wght@400;500;700;800&display=swap');
    html{{direction:{d};}} .stApp{{background:{bg}!important;color:{tx}!important;}}
    section[data-testid="stSidebar"]{{background:{sbg}!important;}}
    section[data-testid="stSidebar"] *{{color:{tx}!important;}}
    .stApp p,.stApp span,.stApp label,.stApp div{{color:{tx}!important;}}
    .stApp h1,.stApp h2,.stApp h3,.stApp h4{{color:{tx}!important;}}
    .stTextInput>div>div>input,.stTextArea>div>div>textarea,.stNumberInput>div>div>input{{background:{ibg}!important;color:{tx}!important;border:1px solid {brd}!important;border-radius:10px!important;}}
    .dm-card{{background:{cbg};backdrop-filter:blur(15px);border:1px solid {brd};border-radius:16px;padding:24px;margin:12px 0;transition:all .3s ease;color:{tx}!important;}}
    .dm-card:hover{{transform:translateY(-2px);box-shadow:0 8px 32px rgba(0,0,0,0.15);}}
    .dm-card *{{color:{tx}!important;}}
    .dm-card-cyan{{border-left:3px solid {pr};}} .dm-card-green{{border-left:3px solid {ac2};}} .dm-card-red{{border-left:3px solid #ff0040;}}
    .dm-m{{background:{cbg};border:1px solid {brd};border-radius:16px;padding:18px 12px;text-align:center;}}
    .dm-m-i{{font-size:1.5rem;}} .dm-m-v{{font-size:1.7rem;font-weight:800;font-family:'JetBrains Mono',monospace!important;background:linear-gradient(135deg,{pr},{ac});-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
    .dm-m-l{{font-size:.68rem;font-weight:600;color:{mu}!important;-webkit-text-fill-color:{mu}!important;text-transform:uppercase;letter-spacing:.08em;margin-top:4px;}}
    div.stButton>button{{background:{btn}!important;color:white!important;border:none!important;border-radius:12px!important;padding:10px 24px!important;font-weight:600!important;transition:all .3s ease!important;}}
    div.stButton>button:hover{{transform:translateY(-2px)!important;box-shadow:0 6px 20px rgba(0,100,255,.3)!important;}}
    div.stButton>button *{{color:white!important;-webkit-text-fill-color:white!important;}}
    .dm-nt{{font-family:'Orbitron',sans-serif;font-weight:900;background:linear-gradient(135deg,{pr},{ac},{ac2});-webkit-background-clip:text;-webkit-text-fill-color:transparent;}}
    .dm-ch{{padding:12px 16px;border-radius:14px;margin:6px 0;max-width:85%;font-size:.9rem;}}
    .dm-cu{{background:{btn};color:white!important;margin-left:auto;}} .dm-cu *{{color:white!important;-webkit-text-fill-color:white!important;}}
    .dm-cb{{background:{cbg};border:1px solid {brd};}}
    h1{{font-family:'Orbitron',sans-serif!important;}}
    {"body,p,span,div,label{font-family:'Tajawal',sans-serif!important;}" if rtl else ""}
    .dm-logo{{text-align:center;padding:10px;background:{cbg};border-radius:20px;border:1px solid {brd};margin-bottom:10px;}}
    </style>""", unsafe_allow_html=True)
    return tmpl


tmpl = apply_css()


# ============================================
#  LOGO
# ============================================
def logo():
    st.markdown("""<div class="dm-logo">
    <svg width="70" height="70" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <defs><linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" style="stop-color:#00f5ff"/><stop offset="50%" style="stop-color:#ff00ff"/><stop offset="100%" style="stop-color:#00ff88"/></linearGradient>
    <filter id="gl"><feGaussianBlur stdDeviation="2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <circle cx="50" cy="50" r="45" fill="none" stroke="url(#g1)" stroke-width="2.5" filter="url(#gl)" opacity=".8"/>
    <circle cx="50" cy="50" r="38" fill="none" stroke="url(#g1)" stroke-width="1" opacity=".4"/>
    <path d="M35,25 C40,35 60,35 65,25" fill="none" stroke="#00f5ff" stroke-width="2" filter="url(#gl)"/>
    <path d="M35,35 C40,45 60,45 65,35" fill="none" stroke="#ff00ff" stroke-width="2" filter="url(#gl)"/>
    <path d="M35,45 C40,55 60,55 65,45" fill="none" stroke="#00ff88" stroke-width="2" filter="url(#gl)"/>
    <path d="M35,55 C40,65 60,65 65,55" fill="none" stroke="#00f5ff" stroke-width="2" filter="url(#gl)"/>
    <path d="M35,65 C40,75 60,75 65,65" fill="none" stroke="#ff00ff" stroke-width="2" filter="url(#gl)"/>
    <line x1="42" y1="30" x2="58" y2="30" stroke="#00f5ff" stroke-width="1.5" opacity=".6"/>
    <line x1="42" y1="40" x2="58" y2="40" stroke="#ff00ff" stroke-width="1.5" opacity=".6"/>
    <line x1="42" y1="50" x2="58" y2="50" stroke="#00ff88" stroke-width="1.5" opacity=".6"/>
    <line x1="42" y1="60" x2="58" y2="60" stroke="#00f5ff" stroke-width="1.5" opacity=".6"/>
    <line x1="42" y1="70" x2="58" y2="70" stroke="#ff00ff" stroke-width="1.5" opacity=".6"/>
    </svg>
    <h3 style="font-family:Orbitron,sans-serif;margin:4px 0;background:linear-gradient(135deg,#00f5ff,#ff00ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">DM SMART LAB AI</h3>
    <p style="font-size:.55rem;opacity:.4;letter-spacing:.3em;text-transform:uppercase;margin:0;">v7.5 Professional</p>
    </div>""", unsafe_allow_html=True)


with st.sidebar:
    logo()

# ============================================
#  LOGIN
# ============================================
if not st.session_state.logged_in:
    lc1, lc2, lc3 = st.columns([1, 2, 1])
    with lc2:
        ll = st.selectbox("🌍", ["🇫🇷 Français", "🇩🇿 العربية", "🇬🇧 English"], label_visibility="collapsed")
        st.session_state.lang = "fr" if "Français" in ll else ("ar" if "العربية" in ll else "en")
        logo()
        st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
        <div style='font-size:3rem;'>🔐</div><h2 class='dm-nt'>{t('login_title')}</h2>
        <p style='opacity:.5;'>{t('login_subtitle')}</p></div>""", unsafe_allow_html=True)
        with st.form("login"):
            u = st.text_input(f"👤 {t('username')}", placeholder="admin / dhia / demo")
            p = st.text_input(f"🔒 {t('password')}", type="password")
            if st.form_submit_button(f"🚀 {t('connect')}", use_container_width=True):
                if u.strip():
                    r = db_login(u.strip(), p)
                    if r is None: st.error("❌ User not found")
                    elif isinstance(r, dict) and "error" in r:
                        if r["error"] == "locked": st.error("🔒 Locked")
                        else: st.error(f"❌ Wrong password. {r.get('left',0)} left")
                    else:
                        for k in ["logged_in", "user_id", "user_name", "user_role", "user_full_name"]:
                            st.session_state[k] = {"logged_in": True, "user_id": r["id"], "user_name": r["username"],
                                                    "user_role": r["role"], "user_full_name": r["full_name"]}[k]
                        db_log(r["id"], r["username"], "Login"); st.rerun()
        st.markdown("<div style='text-align:center;opacity:.4;font-size:.75rem;'>👑 admin/admin2026 | 🔬 dhia/dhia2026 | 👁️ demo/demo123</div>", unsafe_allow_html=True)
    st.stop()

# ============================================
#  SIDEBAR
# ============================================
with st.sidebar:
    ri = ROLES.get(st.session_state.user_role, ROLES["viewer"])
    st.markdown(f"{ri['icon']} **{st.session_state.user_full_name}**")
    st.caption(f"@{st.session_state.user_name} - {tl(ri['label'])}")
    tips = TIPS.get(st.session_state.lang, TIPS["fr"])
    st.info(f"**{t('daily_tip')}:**\n\n{tips[datetime.now().timetuple().tm_yday % len(tips)]}")
    st.markdown("---")
    st.markdown(f"#### 🌍 {t('language')}")
    lc = st.radio("", ["🇫🇷 Français", "🇩🇿 العربية", "🇬🇧 English"], label_visibility="collapsed",
                  index=["fr", "ar", "en"].index(st.session_state.lang))
    nl = "fr" if "Français" in lc else ("ar" if "العربية" in lc else "en")
    if nl != st.session_state.lang: st.session_state.lang = nl; st.rerun()
    st.markdown("---")
    navs = [f"🏠 {t('home')}", f"🔬 {t('scan')}", f"📘 {t('encyclopedia')}", f"📊 {t('dashboard')}",
            f"🧠 {t('quiz')}", f"💬 {t('chatbot')}", f"🔄 {t('compare')}"]
    keys = ["home", "scan", "enc", "dash", "quiz", "chat", "cmp"]
    if has_role(3): navs.append(f"⚙️ {t('admin')}"); keys.append("admin")
    navs.append(f"ℹ️ {t('about')}"); keys.append("about")
    menu = st.radio("Nav", navs, label_visibility="collapsed")
    st.markdown("---")
    dk = st.toggle(f"🌙 {t('dark_mode')}", value=st.session_state.dark_mode)
    if dk != st.session_state.dark_mode: st.session_state.dark_mode = dk; st.rerun()
    st.markdown("---")
    if st.button(f"🚪 {t('logout')}", use_container_width=True):
        db_log(st.session_state.user_id, st.session_state.user_name, "Logout")
        for k in DEFAULTS: st.session_state[k] = DEFAULTS[k]
        st.rerun()

pg = dict(zip(navs, keys)).get(menu, "home")

# ════════════════════════════════════════════
#  PAGE: HOME
# ════════════════════════════════════════════
if pg == "home":
    st.title(f"👋 {get_greeting()}, {st.session_state.user_full_name}!")
    st.markdown(f"<div class='dm-card dm-card-cyan'><h3 class='dm-nt'>DM SMART LAB AI — {t('where_science')}</h3><p style='opacity:.6;'>{t('system_desc')}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    w1, w2, w3 = st.columns([2, 2, 1])
    with w1:
        if st.button(t("welcome_btn"), use_container_width=True, type="primary"):
            speak_js(t("voice_welcome"))
    with w2:
        if st.button(t("intro_btn"), use_container_width=True, type="primary"):
            speak_js(t("voice_intro"))
    with w3:
        if st.button(t("stop_voice"), use_container_width=True): stop_js()
    st.markdown("---")
    st.markdown(f"### 📊 {t('quick_overview')}")
    s = db_stats(st.session_state.user_id)
    for col, (ic, v, lb) in zip(st.columns(4), [("🔬", s["total"], t("total_analyses")), ("✅", s["reliable"], t("reliable")), ("⚠️", s["verify"], t("to_verify")), ("🦠", s["top"], t("most_frequent"))]):
        with col:
            st.markdown(f"<div class='dm-m'><span class='dm-m-i'>{ic}</span><div class='dm-m-v'>{v}</div><div class='dm-m-l'>{lb}</div></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════
#  PAGE: SCAN
# ════════════════════════════════════════════
elif pg == "scan":
    st.title(f"🔬 {t('scan')}")
    mdl, mn, mt = load_model()
    if mn: st.sidebar.success(f"🧠 {mn}")
    else: st.sidebar.info(f"🧠 {t('demo_mode')}")
    st.markdown(f"### 📋 1. {t('patient_info')}")
    ca, cb = st.columns(2)
    pn = ca.text_input(f"{t('patient_name')} *"); pf = cb.text_input(t("patient_firstname"))
    c1, c2, c3, c4 = st.columns(4)
    pa = c1.number_input(t("age"), 0, 120, 30); ps = c2.selectbox(t("sex"), [t("male"), t("female")])
    pw = c3.number_input(t("weight"), 0, 300, 70); pst = c4.selectbox(t("sample_type"), SAMPLES.get(st.session_state.lang, SAMPLES["fr"]))
    st.markdown(f"### 🔬 2. {t('lab_info')}")
    la, lb2, lc = st.columns(3)
    t1 = la.text_input(f"{t('technician')} 1", value=st.session_state.user_full_name)
    t2 = lb2.text_input(f"{t('technician')} 2"); lm = lc.selectbox(t("microscope"), MICROSCOPE_TYPES)
    ld, le = st.columns(2)
    mg = ld.selectbox(t("magnification"), MAGNIFICATIONS, index=3); pt = le.selectbox(t("preparation"), PREPARATION_TYPES)
    nt = st.text_area(t("notes"), height=80)
    st.markdown("---")
    st.markdown(f"### 📸 3. {t('image_capture')}")
    src = st.radio("", [t("take_photo"), t("upload_file")], horizontal=True, label_visibility="collapsed")
    img = None; ih = None
    if t("take_photo") in src:
        st.info(f"📷 {t('camera_hint')}")
        cp = st.camera_input(t("take_photo"))
        if cp: img = Image.open(cp).convert("RGB"); ih = hashlib.md5(cp.getvalue()).hexdigest()
    else:
        uf = st.file_uploader(t("upload_file"), type=["jpg", "jpeg", "png", "bmp", "tiff"])
        if uf: img = Image.open(uf).convert("RGB"); ih = hashlib.md5(uf.getvalue()).hexdigest()
    if img:
        if not pn.strip(): st.error(t("name_required")); st.stop()
        if st.session_state.get("_ih") != ih:
            st.session_state._ih = ih; st.session_state.demo_seed = random.randint(0, 999999); st.session_state.heatmap_seed = random.randint(0, 999999)
        ci, cr = st.columns(2)
        with ci:
            with st.expander("🎛️ Zoom/Adjust"):
                z = st.slider("Zoom", 1.0, 5.0, 1.0, .25); br = st.slider("Brightness", .5, 2.0, 1.0, .1)
                co = st.slider("Contrast", .5, 2.0, 1.0, .1); sa = st.slider("Saturation", .0, 2.0, 1.0, .1)
            adj = adjust(img, br, co, sa)
            if z > 1: adj = zoom(adj, z)
            tabs = st.tabs(["📷 Original", "🔥 Thermal", "📐 Edges", "✨ Enhanced", "🔄 Negative", "🏔️ Emboss", "🎯 Heatmap", "📊 Histogram"])
            with tabs[0]: st.image(adj, use_container_width=True)
            with tabs[1]: st.image(thermal(adj), use_container_width=True)
            with tabs[2]: st.image(edges(adj), use_container_width=True)
            with tabs[3]: st.image(enhanced(adj), use_container_width=True)
            with tabs[4]: st.image(negative(adj), use_container_width=True)
            with tabs[5]: st.image(emboss(adj), use_container_width=True)
            with tabs[6]: st.image(gen_heatmap(img, st.session_state.heatmap_seed), use_container_width=True)
            with tabs[7]:
                hd = histogram(adj)
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=hd["red"], name="R", line=dict(color="red", width=1)))
                    fig.add_trace(go.Scatter(y=hd["green"], name="G", line=dict(color="green", width=1)))
                    fig.add_trace(go.Scatter(y=hd["blue"], name="B", line=dict(color="blue", width=1)))
                    fig.update_layout(height=250, template=tmpl, margin=dict(l=20, r=20, t=20, b=20))
                    st.plotly_chart(fig, use_container_width=True)
        with cr:
            st.markdown(f"### 🧠 {t('result')}")
            with st.spinner("⏳"):
                pg2 = st.progress(0)
                for i in range(100): time.sleep(.004); pg2.progress(i + 1)
                res = predict(mdl, mt, img, st.session_state.demo_seed)
            lb = res["label"]; cf = res["conf"]; rc = risk_color(res["risk"])
            info = PARASITE_DB.get(lb, PARASITE_DB["Negative"])
            if not res["rel"]: st.warning(t("low_conf_warn"))
            if res["demo"]: st.info(t("demo_mode"))
            st.markdown(f"""<div class='dm-card' style='border-left:4px solid {rc};'>
            <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
            <div><h2 style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;margin:0;font-family:Orbitron;'>{lb}</h2>
            <p style='opacity:.4;font-style:italic;'>{info['sci']}</p></div>
            <div style='text-align:center;'><div style='font-size:2.5rem;font-weight:900;font-family:JetBrains Mono;color:{rc}!important;-webkit-text-fill-color:{rc}!important;'>{cf}%</div>
            <div style='font-size:.7rem;opacity:.4;'>{t("confidence")}</div></div></div>
            <hr style='opacity:.1;margin:14px 0;'>
            <p><b>🔬 {t("morphology")}:</b><br>{tl(info['morph'])}</p>
            <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-weight:700;'>{tl(info['risk_d'])}</span></p>
            <div style='background:rgba(0,255,136,.06);padding:12px;border-radius:10px;margin:10px 0;'><b>💡 {t("advice")}:</b><br>{tl(info['advice'])}</div>
            <div style='background:rgba(0,100,255,.06);padding:12px;border-radius:10px;font-style:italic;'>🤖 {tl(info['funny'])}</div>
            </div>""", unsafe_allow_html=True)
            vc1, vc2 = st.columns(2)
            with vc1:
                if st.button(t("listen"), use_container_width=True): speak_js(f"{lb}. {tl(info['funny'])}")
            with vc2:
                if st.button(t("stop_voice"), key="sv2", use_container_width=True): stop_js()
            if info.get("tests"):
                with st.expander(f"🩺 {t('extra_tests')}"): [st.markdown(f"• {x}") for x in info["tests"]]
            dk = tl(info.get("keys", {}))
            if dk and dk not in ["N/A", "غير متوفر"]:
                with st.expander(f"🔑 {t('diagnostic_keys')}"): st.markdown(dk)
            cy = tl(info.get("cycle", {}))
            if cy and cy not in ["N/A", "غير متوفر"]:
                with st.expander(f"🔄 {t('lifecycle')}"): st.markdown(f"**{cy}**")
            if res["preds"]:
                with st.expander(f"📊 {t('all_probabilities')}"):
                    if HAS_PLOTLY:
                        sp = dict(sorted(res["preds"].items(), key=lambda x: x[1], reverse=True))
                        fig = px.bar(x=list(sp.values()), y=list(sp.keys()), orientation='h', color=list(sp.values()), color_continuous_scale='RdYlGn_r')
                        fig.update_layout(height=220, template=tmpl, margin=dict(l=20, r=20, t=10, b=20), showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")
        a1, a2, a3 = st.columns(3)
        with a1:
            try:
                pdf = make_pdf({"Nom": pn, "Prenom": pf, "Age": str(pa), "Sexe": ps, "Poids": str(pw), "Echantillon": pst},
                               {"Microscope": lm, "Grossissement": mg, "Preparation": pt, "Tech1": t1, "Tech2": t2, "Notes": nt}, res, lb)
                st.download_button(t("download_pdf"), pdf, f"Rapport_{pn}_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", use_container_width=True)
            except: pass
        with a2:
            if has_role(2) and st.button(t("save_db"), use_container_width=True):
                aid = db_save_analysis(st.session_state.user_id, {"pn": pn, "pf": pf, "pa": pa, "ps": ps, "pw": pw,
                    "st": pst, "mt": lm, "mg": mg, "pt": pt, "t1": t1, "t2": t2, "nt": nt,
                    "label": lb, "conf": cf, "risk": res["risk"], "rel": 1 if res["rel"] else 0,
                    "preds": res["preds"], "hash": ih, "demo": 1 if res["demo"] else 0})
                db_log(st.session_state.user_id, st.session_state.user_name, "Analysis", f"ID:{aid}"); st.success(t("saved_ok"))
        with a3:
            if st.button(t("new_analysis"), use_container_width=True):
                st.session_state.demo_seed = None; st.session_state._ih = None; st.rerun()

# ════════════════════════════════════════════
#  PAGE: ENCYCLOPEDIA
# ════════════════════════════════════════════
elif pg == "enc":
    st.title(f"📘 {t('encyclopedia')}")
    sr = st.text_input(f"🔍 {t('search')}"); st.markdown("---")
    found = False
    for nm, d in PARASITE_DB.items():
        if nm == "Negative": continue
        if sr.strip() and sr.lower() not in (nm + " " + d["sci"]).lower(): continue
        found = True; rc = risk_color(d["risk"])
        with st.expander(f"{d['icon']} {nm} — *{d['sci']}* | {tl(d['risk_d'])}", expanded=not sr.strip()):
            ci, cv = st.columns([2.5, 1])
            with ci:
                st.markdown(f"""<div class='dm-card' style='border-left:3px solid {rc};'>
                <h4 style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-family:Orbitron;'>{d['sci']}</h4>
                <p><b>🔬 {t("morphology")}:</b><br>{tl(d['morph'])}</p>
                <p><b>📖 {t("description")}:</b><br>{tl(d['desc'])}</p>
                <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-weight:700;'>{tl(d['risk_d'])}</span></p>
                <div style='background:rgba(0,255,136,.06);padding:12px;border-radius:10px;margin:8px 0;'><b>💡:</b> {tl(d['advice'])}</div>
                <div style='background:rgba(0,100,255,.06);padding:12px;border-radius:10px;font-style:italic;'>🤖 {tl(d['funny'])}</div>
                </div>""", unsafe_allow_html=True)
                cy = tl(d.get("cycle", {}))
                if cy and cy not in ["N/A", "غير متوفر"]: st.markdown(f"**🔄 {t('lifecycle')}:** {cy}")
                dk = tl(d.get("keys", {}))
                if dk: st.markdown(f"**🔑 {t('diagnostic_keys')}:**\n{dk}")
                if d.get("tests"): st.markdown(f"**🩺 {t('extra_tests')}:** {', '.join(d['tests'])}")
            with cv:
                rp = risk_pct(d["risk"])
                if rp > 0: st.progress(rp / 100, text=f"{rp}%")
                st.markdown(f'<div style="text-align:center;font-size:4rem;">{d["icon"]}</div>', unsafe_allow_html=True)
                if st.button(t("listen"), key=f"ev_{nm}"): speak_js(f"{nm}. {tl(d['desc'])}")
    if sr.strip() and not found: st.warning(t("no_results"))

# ════════════════════════════════════════════
#  PAGE: DASHBOARD
# ════════════════════════════════════════════
elif pg == "dash":
    st.title(f"📊 {t('dashboard')}")
    s = db_stats() if has_role(3) else db_stats(st.session_state.user_id)
    an = db_analyses() if has_role(3) else db_analyses(st.session_state.user_id)
    for col, (ic, v, lb) in zip(st.columns(5), [("🔬", s["total"], t("total_analyses")), ("✅", s["reliable"], t("reliable")), ("⚠️", s["verify"], t("to_verify")), ("🦠", s["top"], t("most_frequent")), ("📈", f"{s['avg']}%", t("avg_confidence"))]):
        with col: st.markdown(f"<div class='dm-m'><span class='dm-m-i'>{ic}</span><div class='dm-m-v'>{v}</div><div class='dm-m-l'>{lb}</div></div>", unsafe_allow_html=True)
    if s["total"] > 0:
        df = pd.DataFrame(an); st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"#### {t('parasite_distribution')}")
            if HAS_PLOTLY and "parasite_detected" in df.columns:
                pc = df["parasite_detected"].value_counts()
                fig = px.pie(values=pc.values, names=pc.index, hole=.4)
                fig.update_layout(height=350, template=tmpl, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.markdown(f"#### {t('confidence_levels')}")
            if HAS_PLOTLY and "confidence" in df.columns:
                fig = px.histogram(df, x="confidence", nbins=20, color_discrete_sequence=["#00f5ff"])
                fig.update_layout(height=350, template=tmpl, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
        tr = db_trends(30)
        if tr and HAS_PLOTLY:
            st.markdown(f"#### {t('trends')}")
            fig = px.line(pd.DataFrame(tr), x="day", y="count", color="parasite_detected", markers=True)
            fig.update_layout(height=300, template=tmpl, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"### 📋 {t('history')}")
        dc = [c for c in ["id", "analysis_date", "patient_name", "parasite_detected", "confidence", "risk_level", "analyst", "validated"] if c in df.columns]
        st.dataframe(df[dc] if dc else df, use_container_width=True)
        if has_role(2) and "validated" in df.columns:
            uv = df[df["validated"] == 0]
            if not uv.empty:
                vi = st.selectbox("ID:", uv["id"].tolist())
                if st.button(f"✅ {t('validate')} #{vi}"):
                    db_validate(vi, st.session_state.user_full_name); st.success(f"✅ #{vi}"); st.rerun()
        st.markdown("---")
        e1, e2 = st.columns(2)
        with e1: st.download_button(t("export_csv"), df.to_csv(index=False).encode('utf-8-sig'), "data.csv", "text/csv", use_container_width=True)
        with e2: st.download_button(t("export_json"), df.to_json(orient='records', force_ascii=False).encode(), "data.json", "application/json", use_container_width=True)
# ════════════════════════════════════════════
#  PAGE: QUIZ (Enhanced)
# ════════════════════════════════════════════
elif pg == "quiz":
    st.title(f"🧠 {t('quiz')}")
    qs = st.session_state.quiz_state

    with st.expander(t("leaderboard")):
        lb = db_leaderboard()
        if lb:
            for i, e in enumerate(lb[:10]):
                md = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"{md} **{e['username']}** — {e['score']}/{e['total_questions']} ({e['percentage']:.0f}%)")
        else:
            st.info(t("no_data"))

    if not qs["active"]:
        st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
        <div style='font-size:3rem;'>🧠</div>
        <h3>{"fr":"Testez vos connaissances en parasitologie !","ar":"اختبر معارفك في علم الطفيليات!","en":"Test your parasitology knowledge!"}.get(st.session_state.lang,"")</h3>
        <p style='opacity:.6;'>{"fr":f"{len(QUIZ_QUESTIONS)} questions disponibles","ar":f"{len(QUIZ_QUESTIONS)} سؤال متاح","en":f"{len(QUIZ_QUESTIONS)} questions available"}.get(st.session_state.lang,"")</p>
        </div>""", unsafe_allow_html=True)
        # Quiz settings
        st.markdown("---")
        qc1, qc2 = st.columns(2)
        with qc1:
            n_questions = st.slider(
                {"fr": "Nombre de questions:", "ar": "عدد الأسئلة:", "en": "Number of questions:"}.get(st.session_state.lang, ""),
                5, min(25, len(QUIZ_QUESTIONS)), 15
            )
        with qc2:
            cats = list(set(q.get("cat", "General") for q in QUIZ_QUESTIONS))
            cats.insert(0, {"fr": "Toutes les catégories", "ar": "جميع الفئات", "en": "All categories"}.get(st.session_state.lang, "All"))
            chosen_cat = st.selectbox(
                {"fr": "Catégorie:", "ar": "الفئة:", "en": "Category:"}.get(st.session_state.lang, ""),
                cats
            )

        if st.button(t("start_quiz"), use_container_width=True, type="primary"):
            # Filter by category
            if chosen_cat in [cats[0]]:
                pool = list(range(len(QUIZ_QUESTIONS)))
            else:
                pool = [i for i, q in enumerate(QUIZ_QUESTIONS) if q.get("cat") == chosen_cat]
            random.shuffle(pool)
            st.session_state.quiz_state = {
                "current": 0, "score": 0, "answered": [],
                "active": True, "order": pool[:min(n_questions, len(pool))],
                "wrong": []
            }
            db_log(st.session_state.user_id, st.session_state.user_name, "Quiz started",
                   f"n={n_questions} cat={chosen_cat}")
            st.rerun()
    else:
        idx = qs["current"]
        order = qs.get("order", list(range(len(QUIZ_QUESTIONS))))

        if idx < len(order):
            qi = order[idx]
            q = QUIZ_QUESTIONS[qi]
            total_q = len(order)

            # Progress bar
            st.progress(idx / total_q)
            st.markdown(f"### {'سؤال' if st.session_state.lang=='ar' else 'Question'} {idx + 1}/{total_q}")

            cat = q.get("cat", "")
            if cat:
                st.caption(f"📂 {cat}")

            q_text = tl(q["q"])
            st.markdown(f"<div class='dm-card'><h4>{q_text}</h4></div>", unsafe_allow_html=True)

            akey = f"qa_{idx}"
            if akey not in st.session_state:
                # Show options
                cols = st.columns(2)
                for i, opt in enumerate(q["opts"]):
                    with cols[i % 2]:
                        if st.button(f"{'ABCD'[i]}. {opt}", key=f"qo_{idx}_{i}", use_container_width=True):
                            correct = (i == q["ans"])
                            if correct:
                                st.session_state.quiz_state["score"] += 1
                            else:
                                st.session_state.quiz_state.setdefault("wrong", []).append({
                                    "q": q_text, "your": opt, "correct": q["opts"][q["ans"]]
                                })
                            st.session_state.quiz_state["answered"].append(correct)
                            st.session_state[akey] = {"correct": correct, "selected": i}
                            st.rerun()
            else:
                ad = st.session_state[akey]
                if ad["correct"]:
                    st.success(f"✅ {'صحيح!' if st.session_state.lang=='ar' else 'Correct!' if st.session_state.lang=='en' else 'Bonne réponse !'}")
                else:
                    correct_ans = q["opts"][q["ans"]]
                    st.error(f"❌ {'الإجابة الصحيحة' if st.session_state.lang=='ar' else 'Correct answer' if st.session_state.lang=='en' else 'Réponse correcte'}: **{correct_ans}**")

                expl = tl(q.get("expl", {}))
                if expl:
                    st.info(f"📖 {expl}")

                # Show correct option highlighted
                for i, opt in enumerate(q["opts"]):
                    if i == q["ans"]:
                        st.markdown(f"✅ **{opt}**")
                    elif i == ad["selected"] and not ad["correct"]:
                        st.markdown(f"❌ ~~{opt}~~")

                if st.button(t("next_question"), use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1
                    st.rerun()
        else:
            # Quiz finished - show results
            score = qs["score"]
            total_q = len(order)
            pct = int(score / total_q * 100) if total_q > 0 else 0

            if pct >= 80:
                emoji, msg = "🏆", t("score_excellent")
            elif pct >= 60:
                emoji, msg = "👍", t("score_good")
            elif pct >= 40:
                emoji, msg = "📚", t("score_average")
            else:
                emoji, msg = "💪", t("score_low")

            st.markdown(f"""<div class='dm-card dm-card-green' style='text-align:center;'>
            <div style='font-size:5rem;'>{emoji}</div>
            <h2>{t('result')}</h2>
            <div class='dm-nt' style='font-size:3.5rem;'>{score}/{total_q}</div>
            <p style='font-size:1.3rem;'>{pct}%</p>
            <p style='font-size:1rem;opacity:.8;'>{msg}</p>
            </div>""", unsafe_allow_html=True)

            # Save score
            db_quiz_save(st.session_state.user_id, st.session_state.user_name, score, total_q, pct)
            db_log(st.session_state.user_id, st.session_state.user_name, "Quiz done", f"{score}/{total_q}={pct}%")

            # Performance breakdown
            if HAS_PLOTLY and total_q > 0:
                st.markdown("---")
                st.markdown(f"### 📊 {'التحليل' if st.session_state.lang=='ar' else 'Analysis' if st.session_state.lang=='en' else 'Analyse des résultats'}")
                fig = go.Figure(data=[go.Pie(
                    labels=[{"fr": "Correctes", "ar": "صحيحة", "en": "Correct"}.get(st.session_state.lang, ""),
                            {"fr": "Incorrectes", "ar": "خاطئة", "en": "Incorrect"}.get(st.session_state.lang, "")],
                    values=[score, total_q - score],
                    marker_colors=["#00ff88", "#ff0040"],
                    hole=0.5
                )])
                fig.update_layout(height=250, template=tmpl, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

            # Show wrong answers for review
            wrong = qs.get("wrong", [])
            if wrong:
                with st.expander(f"❌ {'الأخطاء' if st.session_state.lang=='ar' else 'Mistakes' if st.session_state.lang=='en' else 'Erreurs à revoir'} ({len(wrong)})"):
                    for i, w in enumerate(wrong):
                        st.markdown(f"""
                        **{i+1}. {w['q']}**
                        - ❌ {'إجابتك' if st.session_state.lang=='ar' else 'Your answer' if st.session_state.lang=='en' else 'Votre réponse'}: ~~{w['your']}~~
                        - ✅ {'الصحيحة' if st.session_state.lang=='ar' else 'Correct' if st.session_state.lang=='en' else 'Correcte'}: **{w['correct']}**
                        ---""")

            st.markdown("---")
            if st.button(t("restart"), use_container_width=True, type="primary"):
                for key in list(st.session_state.keys()):
                    if key.startswith("qa_"):
                        del st.session_state[key]
                st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": False}
                st.rerun()


# ════════════════════════════════════════════
#  PAGE: CHATBOT (DM Bot - Enhanced)
# ════════════════════════════════════════════
elif pg == "chat":
    st.title(f"💬 DM Bot")
    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <p>{{"fr":"Assistant médical intelligent spécialisé en parasitologie",
    "ar":"مساعد طبي ذكي متخصص في علم الطفيليات",
    "en":"Intelligent medical assistant specialized in parasitology"}.get(st.session_state.lang,"")}</p>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "bot", "msg": t("chat_welcome")})

    # Chat container
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='dm-ch dm-cu'>👤 {msg['msg']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='dm-ch dm-cb'>🤖 {msg['msg']}</div>", unsafe_allow_html=True)

    # Input
    user_msg = st.chat_input(t("chat_placeholder"))
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "msg": user_msg})
        reply = chatbot_reply(user_msg)
        st.session_state.chat_history.append({"role": "bot", "msg": reply})
        db_log(st.session_state.user_id, st.session_state.user_name, "Chat", user_msg[:100])
        st.rerun()

    # Quick questions
    st.markdown("---")
    st.markdown(f"**{t('quick_questions')}**")

    # Row 1 - Parasites
    qr1 = st.columns(7)
    quick1 = ["Amoeba", "Giardia", "Plasmodium", "Leishmania", "Trypanosoma", "Schistosoma", "Toxoplasma"]
    for col, q in zip(qr1, quick1):
        with col:
            if st.button(q, key=f"cq1_{q}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(q)})
                st.rerun()

    # Row 2 - More parasites + Techniques
    qr2 = st.columns(7)
    quick2 = ["Ascaris", "Taenia", "Oxyure", "Cryptosporidium", "Microscope", "Coloration", "Concentration"]
    for col, q in zip(qr2, quick2):
        with col:
            if st.button(q, key=f"cq2_{q}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(q)})
                st.rerun()

    # Row 3 - Topics
    qr3 = st.columns(5)
    quick3_labels = {
        "fr": ["Traitement", "Hygiène", "Selle (EPS)", "Aide", "🗑️ Effacer"],
        "ar": ["علاج", "نظافة", "فحص البراز", "مساعدة", "🗑️ مسح"],
        "en": ["Treatment", "Hygiene", "Stool Exam", "Help", "🗑️ Clear"]
    }
    quick3_keys = ["traitement", "hygiene", "selle", "aide", "_clear"]
    q3_labels = quick3_labels.get(st.session_state.lang, quick3_labels["fr"])

    for col, (label, key) in zip(qr3, zip(q3_labels, quick3_keys)):
        with col:
            if st.button(label, key=f"cq3_{key}", use_container_width=True):
                if key == "_clear":
                    st.session_state.chat_history = []
                    st.rerun()
                else:
                    st.session_state.chat_history.append({"role": "user", "msg": label})
                    st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(key)})
                    st.rerun()


# ════════════════════════════════════════════
#  PAGE: COMPARISON (Enhanced)
# ════════════════════════════════════════════
elif pg == "cmp":
    st.title(f"🔄 {t('compare')}")
    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <p>{{"fr":"Comparez deux images microscopiques avec analyse avancée",
    "ar":"قارن بين صورتين مجهريتين بتحليل متقدم",
    "en":"Compare two microscopic images with advanced analysis"}.get(st.session_state.lang,"")}</p>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 📷 {t('image1')}")
        f1 = st.file_uploader(t("image1"), type=["jpg", "jpeg", "png", "bmp"], key="cmp1")
    with c2:
        st.markdown(f"### 📷 {t('image2')}")
        f2 = st.file_uploader(t("image2"), type=["jpg", "jpeg", "png", "bmp"], key="cmp2")

    if f1 and f2:
        i1 = Image.open(f1).convert("RGB")
        i2 = Image.open(f2).convert("RGB")

        c1, c2 = st.columns(2)
        with c1:
            st.image(i1, caption=t("image1"), use_container_width=True)
        with c2:
            st.image(i2, caption=t("image2"), use_container_width=True)

        st.markdown("---")
        if st.button(t("compare_btn"), use_container_width=True, type="primary"):
            with st.spinner("🔄 ..."):
                metrics = compare_imgs(i1, i2)

            # Metrics
            st.markdown(f"### 📊 {{'fr':'Résultats de la comparaison','ar':'نتائج المقارنة','en':'Comparison Results'}.get(st.session_state.lang,'')}")
            mc = st.columns(4)
            with mc[0]:
                st.markdown(f"<div class='dm-m'><span class='dm-m-i'>📊</span><div class='dm-m-v'>{metrics['sim']}%</div><div class='dm-m-l'>{t('similarity')}</div></div>", unsafe_allow_html=True)
            with mc[1]:
                st.markdown(f"<div class='dm-m'><span class='dm-m-i'>🎯</span><div class='dm-m-v'>{metrics['ssim']}</div><div class='dm-m-l'>SSIM</div></div>", unsafe_allow_html=True)
            with mc[2]:
                st.markdown(f"<div class='dm-m'><span class='dm-m-i'>📐</span><div class='dm-m-v'>{metrics['mse']}</div><div class='dm-m-l'>MSE</div></div>", unsafe_allow_html=True)
            with mc[3]:
                # Similarity verdict
                if metrics["sim"] > 90:
                    verdict = {"fr": "Très similaires ✅", "ar": "متشابهتان جداً ✅", "en": "Very similar ✅"}
                elif metrics["sim"] > 70:
                    verdict = {"fr": "Similaires 🟡", "ar": "متشابهتان 🟡", "en": "Similar 🟡"}
                elif metrics["sim"] > 50:
                    verdict = {"fr": "Peu similaires 🟠", "ar": "قليل التشابه 🟠", "en": "Somewhat similar 🟠"}
                else:
                    verdict = {"fr": "Très différentes 🔴", "ar": "مختلفتان جداً 🔴", "en": "Very different 🔴"}
                st.markdown(f"<div class='dm-m'><span class='dm-m-i'>🔍</span><div class='dm-m-v' style='font-size:1rem;'>{tl(verdict)}</div><div class='dm-m-l'>Verdict</div></div>", unsafe_allow_html=True)

            # SSIM gauge
            if HAS_PLOTLY:
                st.markdown("---")
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=metrics["sim"],
                    title={"text": t("similarity")},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#00f5ff"},
                        "steps": [
                            {"range": [0, 30], "color": "#ff0040"},
                            {"range": [30, 60], "color": "#ff9500"},
                            {"range": [60, 80], "color": "#ffff00"},
                            {"range": [80, 100], "color": "#00ff88"}
                        ],
                        "threshold": {"line": {"color": "white", "width": 4}, "thickness": 0.75, "value": metrics["sim"]}
                    }
                ))
                fig.update_layout(height=250, template=tmpl, margin=dict(l=30, r=30, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)

            # Pixel difference
            st.markdown(f"### 🔍 {t('pixel_diff')}")
            diff_img = pixel_diff(i1, i2)
            dc1, dc2, dc3 = st.columns(3)
            with dc1:
                st.image(i1, caption=t("image1"), use_container_width=True)
            with dc2:
                st.image(diff_img, caption=t("pixel_diff"), use_container_width=True)
            with dc3:
                st.image(i2, caption=t("image2"), use_container_width=True)

            # Filter comparison
            st.markdown(f"### 🔬 {t('filter_comparison')}")
            filters = [
                ({"fr": "Thermique", "ar": "حراري", "en": "Thermal"}, thermal),
                ({"fr": "Contours", "ar": "حواف", "en": "Edges"}, edges),
                ({"fr": "Contraste+", "ar": "تباين+", "en": "Enhanced"}, enhanced),
                ({"fr": "Négatif", "ar": "سلبي", "en": "Negative"}, negative),
                ({"fr": "Relief", "ar": "نقش", "en": "Emboss"}, emboss),
            ]
            for fname, ffunc in filters:
                fc1, fc2 = st.columns(2)
                fn = tl(fname)
                with fc1:
                    st.image(ffunc(i1), caption=f"{t('image1')} - {fn}", use_container_width=True)
                with fc2:
                    st.image(ffunc(i2), caption=f"{t('image2')} - {fn}", use_container_width=True)

            # Histogram comparison
            if HAS_PLOTLY:
                st.markdown(f"### 📊 {{'fr':'Comparaison des histogrammes','ar':'مقارنة المدرجات التكرارية','en':'Histogram Comparison'}.get(st.session_state.lang,'')}")
                h1 = histogram(i1)
                h2 = histogram(i2)
                hc1, hc2 = st.columns(2)
                with hc1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=h1["red"], name="R", line=dict(color="red", width=1)))
                    fig.add_trace(go.Scatter(y=h1["green"], name="G", line=dict(color="green", width=1)))
                    fig.add_trace(go.Scatter(y=h1["blue"], name="B", line=dict(color="blue", width=1)))
                    fig.update_layout(title=t("image1"), height=250, template=tmpl, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                with hc2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=h2["red"], name="R", line=dict(color="red", width=1)))
                    fig.add_trace(go.Scatter(y=h2["green"], name="G", line=dict(color="green", width=1)))
                    fig.add_trace(go.Scatter(y=h2["blue"], name="B", line=dict(color="blue", width=1)))
                    fig.update_layout(title=t("image2"), height=250, template=tmpl, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════
#  PAGE: ADMIN
# ════════════════════════════════════════════
elif pg == "admin":
    st.title(f"⚙️ {t('admin')}")
    if not has_role(3):
        st.error("🔒 Admin only"); st.stop()

    tab1, tab2, tab3 = st.tabs([f"👥 {t('users_mgmt')}", f"📜 {t('activity_log')}", f"🖥️ {t('system_info')}"])

    with tab1:
        users = db_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
            st.markdown("---")
            tc1, tc2, tc3 = st.columns(3)
            uid = tc1.number_input("User ID", min_value=1, step=1)
            act = tc2.selectbox("Status", ["Active", "Disabled"])
            if tc3.button("Apply", use_container_width=True):
                db_toggle(uid, act == "Active")
                db_log(st.session_state.user_id, st.session_state.user_name, "Toggle user", f"#{uid}={act}")
                st.success(f"✅ #{uid} → {act}"); st.rerun()

        st.markdown("---")
        st.markdown(f"### ➕ {t('create_user')}")
        with st.form("new_user"):
            nu = st.text_input(f"{t('username')} *")
            np2 = st.text_input(f"{t('password')} *", type="password")
            nf = st.text_input("Full Name *")
            nr = st.selectbox("Role", list(ROLES.keys()))
            ns = st.text_input("Speciality", "Laboratoire")
            if st.form_submit_button(t("create_user"), use_container_width=True):
                if nu and np2 and nf:
                    if db_create_user(nu, np2, nf, nr, ns):
                        db_log(st.session_state.user_id, st.session_state.user_name, "Created user", nu)
                        st.success(f"✅ {nu}"); st.rerun()
                    else:
                        st.error("❌ Username exists")
                else:
                    st.error("❌ Fill all fields")

        st.markdown("---")
        st.markdown(f"### 🔑 {t('change_pwd')}")
        cp1, cp2 = st.columns(2)
        cpid = cp1.number_input("User ID", min_value=1, step=1, key="cpid")
        cpnew = cp2.text_input("New Password", type="password", key="cpnew")
        if st.button(t("change_pwd")):
            if cpnew:
                db_chpw(cpid, cpnew)
                db_log(st.session_state.user_id, st.session_state.user_name, "Changed pwd", f"#{cpid}")
                st.success(f"✅ #{cpid}")

    with tab2:
        logs = db_logs(300)
        if logs:
            ldf = pd.DataFrame(logs)
            if "username" in ldf.columns:
                flt = st.selectbox("Filter:", ["All"] + sorted(ldf["username"].dropna().unique().tolist()))
                if flt != "All": ldf = ldf[ldf["username"] == flt]
            st.dataframe(ldf, use_container_width=True)
        else:
            st.info(t("no_data"))

    with tab3:
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""<div class='dm-card dm-card-green'>
            <h4>🟢 System OK</h4>
            <p><b>Version:</b> {APP_VERSION}</p>
            <p><b>Python:</b> {os.sys.version.split()[0]}</p>
            <p><b>Bcrypt:</b> {'✅' if HAS_BCRYPT else '❌ (SHA256)'}</p>
            <p><b>Plotly:</b> {'✅' if HAS_PLOTLY else '❌'}</p>
            <p><b>QR Code:</b> {'✅' if HAS_QRCODE else '❌'}</p>
            <p><b>Database:</b> SQLite</p>
            </div>""", unsafe_allow_html=True)
        with sc2:
            ts = db_stats()
            st.markdown(f"""<div class='dm-card dm-card-cyan'>
            <h4>📊 Statistics</h4>
            <p><b>Users:</b> {len(db_users())}</p>
            <p><b>Analyses:</b> {ts['total']}</p>
            <p><b>Reliable:</b> {ts['reliable']}</p>
            <p><b>Quiz Scores:</b> {len(db_leaderboard())}</p>
            <p><b>Languages:</b> FR / AR / EN</p>
            </div>""", unsafe_allow_html=True)
        with sc3:
            dbsz = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
            st.markdown(f"""<div class='dm-card'>
            <h4>💾 Storage</h4>
            <p><b>DB Size:</b> {dbsz:.1f} KB</p>
            <p><b>Location:</b> {os.path.abspath(DB_PATH)}</p>
            <p><b>Parasites:</b> {len(CLASS_NAMES)} classes</p>
            <p><b>Quiz:</b> {len(QUIZ_QUESTIONS)} questions</p>
            <p><b>Chat KB:</b> {len(CHAT_KB)} entries</p>
            </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════
#  PAGE: ABOUT
# ════════════════════════════════════════════
elif pg == "about":
    st.title(f"ℹ️ {t('about')}")
    lang = st.session_state.lang

    st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
    <h1 class='dm-nt'>🧬 DM SMART LAB AI</h1>
    <p style='font-size:1.1rem;font-family:Orbitron,sans-serif;'><b>v{APP_VERSION} — Professional Edition</b></p>
    <p style='opacity:.5;'>{t('system_desc')}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='dm-card'>
    <h3>📖 {tl(PROJECT_TITLE)}</h3>
    <p style='line-height:1.8;opacity:.8;'>{{"fr":"Ce projet innovant utilise les technologies de Deep Learning et de Vision par Ordinateur pour assister les techniciens de laboratoire dans l'identification rapide et précise des parasites.",
    "ar":"يستخدم هذا المشروع المبتكر تقنيات التعلم العميق والرؤية الحاسوبية لمساعدة تقنيي المخبر في التعرف السريع والدقيق على الطفيليات.",
    "en":"This innovative project uses Deep Learning and Computer Vision technologies to assist laboratory technicians in the rapid and accurate identification of parasites."}.get(lang,"")}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        d1r = tl(AUTHORS['dev1']['role'])
        d2r = tl(AUTHORS['dev2']['role'])
        st.markdown(f"""<div class='dm-card dm-card-cyan'>
        <h3>👨‍🔬 {t('dev_team')}</h3><br>
        <p><b>🧑‍💻 {AUTHORS['dev1']['name']}</b><br><span style='opacity:.5;'>{d1r}</span></p><br>
        <p><b>🔬 {AUTHORS['dev2']['name']}</b><br><span style='opacity:.5;'>{d2r}</span></p><br>
        <p><b>{{"fr":"Niveau","ar":"المستوى","en":"Level"}.get(lang,"")}:</b> {{"fr":"3ème Année","ar":"السنة الثالثة","en":"3rd Year"}.get(lang,"")}</p>
        <p><b>{{"fr":"Spécialité","ar":"التخصص","en":"Speciality"}.get(lang,"")}:</b> {{"fr":"Laboratoire de Santé Publique","ar":"مخبر الصحة العمومية","en":"Public Health Laboratory"}.get(lang,"")}</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='dm-card'>
        <h3>🏫 {t('institution')}</h3><br>
        <p><b>{tl(INSTITUTION['name'])}</b></p>
        <p>📍 {INSTITUTION['city']}, {tl(INSTITUTION['country'])} 🇩🇿</p><br>
        <h4>🎯 {{"fr":"Objectifs","ar":"الأهداف","en":"Objectives"}.get(lang,"")}</h4>
        <ul>
        <li>{{"fr":"Automatiser la lecture microscopique","ar":"أتمتة القراءة المجهرية","en":"Automate microscopic reading"}.get(lang,"")}</li>
        <li>{{"fr":"Réduire les erreurs diagnostiques","ar":"تقليل الأخطاء التشخيصية","en":"Reduce diagnostic errors"}.get(lang,"")}</li>
        <li>{{"fr":"Accélérer le processus d'analyse","ar":"تسريع عملية التحليل","en":"Speed up analysis process"}.get(lang,"")}</li>
        <li>{{"fr":"Assister les professionnels de santé","ar":"مساعدة المهنيين الصحيين","en":"Assist healthcare professionals"}.get(lang,"")}</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🛠️ {t('technologies')}")
    tc = st.columns(8)
    techs = [("🐍", "Python", "Core"), ("🧠", "TensorFlow", "AI"), ("🎨", "Streamlit", "UI"),
             ("📊", "Plotly", "Charts"), ("🗄️", "SQLite", "DB"), ("🔒", "Bcrypt", "Security"),
             ("📄", "FPDF", "PDF"), ("📱", "QR", "Verify")]
    for col, (i, n, d) in zip(tc, techs):
        with col:
            st.markdown(f"<div class='dm-m'><span class='dm-m-i'>{i}</span><div class='dm-m-v' style='font-size:.85rem;'>{n}</div><div class='dm-m-l'>{d}</div></div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🌟 Features v{APP_VERSION}")
    feat_cols = st.columns(4)
    features = [
        ("📸", {"fr": "Caméra", "ar": "كاميرا", "en": "Camera"}, {"fr": "Capture directe", "ar": "التقاط مباشر", "en": "Direct capture"}),
        ("🌍", {"fr": "3 Langues", "ar": "3 لغات", "en": "3 Languages"}, {"fr": "FR/AR/EN", "ar": "FR/AR/EN", "en": "FR/AR/EN"}),
        ("🤖", "DM Bot", {"fr": "Chatbot IA avancé", "ar": "شات بوت ذكي", "en": "Advanced AI chatbot"}),
        ("🧠", {"fr": "60+ Quiz", "ar": "60+ اختبار", "en": "60+ Quiz"}, {"fr": "Par catégorie", "ar": "حسب الفئة", "en": "By category"}),
        ("🔬", {"fr": "7 Parasites", "ar": "7 طفيليات", "en": "7 Parasites"}, {"fr": "Base complète", "ar": "قاعدة كاملة", "en": "Complete DB"}),
        ("🎯", "Grad-CAM", {"fr": "Heatmap IA", "ar": "خريطة حرارية", "en": "AI Heatmap"}),
        ("📄", "PDF Pro", {"fr": "QR + Signatures", "ar": "QR + توقيعات", "en": "QR + Signatures"}),
        ("🔄", {"fr": "Comparaison+", "ar": "مقارنة+", "en": "Comparison+"}, {"fr": "Pixel diff + filtres", "ar": "فرق بكسل + فلاتر", "en": "Pixel diff + filters"}),
        ("🔊", {"fr": "Voix", "ar": "صوت", "en": "Voice"}, {"fr": "TTS optionnel", "ar": "نطق اختياري", "en": "Optional TTS"}),
        ("📊", "Plotly", {"fr": "Graphiques pro", "ar": "رسوم بيانية", "en": "Pro charts"}),
        ("🔐", {"fr": "Auth Sécurisé", "ar": "مصادقة آمنة", "en": "Secure Auth"}, {"fr": "Bcrypt + lockout", "ar": "Bcrypt + قفل", "en": "Bcrypt + lockout"}),
        ("🌙", {"fr": "Thème Neon", "ar": "ثيم نيون", "en": "Neon Theme"}, {"fr": "Jour/Nuit", "ar": "ليل/نهار", "en": "Day/Night"}),
    ]
    for i, (ic, name, desc) in enumerate(features):
        with feat_cols[i % 4]:
            st.markdown(f"""<div class='dm-card' style='padding:12px;text-align:center;'>
            <div style='font-size:1.6rem;'>{ic}</div>
            <p style='font-weight:700;margin:2px 0;font-size:.83rem;'>{tl(name) if isinstance(name,dict) else name}</p>
            <p style='font-size:.68rem;opacity:.5;'>{tl(desc) if isinstance(desc,dict) else desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.caption(f"{'صُنع بـ ❤️ في' if lang=='ar' else 'Made with ❤️ in' if lang=='en' else 'Fait avec ❤️ à'} {INSTITUTION['city']} — {INSTITUTION['year']} 🇩🇿")
