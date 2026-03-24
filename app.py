# ╔══════════════════════════════════════════════════════════════════════════╗
# ║              DM SMART LAB AI v5.0 - PROFESSIONAL EDITION               ║
# ║       Diagnostic Parasitologique par Intelligence Artificielle          ║
# ║                                                                        ║
# ║  Développé par:                                                        ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)               ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                  ║
# ║                                                                        ║
# ║  INFSPM - Ouargla, Algérie                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝

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
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
from datetime import datetime, timedelta
from fpdf import FPDF

# ============================================
#  1. إعداد الصفحة - تحسين SEO والأداء
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI - Diagnostic Parasitologique",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/dm-smart-lab',
        'Report a bug': None,
        'About': "DM Smart Lab AI v5.0 - Système de diagnostic parasitologique par IA"
    }
)

# ============================================
#  2. الثوابت المحسنة
# ============================================
APP_VERSION = "5.0.0"
APP_PASSWORD_HASH = hashlib.sha256("123".encode()).hexdigest()  # ✅ تشفير كلمة المرور
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)
AUTO_LOCK_MINUTES = 15
MAX_HISTORY = 500  # ✅ حد أقصى للسجل

AUTHORS = {
    "dev1": {"name": "Sebbag Mohamed Dhia Eddine", "role": "Expert IA & Conception", "icon": "🧑‍💻"},
    "dev2": {"name": "Ben Sghir Mohamed", "role": "Expert Laboratoire & Données", "icon": "🔬"}
}

INSTITUTION = {
    "name": "Institut National de Formation Supérieure Paramédicale (INFSPM)",
    "city": "Ouargla",
    "country": "Algérie",
    "year": 2026
}

PROJECT_TITLE = (
    "Exploration du potentiel de l'intelligence artificielle "
    "pour la lecture automatique de l'examen parasitologique "
    "à l'état frais"
)

# ============================================
#  3. نظام اللغات المحسن
# ============================================
TRANSLATIONS = {
    "fr": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Où la Science Rencontre l'Intelligence",
        "login_title": "Connexion Sécurisée",
        "login_subtitle": "Accès Réservé au Personnel Médical Autorisé",
        "login_user": "Identifiant",
        "login_pass": "Mot de Passe",
        "login_btn": "SE CONNECTER",
        "login_error": "Mot de passe incorrect",
        "login_locked": "Compte verrouillé",
        "login_attempts": "tentative(s) restante(s)",
        "logout": "Déconnexion",
        "nav_home": "Accueil",
        "nav_scan": "Scan & Analyse",
        "nav_encyclopedia": "Encyclopédie",
        "nav_dashboard": "Tableau de Bord",
        "nav_about": "À Propos",
        "nav_quiz": "Quiz Médical",
        "nav_chatbot": "Dr. DhiaBot",
        "home_welcome": "Bienvenue",
        "home_step1_title": "Étape 1 : Présentation du Système",
        "home_step1_desc": "Cliquez pour lancer la présentation vocale du système IA.",
        "home_step1_btn": "LANCER LA PRÉSENTATION",
        "home_step2_title": "Étape 2 : Titre Officiel du Mémoire",
        "home_step2_desc": "Écoutez le titre complet du projet de fin d'études.",
        "home_step2_btn": "LIRE LE TITRE DU PROJET",
        "home_unlocked": "SYSTÈME DÉVERROUILLÉ AVEC SUCCÈS !",
        "home_go_scan": "Passez au module de diagnostic dans le menu latéral.",
        "scan_title": "Unité de Diagnostic Parasitologique",
        "scan_blocked": "Veuillez d'abord activer le système dans la page Accueil.",
        "scan_patient_info": "Informations du Patient",
        "scan_nom": "Nom",
        "scan_prenom": "Prénom",
        "scan_age": "Âge",
        "scan_sexe": "Sexe",
        "scan_poids": "Poids (kg)",
        "scan_echantillon": "Type d'Échantillon",
        "scan_thermal": "Vision Thermique",
        "scan_edge": "Détection de Contours",
        "scan_enhanced": "Contraste Amélioré",
        "scan_capture": "Capture Microscopique",
        "scan_camera": "Caméra (temps réel)",
        "scan_upload": "Importer une image",
        "scan_nom_required": "Le nom du patient est obligatoire !",
        "scan_analyzing": "Analyse IA en cours...",
        "scan_result": "Résultat de l'IA",
        "scan_confidence": "Confiance",
        "scan_morphology": "Morphologie",
        "scan_risk": "Risque",
        "scan_advice": "Conseil Médical",
        "scan_low_conf": "Confiance faible. Vérification manuelle recommandée !",
        "scan_demo_mode": "Mode démonstration (aucun modèle chargé)",
        "scan_download_pdf": "Télécharger le Rapport PDF",
        "scan_save": "Sauvegarder",
        "scan_saved": "Résultat sauvegardé avec succès !",
        "scan_new": "Nouvelle Analyse",
        "scan_all_probs": "Toutes les probabilités",
        "scan_extra_tests": "Examens complémentaires suggérés",
        "scan_heatmap": "Zone d'intérêt IA",
        "enc_title": "Encyclopédie des Parasites",
        "enc_search": "Rechercher un parasite...",
        "enc_no_result": "Aucun résultat trouvé.",
        "dash_title": "Tableau de Bord Clinique",
        "dash_total": "Total Analyses",
        "dash_reliable": "Fiables",
        "dash_check": "À Vérifier",
        "dash_frequent": "Plus Fréquent",
        "dash_system": "Système Opérationnel",
        "dash_user": "Utilisateur Actif",
        "dash_session": "Session Active",
        "dash_filter": "Filtrer par parasite",
        "dash_distribution": "Distribution des Parasites",
        "dash_confidence_chart": "Niveaux de Confiance",
        "dash_history": "Historique Complet",
        "dash_export": "Exporter en CSV",
        "dash_export_excel": "Exporter en Excel",
        "dash_export_json": "Exporter en JSON",
        "dash_no_data": "Aucune donnée disponible",
        "dash_no_data_desc": "Effectuez votre première analyse pour voir les statistiques.",
        "dash_patient_compare": "Comparer les analyses d'un patient",
        "about_title": "À Propos du Projet",
        "about_desc": "Système de Diagnostic Parasitologique par IA",
        "about_project_desc": (
            "Ce projet innovant utilise les technologies de Deep Learning "
            "et de Vision par Ordinateur pour assister les techniciens de "
            "laboratoire dans l'identification rapide et précise des "
            "parasites lors de l'examen parasitologique des selles à "
            "l'état frais."
        ),
        "about_team": "Équipe de Développement",
        "about_institution": "Établissement",
        "about_objectives": "Objectifs",
        "about_obj1": "Automatiser la lecture microscopique",
        "about_obj2": "Réduire les erreurs diagnostiques",
        "about_obj3": "Accélérer le processus d'analyse",
        "about_obj4": "Assister les professionnels de santé",
        "about_tech": "Technologies Utilisées",
        "night_mode": "Mode Nuit",
        "language": "Langue",
        "patient_sexe_h": "Homme",
        "patient_sexe_f": "Femme",
        "echantillon_selles": "Selles",
        "echantillon_sang_frottis": "Sang (Frottis)",
        "echantillon_sang_goutte": "Sang (Goutte épaisse)",
        "echantillon_urines": "Urines",
        "echantillon_lcr": "LCR",
        "echantillon_autre": "Autre",
        "voice_intro": (
            "Bonjour ! Il est {time}. Je suis DM Smart Lab, "
            "intelligence artificielle développée par les Techniciens "
            "Supérieurs {dev1} et {dev2}. "
            "Préparez vos lames, et s'il vous plaît, "
            "ne me chatouillez pas avec le microscope !"
        ),
        "voice_title": (
            "Mémoire de Fin d'Études : {title}. "
            "Institut National de Formation Supérieure "
            "Paramédicale de Ouargla."
        ),
        "voice_result": "Résultat pour {patient} : {parasite}. {funny}",
        "quiz_title": "Quiz Parasitologique",
        "quiz_desc": "Testez vos connaissances en parasitologie !",
        "quiz_question": "Question",
        "quiz_score": "Score",
        "quiz_correct": "Bonne réponse !",
        "quiz_wrong": "Mauvaise réponse.",
        "quiz_next": "Question Suivante",
        "quiz_finish": "Résultat Final",
        "quiz_restart": "Recommencer",
        "chatbot_title": "Dr. DhiaBot - Assistant Médical IA",
        "chatbot_placeholder": "Posez votre question sur les parasites...",
        "chatbot_thinking": "Dr. DhiaBot réfléchit...",
        "daily_tip": "Conseil du Jour",
        "activity_log": "Journal d'Activité",
        "pdf_title": "RAPPORT D'ANALYSE PARASITOLOGIQUE",
        "pdf_subtitle": "Analyse assistée par Intelligence Artificielle",
        "pdf_patient_section": "INFORMATIONS DU PATIENT",
        "pdf_result_section": "RESULTAT DE L'ANALYSE IA",
        "pdf_advice_section": "RECOMMANDATIONS CLINIQUES",
        "pdf_validation": "VALIDATION",
        "pdf_technician": "Technicien de Laboratoire",
        "pdf_disclaimer": "Ce rapport est genere par un systeme d'IA et doit etre valide par un professionnel de sante.",
        "stats_weekly": "Statistiques Hebdomadaires",
        "stats_monthly": "Statistiques Mensuelles",
        "scan_duration": "Durée d'analyse",
        "scan_image_quality": "Qualité de l'image",
        "theme_auto": "Thème Automatique",
    },
    "ar": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "حيث يلتقي العلم بالذكاء",
        "login_title": "تسجيل الدخول الآمن",
        "login_subtitle": "الدخول مخصص للكوادر الطبية المعتمدة فقط",
        "login_user": "اسم المستخدم",
        "login_pass": "كلمة المرور",
        "login_btn": "تسجيل الدخول",
        "login_error": "كلمة المرور غير صحيحة",
        "login_locked": "الحساب مقفل",
        "login_attempts": "محاولة(ات) متبقية",
        "logout": "تسجيل الخروج",
        "nav_home": "الرئيسية",
        "nav_scan": "الفحص والتحليل",
        "nav_encyclopedia": "الموسوعة",
        "nav_dashboard": "لوحة التحكم",
        "nav_about": "حول المشروع",
        "nav_quiz": "اختبار طبي",
        "nav_chatbot": "المساعد الذكي",
        "home_welcome": "مرحباً",
        "home_step1_title": "الخطوة 1 : تقديم النظام",
        "home_step1_desc": "اضغط لتشغيل العرض الصوتي.",
        "home_step1_btn": "بدء العرض",
        "home_step2_title": "الخطوة 2 : عنوان المشروع",
        "home_step2_desc": "استمع للعنوان الكامل.",
        "home_step2_btn": "قراءة العنوان",
        "home_unlocked": "تم فتح النظام بنجاح !",
        "home_go_scan": "انتقل إلى وحدة التشخيص.",
        "scan_title": "وحدة التشخيص الطفيلي",
        "scan_blocked": "يرجى تفعيل النظام أولاً.",
        "scan_patient_info": "بيانات المريض",
        "scan_nom": "اللقب",
        "scan_prenom": "الاسم",
        "scan_age": "العمر",
        "scan_sexe": "الجنس",
        "scan_poids": "الوزن (كغ)",
        "scan_echantillon": "نوع العينة",
        "scan_thermal": "الرؤية الحرارية",
        "scan_edge": "كشف الحواف",
        "scan_enhanced": "تحسين التباين",
        "scan_capture": "التصوير المجهري",
        "scan_camera": "الكاميرا",
        "scan_upload": "استيراد صورة",
        "scan_nom_required": "اسم المريض إجباري !",
        "scan_analyzing": "جاري التحليل...",
        "scan_result": "نتيجة الذكاء الاصطناعي",
        "scan_confidence": "نسبة الثقة",
        "scan_morphology": "الشكل المورفولوجي",
        "scan_risk": "مستوى الخطورة",
        "scan_advice": "النصيحة الطبية",
        "scan_low_conf": "نسبة ثقة منخفضة !",
        "scan_demo_mode": "وضع العرض التوضيحي",
        "scan_download_pdf": "تحميل التقرير",
        "scan_save": "حفظ",
        "scan_saved": "تم الحفظ !",
        "scan_new": "تحليل جديد",
        "scan_all_probs": "جميع الاحتمالات",
        "scan_extra_tests": "فحوصات إضافية مقترحة",
        "scan_heatmap": "منطقة اهتمام الذكاء",
        "enc_title": "موسوعة الطفيليات",
        "enc_search": "ابحث...",
        "enc_no_result": "لا توجد نتائج.",
        "dash_title": "لوحة التحكم",
        "dash_total": "إجمالي التحاليل",
        "dash_reliable": "موثوقة",
        "dash_check": "تحتاج مراجعة",
        "dash_frequent": "الأكثر شيوعاً",
        "dash_system": "النظام يعمل",
        "dash_user": "المستخدم النشط",
        "dash_session": "الجلسة النشطة",
        "dash_filter": "تصفية",
        "dash_distribution": "توزيع الطفيليات",
        "dash_confidence_chart": "مستويات الثقة",
        "dash_history": "السجل الكامل",
        "dash_export": "تصدير CSV",
        "dash_export_excel": "تصدير Excel",
        "dash_export_json": "تصدير JSON",
        "dash_no_data": "لا توجد بيانات",
        "dash_no_data_desc": "قم بإجراء تحليل.",
        "dash_patient_compare": "مقارنة تحاليل مريض",
        "about_title": "حول المشروع",
        "about_desc": "نظام التشخيص الطفيلي بالذكاء الاصطناعي",
        "about_project_desc": "يستخدم هذا المشروع التعلم العميق لمساعدة تقنيي المخابر.",
        "about_team": "فريق التطوير",
        "about_institution": "المؤسسة",
        "about_objectives": "الأهداف",
        "about_obj1": "أتمتة القراءة المجهرية",
        "about_obj2": "تقليل أخطاء التشخيص",
        "about_obj3": "تسريع عملية التحليل",
        "about_obj4": "مساعدة المهنيين الصحيين",
        "about_tech": "التقنيات المستخدمة",
        "night_mode": "الوضع الليلي",
        "language": "اللغة",
        "patient_sexe_h": "ذكر",
        "patient_sexe_f": "أنثى",
        "echantillon_selles": "براز",
        "echantillon_sang_frottis": "دم (لطاخة)",
        "echantillon_sang_goutte": "دم (قطرة سميكة)",
        "echantillon_urines": "بول",
        "echantillon_lcr": "سائل دماغي شوكي",
        "echantillon_autre": "أخرى",
        "voice_intro": "مرحباً! الساعة {time}. أنا DM Smart Lab. طوّرني {dev1} و{dev2}.",
        "voice_title": "مذكرة تخرج: {title}. معهد التكوين العالي شبه الطبي بورقلة.",
        "voice_result": "النتيجة لـ {patient}: {parasite}. {funny}",
        "quiz_title": "اختبار طفيليات",
        "quiz_desc": "اختبر معلوماتك!",
        "quiz_question": "سؤال",
        "quiz_score": "النتيجة",
        "quiz_correct": "إجابة صحيحة!",
        "quiz_wrong": "إجابة خاطئة.",
        "quiz_next": "السؤال التالي",
        "quiz_finish": "النتيجة النهائية",
        "quiz_restart": "إعادة",
        "chatbot_title": "المساعد الطبي الذكي",
        "chatbot_placeholder": "اسأل عن الطفيليات...",
        "chatbot_thinking": "المساعد يفكر...",
        "daily_tip": "نصيحة اليوم",
        "activity_log": "سجل النشاطات",
        "pdf_title": "تقرير التحليل الطفيلي",
        "pdf_subtitle": "تحليل بمساعدة الذكاء الاصطناعي",
        "pdf_patient_section": "بيانات المريض",
        "pdf_result_section": "نتيجة التحليل",
        "pdf_advice_section": "التوصيات السريرية",
        "pdf_validation": "المصادقة",
        "pdf_technician": "تقني المخبر",
        "pdf_disclaimer": "هذا التقرير مولد بنظام ذكاء اصطناعي.",
        "stats_weekly": "إحصائيات أسبوعية",
        "stats_monthly": "إحصائيات شهرية",
        "scan_duration": "مدة التحليل",
        "scan_image_quality": "جودة الصورة",
        "theme_auto": "ثيم تلقائي",
    },
    "en": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Where Science Meets Intelligence",
        "login_title": "Secure Login",
        "login_subtitle": "Access Reserved for Authorized Medical Staff",
        "login_user": "Username",
        "login_pass": "Password",
        "login_btn": "LOG IN",
        "login_error": "Incorrect password",
        "login_locked": "Account locked",
        "login_attempts": "attempt(s) remaining",
        "logout": "Log Out",
        "nav_home": "Home",
        "nav_scan": "Scan & Analyse",
        "nav_encyclopedia": "Encyclopedia",
        "nav_dashboard": "Dashboard",
        "nav_about": "About",
        "nav_quiz": "Medical Quiz",
        "nav_chatbot": "Dr. DhiaBot",
        "home_welcome": "Welcome",
        "home_step1_title": "Step 1: System Presentation",
        "home_step1_desc": "Click to launch voice presentation.",
        "home_step1_btn": "LAUNCH PRESENTATION",
        "home_step2_title": "Step 2: Official Project Title",
        "home_step2_desc": "Listen to the full thesis title.",
        "home_step2_btn": "READ PROJECT TITLE",
        "home_unlocked": "SYSTEM UNLOCKED!",
        "home_go_scan": "Go to diagnostic module.",
        "scan_title": "Parasitological Diagnostic Unit",
        "scan_blocked": "Please activate the system first.",
        "scan_patient_info": "Patient Information",
        "scan_nom": "Last Name",
        "scan_prenom": "First Name",
        "scan_age": "Age",
        "scan_sexe": "Sex",
        "scan_poids": "Weight (kg)",
        "scan_echantillon": "Sample Type",
        "scan_thermal": "Thermal Vision",
        "scan_edge": "Edge Detection",
        "scan_enhanced": "Enhanced Contrast",
        "scan_capture": "Microscopic Capture",
        "scan_camera": "Camera",
        "scan_upload": "Upload image",
        "scan_nom_required": "Patient name is required!",
        "scan_analyzing": "AI Analysis in progress...",
        "scan_result": "AI Result",
        "scan_confidence": "Confidence",
        "scan_morphology": "Morphology",
        "scan_risk": "Risk",
        "scan_advice": "Medical Advice",
        "scan_low_conf": "Low confidence!",
        "scan_demo_mode": "Demo mode",
        "scan_download_pdf": "Download PDF",
        "scan_save": "Save",
        "scan_saved": "Saved!",
        "scan_new": "New Analysis",
        "scan_all_probs": "All probabilities",
        "scan_extra_tests": "Suggested additional tests",
        "scan_heatmap": "AI Focus Area",
        "enc_title": "Parasite Encyclopedia",
        "enc_search": "Search...",
        "enc_no_result": "No results.",
        "dash_title": "Clinical Dashboard",
        "dash_total": "Total Analyses",
        "dash_reliable": "Reliable",
        "dash_check": "To Verify",
        "dash_frequent": "Most Frequent",
        "dash_system": "System OK",
        "dash_user": "Active User",
        "dash_session": "Active Session",
        "dash_filter": "Filter",
        "dash_distribution": "Distribution",
        "dash_confidence_chart": "Confidence Levels",
        "dash_history": "Full History",
        "dash_export": "Export CSV",
        "dash_export_excel": "Export Excel",
        "dash_export_json": "Export JSON",
        "dash_no_data": "No data",
        "dash_no_data_desc": "Perform an analysis.",
        "dash_patient_compare": "Compare patient analyses",
        "about_title": "About",
        "about_desc": "AI Parasitological Diagnostic System",
        "about_project_desc": "This project uses Deep Learning to assist lab technicians.",
        "about_team": "Development Team",
        "about_institution": "Institution",
        "about_objectives": "Objectives",
        "about_obj1": "Automate microscopic reading",
        "about_obj2": "Reduce diagnostic errors",
        "about_obj3": "Speed up analysis",
        "about_obj4": "Assist healthcare professionals",
        "about_tech": "Technologies Used",
        "night_mode": "Night Mode",
        "language": "Language",
        "patient_sexe_h": "Male",
        "patient_sexe_f": "Female",
        "echantillon_selles": "Stool",
        "echantillon_sang_frottis": "Blood (Smear)",
        "echantillon_sang_goutte": "Blood (Thick drop)",
        "echantillon_urines": "Urine",
        "echantillon_lcr": "CSF",
        "echantillon_autre": "Other",
        "voice_intro": "Hello! It is {time}. I am DM Smart Lab. Developed by {dev1} and {dev2}.",
        "voice_title": "Thesis: {title}. INFSPM Ouargla.",
        "voice_result": "Result for {patient}: {parasite}. {funny}",
        "quiz_title": "Parasitology Quiz",
        "quiz_desc": "Test your knowledge!",
        "quiz_question": "Question",
        "quiz_score": "Score",
        "quiz_correct": "Correct!",
        "quiz_wrong": "Wrong.",
        "quiz_next": "Next Question",
        "quiz_finish": "Final Result",
        "quiz_restart": "Restart",
        "chatbot_title": "Dr. DhiaBot - AI Medical Assistant",
        "chatbot_placeholder": "Ask about parasites...",
        "chatbot_thinking": "Dr. DhiaBot is thinking...",
        "daily_tip": "Daily Tip",
        "activity_log": "Activity Log",
        "pdf_title": "PARASITOLOGICAL ANALYSIS REPORT",
        "pdf_subtitle": "AI-Assisted Analysis",
        "pdf_patient_section": "PATIENT INFORMATION",
        "pdf_result_section": "AI ANALYSIS RESULT",
        "pdf_advice_section": "CLINICAL RECOMMENDATIONS",
        "pdf_validation": "VALIDATION",
        "pdf_technician": "Lab Technician",
        "pdf_disclaimer": "This report is AI-generated.",
        "stats_weekly": "Weekly Statistics",
        "stats_monthly": "Monthly Statistics",
        "scan_duration": "Analysis Duration",
        "scan_image_quality": "Image Quality",
        "theme_auto": "Auto Theme",
    }
}

# ============================================
#  4. قاعدة بيانات الطفيليات الشاملة
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {
            "fr": "Kyste spherique (10-15um) a 4 noyaux ou Trophozoite avec pseudopodes et hematies phagocytees.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 نوى أو طور غاذي بأقدام كاذبة.",
            "en": "Spherical cyst (10-15um) with 4 nuclei or Trophozoite with pseudopods."
        },
        "description": {
            "fr": "Parasite tissulaire responsable de la dysenterie amibienne et de l'abces hepatique.",
            "ar": "طفيلي نسيجي مسبب للزحار الأميبي وخراج الكبد.",
            "en": "Tissue parasite causing amoebic dysentery and liver abscess."
        },
        "funny": {
            "fr": "Le ninja des intestins ! Il change de forme plus vite que ton humeur.",
            "ar": "نينجا الأمعاء! يغيّر شكله أسرع من مزاجك.",
            "en": "The intestinal ninja! Changes shape faster than your mood."
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Metronidazole (Flagyl) + Amoebicide de contact. Hygiene stricte.",
            "ar": "ميترونيدازول + مبيد أميبي. نظافة صارمة.",
            "en": "Metronidazole (Flagyl) + contact amoebicide. Strict hygiene."
        },
        "extra_tests": {
            "fr": ["Serologie amibienne", "Echographie hepatique", "NFS + CRP"],
            "ar": ["مصلية أميبية", "إيكو كبدي", "تعداد دم كامل"],
            "en": ["Amoebic serology", "Hepatic ultrasound", "CBC + CRP"]
        },
        "color": "#dc2626",
        "icon": "🔴",
        "lifecycle": {
            "fr": "Kyste ingere → Excystation → Trophozoite → Invasion tissulaire → Kyste (selles)",
            "ar": "ابتلاع الكيس ← خروج من الكيس ← طور غاذي ← غزو نسيجي ← كيس (براز)",
            "en": "Cyst ingested → Excystation → Trophozoite → Tissue invasion → Cyst (stool)"
        }
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia (intestinalis)",
        "morphology": {
            "fr": "Trophozoite piriforme en 'cerf-volant' (12-15um) avec 2 noyaux (face de hibou) et 4 paires de flagelles.",
            "ar": "طور غاذي كمثري (12-15 ميكرومتر) بنواتين متناظرتين و4 أزواج أسواط.",
            "en": "Pear-shaped 'kite' trophozoite (12-15um) with 2 nuclei and 4 flagella pairs."
        },
        "description": {
            "fr": "Protozoaire flagelle colonisant le duodenum. Malabsorption chronique.",
            "ar": "أولي سوطي يستعمر الاثني عشر. سوء امتصاص مزمن.",
            "en": "Flagellated protozoan colonizing duodenum. Chronic malabsorption."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil. Un vrai touriste !",
            "ar": "يحدّق فيك بنظارته الشمسية. سائح حقيقي!",
            "en": "Staring at you with sunglasses. A real tourist!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Metronidazole ou Tinidazole. Verifier la source d'eau.",
            "ar": "ميترونيدازول أو تينيدازول. تحقق من المياه.",
            "en": "Metronidazole or Tinidazole. Check water source."
        },
        "extra_tests": {
            "fr": ["Recherche d'antigene Giardia (selles)", "Test de malabsorption"],
            "ar": ["بحث عن مستضد الجيارديا", "اختبار سوء الامتصاص"],
            "en": ["Giardia antigen test (stool)", "Malabsorption test"]
        },
        "color": "#f59e0b",
        "icon": "🟠",
        "lifecycle": {
            "fr": "Kyste ingere → Excystation → Trophozoite → Adhesion intestinale → Kyste",
            "ar": "ابتلاع الكيس ← خروج ← طور غاذي ← التصاق معوي ← كيس",
            "en": "Cyst ingested → Excystation → Trophozoite → Intestinal adhesion → Cyst"
        }
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / tropica",
        "morphology": {
            "fr": "Amastigotes ovoides (2-5um) intracellulaires dans les macrophages. Coloration MGG.",
            "ar": "لامسوطات بيضاوية (2-5 ميكرومتر) داخل البلاعم. تلوين MGG.",
            "en": "Ovoid amastigotes (2-5um) intracellular in macrophages. MGG staining."
        },
        "description": {
            "fr": "Transmis par le phlebotome. Formes: cutanee (bouton d'Orient), viscerale (Kala-azar).",
            "ar": "ينتقل عبر ذبابة الرمل. جلدي أو حشوي.",
            "en": "Transmitted by sandfly. Cutaneous or visceral forms."
        },
        "funny": {
            "fr": "Petit mais costaud ! Il squatte les macrophages.",
            "ar": "صغير لكن قوي! يسكن البلاعم.",
            "en": "Small but tough! Squats in macrophages."
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Glucantime/Amphotericine B. Maladie a Declaration Obligatoire.",
            "ar": "غلوكانتيم/أمفوتيريسين ب. مرض ذو تصريح إجباري.",
            "en": "Glucantime/Amphotericin B. Mandatory reporting."
        },
        "extra_tests": {
            "fr": ["IDR de Montenegro", "Serologie Leishmania", "Ponction de moelle"],
            "ar": ["اختبار مونتينيغرو", "مصلية ليشمانيا", "بزل نخاع"],
            "en": ["Montenegro skin test", "Leishmania serology", "Bone marrow aspirate"]
        },
        "color": "#dc2626",
        "icon": "🔴",
        "lifecycle": {
            "fr": "Piqure phlebotome → Promastigote → Phagocytose → Amastigote → Multiplication",
            "ar": "لدغة ذبابة الرمل ← طور سوطي ← بلعمة ← طور لامسوطي ← تكاثر",
            "en": "Sandfly bite → Promastigote → Phagocytosis → Amastigote → Multiplication"
        }
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax",
        "morphology": {
            "fr": "Forme en 'bague a chaton' dans les hematies. Frottis sanguin + Goutte epaisse.",
            "ar": "شكل 'خاتم' داخل كريات الدم الحمراء. لطاخة + قطرة سميكة.",
            "en": "Signet ring form inside RBCs. Blood smear + thick drop."
        },
        "description": {
            "fr": "Agent du paludisme. P. falciparum: le plus grave. Transmission par anophele.",
            "ar": "مسبب الملاريا. المتصورة المنجلية الأخطر. ينتقل بالأنوفيل.",
            "en": "Malaria agent. P. falciparum: most severe. Anopheles transmission."
        },
        "funny": {
            "fr": "Il demande le mariage a tes globules ! Ne dis pas oui !",
            "ar": "يطلب الزواج من كرياتك! لا تقل نعم!",
            "en": "Proposes to your RBCs! Don't say yes!"
        },
        "risk_level": "critical",
        "risk_display": {"fr": "🚨 URGENCE MÉDICALE", "ar": "🚨 حالة طوارئ", "en": "🚨 EMERGENCY"},
        "advice": {
            "fr": "HOSPITALISATION ! ACT. Parasitemie /4-6h. Surveillance renale/hepatique.",
            "ar": "تنويم فوري! علاج مركب. فحص طفيليات كل 4-6 ساعات.",
            "en": "HOSPITALIZATION! ACT. Parasitemia /4-6h. Renal/hepatic monitoring."
        },
        "extra_tests": {
            "fr": ["TDR Paludisme", "Parasitemie quantitative", "Bilan hepato-renal", "Glycemie"],
            "ar": ["اختبار سريع للملاريا", "طفيليات كمية", "فحص كبد وكلى", "سكر الدم"],
            "en": ["Malaria RDT", "Quantitative parasitemia", "Hepato-renal panel", "Glycemia"]
        },
        "color": "#7f1d1d",
        "icon": "🚨",
        "lifecycle": {
            "fr": "Piqure anophele → Sporozoite → Hepatocyte → Merozoite → Hematie → Gametocyte",
            "ar": "لدغة أنوفيل ← بوغ ← خلية كبد ← جزئية ← كرية حمراء ← عرسة",
            "en": "Anopheles bite → Sporozoite → Hepatocyte → Merozoite → RBC → Gametocyte"
        }
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei / cruzi",
        "morphology": {
            "fr": "Forme en 'S' ou 'C' (15-30um) avec flagelle libre et membrane ondulante.",
            "ar": "شكل S أو C (15-30 ميكرومتر) بسوط حر وغشاء متموج.",
            "en": "S or C shape (15-30um) with free flagellum and undulating membrane."
        },
        "description": {
            "fr": "Parasite du sang. Mouche tse-tse (brucei) ou triatome (cruzi).",
            "ar": "طفيلي دموي. ذبابة تسي تسي أو بق الترياتوم.",
            "en": "Blood parasite. Tsetse fly (brucei) or triatomine (cruzi)."
        },
        "funny": {
            "fr": "Il court comme Mahrez sur l'aile droite !",
            "ar": "يجري مثل محرز على الجناح!",
            "en": "Runs like Mahrez on the right wing!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Examen du LCR si phase neurologique. Pentamidine/Suramine.",
            "ar": "فحص السائل الشوكي. بنتاميدين/سورامين.",
            "en": "CSF exam if neurological. Pentamidine/Suramin."
        },
        "extra_tests": {
            "fr": ["Ponction lombaire", "Serologie Trypanosoma", "IgM serique"],
            "ar": ["بزل قطني", "مصلية التريبانوسوما", "IgM مصلي"],
            "en": ["Lumbar puncture", "Trypanosoma serology", "Serum IgM"]
        },
        "color": "#dc2626",
        "icon": "🔴",
        "lifecycle": {
            "fr": "Piqure mouche → Trypomastigote → Sang → Multiplication → LCR (phase 2)",
            "ar": "لدغة ذبابة ← طور سوطي ← دم ← تكاثر ← سائل شوكي (المرحلة 2)",
            "en": "Fly bite → Trypomastigote → Blood → Multiplication → CSF (phase 2)"
        }
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni",
        "morphology": {
            "fr": "Oeuf ovoide (115-170um) avec eperon terminal (haematobium) ou lateral (mansoni).",
            "ar": "بيضة بيضاوية (115-170 ميكرومتر) بنتوء طرفي أو جانبي.",
            "en": "Ovoid egg (115-170um) with terminal or lateral spine."
        },
        "description": {
            "fr": "Bilharziose. S. haematobium: urinaire. S. mansoni: intestino-hepatique.",
            "ar": "بلهارسيا. دموية: بولية. منسونية: معوية كبدية.",
            "en": "Schistosomiasis. S. haematobium: urinary. S. mansoni: intestino-hepatic."
        },
        "funny": {
            "fr": "L'oeuf avec un dard ! La baignade peut couter cher.",
            "ar": "البيضة ذات الشوكة! السباحة قد تكلفك غالياً.",
            "en": "The egg with a sting! Swimming could cost you."
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Praziquantel. Sediment urinaire 24h. Eviter eaux douces stagnantes.",
            "ar": "برازيكوانتيل. رواسب بول 24 ساعة. تجنب المياه الراكدة.",
            "en": "Praziquantel. 24h urine sediment. Avoid stagnant freshwater."
        },
        "extra_tests": {
            "fr": ["ECBU", "Serologie Schistosoma", "Echographie vesicale"],
            "ar": ["فحص بول", "مصلية البلهارسيا", "إيكو مثانة"],
            "en": ["Urinalysis", "Schistosoma serology", "Bladder ultrasound"]
        },
        "color": "#f59e0b",
        "icon": "🟠",
        "lifecycle": {
            "fr": "Cercaire (eau) → Penetration cutanee → Schistosomule → Veine porte → Oeufs",
            "ar": "سركاريا (ماء) ← اختراق جلدي ← شستوسومولا ← وريد بابي ← بيض",
            "en": "Cercaria (water) → Skin penetration → Schistosomula → Portal vein → Eggs"
        }
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": {
            "fr": "Absence d'elements parasitaires apres examen complet.",
            "ar": "غياب عناصر طفيلية بعد الفحص الكامل.",
            "en": "No parasitic elements found after complete examination."
        },
        "description": {
            "fr": "Echantillon negatif. RAS.",
            "ar": "عينة سلبية.",
            "en": "Negative sample."
        },
        "funny": {
            "fr": "Rien a signaler ! Champagne ! 🥂",
            "ar": "لا شيء! شمبانيا! 🥂",
            "en": "All clear! Champagne! 🥂"
        },
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {
            "fr": "RAS. Bonne hygiene alimentaire.",
            "ar": "لا شيء. نظافة غذائية جيدة.",
            "en": "All clear. Good food hygiene."
        },
        "extra_tests": {
            "fr": ["Aucun examen supplementaire necessaire"],
            "ar": ["لا حاجة لفحوصات إضافية"],
            "en": ["No additional tests needed"]
        },
        "color": "#16a34a",
        "icon": "🟢",
        "lifecycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"}
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())

# ============================================
#  5. أسئلة الاختبار
# ============================================
QUIZ_QUESTIONS = {
    "fr": [
        {"q": "Quel parasite est connu sous le nom de 'bague a chaton' dans les hematies?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Le Plasmodium presente une forme en bague a chaton dans les hematies.", "difficulty": "easy"},
        {"q": "Le kyste de Giardia possede combien de noyaux?", "options": ["2 noyaux", "4 noyaux", "6 noyaux", "8 noyaux"], "answer": 1, "explanation": "Le kyste mature de Giardia contient 4 noyaux.", "difficulty": "easy"},
        {"q": "Quel parasite est transmis par le phlebotome?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "La Leishmania est transmise par le phlebotome.", "difficulty": "medium"},
        {"q": "L'eperon terminal est caracteristique de quel oeuf?", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "L'oeuf de S. haematobium a un eperon terminal.", "difficulty": "medium"},
        {"q": "Quel examen est urgent en cas de suspicion de paludisme?", "options": ["Coproculture", "ECBU", "Goutte epaisse + Frottis", "Serologie"], "answer": 2, "explanation": "La goutte epaisse et le frottis sanguin sont les examens de reference.", "difficulty": "easy"},
        {"q": "Le trophozoite d'E. histolytica se distingue par:", "options": ["Ses flagelles", "Ses hematies phagocytees", "Sa membrane ondulante", "Son kinetoplaste"], "answer": 1, "explanation": "La presence d'hematies phagocytees est le critere de pathogenicite.", "difficulty": "hard"},
        {"q": "La maladie de Chagas est causee par:", "options": ["T. brucei gambiense", "T. cruzi", "L. donovani", "P. vivax"], "answer": 1, "explanation": "Trypanosoma cruzi est l'agent de la maladie de Chagas.", "difficulty": "medium"},
        {"q": "Quel colorant est utilise pour les amastigotes de Leishmania?", "options": ["Ziehl-Neelsen", "Gram", "MGG (May-Grunwald-Giemsa)", "Lugol"], "answer": 2, "explanation": "La coloration MGG permet de visualiser les amastigotes.", "difficulty": "hard"},
        {"q": "Le Praziquantel est le traitement de reference de:", "options": ["Paludisme", "Amibiase", "Bilharziose", "Giardiose"], "answer": 2, "explanation": "Le Praziquantel est le traitement de la bilharziose.", "difficulty": "medium"},
        {"q": "La 'face de hibou' est observee chez:", "options": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "answer": 1, "explanation": "Le trophozoite de Giardia montre 2 noyaux symetriques.", "difficulty": "easy"}
    ],
    "ar": [
        {"q": "أي طفيلي يُعرف بشكل 'الخاتم' داخل كريات الدم الحمراء؟", "options": ["الجيارديا", "المتصورة (البلازموديوم)", "الليشمانيا", "الأميبا"], "answer": 1, "explanation": "المتصورة تظهر بشكل خاتم داخل الكريات الحمراء.", "difficulty": "easy"},
        {"q": "كم نواة في كيس الجيارديا الناضج؟", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "كيس الجيارديا الناضج يحتوي على 4 نوى.", "difficulty": "easy"},
        {"q": "أي طفيلي ينتقل عبر ذبابة الرمل؟", "options": ["البلازموديوم", "التريبانوسوما", "الليشمانيا", "البلهارسيا"], "answer": 2, "explanation": "الليشمانيا تنتقل عبر ذبابة الرمل.", "difficulty": "medium"},
        {"q": "النتوء الطرفي يميز بيضة أي طفيلي؟", "options": ["الأسكاريس", "البلهارسيا الدموية", "البلهارسيا المنسونية", "الشريطية"], "answer": 1, "explanation": "بيضة البلهارسيا الدموية لها نتوء طرفي.", "difficulty": "medium"},
        {"q": "ما الفحص العاجل عند الاشتباه بالملاريا؟", "options": ["زرع براز", "فحص بول", "قطرة سميكة + لطاخة", "مصلية"], "answer": 2, "explanation": "القطرة السميكة واللطاخة هما الفحصان المرجعيان.", "difficulty": "easy"}
    ],
    "en": [
        {"q": "Which parasite shows a 'signet ring' form in RBCs?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Plasmodium shows a signet ring form inside RBCs.", "difficulty": "easy"},
        {"q": "How many nuclei does a mature Giardia cyst have?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "A mature Giardia cyst contains 4 nuclei.", "difficulty": "easy"},
        {"q": "Which parasite is transmitted by the sandfly?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania is transmitted by the sandfly.", "difficulty": "medium"},
        {"q": "The terminal spine is characteristic of which egg?", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "S. haematobium egg has a terminal spine.", "difficulty": "medium"},
        {"q": "What is the urgent test for suspected malaria?", "options": ["Stool culture", "Urinalysis", "Thick smear + Thin smear", "Serology"], "answer": 2, "explanation": "Thick and thin blood smears are the gold standard.", "difficulty": "easy"}
    ]
}

# ============================================
#  6. الشات بوت
# ============================================
CHATBOT_KNOWLEDGE = {
    "fr": {
        "keywords": {
            "amoeba": "L'Entamoeba histolytica est un parasite causant la dysenterie amibienne. Diagnostic: kystes a 4 noyaux ou trophozoites hematophages. Traitement: Metronidazole.",
            "amibe": "L'Entamoeba histolytica cause la dysenterie amibienne. Traitement: Metronidazole.",
            "giardia": "Giardia lamblia colonise le duodenum. Forme en cerf-volant. Traitement: Metronidazole/Tinidazole.",
            "leishmania": "Leishmania transmise par le phlebotome. Formes: cutanee et viscerale. Traitement: Glucantime.",
            "plasmodium": "URGENCE ! Le Plasmodium cause le paludisme. Diagnostic: frottis + goutte epaisse. Traitement: ACT.",
            "malaria": "URGENCE ! Le Plasmodium cause le paludisme. Diagnostic: frottis + goutte epaisse. Traitement: ACT.",
            "paludisme": "URGENCE ! Le Plasmodium cause le paludisme. Diagnostic: frottis + goutte epaisse. Traitement: ACT.",
            "trypanosoma": "Trypanosoma cause la maladie du sommeil (brucei) ou de Chagas (cruzi). Forme en S avec membrane ondulante.",
            "schistosoma": "Schistosoma cause la bilharziose. Oeufs avec eperon. Traitement: Praziquantel.",
            "bilharziose": "La bilharziose est causee par Schistosoma. Contamination dans les eaux douces.",
            "bonjour": "Bonjour ! Je suis Dr. DhiaBot, votre assistant parasitologique. Comment puis-je vous aider ?",
            "merci": "De rien ! N'hesitez pas si vous avez d'autres questions !",
            "microscope": "Le microscope optique: x10 pour reperage, x40 pour identification, x100 (immersion) pour details.",
            "coloration": "Principales colorations: MGG pour hematies, Lugol pour selles, Ziehl-Neelsen pour cryptosporidies.",
            "selle": "L'EPS comprend: examen macroscopique, microscopique direct, et apres concentration.",
            "sang": "Examen du sang: frottis mince + goutte epaisse. Coloration MGG ou Giemsa.",
            "hygiene": "Conseils: lavage des mains, eau potable, cuisson des aliments, protection contre insectes.",
            "diagnostic": "Le diagnostic parasitologique repose sur l'examen direct, les techniques de concentration et parfois la serologie.",
            "traitement": "Le traitement depend du parasite: Metronidazole (amibes, Giardia), ACT (paludisme), Praziquantel (bilharziose).",
            "prevention": "Prevention: hygiene des mains, eau potable, cuisson adequte, moustiquaires, controle des vecteurs.",
        },
        "default": "Je suis Dr. DhiaBot. Posez-moi une question sur: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, ou sur les techniques de diagnostic !",
        "greeting": "Bonjour ! 🤖 Je suis **Dr. DhiaBot**, votre assistant parasitologique intelligent. Posez-moi vos questions !"
    },
    "ar": {
        "keywords": {
            "أميبا": "الأميبا الحالّة للنسج تسبب الزحار الأميبي. التشخيص: أكياس بـ 4 نوى. العلاج: ميترونيدازول.",
            "جيارديا": "الجيارديا تستعمر الاثني عشر. تسبب سوء الامتصاص. العلاج: ميترونيدازول.",
            "ليشمانيا": "الليشمانيا تنتقل عبر ذبابة الرمل. العلاج: غلوكانتيم.",
            "ملاريا": "حالة طوارئ! المتصورة تسبب الملاريا. العلاج: ACT.",
            "بلهارسيا": "البلهارسيا تنتقل في المياه العذبة. العلاج: برازيكوانتيل.",
            "مرحبا": "مرحباً! أنا الدكتور ضياء بوت، مساعدك في علم الطفيليات!",
            "شكرا": "عفواً! لا تتردد في السؤال مجدداً!",
        },
        "default": "أنا الدكتور ضياء بوت. اسألني عن: أميبا، جيارديا، ليشمانيا، بلازموديوم، تريبانوسوما، بلهارسيا.",
        "greeting": "مرحباً! 🤖 أنا **الدكتور ضياء بوت**، مساعدك الذكي. اسألني!"
    },
    "en": {
        "keywords": {
            "amoeba": "E. histolytica causes amoebic dysentery. Diagnosis: 4-nuclei cysts. Treatment: Metronidazole.",
            "giardia": "Giardia colonizes the duodenum. Kite-shaped. Treatment: Metronidazole/Tinidazole.",
            "leishmania": "Leishmania transmitted by sandfly. Treatment: Glucantime.",
            "malaria": "EMERGENCY! Plasmodium causes malaria. Treatment: ACT.",
            "plasmodium": "EMERGENCY! Plasmodium causes malaria. Treatment: ACT.",
            "schistosoma": "Schistosoma causes bilharziasis. Treatment: Praziquantel.",
            "hello": "Hello! I'm Dr. DhiaBot, your parasitology assistant!",
            "thanks": "You're welcome! Don't hesitate to ask more!",
            "diagnosis": "Parasitological diagnosis relies on direct examination, concentration techniques and sometimes serology.",
            "treatment": "Treatment depends on parasite: Metronidazole (amoeba, Giardia), ACT (malaria), Praziquantel (schistosomiasis).",
        },
        "default": "I'm Dr. DhiaBot. Ask me about: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma.",
        "greeting": "Hello! 🤖 I'm **Dr. DhiaBot**, your smart parasitology assistant. Ask me anything!"
    }
}

DAILY_TIPS = {
    "fr": [
        "💡 Toujours examiner les selles dans les 30 minutes suivant le prelevement pour voir les formes vegetatives mobiles.",
        "💡 Le Lugol aide a mettre en evidence les noyaux des kystes d'amibes.",
        "💡 Un frottis sanguin doit etre fin pour bien identifier les Plasmodium.",
        "💡 La goutte epaisse est 10x plus sensible que le frottis mince.",
        "💡 Les oeufs de S. haematobium se cherchent dans les urines de midi.",
        "💡 Pensez a faire 3 EPS a quelques jours d'intervalle.",
        "💡 Le Metronidazole est le traitement de base pour Amoeba, Giardia et Trichomonas.",
        "💡 La coloration de Ziehl-Neelsen modifiee est utile pour Cryptosporidium.",
        "💡 Une goutte epaisse negative ne suffit pas a exclure le paludisme.",
        "💡 Le phlebotome est actif au crepuscule - conseillez les moustiquaires.",
    ],
    "ar": [
        "💡 افحص البراز خلال 30 دقيقة من الأخذ لرؤية الأطوار المتحركة.",
        "💡 اللوغول يساعد في إظهار نوى أكياس الأميبا.",
        "💡 اللطاخة الدموية يجب أن تكون رقيقة لتحديد البلازموديوم.",
        "💡 القطرة السميكة أكثر حساسية 10 مرات من اللطاخة الرقيقة.",
        "💡 ابحث عن بيض البلهارسيا في بول الظهيرة.",
    ],
    "en": [
        "💡 Always examine stool within 30 minutes of collection.",
        "💡 Lugol helps visualize amoebic cyst nuclei.",
        "💡 Blood smear must be thin for proper Plasmodium identification.",
        "💡 Thick smear is 10x more sensitive than thin smear.",
        "💡 Search for S. haematobium eggs in midday urine.",
    ]
}

# ============================================
#  7. تهيئة حالة الجلسة - ✅ الوضع الليلي افتراضي
# ============================================
SESSION_DEFAULTS = {
    "logged_in": False,
    "user_name": "",
    "intro_step": 0,
    "history": [],
    "dark_mode": True,  # ✅ الوضع الليلي افتراضي
    "last_audio_hash": "",
    "login_attempts": 0,
    "lockout_until": None,
    "lang": "fr",
    "activity_log": [],
    "quiz_state": {"current": 0, "score": 0, "answered": [], "active": False},
    "chat_history": [],
    "last_activity": None,
    "splash_shown": False,
    "balloons_shown": False,
    "demo_seed": None,
    "heatmap_seed": None,
    "scan_count": 0,
    "session_start": None,
}

for key, val in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state.session_start is None:
    st.session_state.session_start = datetime.now()

# ============================================
#  8. الدوال المساعدة المحسنة
# ============================================
def t(key):
    lang = st.session_state.get("lang", "fr")
    trans = TRANSLATIONS.get(lang, TRANSLATIONS["fr"])
    return trans.get(key, TRANSLATIONS["fr"].get(key, key))

def get_p_text(data, field):
    lang = st.session_state.get("lang", "fr")
    val = data.get(field, {})
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", ""))
    if isinstance(val, list):
        return val
    return str(val)

def get_greeting():
    h = datetime.now().hour
    lang = st.session_state.get("lang", "fr")
    greetings = {
        "fr": ("Bonjour", "Bon après-midi", "Bonsoir"),
        "ar": ("صباح الخير", "مساء الخير", "مساء الخير"),
        "en": ("Good morning", "Good afternoon", "Good evening")
    }
    g = greetings.get(lang, greetings["fr"])
    if h < 12: return g[0]
    elif h < 18: return g[1]
    return g[2]

def risk_color(level):
    return {"critical":"#7f1d1d","high":"#dc2626","medium":"#f59e0b","low":"#22c55e","none":"#16a34a"}.get(level, "#6b7280")

def risk_percent(level):
    return {"critical":100,"high":80,"medium":50,"low":25,"none":0}.get(level, 0)

def log_activity(action):
    st.session_state.activity_log.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "user": st.session_state.user_name,
        "action": action
    })
    st.session_state.last_activity = datetime.now()
    # ✅ حد أقصى للسجل
    if len(st.session_state.activity_log) > MAX_HISTORY:
        st.session_state.activity_log = st.session_state.activity_log[-MAX_HISTORY:]

def check_auto_lock():
    if st.session_state.last_activity:
        elapsed = (datetime.now() - st.session_state.last_activity).total_seconds() / 60
        if elapsed > AUTO_LOCK_MINUTES:
            log_activity("Auto-locked (inactivity)")
            st.session_state.logged_in = False
            st.session_state.intro_step = 0
            st.rerun()

def get_session_duration():
    """✅ حساب مدة الجلسة"""
    if st.session_state.session_start:
        delta = datetime.now() - st.session_state.session_start
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return "00:00:00"

def speak(text, lang_code=None):
    if lang_code is None:
        lang_code = st.session_state.get("lang", "fr")
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang_code)
        fname = f"_audio_{int(time.time())}_{random.randint(1000,9999)}.mp3"
        tts.save(fname)
        with open(fname, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<audio autoplay style="display:none;">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mpeg"></audio>',
            unsafe_allow_html=True
        )
        try:
            os.remove(fname)
        except OSError:
            pass
    except ImportError:
        safe_text = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
        js_lang = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(lang_code, "fr-FR")
        st.markdown(
            f"""<script>
            try {{
                var msg = new SpeechSynthesisUtterance('{safe_text}');
                msg.lang = '{js_lang}'; msg.rate = 0.9;
                window.speechSynthesis.speak(msg);
            }} catch(e) {{}}
            </script>""",
            unsafe_allow_html=True
        )
    except Exception:
        pass

def chatbot_reply(user_msg):
    lang = st.session_state.get("lang", "fr")
    kb = CHATBOT_KNOWLEDGE.get(lang, CHATBOT_KNOWLEDGE["fr"])
    msg_lower = user_msg.lower().strip()

    for keyword, response in kb["keywords"].items():
        if keyword in msg_lower:
            return response

    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if name.lower() in msg_lower or data["scientific_name"].lower() in msg_lower:
            morpho = get_p_text(data, "morphology")
            desc = get_p_text(data, "description")
            advice = get_p_text(data, "advice")
            funny = get_p_text(data, "funny")
            return f"**{name}** ({data['scientific_name']})\n\n📋 {desc}\n\n🔬 {morpho}\n\n💊 {advice}\n\n🤖 {funny}"

    return kb["default"]

def generate_heatmap_overlay(image, seed=None):
    img = image.copy()
    width, height = img.size
    if seed is None:
        seed = st.session_state.get("heatmap_seed")
        if seed is None:
            seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = seed
    rng = random.Random(seed)
    heatmap = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(heatmap)
    cx = width // 2 + rng.randint(-width//6, width//6)
    cy = height // 2 + rng.randint(-height//6, height//6)
    max_r = min(width, height) // 3
    for r in range(max_r, 0, -3):
        alpha = max(0, min(180, int(180 * (1 - r / max_r))))
        ratio = r / max_r
        if ratio > 0.6:
            color = (0, 255, 0, alpha // 3)
        elif ratio > 0.3:
            color = (255, 255, 0, alpha // 2)
        else:
            color = (255, 0, 0, alpha)
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=color)
    result = Image.alpha_composite(img.convert('RGBA'), heatmap)
    return result.convert('RGB')

def assess_image_quality(image):
    """✅ تقييم جودة الصورة"""
    gray = np.array(ImageOps.grayscale(image))
    brightness = np.mean(gray)
    contrast = np.std(gray)
    sharpness = np.mean(np.abs(np.diff(gray.astype(float), axis=0))) + np.mean(np.abs(np.diff(gray.astype(float), axis=1)))
    score = min(100, int((contrast / 80) * 40 + (sharpness / 30) * 30 + (1 - abs(brightness - 128) / 128) * 30))
    if score >= 80:
        quality = {"fr": "Excellente", "ar": "ممتازة", "en": "Excellent"}
        color = "#22c55e"
    elif score >= 60:
        quality = {"fr": "Bonne", "ar": "جيدة", "en": "Good"}
        color = "#3b82f6"
    elif score >= 40:
        quality = {"fr": "Moyenne", "ar": "متوسطة", "en": "Average"}
        color = "#f59e0b"
    else:
        quality = {"fr": "Faible", "ar": "ضعيفة", "en": "Poor"}
        color = "#ef4444"
    lang = st.session_state.get("lang", "fr")
    return score, quality.get(lang, quality["fr"]), color


# ============================================
#  9. محرك الذكاء الاصطناعي
# ============================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    model = None
    model_name = None
    try:
        import tensorflow as tf
        try:
            files = os.listdir(".")
        except OSError:
            files = []
        for ext in [".h5", ".keras"]:
            found = [f for f in files if f.endswith(ext)]
            if found:
                model_name = found[0]
                model = tf.keras.models.load_model(model_name, compile=False)
                break
        if model is None:
            tflite = [f for f in files if f.endswith(".tflite")]
            if tflite:
                model_name = tflite[0]
                model = tf.lite.Interpreter(model_path=model_name)
                model.allocate_tensors()
    except ImportError:
        pass
    except Exception:
        pass
    return model, model_name

def predict_image(model, image):
    result = {
        "label": "Negative", "confidence": 0,
        "all_predictions": {}, "is_reliable": False,
        "is_demo": False, "info": PARASITE_DB["Negative"]
    }
    if model is None:
        if st.session_state.get("demo_seed") is None:
            st.session_state.demo_seed = random.randint(0, 999999)
        rng = random.Random(st.session_state.demo_seed)
        demo_label = rng.choice(CLASS_NAMES)
        demo_conf = rng.randint(65, 97)
        all_preds = {}
        remaining = 100.0 - demo_conf
        for cls in CLASS_NAMES:
            if cls == demo_label:
                all_preds[cls] = float(demo_conf)
            else:
                val = round(rng.uniform(0, remaining / max(1, len(CLASS_NAMES) - 1)), 1)
                all_preds[cls] = val
        result.update({
            "label": demo_label, "confidence": demo_conf,
            "all_predictions": all_preds,
            "is_reliable": demo_conf >= CONFIDENCE_THRESHOLD,
            "is_demo": True,
            "info": PARASITE_DB.get(demo_label, PARASITE_DB["Negative"])
        })
        return result
    try:
        import tensorflow as tf
        img = ImageOps.fit(image, MODEL_INPUT_SIZE, Image.LANCZOS)
        arr = np.asarray(img).astype(np.float32) / 127.5 - 1.0
        batch = np.expand_dims(arr, 0)
        if isinstance(model, tf.lite.Interpreter):
            inp = model.get_input_details()
            out = model.get_output_details()
            model.set_tensor(inp[0]['index'], batch)
            model.invoke()
            preds = model.get_tensor(out[0]['index'])[0]
        else:
            preds = model.predict(batch, verbose=0)[0]
        idx = int(np.argmax(preds))
        conf = int(preds[idx] * 100)
        label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else "Negative"
        all_p = {CLASS_NAMES[i]: round(float(preds[i])*100, 1) for i in range(min(len(preds), len(CLASS_NAMES)))}
        result.update({
            "label": label, "confidence": conf,
            "all_predictions": all_p,
            "is_reliable": conf >= CONFIDENCE_THRESHOLD,
            "is_demo": False,
            "info": PARASITE_DB.get(label, PARASITE_DB["Negative"])
        })
    except Exception as e:
        st.error(f"Prediction error: {e}")
    return result

def apply_thermal(image):
    enhanced = ImageEnhance.Contrast(image).enhance(1.5)
    gray = ImageOps.grayscale(enhanced)
    smoothed = gray.filter(ImageFilter.GaussianBlur(1))
    return ImageOps.colorize(smoothed, black="navy", white="yellow", mid="red")

def apply_edge_detection(image):
    gray = ImageOps.grayscale(image)
    return gray.filter(ImageFilter.FIND_EDGES)

def apply_enhanced_contrast(image):
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(image).enhance(2.0)).enhance(2.0)


# ============================================
#  10. PDF احترافي
# ============================================
class MedicalPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(True, 25)

    def header(self):
        self.set_font("Arial", "B", 10)
        self.set_text_color(37, 99, 235)
        self.cell(0, 6, "DM SMART LAB AI", 0, 0, "L")
        self.set_font("Arial", "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 1, "R")
        self.set_draw_color(37, 99, 235)
        self.set_line_width(0.6)
        self.line(10, 15, 200, 15)
        self.ln(8)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        self.set_font("Arial", "I", 8)
        self.set_text_color(100, 116, 139)
        self.cell(0, 5, f"DM Smart Lab AI v{APP_VERSION} - Professional Edition", 0, 0, "L")
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", 0, 0, "R")

    def section_title(self, title):
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 11)
        self.cell(0, 8, f"  {title}", 0, 1, "L", True)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def info_line(self, label, value):
        self.set_font("Arial", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(55, 7, label, 0, 0)
        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)
        safe_val = _safe_pdf_text(str(value))
        self.cell(0, 7, safe_val, 0, 1)

    def safe_multi_cell(self, w, h, txt, border=0, align='L'):
        self.multi_cell(w, h, _safe_pdf_text(txt), border, align)


def _safe_pdf_text(text):
    if not text:
        return ""
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ô': 'o', 'ö': 'o',
        'î': 'i', 'ï': 'i',
        'ç': 'c',
        'É': 'E', 'È': 'E', 'Ê': 'E',
        'À': 'A', 'Â': 'A',
        'Ù': 'U', 'Û': 'U',
        'Ô': 'O', 'Î': 'I',
        'Ç': 'C',
        '→': '->', '←': '<-',
        '🔴': '[!]', '🟠': '[!]', '🟢': '[OK]', '🚨': '[!!!]',
        '\u200b': '', '\u200e': '', '\u200f': '',
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    result = []
    for ch in text:
        try:
            ch.encode('latin-1')
            result.append(ch)
        except UnicodeEncodeError:
            result.append('?')
    return ''.join(result)


def generate_pdf(patient, label, conf, info):
    pdf = MedicalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 12, _safe_pdf_text(t("pdf_title")), 0, 1, "C")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, _safe_pdf_text(t("pdf_subtitle")), 0, 1, "C")
    pdf.ln(8)

    pdf.section_title(_safe_pdf_text(t("pdf_patient_section")))
    for k, v in patient.items():
        pdf.info_line(f"{k} :", str(v))
    pdf.info_line("Date :", datetime.now().strftime("%d/%m/%Y"))
    pdf.info_line("Heure :", datetime.now().strftime("%H:%M"))
    pdf.ln(5)

    pdf.section_title(_safe_pdf_text(t("pdf_result_section")))
    pdf.ln(2)
    pdf.set_font("Arial", "B", 16)
    if label == "Negative":
        pdf.set_text_color(22, 163, 74)
    else:
        pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 10, f"RESULTAT: {_safe_pdf_text(label)}", 0, 1, "C")
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, f"Confiance: {conf}%", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_font("Arial", "", 10)
    morpho_text = get_p_text(info, 'morphology')
    pdf.safe_multi_cell(0, 6, f"Morphologie: {morpho_text}")
    pdf.ln(2)
    desc_text = get_p_text(info, 'description')
    pdf.safe_multi_cell(0, 6, f"Description: {desc_text}")
    pdf.ln(5)

    pdf.section_title(_safe_pdf_text(t("pdf_advice_section")))
    pdf.set_font("Arial", "", 10)
    advice_text = get_p_text(info, "advice")
    pdf.safe_multi_cell(0, 6, advice_text)
    pdf.ln(3)

    extra = get_p_text(info, "extra_tests")
    if isinstance(extra, list) and extra:
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, _safe_pdf_text(t("scan_extra_tests")) + ":", 0, 1)
        pdf.set_font("Arial", "", 10)
        for test in extra:
            pdf.cell(0, 6, f"  - {_safe_pdf_text(test)}", 0, 1)

    pdf.ln(10)
    pdf.section_title(_safe_pdf_text(t("pdf_validation")))
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    tech_label = _safe_pdf_text(t("pdf_technician"))
    pdf.cell(95, 7, f"{tech_label} :", 0, 0)
    pdf.cell(95, 7, f"{tech_label} :", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 7, _safe_pdf_text(AUTHORS["dev1"]["name"]), 0, 0)
    pdf.cell(95, 7, _safe_pdf_text(AUTHORS["dev2"]["name"]), 0, 1)
    pdf.ln(12)

    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.safe_multi_cell(0, 5, t("pdf_disclaimer"))

    return pdf.output(dest='S').encode('latin-1')


# ============================================
#  11. التصميم CSS المحسن - ✅ وضع ليلي احترافي
# ============================================
def apply_full_theme():
    dm = st.session_state.get("dark_mode", True)  # ✅ الليلي افتراضي
    if dm:
        bg = "#030712"
        bg2 = "#0a0f1e"
        card = "#0d1425"
        text = "#e2e8f0"
        muted = "#64748b"
        border = "#1e293b"
        primary = "#3b82f6"
        primary_dk = "#2563eb"
        primary_glow = "rgba(59,130,246,0.12)"
        accent = "#06b6d4"
        accent2 = "#8b5cf6"
        sidebar_bg = "#020617"
        sidebar_border = "#1e293b"
        input_bg = "#0d1425"
        grad1 = "#0a1628"
        grad2 = "#030712"
        grad3 = "#0c1631"
        dot_clr = "rgba(59,130,246,0.04)"
        shadow = "rgba(0,0,0,0.6)"
        glass = "rgba(13,20,37,0.88)"
        glass_b = "rgba(59,130,246,0.12)"
        success_bg = "rgba(34,197,94,0.08)"
        warning_bg = "rgba(245,158,11,0.08)"
        error_bg = "rgba(239,68,68,0.08)"
        info_bg = "rgba(59,130,246,0.08)"
    else:
        bg = "#f8fafc"
        bg2 = "#ffffff"
        card = "#ffffff"
        text = "#0f172a"
        muted = "#64748b"
        border = "#e2e8f0"
        primary = "#2563eb"
        primary_dk = "#1d4ed8"
        primary_glow = "rgba(37,99,235,0.08)"
        accent = "#0891b2"
        accent2 = "#7c3aed"
        sidebar_bg = "#f1f5f9"
        sidebar_border = "#e2e8f0"
        input_bg = "#ffffff"
        grad1 = "#dbeafe"
        grad2 = "#f8fafc"
        grad3 = "#e0f2fe"
        dot_clr = "rgba(37,99,235,0.03)"
        shadow = "rgba(0,0,0,0.04)"
        glass = "rgba(255,255,255,0.92)"
        glass_b = "rgba(37,99,235,0.1)"
        success_bg = "rgba(34,197,94,0.06)"
        warning_bg = "rgba(245,158,11,0.06)"
        error_bg = "rgba(239,68,68,0.06)"
        info_bg = "rgba(37,99,235,0.06)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* ═══════════ الأساسيات ═══════════ */
    html, body, [class*="css"], p, span, label, div, li, td, th {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: {text} !important;
    }}
    h1 {{ font-size:2.4rem !important; font-weight:900 !important; letter-spacing:-0.02em; }}
    h2 {{ font-size:1.7rem !important; font-weight:800 !important; }}
    h3 {{ font-size:1.35rem !important; font-weight:700 !important; }}
    h1,h2,h3,h4,h5,h6 {{ color: {text} !important; }}

    /* ═══════════ الخلفية الرئيسية ═══════════ */
    .stApp {{
        background:
            radial-gradient(ellipse at 15% 50%, {grad1} 0%, transparent 55%),
            radial-gradient(ellipse at 85% 15%, {grad3} 0%, transparent 55%),
            radial-gradient(ellipse at 50% 85%, rgba(139,92,246,0.03) 0%, transparent 50%),
            linear-gradient(180deg, {bg} 0%, {bg2} 100%);
        background-attachment: fixed;
    }}
    .stApp::before {{
        content:''; position:fixed; top:0;left:0;right:0;bottom:0;
        background-image: radial-gradient(circle, {dot_clr} 1px, transparent 1px);
        background-size: 32px 32px; pointer-events:none; z-index:0;
    }}

    /* ═══════════ الشريط الجانبي ═══════════ */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sidebar_bg} 0%, {bg2} 100%) !important;
        border-right: 1px solid {sidebar_border} !important;
        backdrop-filter: blur(20px);
    }}
    section[data-testid="stSidebar"] * {{ color: {text} !important; }}

    /* ═══════════ البطاقات ═══════════ */
    .dm-card {{
        background: {glass};
        backdrop-filter: blur(16px) saturate(1.2);
        border: 1px solid {glass_b};
        border-radius: 20px;
        padding: 28px;
        margin: 14px 0;
        box-shadow: 0 4px 24px {shadow}, 0 0 0 1px {glass_b};
        position: relative; z-index: 2;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .dm-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 16px 48px {shadow}, 0 0 0 1px rgba(59,130,246,0.2);
    }}
    .dm-card-blue {{ border-left: 4px solid {primary}; }}
    .dm-card-red {{ border-left: 4px solid #ef4444; }}
    .dm-card-green {{ border-left: 4px solid #22c55e; }}
    .dm-card-orange {{ border-left: 4px solid #f59e0b; }}
    .dm-card-purple {{ border-left: 4px solid #8b5cf6; }}
    .dm-card-cyan {{ border-left: 4px solid #06b6d4; }}
    .dm-card-gradient {{
        background: linear-gradient(135deg, {glass} 0%, rgba(59,130,246,0.05) 100%);
        border: 1px solid {glass_b};
    }}

    /* ═══════════ مؤشرات الإحصائيات ═══════════ */
    .dm-metric {{
        background: {glass};
        backdrop-filter: blur(12px);
        border: 1px solid {glass_b};
        border-radius: 20px;
        padding: 24px 18px;
        text-align: center;
        box-shadow: 0 2px 16px {shadow};
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .dm-metric::before {{
        content: '';
        position: absolute; top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, {primary}, {accent}, {accent2});
        border-radius: 20px 20px 0 0;
    }}
    .dm-metric:hover {{
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 36px {shadow};
    }}
    .dm-metric-icon {{ font-size: 2rem; margin-bottom: 10px; display: block; }}
    .dm-metric-val {{
        font-size: 2.2rem; font-weight: 900;
        font-family: 'JetBrains Mono', monospace !important;
        background: linear-gradient(135deg, {primary}, {accent});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    .dm-metric-lbl {{
        font-size: 0.75rem; font-weight: 600; color: {muted} !important;
        text-transform: uppercase; letter-spacing: 0.1em; margin-top: 8px;
    }}

    /* ═══════════ الأزرار ═══════════ */
    div.stButton > button {{
        background: linear-gradient(135deg, {primary}, {primary_dk}) !important;
        color: white !important; border: none !important;
        border-radius: 14px !important; padding: 14px 32px !important;
        font-weight: 700 !important; font-size: 0.9rem !important;
        letter-spacing: 0.02em;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.3), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    }}
    div.stButton > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 32px rgba(37,99,235,0.45), inset 0 1px 0 rgba(255,255,255,0.1) !important;
    }}
    div.stButton > button:active {{
        transform: translateY(-1px) scale(0.99) !important;
    }}

    /* ═══════════ الحقول ═══════════ */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        background: {input_bg} !important;
        border: 2px solid {border} !important;
        border-radius: 12px !important;
        color: {text} !important;
        transition: all 0.3s ease;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {primary} !important;
        box-shadow: 0 0 0 4px {primary_glow} !important;
    }}

    /* ═══════════ الخطوات ═══════════ */
    .dm-step {{
        display: flex; align-items: center; gap: 12px;
        padding: 14px 20px; border-radius: 14px; margin: 6px 0;
        font-weight: 600; font-size: 0.9rem;
        transition: all 0.3s ease;
    }}
    .dm-step-done {{
        background: {success_bg};
        border: 1px solid rgba(34,197,94,0.25);
        color: #22c55e !important;
    }}
    .dm-step-active {{
        background: {primary_glow};
        border: 1px solid rgba(59,130,246,0.25);
        color: {primary} !important;
        animation: stepPulse 2.5s ease-in-out infinite;
    }}
    .dm-step-pending {{
        background: rgba(100,116,139,0.04);
        border: 1px solid rgba(100,116,139,0.12);
        color: {muted} !important;
    }}
    @keyframes stepPulse {{
        0%,100%{{ box-shadow: 0 0 0 0 {primary_glow}; }}
        50%{{ box-shadow: 0 0 0 10px transparent; }}
    }}

    /* ═══════════ الشات ═══════════ */
    .dm-chat-msg {{
        padding: 16px 20px; border-radius: 18px; margin: 10px 0;
        max-width: 85%; line-height: 1.7; font-size: 0.95rem;
        animation: msgSlide 0.3s ease-out;
    }}
    @keyframes msgSlide {{
        from {{ opacity:0; transform:translateY(10px); }}
        to {{ opacity:1; transform:translateY(0); }}
    }}
    .dm-chat-user {{
        background: linear-gradient(135deg, {primary}, {primary_dk});
        color: white !important; margin-left: auto;
        border-bottom-right-radius: 6px;
        box-shadow: 0 4px 16px rgba(37,99,235,0.25);
    }}
    .dm-chat-user * {{ color: white !important; }}
    .dm-chat-bot {{
        background: {glass};
        border: 1px solid {glass_b};
        border-bottom-left-radius: 6px;
    }}

    /* ═══════════ الاختبار ═══════════ */
    .dm-quiz-option {{
        background: {glass}; border: 2px solid {border};
        border-radius: 14px; padding: 14px 20px; margin: 8px 0;
        cursor: pointer; transition: all 0.3s ease; font-weight: 500;
    }}
    .dm-quiz-option:hover {{
        border-color: {primary}; background: {primary_glow};
        transform: translateX(6px);
    }}

    /* ═══════════ اللوقو ═══════════ */
    .dm-logo-wrap {{
        display: flex; flex-direction: column; align-items: center;
        padding: 28px 0 20px; z-index: 5; position: relative;
    }}
    .dm-logo-main {{
        display: flex; align-items: center; gap: 8px;
        animation: logoFloat 5s ease-in-out infinite;
    }}
    .dm-logo-char {{ font-size: 4rem; font-weight: 900; display: inline-block; }}
    .dm-logo-d {{
        background: linear-gradient(135deg, {primary}, {accent});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 20px {primary_glow});
    }}
    .dm-logo-m {{
        color: white;
        background: linear-gradient(135deg, {primary}, {accent2});
        padding: 8px 22px; border-radius: 16px;
        box-shadow: 0 4px 24px rgba(59,130,246,0.3);
    }}
    .dm-logo-tag {{
        font-size: 0.78rem; font-weight: 700; color: {muted};
        letter-spacing: 0.4em; text-transform: uppercase; margin-top: 12px;
    }}
    .dm-logo-line {{
        width: 60px; height: 3px;
        background: linear-gradient(90deg, {primary}, {accent}, {accent2});
        border-radius: 3px; margin-top: 10px;
    }}
    @keyframes logoFloat {{
        0%,100%{{ transform: translateY(0); }}
        50%{{ transform: translateY(-6px); }}
    }}

    /* ═══════════ مؤشر الثقة الدائري ═══════════ */
    .confidence-ring {{
        width: 140px; height: 140px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto;
        position: relative;
    }}
    .confidence-ring-inner {{
        width: 110px; height: 110px;
        border-radius: 50%;
        background: {card};
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        z-index: 2;
    }}
    .confidence-value {{
        font-size: 2rem; font-weight: 900;
        font-family: 'JetBrains Mono', monospace;
    }}
    .confidence-label {{
        font-size: 0.7rem; font-weight: 600; color: {muted};
        text-transform: uppercase; letter-spacing: 0.1em;
    }}

    /* ═══════════ شريط الجودة ═══════════ */
    .quality-bar {{
        height: 6px; border-radius: 3px; overflow: hidden;
        background: rgba(100,116,139,0.15);
    }}
    .quality-fill {{
        height: 100%; border-radius: 3px;
        transition: width 1s ease;
    }}

    /* ═══════════ الجسيمات ═══════════ */
    .dm-particle {{
        position: fixed; pointer-events: none; z-index: 0; opacity: 0;
        font-size: 1.6rem;
        animation: particleRise 30s linear infinite;
    }}
    @keyframes particleRise {{
        0%{{ transform: translateY(105vh) rotate(0); opacity:0; }}
        5%{{ opacity:0.06; }}
        95%{{ opacity:0.06; }}
        100%{{ transform: translateY(-10vh) rotate(360deg); opacity:0; }}
    }}

    /* ═══════════ شاشة التحميل ═══════════ */
    .dm-splash {{
        position: fixed; top:0; left:0; right:0; bottom:0;
        background: {bg}; z-index: 9999;
        display: flex; flex-direction: column;
        justify-content: center; align-items: center;
        animation: splashFade 0.6s ease 2.8s forwards;
    }}
    @keyframes splashFade {{ to {{ opacity:0; pointer-events:none; }} }}
    .dm-splash-logo {{
        font-size: 5rem;
        animation: splashPulse 1.5s ease-in-out infinite;
    }}
    @keyframes splashPulse {{
        0%,100%{{ transform:scale(1); opacity:0.8; }}
        50%{{ transform:scale(1.12); opacity:1; }}
    }}
    .dm-splash-bar {{
        width: 220px; height: 3px;
        background: rgba(128,128,128,0.15);
        border-radius: 3px; margin-top: 24px; overflow: hidden;
    }}
    .dm-splash-bar-fill {{
        width: 100%; height: 100%;
        background: linear-gradient(90deg, {primary}, {accent}, {accent2});
        animation: loadBar 2.5s ease forwards;
        transform-origin: left;
    }}
    @keyframes loadBar {{ from {{ transform: scaleX(0); }} to {{ transform: scaleX(1); }} }}

    /* ═══════════ شارة الإصدار ═══════════ */
    .dm-version-badge {{
        display: inline-flex; align-items: center; gap: 6px;
        background: linear-gradient(135deg, {primary}, {accent});
        color: white !important; padding: 4px 12px;
        border-radius: 20px; font-size: 0.7rem;
        font-weight: 700; letter-spacing: 0.05em;
    }}

    /* ═══════════ التجاوب ═══════════ */
    @media (max-width: 768px) {{
        .dm-logo-char {{ font-size: 2.8rem; }}
        .dm-card {{ padding: 18px; border-radius: 16px; }}
        .dm-metric-val {{ font-size: 1.6rem; }}
        h1 {{ font-size: 1.8rem !important; }}
    }}
    @media print {{
        .dm-particle, section[data-testid="stSidebar"], .stApp::before {{ display:none !important; }}
    }}

    /* ═══════════ شريط التقدم المخصص ═══════════ */
    .dm-progress {{
        background: rgba(100,116,139,0.1);
        border-radius: 8px; overflow: hidden;
        height: 8px; margin: 8px 0;
    }}
    .dm-progress-fill {{
        height: 100%; border-radius: 8px;
        background: linear-gradient(90deg, {primary}, {accent});
        transition: width 0.8s ease;
    }}

    /* ═══════════ تأثيرات الإنتقال ═══════════ */
    .dm-fade-in {{
        animation: fadeIn 0.5s ease-out;
    }}
    @keyframes fadeIn {{
        from {{ opacity:0; transform:translateY(15px); }}
        to {{ opacity:1; transform:translateY(0); }}
    }}

    /* ═══════════ حالة النظام ═══════════ */
    .dm-status-dot {{
        width: 8px; height: 8px; border-radius: 50%;
        display: inline-block; margin-right: 6px;
        animation: statusBlink 2s ease-in-out infinite;
    }}
    .dm-status-online {{ background: #22c55e; box-shadow: 0 0 8px rgba(34,197,94,0.5); }}
    @keyframes statusBlink {{
        0%,100%{{ opacity:1; }} 50%{{ opacity:0.4; }}
    }}
    </style>

    <!-- الجسيمات -->
    <div class="dm-particle" style="left:3%">🦠</div>
    <div class="dm-particle" style="left:12%;animation-delay:4s">🧬</div>
    <div class="dm-particle" style="left:28%;animation-delay:9s">🔬</div>
    <div class="dm-particle" style="left:45%;animation-delay:2s">🩸</div>
    <div class="dm-particle" style="left:62%;animation-delay:7s">🧪</div>
    <div class="dm-particle" style="left:78%;animation-delay:12s">💊</div>
    <div class="dm-particle" style="left:91%;animation-delay:5s">🧫</div>
    <div class="dm-particle" style="left:55%;animation-delay:15s">⚕️</div>
    """, unsafe_allow_html=True)

apply_full_theme()

# ============================================
#  12. شاشة التحميل + القفل التلقائي
# ============================================
if not st.session_state.get("splash_shown", False):
    st.markdown("""
    <div class="dm-splash" id="splash">
        <div class="dm-splash-logo">🧬</div>
        <h2 style="margin-top:20px; opacity:0.7; font-weight:800;">DM SMART LAB AI</h2>
        <p style="opacity:0.3; letter-spacing:0.4em; text-transform:uppercase; font-size:0.75rem; margin-top:8px;">
            Professional Edition v5.0
        </p>
        <div class="dm-splash-bar">
            <div class="dm-splash-bar-fill"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.splash_shown = True

if st.session_state.logged_in:
    check_auto_lock()

# اللوقو
st.markdown("""
<div class="dm-logo-wrap">
    <div class="dm-logo-main">
        <span class="dm-logo-char dm-logo-d">D</span>
        <span class="dm-logo-char dm-logo-m">M</span>
    </div>
    <div class="dm-logo-tag">Smart Lab AI</div>
    <div class="dm-logo-line"></div>
</div>
""", unsafe_allow_html=True)

# ============================================
#  13. تسجيل الدخول المحسن
# ============================================
if not st.session_state.logged_in:
    if st.session_state.lockout_until:
        if datetime.now() < st.session_state.lockout_until:
            remaining = (st.session_state.lockout_until - datetime.now()).seconds
            st.error(f"⏳ {t('login_locked')}. {remaining}s")
            st.stop()
        else:
            st.session_state.lockout_until = None
            st.session_state.login_attempts = 0

    _, col_login, _ = st.columns([1.2, 2, 1.2])
    with col_login:
        st.markdown(f"""
        <div class='dm-card dm-card-blue dm-fade-in' style='text-align:center;'>
            <div style='font-size:3.5rem; margin-bottom:16px;'>🔐</div>
            <h2 style='margin:0;'>{t('login_title')}</h2>
            <p style='opacity:0.5; margin-top:8px; font-size:0.9rem;'>{t('login_subtitle')}</p>
            <div style='margin-top:12px;'>
                <span class='dm-version-badge'>v{APP_VERSION} Pro</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
        sel_lang = st.selectbox(f"🌍 {t('language')}", list(lang_opts.keys()),
                                index=list(lang_opts.values()).index(st.session_state.lang))
        new_l = lang_opts[sel_lang]
        if new_l != st.session_state.lang:
            st.session_state.lang = new_l
            st.rerun()

        with st.form("login"):
            user = st.text_input(f"👤 {t('login_user')}", placeholder="Dr. / TLS ...")
            pwd = st.text_input(f"🔒 {t('login_pass')}", type="password")
            go = st.form_submit_button(f"🔓 {t('login_btn')}", use_container_width=True)
            if go:
                if hashlib.sha256(pwd.encode()).hexdigest() == APP_PASSWORD_HASH:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.strip() or "Utilisateur"
                    st.session_state.login_attempts = 0
                    st.session_state.last_activity = datetime.now()
                    st.session_state.session_start = datetime.now()
                    log_activity("Login")
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    left = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
                    if left <= 0:
                        st.session_state.lockout_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
                        st.error(f"🔒 {t('login_locked')}")
                    else:
                        st.error(f"❌ {t('login_error')}. {left} {t('login_attempts')}.")
    st.stop()

# ============================================
#  14. الشريط الجانبي المحسن
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:16px 0 12px;'>
        <div style='font-size:2.6rem;'>🧬</div>
        <h3 style='margin:8px 0 4px; font-weight:800;'>DM SMART LAB</h3>
        <span class='dm-version-badge'>v{APP_VERSION} Professional</span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # معلومات المستخدم
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:10px; padding:8px 0;'>
        <div style='width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#06b6d4);
                    display:flex;align-items:center;justify-content:center;font-size:1.1rem;'>👤</div>
        <div>
            <div style='font-weight:700; font-size:0.9rem;'>{st.session_state.user_name}</div>
            <div style='font-size:0.72rem; opacity:0.5;'>
                <span class="dm-status-dot dm-status-online"></span>En ligne • {get_session_duration()}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # نصيحة اليوم
    lang = st.session_state.get("lang", "fr")
    tips = DAILY_TIPS.get(lang, DAILY_TIPS["fr"])
    tip_idx = datetime.now().timetuple().tm_yday % len(tips)
    st.info(f"**{t('daily_tip')}:**\n\n{tips[tip_idx]}")

    st.markdown("---")

    lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
    cur_idx = list(lang_opts.values()).index(st.session_state.lang) if st.session_state.lang in lang_opts.values() else 0
    sel = st.selectbox(f"🌍 {t('language')}", list(lang_opts.keys()), index=cur_idx, key="sidebar_lang")
    if lang_opts[sel] != st.session_state.lang:
        st.session_state.lang = lang_opts[sel]
        st.rerun()

    st.markdown("---")

    nav = [
        f"🏠 {t('nav_home')}", f"🔬 {t('nav_scan')}",
        f"📘 {t('nav_encyclopedia')}", f"📊 {t('nav_dashboard')}",
        f"🧠 {t('nav_quiz')}", f"💬 {t('nav_chatbot')}",
        f"ℹ️ {t('nav_about')}"
    ]
    menu = st.radio("📌", nav, label_visibility="collapsed")

    st.markdown("---")
    dark = st.toggle(f"🌙 {t('night_mode')}", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")
    if st.button(f"🚪 {t('logout')}", use_container_width=True):
        log_activity("Logout")
        for k in list(SESSION_DEFAULTS.keys()):
            st.session_state[k] = SESSION_DEFAULTS[k]
        st.session_state.splash_shown = True
        st.rerun()

st.session_state.last_activity = datetime.now()

page_keys = ["home", "scan", "encyclopedia", "dashboard", "quiz", "chatbot", "about"]
page_map = dict(zip(nav, page_keys))
current_page = page_map.get(menu, "home")

# ╔══════════════════════════════════╗
# ║        PAGE: HOME                ║
# ╚══════════════════════════════════╝
if current_page == "home":
    st.markdown(f"""
    <div class='dm-fade-in'>
        <h1>👋 {get_greeting()}, {st.session_state.user_name} !</h1>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2.5])
    with c1:
        st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <div style="font-size:7rem; animation: logoFloat 4s ease-in-out infinite;">🤖</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='dm-card dm-card-gradient dm-fade-in'>
            <h3>🧬 DM SMART LAB AI — {t('app_subtitle')}</h3>
            <p style='opacity:0.7; line-height:1.8;'>
                {'...' if st.session_state.intro_step < 2 else t('home_go_scan')}
            </p>
            <div style='margin-top:12px;'>
                <span class='dm-version-badge'>v{APP_VERSION}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # الخطوات
    step = st.session_state.intro_step
    steps_data = [t("home_step1_title"), t("home_step2_title"), t("home_unlocked")]
    sc = st.columns(3)
    for i, lbl in enumerate(steps_data):
        with sc[i]:
            cls = "dm-step-done" if step > i else ("dm-step-active" if step == i else "dm-step-pending")
            icon = "✅" if step > i else ("⏳" if step == i else "⬜")
            st.markdown(f'<div class="dm-step {cls}">{icon} {lbl}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if step == 0:
        st.markdown(f"""
        <div class='dm-card dm-card-orange dm-fade-in'>
            <h4>🔒 {t('home_step1_title')}</h4>
            <p style='opacity:0.7;'>{t('home_step1_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔊 {t('home_step1_btn')}", use_container_width=True, type="primary"):
            txt = t("voice_intro").format(
                time=datetime.now().strftime("%H:%M"),
                dev1=AUTHORS["dev1"]["name"],
                dev2=AUTHORS["dev2"]["name"]
            )
            speak(txt)
            with st.spinner("🔊 ..."):
                time.sleep(5)
            st.session_state.intro_step = 1
            log_activity("Intro Step 1 completed")
            st.rerun()

    elif step == 1:
        st.markdown(f"""
        <div class='dm-card dm-card-orange dm-fade-in'>
            <h4>🔒 {t('home_step2_title')}</h4>
            <p style='opacity:0.7;'>{t('home_step2_desc')}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔊 {t('home_step2_btn')}", use_container_width=True, type="primary"):
            txt = t("voice_title").format(title=PROJECT_TITLE)
            speak(txt)
            with st.spinner("🔊 ..."):
                time.sleep(5)
            st.session_state.intro_step = 2
            log_activity("Intro Step 2 completed - System Unlocked")
            st.rerun()

    elif step >= 2:
        st.markdown(f"""
        <div class='dm-card dm-card-green dm-fade-in' style='text-align:center;'>
            <div style='font-size:3rem; margin-bottom:10px;'>🎉</div>
            <h3>✅ {t('home_unlocked')}</h3>
            <p style='opacity:0.7;'>{t('home_go_scan')}</p>
        </div>
        """, unsafe_allow_html=True)
        if not st.session_state.get("balloons_shown", False):
            st.balloons()
            st.session_state.balloons_shown = True

        # ✅ إحصائيات سريعة
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        qs1, qs2, qs3, qs4 = st.columns(4)
        with qs1:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">🔬</span>
            <div class="dm-metric-val">{len(st.session_state.history)}</div>
            <div class="dm-metric-lbl">{t('dash_total')}</div></div>""", unsafe_allow_html=True)
        with qs2:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">🕐</span>
            <div class="dm-metric-val" style="font-size:1.4rem;">{get_session_duration()}</div>
            <div class="dm-metric-lbl">Session</div></div>""", unsafe_allow_html=True)
        with qs3:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">🧠</span>
            <div class="dm-metric-val">{len(PARASITE_DB)-1}</div>
            <div class="dm-metric-lbl">Parasites</div></div>""", unsafe_allow_html=True)
        with qs4:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">✅</span>
            <div class="dm-metric-val" style="font-size:1.4rem;">Active</div>
            <div class="dm-metric-lbl">{t('dash_system')}</div></div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════╗
# ║        PAGE: SCAN                ║
# ╚══════════════════════════════════╝
elif current_page == "scan":
    st.title(f"🔬 {t('scan_title')}")
    if st.session_state.intro_step < 2:
        st.error(f"⛔ {t('scan_blocked')}")
        st.stop()

    model, model_name = load_ai_model()
    if model_name:
        st.sidebar.success(f"🧠 Model: {model_name}")
    else:
        st.sidebar.info("🧠 Demo Mode")

    # بيانات المريض
    st.markdown(f"### 📋 {t('scan_patient_info')}")
    ca, cb = st.columns(2)
    p_nom = ca.text_input(f"{t('scan_nom')} *", placeholder="Benali")
    p_prenom = cb.text_input(t("scan_prenom"), placeholder="Ahmed")
    cc, cd, ce, cf = st.columns(4)
    p_age = cc.number_input(t("scan_age"), 0, 120, 30)
    p_sexe = cd.selectbox(t("scan_sexe"), [t("patient_sexe_h"), t("patient_sexe_f")])
    p_poids = ce.number_input(t("scan_poids"), 0, 300, 70)
    samples = [t("echantillon_selles"), t("echantillon_sang_frottis"), t("echantillon_sang_goutte"),
               t("echantillon_urines"), t("echantillon_lcr"), t("echantillon_autre")]
    p_type = cf.selectbox(t("scan_echantillon"), samples)

    st.markdown("---")
    st.markdown(f"### 📸 {t('scan_capture')}")
    cap_mode = st.radio("Mode:", [f"📷 {t('scan_camera')}", f"📁 {t('scan_upload')}"],
                        horizontal=True, label_visibility="collapsed")

    img_file = None
    if t('scan_camera') in cap_mode:
        img_file = st.camera_input(t("scan_capture"))
    else:
        img_file = st.file_uploader(t("scan_upload"), type=["jpg", "jpeg", "png", "bmp", "tiff"])

    if img_file is not None:
        if not p_nom.strip():
            st.error(f"⚠️ {t('scan_nom_required')}")
            st.stop()

        img_hash = hashlib.md5(img_file.getvalue()).hexdigest()
        if st.session_state.get("_last_img_hash") != img_hash:
            st.session_state._last_img_hash = img_hash
            st.session_state.demo_seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = random.randint(0, 999999)

        image = Image.open(img_file).convert("RGB")

        # ✅ تقييم الجودة
        q_score, q_text, q_color = assess_image_quality(image)

        col_img, col_res = st.columns(2)

        with col_img:
            # مؤشر الجودة
            st.markdown(f"""
            <div class='dm-card' style='padding:16px;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-weight:700; font-size:0.85rem;'>📊 {t('scan_image_quality')}</span>
                    <span style='color:{q_color}; font-weight:800;'>{q_text} ({q_score}%)</span>
                </div>
                <div class='quality-bar' style='margin-top:10px;'>
                    <div class='quality-fill' style='width:{q_score}%; background:{q_color};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            tab_orig, tab_thermal, tab_edge, tab_enhance, tab_heatmap = st.tabs(
                ["📷 Original", "🔥 Thermal", "📐 Edges", "✨ Enhanced", "🎯 AI Focus"]
            )
            with tab_orig:
                st.image(image, caption="Vue originale", use_container_width=True)
            with tab_thermal:
                st.image(apply_thermal(image), caption=t("scan_thermal"), use_container_width=True)
            with tab_edge:
                st.image(apply_edge_detection(image), caption=t("scan_edge"), use_container_width=True)
            with tab_enhance:
                st.image(apply_enhanced_contrast(image), caption=t("scan_enhanced"), use_container_width=True)
            with tab_heatmap:
                st.image(generate_heatmap_overlay(image), caption=t("scan_heatmap"), use_container_width=True)

        with col_res:
            st.markdown(f"### 🧠 {t('scan_result')}")
            start_time = time.time()

            with st.spinner(f"⏳ {t('scan_analyzing')}"):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.006)
                    prog.progress(i + 1)
                result = predict_image(model, image)

            analysis_time = round(time.time() - start_time, 1)
            label = result["label"]
            conf = result["confidence"]
            info = result["info"]
            rc = risk_color(info["risk_level"])

            if not result["is_reliable"]:
                st.warning(f"⚠️ {t('scan_low_conf')} ({conf}%)")
            if result["is_demo"]:
                st.info(f"ℹ️ {t('scan_demo_mode')}")

            risk_disp = get_p_text(info, "risk_display")
            morpho = get_p_text(info, "morphology")
            advice = get_p_text(info, "advice")
            funny = get_p_text(info, "funny")

            # ✅ مؤشر الثقة الدائري
            ring_gradient = f"conic-gradient({rc} 0% {conf}%, rgba(100,116,139,0.15) {conf}% 100%)"
            st.markdown(f"""
            <div class='dm-card dm-fade-in' style='border-left:5px solid {rc};'>
                <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;'>
                    <div>
                        <h2 style='color:{rc}; margin:0;'>{label}</h2>
                        <p style='opacity:0.45; font-style:italic; margin-top:4px;'>{info['scientific_name']}</p>
                        <p style='font-size:0.8rem; opacity:0.4; margin-top:8px;'>
                            ⏱️ {t('scan_duration')}: {analysis_time}s
                        </p>
                    </div>
                    <div class='confidence-ring' style='background:{ring_gradient};'>
                        <div class='confidence-ring-inner'>
                            <div class='confidence-value' style='color:{rc};'>{conf}%</div>
                            <div class='confidence-label'>{t('scan_confidence')}</div>
                        </div>
                    </div>
                </div>
                <hr style='opacity:0.1; margin:20px 0;'>
                <p><b>🔬 {t('scan_morphology')}:</b><br><span style='opacity:0.8;'>{morpho}</span></p>
                <p><b>⚠️ {t('scan_risk')}:</b> <span style='color:{rc}; font-weight:800;'>{risk_disp}</span></p>
                <div style='background:rgba(34,197,94,0.06); padding:16px; border-radius:14px; margin:14px 0; border:1px solid rgba(34,197,94,0.12);'>
                    <b>💡 {t('scan_advice')}:</b><br>{advice}
                </div>
                <div style='background:rgba(59,130,246,0.05); padding:16px; border-radius:14px; font-style:italic; border:1px solid rgba(59,130,246,0.1);'>
                    🤖 {funny}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # الفحوصات الإضافية
            extra = get_p_text(info, "extra_tests")
            if isinstance(extra, list) and extra and extra[0] != "N/A":
                with st.expander(f"🩺 {t('scan_extra_tests')}"):
                    for test_item in extra:
                        st.markdown(f"• {test_item}")

            # دورة الحياة
            lifecycle = get_p_text(info, "lifecycle")
            if lifecycle and lifecycle != "N/A":
                with st.expander("🔄 Cycle de Vie"):
                    st.markdown(f"**{lifecycle}**")

            speak(t("voice_result").format(patient=p_nom, parasite=label, funny=funny))

            # كل التنبؤات
            if result["all_predictions"]:
                with st.expander(f"📊 {t('scan_all_probs')}"):
                    for cls, prob in sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True):
                        bar_color = risk_color(PARASITE_DB.get(cls, {}).get("risk_level", "none"))
                        st.markdown(f"""
                        <div style='display:flex; align-items:center; gap:10px; margin:6px 0;'>
                            <span style='width:160px; font-size:0.85rem; font-weight:600;'>{cls}</span>
                            <div class='dm-progress' style='flex:1;'>
                                <div class='dm-progress-fill' style='width:{min(prob,100)}%; background:{bar_color};'></div>
                            </div>
                            <span style='font-family:JetBrains Mono,monospace; font-weight:700; font-size:0.85rem; color:{bar_color};'>{prob}%</span>
                        </div>
                        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📄 Actions")
        a1, a2, a3 = st.columns(3)
        with a1:
            pat = {
                t("scan_nom"): p_nom, t("scan_prenom"): p_prenom,
                t("scan_age"): str(p_age), t("scan_sexe"): p_sexe,
                t("scan_poids"): str(p_poids), t("scan_echantillon"): p_type
            }
            try:
                pdf = generate_pdf(pat, label, conf, info)
                st.download_button(
                    f"📥 {t('scan_download_pdf')}", pdf,
                    f"Rapport_{p_nom}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    "application/pdf", use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF Error: {e}")
        with a2:
            if st.button(f"💾 {t('scan_save')}", use_container_width=True):
                entry = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Patient": f"{p_nom} {p_prenom}".strip(),
                    "Age": p_age, "Sexe": p_sexe,
                    "Echantillon": p_type, "Parasite": label,
                    "Confiance": f"{conf}%",
                    "Risque": _safe_pdf_text(risk_disp),
                    "Status": "Fiable" if result["is_reliable"] else "A verifier",
                    "Duration": f"{analysis_time}s",
                    "Quality": f"{q_score}%"
                }
                st.session_state.history.append(entry)
                st.session_state.scan_count += 1
                if len(st.session_state.history) > MAX_HISTORY:
                    st.session_state.history = st.session_state.history[-MAX_HISTORY:]
                log_activity(f"Scan saved: {label} for {p_nom}")
                st.success(f"✅ {t('scan_saved')}")
        with a3:
            if st.button(f"🔄 {t('scan_new')}", use_container_width=True):
                st.session_state.demo_seed = None
                st.session_state.heatmap_seed = None
                st.session_state._last_img_hash = None
                st.rerun()


# ╔══════════════════════════════════╗
# ║        PAGE: ENCYCLOPEDIA        ║
# ╚══════════════════════════════════╝
elif current_page == "encyclopedia":
    st.title(f"📘 {t('enc_title')}")
    search = st.text_input(f"🔍 {t('enc_search')}", placeholder="amoeba, giardia, plasmodium...")
    st.markdown("---")

    found_any = False
    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if search.strip() and search.lower() not in (name + " " + data["scientific_name"]).lower():
            continue
        found_any = True
        rc = risk_color(data["risk_level"])
        risk_disp = get_p_text(data, "risk_display")

        with st.expander(f"{data.get('icon','🦠')} {name} — *{data['scientific_name']}* | {risk_disp}"):
            ci, cv = st.columns([2.5, 1])
            with ci:
                st.markdown(f"""<div class='dm-card dm-fade-in' style='border-left:4px solid {rc};'>
                <h4 style='color:{rc};'>{data['scientific_name']}</h4>
                <p><b>🔬 {t('scan_morphology')}:</b><br>{get_p_text(data,'morphology')}</p>
                <p><b>📖 Description:</b><br>{get_p_text(data,'description')}</p>
                <p><b>⚠️ {t('scan_risk')}:</b> <span style='color:{rc};font-weight:700;'>{risk_disp}</span></p>
                <div style='background:rgba(22,163,74,0.06);padding:14px;border-radius:14px;margin:10px 0;border:1px solid rgba(22,163,74,0.1);'>
                    <b>💡 {t('scan_advice')}:</b><br>{get_p_text(data,'advice')}
                </div>
                <div style='background:rgba(59,130,246,0.05);padding:14px;border-radius:14px;font-style:italic;border:1px solid rgba(59,130,246,0.08);'>
                    🤖 {get_p_text(data,'funny')}
                </div>
                </div>""", unsafe_allow_html=True)

                lifecycle = get_p_text(data, "lifecycle")
                if lifecycle and lifecycle != "N/A":
                    st.markdown(f"**🔄 Cycle:** {lifecycle}")

                extra = get_p_text(data, "extra_tests")
                if isinstance(extra, list):
                    st.markdown(f"**🩺 {t('scan_extra_tests')}:** {', '.join(extra)}")

            with cv:
                rp = risk_percent(data["risk_level"])
                st.markdown(f'<div style="text-align:center;font-size:5rem;margin:20px 0;">{data.get("icon","🦠")}</div>', unsafe_allow_html=True)
                if rp > 0:
                    st.markdown(f"""
                    <div class='dm-card' style='padding:16px; text-align:center;'>
                        <div style='font-family:JetBrains Mono,monospace; font-size:1.8rem; font-weight:900; color:{rc};'>{rp}%</div>
                        <div style='font-size:0.75rem; opacity:0.5; text-transform:uppercase;'>Danger</div>
                    </div>
                    """, unsafe_allow_html=True)

    if search.strip() and not found_any:
        st.warning(f"🔍 {t('enc_no_result')}")


# ╔══════════════════════════════════╗
# ║        PAGE: DASHBOARD           ║
# ╚══════════════════════════════════╝
elif current_page == "dashboard":
    st.title(f"📊 {t('dash_title')}")
    hist = st.session_state.history
    total = len(hist)

    if total > 0:
        df = pd.DataFrame(hist)
        fiable = df[df["Status"] == "Fiable"].shape[0] if "Status" in df.columns else total
        averif = total - fiable
        common = df["Parasite"].value_counts().idxmax() if "Parasite" in df.columns else "N/A"
    else:
        df = pd.DataFrame()
        fiable = averif = 0
        common = "N/A"

    # مؤشرات الأداء
    kc = st.columns(4)
    for col, (ic, val, lbl, clr) in zip(kc, [
        ("🔬", total, t("dash_total"), "#3b82f6"),
        ("✅", fiable, t("dash_reliable"), "#22c55e"),
        ("⚠️", averif, t("dash_check"), "#f59e0b"),
        ("🦠", common, t("dash_frequent"), "#ef4444"),
    ]):
        with col:
            st.markdown(f"""<div class="dm-metric dm-fade-in">
            <span class="dm-metric-icon">{ic}</span>
            <div class="dm-metric-val" style="color:{clr} !important; -webkit-text-fill-color:{clr};">{val}</div>
            <div class="dm-metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    # حالة النظام
    sc = st.columns(3)
    with sc[0]:
        st.markdown(f"""<div class='dm-card dm-card-green' style='padding:18px;'>
        <div style='display:flex;align-items:center;gap:8px;'>
            <span class="dm-status-dot dm-status-online"></span>
            <span style='font-weight:700;'>{t('dash_system')}</span>
        </div></div>""", unsafe_allow_html=True)
    with sc[1]:
        st.markdown(f"""<div class='dm-card dm-card-blue' style='padding:18px;'>
        <div style='display:flex;align-items:center;gap:8px;'>
            <span>👤</span>
            <span style='font-weight:700;'>{st.session_state.user_name}</span>
        </div></div>""", unsafe_allow_html=True)
    with sc[2]:
        st.markdown(f"""<div class='dm-card dm-card-purple' style='padding:18px;'>
        <div style='display:flex;align-items:center;gap:8px;'>
            <span>🕐</span>
            <span style='font-weight:700;'>{datetime.now().strftime('%H:%M — %d/%m/%Y')}</span>
        </div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    if not df.empty and "Parasite" in df.columns:
        filt = st.selectbox(f"🔍 {t('dash_filter')}", ["Tous/All"] + df["Parasite"].unique().tolist())
        filtered = df if filt == "Tous/All" else df[df["Parasite"] == filt]

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f"#### 📊 {t('dash_distribution')}")
            dist_data = filtered["Parasite"].value_counts()
            st.bar_chart(dist_data, color="#3b82f6")

        with cc2:
            if "Confiance" in filtered.columns:
                st.markdown(f"#### 📈 {t('dash_confidence_chart')}")
                try:
                    cv = filtered["Confiance"].str.rstrip('%').astype(float)
                    st.line_chart(cv.reset_index(drop=True))
                except Exception:
                    pass

        # مقارنة تحاليل مريض
        if "Patient" in df.columns and len(df["Patient"].unique()) > 0:
            st.markdown("---")
            st.markdown(f"### 🔁 {t('dash_patient_compare')}")
            patients = df["Patient"].unique().tolist()
            sel_patient = st.selectbox("Patient:", patients)
            patient_df = df[df["Patient"] == sel_patient]
            st.dataframe(patient_df, use_container_width=True)

        st.markdown("---")
        st.markdown(f"### 📋 {t('dash_history')}")
        st.dataframe(filtered, use_container_width=True)

        # تصدير
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            csv = filtered.to_csv(index=False).encode('utf-8-sig')
            st.download_button(f"⬇️ {t('dash_export')}", csv, "analyses.csv", "text/csv", use_container_width=True)
        with ex2:
            json_data = filtered.to_json(orient='records', force_ascii=False).encode('utf-8')
            st.download_button(f"⬇️ {t('dash_export_json')}", json_data, "analyses.json", "application/json", use_container_width=True)
        with ex3:
            try:
                import openpyxl  # noqa: F401
                buf = io.BytesIO()
                filtered.to_excel(buf, index=False, engine='openpyxl')
                st.download_button(
                    f"⬇️ {t('dash_export_excel')}", buf.getvalue(),
                    "analyses.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            except ImportError:
                st.info("📦 `pip install openpyxl`")
            except Exception as e:
                st.error(f"Excel error: {e}")

        # سجل النشاطات
        if st.session_state.activity_log:
            with st.expander(f"📜 {t('activity_log')}"):
                st.dataframe(pd.DataFrame(st.session_state.activity_log), use_container_width=True)
    else:
        st.markdown(f"""<div class='dm-card dm-fade-in' style='text-align:center;padding:60px;'>
        <div style='font-size:5rem; opacity:0.3;'>📊</div>
        <h3 style='margin-top:16px;'>{t('dash_no_data')}</h3>
        <p style='opacity:0.5;'>{t('dash_no_data_desc')}</p></div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════╗
# ║        PAGE: QUIZ                ║
# ╚══════════════════════════════════╝
elif current_page == "quiz":
    st.title(f"🧠 {t('quiz_title')}")
    st.markdown(f"""<div class='dm-card dm-card-purple dm-fade-in'>
    <p style='font-size:1.05rem;'>{t('quiz_desc')}</p></div>""", unsafe_allow_html=True)

    lang = st.session_state.get("lang", "fr")
    questions = QUIZ_QUESTIONS.get(lang, QUIZ_QUESTIONS["fr"])
    qs = st.session_state.quiz_state

    if not qs["active"]:
        st.markdown("""
        <div class='dm-card' style='text-align:center; padding:40px;'>
            <div style='font-size:4rem; margin-bottom:16px;'>🎮</div>
            <h3>Ready to test your knowledge?</h3>
            <p style='opacity:0.5;'>Answer questions about parasitology!</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎮 Start Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": True}
            log_activity("Quiz started")
            st.rerun()
    else:
        idx = qs["current"]
        if idx < len(questions):
            q = questions[idx]
            prog_pct = idx / len(questions)
            st.markdown(f"""
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;'>
                <span style='font-weight:700;'>{t('quiz_question')} {idx+1}/{len(questions)}</span>
                <span style='font-weight:700; color:#3b82f6;'>{t('quiz_score')}: {qs['score']}/{idx}</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(prog_pct)

            # مستوى الصعوبة
            diff = q.get("difficulty", "medium")
            diff_colors = {"easy": "#22c55e", "medium": "#f59e0b", "hard": "#ef4444"}
            diff_labels = {"easy": "Facile", "medium": "Moyen", "hard": "Difficile"}
            st.markdown(f"""
            <div class='dm-card dm-fade-in'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;'>
                    <span style='font-size:0.8rem; opacity:0.5;'>#{idx+1}</span>
                    <span style='background:{diff_colors.get(diff,"#f59e0b")}22; color:{diff_colors.get(diff,"#f59e0b")};
                           padding:4px 12px; border-radius:20px; font-size:0.75rem; font-weight:700;'>
                        {diff_labels.get(diff, diff)}
                    </span>
                </div>
                <h4>{q['q']}</h4>
            </div>
            """, unsafe_allow_html=True)

            answer_key = f"quiz_answered_{idx}"
            if answer_key not in st.session_state:
                for i, opt in enumerate(q["options"]):
                    if st.button(f"{'ABCD'[i]}. {opt}", key=f"quiz_{idx}_{i}", use_container_width=True):
                        is_correct = (i == q["answer"])
                        if is_correct:
                            st.session_state.quiz_state["score"] += 1
                        st.session_state.quiz_state["answered"].append(is_correct)
                        st.session_state[answer_key] = {"correct": is_correct, "selected": i}
                        st.rerun()
            else:
                answer_data = st.session_state[answer_key]
                if answer_data["correct"]:
                    st.success(f"✅ {t('quiz_correct')}")
                else:
                    st.error(f"❌ {t('quiz_wrong')} → {q['options'][q['answer']]}")
                st.info(f"📖 {q['explanation']}")

                if st.button(f"➡️ {t('quiz_next')}", use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1
                    st.rerun()
        else:
            score = qs["score"]
            total_q = len(questions)
            pct = int(score / total_q * 100) if total_q > 0 else 0

            if pct >= 80: emoji, msg, grade = "🏆", "Excellent !", "A+"
            elif pct >= 60: emoji, msg, grade = "👍", "Bien !", "B"
            elif pct >= 40: emoji, msg, grade = "📚", "Continuez !", "C"
            else: emoji, msg, grade = "💪", "Revoyez !", "D"

            st.markdown(f"""<div class='dm-card dm-card-green dm-fade-in' style='text-align:center; padding:40px;'>
            <div style='font-size:5rem;'>{emoji}</div>
            <h2 style='margin-top:16px;'>{t('quiz_finish')}</h2>
            <div style='font-size:4rem; font-weight:900; font-family:JetBrains Mono,monospace;
                        background:linear-gradient(135deg,#3b82f6,#06b6d4);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        margin:16px 0;'>{score}/{total_q}</div>
            <div style='display:flex; justify-content:center; gap:20px; margin:16px 0;'>
                <div class='dm-card' style='padding:12px 24px;'>
                    <div style='font-size:0.75rem; opacity:0.5;'>Score</div>
                    <div style='font-weight:800; font-size:1.2rem;'>{pct}%</div>
                </div>
                <div class='dm-card' style='padding:12px 24px;'>
                    <div style='font-size:0.75rem; opacity:0.5;'>Grade</div>
                    <div style='font-weight:800; font-size:1.2rem;'>{grade}</div>
                </div>
            </div>
            <p style='font-size:1.1rem; opacity:0.7;'>{msg}</p>
            </div>""", unsafe_allow_html=True)

            log_activity(f"Quiz finished: {score}/{total_q} ({pct}%)")

            if st.button(f"🔄 {t('quiz_restart')}", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("quiz_answered_"):
                        del st.session_state[key]
                st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": False}
                st.rerun()


# ╔══════════════════════════════════╗
# ║        PAGE: CHATBOT             ║
# ╚══════════════════════════════════╝
elif current_page == "chatbot":
    st.title(f"💬 {t('chatbot_title')}")

    lang = st.session_state.get("lang", "fr")
    kb = CHATBOT_KNOWLEDGE.get(lang, CHATBOT_KNOWLEDGE["fr"])

    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "bot", "msg": kb["greeting"]})

    # عرض المحادثة
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"<div class='dm-chat-msg dm-chat-user'>👤 {msg['msg']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='dm-chat-msg dm-chat-bot'>🤖 {msg['msg']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input(t("chatbot_placeholder"))
    if user_input:
        st.session_state.chat_history.append({"role": "user", "msg": user_input})
        reply = chatbot_reply(user_input)
        st.session_state.chat_history.append({"role": "bot", "msg": reply})
        log_activity(f"Chat: {user_input[:50]}")
        st.rerun()

    st.markdown("---")
    st.markdown("**Quick Questions:**")
    qc = st.columns(4)
    quick_qs = {
        "fr": ["Amoeba?", "Giardia?", "Plasmodium?", "Diagnostic?"],
        "ar": ["أميبا؟", "جيارديا؟", "ملاريا؟", "مرحبا"],
        "en": ["Amoeba?", "Giardia?", "Malaria?", "Diagnosis?"]
    }
    for col, q in zip(qc, quick_qs.get(lang, quick_qs["fr"])):
        with col:
            if st.button(q, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                reply = chatbot_reply(q)
                st.session_state.chat_history.append({"role": "bot", "msg": reply})
                st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ╔══════════════════════════════════╗
# ║        PAGE: ABOUT               ║
# ╚══════════════════════════════════╝
elif current_page == "about":
    st.title(f"ℹ️ {t('about_title')}")

    st.markdown(f"""<div class='dm-card dm-card-gradient dm-fade-in' style='text-align:center;'>
    <h1 style='margin:0;'>
        <span style='background:linear-gradient(135deg,#3b82f6,#06b6d4);
              -webkit-background-clip:text; -webkit-text-fill-color:transparent;'>
            🧬 DM SMART LAB AI
        </span>
    </h1>
    <p style='font-size:1.15rem; margin-top:8px;'>
        <span class='dm-version-badge'>v{APP_VERSION} Professional Edition</span>
    </p>
    <p style='opacity:0.55; margin-top:12px;'>{t('about_desc')}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='dm-card dm-fade-in'>
    <h3>📖 {PROJECT_TITLE}</h3>
    <p style='line-height:1.9; opacity:0.8;'>{t('about_project_desc')}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='dm-card dm-card-blue dm-fade-in'>
        <h3>👨‍🔬 {t('about_team')}</h3><br>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:16px;'>
            <div style='width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#06b6d4);
                        display:flex;align-items:center;justify-content:center;font-size:1.4rem;'>🧑‍💻</div>
            <div>
                <p style='font-weight:700;margin:0;'>{AUTHORS['dev1']['name']}</p>
                <p style='opacity:0.5;font-size:0.85rem;margin:0;'>{AUTHORS['dev1']['role']}</p>
            </div>
        </div>
        <div style='display:flex;align-items:center;gap:12px;margin-bottom:16px;'>
            <div style='width:48px;height:48px;border-radius:50%;background:linear-gradient(135deg,#8b5cf6,#ec4899);
                        display:flex;align-items:center;justify-content:center;font-size:1.4rem;'>🔬</div>
            <div>
                <p style='font-weight:700;margin:0;'>{AUTHORS['dev2']['name']}</p>
                <p style='opacity:0.5;font-size:0.85rem;margin:0;'>{AUTHORS['dev2']['role']}</p>
            </div>
        </div>
        <p style='opacity:0.6;font-size:0.9rem;'><b>Niveau:</b> 3eme Annee<br><b>Specialite:</b> Laboratoire de Sante Publique</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='dm-card dm-fade-in'>
        <h3>🏫 {t('about_institution')}</h3><br>
        <p style='font-weight:700;'>{INSTITUTION['name']}</p>
        <p>📍 {INSTITUTION['city']}, {INSTITUTION['country']} 🇩🇿</p><br>
        <h4>🎯 {t('about_objectives')}</h4>
        <ul style='line-height:2;'>
            <li>{t('about_obj1')}</li><li>{t('about_obj2')}</li>
            <li>{t('about_obj3')}</li><li>{t('about_obj4')}</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🛠️ {t('about_tech')}")
    tc = st.columns(6)
    techs = [
        ("🐍","Python","Language"),("🧠","TensorFlow","Deep Learning"),
        ("🎨","Streamlit","Interface"),("📊","Pandas","Data"),
        ("🖼️","Pillow","Imaging"),("📄","FPDF","Reports")
    ]
    for col, (i, n, d) in zip(tc, techs):
        with col:
            st.markdown(f"""<div class="dm-metric dm-fade-in">
            <span class="dm-metric-icon">{i}</span>
            <div class="dm-metric-val" style="font-size:1rem; -webkit-text-fill-color:inherit;">{n}</div>
            <div class="dm-metric-lbl">{d}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🌟 Features v5.0 Professional")
    feat_cols = st.columns(3)
    features = [
        ("🤖", "Dr. DhiaBot", "AI Medical Chatbot"),
        ("🧠", "Smart Quiz", "With difficulty levels"),
        ("🔥", "Multi-Filters", "Thermal + Edge + AI Focus"),
        ("🎯", "AI Heatmap", "Intelligent focus areas"),
        ("📊", "Quality Score", "Image quality assessment"),
        ("⏱️", "Analysis Timer", "Performance tracking"),
        ("🌙", "Pro Dark Mode", "Premium dark theme"),
        ("📈", "Advanced Charts", "Interactive dashboards"),
        ("🔒", "Enhanced Security", "SHA-256 + Auto-lock"),
    ]
    for i, (ic, name, desc) in enumerate(features):
        with feat_cols[i % 3]:
            st.markdown(f"""<div class='dm-card dm-fade-in' style='padding:18px;text-align:center;'>
            <div style='font-size:2rem;margin-bottom:8px;'>{ic}</div>
            <p style='font-weight:800;margin:4px 0;font-size:0.95rem;'>{name}</p>
            <p style='font-size:0.78rem;opacity:0.5;'>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center; padding:20px 0;'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/1200px-Flag_of_Algeria.svg.png' width='80' style='border-radius:8px; box-shadow:0 4px 12px rgba(0,0,0,0.15);'>
    </div>
    """, unsafe_allow_html=True)
    st.caption(f"Fait avec ❤️ à {INSTITUTION['city']} — {INSTITUTION['year']}")
