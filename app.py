# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║              DM SMART LAB AI v5.0 - ULTRA FUTURISTIC EDITION               ║
# ║         Diagnostic Parasitologique par Intelligence Artificielle            ║
# ║                                                                            ║
# ║  Développé par:                                                            ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)                   ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                      ║
# ║                                                                            ║
# ║  INFSPM - Ouargla, Algérie                                                ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

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
import math
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from datetime import datetime, timedelta
from fpdf import FPDF

# ============================================
#  1. إعداد الصفحة
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI v5.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
#  2. الثوابت
# ============================================
APP_VERSION = "5.0.0"
APP_PASSWORD = "123"
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)
AUTO_LOCK_MINUTES = 15

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
#  3. أنواع المجاهر والتحضيرات - جديد
# ============================================
MICROSCOPE_TYPES = {
    "fr": {
        "optique": "Microscope Optique (Photonique)",
        "binoculaire": "Microscope Binoculaire",
        "inversé": "Microscope Inversé",
        "fluorescence": "Microscope à Fluorescence",
        "contraste_phase": "Microscope à Contraste de Phase",
        "fond_noir": "Microscope à Fond Noir",
        "numerique": "Microscope Numérique"
    },
    "ar": {
        "optique": "مجهر ضوئي (فوتوني)",
        "binoculaire": "مجهر ثنائي العينية",
        "inversé": "مجهر مقلوب",
        "fluorescence": "مجهر فلوري",
        "contraste_phase": "مجهر تباين الطور",
        "fond_noir": "مجهر الحقل المظلم",
        "numerique": "مجهر رقمي"
    },
    "en": {
        "optique": "Optical (Light) Microscope",
        "binoculaire": "Binocular Microscope",
        "inversé": "Inverted Microscope",
        "fluorescence": "Fluorescence Microscope",
        "contraste_phase": "Phase Contrast Microscope",
        "fond_noir": "Dark Field Microscope",
        "numerique": "Digital Microscope"
    }
}

MAGNIFICATION_OPTIONS = ["x10", "x20", "x40", "x60", "x100 (Immersion)"]

PREPARATION_TYPES = {
    "fr": {
        "etat_frais": "État Frais (Direct)",
        "lugol": "Coloration au Lugol",
        "mif": "MIF (Merthiolate-Iode-Formol)",
        "ritchie": "Concentration de Ritchie",
        "kato_katz": "Technique de Kato-Katz",
        "mgg": "Coloration MGG (May-Grünwald-Giemsa)",
        "giemsa": "Coloration au Giemsa",
        "ziehl": "Ziehl-Neelsen Modifié",
        "trichrome": "Coloration Trichrome",
        "weber": "Coloration de Weber",
        "goutte_epaisse": "Goutte Épaisse",
        "frottis_mince": "Frottis Mince",
        "scotch_test": "Scotch-Test (Graham)",
        "baermann": "Technique de Baermann",
        "knott": "Technique de Knott"
    },
    "ar": {
        "etat_frais": "فحص مباشر (حالة طازجة)",
        "lugol": "تلوين اللوغول",
        "mif": "MIF (ميرثيولات-يود-فورمول)",
        "ritchie": "تقنية ريتشي للتركيز",
        "kato_katz": "تقنية كاتو-كاتز",
        "mgg": "تلوين MGG (ماي-غرونوالد-جيمزا)",
        "giemsa": "تلوين جيمزا",
        "ziehl": "زيل-نيلسن المعدّل",
        "trichrome": "تلوين ثلاثي الألوان",
        "weber": "تلوين ويبر",
        "goutte_epaisse": "قطرة سميكة",
        "frottis_mince": "لطاخة رقيقة",
        "scotch_test": "اختبار سكوتش (غراهام)",
        "baermann": "تقنية بايرمان",
        "knott": "تقنية نوت"
    },
    "en": {
        "etat_frais": "Wet Mount (Direct)",
        "lugol": "Lugol Staining",
        "mif": "MIF (Merthiolate-Iodine-Formol)",
        "ritchie": "Ritchie Concentration",
        "kato_katz": "Kato-Katz Technique",
        "mgg": "MGG Staining (May-Grünwald-Giemsa)",
        "giemsa": "Giemsa Staining",
        "ziehl": "Modified Ziehl-Neelsen",
        "trichrome": "Trichrome Staining",
        "weber": "Weber Staining",
        "goutte_epaisse": "Thick Smear",
        "frottis_mince": "Thin Smear",
        "scotch_test": "Scotch-Test (Graham)",
        "baermann": "Baermann Technique",
        "knott": "Knott Technique"
    }
}

# ============================================
#  4. نظام اللغات الكامل المحسّن
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
        "scan_lab_info": "Informations du Laboratoire",
        "scan_technician1": "Technicien 1",
        "scan_technician2": "Technicien 2",
        "scan_microscope_type": "Type de Microscope",
        "scan_magnification": "Grossissement",
        "scan_preparation": "Type de Préparation",
        "scan_notes": "Notes / Observations",
        "scan_zoom_title": "Zoom & Région d'Intérêt",
        "scan_zoom_level": "Niveau de Zoom",
        "scan_select_region": "Sélectionner la Région",
        "scan_brightness": "Luminosité",
        "scan_contrast_adj": "Contraste",
        "scan_saturation": "Saturation",
        "scan_negative": "Négatif",
        "scan_emboss": "Relief",
        "scan_sharpen": "Netteté",
        "scan_denoise": "Débruitage",
        "scan_histogram": "Histogramme",
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
        "echantillon_peau": "Biopsie Cutanée",
        "echantillon_crachat": "Crachat",
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
        "quiz_category": "Catégorie",
        "chatbot_title": "Dr. DhiaBot - Assistant Médical IA",
        "chatbot_placeholder": "Posez votre question sur les parasites...",
        "chatbot_thinking": "Dr. DhiaBot réfléchit...",
        "daily_tip": "Conseil du Jour",
        "activity_log": "Journal d'Activité",
        "pdf_title": "RAPPORT D'ANALYSE PARASITOLOGIQUE",
        "pdf_subtitle": "Analyse assistée par Intelligence Artificielle",
        "pdf_patient_section": "INFORMATIONS DU PATIENT",
        "pdf_lab_section": "INFORMATIONS DU LABORATOIRE",
        "pdf_result_section": "RESULTAT DE L'ANALYSE IA",
        "pdf_advice_section": "RECOMMANDATIONS CLINIQUES",
        "pdf_validation": "VALIDATION",
        "pdf_technician": "Technicien de Laboratoire",
        "pdf_disclaimer": "Ce rapport est genere par un systeme d'IA et doit etre valide par un professionnel de sante.",
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
        "scan_lab_info": "معلومات المخبر",
        "scan_technician1": "التقني 1",
        "scan_technician2": "التقني 2",
        "scan_microscope_type": "نوع المجهر",
        "scan_magnification": "التكبير",
        "scan_preparation": "نوع التحضير",
        "scan_notes": "ملاحظات",
        "scan_zoom_title": "التكبير ومنطقة الاهتمام",
        "scan_zoom_level": "مستوى التكبير",
        "scan_select_region": "تحديد المنطقة",
        "scan_brightness": "السطوع",
        "scan_contrast_adj": "التباين",
        "scan_saturation": "التشبع",
        "scan_negative": "سلبي",
        "scan_emboss": "نقش بارز",
        "scan_sharpen": "حدّة",
        "scan_denoise": "إزالة الضوضاء",
        "scan_histogram": "المدرج التكراري",
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
        "echantillon_peau": "خزعة جلدية",
        "echantillon_crachat": "بلغم",
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
        "quiz_category": "التصنيف",
        "chatbot_title": "المساعد الطبي الذكي",
        "chatbot_placeholder": "اسأل عن الطفيليات...",
        "chatbot_thinking": "المساعد يفكر...",
        "daily_tip": "نصيحة اليوم",
        "activity_log": "سجل النشاطات",
        "pdf_title": "تقرير التحليل الطفيلي",
        "pdf_subtitle": "تحليل بمساعدة الذكاء الاصطناعي",
        "pdf_patient_section": "بيانات المريض",
        "pdf_lab_section": "معلومات المخبر",
        "pdf_result_section": "نتيجة التحليل",
        "pdf_advice_section": "التوصيات السريرية",
        "pdf_validation": "المصادقة",
        "pdf_technician": "تقني المخبر",
        "pdf_disclaimer": "هذا التقرير مولد بنظام ذكاء اصطناعي.",
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
        "scan_lab_info": "Laboratory Information",
        "scan_technician1": "Technician 1",
        "scan_technician2": "Technician 2",
        "scan_microscope_type": "Microscope Type",
        "scan_magnification": "Magnification",
        "scan_preparation": "Preparation Type",
        "scan_notes": "Notes / Observations",
        "scan_zoom_title": "Zoom & Region of Interest",
        "scan_zoom_level": "Zoom Level",
        "scan_select_region": "Select Region",
        "scan_brightness": "Brightness",
        "scan_contrast_adj": "Contrast",
        "scan_saturation": "Saturation",
        "scan_negative": "Negative",
        "scan_emboss": "Emboss",
        "scan_sharpen": "Sharpen",
        "scan_denoise": "Denoise",
        "scan_histogram": "Histogram",
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
        "echantillon_peau": "Skin Biopsy",
        "echantillon_crachat": "Sputum",
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
        "quiz_category": "Category",
        "chatbot_title": "Dr. DhiaBot - AI Medical Assistant",
        "chatbot_placeholder": "Ask about parasites...",
        "chatbot_thinking": "Dr. DhiaBot is thinking...",
        "daily_tip": "Daily Tip",
        "activity_log": "Activity Log",
        "pdf_title": "PARASITOLOGICAL ANALYSIS REPORT",
        "pdf_subtitle": "AI-Assisted Analysis",
        "pdf_patient_section": "PATIENT INFORMATION",
        "pdf_lab_section": "LABORATORY INFORMATION",
        "pdf_result_section": "AI ANALYSIS RESULT",
        "pdf_advice_section": "CLINICAL RECOMMENDATIONS",
        "pdf_validation": "VALIDATION",
        "pdf_technician": "Lab Technician",
        "pdf_disclaimer": "This report is AI-generated.",
    }
}

# ============================================
#  5. قاعدة بيانات الطفيليات الشاملة والمُحسّنة
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {
            "fr": "Kyste spherique (10-15um) a 4 noyaux, corps chromatoide en cigare. Trophozoite (20-40um) avec pseudopodes digitiformes et hematies phagocytees. Noyau a chromatine peripherique reguliere et caryosome central.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 نوى، جسم كروماتيني على شكل سيجار. طور غاذي (20-40 ميكرومتر) بأقدام كاذبة إصبعية وكريات حمراء مبتلعة. نواة بكروماتين محيطي منتظم وجسيم مركزي.",
            "en": "Spherical cyst (10-15um) with 4 nuclei, cigar-shaped chromatoid body. Trophozoite (20-40um) with digitiform pseudopods and phagocytized RBCs. Nucleus with regular peripheral chromatin and central karyosome."
        },
        "description": {
            "fr": "Protozoaire rhizopode responsable de l'amibiase intestinale (dysenterie amibienne) et extra-intestinale (abces hepatique, pulmonaire, cerebral). Transmission feco-orale par ingestion de kystes. Prevalence elevee en zones tropicales.",
            "ar": "أولي جذري القدم مسبب للأميبيا المعوية (الزحار الأميبي) وخارج المعوية (خراج كبدي، رئوي، دماغي). ينتقل بالطريق البرازي-الفموي عبر ابتلاع الأكياس. انتشار مرتفع في المناطق الاستوائية.",
            "en": "Rhizopod protozoan causing intestinal amebiasis (amoebic dysentery) and extra-intestinal disease (hepatic, pulmonary, cerebral abscess). Feco-oral transmission via cyst ingestion. High prevalence in tropical zones."
        },
        "funny": {
            "fr": "Le ninja des intestins ! Il change de forme plus vite que ton humeur un lundi matin. Et il mange des globules rouges au petit-dejeuner !",
            "ar": "نينجا الأمعاء! يغيّر شكله أسرع من مزاجك صباح الاثنين. ويأكل كريات حمراء على الفطور!",
            "en": "The intestinal ninja! Changes shape faster than your mood on Monday morning. And eats red blood cells for breakfast!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Traitement en deux etapes: 1) Amoebicide tissulaire: Metronidazole (Flagyl) 500mg x3/j pendant 7-10 jours, 2) Amoebicide de contact: Tiliquinol-Tilbroquinol (Intetrix) pour eradiquer les kystes. Hygiene feco-orale stricte. Controle EPS a J15 et J30.",
            "ar": "علاج على مرحلتين: 1) مبيد أميبي نسيجي: ميترونيدازول 500 مغ × 3/يوم لمدة 7-10 أيام، 2) مبيد أميبي تلامسي: تيليكينول-تيلبروكينول (إنتيتريكس) للقضاء على الأكياس. نظافة صارمة. مراقبة بعد 15 و30 يوماً.",
            "en": "Two-step treatment: 1) Tissue amoebicide: Metronidazole 500mg x3/d for 7-10 days, 2) Contact amoebicide: Tiliquinol-Tilbroquinol (Intetrix) to eradicate cysts. Strict feco-oral hygiene. Follow-up at D15 and D30."
        },
        "extra_tests": {
            "fr": ["Serologie amibienne (IgG/IgM)", "Echographie hepatique", "NFS + CRP + VS", "Coproculture", "PCR Entamoeba", "Scanner abdominal si abces suspecte"],
            "ar": ["مصلية أميبية (IgG/IgM)", "إيكو كبدي", "تعداد دم + CRP + سرعة ترسب", "زرع براز", "PCR أنتاميبا", "سكانر بطني إذا اشتبه بخراج"],
            "en": ["Amoebic serology (IgG/IgM)", "Hepatic ultrasound", "CBC + CRP + ESR", "Stool culture", "Entamoeba PCR", "Abdominal CT if abscess suspected"]
        },
        "color": "#dc2626",
        "icon": "🔴",
        "lifecycle": {
            "fr": "Kyste mature ingere (eau/aliments contamines) → Excystation dans l'intestin grele → 8 Trophozoites → Colonisation du colon → Invasion muqueuse (ulceres en bouton de chemise) → Dissemination hematogene possible (foie) → Enkystement → Emission des kystes dans les selles",
            "ar": "ابتلاع كيس ناضج (ماء/طعام ملوث) ← خروج من الكيس في الأمعاء الدقيقة ← 8 أطوار غاذية ← استعمار القولون ← غزو الغشاء المخاطي (تقرحات زر القميص) ← انتشار دموي محتمل (الكبد) ← تكيس ← طرح الأكياس في البراز",
            "en": "Mature cyst ingested (contaminated water/food) → Excystation in small intestine → 8 Trophozoites → Colon colonization → Mucosal invasion (flask-shaped ulcers) → Possible hematogenous spread (liver) → Encystation → Cyst passage in stool"
        },
        "diagnostic_keys": {
            "fr": "- E. histolytica vs E. dispar: seule E. histolytica phagocyte les hematies\n- Kyste a 4 noyaux (vs E. coli a 8 noyaux)\n- Corps chromatoides en cigare (vs pointus chez E. coli)\n- Trophozoite: 20-40um avec mobilite directionnelle",
            "ar": "- تمييز عن E. dispar: فقط E. histolytica تبتلع الكريات\n- كيس بـ 4 نوى (مقابل 8 عند E. coli)\n- أجسام كروماتينية سيجارية\n- طور غاذي: 20-40 ميكرومتر بحركة اتجاهية",
            "en": "- E. histolytica vs E. dispar: only E. histolytica phagocytizes RBCs\n- 4-nuclei cyst (vs 8 in E. coli)\n- Cigar-shaped chromatoid bodies (vs pointed in E. coli)\n- Trophozoite: 20-40um with directional motility"
        }
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia (intestinalis / duodenalis)",
        "morphology": {
            "fr": "Trophozoite piriforme en 'cerf-volant' (12-15um x 7-10um) avec 2 noyaux symetriques (face de hibou), disque adhesif ventral, axostyle median et 4 paires de flagelles. Kyste ovoide (8-12um) a 4 noyaux avec flagelles internes visibles.",
            "ar": "طور غاذي كمثري على شكل 'طائرة ورقية' (12-15 × 7-10 ميكرومتر) بنواتين متناظرتين (وجه بومة)، قرص لاصق بطني، محور مركزي و4 أزواج أسواط. كيس بيضاوي (8-12 ميكرومتر) بـ 4 نوى وأسواط داخلية مرئية.",
            "en": "Pear-shaped 'kite' trophozoite (12-15 x 7-10um) with 2 symmetric nuclei (owl face), ventral adhesive disc, median axostyle and 4 flagella pairs. Ovoid cyst (8-12um) with 4 nuclei and visible internal flagella."
        },
        "description": {
            "fr": "Protozoaire flagelle cosmopolite colonisant le duodenum et le jejunum proximal. Responsable de la giardiose: diarrhee chronique graisseuse, malabsorption, retard de croissance chez l'enfant. Transmission hydrique ++ (kystes tres resistants dans l'eau).",
            "ar": "أولي سوطي عالمي الانتشار يستعمر الاثني عشر والصائم. مسبب لداء الجيارديا: إسهال دهني مزمن، سوء امتصاص، تأخر نمو عند الأطفال. انتقال مائي (أكياس مقاومة جداً في الماء).",
            "en": "Cosmopolitan flagellated protozoan colonizing duodenum and proximal jejunum. Causes giardiasis: chronic fatty diarrhea, malabsorption, growth retardation in children. Waterborne transmission (cysts very resistant in water)."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil a double verre ! Un vrai touriste de l'intestin qui refuse de partir meme apres les vacances !",
            "ar": "يحدّق فيك بنظارته ذات العدستين! سائح حقيقي في الأمعاء يرفض المغادرة حتى بعد العطلة!",
            "en": "Staring at you with double-lens sunglasses! A real intestinal tourist who refuses to leave even after vacation!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Metronidazole 250mg x3/j pendant 5 jours OU Tinidazole 2g en dose unique. Alternative: Albendazole 400mg/j x 5j. Verifier la source d'eau potable. Traitement de la famille si cas groupes. Controle EPS a J15.",
            "ar": "ميترونيدازول 250 مغ × 3/يوم لـ 5 أيام أو تينيدازول 2غ جرعة واحدة. بديل: ألبندازول 400 مغ/يوم × 5 أيام. تحقق من مصدر المياه. علاج العائلة إذا وُجدت حالات. مراقبة بعد 15 يوماً.",
            "en": "Metronidazole 250mg x3/d for 5 days OR Tinidazole 2g single dose. Alternative: Albendazole 400mg/d x 5d. Check water source. Family treatment if cluster cases. Follow-up at D15."
        },
        "extra_tests": {
            "fr": ["Recherche d'antigene Giardia (selles - ELISA)", "Test de malabsorption (D-xylose)", "Dosage IgA secretoires", "EPS x3 a intervals", "PCR Giardia si negatif persistant"],
            "ar": ["بحث عن مستضد الجيارديا (براز - ELISA)", "اختبار سوء امتصاص (D-xylose)", "قياس IgA إفرازي", "فحص براز × 3 على فترات", "PCR جيارديا إذا استمر السلبي"],
            "en": ["Giardia antigen test (stool - ELISA)", "Malabsorption test (D-xylose)", "Secretory IgA levels", "Stool exam x3 at intervals", "Giardia PCR if persistent negative"]
        },
        "color": "#f59e0b",
        "icon": "🟠",
        "lifecycle": {
            "fr": "Kyste ingere (eau contaminee) → Excystation dans le duodenum (pH acide + bile) → 2 Trophozoites → Fixation par disque adhesif sur la muqueuse duodenale → Multiplication par scissiparite → Enkystement dans le colon → Emission des kystes (forme infestante)",
            "ar": "ابتلاع الكيس (ماء ملوث) ← خروج في الاثني عشر (حموضة + صفراء) ← طوران غاذيان ← التصاق بالقرص اللاصق على غشاء الاثني عشر ← تكاثر بالانشطار ← تكيس في القولون ← طرح الأكياس (الشكل المعدي)",
            "en": "Cyst ingested (contaminated water) → Excystation in duodenum (acid pH + bile) → 2 Trophozoites → Adhesive disc attachment to duodenal mucosa → Binary fission multiplication → Encystation in colon → Cyst passage (infective form)"
        },
        "diagnostic_keys": {
            "fr": "- Forme en cerf-volant pathognomonique\n- 2 noyaux = face de hibou\n- Disque adhesif ventral visible au Lugol\n- Kyste ovoide a 4 noyaux\n- Mobilite 'feuille morte' caracteristique",
            "ar": "- شكل الطائرة الورقية مميز\n- نواتان = وجه البومة\n- قرص لاصق بطني يظهر باللوغول\n- كيس بيضاوي بـ 4 نوى\n- حركة 'الورقة الساقطة' المميزة",
            "en": "- Pathognomonic kite shape\n- 2 nuclei = owl face\n- Ventral adhesive disc visible with Lugol\n- Ovoid 4-nuclei cyst\n- Characteristic 'falling leaf' motility"
        }
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / tropica / major",
        "morphology": {
            "fr": "Amastigotes ovoides (2-5um) intracellulaires dans les macrophages. Noyau excentre + kinetoplaste en battonnet (coloration MGG). Promastigotes fusiformes (15-25um) avec flagelle anterieur en culture.",
            "ar": "لامسوطات بيضاوية (2-5 ميكرومتر) داخل البلاعم. نواة جانبية + حركي عصوي (تلوين MGG). سوطيات مغزلية (15-25 ميكرومتر) بسوط أمامي في الزرع.",
            "en": "Ovoid amastigotes (2-5um) intracellular in macrophages. Eccentric nucleus + rod-shaped kinetoplast (MGG staining). Fusiform promastigotes (15-25um) with anterior flagellum in culture."
        },
        "description": {
            "fr": "Protozoaire transmis par le phlebotome (Phlebotomus/Lutzomyia). Trois formes cliniques: cutanee (bouton d'Orient - L. major/tropica), viscerale (Kala-azar - L. infantum/donovani), muco-cutanee (L. braziliensis). En Algerie: L. infantum (nord) et L. major (sud).",
            "ar": "أولي ينتقل بذبابة الرمل (فليبوتوم). ثلاثة أشكال سريرية: جلدي (حبة الشرق - L. major/tropica)، حشوي (كالا آزار - L. infantum/donovani)، مخاطي جلدي (L. braziliensis). في الجزائر: L. infantum (شمال) وL. major (جنوب).",
            "en": "Protozoan transmitted by sandfly (Phlebotomus/Lutzomyia). Three clinical forms: cutaneous (Oriental sore - L. major/tropica), visceral (Kala-azar - L. infantum/donovani), mucocutaneous (L. braziliensis). In Algeria: L. infantum (north) and L. major (south)."
        },
        "funny": {
            "fr": "Petit mais costaud ! Il squatte les macrophages comme un locataire qui ne paie jamais son loyer. Et en plus, il arrive par taxi-phlebotome !",
            "ar": "صغير لكن قوي! يسكن البلاعم كمستأجر لا يدفع الإيجار أبداً. وفوق ذلك يأتي بتاكسي ذبابة الرمل!",
            "en": "Small but mighty! Squats in macrophages like a tenant who never pays rent. And arrives by sandfly-taxi!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Cutanee: Glucantime IM (20mg/kg/j x 20j) ou cryotherapie locale. Viscerale: Amphotericine B liposomale (AmBisome) ou Glucantime. Maladie a Declaration Obligatoire en Algerie. Surveillance NFS + bilan renal/hepatique sous traitement.",
            "ar": "جلدي: غلوكانتيم عضلياً (20مغ/كغ/يوم × 20 يوم) أو علاج بالتبريد موضعي. حشوي: أمفوتيريسين ب ليبوزومي (أمبيزوم) أو غلوكانتيم. مرض ذو تصريح إجباري في الجزائر. مراقبة تعداد الدم + وظائف الكلى والكبد.",
            "en": "Cutaneous: Glucantime IM (20mg/kg/d x 20d) or local cryotherapy. Visceral: Liposomal Amphotericin B (AmBisome) or Glucantime. Mandatory reporting in Algeria. Monitor CBC + renal/hepatic function during treatment."
        },
        "extra_tests": {
            "fr": ["IDR de Montenegro (hypersensibilite retardee)", "Serologie Leishmania (IFI, ELISA, Western Blot)", "Ponction de moelle osseuse (Leishmania viscerale)", "Biopsie cutanee + coloration MGG", "PCR Leishmania (reference)", "NFS (pancytopenie si viscerale)", "Electrophorese des proteines"],
            "ar": ["اختبار مونتينيغرو (فرط حساسية متأخر)", "مصلية ليشمانيا (IFI, ELISA, Western Blot)", "بزل نخاع العظم (ليشمانيا حشوية)", "خزعة جلدية + تلوين MGG", "PCR ليشمانيا (مرجعي)", "تعداد دم (قلة كريات شاملة إذا حشوية)", "رحلان كهربائي للبروتينات"],
            "en": ["Montenegro skin test (delayed hypersensitivity)", "Leishmania serology (IFI, ELISA, Western Blot)", "Bone marrow aspirate (visceral)", "Skin biopsy + MGG staining", "Leishmania PCR (reference)", "CBC (pancytopenia if visceral)", "Protein electrophoresis"]
        },
        "color": "#dc2626",
        "icon": "🔴",
        "lifecycle": {
            "fr": "Piqure du phlebotome femelle → Inoculation de promastigotes metacycliques → Phagocytose par macrophages → Transformation en amastigotes intracellulaires → Multiplication par scissiparite → Lyse du macrophage → Reinvasion → Le phlebotome s'infecte en piquant",
            "ar": "لدغة ذبابة الرمل الأنثى ← حقن سوطيات بعدية ← بلعمة بالبلاعم ← تحول إلى لامسوطات داخل خلوية ← تكاثر بالانشطار ← تحلل البلعم ← إعادة غزو ← ذبابة الرمل تُصاب عند اللدغ",
            "en": "Female sandfly bite → Metacyclic promastigote inoculation → Macrophage phagocytosis → Intracellular amastigote transformation → Binary fission → Macrophage lysis → Reinvasion → Sandfly infected when biting"
        },
        "diagnostic_keys": {
            "fr": "- Amastigotes: 2-5um, intracellulaires (macrophages)\n- Noyau + kinetoplaste visible au MGG\n- Culture sur milieu NNN: promastigotes en 5-15 jours\n- PCR: gold standard pour identification d'espece",
            "ar": "- لامسوطات: 2-5 ميكرومتر داخل البلاعم\n- نواة + حركي مرئي بـ MGG\n- زرع على وسط NNN: سوطيات في 5-15 يوم\n- PCR: المعيار الذهبي لتحديد النوع",
            "en": "- Amastigotes: 2-5um, intracellular (macrophages)\n- Nucleus + kinetoplast visible on MGG\n- NNN culture: promastigotes in 5-15 days\n- PCR: gold standard for species identification"
        }
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax / ovale / malariae / knowlesi",
        "morphology": {
            "fr": "P. falciparum: anneau fin en 'bague a chaton' (1-2um), gametocytes en banane. P. vivax: trophozoite amiboide, hematies agrandies avec granulations de Schuffner. P. malariae: trophozoite en bande equatoriale. Schizontes: rosace a merozoites.",
            "ar": "P. falciparum: حلقة رفيعة 'خاتم' (1-2 ميكرومتر)، عرسات موزية. P. vivax: طور غاذي أميبي، كريات متضخمة بحبيبات شوفنر. P. malariae: طور غاذي شريطي استوائي. منسقات: وردة بجزيئيات.",
            "en": "P. falciparum: thin 'signet ring' (1-2um), banana-shaped gametocytes. P. vivax: amoeboid trophozoite, enlarged RBCs with Schuffner dots. P. malariae: band-form trophozoite. Schizonts: rosette with merozoites."
        },
        "description": {
            "fr": "URGENCE MEDICALE ABSOLUE ! Agent du paludisme (malaria). 5 especes humaines. P. falciparum: le plus mortel (acces pernicieux, neuropaludisme). Transmission par l'anophele femelle. 229 millions de cas/an dans le monde (OMS 2019). En Algerie: paludisme d'importation ++.",
            "ar": "حالة طوارئ طبية مطلقة! مسبب الملاريا. 5 أنواع بشرية. المتصورة المنجلية: الأكثر فتكاً (ملاريا دماغية). ينتقل بأنثى الأنوفيل. 229 مليون حالة/سنة عالمياً (منظمة الصحة 2019). في الجزائر: ملاريا مستوردة بشكل رئيسي.",
            "en": "ABSOLUTE MEDICAL EMERGENCY! Malaria agent. 5 human species. P. falciparum: most lethal (cerebral malaria). Transmitted by female Anopheles. 229 million cases/year worldwide (WHO 2019). In Algeria: mainly imported malaria."
        },
        "funny": {
            "fr": "Il demande le mariage a tes globules rouges ! Ne dis pas oui ! Et ses gametocytes en banane... c'est le clown du microscope !",
            "ar": "يطلب الزواج من كرياتك الحمراء! لا تقل نعم! وعرساته الموزية... مهرج المجهر!",
            "en": "Proposes to your RBCs! Don't say yes! And its banana gametocytes... the microscope's clown!"
        },
        "risk_level": "critical",
        "risk_display": {"fr": "🚨 URGENCE MÉDICALE", "ar": "🚨 حالة طوارئ", "en": "🚨 EMERGENCY"},
        "advice": {
            "fr": "HOSPITALISATION IMMEDIATE si P. falciparum ! ACT (Artemisinine + Lumefrantine/Amodiaquine). Quinine IV si forme grave. Parasitemie de controle /4-6h. Surveillance: glycemie, creatinine, bilirubine, lactates. Transfusion si anemie severe. Declaration obligatoire.",
            "ar": "تنويم فوري إذا P. falciparum! علاج مركب بالأرتيميسينين (ACT). كينين وريدي إذا شكل خطير. فحص طفيليات كل 4-6 ساعات. مراقبة: سكر، كرياتينين، بيليروبين، لاكتات. نقل دم إذا فقر دم شديد. تصريح إجباري.",
            "en": "IMMEDIATE HOSPITALIZATION if P. falciparum! ACT (Artemisinin + Lumefantrine/Amodiaquine). IV Quinine if severe. Parasitemia check /4-6h. Monitor: glucose, creatinine, bilirubin, lactate. Transfusion if severe anemia. Mandatory reporting."
        },
        "extra_tests": {
            "fr": ["TDR Paludisme (HRP2/pLDH)", "Frottis mince + Goutte epaisse (URGENCE)", "Parasitemie quantitative (%)", "NFS complete (anemie, thrombopenie)", "Bilan hepato-renal complet", "Glycemie (hypoglycemie frequente)", "Lactates + Gaz du sang", "Bilirubine totale/conjuguee", "Haptoglobine (hemolyse)", "Groupe sanguin (si transfusion)"],
            "ar": ["اختبار سريع (HRP2/pLDH)", "لطاخة رقيقة + قطرة سميكة (عاجل)", "طفيليات كمية (%)", "تعداد دم كامل (فقر دم، قلة صفيحات)", "وظائف كبد وكلى كاملة", "سكر الدم (نقص سكر شائع)", "لاكتات + غازات الدم", "بيليروبين كلي/مباشر", "هابتوغلوبين (انحلال)", "زمرة دموية (إذا نقل دم)"],
            "en": ["Malaria RDT (HRP2/pLDH)", "Thin smear + Thick smear (URGENT)", "Quantitative parasitemia (%)", "Complete CBC (anemia, thrombocytopenia)", "Full hepato-renal panel", "Blood glucose (frequent hypoglycemia)", "Lactate + Blood gases", "Total/conjugated bilirubin", "Haptoglobin (hemolysis)", "Blood type (if transfusion)"]
        },
        "color": "#7f1d1d",
        "icon": "🚨",
        "lifecycle": {
            "fr": "Piqure anophele femelle → Sporozoites → Hepatocytes (cycle exo-erythrocytaire, 7-15j) → Merozoites → Invasion des hematies (cycle erythrocytaire: 48h P.f/v, 72h P.m) → Schizontes → Eclatement → Reinvasion + Gametocytes → Ingestion par anophele → Cycle sexue (oocinete → oocyste → sporozoites)",
            "ar": "لدغة أنثى الأنوفيل ← بوغيات ← خلايا كبد (دورة خارج كرياتية 7-15 يوم) ← جزيئيات ← غزو الكريات الحمراء (دورة كرياتية: 48 ساعة P.f/v، 72 ساعة P.m) ← منسقات ← انفجار ← إعادة غزو + عرسات ← ابتلاع بالأنوفيل ← دورة جنسية",
            "en": "Female Anopheles bite → Sporozoites → Hepatocytes (exo-erythrocytic cycle, 7-15d) → Merozoites → RBC invasion (erythrocytic cycle: 48h P.f/v, 72h P.m) → Schizonts → Burst → Reinvasion + Gametocytes → Anopheles ingestion → Sexual cycle (ookinete → oocyst → sporozoites)"
        },
        "diagnostic_keys": {
            "fr": "- URGENCE: resultat en <2h\n- Frottis: identification d'espece\n- Goutte epaisse: 10x plus sensible\n- P. falciparum: polyparasitisme, formes en banane\n- Seuil: >2% parasitemie = forme grave\n- TDR: depistage rapide mais confirmer au microscope",
            "ar": "- عاجل: نتيجة في أقل من ساعتين\n- لطاخة: تحديد النوع\n- قطرة سميكة: أكثر حساسية 10 مرات\n- P. falciparum: تطفل متعدد، أشكال موزية\n- حد: >2% طفيليات = شكل خطير\n- TDR: فحص سريع لكن تأكيد بالمجهر",
            "en": "- URGENT: result in <2h\n- Smear: species identification\n- Thick smear: 10x more sensitive\n- P. falciparum: polyparasitism, banana forms\n- Threshold: >2% parasitemia = severe\n- RDT: rapid screening but confirm by microscopy"
        }
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "morphology": {
            "fr": "Forme en 'S' ou 'C' (15-30um x 1.5-3um) avec flagelle libre, membrane ondulante bien visible et kinetoplaste posterieur. Noyau central. Coloration MGG/Giemsa. Polymorphisme: formes trapues et formes greles.",
            "ar": "شكل S أو C (15-30 × 1.5-3 ميكرومتر) بسوط حر، غشاء متموج واضح وحركي خلفي. نواة مركزية. تلوين MGG/جيمزا. تعدد أشكال: أشكال ممتلئة ونحيلة.",
            "en": "S or C shape (15-30 x 1.5-3um) with free flagellum, prominent undulating membrane and posterior kinetoplast. Central nucleus. MGG/Giemsa staining. Polymorphism: stumpy and slender forms."
        },
        "description": {
            "fr": "T. brucei gambiense/rhodesiense: Trypanosomiase Humaine Africaine (maladie du sommeil), transmise par la mouche tse-tse (Glossina). T. cruzi: maladie de Chagas (Amerique latine), transmise par les triatomes (reduves). Phase lymphatico-sanguine puis neuro-meningee.",
            "ar": "T. brucei gambiense/rhodesiense: داء المثقبيات الأفريقي (مرض النوم)، ينتقل بذبابة تسي تسي (Glossina). T. cruzi: مرض شاغاس (أمريكا اللاتينية)، ينتقل بالبق القاتل (الترياتوم). مرحلة لمفية-دموية ثم عصبية-سحائية.",
            "en": "T. brucei gambiense/rhodesiense: Human African Trypanosomiasis (sleeping sickness), transmitted by tsetse fly (Glossina). T. cruzi: Chagas disease (Latin America), transmitted by triatomine bugs. Lymphatic-blood phase then neuro-meningeal phase."
        },
        "funny": {
            "fr": "Il court comme Mahrez sur l'aile droite avec sa membrane ondulante ! Et sa mouche tse-tse, c'est le pire chauffeur de taxi d'Afrique !",
            "ar": "يجري مثل محرز على الجناح بغشائه المتموج! وذبابة تسي تسي أسوأ سائق تاكسي في أفريقيا!",
            "en": "Runs like Mahrez on the right wing with its undulating membrane! And the tsetse fly is Africa's worst taxi driver!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Phase 1 (hemolymphatique): Pentamidine (gambiense) / Suramine (rhodesiense). Phase 2 (neurologique): NECT (Eflornithine+Nifurtimox) pour gambiense / Melarsoprol pour rhodesiense. Chagas: Benznidazole/Nifurtimox. Ponction lombaire OBLIGATOIRE pour le staging.",
            "ar": "المرحلة 1 (دموية لمفية): بنتاميدين (gambiense) / سورامين (rhodesiense). المرحلة 2 (عصبية): NECT (إيفلورنيثين+نيفورتيموكس) لـ gambiense / ميلارسوبرول لـ rhodesiense. شاغاس: بنزنيدازول/نيفورتيموكس. بزل قطني إلزامي للتصنيف.",
            "en": "Phase 1 (hemolymphatic): Pentamidine (gambiense) / Suramin (rhodesiense). Phase 2 (neurological): NECT (Eflornithine+Nifurtimox) for gambiense / Melarsoprol for rhodesiense. Chagas: Benznidazole/Nifurtimox. Lumbar puncture MANDATORY for staging."
        },
        "extra_tests": {
            "fr": ["Ponction lombaire (cellularite >5/mm3 = phase 2)", "Serologie Trypanosoma (CATT pour gambiense)", "IgM serique (tres elevee)", "Recherche dans le suc ganglionnaire", "NFS (anemie, VS elevee)", "Proteinorachie du LCR", "Xenodiagnostic (Chagas)"],
            "ar": ["بزل قطني (خلايا >5/مم3 = مرحلة 2)", "مصلية التريبانوسوما (CATT لـ gambiense)", "IgM مصلي (مرتفع جداً)", "بحث في عصارة العقدة", "تعداد دم (فقر دم، سرعة ترسب مرتفعة)", "بروتين السائل الشوكي", "تشخيص حيوي (شاغاس)"],
            "en": ["Lumbar puncture (cells >5/mm3 = phase 2)", "Trypanosoma serology (CATT for gambiense)", "Serum IgM (very elevated)", "Lymph node aspirate search", "CBC (anemia, elevated ESR)", "CSF protein", "Xenodiagnosis (Chagas)"]
        },
        "color": "#dc2626",
        "icon": "🔴",
        "lifecycle": {
            "fr": "Piqure mouche tse-tse → Trypomastigotes metacycliques → Sang/lymphe → Multiplication (formes sanguines) → Phase 1 hemolymphatique → Franchissement BHE → Phase 2 neurologique → La mouche s'infecte en piquant → Cycle dans la glossine (epimastigotes → trypomastigotes metacycliques)",
            "ar": "لدغة ذبابة تسي تسي ← طور سوطي بعدي ← دم/لمف ← تكاثر (أشكال دموية) ← مرحلة 1 دموية لمفية ← عبور الحاجز الدموي الدماغي ← مرحلة 2 عصبية ← الذبابة تُصاب بالعض ← دورة في الذبابة",
            "en": "Tsetse fly bite → Metacyclic trypomastigotes → Blood/lymph → Multiplication (blood forms) → Phase 1 hemolymphatic → BBB crossing → Phase 2 neurological → Fly infected when biting → Cycle in glossina (epimastigotes → metacyclic trypomastigotes)"
        },
        "diagnostic_keys": {
            "fr": "- Forme en S/C avec membrane ondulante\n- Kinetoplaste posterieur bien visible\n- Recherche dans sang, LCR, suc ganglionnaire\n- IgM serique tres elevee (orientation)\n- Staging par ponction lombaire obligatoire\n- Polymorphisme: formes trapues et greles",
            "ar": "- شكل S/C بغشاء متموج\n- حركي خلفي واضح\n- بحث في الدم، السائل الشوكي، عصارة العقدة\n- IgM مصلي مرتفع جداً\n- تصنيف ببزل قطني إلزامي",
            "en": "- S/C shape with undulating membrane\n- Posterior kinetoplast visible\n- Search in blood, CSF, lymph aspirate\n- Very elevated serum IgM\n- Mandatory LP for staging"
        }
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni / japonicum",
        "morphology": {
            "fr": "Oeuf ovoide (115-170um) avec eperon terminal (S. haematobium) ou lateral (S. mansoni). Miracidium mobile a l'interieur. Vers adultes (1-2cm): males dans le canal gynecophore, femelles plus longues. Cercaires bifurquees dans l'eau.",
            "ar": "بيضة بيضاوية (115-170 ميكرومتر) بنتوء طرفي (S. haematobium) أو جانبي (S. mansoni). ميراسيديوم متحرك بالداخل. ديدان بالغة (1-2 سم): ذكور في القناة النسائية الحاملة، إناث أطول. سركاريا متشعبة في الماء.",
            "en": "Ovoid egg (115-170um) with terminal spine (S. haematobium) or lateral spine (S. mansoni). Motile miracidium inside. Adult worms (1-2cm): males in gynecophoral canal, females longer. Bifurcated cercariae in water."
        },
        "description": {
            "fr": "Trematode responsable de la bilharziose (schistosomiase). S. haematobium: bilharziose uro-genitale (hematurie). S. mansoni: bilharziose hepato-intestinale. S. japonicum: forme hepato-splenique severe. 2eme endemie parasitaire mondiale apres le paludisme.",
            "ar": "ديدان مثقوبة مسببة للبلهارسيا (داء المنشقات). S. haematobium: بلهارسيا بولية تناسلية (دم في البول). S. mansoni: بلهارسيا كبدية معوية. S. japonicum: شكل كبدي طحالي شديد. ثاني وباء طفيلي عالمياً بعد الملاريا.",
            "en": "Trematode causing bilharziasis (schistosomiasis). S. haematobium: urogenital (hematuria). S. mansoni: hepato-intestinal. S. japonicum: severe hepato-splenic form. 2nd parasitic endemic worldwide after malaria."
        },
        "funny": {
            "fr": "L'oeuf avec un dard ! La baignade dans les marigots peut couter cher. Et les cercaires, c'est comme des micro-torpilles qui visent ta peau !",
            "ar": "البيضة ذات الشوكة! السباحة في المستنقعات مكلفة. والسركاريا كطوربيدات صغيرة تستهدف جلدك!",
            "en": "The egg with a sting! Swimming in ponds can be costly. And cercariae are like micro-torpedoes targeting your skin!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Praziquantel 40mg/kg en dose unique (ou 2 prises). S. haematobium: ECBU avec sediment urinaire de midi. S. mansoni: EPS + concentration. Prevention: eviter contact eau douce en zone d'endemie. Controle a 3 mois.",
            "ar": "برازيكوانتيل 40 مغ/كغ جرعة واحدة (أو جرعتين). S. haematobium: فحص بول مع رواسب الظهيرة. S. mansoni: فحص براز + تركيز. وقاية: تجنب المياه العذبة في المناطق الموبوءة. مراقبة بعد 3 أشهر.",
            "en": "Praziquantel 40mg/kg single dose (or 2 doses). S. haematobium: urine with midday sediment. S. mansoni: stool exam + concentration. Prevention: avoid freshwater in endemic areas. Follow-up at 3 months."
        },
        "extra_tests": {
            "fr": ["ECBU + sediment urinaire (midi)", "Serologie Schistosoma", "Echographie vesicale/hepatique", "NFS + Eosinophilie", "Biopsie rectale (granulomes)", "Cystoscopie si hematurie chronique"],
            "ar": ["فحص بول + رواسب (الظهيرة)", "مصلية البلهارسيا", "إيكو مثانة/كبد", "تعداد دم + حمضات", "خزعة مستقيمية (ورم حبيبي)", "تنظير مثانة إذا دم مزمن"],
            "en": ["Urinalysis + sediment (midday)", "Schistosoma serology", "Bladder/hepatic ultrasound", "CBC + Eosinophilia", "Rectal biopsy (granulomas)", "Cystoscopy if chronic hematuria"]
        },
        "color": "#f59e0b",
        "icon": "🟠",
        "lifecycle": {
            "fr": "Oeuf → Miracidium (eau) → Penetration mollusque (Bulinus/Biomphalaria) → Sporocyste → Cercaire bifurquee → Penetration cutanee (baignade) → Schistosomule → Migration portale → Vers adultes (accouplement) → Ponte des oeufs → Migration vers vessie/intestin → Emission",
            "ar": "بيضة ← ميراسيديوم (ماء) ← اختراق حلزون (بولينوس/بيومفالاريا) ← كيسة بوغية ← سركاريا متشعبة ← اختراق جلدي (سباحة) ← شستوسومولا ← هجرة بابية ← ديدان بالغة (تزاوج) ← وضع البيض ← هجرة نحو المثانة/الأمعاء ← إخراج",
            "en": "Egg → Miracidium (water) → Snail penetration (Bulinus/Biomphalaria) → Sporocyst → Bifurcated cercaria → Skin penetration (swimming) → Schistosomula → Portal migration → Adult worms (mating) → Egg laying → Migration to bladder/intestine → Release"
        },
        "diagnostic_keys": {
            "fr": "- S. haematobium: eperon TERMINAL, urines de MIDI\n- S. mansoni: eperon LATERAL, selles\n- Miracidium vivant a l'interieur de l'oeuf\n- Eosinophilie elevee (orientation)\n- Biopsie rectale: granulomes bilharziens",
            "ar": "- S. haematobium: نتوء طرفي، بول الظهيرة\n- S. mansoni: نتوء جانبي، براز\n- ميراسيديوم حي داخل البيضة\n- حمضات مرتفعة\n- خزعة مستقيم: ورم حبيبي بلهارسي",
            "en": "- S. haematobium: TERMINAL spine, MIDDAY urine\n- S. mansoni: LATERAL spine, stool\n- Living miracidium inside egg\n- Elevated eosinophilia\n- Rectal biopsy: bilharzial granulomas"
        }
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": {
            "fr": "Absence d'elements parasitaires (oeufs, kystes, trophozoites, larves) apres examen direct et apres concentration. Flore bacterienne normale. Residus alimentaires eventuels. Cristaux de Charcot-Leyden absents.",
            "ar": "غياب عناصر طفيلية (بيض، أكياس، أطوار غاذية، يرقات) بعد الفحص المباشر وبعد التركيز. نبيت جرثومي طبيعي. بقايا غذائية محتملة. بلورات شاركو-لايدن غائبة.",
            "en": "Absence of parasitic elements (eggs, cysts, trophozoites, larvae) after direct exam and concentration. Normal bacterial flora. Possible food residues. Charcot-Leyden crystals absent."
        },
        "description": {
            "fr": "Echantillon negatif apres examen parasitologique complet. Un seul examen negatif n'exclut pas une parasitose (sensibilite 50-60%). Recommander 3 EPS a quelques jours d'intervalle.",
            "ar": "عينة سلبية بعد الفحص الطفيلي الكامل. فحص سلبي واحد لا يستبعد الإصابة (حساسية 50-60%). يُنصح بـ 3 فحوصات على فترات.",
            "en": "Negative sample after complete parasitological exam. A single negative exam does not exclude parasitosis (sensitivity 50-60%). Recommend 3 exams at intervals."
        },
        "funny": {
            "fr": "Rien a signaler ! Champagne ! Mais ne baisse pas ta garde... les parasites sont des maitres du cache-cache ! 🥂",
            "ar": "لا شيء! شمبانيا! لكن لا تخفض حذرك... الطفيليات أساتذة الاختباء! 🥂",
            "en": "All clear! Champagne! But don't let your guard down... parasites are hide-and-seek masters! 🥂"
        },
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {
            "fr": "RAS pour le moment. Repeter l'examen x3 si suspicion clinique persiste. Maintenir une bonne hygiene alimentaire et hydrique. Eviter les eaux non traitees.",
            "ar": "لا شيء حالياً. كرر الفحص × 3 إذا استمر الاشتباه السريري. حافظ على نظافة غذائية ومائية جيدة.",
            "en": "All clear for now. Repeat x3 if clinical suspicion persists. Maintain good food and water hygiene."
        },
        "extra_tests": {
            "fr": ["Repeter EPS x3 si clinique evocatrice", "Serologie parasitaire ciblee si besoin", "NFS (eosinophilie?)"],
            "ar": ["كرر فحص البراز × 3 إذا كانت السريريات موحية", "مصلية طفيلية موجهة إذا لزم", "تعداد دم (حمضات؟)"],
            "en": ["Repeat stool exam x3 if suggestive symptoms", "Targeted parasitic serology if needed", "CBC (eosinophilia?)"]
        },
        "color": "#16a34a",
        "icon": "🟢",
        "lifecycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "diagnostic_keys": {
            "fr": "- Examen direct + Lugol negatif\n- Concentration (Ritchie/flottation) negative\n- Repeter x3 si doute clinique",
            "ar": "- فحص مباشر + لوغول سلبي\n- تركيز (ريتشي/تطفيل) سلبي\n- كرر × 3 إذا شك سريري",
            "en": "- Direct exam + Lugol negative\n- Concentration (Ritchie/flotation) negative\n- Repeat x3 if clinical doubt"
        }
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())

# ============================================
#  6. قاعدة أسئلة الاختبار - محسّنة ومنوّعة جداً
# ============================================
QUIZ_QUESTIONS = {
    "fr": [
        # === Protozoaires intestinaux ===
        {"q": "Quel parasite est connu sous le nom de 'bague a chaton' dans les hematies?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Le Plasmodium presente une forme en bague a chaton (signet ring) dans les hematies au stade trophozoite jeune.", "category": "Hematozoaires"},
        {"q": "Le kyste mature de Giardia possede combien de noyaux?", "options": ["2 noyaux", "4 noyaux", "6 noyaux", "8 noyaux"], "answer": 1, "explanation": "Le kyste mature de Giardia lamblia contient 4 noyaux. Le trophozoite en possede 2.", "category": "Protozoaires intestinaux"},
        {"q": "Quel parasite est transmis par le phlebotome?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "La Leishmania est transmise par la piqure du phlebotome (mouche des sables).", "category": "Protozoaires tissulaires"},
        {"q": "L'eperon terminal est caracteristique de quel oeuf?", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "L'oeuf de Schistosoma haematobium possede un eperon terminal. S. mansoni a un eperon lateral.", "category": "Helminthes"},
        {"q": "Quel examen est urgent en cas de suspicion de paludisme?", "options": ["Coproculture", "ECBU", "Goutte epaisse + Frottis", "Serologie"], "answer": 2, "explanation": "La goutte epaisse et le frottis sanguin sont les examens de reference urgents pour le paludisme.", "category": "Diagnostic"},
        {"q": "Le trophozoite d'E. histolytica se distingue par:", "options": ["Ses flagelles", "Ses hematies phagocytees", "Sa membrane ondulante", "Son kinetoplaste"], "answer": 1, "explanation": "La presence d'hematies phagocytees est le critere de pathogenicite d'E. histolytica hematophage.", "category": "Protozoaires intestinaux"},
        {"q": "La maladie de Chagas est causee par:", "options": ["T. brucei gambiense", "T. cruzi", "L. donovani", "P. vivax"], "answer": 1, "explanation": "Trypanosoma cruzi est l'agent de la maladie de Chagas, transmise par les triatomes.", "category": "Protozoaires sanguins"},
        {"q": "Quel colorant est utilise pour les amastigotes de Leishmania?", "options": ["Ziehl-Neelsen", "Gram", "MGG (May-Grunwald-Giemsa)", "Lugol"], "answer": 2, "explanation": "La coloration MGG permet de visualiser les amastigotes avec noyau et kinetoplaste.", "category": "Techniques"},
        {"q": "Le Praziquantel est le traitement de reference de:", "options": ["Paludisme", "Amibiase", "Bilharziose", "Giardiose"], "answer": 2, "explanation": "Le Praziquantel est le medicament de choix contre la bilharziose.", "category": "Therapeutique"},
        {"q": "La 'face de hibou' est observee chez:", "options": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "answer": 1, "explanation": "Le trophozoite de Giardia vu de face montre 2 noyaux symetriques = face de hibou.", "category": "Morphologie"},
        # === Techniques de laboratoire ===
        {"q": "La technique de Ritchie est une methode de:", "options": ["Coloration", "Concentration diphasique", "Culture", "Serologie"], "answer": 1, "explanation": "La technique de Ritchie (formol-ether) est une methode de concentration diphasique pour les oeufs et kystes.", "category": "Techniques"},
        {"q": "Le Lugol sert a mettre en evidence:", "options": ["Les flagelles", "Les noyaux des kystes", "Les hematies", "Les bacteries"], "answer": 1, "explanation": "Le Lugol (iode) colore le glycogene et met en evidence les noyaux des kystes de protozoaires.", "category": "Techniques"},
        {"q": "L'objectif x100 (immersion) necessite:", "options": ["De l'eau", "De l'huile", "De l'alcool", "Du serum physiologique"], "answer": 1, "explanation": "L'objectif x100 a immersion necessite de l'huile pour augmenter l'indice de refraction.", "category": "Microscopie"},
        {"q": "Le scotch-test de Graham permet de rechercher:", "options": ["Giardia", "Enterobius (oxyure)", "Ascaris", "Taenia"], "answer": 1, "explanation": "Le scotch-test matinal recherche les oeufs d'Enterobius vermicularis deposes dans les plis perianaux.", "category": "Techniques"},
        {"q": "Quelle technique est recommandee pour Cryptosporidium?", "options": ["Lugol", "Ziehl-Neelsen modifie", "MGG", "Gram"], "answer": 1, "explanation": "La coloration de Ziehl-Neelsen modifiee (safranine) met en evidence les oocystes de Cryptosporidium.", "category": "Techniques"},
        # === Helminthes ===
        {"q": "L'oeuf d'Ascaris lumbricoides est:", "options": ["Ovoide avec eperon", "Mamelonne avec coque epaisse", "Operculé", "En forme de citron"], "answer": 1, "explanation": "L'oeuf d'Ascaris est ovoide (60-70um), mamelonne avec une coque epaisse brune.", "category": "Helminthes"},
        {"q": "Le scolex de Taenia solium possede:", "options": ["Ventouses uniquement", "Crochets uniquement", "Ventouses + crochets", "Bothridies"], "answer": 2, "explanation": "T. solium (tenia arme) possede 4 ventouses ET une double couronne de crochets sur le rostellum.", "category": "Helminthes"},
        {"q": "Les microfilaires se recherchent dans:", "options": ["Les selles", "Le sang (horaire)", "Les urines", "Le LCR"], "answer": 1, "explanation": "Les microfilaires ont une periodicite sanguine (nocturne pour W. bancrofti, diurne pour Loa loa).", "category": "Helminthes"},
        {"q": "L'Eosinophilie sanguine oriente vers:", "options": ["Une infection bacterienne", "Une helminthiase", "Une virose", "Un paludisme"], "answer": 1, "explanation": "L'eosinophilie est un marqueur d'orientation majeur vers une helminthiase (migration larvaire ++)", "category": "Diagnostic"},
        {"q": "La cysticercose est causee par:", "options": ["Le ver adulte de T. saginata", "La larve de T. solium", "Echinococcus", "Ascaris"], "answer": 1, "explanation": "La cysticercose est causee par la larve (cysticerque) de Taenia solium chez l'homme (impasse parasitaire).", "category": "Helminthes"},
        # === Épidémiologie ===
        {"q": "En Algerie, la leishmaniose cutanee du sud est due a:", "options": ["L. infantum", "L. major", "L. tropica", "L. braziliensis"], "answer": 1, "explanation": "L. major cause la forme cutanee zoonotique du sud algerien (Clou de Biskra). L. infantum est au nord.", "category": "Epidemiologie"},
        {"q": "Le reservoir de T. brucei gambiense est principalement:", "options": ["Le betail", "L'homme", "Le porc", "Les rongeurs"], "answer": 1, "explanation": "Pour T. b. gambiense (forme chronique), l'homme est le principal reservoir. Le betail pour rhodesiense.", "category": "Epidemiologie"},
        {"q": "La bilharziose urinaire se contracte par:", "options": ["Ingestion d'eau", "Contact cutane avec eau douce", "Piqure d'insecte", "Voie aerienne"], "answer": 1, "explanation": "Les cercaires de Schistosoma penetrent activement la peau lors du contact avec l'eau douce contaminee.", "category": "Epidemiologie"},
        {"q": "Quel est le moustique vecteur du paludisme?", "options": ["Aedes", "Culex", "Anopheles", "Simulium"], "answer": 2, "explanation": "L'anophele femelle est le seul vecteur du Plasmodium. Aedes transmet la dengue/Zika.", "category": "Epidemiologie"},
        {"q": "Le kyste hydatique est du a:", "options": ["Taenia saginata", "Echinococcus granulosus", "Fasciola hepatica", "Toxocara canis"], "answer": 1, "explanation": "Echinococcus granulosus (ver du chien) cause le kyste hydatique chez l'homme.", "category": "Helminthes"},
        # === Morphologie avancée ===
        {"q": "Le corps chromatoide 'en cigare' est typique de:", "options": ["E. histolytica", "E. coli", "Giardia", "Balantidium"], "answer": 0, "explanation": "Le kyste d'E. histolytica contient des corps chromatoides en cigare (vs pointus chez E. coli).", "category": "Morphologie"},
        {"q": "Quel protozoaire possede un macronoyau et un micronoyau?", "options": ["Giardia", "Balantidium coli", "Trichomonas", "Entamoeba"], "answer": 1, "explanation": "Balantidium coli est le seul protozoaire cilie pathogene humain, avec macro et micronoyau.", "category": "Morphologie"},
        {"q": "La membrane ondulante est caracteristique de:", "options": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "answer": 1, "explanation": "Le Trypanosoma possede une membrane ondulante bien visible reliant le flagelle au corps.", "category": "Morphologie"},
        {"q": "Le gametocyte en 'banane' (falciforme) est typique de:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "Les gametocytes de P. falciparum sont en forme de banane (falciformes), pathognomoniques.", "category": "Hematozoaires"},
        {"q": "Combien de noyaux possede le kyste d'Entamoeba coli?", "options": ["4", "6", "8", "12"], "answer": 2, "explanation": "Le kyste mature d'E. coli contient 8 noyaux (vs 4 pour E. histolytica).", "category": "Morphologie"},
        # === Thérapeutique ===
        {"q": "Le Metronidazole est inefficace contre:", "options": ["E. histolytica", "Giardia", "Helminthes", "Trichomonas"], "answer": 2, "explanation": "Le Metronidazole est un anti-protozoaire. Il est inefficace contre les helminthes (vers).", "category": "Therapeutique"},
        {"q": "L'Albendazole est un:", "options": ["Anti-protozoaire", "Anti-helminthique a large spectre", "Antibiotique", "Antifongique"], "answer": 1, "explanation": "L'Albendazole est un anti-helminthique a large spectre agissant sur nematodes et cestodes.", "category": "Therapeutique"},
        {"q": "Le traitement de reference du paludisme grave est:", "options": ["Chloroquine", "Artesunate IV", "Metronidazole", "Praziquantel"], "answer": 1, "explanation": "L'Artesunate IV a remplace la Quinine comme traitement de 1ere ligne du paludisme grave (OMS).", "category": "Therapeutique"},
        {"q": "L'Ivermectine est utilisee contre:", "options": ["Filarioses et strongyloidose", "Paludisme", "Amibiase", "Giardiose"], "answer": 0, "explanation": "L'Ivermectine est l'anti-helminthique de reference pour les filarioses et la strongyloidose.", "category": "Therapeutique"},
        {"q": "Le Niclosamide (Tredemine) agit sur:", "options": ["Les nematodes", "Les cestodes (tenias)", "Les trematodes", "Les protozoaires"], "answer": 1, "explanation": "Le Niclosamide est specifique des cestodes (Taenia saginata/solium).", "category": "Therapeutique"},
        # === Cas cliniques ===
        {"q": "Un patient revient d'Afrique avec fievre + frissons + acces febriles rythmes. Suspicion de:", "options": ["Amibiase", "Paludisme", "Bilharziose", "Giardiose"], "answer": 1, "explanation": "Fievre + frissons + rythme apres retour d'Afrique = paludisme jusqu'a preuve du contraire (URGENCE).", "category": "Cas clinique"},
        {"q": "Hematurie terminale + baignade en eau douce en Afrique =", "options": ["Giardiose", "Paludisme", "Bilharziose urinaire", "Amibiase"], "answer": 2, "explanation": "Hematurie + baignade en eau douce en zone d'endemie = bilharziose a S. haematobium.", "category": "Cas clinique"},
        {"q": "Diarrhee graisseuse chronique + malabsorption chez un enfant =", "options": ["Amibiase", "Giardiose", "Cryptosporidiose", "Salmonellose"], "answer": 1, "explanation": "Giardia lamblia est la cause la plus frequente de diarrhee graisseuse avec malabsorption chez l'enfant.", "category": "Cas clinique"},
        {"q": "Chancre d'inoculation + adénopathies cervicales + somnolence =", "options": ["Paludisme", "Leishmaniose", "Trypanosomiase", "Toxoplasmose"], "answer": 2, "explanation": "Chancre + adenopathies + troubles du sommeil = Trypanosomiase Humaine Africaine (maladie du sommeil).", "category": "Cas clinique"},
        {"q": "Bouton ulcere indolore + retour du Sahara algerien =", "options": ["Leishmaniose cutanee", "Furoncle", "Anthrax", "Mycose"], "answer": 0, "explanation": "Ulcere indolore apres sejour au Sud = Leishmaniose cutanee (Clou de Biskra) a L. major.", "category": "Cas clinique"},
    ],
    "ar": [
        {"q": "أي طفيلي يُعرف بشكل 'الخاتم' داخل كريات الدم الحمراء؟", "options": ["الجيارديا", "المتصورة (البلازموديوم)", "الليشمانيا", "الأميبا"], "answer": 1, "explanation": "المتصورة تظهر بشكل خاتم داخل الكريات الحمراء في طور الغاذي الشاب.", "category": "طفيليات دموية"},
        {"q": "كم نواة في كيس الجيارديا الناضج؟", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "كيس الجيارديا الناضج يحتوي على 4 نوى. الطور الغاذي يحتوي على 2.", "category": "أوالي معوية"},
        {"q": "أي طفيلي ينتقل عبر ذبابة الرمل؟", "options": ["البلازموديوم", "التريبانوسوما", "الليشمانيا", "البلهارسيا"], "answer": 2, "explanation": "الليشمانيا تنتقل عبر لدغة ذبابة الرمل (الفليبوتوم).", "category": "أوالي نسيجية"},
        {"q": "النتوء الطرفي يميز بيضة أي طفيلي؟", "options": ["الأسكاريس", "البلهارسيا الدموية", "البلهارسيا المنسونية", "الشريطية"], "answer": 1, "explanation": "بيضة البلهارسيا الدموية لها نتوء طرفي. المنسونية لها نتوء جانبي.", "category": "ديدان"},
        {"q": "ما الفحص العاجل عند الاشتباه بالملاريا؟", "options": ["زرع براز", "فحص بول", "قطرة سميكة + لطاخة", "مصلية"], "answer": 2, "explanation": "القطرة السميكة واللطاخة الدموية هما الفحصان المرجعيان العاجلان للملاريا.", "category": "تشخيص"},
        {"q": "تقنية ريتشي هي طريقة:", "options": ["تلوين", "تركيز ثنائي الطور", "زرع", "مصلية"], "answer": 1, "explanation": "تقنية ريتشي (فورمول-إيثر) هي طريقة تركيز ثنائية الطور للبيض والأكياس.", "category": "تقنيات"},
        {"q": "اللوغول يساعد في إظهار:", "options": ["الأسواط", "نوى الأكياس", "الكريات الحمراء", "البكتيريا"], "answer": 1, "explanation": "اللوغول يلوّن الغليكوجين ويُظهر نوى أكياس الأوالي.", "category": "تقنيات"},
        {"q": "الهدف ×100 (الغمر) يحتاج:", "options": ["ماء", "زيت", "كحول", "محلول ملحي"], "answer": 1, "explanation": "الهدف ×100 بالغمر يحتاج زيت الأرز لزيادة معامل الانكسار.", "category": "مجهرية"},
        {"q": "فحص سكوتش غراهام يبحث عن:", "options": ["الجيارديا", "الحرقص (الأوكسيور)", "الأسكاريس", "الشريطية"], "answer": 1, "explanation": "اختبار سكوتش الصباحي يبحث عن بيض الحرقص في الثنايا حول الشرج.", "category": "تقنيات"},
        {"q": "العرسة الموزية (المنجلية) مميزة لـ:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "عرسات P. falciparum لها شكل الموزة المميز.", "category": "طفيليات دموية"},
        {"q": "كم نواة في كيس Entamoeba coli الناضج؟", "options": ["4", "6", "8", "12"], "answer": 2, "explanation": "كيس E. coli الناضج يحتوي على 8 نوى (مقابل 4 لـ E. histolytica).", "category": "مورفولوجيا"},
        {"q": "الغشاء المتموج مميز لـ:", "options": ["الجيارديا", "التريبانوسوما", "الليشمانيا", "البلازموديوم"], "answer": 1, "explanation": "التريبانوسوما يمتلك غشاءً متموجاً واضحاً يربط السوط بالجسم.", "category": "مورفولوجيا"},
        {"q": "مريض عائد من أفريقيا بحمى + قشعريرة + نوبات حرارة منتظمة:", "options": ["أميبيا", "ملاريا", "بلهارسيا", "جيارديا"], "answer": 1, "explanation": "حمى + قشعريرة + نوبات بعد العودة من أفريقيا = ملاريا حتى يثبت العكس.", "category": "حالة سريرية"},
        {"q": "دم في نهاية التبول + سباحة في ماء عذب في أفريقيا:", "options": ["جيارديا", "ملاريا", "بلهارسيا بولية", "أميبيا"], "answer": 2, "explanation": "بيلة دموية + سباحة في ماء عذب = بلهارسيا S. haematobium.", "category": "حالة سريرية"},
        {"q": "الميترونيدازول غير فعال ضد:", "options": ["الأميبا", "الجيارديا", "الديدان", "المشعرات"], "answer": 2, "explanation": "الميترونيدازول مضاد أوالي. غير فعال ضد الديدان.", "category": "علاج"},
    ],
    "en": [
        {"q": "Which parasite shows a 'signet ring' form in RBCs?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Plasmodium shows a signet ring form inside RBCs at the young trophozoite stage.", "category": "Blood parasites"},
        {"q": "How many nuclei does a mature Giardia cyst have?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "A mature Giardia cyst contains 4 nuclei. The trophozoite has 2.", "category": "Intestinal protozoa"},
        {"q": "Which parasite is transmitted by the sandfly?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania is transmitted by the sandfly (phlebotomus) bite.", "category": "Tissue protozoa"},
        {"q": "The terminal spine is characteristic of which egg?", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "S. haematobium egg has a terminal spine. S. mansoni has a lateral spine.", "category": "Helminths"},
        {"q": "What is the urgent test for suspected malaria?", "options": ["Stool culture", "Urinalysis", "Thick smear + Thin smear", "Serology"], "answer": 2, "explanation": "Thick and thin blood smears are the gold standard for malaria diagnosis.", "category": "Diagnosis"},
        {"q": "The Ritchie technique is a method of:", "options": ["Staining", "Diphasic concentration", "Culture", "Serology"], "answer": 1, "explanation": "Ritchie (formol-ether) is a diphasic concentration method for eggs and cysts.", "category": "Techniques"},
        {"q": "Lugol helps visualize:", "options": ["Flagella", "Cyst nuclei", "Red blood cells", "Bacteria"], "answer": 1, "explanation": "Lugol (iodine) stains glycogen and highlights protozoan cyst nuclei.", "category": "Techniques"},
        {"q": "The x100 immersion objective requires:", "options": ["Water", "Oil", "Alcohol", "Saline"], "answer": 1, "explanation": "The x100 immersion objective requires oil to increase the refractive index.", "category": "Microscopy"},
        {"q": "The banana-shaped gametocyte is typical of:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "P. falciparum gametocytes are banana-shaped (falciform), pathognomonic.", "category": "Blood parasites"},
        {"q": "How many nuclei does a mature E. coli cyst have?", "options": ["4", "6", "8", "12"], "answer": 2, "explanation": "Mature E. coli cyst contains 8 nuclei (vs 4 in E. histolytica).", "category": "Morphology"},
        {"q": "The undulating membrane is characteristic of:", "options": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "answer": 1, "explanation": "Trypanosoma has a prominent undulating membrane connecting flagellum to body.", "category": "Morphology"},
        {"q": "Patient from Africa with fever + chills + rhythmic attacks:", "options": ["Amebiasis", "Malaria", "Schistosomiasis", "Giardiasis"], "answer": 1, "explanation": "Fever + chills + rhythmic attacks after Africa = malaria until proven otherwise.", "category": "Clinical case"},
        {"q": "Terminal hematuria + freshwater swimming in Africa:", "options": ["Giardiasis", "Malaria", "Urinary schistosomiasis", "Amebiasis"], "answer": 2, "explanation": "Hematuria + freshwater swimming in endemic area = S. haematobium.", "category": "Clinical case"},
        {"q": "Metronidazole is ineffective against:", "options": ["E. histolytica", "Giardia", "Helminths", "Trichomonas"], "answer": 2, "explanation": "Metronidazole is an anti-protozoal. Ineffective against helminths (worms).", "category": "Therapeutics"},
        {"q": "Albendazole is a:", "options": ["Anti-protozoal", "Broad-spectrum anti-helminthic", "Antibiotic", "Antifungal"], "answer": 1, "explanation": "Albendazole is a broad-spectrum anti-helminthic acting on nematodes and cestodes.", "category": "Therapeutics"},
    ]
}

# ============================================
#  7. قاعدة بيانات الشات بوت - محسّنة وشاملة
# ============================================
CHATBOT_KNOWLEDGE = {
    "fr": {
        "keywords": {
            "amoeba": "🔬 **Entamoeba histolytica**\n\nParasite causant la dysenterie amibienne et l'abces hepatique.\n\n**Diagnostic:** Kystes a 4 noyaux (Lugol), trophozoites hematophages (etat frais).\n**Taille:** Kyste 10-15um, Trophozoite 20-40um\n**Distinction:** E. histolytica phagocyte les hematies (vs E. dispar qui ne le fait pas)\n**Traitement:** Metronidazole 500mg x3/j (7-10j) + Amoebicide de contact\n**Milieu:** Transmission feco-orale, eau contaminee",
            "amibe": "🔬 **Entamoeba histolytica**\n\nParasite causant la dysenterie amibienne et l'abces hepatique.\n\n**Diagnostic:** Kystes a 4 noyaux (Lugol), trophozoites hematophages (etat frais).\n**Traitement:** Metronidazole + Intetrix",
            "giardia": "🔬 **Giardia lamblia**\n\nProtozoaire flagelle du duodenum.\n\n**Morphologie:** Trophozoite en cerf-volant (12-15um), face de hibou (2 noyaux), kyste ovoide a 4 noyaux.\n**Symptomes:** Diarrhee graisseuse, malabsorption, ballonnements\n**Diagnostic:** EPS direct + Lugol, antigene Giardia (ELISA)\n**Traitement:** Metronidazole 250mg x3/j (5j) ou Tinidazole 2g dose unique\n**Prevention:** Eau potable, hygiene des mains",
            "leishmania": "🔬 **Leishmania spp.**\n\nTransmise par le phlebotome. Formes cutanee et viscerale.\n\n**Morphologie:** Amastigotes 2-5um intracellulaires (macrophages), noyau + kinetoplaste au MGG\n**En Algerie:** L. major (sud, cutanee) et L. infantum (nord, viscerale)\n**Diagnostic:** Frottis de lesion + MGG, PCR, serologie, culture NNN\n**Traitement:** Glucantime IM (cutanee), Amphotericine B (viscerale)\n**MDO en Algerie** (Maladie a Declaration Obligatoire)",
            "plasmodium": "🚨 **URGENCE - Plasmodium spp.**\n\nAgent du paludisme. P. falciparum = le plus grave !\n\n**Morphologie:** Bague a chaton dans les hematies, gametocytes en banane (P.f)\n**Diagnostic URGENT:** Frottis mince + Goutte epaisse (resultat <2h!)\n**Seuil critique:** Parasitemie >2% = forme grave\n**Traitement:** ACT (Artemisinine) ou Artesunate IV si grave\n**5 especes:** P. falciparum, vivax, ovale, malariae, knowlesi\n**Vecteur:** Anophele femelle",
            "malaria": "🚨 **URGENCE - Paludisme**\n\n229 millions de cas/an (OMS). Mortel si P. falciparum non traite !\n\n**Fievre + frissons + retour de zone d'endemie = paludisme jusqu'a preuve du contraire**\n**Frottis + Goutte epaisse EN URGENCE**\n**TDR pour depistage rapide**\n**Hospitalisation si P. falciparum**",
            "paludisme": "🚨 **URGENCE - Paludisme**\n\nMeme chose que Malaria. Voir reponse ci-dessus.",
            "trypanosoma": "🔬 **Trypanosoma spp.**\n\nMaladie du sommeil (T. brucei) ou de Chagas (T. cruzi).\n\n**Morphologie:** Forme en S/C (15-30um), membrane ondulante, flagelle libre, kinetoplaste\n**Diagnostic:** Frottis sanguin, ponction ganglionnaire, LCR (staging)\n**Staging:** Ponction lombaire OBLIGATOIRE (>5 cellules/mm3 = phase 2 neurologique)\n**Traitement:** Phase 1: Pentamidine/Suramine. Phase 2: NECT ou Melarsoprol\n**IgM serique tres elevee = orientation diagnostique**",
            "schistosoma": "🔬 **Schistosoma spp.**\n\nCause la bilharziose. 2eme endemie parasitaire mondiale.\n\n**S. haematobium:** Eperon TERMINAL, urines de MIDI, bilharziose urinaire\n**S. mansoni:** Eperon LATERAL, selles, bilharziose hepato-intestinale\n**Diagnostic:** Oeufs dans urines/selles, serologie, echographie\n**Traitement:** Praziquantel 40mg/kg dose unique\n**Prevention:** Eviter eau douce en zone d'endemie",
            "bilharziose": "🔬 **Bilharziose (Schistosomiase)**\n\nMeme chose que Schistosoma. Contamination par contact avec eau douce contaminee.\n**Cercaires penetrent la peau**\n**S. haematobium: urines, S. mansoni: selles**",
            "bonjour": "Bonjour ! 👋 Je suis **Dr. DhiaBot**, votre assistant parasitologique intelligent. Je peux vous aider avec:\n\n🔬 Identification des parasites\n💊 Traitements recommandes\n🧪 Techniques de laboratoire\n📋 Interpretation des resultats\n🩺 Cas cliniques\n\nPosez-moi votre question !",
            "salut": "Salut ! 😊 Je suis Dr. DhiaBot. Comment puis-je vous aider en parasitologie ?",
            "merci": "De rien ! 😊 C'est mon plaisir de vous aider. La parasitologie est ma passion ! N'hesitez pas si vous avez d'autres questions !",
            "microscope": "🔬 **Le Microscope en Parasitologie:**\n\n**Objectifs:**\n• x10: Reperage general de la lame\n• x40: Identification des oeufs, kystes, trophozoites\n• x100 (immersion a l'huile): Details morphologiques fins (Plasmodium, Leishmania)\n\n**Types recommandes:**\n• Optique binoculaire: Standard pour EPS\n• Contraste de phase: Mobilite des trophozoites\n• Fluorescence: Cryptosporidium (auramine)\n\n**Conseil:** Toujours commencer par x10 pour reperer, puis x40 pour identifier !",
            "coloration": "🎨 **Colorations en Parasitologie:**\n\n**Lugol (Iode):** Noyaux des kystes (amibes, Giardia)\n**MGG (May-Grunwald-Giemsa):** Parasites sanguins (Plasmodium, Leishmania, Trypanosoma)\n**Giemsa:** Frottis sanguin\n**Ziehl-Neelsen modifie:** Cryptosporidium, Isospora\n**Trichrome:** Microsporidies, amibes\n**Weber (chromotrope):** Microsporidies\n**Coloration au fer:** Flagelles\n\n**Regle:** Chaque parasite a SA coloration optimale !",
            "selle": "💩 **Examen Parasitologique des Selles (EPS):**\n\n**1. Examen macroscopique:** Consistance, couleur, mucus, sang, vers adultes\n**2. Examen microscopique direct:**\n   • Etat frais (NaCl 0.9%): Mobilite des trophozoites\n   • Lugol: Noyaux des kystes\n**3. Apres concentration:**\n   • Ritchie (formol-ether): Oeufs et kystes\n   • Flottation (Willis): Oeufs legers\n   • Kato-Katz: Quantitatif\n\n⚠️ **Examiner dans les 30 min** pour voir les formes vegetatives !\n📌 **Repeter x3** a quelques jours d'intervalle (sensibilite 50-60% pour un seul EPS)",
            "sang": "🩸 **Examen du Sang pour Parasites:**\n\n**Frottis mince:** Identification d'espece (morphologie)\n**Goutte epaisse:** Plus sensible (10x), detection des faibles parasitemies\n**Coloration:** MGG ou Giemsa\n**TDR:** Tests rapides (HRP2, pLDH) pour depistage\n\n**Quand faire?**\n• Paludisme: URGENCE, resultat <2h\n• Filaires: Periodicite (W. bancrofti = nuit, Loa loa = jour)\n• Trypanosoma: Recherche sur lame\n• Leishmania viscerale: Ponction medullaire\n\n⚠️ **Frottis + Goutte epaisse = tandem obligatoire en paludisme**",
            "hygiene": "🧼 **Conseils d'Hygiene Anti-Parasitaire:**\n\n✅ Lavage des mains au savon (avant repas, apres WC)\n✅ Eau potable (filtree, bouillie ou en bouteille)\n✅ Cuisson suffisante des viandes (>65°C)\n✅ Lavage des fruits et legumes\n✅ Moustiquaires impregnees (paludisme)\n✅ Eviter eau douce stagnante (bilharziose)\n✅ Repulsifs anti-phlebotomes (crepuscule)\n✅ Deworming regulier en zone d'endemie\n✅ Assainissement de l'eau et des latrines",
            "concentration": "🧪 **Techniques de Concentration:**\n\n**Ritchie (Formol-Ether):** Reference universelle, concentration diphasique des oeufs, kystes et larves.\n**Willis (Flottation):** NaCl sature, oeufs legers flottent en surface.\n**Kato-Katz:** Semi-quantitatif, OMS pour zones d'endemie.\n**Baermann:** Specifique pour larves de Strongyloides.\n**MIF (Merthiolate-Iode-Formol):** Conservation + coloration simultanee.\n\n💡 **La concentration augmente la sensibilite de 2 a 3 fois !**",
            "eps": "📋 **Conduite d'un EPS complet:**\n\n1. Renseignements cliniques\n2. Examen macroscopique des selles\n3. Examen direct: etat frais + Lugol\n4. Concentration: Ritchie ± Willis\n5. Techniques speciales si besoin\n6. Resultat detaille + conclusion\n\n⚠️ Toujours preciser: direct negatif / concentration negative",
            "ascaris": "🪱 **Ascaris lumbricoides:**\n\nVer rond (nematode) le plus frequent au monde.\n**Oeuf:** Mamelonne, coque epaisse brune (60-70um)\n**Ver adulte:** 15-30cm (femelle), 15-20cm (male)\n**Cycle:** Ingestion oeuf → larve → migration pulmonaire (Loeffler) → intestin grele\n**Diagnostic:** Oeufs dans EPS, ver adulte expulse\n**Traitement:** Albendazole 400mg dose unique ou Mebendazole",
            "taenia": "🪱 **Taenia spp. (Cestodes):**\n\n**T. saginata (inerme):** Viande de boeuf, pas de crochets\n**T. solium (arme):** Viande de porc, crochets sur scolex (risque de cysticercose!)\n**Diagnostic:** Anneaux dans les selles, scotch-test, oeufs (non distinguables)\n**Traitement:** Niclosamide (Tredemine) ou Praziquantel\n**Prevention:** Cuisson de la viande (>65°C), inspection sanitaire",
            "toxoplasma": "🔬 **Toxoplasma gondii:**\n\nProtozoaire intracellulaire. Chat = hote definitif.\n**Transmission:** Viande mal cuite, oocystes du chat, transplacentaire\n**Danger:** Femme enceinte sero-negative (toxoplasmose congenitale)\n**Diagnostic:** Serologie IgG/IgM, avidite des IgG\n**Traitement:** Spiramycine (femme enceinte), Pyrimethamine-Sulfadiazine",
            "oxyure": "🪱 **Enterobius vermicularis (Oxyure):**\n\nVer le plus frequent chez l'enfant.\n**Symptome:** Prurit anal nocturne ++\n**Diagnostic:** Scotch-test de Graham (matin avant toilette)\n**Traitement:** Flubendazole (Fluvermal), toute la famille!\n**Auto-reinfestation** frequente",
            "strongyloides": "🪱 **Strongyloides stercoralis (Anguillule):**\n\nNematode avec cycle d'auto-infestation endogene.\n**Danger:** Syndrome d'hyper-infestation chez immunodeprime\n**Diagnostic:** Larves rhabditoides dans les selles fraiches, Baermann\n**Traitement:** Ivermectine (reference)\n⚠️ **Depister avant toute corticotherapie !**",
            "cryptosporidium": "🔬 **Cryptosporidium:**\n\nCoccidian intracellulaire. Opportuniste chez VIH+.\n**Oocystes:** 4-6um, Ziehl-Neelsen modifie (rouge sur fond vert)\n**Symptomes:** Diarrhee aqueuse profuse, cholera-like\n**Diagnostic:** Ziehl modifie, auramine (fluorescence), PCR\n**Traitement:** Nitazoxanide. Restauration immunitaire (ARV) chez VIH+",
            "qui es tu": "🤖 Je suis **Dr. DhiaBot**, l'assistant IA parasitologique le plus avance ! Developpe par Sebbag Mohamed Dhia Eddine et Ben Sghir Mohamed a l'INFSPM de Ouargla, Algerie. Je connais tous les parasites et je suis toujours pret a vous aider !",
            "aide": "📚 **Je peux vous aider avec:**\n\n🔬 **Parasites:** Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Oxyure, Strongyloides, Cryptosporidium...\n🧪 **Techniques:** EPS, coloration, concentration, microscopie, sang\n💊 **Traitements:** Anti-protozoaires, anti-helminthiques\n🩺 **Clinique:** Symptomes, cas cliniques\n🧼 **Prevention:** Hygiene, prophylaxie\n\nTapez le nom d'un parasite ou un mot-cle !",
            "diagnostic": "🩺 **Demarche Diagnostique en Parasitologie:**\n\n1. **Clinique:** Symptomes, voyage, exposition\n2. **Orientation:** NFS (eosinophilie?), serologie\n3. **Confirmation:**\n   - Selles → EPS direct + concentration\n   - Sang → Frottis + Goutte epaisse\n   - Urines → Sediment (Schistosoma)\n   - Tissus → Biopsie + coloration\n4. **Biologie moleculaire:** PCR (reference)\n5. **Imagerie:** Echo, scanner si besoin",
        },
        "default": "🤖 Je suis **Dr. DhiaBot**, votre assistant parasitologique.\n\nJe connais: **Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Oxyure, Strongyloides, Cryptosporidium**\n\nEt aussi: **techniques de labo, colorations, microscopie, traitements, epidemiologie, hygiene**\n\n💡 Tapez un mot-cle ou 'aide' pour la liste complete !",
        "greeting": "👋 Bonjour ! Je suis **Dr. DhiaBot** 🤖 votre assistant parasitologique intelligent.\n\nJe peux vous aider avec l'identification des parasites, les techniques de laboratoire, les traitements, et bien plus !\n\n💡 Essayez: 'amoeba', 'microscope', 'coloration', 'aide'"
    },
    "ar": {
        "keywords": {
            "أميبا": "🔬 **الأميبا الحالّة للنسج**\n\nتسبب الزحار الأميبي وخراج الكبد.\n**التشخيص:** أكياس بـ 4 نوى (لوغول)، أطوار غاذية آكلة للكريات.\n**العلاج:** ميترونيدازول + مبيد أميبي تلامسي.",
            "جيارديا": "🔬 **الجيارديا**\n\nتستعمر الاثني عشر. شكل طائرة ورقية بوجه بومة.\n**العلاج:** ميترونيدازول أو تينيدازول.",
            "ليشمانيا": "🔬 **الليشمانيا**\n\nتنتقل عبر ذبابة الرمل.\n**في الجزائر:** L. major (جنوب، جلدي) وL. infantum (شمال، حشوي).\n**العلاج:** غلوكانتيم/أمفوتيريسين ب.",
            "ملاريا": "🚨 **حالة طوارئ! الملاريا**\n\nالمتصورة تسبب الملاريا. شكل خاتم في الكريات.\n**فحص عاجل:** لطاخة + قطرة سميكة.\n**العلاج:** ACT.",
            "بلهارسيا": "🔬 **البلهارسيا**\n\nتنتقل في المياه العذبة.\n**S. haematobium:** نتوء طرفي، بول.\n**S. mansoni:** نتوء جانبي، براز.\n**العلاج:** برازيكوانتيل.",
            "مرحبا": "مرحباً! 👋 أنا **الدكتور ضياء بوت**، مساعدك في علم الطفيليات.\n\nأستطيع مساعدتك في:\n🔬 تحديد الطفيليات\n💊 العلاجات\n🧪 تقنيات المخبر\n\nاسألني!",
            "مجهر": "🔬 **المجهر في علم الطفيليات:**\n\n**×10:** استكشاف عام\n**×40:** تحديد البيض والأكياس\n**×100 (غمر):** تفاصيل دقيقة (بلازموديوم، ليشمانيا)",
            "تلوين": "🎨 **التلوينات:**\n**لوغول:** نوى الأكياس\n**MGG/جيمزا:** طفيليات الدم\n**زيل-نيلسن المعدل:** كريبتوسبوريديوم",
            "براز": "💩 **فحص البراز الطفيلي:**\n1. فحص عياني\n2. فحص مباشر + لوغول\n3. تركيز (ريتشي)\n⚠️ افحص خلال 30 دقيقة!",
            "مساعدة": "📚 أعرف: أميبا، جيارديا، ليشمانيا، ملاريا، تريبانوسوما، بلهارسيا، أسكاريس، شريطية...\nوأيضاً: تقنيات المخبر، التلوينات، المجهرية، العلاجات.\n💡 اكتب اسم الطفيلي!",
        },
        "default": "🤖 أنا **الدكتور ضياء بوت**. أعرف جميع الطفيليات الرئيسية وتقنيات المخبر.\n💡 اكتب اسم الطفيلي أو 'مساعدة'!",
        "greeting": "مرحباً! 👋 أنا **الدكتور ضياء بوت** 🤖 مساعدك الذكي في علم الطفيليات.\n💡 جرب: 'أميبا'، 'مجهر'، 'تلوين'، 'مساعدة'"
    },
    "en": {
        "keywords": {
            "amoeba": "🔬 **Entamoeba histolytica**\n\nCauses amoebic dysentery and liver abscess.\n**Diagnosis:** 4-nuclei cysts (Lugol), hematophagous trophozoites.\n**Treatment:** Metronidazole + contact amoebicide.",
            "giardia": "🔬 **Giardia lamblia**\n\nDuodenal flagellate. Kite shape, owl face.\n**Treatment:** Metronidazole/Tinidazole.",
            "leishmania": "🔬 **Leishmania**\n\nSandfly-transmitted. Cutaneous and visceral forms.\n**Treatment:** Glucantime/Amphotericin B.",
            "malaria": "🚨 **EMERGENCY - Malaria**\n\nPlasmodium causes malaria. Signet ring in RBCs.\n**URGENT:** Thick + Thin smear.\n**Treatment:** ACT.",
            "plasmodium": "🚨 **EMERGENCY - Plasmodium**\n\nSame as malaria. See above.",
            "schistosoma": "🔬 **Schistosoma**\n\nBilharziasis. Eggs with terminal/lateral spine.\n**Treatment:** Praziquantel.",
            "hello": "Hello! 👋 I'm **Dr. DhiaBot**, your parasitology AI assistant.\n\nI can help with:\n🔬 Parasite identification\n💊 Treatments\n🧪 Lab techniques\n\nAsk me!",
            "microscope": "🔬 **Microscopy in Parasitology:**\n\n**x10:** General scanning\n**x40:** Egg/cyst identification\n**x100 (oil immersion):** Fine details (Plasmodium, Leishmania)",
            "staining": "🎨 **Stains:**\n**Lugol:** Cyst nuclei\n**MGG/Giemsa:** Blood parasites\n**Modified ZN:** Cryptosporidium",
            "stool": "💩 **Stool Parasitology:**\n1. Macroscopic exam\n2. Direct + Lugol\n3. Concentration (Ritchie)\n⚠️ Examine within 30 min!",
            "help": "📚 I know: Amoeba, Giardia, Leishmania, Malaria, Trypanosoma, Schistosoma, Ascaris, Taenia...\nAlso: lab techniques, staining, microscopy, treatments.\n💡 Type a parasite name!",
        },
        "default": "🤖 I'm **Dr. DhiaBot**. I know all major parasites and lab techniques.\n💡 Type a parasite name or 'help'!",
        "greeting": "Hello! 👋 I'm **Dr. DhiaBot** 🤖 your smart parasitology assistant.\n💡 Try: 'amoeba', 'microscope', 'staining', 'help'"
    }
}

DAILY_TIPS = {
    "fr": [
        "💡 Toujours examiner les selles dans les 30 minutes suivant le prelevement pour voir les formes vegetatives mobiles.",
        "💡 Le Lugol aide a mettre en evidence les noyaux des kystes d'amibes. Preparez une dilution fraiche chaque semaine.",
        "💡 Un frottis sanguin doit etre fin (monocouche) pour bien identifier les Plasmodium. L'angle de 45° est crucial.",
        "💡 La goutte epaisse est 10x plus sensible que le frottis mince pour detecter les parasites sanguins.",
        "💡 Les oeufs de Schistosoma haematobium se cherchent dans les urines de midi (pic d'excretion).",
        "💡 Pensez a faire 3 EPS a quelques jours d'intervalle pour augmenter la sensibilite diagnostique.",
        "💡 Le Metronidazole est le traitement de base pour Amoeba, Giardia et Trichomonas. Retenir ce trio !",
        "💡 La coloration de Ziehl-Neelsen modifiee est indispensable pour Cryptosporidium et Isospora.",
        "💡 En cas de paludisme, la premiere goutte epaisse negative ne suffit pas. Repeter a 6-12h d'intervalle.",
        "💡 Le phlebotome est actif au crepuscule - conseillez les moustiquaires et repulsifs aux patients.",
        "💡 L'eosinophilie sanguine est un marqueur d'orientation vers une helminthiase. Pensez-y devant une hypereosinophilie !",
        "💡 La technique de Baermann est specifique pour les larves de Strongyloides. Indispensable avant corticotherapie.",
        "💡 Le kyste d'E. coli a 8 noyaux vs 4 pour E. histolytica. C'est le critere differentiel numero 1.",
        "💡 Toujours noter la consistance des selles: les trophozoites sont dans les selles liquides, les kystes dans les selles formees.",
        "💡 La PCR est le gold standard pour l'identification des especes de Leishmania. Demandez-la en cas de doute.",
    ],
    "ar": [
        "💡 افحص البراز خلال 30 دقيقة من الأخذ لرؤية الأطوار المتحركة.",
        "💡 اللوغول يساعد في إظهار نوى أكياس الأميبا. حضّر تخفيفاً طازجاً كل أسبوع.",
        "💡 اللطاخة الدموية يجب أن تكون رقيقة (أحادية الطبقة) لتحديد البلازموديوم. زاوية 45° مهمة.",
        "💡 القطرة السميكة أكثر حساسية 10 مرات من اللطاخة الرقيقة لكشف طفيليات الدم.",
        "💡 ابحث عن بيض البلهارسيا الدموية في بول الظهيرة (ذروة الإفراز).",
        "💡 أعد فحص البراز 3 مرات على فترات لزيادة حساسية التشخيص.",
        "💡 الميترونيدازول هو الأساس لعلاج الأميبا والجيارديا والمشعرات. احفظ هذا الثلاثي!",
        "💡 كيس E. coli به 8 نوى مقابل 4 لـ E. histolytica. هذا المعيار التفريقي الأول.",
        "💡 سجّل دائماً قوام البراز: الأطوار الغاذية في السائل، الأكياس في المتشكل.",
        "💡 ارتفاع الحمضات في الدم يوجّه نحو إصابة بالديدان.",
    ],
    "en": [
        "💡 Always examine stool within 30 minutes of collection to see motile trophozoites.",
        "💡 Lugol helps visualize amoebic cyst nuclei. Prepare fresh dilution weekly.",
        "💡 Blood smear must be thin (monolayer) for proper Plasmodium identification. 45° angle is key.",
        "💡 Thick smear is 10x more sensitive than thin smear for blood parasites.",
        "💡 Search for S. haematobium eggs in midday urine (peak excretion).",
        "💡 Repeat stool exam x3 at intervals to increase diagnostic sensitivity.",
        "💡 Metronidazole treats Amoeba, Giardia and Trichomonas. Remember this trio!",
        "💡 Modified Ziehl-Neelsen staining is essential for Cryptosporidium and Isospora.",
        "💡 First negative thick smear doesn't rule out malaria. Repeat at 6-12h intervals.",
        "💡 Blood eosinophilia strongly suggests helminthiasis. Always check the differential!",
    ]
}

# ============================================
#  8. تهيئة حالة الجلسة
# ============================================
SESSION_DEFAULTS = {
    "logged_in": False,
    "user_name": "",
    "intro_step": 0,
    "history": [],
    "dark_mode": True,  # ✅ الوضع المظلم كافتراضي
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
}

for key, val in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================
#  9. الدوال المساعدة
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
    return {"critical":"#ff0040","high":"#ff3366","medium":"#ff9500","low":"#00e676","none":"#00e676"}.get(level, "#6b7280")

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

def check_auto_lock():
    if st.session_state.last_activity:
        elapsed = (datetime.now() - st.session_state.last_activity).total_seconds() / 60
        if elapsed > AUTO_LOCK_MINUTES:
            log_activity("Auto-locked (inactivity)")
            st.session_state.logged_in = False
            st.session_state.intro_step = 0
            st.rerun()

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
            }}   
