# ╔══════════════════════════════════════════════════════════════════╗
# ║              DM SMART LAB AI v3.0 - FINAL EDITION               ║
# ║     Diagnostic Parasitologique par Intelligence Artificielle     ║
# ║                                                                  ║
# ║  Développé par:                                                  ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)         ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)            ║
# ║                                                                  ║
# ║  INFSPM - Ouargla, Algérie 🇩🇿                                  ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import numpy as np
import pandas as pd
import time
import os
import base64
import hashlib
import random
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from datetime import datetime, timedelta
from fpdf import FPDF

# ============================================
#  1. إعداد الصفحة (يجب أن يكون أول أمر)
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
#  2. الثوابت والإعدادات العامة
# ============================================
APP_VERSION = "3.0.0"
APP_PASSWORD = "DM@2026secure!"
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)

AUTHORS = {
    "dev1": {"name": "Sebbag Mohamed Dhia Eddine", "role": "Expert IA & Conception"},
    "dev2": {"name": "Ben Sghir Mohamed", "role": "Expert Laboratoire & Données"}
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
#  3. نظام اللغات المتعددة الحقيقي
# ============================================
TRANSLATIONS = {
    "fr": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Où la Science Rencontre l'Intelligence",
        "login_title": "Connexion Sécurisée",
        "login_subtitle": "Accès Réservé au Personnel Médical",
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
        "dash_no_data": "Aucune donnée disponible",
        "dash_no_data_desc": "Effectuez votre première analyse pour voir les statistiques.",
        "about_title": "À Propos du Projet",
        "about_desc": "Système de Diagnostic Parasitologique Assisté par Intelligence Artificielle",
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
        "pdf_title": "RAPPORT D'ANALYSE PARASITOLOGIQUE",
        "pdf_subtitle": "Analyse assistée par Intelligence Artificielle",
        "pdf_patient_section": "INFORMATIONS DU PATIENT",
        "pdf_result_section": "RÉSULTAT DE L'ANALYSE IA",
        "pdf_advice_section": "RECOMMANDATIONS CLINIQUES",
        "pdf_validation": "VALIDATION",
        "pdf_technician": "Technicien de Laboratoire",
        "pdf_disclaimer": "Ce rapport est généré par un système d'IA et doit être validé par un professionnel de santé.",
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
    },
    "ar": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "حيث يلتقي العلم بالذكاء",
        "login_title": "تسجيل الدخول الآمن",
        "login_subtitle": "الدخول مخصص للكوادر الطبية فقط",
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
        "home_welcome": "مرحباً",
        "home_step1_title": "الخطوة 1 : تقديم النظام",
        "home_step1_desc": "اضغط لتشغيل العرض الصوتي لنظام الذكاء الاصطناعي.",
        "home_step1_btn": "بدء العرض",
        "home_step2_title": "الخطوة 2 : عنوان المشروع الرسمي",
        "home_step2_desc": "استمع للعنوان الكامل لمذكرة التخرج.",
        "home_step2_btn": "قراءة العنوان",
        "home_unlocked": "تم فتح النظام بنجاح !",
        "home_go_scan": "انتقل إلى وحدة التشخيص من القائمة الجانبية.",
        "scan_title": "وحدة التشخيص الطفيلي",
        "scan_blocked": "يرجى تفعيل النظام أولاً من صفحة الرئيسية.",
        "scan_patient_info": "بيانات المريض",
        "scan_nom": "اللقب",
        "scan_prenom": "الاسم",
        "scan_age": "العمر",
        "scan_sexe": "الجنس",
        "scan_poids": "الوزن (كغ)",
        "scan_echantillon": "نوع العينة",
        "scan_thermal": "الرؤية الحرارية",
        "scan_capture": "التصوير المجهري",
        "scan_camera": "الكاميرا (مباشر)",
        "scan_upload": "استيراد صورة",
        "scan_nom_required": "اسم المريض إجباري !",
        "scan_analyzing": "جاري التحليل بالذكاء الاصطناعي...",
        "scan_result": "نتيجة الذكاء الاصطناعي",
        "scan_confidence": "نسبة الثقة",
        "scan_morphology": "الشكل المورفولوجي",
        "scan_risk": "مستوى الخطورة",
        "scan_advice": "النصيحة الطبية",
        "scan_low_conf": "نسبة ثقة منخفضة. يُنصح بالتحقق اليدوي !",
        "scan_demo_mode": "وضع العرض التوضيحي (لا يوجد موديل)",
        "scan_download_pdf": "تحميل التقرير PDF",
        "scan_save": "حفظ",
        "scan_saved": "تم الحفظ بنجاح !",
        "scan_new": "تحليل جديد",
        "scan_all_probs": "جميع الاحتمالات",
        "enc_title": "موسوعة الطفيليات",
        "enc_search": "ابحث عن طفيلي...",
        "enc_no_result": "لا توجد نتائج.",
        "dash_title": "لوحة التحكم السريرية",
        "dash_total": "إجمالي التحاليل",
        "dash_reliable": "موثوقة",
        "dash_check": "تحتاج مراجعة",
        "dash_frequent": "الأكثر شيوعاً",
        "dash_system": "النظام يعمل",
        "dash_user": "المستخدم النشط",
        "dash_session": "الجلسة النشطة",
        "dash_filter": "تصفية حسب الطفيلي",
        "dash_distribution": "توزيع الطفيليات",
        "dash_confidence_chart": "مستويات الثقة",
        "dash_history": "السجل الكامل",
        "dash_export": "تصدير CSV",
        "dash_no_data": "لا توجد بيانات",
        "dash_no_data_desc": "قم بإجراء أول تحليل لرؤية الإحصاءات هنا.",
        "about_title": "حول المشروع",
        "about_desc": "نظام التشخيص الطفيلي المعتمد على الذكاء الاصطناعي",
        "about_project_desc": (
            "يستخدم هذا المشروع المبتكر تقنيات التعلم العميق "
            "ورؤية الحاسوب لمساعدة تقنيي المخابر في التعرف "
            "السريع والدقيق على الطفيليات أثناء الفحص المجهري "
            "المباشر للبراز."
        ),
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
        "pdf_title": "تقرير التحليل الطفيلي",
        "pdf_subtitle": "تحليل بمساعدة الذكاء الاصطناعي",
        "pdf_patient_section": "بيانات المريض",
        "pdf_result_section": "نتيجة التحليل",
        "pdf_advice_section": "التوصيات السريرية",
        "pdf_validation": "المصادقة",
        "pdf_technician": "تقني المخبر",
        "pdf_disclaimer": "هذا التقرير مولّد بنظام ذكاء اصطناعي ويجب مصادقته من قبل مختص صحي.",
        "voice_intro": (
            "مرحباً! الساعة الآن {time}. أنا DM Smart Lab، "
            "ذكاء اصطناعي طوّره التقنيان الساميان "
            "{dev1} و{dev2}. "
            "حضّروا شرائحكم، ومن فضلكم لا تدغدغوني بالمجهر!"
        ),
        "voice_title": (
            "مذكرة تخرج: {title}. "
            "المعهد الوطني للتكوين العالي شبه الطبي بورقلة."
        ),
        "voice_result": "النتيجة لـ {patient}: {parasite}. {funny}",
    },
    "en": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Where Science Meets Intelligence",
        "login_title": "Secure Login",
        "login_subtitle": "Access Reserved for Medical Staff",
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
        "home_welcome": "Welcome",
        "home_step1_title": "Step 1: System Presentation",
        "home_step1_desc": "Click to launch the AI system voice presentation.",
        "home_step1_btn": "LAUNCH PRESENTATION",
        "home_step2_title": "Step 2: Official Project Title",
        "home_step2_desc": "Listen to the full thesis title.",
        "home_step2_btn": "READ THE PROJECT TITLE",
        "home_unlocked": "SYSTEM SUCCESSFULLY UNLOCKED!",
        "home_go_scan": "Go to the diagnostic module in the sidebar menu.",
        "scan_title": "Parasitological Diagnostic Unit",
        "scan_blocked": "Please activate the system first on the Home page.",
        "scan_patient_info": "Patient Information",
        "scan_nom": "Last Name",
        "scan_prenom": "First Name",
        "scan_age": "Age",
        "scan_sexe": "Sex",
        "scan_poids": "Weight (kg)",
        "scan_echantillon": "Sample Type",
        "scan_thermal": "Thermal Vision",
        "scan_capture": "Microscopic Capture",
        "scan_camera": "Camera (real-time)",
        "scan_upload": "Import an image",
        "scan_nom_required": "Patient name is required!",
        "scan_analyzing": "AI Analysis in progress...",
        "scan_result": "AI Result",
        "scan_confidence": "Confidence",
        "scan_morphology": "Morphology",
        "scan_risk": "Risk",
        "scan_advice": "Medical Advice",
        "scan_low_conf": "Low confidence. Manual verification recommended!",
        "scan_demo_mode": "Demo mode (no model loaded)",
        "scan_download_pdf": "Download PDF Report",
        "scan_save": "Save",
        "scan_saved": "Result saved successfully!",
        "scan_new": "New Analysis",
        "scan_all_probs": "All probabilities",
        "enc_title": "Parasite Encyclopedia",
        "enc_search": "Search for a parasite...",
        "enc_no_result": "No results found.",
        "dash_title": "Clinical Dashboard",
        "dash_total": "Total Analyses",
        "dash_reliable": "Reliable",
        "dash_check": "To Verify",
        "dash_frequent": "Most Frequent",
        "dash_system": "System Operational",
        "dash_user": "Active User",
        "dash_session": "Active Session",
        "dash_filter": "Filter by parasite",
        "dash_distribution": "Parasite Distribution",
        "dash_confidence_chart": "Confidence Levels",
        "dash_history": "Full History",
        "dash_export": "Export CSV",
        "dash_no_data": "No data available",
        "dash_no_data_desc": "Perform your first analysis to see statistics here.",
        "about_title": "About the Project",
        "about_desc": "AI-Powered Parasitological Diagnostic System",
        "about_project_desc": (
            "This innovative project uses Deep Learning and Computer "
            "Vision to assist lab technicians in rapid and accurate "
            "identification of parasites during fresh stool microscopic "
            "examination."
        ),
        "about_team": "Development Team",
        "about_institution": "Institution",
        "about_objectives": "Objectives",
        "about_obj1": "Automate microscopic reading",
        "about_obj2": "Reduce diagnostic errors",
        "about_obj3": "Speed up the analysis process",
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
        "pdf_title": "PARASITOLOGICAL ANALYSIS REPORT",
        "pdf_subtitle": "AI-Assisted Analysis",
        "pdf_patient_section": "PATIENT INFORMATION",
        "pdf_result_section": "AI ANALYSIS RESULT",
        "pdf_advice_section": "CLINICAL RECOMMENDATIONS",
        "pdf_validation": "VALIDATION",
        "pdf_technician": "Lab Technician",
        "pdf_disclaimer": "This report is AI-generated and must be validated by a healthcare professional.",
        "voice_intro": (
            "Hello! It is {time}. I am DM Smart Lab, "
            "artificial intelligence developed by Senior Technicians "
            "{dev1} and {dev2}. "
            "Prepare your slides, and please don't tickle me with the microscope!"
        ),
        "voice_title": (
            "Graduation Thesis: {title}. "
            "National Institute of Higher Paramedical Training of Ouargla."
        ),
        "voice_result": "Result for {patient}: {parasite}. {funny}",
    }
}

# ============================================
#  4. قاعدة بيانات الطفيليات الشاملة
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {
            "fr": "Kyste sphérique (10-15µm) à 4 noyaux ou Trophozoïte avec pseudopodes et hématies phagocytées (forme invasive).",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 نوى أو طور غاذي بأقدام كاذبة وكريات دم حمراء مبتلعة (شكل غازي).",
            "en": "Spherical cyst (10-15µm) with 4 nuclei or Trophozoite with pseudopods and phagocytosed RBCs (invasive form)."
        },
        "description": {
            "fr": "Parasite tissulaire responsable de la dysenterie amibienne et de l'abcès hépatique. Transmission fécale-orale par ingestion de kystes.",
            "ar": "طفيلي نسيجي مسبب للزحار الأميبي وخراج الكبد. الانتقال عبر الفم-البراز بابتلاع الأكياس.",
            "en": "Tissue parasite causing amoebic dysentery and liver abscess. Fecal-oral transmission through cyst ingestion."
        },
        "funny": {
            "fr": "🥷 Le ninja des intestins ! Il change de forme plus vite que ton humeur un lundi matin.",
            "ar": "🥷 نينجا الأمعاء! يغيّر شكله أسرع من مزاجك يوم الإثنين.",
            "en": "🥷 The intestinal ninja! Changes shape faster than your Monday mood."
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Traitement au Métronidazole (Flagyl) + Amœbicide de contact. Hygiène stricte des mains. Contrôle parasitologique post-traitement.",
            "ar": "علاج بالميترونيدازول (فلاجيل) + مبيد أميبي موضعي. نظافة صارمة لليدين. مراقبة طفيلية بعد العلاج.",
            "en": "Metronidazole (Flagyl) + contact amoebicide. Strict hand hygiene. Post-treatment parasitological control."
        },
        "color": "#dc2626",
        "icon": "🔴"
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia (intestinalis)",
        "morphology": {
            "fr": "Trophozoïte piriforme en 'cerf-volant' (12-15µm) avec 2 noyaux symétriques (face de hibou) et 4 paires de flagelles. Kyste ovoïde à 4 noyaux.",
            "ar": "طور غاذي كمثري على شكل 'طائرة ورقية' (12-15 ميكرومتر) بنواتين متناظرتين (وجه بومة) و4 أزواج من الأسواط. كيس بيضاوي بـ 4 نوى.",
            "en": "Pear-shaped 'kite' trophozoite (12-15µm) with 2 symmetrical nuclei (owl face) and 4 pairs of flagella. Ovoid cyst with 4 nuclei."
        },
        "description": {
            "fr": "Protozoaire flagellé colonisant le duodénum et le jéjunum. Provoque une malabsorption chronique. Très fréquent chez l'enfant.",
            "ar": "أولي سوطي يستعمر الاثني عشر والصائم. يسبب سوء امتصاص مزمن. شائع جداً عند الأطفال.",
            "en": "Flagellated protozoan colonizing the duodenum and jejunum. Causes chronic malabsorption. Very common in children."
        },
        "funny": {
            "fr": "👀 Regarde-le ! Il te fixe avec ses lunettes de soleil. Un vrai touriste qui refuse de partir !",
            "ar": "👀 انظر إليه! يحدّق فيك بنظارته الشمسية. سائح حقيقي يرفض المغادرة!",
            "en": "👀 Look at him! Staring at you with sunglasses. A real tourist who refuses to leave!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Métronidazole ou Tinidazole. Vérifier la source d'eau. Examen parasitologique de toute la famille.",
            "ar": "ميترونيدازول أو تينيدازول. التحقق من مصدر المياه. فحص طفيلي لكل العائلة.",
            "en": "Metronidazole or Tinidazole. Check water source. Parasitological exam for the whole family."
        },
        "color": "#f59e0b",
        "icon": "🟠"
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / tropica",
        "morphology": {
            "fr": "Formes amastigotes ovoïdes (2-5µm) intracellulaires dans les macrophages. Noyau et kinétoplaste bien visibles (coloration MGG).",
            "ar": "أشكال لامسوطة بيضاوية (2-5 ميكرومتر) داخل البلاعم. النواة والحركيات واضحة (تلوين MGG).",
            "en": "Ovoid amastigote forms (2-5µm) intracellular in macrophages. Nucleus and kinetoplast well visible (MGG staining)."
        },
        "description": {
            "fr": "Parasite transmis par la piqûre du phlébotome. Formes: cutanée (bouton d'Orient), viscérale (Kala-azar).",
            "ar": "طفيلي ينتقل عبر لدغة ذبابة الرمل. الأشكال: جلدي (حبة الشرق)، حشوي (كالا آزار).",
            "en": "Parasite transmitted by sandfly bite. Forms: cutaneous (Oriental sore), visceral (Kala-azar)."
        },
        "funny": {
            "fr": "💪 Petit mais costaud ! Il squatte les macrophages comme un invité qui ne part jamais.",
            "ar": "💪 صغير لكن قوي! يسكن البلاعم كضيف لا يغادر أبداً.",
            "en": "💪 Small but tough! Squats in macrophages like a guest who never leaves."
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Glucantime/Amphotéricine B. Maladie à Déclaration Obligatoire (MDO). Protection contre les phlébotomes.",
            "ar": "غلوكانتيم/أمفوتيريسين ب. مرض ذو تصريح إجباري. الحماية من ذباب الرمل.",
            "en": "Glucantime/Amphotericin B. Mandatory reporting disease. Protection against sandflies."
        },
        "color": "#dc2626",
        "icon": "🔴"
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax",
        "morphology": {
            "fr": "Forme en 'bague à chaton' (trophozoïte jeune) à l'intérieur des hématies. Diagnostic par frottis sanguin et goutte épaisse.",
            "ar": "شكل 'خاتم' (طور غاذي فتي) داخل كريات الدم الحمراء. التشخيص بلطاخة الدم والقطرة السميكة.",
            "en": "Signet ring form (young trophozoite) inside RBCs. Diagnosis by blood smear and thick drop."
        },
        "description": {
            "fr": "Agent causal du paludisme (Malaria). P. falciparum: forme la plus grave. Transmission par l'anophèle femelle.",
            "ar": "المسبب للملاريا. المتصورة المنجلية: الشكل الأخطر. الانتقال عبر أنثى الأنوفيل.",
            "en": "Causative agent of Malaria. P. falciparum: most severe form. Transmitted by female Anopheles."
        },
        "funny": {
            "fr": "💍 Il demande le mariage à tes globules rouges ! Une bague très dangereuse, ne dis pas oui !",
            "ar": "💍 يطلب الزواج من كرياتك الحمراء! خاتم خطير جداً، لا تقل نعم!",
            "en": "💍 He proposes to your red blood cells! A very dangerous ring, don't say yes!"
        },
        "risk_level": "critical",
        "risk_display": {"fr": "🚨 URGENCE MÉDICALE", "ar": "🚨 حالة طوارئ طبية", "en": "🚨 MEDICAL EMERGENCY"},
        "advice": {
            "fr": "HOSPITALISATION IMMÉDIATE ! ACT (Artemisinin-based Combination Therapy). Parasitémie toutes les 4-6h. Surveillance rénale et hépatique.",
            "ar": "تنويم فوري! علاج مركب بالأرتيميسينين. فحص الطفيليات كل 4-6 ساعات. مراقبة وظائف الكلى والكبد.",
            "en": "IMMEDIATE HOSPITALIZATION! ACT therapy. Parasitemia every 4-6h. Renal and hepatic monitoring."
        },
        "color": "#7f1d1d",
        "icon": "🚨"
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei / cruzi",
        "morphology": {
            "fr": "Forme allongée en 'S' ou 'C' (15-30µm) avec un flagelle libre antérieur et une membrane ondulante caractéristique. Kinétoplaste bien visible.",
            "ar": "شكل مطاول على شكل 'S' أو 'C' (15-30 ميكرومتر) بسوط حر أمامي وغشاء متموج مميز. الحركيات واضحة.",
            "en": "Elongated 'S' or 'C' shape (15-30µm) with free anterior flagellum and characteristic undulating membrane. Kinetoplast visible."
        },
        "description": {
            "fr": "Parasite extracellulaire du sang. Transmis par la mouche tsé-tsé (T. brucei) ou le triatome (T. cruzi/Chagas).",
            "ar": "طفيلي خارج خلوي في الدم. ينتقل عبر ذبابة تسي تسي أو بق الترياتوم (شاغاس).",
            "en": "Extracellular blood parasite. Transmitted by tsetse fly (T. brucei) or triatomine bug (T. cruzi/Chagas)."
        },
        "funny": {
            "fr": "⚡ Il court dans ton sang comme Mahrez sur l'aile droite ! Imprévisible et rapide.",
            "ar": "⚡ يجري في دمك مثل محرز على الجناح الأيمن! غير متوقع وسريع.",
            "en": "⚡ Runs through your blood like Mahrez on the right wing! Unpredictable and fast."
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Examen du LCR si suspicion de phase neurologique. Pentamidine ou Suramine en phase précoce.",
            "ar": "فحص السائل الدماغي الشوكي عند الاشتباه في المرحلة العصبية. بنتاميدين أو سورامين في المرحلة المبكرة.",
            "en": "CSF exam if neurological phase suspected. Pentamidine or Suramin in early phase."
        },
        "color": "#dc2626",
        "icon": "🔴"
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni",
        "morphology": {
            "fr": "Œuf ovoïde de grande taille (115-170µm) avec un éperon terminal (S. haematobium) ou latéral (S. mansoni) caractéristique.",
            "ar": "بيضة بيضاوية كبيرة (115-170 ميكرومتر) بنتوء طرفي (البلهارسيا الدموية) أو جانبي (المنسونية) مميز.",
            "en": "Large ovoid egg (115-170µm) with characteristic terminal (S. haematobium) or lateral (S. mansoni) spine."
        },
        "description": {
            "fr": "Trématode responsable de la bilharziose. S. haematobium: forme urinaire. S. mansoni: forme intestino-hépatique.",
            "ar": "مثقوبة مسببة للبلهارسيا. البلهارسيا الدموية: شكل بولي. المنسونية: شكل معوي كبدي.",
            "en": "Trematode causing schistosomiasis. S. haematobium: urinary form. S. mansoni: intestino-hepatic form."
        },
        "funny": {
            "fr": "🏊 L'œuf avec un dard ! La prochaine baignade en eau douce pourrait te coûter cher.",
            "ar": "🏊 البيضة ذات الشوكة! السباحة القادمة في المياه العذبة قد تكلفك غالياً.",
            "en": "🏊 The egg with a sting! Your next freshwater swim could cost you dearly."
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Praziquantel (dose unique). Analyse du sédiment urinaire de 24h. Éviter les baignades en eau douce stagnante.",
            "ar": "برازيكوانتيل (جرعة واحدة). تحليل رواسب البول 24 ساعة. تجنب السباحة في المياه العذبة الراكدة.",
            "en": "Praziquantel (single dose). 24h urine sediment analysis. Avoid swimming in stagnant freshwater."
        },
        "color": "#f59e0b",
        "icon": "🟠"
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": {
            "fr": "Absence d'éléments parasitaires après examen macro et microscopique complet (état frais + coloration).",
            "ar": "غياب عناصر طفيلية بعد الفحص العياني والمجهري الكامل (حالة طازجة + تلوين).",
            "en": "Absence of parasitic elements after complete macro and microscopic examination (fresh state + staining)."
        },
        "description": {
            "fr": "Échantillon négatif. Débris alimentaires, cristaux ou artefacts possibles sans signification clinique.",
            "ar": "عينة سلبية. بقايا غذائية أو بلورات أو قطع اصطناعية محتملة بدون أهمية سريرية.",
            "en": "Negative sample. Possible food debris, crystals, or artifacts without clinical significance."
        },
        "funny": {
            "fr": "✨ Rien à signaler ! Ton microscope peut aller se reposer. Champagne ! 🥂",
            "ar": "✨ لا شيء للإبلاغ عنه! مجهرك يمكنه الراحة الآن. شمبانيا! 🥂",
            "en": "✨ Nothing to report! Your microscope can rest now. Champagne! 🥂"
        },
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {
            "fr": "RAS. Continuer une bonne hygiène alimentaire et hydrique. Contrôle recommandé si symptômes persistent.",
            "ar": "لا شيء يُذكر. استمر في النظافة الغذائية والمائية الجيدة. يُنصح بمراقبة إذا استمرت الأعراض.",
            "en": "All clear. Maintain good food and water hygiene. Follow-up recommended if symptoms persist."
        },
        "color": "#16a34a",
        "icon": "🟢"
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())

# ============================================
#  5. تهيئة حالة الجلسة الكاملة
# ============================================
SESSION_DEFAULTS = {
    "logged_in": False,
    "user_name": "",
    "intro_step": 0,
    "history": [],
    "dark_mode": False,
    "last_audio_hash": "",
    "login_attempts": 0,
    "lockout_until": None,
    "lang": "fr",
    "model_loaded": False,
}

for key, val in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================
#  6. دالة الترجمة
# ============================================
def t(key: str) -> str:
    """إرجاع النص المترجم حسب اللغة الحالية"""
    lang = st.session_state.get("lang", "fr")
    translations = TRANSLATIONS.get(lang, TRANSLATIONS["fr"])
    return translations.get(key, TRANSLATIONS["fr"].get(key, key))


def get_parasite_text(parasite_data: dict, field: str) -> str:
    """إرجاع نص الطفيلي حسب اللغة"""
    lang = st.session_state.get("lang", "fr")
    data = parasite_data.get(field, {})
    if isinstance(data, dict):
        return data.get(lang, data.get("fr", ""))
    return str(data)


# ============================================
#  7. دوال مساعدة
# ============================================
def get_greeting() -> str:
    """تحية حسب الوقت"""
    h = datetime.now().hour
    lang = st.session_state.get("lang", "fr")
    if lang == "ar":
        if h < 12: return "صباح الخير"
        elif h < 18: return "مساء الخير"
        return "مساء الخير"
    elif lang == "en":
        if h < 12: return "Good morning"
        elif h < 18: return "Good afternoon"
        return "Good evening"
    else:
        if h < 12: return "Bonjour"
        elif h < 18: return "Bon après-midi"
        return "Bonsoir"


def get_risk_color(level: str) -> str:
    """لون المخاطر"""
    return {
        "critical": "#7f1d1d",
        "high": "#dc2626",
        "medium": "#f59e0b",
        "low": "#22c55e",
        "none": "#16a34a"
    }.get(level, "#6b7280")


def get_risk_percent(level: str) -> int:
    """نسبة الخطورة"""
    return {
        "critical": 100, "high": 80,
        "medium": 50, "low": 25, "none": 0
    }.get(level, 0)


def speak(text: str, lang_code: str = None):
    """تحويل النص إلى صوت مع حماية التكرار"""
    if lang_code is None:
        lang_code = {"fr": "fr", "ar": "ar", "en": "en"}.get(
            st.session_state.get("lang", "fr"), "fr"
        )

    text_hash = hashlib.md5(text.encode()).hexdigest()
    if st.session_state.get("last_audio_hash") == text_hash:
        return

    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang_code)
        fname = f"_temp_audio_{int(time.time())}.mp3"
        tts.save(fname)
        with open(fname, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(
            f'<audio autoplay style="display:none;">'
            f'<source src="data:audio/mp3;base64,{b64}" type="audio/mpeg">'
            f'</audio>',
            unsafe_allow_html=True
        )
        try:
            os.remove(fname)
        except OSError:
            pass
        st.session_state.last_audio_hash = text_hash
    except Exception:
        pass


# ============================================
#  8. محرك الذكاء الاصطناعي
# ============================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    """تحميل موديل الذكاء الاصطناعي"""
    model = None
    model_name = None
    try:
        import tensorflow as tf
        files = os.listdir(".")

        # البحث عن ملفات الموديل
        for ext in [".h5", ".keras"]:
            found = [f for f in files if f.endswith(ext)]
            if found:
                model_name = found[0]
                model = tf.keras.models.load_model(model_name, compile=False)
                break

        # محاولة TFLite
        if model is None:
            tflite_files = [f for f in files if f.endswith(".tflite")]
            if tflite_files:
                model_name = tflite_files[0]
                model = tf.lite.Interpreter(model_path=model_name)
                model.allocate_tensors()

    except Exception as e:
        st.sidebar.warning(f"⚠️ Model: {e}")

    return model, model_name


def predict_image(model, image: Image.Image) -> dict:
    """تحليل الصورة والتنبؤ"""
    result = {
        "label": "Negative",
        "confidence": 0,
        "all_predictions": {},
        "is_reliable": False,
        "is_demo": False,
        "info": PARASITE_DB["Negative"]
    }

    if model is None:
        # وضع العرض التوضيحي
        demo_label = random.choice(CLASS_NAMES)
        demo_conf = random.randint(65, 97)
        result.update({
            "label": demo_label,
            "confidence": demo_conf,
            "is_reliable": demo_conf >= CONFIDENCE_THRESHOLD,
            "is_demo": True,
            "info": PARASITE_DB.get(demo_label, PARASITE_DB["Negative"])
        })
        return result

    try:
        import tensorflow as tf

        # تحضير الصورة
        img = ImageOps.fit(image, MODEL_INPUT_SIZE, Image.LANCZOS)
        img_array = np.asarray(img).astype(np.float32) / 127.5 - 1.0
        img_batch = np.expand_dims(img_array, axis=0)

        if isinstance(model, tf.lite.Interpreter):
            input_det = model.get_input_details()
            output_det = model.get_output_details()
            model.set_tensor(input_det[0]['index'], img_batch)
            model.invoke()
            predictions = model.get_tensor(output_det[0]['index'])[0]
        else:
            predictions = model.predict(img_batch, verbose=0)[0]

        idx = np.argmax(predictions)
        confidence = int(predictions[idx] * 100)
        label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else "Negative"

        all_preds = {}
        for i, cls in enumerate(CLASS_NAMES):
            if i < len(predictions):
                all_preds[cls] = round(float(predictions[i]) * 100, 1)

        result.update({
            "label": label,
            "confidence": confidence,
            "all_predictions": all_preds,
            "is_reliable": confidence >= CONFIDENCE_THRESHOLD,
            "is_demo": False,
            "info": PARASITE_DB.get(label, PARASITE_DB["Negative"])
        })

    except Exception as e:
        st.error(f"Prediction error: {e}")

    return result


def apply_thermal(image: Image.Image) -> Image.Image:
    """فلتر حراري محسّن"""
    enhanced = ImageEnhance.Contrast(image).enhance(1.5)
    gray = ImageOps.grayscale(enhanced)
    smoothed = gray.filter(ImageFilter.GaussianBlur(radius=1))
    return ImageOps.colorize(smoothed, black="navy", white="yellow", mid="red")


# ============================================
#  9. مولد تقارير PDF احترافي
# ============================================
class MedicalPDF(FPDF):
    """تقرير طبي احترافي مع هوية بصرية"""

    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        self.set_font("Arial", "B", 10)
        self.set_text_color(37, 99, 235)
        self.cell(0, 6, "DM SMART LAB AI", 0, 0, "L")
        self.set_font("Arial", "", 9)
        self.set_text_color(100, 116, 139)
        self.cell(0, 6, datetime.now().strftime("%d/%m/%Y  %H:%M"), 0, 1, "R")
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
        self.cell(0, 5, f"DM Smart Lab AI v{APP_VERSION} - {INSTITUTION['name']}", 0, 0, "L")
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", 0, 0, "R")

    def section_header(self, title):
        self.set_fill_color(37, 99, 235)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 11)
        self.cell(0, 8, f"  {title}", 0, 1, "L", fill=True)
        self.ln(3)
        self.set_text_color(0, 0, 0)

    def info_line(self, label, value):
        self.set_font("Arial", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(55, 7, label, 0, 0)
        self.set_font("Arial", "", 10)
        self.set_text_color(0, 0, 0)
        self.cell(0, 7, str(value), 0, 1)


def generate_pdf(patient: dict, label: str, conf: int, info: dict) -> bytes:
    """توليد التقرير"""
    lang = st.session_state.get("lang", "fr")
    pdf = MedicalPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # العنوان
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 12, t("pdf_title"), 0, 1, "C")
    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 6, t("pdf_subtitle"), 0, 1, "C")
    pdf.ln(8)

    # بيانات المريض
    pdf.section_header(t("pdf_patient_section"))
    for k, v in patient.items():
        pdf.info_line(f"{k} :", str(v))
    pdf.info_line("Date :", datetime.now().strftime("%d/%m/%Y"))
    pdf.ln(5)

    # النتيجة
    pdf.section_header(t("pdf_result_section"))
    pdf.ln(2)
    pdf.set_font("Arial", "B", 16)
    if label == "Negative":
        pdf.set_text_color(22, 163, 74)
    else:
        pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 10, f"RESULTAT: {label}", 0, 1, "C")
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 8, f"{t('scan_confidence')}: {conf}%", 0, 1, "C")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Nom scientifique:", 0, 1)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 6, info.get("scientific_name", "N/A"))
    pdf.ln(2)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, f"{t('scan_morphology')}:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, get_parasite_text(info, "morphology"))
    pdf.ln(2)

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 7, "Description:", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, get_parasite_text(info, "description"))
    pdf.ln(2)

    pdf.set_font("Arial", "B", 10)
    risk_txt = info.get("risk_display", {})
    if isinstance(risk_txt, dict):
        risk_txt = risk_txt.get(lang, risk_txt.get("fr", ""))
    pdf.cell(0, 7, f"{t('scan_risk')}: {risk_txt}", 0, 1)
    pdf.ln(5)

    # التوصيات
    pdf.section_header(t("pdf_advice_section"))
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, get_parasite_text(info, "advice"))
    pdf.ln(10)

    # التوقيعات
    pdf.section_header(t("pdf_validation"))
    pdf.ln(5)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(95, 7, f"{t('pdf_technician')} :", 0, 0)
    pdf.cell(95, 7, f"{t('pdf_technician')} :", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.cell(95, 7, AUTHORS["dev1"]["name"], 0, 0)
    pdf.cell(95, 7, AUTHORS["dev2"]["name"], 0, 1)
    pdf.ln(12)

    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5, t("pdf_disclaimer"))

    return pdf.output(dest='S').encode('latin-1')


# ============================================
#  10. التصميم CSS الاحترافي الكامل
# ============================================
def apply_full_theme():
    """تطبيق التصميم المتكامل"""
    dm = st.session_state.get("dark_mode", False)

    if dm:
        bg = "#050a15"
        bg2 = "#0a1628"
        card = "#0f1d32"
        card_hover = "#142540"
        text = "#e2e8f0"
        text_muted = "#64748b"
        border = "#1e3a5f"
        primary = "#3b82f6"
        primary_dark = "#1d4ed8"
        primary_glow = "rgba(59, 130, 246, 0.15)"
        accent = "#06b6d4"
        sidebar_bg = "#030712"
        sidebar_border = "#1e293b"
        input_bg = "#0f1d32"
        grad1 = "#0a1628"
        grad2 = "#050a15"
        grad3 = "#0f1d32"
        dot_color = "rgba(59, 130, 246, 0.06)"
        shadow = "rgba(0,0,0,0.5)"
        glass = "rgba(15, 29, 50, 0.8)"
        glass_border = "rgba(59, 130, 246, 0.15)"
    else:
        bg = "#f0f4f8"
        bg2 = "#ffffff"
        card = "#ffffff"
        card_hover = "#f8fafc"
        text = "#0f172a"
        text_muted = "#64748b"
        border = "#e2e8f0"
        primary = "#2563eb"
        primary_dark = "#1e40af"
        primary_glow = "rgba(37, 99, 235, 0.1)"
        accent = "#0891b2"
        sidebar_bg = "#f8fafc"
        sidebar_border = "#e2e8f0"
        input_bg = "#ffffff"
        grad1 = "#dbeafe"
        grad2 = "#f0f4f8"
        grad3 = "#e0f2fe"
        dot_color = "rgba(37, 99, 235, 0.04)"
        shadow = "rgba(0,0,0,0.06)"
        glass = "rgba(255, 255, 255, 0.85)"
        glass_border = "rgba(37, 99, 235, 0.12)"

    st.markdown(f"""
    <style>
    /* ========================================= */
    /*          IMPORTS & RESET                   */
    /* ========================================= */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    *, *::before, *::after {{
        box-sizing: border-box;
    }}

    html, body, [class*="css"], p, span, label, div,
    .stMarkdown, .stText, li, td, th {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', Roboto, sans-serif !important;
        color: {text} !important;
    }}

    h1 {{ font-size: 2.2rem !important; font-weight: 800 !important; letter-spacing: -0.03em; }}
    h2 {{ font-size: 1.6rem !important; font-weight: 700 !important; letter-spacing: -0.02em; }}
    h3 {{ font-size: 1.3rem !important; font-weight: 700 !important; }}
    h4 {{ font-size: 1.1rem !important; font-weight: 600 !important; }}
    h1, h2, h3, h4, h5, h6 {{
        font-family: 'Inter', sans-serif !important;
        color: {text} !important;
    }}

    /* ========================================= */
    /*          MAIN BACKGROUND                   */
    /* ========================================= */
    .stApp {{
        background:
            radial-gradient(ellipse at 20% 50%, {grad1} 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, {grad3} 0%, transparent 50%),
            radial-gradient(ellipse at 50% 100%, {grad1} 0%, transparent 50%),
            linear-gradient(180deg, {bg} 0%, {bg2} 100%);
        background-attachment: fixed;
    }}

    /* شبكة النقاط */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image:
            radial-gradient(circle, {dot_color} 1.2px, transparent 1.2px);
        background-size: 28px 28px;
        pointer-events: none;
        z-index: 0;
    }}

    /* ========================================= */
    /*          SIDEBAR                           */
    /* ========================================= */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sidebar_bg} 0%, {bg2} 100%) !important;
        border-right: 1px solid {sidebar_border} !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] .stRadio > label {{
        font-weight: 500 !important;
        padding: 4px 0 !important;
    }}

    section[data-testid="stSidebar"] hr {{
        border-color: {sidebar_border} !important;
        opacity: 0.5;
    }}

    /* ========================================= */
    /*          GLASS CARDS                       */
    /* ========================================= */
    .dm-card {{
        background: {glass};
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid {glass_border};
        border-radius: 20px;
        padding: 28px;
        margin: 14px 0;
        box-shadow:
            0 4px 30px {shadow},
            inset 0 1px 0 rgba(255,255,255,0.05);
        position: relative;
        z-index: 2;
        transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }}

    .dm-card:hover {{
        transform: translateY(-3px);
        box-shadow:
            0 12px 40px {shadow},
            0 0 0 1px {glass_border},
            inset 0 1px 0 rgba(255,255,255,0.08);
    }}

    .dm-card-blue {{ border-left: 4px solid {primary}; }}
    .dm-card-red {{ border-left: 4px solid #ef4444; }}
    .dm-card-green {{ border-left: 4px solid #22c55e; }}
    .dm-card-orange {{ border-left: 4px solid #f59e0b; }}
    .dm-card-purple {{ border-left: 4px solid #8b5cf6; }}

    /* ========================================= */
    /*          METRIC CARDS                      */
    /* ========================================= */
    .dm-metric {{
        background: {glass};
        backdrop-filter: blur(10px);
        border: 1px solid {glass_border};
        border-radius: 18px;
        padding: 22px 16px;
        text-align: center;
        box-shadow: 0 2px 16px {shadow};
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}

    .dm-metric::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, {primary}, {accent});
        border-radius: 18px 18px 0 0;
    }}

    .dm-metric:hover {{
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 8px 30px {shadow};
    }}

    .dm-metric-icon {{
        font-size: 1.8rem;
        margin-bottom: 8px;
        display: block;
    }}

    .dm-metric-val {{
        font-size: 2rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace !important;
        color: {primary} !important;
        line-height: 1.2;
    }}

    .dm-metric-lbl {{
        font-size: 0.78rem;
        font-weight: 600;
        color: {text_muted} !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 8px;
    }}

    /* ========================================= */
    /*          BUTTONS                           */
    /* ========================================= */
    div.stButton > button {{
        background: linear-gradient(135deg, {primary} 0%, {primary_dark} 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 13px 30px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        letter-spacing: 0.015em;
        transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94) !important;
        box-shadow:
            0 4px 15px rgba(37, 99, 235, 0.3),
            0 1px 3px rgba(0,0,0,0.1) !important;
        position: relative;
        overflow: hidden;
    }}

    div.stButton > button::after {{
        content: '';
        position: absolute;
        top: 0; left: -100%; right: 0; bottom: 0;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
        transition: left 0.5s ease;
    }}

    div.stButton > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow:
            0 8px 28px rgba(37, 99, 235, 0.45),
            0 2px 6px rgba(0,0,0,0.15) !important;
    }}

    div.stButton > button:hover::after {{
        left: 100%;
    }}

    div.stButton > button:active {{
        transform: translateY(0) scale(0.98) !important;
    }}

    /* ========================================= */
    /*          INPUTS                            */
    /* ========================================= */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        background: {input_bg} !important;
        border: 2px solid {border} !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        color: {text} !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
    }}

    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {primary} !important;
        box-shadow: 0 0 0 4px {primary_glow} !important;
        outline: none !important;
    }}

    .stSelectbox > div > div > div {{
        background: {input_bg} !important;
        border: 2px solid {border} !important;
        border-radius: 12px !important;
        color: {text} !important;
    }}

    /* ========================================= */
    /*          EXPANDER                          */
    /* ========================================= */
    .streamlit-expanderHeader {{
        background: {glass} !important;
        border: 1px solid {glass_border} !important;
        border-radius: 14px !important;
        font-weight: 600 !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }}

    .streamlit-expanderHeader:hover {{
        background: {card_hover} !important;
        border-color: {primary} !important;
    }}

    /* ========================================= */
    /*          PROGRESS BAR                      */
    /* ========================================= */
    .stProgress > div > div > div {{
        background: linear-gradient(90deg, {primary}, {accent}) !important;
        border-radius: 10px !important;
        height: 8px !important;
    }}

    /* ========================================= */
    /*          DATAFRAME / TABLE                 */
    /* ========================================= */
    .stDataFrame {{
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid {border} !important;
    }}

    /* ========================================= */
    /*          LOGO ANIMATION                    */
    /* ========================================= */
    .dm-logo-wrap {{
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 24px 0 16px 0;
        position: relative;
        z-index: 5;
    }}

    .dm-logo-main {{
        display: flex;
        align-items: center;
        gap: 6px;
        animation: logoBreath 4s ease-in-out infinite;
    }}

    .dm-logo-char {{
        font-family: 'Inter', sans-serif;
        font-size: 3.8rem;
        font-weight: 900;
        line-height: 1;
        display: inline-block;
    }}

    .dm-logo-d {{
        color: {primary};
        text-shadow: 0 0 30px {primary_glow};
        animation: charShift 3s ease-in-out infinite;
    }}

    .dm-logo-m {{
        color: white;
        background: linear-gradient(135deg, {primary}, {accent});
        padding: 6px 20px;
        border-radius: 14px;
        box-shadow:
            0 4px 20px rgba(37, 99, 235, 0.35),
            inset 0 1px 0 rgba(255,255,255,0.2);
        animation: charShift 3s ease-in-out infinite 0.5s;
    }}

    .dm-logo-tag {{
        font-size: 0.82rem;
        font-weight: 600;
        color: {text_muted};
        letter-spacing: 0.35em;
        text-transform: uppercase;
        margin-top: 10px;
    }}

    .dm-logo-line {{
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, {primary}, {accent});
        border-radius: 3px;
        margin-top: 8px;
    }}

    @keyframes logoBreath {{
        0%, 100% {{ transform: translateY(0) scale(1); }}
        50% {{ transform: translateY(-5px) scale(1.02); }}
    }}

    @keyframes charShift {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-3px); }}
    }}

    /* ========================================= */
    /*          FLOATING PARTICLES                */
    /* ========================================= */
    .dm-particle {{
        position: fixed;
        pointer-events: none;
        z-index: 0;
        opacity: 0;
        font-size: 1.8rem;
        animation: particleRise 25s linear infinite;
    }}

    @keyframes particleRise {{
        0% {{
            transform: translateY(105vh) rotate(0deg) scale(0.7);
            opacity: 0;
        }}
        8% {{ opacity: 0.08; }}
        92% {{ opacity: 0.08; }}
        100% {{
            transform: translateY(-10vh) rotate(360deg) scale(1);
            opacity: 0;
        }}
    }}

    /* ========================================= */
    /*          STEP INDICATOR                    */
    /* ========================================= */
    .dm-step {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 18px;
        border-radius: 12px;
        margin: 6px 0;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
    }}

    .dm-step-done {{
        background: rgba(34, 197, 94, 0.1);
        border: 1px solid rgba(34, 197, 94, 0.3);
        color: #22c55e !important;
    }}

    .dm-step-active {{
        background: {primary_glow};
        border: 1px solid rgba(37, 99, 235, 0.3);
        color: {primary} !important;
        animation: stepPulse 2s ease-in-out infinite;
    }}

    .dm-step-pending {{
        background: rgba(100, 116, 139, 0.05);
        border: 1px solid rgba(100, 116, 139, 0.15);
        color: {text_muted} !important;
    }}

    @keyframes stepPulse {{
        0%, 100% {{ box-shadow: 0 0 0 0 {primary_glow}; }}
        50% {{ box-shadow: 0 0 0 8px transparent; }}
    }}

    /* ========================================= */
    /*          RESULT BADGE                      */
    /* ========================================= */
    .dm-result-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        border-radius: 50px;
        font-weight: 700;
        font-size: 0.85rem;
        letter-spacing: 0.05em;
    }}

    /* ========================================= */
    /*          RESPONSIVE                        */
    /* ========================================= */
    @media (max-width: 768px) {{
        .dm-logo-char {{ font-size: 2.8rem; }}
        .dm-card {{ padding: 18px; border-radius: 16px; }}
        .dm-metric {{ padding: 16px 12px; }}
        .dm-metric-val {{ font-size: 1.5rem; }}
        h1 {{ font-size: 1.6rem !important; }}
    }}

    /* ========================================= */
    /*          PRINT                             */
    /* ========================================= */
    @media print {{
        .dm-particle,
        section[data-testid="stSidebar"],
        .stApp::before {{
            display: none !important;
        }}
    }}

    /* ========================================= */
    /*       SCROLLBAR (dark mode only)           */
    /* ========================================= */
    {"" if not dm else f'''
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: {bg}; }}
    ::-webkit-scrollbar-thumb {{
        background: {border};
        border-radius: 10px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: {primary}; }}
    '''}
    </style>

    <!-- Floating Particles -->
    <div class="dm-particle" style="left:4%;animation-delay:0s;">🦠</div>
    <div class="dm-particle" style="left:15%;animation-delay:5s;">🧬</div>
    <div class="dm-particle" style="left:30%;animation-delay:10s;">🔬</div>
    <div class="dm-particle" style="left:48%;animation-delay:3s;">🩸</div>
    <div class="dm-particle" style="left:65%;animation-delay:8s;">🧪</div>
    <div class="dm-particle" style="left:80%;animation-delay:13s;">💊</div>
    <div class="dm-particle" style="left:92%;animation-delay:6s;">🧫</div>
    """, unsafe_allow_html=True)


# تطبيق التصميم فوراً
apply_full_theme()


# ============================================
#  11. اللوقو المتحرك
# ============================================
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
#  12. صفحة تسجيل الدخول
# ============================================
if not st.session_state.logged_in:
    # التحقق من القفل
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
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='dm-card dm-card-blue' style='text-align:center;'>
            <div style='font-size:3.5rem; margin-bottom:12px;'>🔐</div>
            <h2 style='margin:0;'>{t('login_title')}</h2>
            <p style='opacity:0.6; margin-top:6px;'>{t('login_subtitle')}</p>
        </div>
        """, unsafe_allow_html=True)

        # اختيار اللغة قبل الدخول
        lang_options = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
        selected_lang = st.selectbox(
            f"🌍 {t('language')}",
            options=list(lang_options.keys()),
            index=0
        )
        new_lang = lang_options[selected_lang]
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=True):
            user = st.text_input(f"👤 {t('login_user')}", placeholder="Dr. / TLS ...")
            pwd = st.text_input(f"🔒 {t('login_pass')}", type="password", placeholder="••••••••")
            submitted = st.form_submit_button(f"🔓 {t('login_btn')}", use_container_width=True)

            if submitted:
                if not user.strip():
                    st.warning(f"⚠️ {t('login_user')}")
                elif pwd == APP_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.strip()
                    st.session_state.login_attempts = 0
                    st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    left = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
                    if left <= 0:
                        st.session_state.lockout_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
                        st.error(f"🔒 {t('login_locked')} ({LOCKOUT_MINUTES} min)")
                    else:
                        st.error(f"❌ {t('login_error')}. {left} {t('login_attempts')}.")

        st.markdown("""
        <div style='text-align:center; margin-top:24px; opacity:0.35; font-size:0.78rem;'>
            🔐 Powered by DM Smart Lab AI
        </div>
        """, unsafe_allow_html=True)

    st.stop()


# ============================================
#  13. الشريط الجانبي (بعد الدخول)
# ============================================
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center; padding:12px 0 8px 0;'>
        <div style='font-size:2.8rem;'>🧬</div>
        <h3 style='margin:6px 0 2px 0;'>DM SMART LAB</h3>
        <p style='font-size:0.72rem; opacity:0.4; letter-spacing:0.2em;
                  text-transform:uppercase; margin:0;'>
            Smart Lab AI v{APP_VERSION}
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.user_name}**")
    st.markdown("---")

    # اختيار اللغة
    lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
    current_lang_display = [k for k, v in lang_opts.items() if v == st.session_state.lang]
    current_idx = list(lang_opts.values()).index(st.session_state.lang) if st.session_state.lang in lang_opts.values() else 0

    sel_lang = st.selectbox(
        f"🌍 {t('language')}",
        options=list(lang_opts.keys()),
        index=current_idx
    )
    new_lang_val = lang_opts[sel_lang]
    if new_lang_val != st.session_state.lang:
        st.session_state.lang = new_lang_val
        st.rerun()

    st.markdown("---")

    # القائمة
    nav_items = [
        f"🏠 {t('nav_home')}",
        f"🔬 {t('nav_scan')}",
        f"📘 {t('nav_encyclopedia')}",
        f"📊 {t('nav_dashboard')}",
        f"ℹ️ {t('nav_about')}"
    ]
    menu = st.radio("📌 Navigation", nav_items, label_visibility="collapsed")

    st.markdown("---")

    # الوضع الليلي
    dark = st.toggle(f"🌙 {t('night_mode')}", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")

    if st.button(f"🚪 {t('logout')}", use_container_width=True):
        for k in SESSION_DEFAULTS:
            st.session_state[k] = SESSION_DEFAULTS[k]
        st.rerun()

    st.markdown(f"""
    <div style='text-align:center; opacity:0.3; font-size:0.7rem; margin-top:20px;'>
        v{APP_VERSION} — INFSPM Ouargla
    </div>
    """, unsafe_allow_html=True)


# ============================================
#  14. توجيه الصفحات
# ============================================
page_map = {
    nav_items[0]: "home",
    nav_items[1]: "scan",
    nav_items[2]: "encyclopedia",
    nav_items[3]: "dashboard",
    nav_items[4]: "about"
}
current_page = page_map.get(menu, "home")


# ╔══════════════════════════════════════════╗
# ║          PAGE: HOME / ACCUEIL            ║
# ╚══════════════════════════════════════════╝
if current_page == "home":
    st.title(f"👋 {get_greeting()}, {st.session_state.user_name} !")

    c_icon, c_text = st.columns([1, 2.5])
    with c_icon:
        st.markdown("""
        <div style="text-align:center; padding:20px 0;">
            <div style="font-size:7rem; line-height:1;">🤖</div>
        </div>
        """, unsafe_allow_html=True)

    with c_text:
        st.markdown(f"""
        <div class='dm-card dm-card-blue'>
            <h3>🧬 DM SMART LAB — {t('app_subtitle')}</h3>
            <p>{t('home_step1_desc') if st.session_state.intro_step == 0 else
                t('home_step2_desc') if st.session_state.intro_step == 1 else
                t('home_go_scan')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # شريط الخطوات
    step = st.session_state.intro_step
    steps_data = [
        (t("home_step1_title"), "1️⃣"),
        (t("home_step2_title"), "2️⃣"),
        (t("home_unlocked"), "3️⃣"),
    ]

    step_cols = st.columns(3)
    for i, (lbl, icon) in enumerate(steps_data):
        with step_cols[i]:
            if step > i:
                css_class = "dm-step-done"
                status = "✅"
            elif step == i:
                css_class = "dm-step-active"
                status = "⏳"
            else:
                css_class = "dm-step-pending"
                status = "⬜"
            st.markdown(
                f'<div class="dm-step {css_class}">{status} {icon} {lbl}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # الخطوة 1
    if step == 0:
        st.markdown(f"""
        <div class='dm-card dm-card-orange'>
            <h4>🔒 {t('home_step1_title')}</h4>
            <p>{t('home_step1_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🔊 {t('home_step1_btn')}", use_container_width=True, type="primary"):
            voice_text = t("voice_intro").format(
                time=datetime.now().strftime("%H:%M"),
                dev1=AUTHORS["dev1"]["name"],
                dev2=AUTHORS["dev2"]["name"]
            )
            speak(voice_text)
            with st.spinner("🔊 ..."):
                time.sleep(12)
            st.session_state.intro_step = 1
            st.rerun()

    # الخطوة 2
    elif step == 1:
        st.markdown(f"""
        <div class='dm-card dm-card-orange'>
            <h4>🔒 {t('home_step2_title')}</h4>
            <p>{t('home_step2_desc')}</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button(f"🔊 {t('home_step2_btn')}", use_container_width=True, type="primary"):
            voice_text = t("voice_title").format(title=PROJECT_TITLE)
            speak(voice_text)
            with st.spinner("🔊 ..."):
                time.sleep(12)
            st.session_state.intro_step = 2
            st.rerun()

    # تم الفتح
    elif step >= 2:
        st.markdown(f"""
        <div class='dm-card dm-card-green'>
            <h3>✅ {t('home_unlocked')}</h3>
            <p style='font-size:1.05rem;'>{t('home_go_scan')}</p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()


# ╔══════════════════════════════════════════╗
# ║          PAGE: SCAN & ANALYSE            ║
# ╚══════════════════════════════════════════╝
elif current_page == "scan":
    st.title(f"🔬 {t('scan_title')}")

    if st.session_state.intro_step < 2:
        st.error(f"⛔ {t('scan_blocked')}")
        st.stop()

    # تحميل الموديل
    model, model_name = load_ai_model()
    if model_name:
        st.sidebar.success(f"🧠 {model_name}")
    else:
        st.sidebar.info("🧠 Demo Mode")

    # === بيانات المريض ===
    st.markdown(f"### 📋 1. {t('scan_patient_info')}")
    st.markdown('<div class="dm-card">', unsafe_allow_html=True)

    ca, cb = st.columns(2)
    p_nom = ca.text_input(f"{t('scan_nom')} *", placeholder="Benali")
    p_prenom = cb.text_input(t("scan_prenom"), placeholder="Ahmed")

    cc, cd, ce, cf = st.columns(4)
    p_age = cc.number_input(t("scan_age"), 0, 120, 30)
    p_sexe = cd.selectbox(t("scan_sexe"), [t("patient_sexe_h"), t("patient_sexe_f")])
    p_poids = ce.number_input(t("scan_poids"), 0, 300, 70)
    sample_options = [
        t("echantillon_selles"), t("echantillon_sang_frottis"),
        t("echantillon_sang_goutte"), t("echantillon_urines"),
        t("echantillon_lcr"), t("echantillon_autre")
    ]
    p_type = cf.selectbox(t("scan_echantillon"), sample_options)

    thermal = st.toggle(f"🔥 {t('scan_thermal')}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # === التصوير ===
    st.markdown(f"### 📸 2. {t('scan_capture')}")
    cap_mode = st.radio(
        "Mode:",
        [f"📷 {t('scan_camera')}", f"📁 {t('scan_upload')}"],
        horizontal=True,
        label_visibility="collapsed"
    )

    img_file = None
    if t('scan_camera') in cap_mode:
        img_file = st.camera_input(t("scan_capture"))
    else:
        img_file = st.file_uploader(
            t("scan_upload"),
            type=["jpg", "jpeg", "png", "bmp", "tiff"]
        )

    # === التحليل ===
    if img_file is not None:
        if not p_nom.strip():
            st.error(f"⚠️ {t('scan_nom_required')}")
            st.stop()

        image = Image.open(img_file).convert("RGB")
        col_img, col_res = st.columns(2)

        with col_img:
            if thermal:
                disp = apply_thermal(image)
                st.image(disp, caption=f"🔥 {t('scan_thermal')}", use_container_width=True)
            else:
                st.image(image, caption="📷 Microscope", use_container_width=True)

        with col_res:
            st.markdown(f"### 🧠 {t('scan_result')}")

            with st.spinner(f"⏳ {t('scan_analyzing')}"):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.012)
                    prog.progress(i + 1)
                result = predict_image(model, image)

            label = result["label"]
            conf = result["confidence"]
            info = result["info"]
            rc = get_risk_color(info["risk_level"])

            # تحذيرات
            if not result["is_reliable"]:
                st.warning(f"⚠️ {t('scan_low_conf')} ({conf}%)")
            if result["is_demo"]:
                st.info(f"ℹ️ {t('scan_demo_mode')}")

            # بطاقة النتيجة
            risk_disp = get_parasite_text(info, "risk_display")
            morpho_text = get_parasite_text(info, "morphology")
            advice_text = get_parasite_text(info, "advice")
            funny_text = get_parasite_text(info, "funny")

            st.markdown(f"""
            <div class='dm-card' style='border-left:5px solid {rc};'>
                <div style='display:flex; justify-content:space-between;
                            align-items:center; flex-wrap:wrap; gap:12px;'>
                    <div>
                        <h2 style='color:{rc}; margin:0;'>{label}</h2>
                        <p style='opacity:0.55; margin:4px 0 0 0;
                                  font-style:italic;'>
                            {info['scientific_name']}
                        </p>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:2.8rem; font-weight:900;
                                    color:{rc};
                                    font-family:JetBrains Mono,monospace;'>
                            {conf}%
                        </div>
                        <div style='font-size:0.75rem; opacity:0.45;
                                    text-transform:uppercase;
                                    letter-spacing:0.1em;'>
                            {t('scan_confidence')}
                        </div>
                    </div>
                </div>

                <hr style='opacity:0.15; margin:16px 0;'>

                <p><b>🔬 {t('scan_morphology')} :</b><br>
                   <span style='opacity:0.85;'>{morpho_text}</span></p>

                <p><b>⚠️ {t('scan_risk')} :</b>
                   <span style='color:{rc}; font-weight:700;'>
                       {risk_disp}
                   </span></p>

                <div style='background:rgba(34,197,94,0.08); padding:14px;
                            border-radius:12px; margin:12px 0;'>
                    <b>💡 {t('scan_advice')} :</b><br>
                    <span style='opacity:0.85;'>{advice_text}</span>
                </div>

                <div style='background:rgba(37,99,235,0.06); padding:14px;
                            border-radius:12px; font-style:italic;'>
                    🤖 {funny_text}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # الصوت
            voice_result = t("voice_result").format(
                patient=p_nom, parasite=label, funny=funny_text
            )
            speak(voice_result)

            # جميع التنبؤات
            if result["all_predictions"]:
                with st.expander(f"📊 {t('scan_all_probs')}"):
                    for cls, prob in sorted(
                        result["all_predictions"].items(),
                        key=lambda x: x[1], reverse=True
                    ):
                        st.progress(prob / 100, text=f"{cls}: {prob}%")

        st.markdown("---")
        st.markdown("### 📄 Actions")

        act1, act2, act3 = st.columns(3)

        with act1:
            patient_dict = {
                t("scan_nom"): p_nom,
                t("scan_prenom"): p_prenom,
                t("scan_age"): f"{p_age}",
                t("scan_sexe"): p_sexe,
                t("scan_poids"): f"{p_poids}",
                t("scan_echantillon"): p_type
            }
            pdf_bytes = generate_pdf(patient_dict, label, conf, info)
            st.download_button(
                f"📥 {t('scan_download_pdf')}",
                data=pdf_bytes,
                file_name=f"Rapport_{p_nom}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with act2:
            if st.button(f"💾 {t('scan_save')}", use_container_width=True):
                entry = {
                    "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Patient": f"{p_nom} {p_prenom}".strip(),
                    "Age": p_age,
                    "Sexe": p_sexe,
                    "Echantillon": p_type,
                    "Parasite": label,
                    "Confiance": f"{conf}%",
                    "Risque": risk_disp,
                    "Status": "Fiable" if result["is_reliable"] else "A verifier"
                }
                st.session_state.history.append(entry)
                st.success(f"✅ {t('scan_saved')}")

        with act3:
            if st.button(f"🔄 {t('scan_new')}", use_container_width=True):
                st.rerun()


# ╔══════════════════════════════════════════╗
# ║          PAGE: ENCYCLOPÉDIE              ║
# ╚══════════════════════════════════════════╝
elif current_page == "encyclopedia":
    st.title(f"📘 {t('enc_title')}")

    search = st.text_input(f"🔍 {t('enc_search')}", placeholder="amoeba, giardia, plasmodium...")

    st.markdown("---")

    # إحصائيات
    stat_c = st.columns(4)
    total_parasites = len([k for k in PARASITE_DB if k != "Negative"])
    high_risk = sum(1 for v in PARASITE_DB.values() if v.get("risk_level") in ["high", "critical"])
    med_risk = sum(1 for v in PARASITE_DB.values() if v.get("risk_level") == "medium")

    for col, (ic, val, lbl, clr) in zip(stat_c, [
        ("🦠", total_parasites, "Parasites", "#2563eb"),
        ("🔴", high_risk, "Risque Élevé", "#dc2626"),
        ("🟠", med_risk, "Risque Moyen", "#f59e0b"),
        ("📖", len(PARASITE_DB), "Total Fiches", "#8b5cf6"),
    ]):
        with col:
            st.markdown(f"""
            <div class="dm-metric">
                <span class="dm-metric-icon">{ic}</span>
                <div class="dm-metric-val" style="color:{clr} !important;">{val}</div>
                <div class="dm-metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue

        # فلترة البحث
        if search.strip():
            searchable = (name + data["scientific_name"]).lower()
            if search.lower() not in searchable:
                continue

        rc = get_risk_color(data["risk_level"])
        risk_disp = get_parasite_text(data, "risk_display")

        with st.expander(f"🔬 {name} — *{data['scientific_name']}* | {risk_disp}"):
            ci, cv = st.columns([2.5, 1])

            with ci:
                st.markdown(f"""
                <div class='dm-card' style='border-left:4px solid {rc};'>
                    <h4 style='color:{rc};'>{data['scientific_name']}</h4>

                    <p><b>🔬 {t('scan_morphology')} :</b><br>
                       {get_parasite_text(data, 'morphology')}</p>

                    <p><b>📖 Description :</b><br>
                       {get_parasite_text(data, 'description')}</p>

                    <p><b>⚠️ {t('scan_risk')} :</b>
                       <span style='color:{rc}; font-weight:700;'>
                           {risk_disp}
                       </span></p>

                    <div style='background:rgba(22,163,74,0.08); padding:14px;
                                border-radius:12px; margin:10px 0;'>
                        <b>💡 {t('scan_advice')} :</b><br>
                        {get_parasite_text(data, 'advice')}
                    </div>

                    <div style='background:rgba(37,99,235,0.06); padding:14px;
                                border-radius:12px; font-style:italic;'>
                        🤖 {get_parasite_text(data, 'funny')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with cv:
                rp = get_risk_percent(data["risk_level"])
                if rp > 0:
                    st.progress(rp / 100, text=f"Dangerosité: {rp}%")
                st.markdown(f"""
                <div style='text-align:center; padding:10px;'>
                    <div style='font-size:4rem;'>{data.get('icon', '🦠')}</div>
                </div>
                """, unsafe_allow_html=True)

    if search.strip():
        found = any(
            search.lower() in (n + d["scientific_name"]).lower()
            for n, d in PARASITE_DB.items() if n != "Negative"
        )
        if not found:
            st.warning(f"🔍 {t('enc_no_result')}")


# ╔══════════════════════════════════════════╗
# ║          PAGE: DASHBOARD                 ║
# ╚══════════════════════════════════════════╝
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

    # KPIs
    kpi_cols = st.columns(4)
    kpi_data = [
        ("🔬", total, t("dash_total"), "#3b82f6"),
        ("✅", fiable, t("dash_reliable"), "#22c55e"),
        ("⚠️", averif, t("dash_check"), "#f59e0b"),
        ("🦠", common, t("dash_frequent"), "#ef4444"),
    ]
    for col, (ic, val, lbl, clr) in zip(kpi_cols, kpi_data):
        with col:
            st.markdown(f"""
            <div class="dm-metric">
                <span class="dm-metric-icon">{ic}</span>
                <div class="dm-metric-val" style="color:{clr} !important;">{val}</div>
                <div class="dm-metric-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # حالة النظام
    sys_cols = st.columns(3)
    with sys_cols[0]:
        st.markdown(f"""
        <div class='dm-card dm-card-green'>
            <h4>🟢 {t('dash_system')}</h4>
            <p style='opacity:0.7;'>All modules OK</p>
        </div>
        """, unsafe_allow_html=True)

    with sys_cols[1]:
        st.markdown(f"""
        <div class='dm-card dm-card-blue'>
            <h4>👤 {t('dash_user')}</h4>
            <p>{st.session_state.user_name}</p>
        </div>
        """, unsafe_allow_html=True)

    with sys_cols[2]:
        st.markdown(f"""
        <div class='dm-card dm-card-purple'>
            <h4>🕐 {t('dash_session')}</h4>
            <p>{datetime.now().strftime('%H:%M — %d/%m/%Y')}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # الرسوم
    if not df.empty and "Parasite" in df.columns:
        # فلتر
        filter_opts = ["Tous / All"] + df["Parasite"].unique().tolist()
        filt = st.selectbox(f"🔍 {t('dash_filter')}", filter_opts)
        filtered = df if filt == "Tous / All" else df[df["Parasite"] == filt]

        chart_c1, chart_c2 = st.columns(2)
        with chart_c1:
            st.markdown(f"#### 📊 {t('dash_distribution')}")
            st.bar_chart(filtered["Parasite"].value_counts(), color="#3b82f6")

        with chart_c2:
            if "Confiance" in filtered.columns:
                st.markdown(f"#### 📈 {t('dash_confidence_chart')}")
                try:
                    conf_vals = filtered["Confiance"].str.rstrip('%').astype(float)
                    st.line_chart(conf_vals.reset_index(drop=True))
                except Exception:
                    st.info("Chart unavailable")

            # رسم بياني بالتاريخ
            if "Date" in filtered.columns:
                try:
                    date_series = pd.to_datetime(filtered["Date"], format="%Y-%m-%d %H:%M")
                    by_date = date_series.dt.date.value_counts().sort_index()
                    if len(by_date) > 1:
                        st.markdown("#### 📅 Analyses par Jour")
                        st.line_chart(by_date)
                except Exception:
                    pass

        st.markdown("---")
        st.markdown(f"### 📋 {t('dash_history')}")
        st.dataframe(filtered, use_container_width=True)

        csv = filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            f"⬇️ {t('dash_export')}",
            data=csv,
            file_name=f"dm_lab_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    else:
        st.markdown(f"""
        <div class='dm-card' style='text-align:center; padding:50px 20px;'>
            <div style='font-size:4.5rem; margin-bottom:12px;'>📊</div>
            <h3>{t('dash_no_data')}</h3>
            <p style='opacity:0.6;'>{t('dash_no_data_desc')}</p>
        </div>
        """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║          PAGE: À PROPOS                  ║
# ╚══════════════════════════════════════════╝
elif current_page == "about":
    st.title(f"ℹ️ {t('about_title')}")

    st.markdown(f"""
    <div class='dm-card dm-card-blue' style='text-align:center;'>
        <h1 style='color:#2563eb; margin:0;'>🧬 DM SMART LAB AI</h1>
        <p style='font-size:1.15rem; margin-top:6px;'>
            <b>Version {APP_VERSION}</b>
        </p>
        <p style='opacity:0.65;'>{t('about_desc')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # وصف المشروع
    st.markdown(f"""
    <div class='dm-card'>
        <h3>📖 {PROJECT_TITLE}</h3>
        <p style='line-height:1.8; opacity:0.85;'>{t('about_project_desc')}</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # الفريق والمؤسسة
    about_c1, about_c2 = st.columns(2)

    with about_c1:
        st.markdown(f"""
        <div class='dm-card dm-card-blue'>
            <h3>👨‍🔬 {t('about_team')}</h3>
            <br>
            <p>
                <b>🧑‍💻 {AUTHORS['dev1']['name']}</b><br>
                <span style='opacity:0.6;'>{AUTHORS['dev1']['role']}</span>
            </p>
            <br>
            <p>
                <b>🔬 {AUTHORS['dev2']['name']}</b><br>
                <span style='opacity:0.6;'>{AUTHORS['dev2']['role']}</span>
            </p>
            <br>
            <p><b>Niveau :</b> 3ème Année</p>
            <p><b>Spécialité :</b> Laboratoire de Santé Publique</p>
        </div>
        """, unsafe_allow_html=True)

    with about_c2:
        st.markdown(f"""
        <div class='dm-card'>
            <h3>🏫 {t('about_institution')}</h3>
            <br>
            <p><b>{INSTITUTION['name']}</b></p>
            <p>📍 {INSTITUTION['city']}, {INSTITUTION['country']} 🇩🇿</p>
            <br>
            <h4>🎯 {t('about_objectives')}</h4>
            <ul>
                <li>{t('about_obj1')}</li>
                <li>{t('about_obj2')}</li>
                <li>{t('about_obj3')}</li>
                <li>{t('about_obj4')}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # التقنيات
    st.markdown(f"### 🛠️ {t('about_tech')}")
    tech_cols = st.columns(6)
    techs = [
        ("🐍", "Python", "Language"),
        ("🧠", "TensorFlow", "Deep Learning"),
        ("🎨", "Streamlit", "Interface"),
        ("📊", "Pandas", "Data"),
        ("🖼️", "Pillow", "Imaging"),
        ("📄", "FPDF", "PDF Reports"),
    ]
    for col, (ic, name, desc) in zip(tech_cols, techs):
        with col:
            st.markdown(f"""
            <div class="dm-metric">
                <span class="dm-metric-icon">{ic}</span>
                <div class="dm-metric-val" style="font-size:1rem;">{name}</div>
                <div class="dm-metric-lbl">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # العلم
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/"
        "7/77/Flag_of_Algeria.svg/1200px-Flag_of_Algeria.svg.png",
        width=80
    )
    st.caption(f"Fait avec ❤️ à {INSTITUTION['city']} — {INSTITUTION['year']}")
