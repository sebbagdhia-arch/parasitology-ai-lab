
import streamlit as st
import numpy as np
import pandas as pd
import os
import io
import json
import time
import base64
import hashlib
from datetime import datetime, timedelta
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw

st.set_page_config(
    page_title="DM SMART LAB AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

APP_VERSION = "5.2.0"
APP_PASSWORD = "DM@2026secure!"
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)
HISTORY_FILE = "analysis_history.json"
ACTIVITY_FILE = "activity_log.json"
CHAT_FILE = "chat_history.json"

AUTHORS = {
    "dev1": {"name": "Sebbag Mohamed Dhia Eddine", "role": "Expert IA & Conception"},
    "dev2": {"name": "Ben Sghir Mohamed", "role": "Expert Laboratoire & Données"},
}

INSTITUTION = {
    "name": "Institut National de Formation Supérieure Paramédicale (INFSPM)",
    "city": "Ouargla",
    "country": "Algérie",
    "year": 2026,
}

PROJECT_TITLE = (
    "Exploration du potentiel de l'intelligence artificielle "
    "pour la lecture automatique de l'examen parasitologique "
    "à l'état frais"
)

MODEL_CLASSES = [
    "Amoeba",
    "Giardia",
    "Leishmania",
    "Plasmodium",
    "Trypanosoma",
    "Schistosoma",
    "Negative",
]

LABEL_MAP = {
    "Amoeba": "Amoeba",
    "Giardia": "Giardia",
    "Leishmania": "Leishmania",
    "Plasmodium": "Plasmodium",
    "Trypanosoma": "Trypanosoma",
    "Schistosoma": "Schistosoma",
    "Negative": "Negative",
}

TRANSLATIONS = {
    "fr": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Diagnostic parasitologique intelligent",
        "login_title": "Connexion sécurisée",
        "login_user": "Identifiant",
        "login_pass": "Mot de passe",
        "login_btn": "Se connecter",
        "login_error": "Mot de passe incorrect",
        "login_locked": "Compte temporairement verrouillé",
        "logout": "Déconnexion",
        "language": "Langue",
        "night_mode": "Mode nuit",
        "nav_scan": "Scan",
        "nav_encyclopedia": "Encyclopédie",
        "nav_dashboard": "Tableau de bord",
        "nav_quiz": "Quiz",
        "nav_chatbot": "Assistant",
        "nav_about": "À propos",
        "scan_title": "Unité de diagnostic parasitologique",
        "scan_patient_info": "Informations patient",
        "scan_nom": "Nom",
        "scan_prenom": "Prénom",
        "scan_age": "Âge",
        "scan_sexe": "Sexe",
        "scan_poids": "Poids (kg)",
        "scan_echantillon": "Type d'échantillon",
        "scan_camera": "Caméra",
        "scan_upload": "Importer une image",
        "scan_capture": "Capture microscopique",
        "scan_result": "Résultat IA",
        "scan_confidence": "Confiance",
        "scan_morphology": "Morphologie",
        "scan_risk": "Risque",
        "scan_advice": "Conseil",
        "scan_heatmap": "Zone d'intérêt IA",
        "scan_all_probs": "Toutes les probabilités",
        "scan_extra_tests": "Examens complémentaires",
        "scan_download_pdf": "Télécharger PDF",
        "scan_save": "Sauvegarder",
        "scan_saved": "Analyse sauvegardée",
        "scan_new": "Nouvelle analyse",
        "scan_no_model": "Aucun modèle IA détecté. Analyse indisponible.",
        "scan_model_loaded": "Modèle chargé",
        "scan_required_name": "Le nom du patient est obligatoire",
        "scan_analyzing": "Analyse en cours...",
        "scan_low_conf": "Confiance faible. Vérification manuelle recommandée.",
        "patient_sexe_h": "Homme",
        "patient_sexe_f": "Femme",
        "echantillon_selles": "Selles",
        "echantillon_sang_frottis": "Sang (Frottis)",
        "echantillon_sang_goutte": "Sang (Goutte épaisse)",
        "echantillon_urines": "Urines",
        "echantillon_lcr": "LCR",
        "echantillon_autre": "Autre",
        "dash_title": "Tableau de bord clinique",
        "dash_total": "Analyses",
        "dash_reliable": "Fiables",
        "dash_check": "À vérifier",
        "dash_frequent": "Le plus fréquent",
        "dash_distribution": "Distribution",
        "dash_history": "Historique",
        "dash_export_csv": "Exporter CSV",
        "dash_export_json": "Exporter JSON",
        "dash_export_excel": "Exporter Excel",
        "dash_no_data": "Aucune donnée disponible",
        "enc_title": "Encyclopédie des parasites",
        "enc_search": "Rechercher un parasite",
        "quiz_title": "Quiz parasitologique",
        "quiz_start": "Démarrer le quiz",
        "quiz_next": "Question suivante",
        "quiz_finish": "Résultat final",
        "quiz_restart": "Recommencer",
        "chatbot_title": "Dr. DhiaBot",
        "chatbot_placeholder": "Posez une question...",
        "about_title": "À propos du projet",
        "pdf_title": "RAPPORT D'ANALYSE PARASITOLOGIQUE",
        "pdf_subtitle": "Analyse assistée par intelligence artificielle",
        "pdf_patient": "INFORMATIONS PATIENT",
        "pdf_result": "RÉSULTAT IA",
        "pdf_advice": "RECOMMANDATIONS",
        "pdf_warning": "Ce document doit être validé par un professionnel de santé.",
        "intro_text": "Bienvenue dans DM Smart Lab AI. Je suis votre microscope intelligent. Le système est prêt. Redirection automatique vers l'unité de scan.",
        "quality_good": "Image exploitable",
        "quality_bad": "Image faible qualité",
        "quality_blur": "Image floue",
        "quality_dark": "Image trop sombre",
        "quality_bright": "Image trop lumineuse",
        "quality_retake": "Veuillez reprendre une image plus nette avant l'analyse.",
        "activity_log": "Journal d'activité",
        "clear_chat": "Effacer le chat",
        "voice_off": "Désactiver le son",
        "voice_on": "Activer le son",
    },
    "ar": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "تشخيص طفيليات ذكي",
        "login_title": "تسجيل دخول آمن",
        "login_user": "اسم المستخدم",
        "login_pass": "كلمة المرور",
        "login_btn": "دخول",
        "login_error": "كلمة المرور غير صحيحة",
        "login_locked": "الحساب مقفل مؤقتًا",
        "logout": "تسجيل الخروج",
        "language": "اللغة",
        "night_mode": "الوضع الليلي",
        "nav_scan": "الفحص",
        "nav_encyclopedia": "الموسوعة",
        "nav_dashboard": "لوحة التحكم",
        "nav_quiz": "الاختبار",
        "nav_chatbot": "المساعد",
        "nav_about": "حول المشروع",
        "scan_title": "وحدة التشخيص الطفيلي",
        "scan_patient_info": "بيانات المريض",
        "scan_nom": "اللقب",
        "scan_prenom": "الاسم",
        "scan_age": "العمر",
        "scan_sexe": "الجنس",
        "scan_poids": "الوزن (كغ)",
        "scan_echantillon": "نوع العينة",
        "scan_camera": "الكاميرا",
        "scan_upload": "رفع صورة",
        "scan_capture": "التقاط مجهري",
        "scan_result": "نتيجة الذكاء الاصطناعي",
        "scan_confidence": "نسبة الثقة",
        "scan_morphology": "الصفات الشكلية",
        "scan_risk": "الخطورة",
        "scan_advice": "النصيحة",
        "scan_heatmap": "منطقة اهتمام الذكاء",
        "scan_all_probs": "كل الاحتمالات",
        "scan_extra_tests": "فحوصات إضافية",
        "scan_download_pdf": "تحميل PDF",
        "scan_save": "حفظ",
        "scan_saved": "تم حفظ التحليل",
        "scan_new": "تحليل جديد",
        "scan_no_model": "لم يتم العثور على موديل الذكاء الاصطناعي. التحليل غير متاح.",
        "scan_model_loaded": "تم تحميل الموديل",
        "scan_required_name": "اسم المريض إجباري",
        "scan_analyzing": "جاري التحليل...",
        "scan_low_conf": "الثقة منخفضة، ينصح بالمراجعة اليدوية.",
        "patient_sexe_h": "ذكر",
        "patient_sexe_f": "أنثى",
        "echantillon_selles": "براز",
        "echantillon_sang_frottis": "دم (لطاخة)",
        "echantillon_sang_goutte": "دم (قطرة سميكة)",
        "echantillon_urines": "بول",
        "echantillon_lcr": "سائل دماغي شوكي",
        "echantillon_autre": "أخرى",
        "dash_title": "لوحة التحكم",
        "dash_total": "التحاليل",
        "dash_reliable": "موثوقة",
        "dash_check": "تحتاج مراجعة",
        "dash_frequent": "الأكثر شيوعًا",
        "dash_distribution": "التوزيع",
        "dash_history": "السجل",
        "dash_export_csv": "تصدير CSV",
        "dash_export_json": "تصدير JSON",
        "dash_export_excel": "تصدير Excel",
        "dash_no_data": "لا توجد بيانات",
        "enc_title": "موسوعة الطفيليات",
        "enc_search": "ابحث عن طفيلي",
        "quiz_title": "اختبار الطفيليات",
        "quiz_start": "ابدأ الاختبار",
        "quiz_next": "السؤال التالي",
        "quiz_finish": "النتيجة النهائية",
        "quiz_restart": "إعادة",
        "chatbot_title": "الدكتور ضياء بوت",
        "chatbot_placeholder": "اكتب سؤالك...",
        "about_title": "حول المشروع",
        "pdf_title": "تقرير تحليل طفيليات",
        "pdf_subtitle": "تحليل مدعوم بالذكاء الاصطناعي",
        "pdf_patient": "بيانات المريض",
        "pdf_result": "النتيجة",
        "pdf_advice": "التوصيات",
        "pdf_warning": "هذا التقرير يحتاج إلى اعتماد مختص صحي.",
        "intro_text": "مرحبًا بكم في دي إم سمارت لاب. أنا المجهر الذكي الخاص بكم. النظام جاهز الآن. سيتم الانتقال تلقائيًا إلى صفحة الفحص.",
        "quality_good": "الصورة صالحة للتحليل",
        "quality_bad": "جودة الصورة ضعيفة",
        "quality_blur": "الصورة ضبابية",
        "quality_dark": "الصورة مظلمة جدًا",
        "quality_bright": "الصورة ساطعة جدًا",
        "quality_retake": "يرجى إعادة التقاط صورة أوضح قبل التحليل.",
        "activity_log": "سجل النشاط",
        "clear_chat": "مسح المحادثة",
        "voice_off": "إيقاف الصوت",
        "voice_on": "تشغيل الصوت",
    },
    "en": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Smart parasitology diagnosis",
        "login_title": "Secure login",
        "login_user": "Username",
        "login_pass": "Password",
        "login_btn": "Log in",
        "login_error": "Incorrect password",
        "login_locked": "Account temporarily locked",
        "logout": "Log out",
        "language": "Language",
        "night_mode": "Night mode",
        "nav_scan": "Scan",
        "nav_encyclopedia": "Encyclopedia",
        "nav_dashboard": "Dashboard",
        "nav_quiz": "Quiz",
        "nav_chatbot": "Assistant",
        "nav_about": "About",
        "scan_title": "Parasitology diagnostic unit",
        "scan_patient_info": "Patient information",
        "scan_nom": "Last name",
        "scan_prenom": "First name",
        "scan_age": "Age",
        "scan_sexe": "Sex",
        "scan_poids": "Weight (kg)",
        "scan_echantillon": "Sample type",
        "scan_camera": "Camera",
        "scan_upload": "Upload image",
        "scan_capture": "Microscope capture",
        "scan_result": "AI result",
        "scan_confidence": "Confidence",
        "scan_morphology": "Morphology",
        "scan_risk": "Risk",
        "scan_advice": "Advice",
        "scan_heatmap": "AI focus area",
        "scan_all_probs": "All probabilities",
        "scan_extra_tests": "Additional tests",
        "scan_download_pdf": "Download PDF",
        "scan_save": "Save",
        "scan_saved": "Analysis saved",
        "scan_new": "New analysis",
        "scan_no_model": "No AI model detected. Analysis unavailable.",
        "scan_model_loaded": "Model loaded",
        "scan_required_name": "Patient name is required",
        "scan_analyzing": "Analysing...",
        "scan_low_conf": "Low confidence. Manual review recommended.",
        "patient_sexe_h": "Male",
        "patient_sexe_f": "Female",
        "echantillon_selles": "Stool",
        "echantillon_sang_frottis": "Blood smear",
        "echantillon_sang_goutte": "Thick blood drop",
        "echantillon_urines": "Urine",
        "echantillon_lcr": "CSF",
        "echantillon_autre": "Other",
        "dash_title": "Clinical dashboard",
        "dash_total": "Analyses",
        "dash_reliable": "Reliable",
        "dash_check": "Need review",
        "dash_frequent": "Most frequent",
        "dash_distribution": "Distribution",
        "dash_history": "History",
        "dash_export_csv": "Export CSV",
        "dash_export_json": "Export JSON",
        "dash_export_excel": "Export Excel",
        "dash_no_data": "No data available",
        "enc_title": "Parasite encyclopedia",
        "enc_search": "Search a parasite",
        "quiz_title": "Parasitology quiz",
        "quiz_start": "Start quiz",
        "quiz_next": "Next question",
        "quiz_finish": "Final result",
        "quiz_restart": "Restart",
        "chatbot_title": "Dr. DhiaBot",
        "chatbot_placeholder": "Ask a question...",
        "about_title": "About the project",
        "pdf_title": "PARASITOLOGY ANALYSIS REPORT",
        "pdf_subtitle": "AI-assisted analysis",
        "pdf_patient": "PATIENT INFORMATION",
        "pdf_result": "AI RESULT",
        "pdf_advice": "RECOMMENDATIONS",
        "pdf_warning": "This document must be validated by a healthcare professional.",
        "intro_text": "Welcome to DM Smart Lab AI. I am your smart microscope. The system is ready. Redirecting automatically to the scan unit.",
        "quality_good": "Image usable",
        "quality_bad": "Low image quality",
        "quality_blur": "Blurred image",
        "quality_dark": "Image too dark",
        "quality_bright": "Image too bright",
        "quality_retake": "Please retake a clearer image before analysis.",
        "activity_log": "Activity log",
        "clear_chat": "Clear chat",
        "voice_off": "Mute voice",
        "voice_on": "Enable voice",
    }
}

PARASITE_DB = {
    "Amoeba": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {"fr": "Kyste sphérique 10-15 µm à 4 noyaux ou trophozoïte avec pseudopodes.", "ar": "كيس كروي 10-15 ميكرومتر بأربع نوى أو طور غاذي بأقدام كاذبة.", "en": "Spherical cyst 10-15 µm with 4 nuclei or trophozoite with pseudopods."},
        "description": {"fr": "Parasite intestinal responsable de l'amibiase.", "ar": "طفيلي معوي مسؤول عن الأميبيا.", "en": "Intestinal parasite causing amoebiasis."},
        "advice": {"fr": "Metronidazole + confirmation biologique si doute.", "ar": "ميترونيدازول مع تأكيد مخبري عند الشك.", "en": "Metronidazole + biological confirmation if needed."},
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "extra_tests": {"fr": ["Examen parasitologique répété", "Recherche de kystes/trophozoïtes"], "ar": ["إعادة الفحص الطفيلي", "البحث عن الأكياس والأطوار الغاذية"], "en": ["Repeat stool exam", "Search for cysts/trophozoites"]},
        "color": "#ef4444",
        "icon": "🦠",
        "funny": {"fr": "L'amibe n'aime pas qu'on l'oublie au microscope.", "ar": "الأميبا لا تحب أن تُنسى تحت المجهر.", "en": "Amoeba does not like being ignored under the microscope."}
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia",
        "morphology": {"fr": "Trophozoïte piriforme avec deux noyaux, aspect de face de hibou.", "ar": "طور غاذي كمثري بنواتين بشكل وجه بومة.", "en": "Pear-shaped trophozoite with two nuclei, owl-face appearance."},
        "description": {"fr": "Protozoaire intestinal causant une malabsorption.", "ar": "أولي معوي يسبب سوء الامتصاص.", "en": "Intestinal protozoan causing malabsorption."},
        "advice": {"fr": "Metronidazole ou Tinidazole. Vérifier l'eau consommée.", "ar": "ميترونيدازول أو تينيدازول مع فحص مصدر الماء.", "en": "Metronidazole or Tinidazole. Check water source."},
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "extra_tests": {"fr": ["Test antigénique Giardia", "Examens répétés des selles"], "ar": ["اختبار مستضد الجيارديا", "فحوصات براز متكررة"], "en": ["Giardia antigen test", "Repeated stool exams"]},
        "color": "#f59e0b",
        "icon": "🧫",
        "funny": {"fr": "La face de hibou la plus célèbre de la parasitologie.", "ar": "أشهر وجه بومة في علم الطفيليات.", "en": "The most famous owl face in parasitology."}
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / tropica",
        "morphology": {"fr": "Amastigotes intracellulaires dans les macrophages.", "ar": "أشكال لا سوطية داخل البالعات.", "en": "Intracellular amastigotes inside macrophages."},
        "description": {"fr": "Parasite transmis par le phlébotome.", "ar": "طفيلي ينتقل بواسطة ذبابة الرمل.", "en": "Parasite transmitted by sandfly."},
        "advice": {"fr": "Confirmer par frottis, sérologie ou ponction selon le contexte.", "ar": "يؤكد باللطاخة أو المصلية أو البزل حسب الحالة.", "en": "Confirm with smear, serology or aspiration depending on context."},
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "extra_tests": {"fr": ["Coloration MGG", "Sérologie", "Ponction médullaire si besoin"], "ar": ["صبغة MGG", "فحص مصلي", "بزل نقي العظم عند الحاجة"], "en": ["MGG stain", "Serology", "Bone marrow aspiration if needed"]},
        "color": "#dc2626",
        "icon": "🩸",
        "funny": {"fr": "Petit parasite, grand problème si on le laisse passer.", "ar": "طفيلي صغير لكن مشكلته كبيرة إذا تم تجاهله.", "en": "Small parasite, big problem if missed."}
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax",
        "morphology": {"fr": "Forme en bague dans les hématies sur frottis sanguin.", "ar": "شكل حلقي داخل كريات الدم الحمراء في اللطاخة.", "en": "Ring form inside red blood cells on blood smear."},
        "description": {"fr": "Agent du paludisme. Urgence clinique potentielle.", "ar": "مسبب الملاريا وقد تكون حالة إسعافية.", "en": "Malaria agent. Potential clinical emergency."},
        "advice": {"fr": "Frottis + goutte épaisse + prise en charge urgente selon gravité.", "ar": "لطاخة + قطرة سميكة + تدبير استعجالي حسب الشدة.", "en": "Thin smear + thick smear + urgent management depending on severity."},
        "risk_level": "critical",
        "risk_display": {"fr": "Urgence 🚨", "ar": "استعجالي 🚨", "en": "Emergency 🚨"},
        "extra_tests": {"fr": ["Goutte épaisse", "Frottis répété", "Bilan rénal/hépatique"], "ar": ["قطرة سميكة", "إعادة اللطاخة", "فحص الكبد والكلى"], "en": ["Thick smear", "Repeated smear", "Renal/hepatic panel"]},
        "color": "#7f1d1d",
        "icon": "🚨",
        "funny": {"fr": "Quand Plasmodium apparaît, le laboratoire se met en alerte.", "ar": "عند ظهور البلازموديوم يدخل المخبر في حالة تأهب.", "en": "When Plasmodium appears, the lab goes on alert."}
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei / cruzi",
        "morphology": {"fr": "Forme allongée avec membrane ondulante.", "ar": "شكل طولي بغشاء متموج.", "en": "Elongated form with undulating membrane."},
        "description": {"fr": "Parasite sanguin transmis par vecteur.", "ar": "طفيلي دموي ينتقل بواسطة ناقل.", "en": "Vector-borne blood parasite."},
        "advice": {"fr": "Confirmer sur frottis ou examens spécialisés.", "ar": "يؤكد باللطاخة أو فحوص متخصصة.", "en": "Confirm by smear or specialized tests."},
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "extra_tests": {"fr": ["Sérologie", "Examen du LCR si suspicion neurologique"], "ar": ["فحص مصلي", "فحص السائل الشوكي عند الشك العصبي"], "en": ["Serology", "CSF exam if neurological suspicion"]},
        "color": "#dc2626",
        "icon": "🧬",
        "funny": {"fr": "Il bouge bien... mais on préfère le repérer vite.", "ar": "يتحرك جيدًا... لكن الأفضل اكتشافه بسرعة.", "en": "Moves fast... better detect it quickly."}
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni",
        "morphology": {"fr": "Œufs ovoïdes avec éperon terminal ou latéral.", "ar": "بيض بيضوي بنتوء طرفي أو جانبي.", "en": "Ovoid eggs with terminal or lateral spine."},
        "description": {"fr": "Agent de la bilharziose.", "ar": "مسبب البلهارسيا.", "en": "Agent of schistosomiasis."},
        "advice": {"fr": "Praziquantel et examens urinaires/stercoraux selon le type.", "ar": "برازيكوانتيل مع فحوص بولية أو برازية حسب النوع.", "en": "Praziquantel with urine/stool investigations depending on type."},
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "extra_tests": {"fr": ["Examen des urines", "Recherche d'œufs", "Échographie si besoin"], "ar": ["فحص البول", "البحث عن البيوض", "إيكوغرافي عند الحاجة"], "en": ["Urine exam", "Egg search", "Ultrasound if needed"]},
        "color": "#f59e0b",
        "icon": "💧",
        "funny": {"fr": "Le parasite qui rappelle que l'eau douce n'est pas toujours innocente.", "ar": "الطفيلي الذي يذكرك أن الماء العذب ليس دائمًا بريئًا.", "en": "The parasite that reminds you freshwater is not always innocent."}
    },
    "Negative": {
        "scientific_name": "No parasite detected",
        "morphology": {"fr": "Aucun élément parasitaire identifié sur cette image.", "ar": "لم يتم كشف أي عنصر طفيلي في هذه الصورة.", "en": "No parasitic element identified in this image."},
        "description": {"fr": "Image sans détection parasitaire probable.", "ar": "صورة دون كشف طفيلي محتمل.", "en": "Image with no likely parasitic detection."},
        "advice": {"fr": "Corréler avec le contexte clinique et répéter l'examen si besoin.", "ar": "يربط بالسياق السريري ويعاد الفحص عند الحاجة.", "en": "Correlate clinically and repeat exam if needed."},
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "extra_tests": {"fr": ["Aucun examen complémentaire spécifique"], "ar": ["لا يوجد فحص إضافي نوعي"], "en": ["No specific additional test"]},
        "color": "#16a34a",
        "icon": "✅",
        "funny": {"fr": "Rien à signaler pour cette image.", "ar": "لا شيء مميز في هذه الصورة.", "en": "Nothing remarkable in this image."}
    }
}

QUIZ_QUESTIONS = {
    "fr": [
        {"q": "Quel parasite montre une forme en bague dans les hématies ?", "options": ["Giardia", "Plasmodium", "Amoeba", "Schistosoma"], "answer": 1},
        {"q": "Quel parasite montre une 'face de hibou' ?", "options": ["Leishmania", "Giardia", "Trypanosoma", "Amoeba"], "answer": 1},
        {"q": "Quel traitement est classique contre la bilharziose ?", "options": ["Praziquantel", "ACT", "Metronidazole", "Amphotéricine"], "answer": 0},
        {"q": "Quel examen est urgent en cas de paludisme ?", "options": ["ECBU", "Sérologie seule", "Frottis + goutte épaisse", "Coproculture"], "answer": 2},
        {"q": "Le parasite transmis par le phlébotome est :", "options": ["Leishmania", "Giardia", "Schistosoma", "Amoeba"], "answer": 0},
    ],
    "ar": [
        {"q": "أي طفيلي يظهر بشكل حلقي داخل الكريات الحمراء؟", "options": ["جيارديا", "بلازموديوم", "أميبا", "بلهارسيا"], "answer": 1},
        {"q": "من هو الطفيلي المعروف بوجه البومة؟", "options": ["ليشمانيا", "جيارديا", "تريبانوسوما", "أميبا"], "answer": 1},
        {"q": "ما العلاج الشائع للبلهارسيا؟", "options": ["برازيكوانتيل", "ACT", "ميترونيدازول", "أمفوتيريسين"], "answer": 0},
        {"q": "ما الفحص العاجل عند الشك في الملاريا؟", "options": ["ECBU", "مصلية فقط", "لطاخة + قطرة سميكة", "زرع براز"], "answer": 2},
        {"q": "أي طفيلي ينتقل بذبابة الرمل؟", "options": ["ليشمانيا", "جيارديا", "بلهارسيا", "أميبا"], "answer": 0},
    ],
    "en": [
        {"q": "Which parasite shows a ring form in RBCs?", "options": ["Giardia", "Plasmodium", "Amoeba", "Schistosoma"], "answer": 1},
        {"q": "Which parasite has an owl-face appearance?", "options": ["Leishmania", "Giardia", "Trypanosoma", "Amoeba"], "answer": 1},
        {"q": "Which drug is classic for schistosomiasis?", "options": ["Praziquantel", "ACT", "Metronidazole", "Amphotericin"], "answer": 0},
        {"q": "What is urgent for suspected malaria?", "options": ["Urinalysis", "Serology only", "Thin smear + Thick smear", "Stool culture"], "answer": 2},
        {"q": "Which parasite is transmitted by sandfly?", "options": ["Leishmania", "Giardia", "Schistosoma", "Amoeba"], "answer": 0},
    ]
}

CHATBOT_KNOWLEDGE = {
    "fr": {
        "amoeba": "Amoeba: parasite intestinal, diagnostic par examen des selles, traitement souvent par metronidazole.",
        "giardia": "Giardia: trophozoïte en face de hibou, malabsorption, transmission hydrique fréquente.",
        "plasmodium": "Plasmodium: urgence potentielle, confirmer par frottis sanguin et goutte épaisse.",
        "leishmania": "Leishmania: transmise par phlébotome, formes cutanée ou viscérale.",
        "schistosoma": "Schistosoma: bilharziose, recherche d'œufs dans urines ou selles.",
        "trypanosoma": "Trypanosoma: parasite sanguin, confirmation par examens spécialisés.",
    },
    "ar": {
        "أميبا": "الأميبا: طفيلي معوي، يشخّص غالبًا بفحص البراز، ويعالج غالبًا بميترونيدازول.",
        "جيارديا": "الجيارديا: طور غاذي بشكل وجه بومة، وتنتقل كثيرًا عبر الماء.",
        "ملاريا": "الملاريا: قد تكون حالة استعجالية وتؤكد باللطاخة والقطرة السميكة.",
        "بلازموديوم": "البلازموديوم: يظهر في كريات الدم الحمراء وقد يكون خطيرًا.",
        "ليشمانيا": "الليشمانيا: تنتقل بذبابة الرمل ولها أشكال جلدية أو حشوية.",
        "بلهارسيا": "البلهارسيا: يتم البحث عن بيوضها في البول أو البراز حسب النوع.",
        "تريبانوسوما": "التريبانوسوما: طفيلي دموي يحتاج فحوصًا تأكيدية متخصصة.",
    },
    "en": {
        "amoeba": "Amoeba: intestinal parasite, often diagnosed by stool examination, often treated with metronidazole.",
        "giardia": "Giardia: owl-face trophozoite, often waterborne, may cause malabsorption.",
        "plasmodium": "Plasmodium: potentially urgent, confirm with blood smear and thick smear.",
        "leishmania": "Leishmania: transmitted by sandfly, may be cutaneous or visceral.",
        "schistosoma": "Schistosoma: search for eggs in urine or stool depending on species.",
        "trypanosoma": "Trypanosoma: blood parasite requiring confirmatory tests.",
    }
}

def t(key):
    lang = st.session_state.get("lang", "ar")
    return TRANSLATIONS.get(lang, TRANSLATIONS["ar"]).get(key, key)

def get_lang():
    return st.session_state.get("lang", "ar")

def get_p_text(data, field):
    lang = get_lang()
    value = data.get(field, "")
    if isinstance(value, dict):
        return value.get(lang, value.get("fr", ""))
    return value

def risk_color(level):
    return {
        "critical": "#7f1d1d",
        "high": "#dc2626",
        "medium": "#f59e0b",
        "low": "#22c55e",
        "none": "#16a34a",
    }.get(level, "#64748b")

def safe_load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default
    return default

def safe_save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

def log_activity(action):
    st.session_state.activity_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": st.session_state.get("user_name", ""),
        "action": action
    })
    safe_save_json(ACTIVITY_FILE, st.session_state.activity_log)

DEFAULTS = {
    "logged_in": False,
    "user_name": "",
    "lang": "ar",
    "dark_mode": True,
    "login_attempts": 0,
    "lockout_until": None,
    "history": safe_load_json(HISTORY_FILE, []),
    "activity_log": safe_load_json(ACTIVITY_FILE, []),
    "chat_history": safe_load_json(CHAT_FILE, []),
    "current_page": "intro",
    "intro_done": False,
    "quiz_index": 0,
    "quiz_score": 0,
    "quiz_started": False,
    "last_feedback": "",
    "voice_enabled": True,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def apply_theme():
    dark = st.session_state.get("dark_mode", True)
    lang = st.session_state.get("lang", "ar")
    rtl = "rtl" if lang == "ar" else "ltr"
    align = "right" if lang == "ar" else "left"

    if dark:
        bg = "#07121f"
        bg2 = "#0d1b2d"
        card = "rgba(10, 24, 43, 0.82)"
        text = "#eef6ff"
        muted = "#a8bdd4"
        border = "rgba(96,165,250,0.14)"
        primary = "#60a5fa"
        secondary = "#22d3ee"
        accent = "#8b5cf6"
        glow = "rgba(34,211,238,0.18)"
        input_bg = "#11233a"
    else:
        bg = "#f0f6ff"
        bg2 = "#ffffff"
        card = "rgba(255,255,255,0.92)"
        text = "#0f172a"
        muted = "#475569"
        border = "rgba(37,99,235,0.10)"
        primary = "#2563eb"
        secondary = "#0891b2"
        accent = "#7c3aed"
        glow = "rgba(37,99,235,0.12)"
        input_bg = "#ffffff"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], p, span, div, label, li, td, th, input, textarea, button {{
        font-family: 'Cairo', 'Inter', sans-serif !important;
        direction: {rtl};
        text-align: {align};
        color: {text};
    }}

    .stApp {{
        background:
            radial-gradient(circle at 10% 15%, rgba(34,211,238,0.10), transparent 25%),
            radial-gradient(circle at 85% 10%, rgba(139,92,246,0.10), transparent 24%),
            radial-gradient(circle at 75% 80%, rgba(96,165,250,0.08), transparent 26%),
            linear-gradient(180deg, {bg} 0%, {bg2} 100%);
    }}

    .stApp::before {{
        content:'';
        position:fixed;
        inset:0;
        background-image: radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 26px 26px;
        pointer-events:none;
        z-index:0;
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(5,10,18,0.96), rgba(11,22,38,0.96)) !important;
        border-left: 1px solid rgba(255,255,255,0.06);
    }}

    section[data-testid="stSidebar"] * {{
        color: #e7f0fb !important;
    }}

    .dm-shell {{
        position:relative;
        z-index:2;
    }}

    .dm-card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 24px;
        padding: 22px;
        margin: 12px 0;
        backdrop-filter: blur(14px);
        box-shadow: 0 12px 34px rgba(0,0,0,0.16);
    }}

    .dm-hero {{
        background:
            radial-gradient(circle at 12% 25%, rgba(34,211,238,0.14), transparent 25%),
            radial-gradient(circle at 82% 12%, rgba(96,165,250,0.16), transparent 28%),
            linear-gradient(135deg, rgba(96,165,250,0.08), rgba(34,211,238,0.06), rgba(139,92,246,0.06));
        border: 1px solid {border};
        border-radius: 28px;
        padding: 28px;
        position:relative;
        overflow:hidden;
    }}

    .hero-title {{
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 6px 0;
    }}

    .hero-sub {{
        color: {muted};
        font-size: 1rem;
    }}

    .logo-wrap {{
        display:flex;
        align-items:center;
        gap:12px;
        margin-bottom: 14px;
    }}

    .logo-ico {{
        width:64px;
        height:64px;
        border-radius:20px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:2rem;
        background: linear-gradient(135deg, rgba(96,165,250,0.28), rgba(34,211,238,0.20), rgba(139,92,246,0.18));
        box-shadow: 0 0 24px {glow};
    }}

    .logo-main {{
        font-weight:800;
        font-size:1.05rem;
    }}

    .logo-sub {{
        color:{muted};
        font-size:0.8rem;
    }}

    .avatar-card {{
        background: {card};
        border: 1px solid {border};
        border-radius: 28px;
        padding: 18px;
        text-align:center;
        box-shadow: 0 12px 30px rgba(0,0,0,0.12);
        position:relative;
        overflow:hidden;
    }}

    .avatar-circle {{
        width: 160px;
        height: 160px;
        border-radius: 50%;
        margin: 0 auto 14px auto;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size: 4.6rem;
        background: linear-gradient(135deg, rgba(96,165,250,0.24), rgba(34,211,238,0.16), rgba(139,92,246,0.12));
        border: 2px solid rgba(255,255,255,0.10);
        box-shadow: inset 0 0 18px rgba(255,255,255,0.06), 0 0 26px rgba(96,165,250,0.12);
    }}

    .avatar-name {{
        font-size: 1rem;
        font-weight: 800;
    }}

    .avatar-role {{
        color: {muted};
        font-size: 0.84rem;
    }}

    .microscope-zone {{
        text-align:center;
        padding-top:10px;
    }}

    .microscope-svg {{
        width: 190px;
        height: 190px;
        margin: 0 auto;
        filter: drop-shadow(0 0 24px rgba(96,165,250,0.22));
        animation: floatMic 2.8s ease-in-out infinite;
    }}

    @keyframes floatMic {{
        0%,100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-10px); }}
    }}

    .speech-box {{
        margin-top: 16px;
        padding: 16px 18px;
        border-radius: 20px;
        background: rgba(96,165,250,0.10);
        border: 1px solid rgba(96,165,250,0.18);
        font-weight: 600;
        min-height: 90px;
        box-shadow: 0 0 18px rgba(34,211,238,0.06);
    }}

    .pulse-dot {{
        display:inline-block;
        width:10px;
        height:10px;
        border-radius:50%;
        background:#22d3ee;
        margin-left:8px;
        animation:pulseDot 1.1s infinite;
    }}

    @keyframes pulseDot {{
        0% {{ transform:scale(0.8); opacity:0.5; }}
        50% {{ transform:scale(1.3); opacity:1; }}
        100% {{ transform:scale(0.8); opacity:0.5; }}
    }}

    .dm-metric {{
        background: {card};
        border: 1px solid {border};
        border-radius: 22px;
        padding: 18px;
        text-align:center;
        box-shadow: 0 10px 26px rgba(0,0,0,0.12);
    }}

    .dm-metric-val {{
        font-size: 2rem;
        font-weight: 800;
        color: {primary};
    }}

    .dm-metric-lbl {{
        color: {muted};
        font-size: 0.86rem;
    }}

    .stButton > button, .stDownloadButton > button {{
        border-radius: 15px !important;
        border: 0 !important;
        padding: 0.72rem 1rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, {primary}, {secondary}, {accent}) !important;
        color: white !important;
        box-shadow: 0 10px 24px rgba(37,99,235,0.22);
    }}

    .stTextInput input, .stNumberInput input, .stTextArea textarea {{
        background: {input_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 13px !important;
        color: {text} !important;
    }}

    div[data-baseweb="select"] > div {{
        background: {input_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 13px !important;
    }}

    .tag {{
        display:inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        margin: 4px 8px 4px 0;
        font-weight: 700;
        font-size: 0.8rem;
        background: rgba(34,211,238,0.10);
        color: {secondary};
        border: 1px solid rgba(34,211,238,0.14);
    }}

    .lens-frame {{
        border: 2px dashed rgba(96,165,250,0.22);
        border-radius: 26px;
        padding: 16px;
        background:
            radial-gradient(circle at center, rgba(96,165,250,0.06), transparent 60%);
    }}

    .lens-title {{
        font-weight: 800;
        margin-bottom: 10px;
    }}

    .result-card {{
        border-radius: 24px;
        padding: 22px;
        border: 1px solid {border};
        background: {card};
        box-shadow: 0 12px 32px rgba(0,0,0,0.14);
    }}

    .chip {{
        display:inline-block;
        padding: 7px 12px;
        border-radius: 999px;
        margin: 4px 8px 4px 0;
        font-weight: 700;
        font-size: 0.82rem;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06);
    }}

    .chat-user {{
        background: linear-gradient(135deg, {primary}, {secondary});
        color: white !important;
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0 8px auto;
        width: fit-content;
        max-width: 86%;
    }}

    .chat-bot {{
        background: {card};
        border: 1px solid {border};
        padding: 12px 16px;
        border-radius: 18px;
        margin: 8px 0;
        width: fit-content;
        max-width: 86%;
    }}

    .warning-box {{
        border-radius: 16px;
        padding: 12px 14px;
        background: rgba(245,158,11,0.10);
        border: 1px solid rgba(245,158,11,0.20);
    }}

    .good-box {{
        border-radius: 16px;
        padding: 12px 14px;
        background: rgba(34,197,94,0.10);
        border: 1px solid rgba(34,197,94,0.20);
    }}
    </style>
    """, unsafe_allow_html=True)

apply_theme()

def autoplay_tts(text, lang_code=None):
    if not st.session_state.get("voice_enabled", True):
        return
    if lang_code is None:
        lang_code = "ar" if get_lang() == "ar" else "fr" if get_lang() == "fr" else "en"
    try:
        from gtts import gTTS
        text_hash = hashlib.md5(text.encode("utf-8")).hexdigest()
        file_name = f"voice_{text_hash}.mp3"
        if not os.path.exists(file_name):
            tts = gTTS(text=text, lang=lang_code)
            tts.save(file_name)
        with open(file_name, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """,
            unsafe_allow_html=True
        )
    except:
        pass

def microscope_svg():
    return """
    <svg class="microscope-svg" viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="#60a5fa"/>
          <stop offset="50%" stop-color="#22d3ee"/>
          <stop offset="100%" stop-color="#8b5cf6"/>
        </linearGradient>
      </defs>
      <circle cx="110" cy="110" r="96" fill="rgba(96,165,250,0.06)" stroke="rgba(96,165,250,0.16)" stroke-width="2"/>
      <rect x="110" y="42" width="18" height="58" rx="8" transform="rotate(28 119 72)" fill="url(#g1)"/>
      <rect x="78" y="82" width="18" height="54" rx="8" transform="rotate(-18 87 109)" fill="url(#g1)"/>
      <circle cx="135" cy="86" r="12" fill="#dbeafe" stroke="#60a5fa" stroke-width="3"/>
      <path d="M89 124 C101 86, 154 92, 154 136 L154 152" fill="none" stroke="url(#g1)" stroke-width="12" stroke-linecap="round"/>
      <rect x="86" y="150" width="78" height="16" rx="8" fill="url(#g1)"/>
      <rect x="60" y="168" width="110" height="18" rx="9" fill="#93c5fd"/>
      <circle cx="112" cy="112" r="6" fill="#22d3ee">
        <animate attributeName="r" values="5;8;5" dur="1.2s" repeatCount="indefinite"/>
      </circle>
    </svg>
    """

def load_labels_from_file():
    if os.path.exists("labels.txt"):
        labels = []
        with open("labels.txt", "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(" ", 1)
                if len(parts) == 2:
                    labels.append(parts[1].strip())
        if labels:
            return labels
    return MODEL_CLASSES

@st.cache_resource(show_spinner=False)
def load_ai_model():
    try:
        import tensorflow as tf
    except Exception:
        return None, None, None

    labels = load_labels_from_file()
    files = os.listdir(".")
    model = None
    model_name = None

    try:
        keras_files = [f for f in files if f.endswith(".keras") or f.endswith(".h5")]
        tflite_files = [f for f in files if f.endswith(".tflite")]

        if keras_files:
            model_name = keras_files[0]
            model = tf.keras.models.load_model(model_name, compile=False)
        elif tflite_files:
            model_name = tflite_files[0]
            model = tf.lite.Interpreter(model_path=model_name)
            model.allocate_tensors()
    except Exception:
        model = None
        model_name = None

    return model, model_name, labels

def preprocess_image_for_model(image):
    img = ImageOps.fit(image.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    arr = (arr / 127.5) - 1
    arr = np.expand_dims(arr, axis=0)
    return arr

def predict_image(model, labels, image):
    result = {
        "available": False,
        "label": None,
        "confidence": 0,
        "all_predictions": {},
        "is_reliable": False,
        "info": None,
        "error": None
    }

    if model is None:
        result["error"] = "NO_MODEL"
        return result

    try:
        import tensorflow as tf
        batch = preprocess_image_for_model(image)

        if isinstance(model, tf.lite.Interpreter):
            input_details = model.get_input_details()
            output_details = model.get_output_details()
            input_dtype = input_details[0]["dtype"]
            input_data = batch.astype(input_dtype) if input_dtype != np.float32 else batch.astype(np.float32)
            model.set_tensor(input_details[0]["index"], input_data)
            model.invoke()
            preds = model.get_tensor(output_details[0]["index"])[0]
        else:
            preds = model.predict(batch, verbose=0)[0]

        preds = np.array(preds, dtype=np.float32).flatten()
        preds = np.nan_to_num(preds, nan=0.0, posinf=0.0, neginf=0.0)

        if len(preds) != len(labels):
            result["error"] = f"LABEL_MODEL_MISMATCH: preds={len(preds)} labels={len(labels)}"
            return result

        idx = int(np.argmax(preds))
        raw_label = labels[idx]
        label = LABEL_MAP.get(raw_label, raw_label)
        confidence = float(preds[idx]) * 100

        all_predictions = {
            LABEL_MAP.get(labels[i], labels[i]): round(float(preds[i]) * 100, 2)
            for i in range(len(labels))
        }

        result.update({
            "available": True,
            "label": label,
            "confidence": round(confidence, 2),
            "all_predictions": dict(sorted(all_predictions.items(), key=lambda x: x[1], reverse=True)),
            "is_reliable": confidence >= CONFIDENCE_THRESHOLD,
            "info": PARASITE_DB.get(label, PARASITE_DB["Negative"])
        })
        return result
    except Exception as e:
        result["error"] = str(e)
        return result

def apply_thermal(image):
    enhanced = ImageEnhance.Contrast(image).enhance(1.6)
    gray = ImageOps.grayscale(enhanced)
    return ImageOps.colorize(gray, black="#0f172a", mid="#ef4444", white="#fde047")

def apply_edge_detection(image):
    gray = ImageOps.grayscale(image)
    return gray.filter(ImageFilter.FIND_EDGES)

def apply_enhanced_contrast(image):
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(image).enhance(2.2)).enhance(1.8)

def apply_stain_simulation(image):
    gray = ImageOps.grayscale(image)
    return ImageOps.colorize(gray, black="#3b0764", mid="#9333ea", white="#f5d0fe")

def generate_heatmap_overlay(image):
    img = image.convert("RGBA")
    w, h = img.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = w // 2, h // 2
    max_r = min(w, h) // 3
    for r in range(max_r, 0, -6):
        ratio = r / max_r
        if ratio > 0.66:
            color = (34, 197, 94, 24)
        elif ratio > 0.33:
            color = (250, 204, 21, 34)
        else:
            color = (239, 68, 68, 50)
        draw.ellipse((cx-r, cy-r, cx+r, cy+r), fill=color)
    return Image.alpha_composite(img, overlay).convert("RGB")

def estimate_image_quality(image):
    gray = ImageOps.grayscale(image)
    arr = np.array(gray).astype(np.float32)
    brightness = arr.mean()
    lap = np.array(gray.filter(ImageFilter.FIND_EDGES)).astype(np.float32)
    sharpness = lap.var()

    issues = []
    if brightness < 45:
        issues.append("dark")
    if brightness > 215:
        issues.append("bright")
    if sharpness < 180:
        issues.append("blur")

    score = 100
    if "dark" in issues:
        score -= 25
    if "bright" in issues:
        score -= 20
    if "blur" in issues:
        score -= 35
    score = max(score, 0)

    return {
        "brightness": round(float(brightness), 2),
        "sharpness": round(float(sharpness), 2),
        "issues": issues,
        "usable": len(issues) == 0 or (len(issues) == 1 and "blur" not in issues),
        "score": score
    }

def generate_pdf_bytes(patient, label, conf, info):
    try:
        from fpdf import FPDF
    except:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, t("pdf_title"), ln=True, align="C")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, t("pdf_subtitle"), ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, t("pdf_patient"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    for k, v in patient.items():
        pdf.multi_cell(0, 6, f"{k}: {v}")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, t("pdf_result"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, f"Label: {label}")
    pdf.multi_cell(0, 6, f"{t('scan_confidence')}: {conf}%")
    pdf.multi_cell(0, 6, f"{t('scan_morphology')}: {get_p_text(info, 'morphology')}")
    pdf.multi_cell(0, 6, f"Description: {get_p_text(info, 'description')}")

    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, t("pdf_advice"), ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, get_p_text(info, "advice"))

    extra = get_p_text(info, "extra_tests")
    if isinstance(extra, list):
        for item in extra:
            pdf.multi_cell(0, 6, f"- {item}")

    pdf.ln(4)
    pdf.set_font("Helvetica", "I", 9)
    pdf.multi_cell(0, 6, t("pdf_warning"))

    out = pdf.output(dest="S")
    if isinstance(out, bytearray):
        return bytes(out)
    if isinstance(out, str):
        return out.encode("latin-1", errors="replace")
    return out

def render_login():
    st.markdown('<div class="dm-shell">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dm-hero">
        <div class="logo-wrap">
            <div class="logo-ico">🔬</div>
            <div>
                <div class="logo-main">DM SMART LAB AI</div>
                <div class="logo-sub">Parasitology • AI • Clinical Support</div>
            </div>
        </div>
        <div class="hero-title">{t("login_title")}</div>
        <div class="hero-sub">{t("app_subtitle")}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.1, 1.6, 1.1])
    with c2:
        st.markdown('<div class="dm-card">', unsafe_allow_html=True)

        lang_options = {"العربية 🇩🇿": "ar", "Français 🇫🇷": "fr", "English 🇬🇧": "en"}
        current_lang_label = [k for k, v in lang_options.items() if v == st.session_state.lang][0]
        selected_lang = st.selectbox(t("language"), list(lang_options.keys()), index=list(lang_options.keys()).index(current_lang_label))
        if lang_options[selected_lang] != st.session_state.lang:
            st.session_state.lang = lang_options[selected_lang]
            st.rerun()

        if st.session_state.lockout_until:
            if datetime.now() < st.session_state.lockout_until:
                remain = int((st.session_state.lockout_until - datetime.now()).total_seconds())
                st.error(f"{t('login_locked')} - {remain}s")
                st.stop()
            else:
                st.session_state.lockout_until = None
                st.session_state.login_attempts = 0

        user = st.text_input(t("login_user"), placeholder="Doctor / TLS")
        pwd = st.text_input(t("login_pass"), type="password")

        if st.button(f"🔐 {t('login_btn')}", use_container_width=True):
            if pwd == APP_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.user_name = user.strip() if user.strip() else "Utilisateur"
                st.session_state.current_page = "intro"
                log_activity("Login success")
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                remaining = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
                if remaining <= 0:
                    st.session_state.lockout_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
                    st.error(t("login_locked"))
                else:
                    st.error(f"{t('login_error')} - {remaining}")

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_sidebar(model_name):
    with st.sidebar:
        st.markdown("""
        <div class="logo-wrap">
            <div class="logo-ico">🧬</div>
            <div>
                <div class="logo-main">DM SMART LAB AI</div>
                <div class="logo-sub">Ultimate Clinical Edition</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**👤 {st.session_state.user_name}**")
        st.caption(f"v{APP_VERSION}")

        if model_name:
            st.success(f"🧠 {t('scan_model_loaded')}: {model_name}")
        else:
            st.warning(f"🧠 {t('scan_no_model')}")

        lang_options = {"العربية 🇩🇿": "ar", "Français 🇫🇷": "fr", "English 🇬🇧": "en"}
        current_lang_label = [k for k, v in lang_options.items() if v == st.session_state.lang][0]
        selected_lang = st.selectbox(t("language"), list(lang_options.keys()), index=list(lang_options.keys()).index(current_lang_label), key="sidebar_lang")
        if lang_options[selected_lang] != st.session_state.lang:
            st.session_state.lang = lang_options[selected_lang]
            st.rerun()

        dark = st.toggle(t("night_mode"), value=st.session_state.dark_mode)
        if dark != st.session_state.dark_mode:
            st.session_state.dark_mode = dark
            st.rerun()

        voice_label = t("voice_off") if st.session_state.voice_enabled else t("voice_on")
        if st.button(f"🔊 {voice_label}", use_container_width=True):
            st.session_state.voice_enabled = not st.session_state.voice_enabled
            st.rerun()

        st.markdown("---")

        navs = {
            f"🔬 {t('nav_scan')}": "scan",
            f"📘 {t('nav_encyclopedia')}": "encyclopedia",
            f"📊 {t('nav_dashboard')}": "dashboard",
            f"🧠 {t('nav_quiz')}": "quiz",
            f"💬 {t('nav_chatbot')}": "chatbot",
            f"ℹ️ {t('nav_about')}": "about",
        }

        current_label = None
        for label, value in navs.items():
            if value == st.session_state.current_page:
                current_label = label
                break
        if current_label is None:
            current_label = list(navs.keys())[0]

        selected = st.radio("Navigation", list(navs.keys()), index=list(navs.keys()).index(current_label))
        st.session_state.current_page = navs[selected]

        st.markdown("---")
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_name = ""
            st.session_state.current_page = "intro"
            st.session_state.intro_done = False
            log_activity("Logout")
            st.rerun()

def render_intro():
    st.markdown('<div class="dm-shell">', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="dm-hero">
        <div class="hero-title">{t('app_title')}</div>
        <div class="hero-sub">{t('app_subtitle')}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.25, 1, 1.25])

    with c1:
        st.markdown(f"""
        <div class="avatar-card">
            <div class="avatar-circle">🧑‍💻</div>
            <div class="avatar-name">{AUTHORS['dev1']['name']}</div>
            <div class="avatar-role">{AUTHORS['dev1']['role']}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="microscope-zone">
            {microscope_svg()}
            <div class="speech-box">
                {t('intro_text')}
                <span class="pulse-dot"></span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="avatar-card">
            <div class="avatar-circle">🧪</div>
            <div class="avatar-name">{AUTHORS['dev2']['name']}</div>
            <div class="avatar-role">{AUTHORS['dev2']['role']}</div>
        </div>
        """, unsafe_allow_html=True)

    autoplay_tts(t("intro_text"), "ar" if get_lang() == "ar" else "fr" if get_lang() == "fr" else "en")
    st.info("⏳ Auto redirect...")
    time.sleep(4)
    st.session_state.intro_done = True
    st.session_state.current_page = "scan"
    st.rerun()

def render_scan(model, model_name, labels):
    st.title(f"🔬 {t('scan_title')}")

    st.markdown('<div class="dm-card">', unsafe_allow_html=True)
    st.subheader(f"📋 {t('scan_patient_info')}")
    col1, col2 = st.columns(2)
    p_nom = col1.text_input(f"{t('scan_nom')} *")
    p_prenom = col2.text_input(t("scan_prenom"))
    c3, c4, c5, c6 = st.columns(4)
    p_age = c3.number_input(t("scan_age"), 0, 120, 30)
    p_sexe = c4.selectbox(t("scan_sexe"), [t("patient_sexe_h"), t("patient_sexe_f")])
    p_poids = c5.number_input(t("scan_poids"), 0, 300, 70)
    p_type = c6.selectbox(t("scan_echantillon"), [
        t("echantillon_selles"),
        t("echantillon_sang_frottis"),
        t("echantillon_sang_goutte"),
        t("echantillon_urines"),
        t("echantillon_lcr"),
        t("echantillon_autre")
    ])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dm-card">', unsafe_allow_html=True)
    st.markdown("""
    <span class="tag">💧 Fresh / État frais</span>
    <span class="tag">🎨 Coloration</span>
    <span class="tag">🔥 Thermal</span>
    <span class="tag">📐 Edge</span>
    <span class="tag">✨ Enhanced</span>
    """, unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    thermal = f1.toggle("🔥 Thermal")
    edge = f2.toggle("📐 Edge")
    enhanced = f3.toggle("✨ Enhanced")
    stain = f4.toggle("🎨 Coloration")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dm-card lens-frame">', unsafe_allow_html=True)
    st.markdown(f'<div class="lens-title">📸 {t("scan_capture")}</div>', unsafe_allow_html=True)
    mode = st.radio("", [f"📷 {t('scan_camera')}", f"📁 {t('scan_upload')}"], horizontal=True)

    img_file = None
    if t("scan_camera") in mode:
        img_file = st.camera_input("Microscope Lens")
    else:
        img_file = st.file_uploader(t("scan_upload"), type=["jpg", "jpeg", "png", "bmp", "webp"])
    st.markdown('</div>', unsafe_allow_html=True)

    if img_file:
        if not p_nom.strip():
            st.error(t("scan_required_name"))
            return

        image = Image.open(img_file).convert("RGB")
        quality = estimate_image_quality(image)

        if quality["usable"]:
            st.markdown(f'<div class="good-box">✅ {t("quality_good")} — Score: {quality["score"]}/100</div>', unsafe_allow_html=True)
        else:
            msgs = []
            if "blur" in quality["issues"]:
                msgs.append(t("quality_blur"))
            if "dark" in quality["issues"]:
                msgs.append(t("quality_dark"))
            if "bright" in quality["issues"]:
                msgs.append(t("quality_bright"))
            st.markdown(f'<div class="warning-box">⚠️ {t("quality_bad")} — {", ".join(msgs)}<br>{t("quality_retake")}</div>', unsafe_allow_html=True)

        ci, cr = st.columns([1.2, 1])

        with ci:
            tabs = st.tabs(["Original", "Thermal", "Edges", "Enhanced", "Coloration", t("scan_heatmap")])
            with tabs[0]:
                st.image(image, use_container_width=True)
            with tabs[1]:
                st.image(apply_thermal(image), use_container_width=True)
            with tabs[2]:
                st.image(apply_edge_detection(image), use_container_width=True)
            with tabs[3]:
                st.image(apply_enhanced_contrast(image), use_container_width=True)
            with tabs[4]:
                st.image(apply_stain_simulation(image), use_container_width=True)
            with tabs[5]:
                st.image(generate_heatmap_overlay(image), use_container_width=True)

        img_for_prediction = image.copy()
        if thermal:
            img_for_prediction = apply_thermal(img_for_prediction).convert("RGB")
        if edge:
            img_for_prediction = apply_edge_detection(img_for_prediction).convert("RGB")
        if enhanced:
            img_for_prediction = apply_enhanced_contrast(img_for_prediction).convert("RGB")
        if stain:
            img_for_prediction = apply_stain_simulation(img_for_prediction).convert("RGB")

        with cr:
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.subheader(f"🧠 {t('scan_result')}")

            if model is None:
                st.error(t("scan_no_model"))
                st.markdown("ضع ملف الموديل الحقيقي داخل نفس المجلد: `.keras` أو `.h5` أو `.tflite`")
                st.markdown('</div>', unsafe_allow_html=True)
                return

            if not quality["usable"]:
                st.warning(t("quality_retake"))
                st.markdown('</div>', unsafe_allow_html=True)
                return

            with st.spinner(t("scan_analyzing")):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.005)
                    prog.progress(i + 1)
                result = predict_image(model, labels, img_for_prediction)

            if not result["available"]:
                st.error(f"Prediction error: {result['error']}")
                st.markdown('</div>', unsafe_allow_html=True)
                return

            label = result["label"]
            conf = result["confidence"]
            info = result["info"]
            rc = risk_color(info["risk_level"])

            st.markdown(f"""
            <h2 style="margin-bottom:0;color:{rc};">{label}</h2>
            <div style="opacity:0.75;font-style:italic;margin-bottom:8px;">{info["scientific_name"]}</div>
            <div class="chip">📊 {t("scan_confidence")}: {conf}%</div>
            <div class="chip">⚠️ {t("scan_risk")}: {get_p_text(info, "risk_display")}</div>
            <div class="chip">🔬 Quality: {quality["score"]}/100</div>
            """, unsafe_allow_html=True)

            if not result["is_reliable"]:
                st.warning(t("scan_low_conf"))

            st.markdown(f"**🔬 {t('scan_morphology')}**")
            st.write(get_p_text(info, "morphology"))

            st.markdown("**📝 Description**")
            st.write(get_p_text(info, "description"))

            st.markdown(f"**💡 {t('scan_advice')}**")
            st.write(get_p_text(info, "advice"))

            st.markdown(f"**🩺 {t('scan_extra_tests')}**")
            extra = get_p_text(info, "extra_tests")
            if isinstance(extra, list):
                for item in extra:
                    st.markdown(f"- {item}")

            with st.expander(f"📈 {t('scan_all_probs')}"):
                for cls, prob in result["all_predictions"].items():
                    st.progress(prob / 100, text=f"{cls}: {prob}%")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("---")
        a1, a2, a3 = st.columns(3)

        patient_data = {
            t("scan_nom"): p_nom,
            t("scan_prenom"): p_prenom,
            t("scan_age"): p_age,
            t("scan_sexe"): p_sexe,
            t("scan_poids"): p_poids,
            t("scan_echantillon"): p_type,
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        pdf_data = generate_pdf_bytes(patient_data, label, conf, info)

        with a1:
            if pdf_data:
                st.download_button(
                    f"📄 {t('scan_download_pdf')}",
                    data=pdf_data,
                    file_name=f"report_{p_nom}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        with a2:
            if st.button(f"💾 {t('scan_save')}", use_container_width=True):
                entry = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Patient": f"{p_nom} {p_prenom}".strip(),
                    "Age": p_age,
                    "Sexe": p_sexe,
                    "Poids": p_poids,
                    "Echantillon": p_type,
                    "Parasite": label,
                    "Confiance": conf,
                    "Risque": get_p_text(info, "risk_display"),
                    "QualityScore": quality["score"],
                    "Status": "Reliable" if result["is_reliable"] else "Review",
                    "Model": model_name if model_name else "N/A"
                }
                st.session_state.history.append(entry)
                safe_save_json(HISTORY_FILE, st.session_state.history)
                log_activity(f"Saved analysis for {p_nom}: {label}")
                st.success(t("scan_saved"))

        with a3:
            if st.button(f"🔄 {t('scan_new')}", use_container_width=True):
                st.rerun()

def render_encyclopedia():
    st.title(f"📘 {t('enc_title')}")
    q = st.text_input(f"🔍 {t('enc_search')}")
    for name, data in PARASITE_DB.items():
        if q.strip() and q.lower() not in name.lower() and q.lower() not in data["scientific_name"].lower():
            continue
        rc = risk_color(data["risk_level"])
        with st.expander(f"{data['icon']} {name} — {data['scientific_name']}"):
            st.markdown(f"""
            <div class="dm-card" style="border-left: 5px solid {rc};">
                <h3 style="margin-bottom:0;color:{rc};">{name}</h3>
                <p style="opacity:0.8;font-style:italic;">{data['scientific_name']}</p>
                <p><b>{t('scan_morphology')}:</b> {get_p_text(data, 'morphology')}</p>
                <p><b>Description:</b> {get_p_text(data, 'description')}</p>
                <p><b>{t('scan_risk')}:</b> {get_p_text(data, 'risk_display')}</p>
                <p><b>{t('scan_advice')}:</b> {get_p_text(data, 'advice')}</p>
            </div>
            """, unsafe_allow_html=True)

def render_dashboard():
    st.title(f"📊 {t('dash_title')}")
    hist = st.session_state.history
    if not hist:
        st.info(t("dash_no_data"))
        return

    df = pd.DataFrame(hist)
    total = len(df)
    reliable = df[df["Status"] == "Reliable"].shape[0] if "Status" in df.columns else 0
    review = total - reliable
    common = df["Parasite"].value_counts().idxmax() if "Parasite" in df.columns else "-"

    m1, m2, m3, m4 = st.columns(4)
    for col, val, lbl in [
        (m1, total, t("dash_total")),
        (m2, reliable, t("dash_reliable")),
        (m3, review, t("dash_check")),
        (m4, common, t("dash_frequent")),
    ]:
        with col:
            st.markdown(f"""
            <div class="dm-metric">
                <div class="dm-metric-val">{val}</div>
                <div class="dm-metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if "Parasite" in df.columns:
            st.subheader(t("dash_distribution"))
            st.bar_chart(df["Parasite"].value_counts())
    with c2:
        if "Confiance" in df.columns:
            st.subheader("Confidence trend")
            st.line_chart(df["Confiance"].astype(float).reset_index(drop=True))

    st.markdown("---")
    st.subheader(t("dash_history"))
    st.dataframe(df, use_container_width=True)

    e1, e2, e3 = st.columns(3)
    with e1:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(t("dash_export_csv"), data=csv, file_name="analyses.csv", mime="text/csv", use_container_width=True)
    with e2:
        js = df.to_json(orient="records", force_ascii=False).encode("utf-8")
        st.download_button(t("dash_export_json"), data=js, file_name="analyses.json", mime="application/json", use_container_width=True)
    with e3:
        buf = io.BytesIO()
        try:
            df.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                t("dash_export_excel"),
                data=buf.getvalue(),
                file_name="analyses.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Excel export error: {e}")

    if st.session_state.activity_log:
        with st.expander(f"📜 {t('activity_log')}"):
            st.dataframe(pd.DataFrame(st.session_state.activity_log), use_container_width=True)

def render_quiz():
    st.title(f"🧠 {t('quiz_title')}")
    questions = QUIZ_QUESTIONS[get_lang()]

    if not st.session_state.quiz_started:
        if st.button(f"🎮 {t('quiz_start')}", use_container_width=True):
            st.session_state.quiz_started = True
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.last_feedback = ""
            log_activity("Quiz started")
            st.rerun()
        return

    idx = st.session_state.quiz_index
    if idx >= len(questions):
        score = st.session_state.quiz_score
        pct = int(score / len(questions) * 100)
        st.success(f"{t('quiz_finish')}: {score}/{len(questions)} ({pct}%)")
        if st.button(f"🔄 {t('quiz_restart')}", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.last_feedback = ""
            st.rerun()
        return

    q = questions[idx]
    st.progress(idx / len(questions))
    st.markdown(f'<div class="dm-card"><h3>{q["q"]}</h3></div>', unsafe_allow_html=True)

    for i, opt in enumerate(q["options"]):
        if st.button(opt, key=f"quiz_{idx}_{i}", use_container_width=True):
            if i == q["answer"]:
                st.session_state.quiz_score += 1
                st.session_state.last_feedback = "✅ Correct" if get_lang() != "ar" else "✅ إجابة صحيحة"
            else:
                correct = q["options"][q["answer"]]
                st.session_state.last_feedback = f"❌ {correct}"
            st.session_state.quiz_index += 1
            st.rerun()

    if st.session_state.last_feedback:
        st.info(st.session_state.last_feedback)

def chatbot_reply(msg):
    lang = get_lang()
    db = CHATBOT_KNOWLEDGE[lang]
    text = msg.lower().strip()

    for k, v in db.items():
        if k.lower() in text:
            return v

    for name, info in PARASITE_DB.items():
        if name.lower() in text or info["scientific_name"].lower() in text:
            return f"""**{name}**
- {get_p_text(info, 'description')}
- {t('scan_morphology')}: {get_p_text(info, 'morphology')}
- {t('scan_advice')}: {get_p_text(info, 'advice')}
"""
    if lang == "ar":
        return "أنا المساعد الطبي. اسألني عن: أميبا، جيارديا، ليشمانيا، بلازموديوم، تريبانوسوما، بلهارسيا."
    if lang == "fr":
        return "Je suis l'assistant médical. Posez-moi une question sur Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma ou Schistosoma."
    return "I am the medical assistant. Ask me about Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma or Schistosoma."

def render_chatbot():
    st.title(f"💬 {t('chatbot_title')}")

    if not st.session_state.chat_history:
        welcome = {
            "ar": "مرحبًا، أنا مساعدك الطبي الذكي. كيف أساعدك؟",
            "fr": "Bonjour, je suis votre assistant médical intelligent. Comment puis-je vous aider ?",
            "en": "Hello, I am your smart medical assistant. How can I help?",
        }
        st.session_state.chat_history.append({"role": "bot", "msg": welcome[get_lang()]})
        safe_save_json(CHAT_FILE, st.session_state.chat_history)

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="chat-user">👤 {msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bot">🤖 {msg["msg"]}</div>', unsafe_allow_html=True)

    user_input = st.chat_input(t("chatbot_placeholder"))
    if user_input:
        st.session_state.chat_history.append({"role": "user", "msg": user_input})
        rep = chatbot_reply(user_input)
        st.session_state.chat_history.append({"role": "bot", "msg": rep})
        safe_save_json(CHAT_FILE, st.session_state.chat_history)
        log_activity(f"Chat used: {user_input[:40]}")
        st.rerun()

    st.markdown("---")
    q1, q2, q3, q4 = st.columns(4)
    quick = {
        "ar": ["أميبا", "جيارديا", "ملاريا", "بلهارسيا"],
        "fr": ["Amoeba", "Giardia", "Paludisme", "Schistosoma"],
        "en": ["Amoeba", "Giardia", "Malaria", "Schistosoma"],
    }
    for col, txt in zip([q1, q2, q3, q4], quick[get_lang()]):
        with col:
            if st.button(txt, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": txt})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(txt)})
                safe_save_json(CHAT_FILE, st.session_state.chat_history)
                st.rerun()

    if st.button(f"🗑️ {t('clear_chat')}", use_container_width=True):
        st.session_state.chat_history = []
        safe_save_json(CHAT_FILE, [])
        st.rerun()

def render_about():
    st.title(f"ℹ️ {t('about_title')}")
    st.markdown(f"""
    <div class="dm-hero">
        <div class="hero-title">DM SMART LAB AI v{APP_VERSION}</div>
        <div class="hero-sub">{PROJECT_TITLE}</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="dm-card">
            <h3>👨‍🔬 Team</h3>
            <p><b>{AUTHORS['dev1']['name']}</b><br>{AUTHORS['dev1']['role']}</p>
            <p><b>{AUTHORS['dev2']['name']}</b><br>{AUTHORS['dev2']['role']}</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="dm-card">
            <h3>🏫 Institution</h3>
            <p><b>{INSTITUTION['name']}</b></p>
            <p>{INSTITUTION['city']}, {INSTITUTION['country']} — {INSTITUTION['year']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="dm-card">
        <h3>✨ Features</h3>
        <p>🔬 Teachable Machine optimized preprocessing</p>
        <p>🎨 Stain simulation</p>
        <p>🔥 Thermal / Edge / Enhanced filters</p>
        <p>🎯 Heatmap focus area</p>
        <p>🧪 Image quality detector</p>
        <p>💬 Better chatbot</p>
        <p>🧠 Better quiz</p>
        <p>📊 Persistent dashboard</p>
        <p>📄 PDF export</p>
        <p>🌍 Better Arabic support</p>
    </div>
    """, unsafe_allow_html=True)

model, model_name, labels = load_ai_model()

if not st.session_state.logged_in:
    render_login()
    st.stop()

render_sidebar(model_name)

if st.session_state.current_page == "intro":
    render_intro()
elif st.session_state.current_page == "scan":
    render_scan(model, model_name, labels)
elif st.session_state.current_page == "encyclopedia":
    render_encyclopedia()
elif st.session_state.current_page == "dashboard":
    render_dashboard()
elif st.session_state.current_page == "quiz":
    render_quiz()
elif st.session_state.current_page == "chatbot":
    render_chatbot()
elif st.session_state.current_page == "about":
    render_about()
else:
    render_scan(model, model_name, labels)

