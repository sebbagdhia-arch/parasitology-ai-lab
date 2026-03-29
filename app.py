# ╔══════════════════════════════════════════════════════════════════╗
# ║          DM SMART LAB AI v4.2 - FINAL FIXED VERSION             ║
# ║     Diagnostic Parasitologique par Intelligence Artificielle     ║
# ║                                                                  ║
# ║  Développé par:                                                  ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)         ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)            ║
# ║                                                                  ║
# ║  INFSPM - Ouargla, Algérie                                      ║
# ╚══════════════════════════════════════════════════════════════════╝

import streamlit as st
import numpy as np
import pandas as pd
import time
import os
import base64
import random
import io
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
from datetime import datetime, timedelta
from fpdf import FPDF

# ============================================
#  PAGE CONFIG
# ============================================
st.set_page_config(page_title="DM Smart Lab AI", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

# ============================================
#  CONSTANTS
# ============================================
APP_VERSION = "4.2.0"
APP_PASSWORD = "123"
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_MINUTES = 5
CONFIDENCE_THRESHOLD = 60
AUTO_LOCK_MINUTES = 15

AUTHORS = {
    "dev1": {"name": "Sebbag Mohamed Dhia Eddine", "role": "Expert IA & Conception"},
    "dev2": {"name": "Ben Sghir Mohamed", "role": "Expert Laboratoire & Données"}
}
INSTITUTION = {"name": "INFSPM", "city": "Ouargla", "country": "Algérie", "year": 2026}
PROJECT_TITLE = "Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais"

# ============================================
#  PARASITE DATABASE
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {"fr": "Kyste spherique (10-15um) a 4 noyaux ou Trophozoite avec pseudopodes et hematies phagocytees.", "ar": "كيس كروي بـ 4 نوى أو طور غاذي بأقدام كاذبة.", "en": "Spherical cyst (10-15um) with 4 nuclei or Trophozoite with pseudopods."},
        "description": {"fr": "Parasite tissulaire responsable de la dysenterie amibienne.", "ar": "طفيلي نسيجي مسبب للزحار الأميبي.", "en": "Tissue parasite causing amoebic dysentery."},
        "funny": {"fr": "Le ninja des intestins !", "ar": "نينجا الأمعاء!", "en": "The intestinal ninja!"},
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {"fr": "Metronidazole (Flagyl) + Amoebicide de contact.", "ar": "ميترونيدازول + مبيد أميبي.", "en": "Metronidazole + contact amoebicide."},
        "extra_tests": {"fr": ["Serologie amibienne", "Echographie hepatique", "NFS + CRP"], "ar": ["مصلية أميبية", "إيكو كبدي", "تعداد دم"], "en": ["Amoebic serology", "Hepatic ultrasound", "CBC + CRP"]},
        "color": "#dc2626", "icon": "🔴",
        "lifecycle": {"fr": "Kyste ingere → Trophozoite → Invasion tissulaire → Kyste", "ar": "ابتلاع الكيس ← طور غاذي ← غزو نسيجي ← كيس", "en": "Cyst ingested → Trophozoite → Tissue invasion → Cyst"}
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia",
        "morphology": {"fr": "Trophozoite piriforme en 'cerf-volant' avec 2 noyaux et 4 paires de flagelles.", "ar": "طور غاذي كمثري بنواتين و4 أزواج أسواط.", "en": "Pear-shaped trophozoite with 2 nuclei and 4 flagella pairs."},
        "description": {"fr": "Protozoaire flagelle colonisant le duodenum.", "ar": "أولي سوطي يستعمر الاثني عشر.", "en": "Flagellated protozoan colonizing duodenum."},
        "funny": {"fr": "Il te fixe avec ses lunettes de soleil !", "ar": "يحدّق فيك بنظارته!", "en": "Staring with sunglasses!"},
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {"fr": "Metronidazole ou Tinidazole.", "ar": "ميترونيدازول أو تينيدازول.", "en": "Metronidazole or Tinidazole."},
        "extra_tests": {"fr": ["Antigene Giardia (selles)", "Test malabsorption"], "ar": ["مستضد الجيارديا", "اختبار سوء الامتصاص"], "en": ["Giardia antigen test", "Malabsorption test"]},
        "color": "#f59e0b", "icon": "🟠",
        "lifecycle": {"fr": "Kyste → Trophozoite → Adhesion intestinale → Kyste", "ar": "كيس ← طور غاذي ← التصاق معوي ← كيس", "en": "Cyst → Trophozoite → Intestinal adhesion → Cyst"}
    },
    "Leishmania": {
        "scientific_name": "Leishmania spp.",
        "morphology": {"fr": "Amastigotes ovoides intracellulaires dans les macrophages. Coloration MGG.", "ar": "لامسوطات بيضاوية داخل البلاعم. تلوين MGG.", "en": "Ovoid amastigotes intracellular in macrophages."},
        "description": {"fr": "Transmis par le phlebotome. Formes cutanee et viscerale.", "ar": "ينتقل عبر ذبابة الرمل. جلدي أو حشوي.", "en": "Transmitted by sandfly. Cutaneous or visceral."},
        "funny": {"fr": "Petit mais costaud !", "ar": "صغير لكن قوي!", "en": "Small but tough!"},
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {"fr": "Glucantime/Amphotericine B.", "ar": "غلوكانتيم/أمفوتيريسين ب.", "en": "Glucantime/Amphotericin B."},
        "extra_tests": {"fr": ["IDR Montenegro", "Serologie Leishmania", "Ponction moelle"], "ar": ["اختبار مونتينيغرو", "مصلية ليشمانيا", "بزل نخاع"], "en": ["Montenegro test", "Leishmania serology", "Bone marrow"]},
        "color": "#dc2626", "icon": "🔴",
        "lifecycle": {"fr": "Phlebotome → Promastigote → Phagocytose → Amastigote", "ar": "ذبابة رمل ← طور سوطي ← بلعمة ← لامسوطي", "en": "Sandfly → Promastigote → Phagocytosis → Amastigote"}
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax",
        "morphology": {"fr": "Forme en 'bague a chaton' dans les hematies.", "ar": "شكل 'خاتم' داخل كريات الدم الحمراء.", "en": "Signet ring form inside RBCs."},
        "description": {"fr": "Agent du paludisme. URGENCE MEDICALE.", "ar": "مسبب الملاريا. حالة طوارئ.", "en": "Malaria agent. MEDICAL EMERGENCY."},
        "funny": {"fr": "Il squatte tes globules !", "ar": "يسكن كرياتك!", "en": "Squats in your RBCs!"},
        "risk_level": "critical",
        "risk_display": {"fr": "🚨 URGENCE", "ar": "🚨 طوارئ", "en": "🚨 EMERGENCY"},
        "advice": {"fr": "HOSPITALISATION ! ACT. Parasitemie /4-6h.", "ar": "تنويم فوري! علاج مركب.", "en": "HOSPITALIZATION! ACT."},
        "extra_tests": {"fr": ["TDR Paludisme", "Parasitemie quantitative", "Bilan hepato-renal"], "ar": ["اختبار سريع للملاريا", "طفيليات كمية", "فحص كبد وكلى"], "en": ["Malaria RDT", "Quantitative parasitemia", "Hepato-renal panel"]},
        "color": "#7f1d1d", "icon": "🚨",
        "lifecycle": {"fr": "Anophele → Sporozoite → Hepatocyte → Merozoite → Hematie", "ar": "أنوفيل ← بوغ ← خلية كبد ← جزئية ← كرية حمراء", "en": "Anopheles → Sporozoite → Hepatocyte → Merozoite → RBC"}
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei / cruzi",
        "morphology": {"fr": "Forme en S/C avec flagelle et membrane ondulante.", "ar": "شكل S أو C بسوط حر وغشاء متموج.", "en": "S/C shape with flagellum and undulating membrane."},
        "description": {"fr": "Maladie du sommeil (brucei) ou Chagas (cruzi).", "ar": "مرض النوم أو شاغاس.", "en": "Sleeping sickness or Chagas disease."},
        "funny": {"fr": "Il court comme Mahrez !", "ar": "يجري مثل محرز!", "en": "Runs like Mahrez!"},
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {"fr": "Examen LCR. Pentamidine/Suramine.", "ar": "فحص السائل الشوكي. بنتاميدين.", "en": "CSF exam. Pentamidine/Suramin."},
        "extra_tests": {"fr": ["Ponction lombaire", "Serologie Trypanosoma"], "ar": ["بزل قطني", "مصلية التريبانوسوما"], "en": ["Lumbar puncture", "Trypanosoma serology"]},
        "color": "#dc2626", "icon": "🔴",
        "lifecycle": {"fr": "Mouche tse-tse → Trypomastigote → Sang → LCR", "ar": "ذبابة تسي تسي ← طور سوطي ← دم ← سائل شوكي", "en": "Tsetse fly → Trypomastigote → Blood → CSF"}
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma spp.",
        "morphology": {"fr": "Oeuf ovoide avec eperon terminal ou lateral.", "ar": "بيضة بيضاوية بنتوء طرفي أو جانبي.", "en": "Ovoid egg with terminal or lateral spine."},
        "description": {"fr": "Bilharziose urinaire ou intestino-hepatique.", "ar": "بلهارسيا بولية أو معوية كبدية.", "en": "Urinary or intestino-hepatic schistosomiasis."},
        "funny": {"fr": "La baignade peut couter cher !", "ar": "السباحة قد تكلفك غالياً!", "en": "Swimming could cost you!"},
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {"fr": "Praziquantel. Eviter eaux stagnantes.", "ar": "برازيكوانتيل. تجنب المياه الراكدة.", "en": "Praziquantel. Avoid stagnant water."},
        "extra_tests": {"fr": ["ECBU", "Serologie Schistosoma", "Echo vesicale"], "ar": ["فحص بول", "مصلية البلهارسيا", "إيكو مثانة"], "en": ["Urinalysis", "Schistosoma serology", "Bladder US"]},
        "color": "#f59e0b", "icon": "🟠",
        "lifecycle": {"fr": "Cercaire → Penetration cutanee → Veine porte → Oeufs", "ar": "سركاريا ← اختراق جلدي ← وريد بابي ← بيض", "en": "Cercaria → Skin → Portal vein → Eggs"}
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": {"fr": "Absence d'elements parasitaires.", "ar": "غياب عناصر طفيلية.", "en": "No parasitic elements."},
        "description": {"fr": "Echantillon negatif.", "ar": "عينة سلبية.", "en": "Negative sample."},
        "funny": {"fr": "Rien a signaler ! Champagne ! 🥂", "ar": "لا شيء! شمبانيا! 🥂", "en": "All clear! Champagne! 🥂"},
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {"fr": "RAS. Bonne hygiene.", "ar": "لا شيء. نظافة جيدة.", "en": "All clear. Good hygiene."},
        "extra_tests": {"fr": ["Aucun"], "ar": ["لا حاجة"], "en": ["None needed"]},
        "color": "#16a34a", "icon": "🟢",
        "lifecycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"}
    }
}

# ============================================
#  LABEL MAPPING: labels.txt → PARASITE_DB
# ============================================
LABEL_MAP = {
    "amoeba": "Amoeba (E. histolytica)",
    "giardia": "Giardia",
    "leishmania": "Leishmania",
    "plasmodium": "Plasmodium",
    "trypanosoma": "Trypanosoma",
    "schistosoma": "Schistosoma",
    "negative": "Negative",
}

# ============================================
#  TRANSLATIONS
# ============================================
TRANSLATIONS = {
    "fr": {
        "app_title": "DM SMART LAB AI", "app_subtitle": "Où la Science Rencontre l'Intelligence",
        "login_title": "Connexion Sécurisée", "login_subtitle": "Personnel Médical",
        "login_user": "Identifiant", "login_pass": "Mot de Passe", "login_btn": "CONNEXION",
        "login_error": "Mot de passe incorrect", "login_locked": "Compte verrouillé",
        "login_attempts": "tentative(s) restante(s)", "logout": "Déconnexion",
        "nav_home": "Accueil", "nav_scan": "Scan & Analyse", "nav_encyclopedia": "Encyclopédie",
        "nav_dashboard": "Tableau de Bord", "nav_about": "À Propos",
        "nav_quiz": "Quiz", "nav_chatbot": "Dr. DhiaBot",
        "home_step1_title": "Étape 1 : Présentation", "home_step1_desc": "Lancez la présentation vocale.",
        "home_step1_btn": "LANCER", "home_step2_title": "Étape 2 : Titre du Mémoire",
        "home_step2_desc": "Écoutez le titre.", "home_step2_btn": "LIRE",
        "home_unlocked": "SYSTÈME DÉVERROUILLÉ !", "home_go_scan": "Passez au diagnostic.",
        "scan_title": "Diagnostic Parasitologique", "scan_blocked": "Activez d'abord le système.",
        "scan_patient_info": "Patient", "scan_nom": "Nom", "scan_prenom": "Prénom",
        "scan_age": "Âge", "scan_sexe": "Sexe", "scan_poids": "Poids (kg)",
        "scan_echantillon": "Échantillon", "scan_thermal": "Thermique",
        "scan_edge": "Contours", "scan_enhanced": "Contraste", "scan_capture": "Capture",
        "scan_camera": "Caméra", "scan_upload": "Importer",
        "scan_nom_required": "Nom obligatoire !", "scan_analyzing": "Analyse IA...",
        "scan_result": "Résultat IA", "scan_confidence": "Confiance",
        "scan_morphology": "Morphologie", "scan_risk": "Risque", "scan_advice": "Conseil",
        "scan_low_conf": "Confiance faible !", "scan_download_pdf": "PDF",
        "scan_save": "Sauvegarder", "scan_saved": "Sauvegardé !",
        "scan_new": "Nouvelle Analyse", "scan_all_probs": "Toutes les probabilités",
        "scan_extra_tests": "Examens complémentaires", "scan_heatmap": "Zone IA",
        "enc_title": "Encyclopédie", "enc_search": "Rechercher...", "enc_no_result": "Aucun résultat.",
        "dash_title": "Tableau de Bord", "dash_total": "Total", "dash_reliable": "Fiables",
        "dash_check": "À Vérifier", "dash_frequent": "Fréquent", "dash_system": "Système OK",
        "dash_filter": "Filtrer", "dash_distribution": "Distribution",
        "dash_confidence_chart": "Confiance", "dash_history": "Historique",
        "dash_export": "CSV", "dash_export_json": "JSON", "dash_export_excel": "Excel",
        "dash_no_data": "Aucune donnée", "dash_no_data_desc": "Effectuez une analyse.",
        "dash_patient_compare": "Comparer patient",
        "about_title": "À Propos", "about_desc": "Système IA Parasitologique",
        "about_project_desc": "Deep Learning pour assister les techniciens de laboratoire.",
        "about_team": "Équipe", "about_institution": "Établissement",
        "about_objectives": "Objectifs", "about_obj1": "Automatiser la lecture",
        "about_obj2": "Réduire les erreurs", "about_obj3": "Accélérer l'analyse",
        "about_obj4": "Assister les professionnels", "about_tech": "Technologies",
        "night_mode": "Mode Nuit", "language": "Langue",
        "patient_sexe_h": "Homme", "patient_sexe_f": "Femme",
        "echantillon_selles": "Selles", "echantillon_sang_frottis": "Sang (Frottis)",
        "echantillon_sang_goutte": "Sang (Goutte épaisse)", "echantillon_urines": "Urines",
        "echantillon_lcr": "LCR", "echantillon_autre": "Autre",
        "voice_intro": "Bonjour ! Il est {time}. Je suis DM Smart Lab, développée par {dev1} et {dev2}.",
        "voice_title": "Mémoire : {title}. INFSPM Ouargla.",
        "voice_result": "Résultat pour {patient} : {parasite}. {funny}",
        "quiz_title": "Quiz", "quiz_desc": "Testez vos connaissances !",
        "quiz_question": "Question", "quiz_correct": "Correct !", "quiz_wrong": "Faux.",
        "quiz_next": "Suivante", "quiz_finish": "Résultat", "quiz_restart": "Recommencer",
        "chatbot_title": "Dr. DhiaBot", "chatbot_placeholder": "Question...",
        "daily_tip": "Conseil du Jour", "activity_log": "Journal",
        "pdf_title": "RAPPORT PARASITOLOGIQUE", "pdf_subtitle": "Analyse IA",
        "pdf_patient_section": "PATIENT", "pdf_result_section": "RESULTAT",
        "pdf_advice_section": "RECOMMANDATIONS", "pdf_validation": "VALIDATION",
        "pdf_technician": "Technicien", "pdf_disclaimer": "Rapport genere par IA.",
        "model_loaded": "✅ Modèle IA chargé: {name} — Résultats RÉELS",
        "model_demo": "⚠️ Aucun modèle — Mode DEMO (résultats aléatoires)",
        "model_error": "❌ Erreur modèle: {error}",
    },
    "ar": {
        "app_title": "DM SMART LAB AI", "app_subtitle": "حيث يلتقي العلم بالذكاء",
        "login_title": "تسجيل الدخول", "login_subtitle": "للكوادر الطبية",
        "login_user": "المستخدم", "login_pass": "كلمة المرور", "login_btn": "دخول",
        "login_error": "كلمة مرور خاطئة", "login_locked": "الحساب مقفل",
        "login_attempts": "محاولة متبقية", "logout": "خروج",
        "nav_home": "الرئيسية", "nav_scan": "الفحص", "nav_encyclopedia": "الموسوعة",
        "nav_dashboard": "لوحة التحكم", "nav_about": "حول",
        "nav_quiz": "اختبار", "nav_chatbot": "المساعد",
        "home_step1_title": "الخطوة 1", "home_step1_desc": "اضغط للعرض.",
        "home_step1_btn": "بدء", "home_step2_title": "الخطوة 2",
        "home_step2_desc": "استمع للعنوان.", "home_step2_btn": "قراءة",
        "home_unlocked": "تم فتح النظام !", "home_go_scan": "انتقل للتشخيص.",
        "scan_title": "وحدة التشخيص", "scan_blocked": "فعّل النظام أولاً.",
        "scan_patient_info": "المريض", "scan_nom": "اللقب", "scan_prenom": "الاسم",
        "scan_age": "العمر", "scan_sexe": "الجنس", "scan_poids": "الوزن",
        "scan_echantillon": "العينة", "scan_thermal": "حرارية",
        "scan_edge": "حواف", "scan_enhanced": "تباين", "scan_capture": "تصوير",
        "scan_camera": "كاميرا", "scan_upload": "استيراد",
        "scan_nom_required": "الاسم إجباري !", "scan_analyzing": "جاري التحليل...",
        "scan_result": "النتيجة", "scan_confidence": "الثقة",
        "scan_morphology": "المورفولوجيا", "scan_risk": "الخطورة", "scan_advice": "النصيحة",
        "scan_low_conf": "ثقة منخفضة !", "scan_download_pdf": "PDF",
        "scan_save": "حفظ", "scan_saved": "تم الحفظ !",
        "scan_new": "تحليل جديد", "scan_all_probs": "كل الاحتمالات",
        "scan_extra_tests": "فحوصات إضافية", "scan_heatmap": "منطقة الاهتمام",
        "enc_title": "الموسوعة", "enc_search": "ابحث...", "enc_no_result": "لا نتائج.",
        "dash_title": "لوحة التحكم", "dash_total": "الإجمالي", "dash_reliable": "موثوقة",
        "dash_check": "تحتاج مراجعة", "dash_frequent": "الأكثر", "dash_system": "النظام يعمل",
        "dash_filter": "تصفية", "dash_distribution": "التوزيع",
        "dash_confidence_chart": "الثقة", "dash_history": "السجل",
        "dash_export": "CSV", "dash_export_json": "JSON", "dash_export_excel": "Excel",
        "dash_no_data": "لا بيانات", "dash_no_data_desc": "قم بتحليل.",
        "dash_patient_compare": "مقارنة مريض",
        "about_title": "حول", "about_desc": "نظام تشخيص بالذكاء الاصطناعي",
        "about_project_desc": "تعلم عميق لمساعدة تقنيي المخابر.",
        "about_team": "الفريق", "about_institution": "المؤسسة",
        "about_objectives": "الأهداف", "about_obj1": "أتمتة القراءة",
        "about_obj2": "تقليل الأخطاء", "about_obj3": "تسريع التحليل",
        "about_obj4": "مساعدة المهنيين", "about_tech": "التقنيات",
        "night_mode": "ليلي", "language": "اللغة",
        "patient_sexe_h": "ذكر", "patient_sexe_f": "أنثى",
        "echantillon_selles": "براز", "echantillon_sang_frottis": "دم (لطاخة)",
        "echantillon_sang_goutte": "دم (قطرة)", "echantillon_urines": "بول",
        "echantillon_lcr": "سائل شوكي", "echantillon_autre": "أخرى",
        "voice_intro": "مرحباً! الساعة {time}. أنا DM Smart Lab.",
        "voice_title": "مذكرة: {title}.",
        "voice_result": "النتيجة: {parasite}. {funny}",
        "quiz_title": "اختبار", "quiz_desc": "اختبر معلوماتك!",
        "quiz_question": "سؤال", "quiz_correct": "صحيح!", "quiz_wrong": "خطأ.",
        "quiz_next": "التالي", "quiz_finish": "النتيجة", "quiz_restart": "إعادة",
        "chatbot_title": "المساعد", "chatbot_placeholder": "اسأل...",
        "daily_tip": "نصيحة اليوم", "activity_log": "السجل",
        "pdf_title": "تقرير التحليل", "pdf_subtitle": "ذكاء اصطناعي",
        "pdf_patient_section": "المريض", "pdf_result_section": "النتيجة",
        "pdf_advice_section": "التوصيات", "pdf_validation": "المصادقة",
        "pdf_technician": "التقني", "pdf_disclaimer": "تقرير بالذكاء الاصطناعي.",
        "model_loaded": "✅ تم تحميل النموذج: {name} — نتائج حقيقية",
        "model_demo": "⚠️ لا يوجد نموذج — وضع تجريبي (نتائج عشوائية)",
        "model_error": "❌ خطأ: {error}",
    },
    "en": {
        "app_title": "DM SMART LAB AI", "app_subtitle": "Where Science Meets Intelligence",
        "login_title": "Secure Login", "login_subtitle": "Medical Staff Only",
        "login_user": "Username", "login_pass": "Password", "login_btn": "LOG IN",
        "login_error": "Wrong password", "login_locked": "Account locked",
        "login_attempts": "attempt(s) left", "logout": "Log Out",
        "nav_home": "Home", "nav_scan": "Scan", "nav_encyclopedia": "Encyclopedia",
        "nav_dashboard": "Dashboard", "nav_about": "About",
        "nav_quiz": "Quiz", "nav_chatbot": "Dr. DhiaBot",
        "home_step1_title": "Step 1: Presentation", "home_step1_desc": "Launch voice presentation.",
        "home_step1_btn": "LAUNCH", "home_step2_title": "Step 2: Project Title",
        "home_step2_desc": "Listen to title.", "home_step2_btn": "READ",
        "home_unlocked": "SYSTEM UNLOCKED!", "home_go_scan": "Go to diagnostic.",
        "scan_title": "Parasitological Diagnostic", "scan_blocked": "Activate system first.",
        "scan_patient_info": "Patient", "scan_nom": "Last Name", "scan_prenom": "First Name",
        "scan_age": "Age", "scan_sexe": "Sex", "scan_poids": "Weight (kg)",
        "scan_echantillon": "Sample", "scan_thermal": "Thermal",
        "scan_edge": "Edges", "scan_enhanced": "Enhanced", "scan_capture": "Capture",
        "scan_camera": "Camera", "scan_upload": "Upload",
        "scan_nom_required": "Name required!", "scan_analyzing": "AI Analyzing...",
        "scan_result": "AI Result", "scan_confidence": "Confidence",
        "scan_morphology": "Morphology", "scan_risk": "Risk", "scan_advice": "Advice",
        "scan_low_conf": "Low confidence!", "scan_download_pdf": "PDF",
        "scan_save": "Save", "scan_saved": "Saved!",
        "scan_new": "New Analysis", "scan_all_probs": "All probabilities",
        "scan_extra_tests": "Additional tests", "scan_heatmap": "AI Focus",
        "enc_title": "Encyclopedia", "enc_search": "Search...", "enc_no_result": "No results.",
        "dash_title": "Dashboard", "dash_total": "Total", "dash_reliable": "Reliable",
        "dash_check": "To Verify", "dash_frequent": "Frequent", "dash_system": "System OK",
        "dash_filter": "Filter", "dash_distribution": "Distribution",
        "dash_confidence_chart": "Confidence", "dash_history": "History",
        "dash_export": "CSV", "dash_export_json": "JSON", "dash_export_excel": "Excel",
        "dash_no_data": "No data", "dash_no_data_desc": "Run an analysis.",
        "dash_patient_compare": "Compare patient",
        "about_title": "About", "about_desc": "AI Diagnostic System",
        "about_project_desc": "Deep Learning to assist lab technicians.",
        "about_team": "Team", "about_institution": "Institution",
        "about_objectives": "Objectives", "about_obj1": "Automate reading",
        "about_obj2": "Reduce errors", "about_obj3": "Speed up analysis",
        "about_obj4": "Assist professionals", "about_tech": "Technologies",
        "night_mode": "Night Mode", "language": "Language",
        "patient_sexe_h": "Male", "patient_sexe_f": "Female",
        "echantillon_selles": "Stool", "echantillon_sang_frottis": "Blood (Smear)",
        "echantillon_sang_goutte": "Blood (Thick)", "echantillon_urines": "Urine",
        "echantillon_lcr": "CSF", "echantillon_autre": "Other",
        "voice_intro": "Hello! It is {time}. I am DM Smart Lab.",
        "voice_title": "Thesis: {title}.",
        "voice_result": "Result: {parasite}. {funny}",
        "quiz_title": "Quiz", "quiz_desc": "Test your knowledge!",
        "quiz_question": "Question", "quiz_correct": "Correct!", "quiz_wrong": "Wrong.",
        "quiz_next": "Next", "quiz_finish": "Result", "quiz_restart": "Restart",
        "chatbot_title": "Dr. DhiaBot", "chatbot_placeholder": "Ask...",
        "daily_tip": "Daily Tip", "activity_log": "Activity Log",
        "pdf_title": "PARASITOLOGICAL REPORT", "pdf_subtitle": "AI Analysis",
        "pdf_patient_section": "PATIENT", "pdf_result_section": "RESULT",
        "pdf_advice_section": "RECOMMENDATIONS", "pdf_validation": "VALIDATION",
        "pdf_technician": "Technician", "pdf_disclaimer": "AI-generated report.",
        "model_loaded": "✅ AI Model loaded: {name} — REAL results",
        "model_demo": "⚠️ No model — DEMO mode (random results)",
        "model_error": "❌ Model error: {error}",
    }
}

QUIZ_QUESTIONS = {
    "fr": [
        {"q": "Quel parasite montre une 'bague a chaton' dans les hematies?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Le Plasmodium forme un anneau dans les hematies."},
        {"q": "Combien de noyaux dans le kyste de Giardia?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "Le kyste mature de Giardia a 4 noyaux."},
        {"q": "Quel parasite est transmis par le phlebotome?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania est transmise par le phlebotome."},
        {"q": "L'eperon terminal est chez quel oeuf?", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "S. haematobium a un eperon terminal."},
        {"q": "Examen urgent pour le paludisme?", "options": ["Coproculture", "ECBU", "Goutte epaisse + Frottis", "Serologie"], "answer": 2, "explanation": "Goutte epaisse et frottis sanguin."},
    ],
    "ar": [
        {"q": "أي طفيلي يظهر بشكل 'خاتم' في كريات الدم؟", "options": ["جيارديا", "بلازموديوم", "ليشمانيا", "أميبا"], "answer": 1, "explanation": "البلازموديوم يشكل حلقة في الكريات."},
        {"q": "كم نواة في كيس الجيارديا؟", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "كيس الجيارديا الناضج 4 نوى."},
        {"q": "أي طفيلي ينتقل بذبابة الرمل؟", "options": ["بلازموديوم", "تريبانوسوما", "ليشمانيا", "بلهارسيا"], "answer": 2, "explanation": "الليشمانيا تنتقل بالفليبوتوم."},
    ],
    "en": [
        {"q": "Which parasite shows a 'signet ring' in RBCs?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Plasmodium forms a ring inside RBCs."},
        {"q": "How many nuclei in a Giardia cyst?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "Mature Giardia cyst has 4 nuclei."},
        {"q": "Which parasite is transmitted by sandfly?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania is transmitted by sandfly."},
    ]
}

CHATBOT_KB = {
    "fr": {
        "keywords": {"amoeba": "Entamoeba histolytica: dysenterie amibienne. Traitement: Metronidazole.", "amibe": "Entamoeba histolytica: dysenterie amibienne. Traitement: Metronidazole.", "giardia": "Giardia lamblia: malabsorption. Traitement: Metronidazole.", "leishmania": "Leishmania: phlebotome. Traitement: Glucantime.", "plasmodium": "URGENCE! Paludisme. Traitement: ACT.", "malaria": "URGENCE! Paludisme. Traitement: ACT.", "paludisme": "URGENCE! Paludisme. Traitement: ACT.", "trypanosoma": "Maladie du sommeil/Chagas.", "schistosoma": "Bilharziose. Traitement: Praziquantel.", "bonjour": "Bonjour! Comment puis-je vous aider?", "microscope": "Objectif x10 reperage, x40 identification, x100 immersion."},
        "default": "Je connais: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma.",
        "greeting": "Bonjour! Je suis Dr. DhiaBot 🤖"
    },
    "ar": {
        "keywords": {"أميبا": "الأميبا: زحار أميبي. علاج: ميترونيدازول.", "جيارديا": "الجيارديا: سوء امتصاص. علاج: ميترونيدازول.", "ليشمانيا": "الليشمانيا: ذبابة الرمل. علاج: غلوكانتيم.", "ملاريا": "طوارئ! الملاريا. علاج: ACT.", "بلهارسيا": "البلهارسيا. علاج: برازيكوانتيل.", "مرحبا": "مرحباً! كيف أساعدك؟"},
        "default": "أعرف: أميبا، جيارديا، ليشمانيا، بلازموديوم، تريبانوسوما، بلهارسيا.",
        "greeting": "مرحباً! أنا الدكتور ضياء بوت 🤖"
    },
    "en": {
        "keywords": {"amoeba": "E. histolytica: amoebic dysentery. Treatment: Metronidazole.", "giardia": "Giardia: malabsorption. Treatment: Metronidazole.", "leishmania": "Leishmania: sandfly. Treatment: Glucantime.", "plasmodium": "EMERGENCY! Malaria. Treatment: ACT.", "malaria": "EMERGENCY! Malaria. Treatment: ACT.", "schistosoma": "Schistosomiasis. Treatment: Praziquantel.", "hello": "Hello! How can I help?"},
        "default": "I know: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma.",
        "greeting": "Hello! I'm Dr. DhiaBot 🤖"
    }
}

DAILY_TIPS = {
    "fr": ["💡 Examiner les selles dans les 30 min.", "💡 Lugol pour les noyaux des kystes.", "💡 Frottis fin pour identifier Plasmodium.", "💡 Goutte epaisse 10x plus sensible.", "💡 3 EPS a quelques jours d'intervalle."],
    "ar": ["💡 افحص البراز خلال 30 دقيقة.", "💡 اللوغول لإظهار النوى.", "💡 لطاخة رقيقة للبلازموديوم.", "💡 القطرة السميكة أكثر حساسية 10 مرات."],
    "en": ["💡 Examine stool within 30 min.", "💡 Lugol for cyst nuclei.", "💡 Thin smear for Plasmodium.", "💡 Thick smear 10x more sensitive."]
}

# ============================================
#  SESSION STATE
# ============================================
DEFAULTS = {
    "logged_in": False, "user_name": "", "intro_step": 0, "history": [],
    "dark_mode": False, "login_attempts": 0, "lockout_until": None,
    "lang": "fr", "activity_log": [],
    "quiz_state": {"current": 0, "score": 0, "answered": [], "active": False},
    "chat_history": [], "last_activity": None,
    "splash_shown": False, "balloons_shown": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================
#  HELPER FUNCTIONS
# ============================================
def t(key):
    lang = st.session_state.get("lang", "fr")
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, TRANSLATIONS["fr"].get(key, key))

def get_p_text(data, field):
    lang = st.session_state.get("lang", "fr")
    val = data.get(field, {})
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", ""))
    return val if not isinstance(val, list) else val

def get_greeting():
    h = datetime.now().hour
    lang = st.session_state.get("lang", "fr")
    g = {"fr": ("Bonjour", "Bon après-midi", "Bonsoir"), "ar": ("صباح الخير", "مساء الخير", "مساء الخير"), "en": ("Good morning", "Good afternoon", "Good evening")}.get(lang, ("Bonjour", "Bon après-midi", "Bonsoir"))
    return g[0] if h < 12 else g[1] if h < 18 else g[2]

def risk_color(level):
    return {"critical": "#7f1d1d", "high": "#dc2626", "medium": "#f59e0b", "none": "#16a34a"}.get(level, "#6b7280")

def risk_percent(level):
    return {"critical": 100, "high": 80, "medium": 50, "none": 0}.get(level, 0)

def log_activity(action):
    st.session_state.activity_log.append({"time": datetime.now().strftime("%H:%M:%S"), "user": st.session_state.user_name, "action": action})
    st.session_state.last_activity = datetime.now()

def check_auto_lock():
    if st.session_state.last_activity and (datetime.now() - st.session_state.last_activity).total_seconds() / 60 > AUTO_LOCK_MINUTES:
        st.session_state.logged_in = False
        st.session_state.intro_step = 0
        st.rerun()

def speak(text, lang_code=None):
    if lang_code is None:
        lang_code = st.session_state.get("lang", "fr")
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang=lang_code)
        fname = f"_audio_{int(time.time())}.mp3"
        tts.save(fname)
        with open(fname, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
        try: os.remove(fname)
        except: pass
    except:
        safe = text.replace("'", "\\'").replace('\n', ' ')
        js_lang = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(lang_code, "fr-FR")
        st.markdown(f"<script>try{{var m=new SpeechSynthesisUtterance('{safe}');m.lang='{js_lang}';speechSynthesis.speak(m);}}catch(e){{}}</script>", unsafe_allow_html=True)

def chatbot_reply(msg):
    lang = st.session_state.get("lang", "fr")
    kb = CHATBOT_KB.get(lang, CHATBOT_KB["fr"])
    ml = msg.lower().strip()
    for kw, resp in kb["keywords"].items():
        if kw in ml:
            return resp
    for name, data in PARASITE_DB.items():
        if name == "Negative": continue
        if name.lower() in ml or data["scientific_name"].lower() in ml:
            return f"**{name}** ({data['scientific_name']})\n{get_p_text(data, 'description')}\n💊 {get_p_text(data, 'advice')}"
    return kb["default"]

def generate_heatmap_overlay(image):
    img = image.copy()
    w, h = img.size
    rng = random.Random(42)
    heatmap = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(heatmap)
    cx, cy = w // 2 + rng.randint(-w // 6, w // 6), h // 2 + rng.randint(-h // 6, h // 6)
    max_r = min(w, h) // 3
    for r in range(max_r, 0, -3):
        alpha = max(0, min(180, int(180 * (1 - r / max_r))))
        ratio = r / max_r
        color = (0, 255, 0, alpha // 3) if ratio > 0.6 else (255, 255, 0, alpha // 2) if ratio > 0.3 else (255, 0, 0, alpha)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    return Image.alpha_composite(img.convert('RGBA'), heatmap).convert('RGB')

def apply_thermal(image):
    return ImageOps.colorize(ImageOps.grayscale(ImageEnhance.Contrast(image).enhance(1.5)).filter(ImageFilter.GaussianBlur(1)), black="navy", white="yellow", mid="red")

def apply_edge(image):
    return ImageOps.grayscale(image).filter(ImageFilter.FIND_EDGES)

def apply_enhance(image):
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(image).enhance(2.0)).enhance(2.0)


# ============================================
#  ✅✅✅ AI ENGINE — THE FIX
# ============================================
@st.cache_resource(show_spinner="🧠 Chargement du modèle IA...")
def load_ai_model():
    """Load Teachable Machine model"""
    try:
        import tensorflow as tf
        tf.get_logger().setLevel('ERROR')
    except ImportError:
        return None, None, "TensorFlow not installed"

    # Search for model file
    model_file = None
    for candidate in ["keras_model.h5", "model.h5"]:
        if os.path.exists(candidate):
            model_file = candidate
            break
    if model_file is None:
        for f in os.listdir("."):
            if f.endswith((".h5", ".keras")):
                model_file = f
                break
    if model_file is None:
        return None, None, "No model file found in directory"

    try:
        model = tf.keras.models.load_model(model_file, compile=False)
        return model, model_file, None
    except Exception as e:
        return None, model_file, str(e)


def load_class_names():
    """Load and map labels from labels.txt"""
    labels = []
    if os.path.exists("labels.txt"):
        with open("labels.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(" ", 1)
                if len(parts) == 2 and parts[0].isdigit():
                    labels.append(parts[1].strip())
                else:
                    labels.append(line.strip())

    if not labels:
        return list(PARASITE_DB.keys())

    # Map short names to PARASITE_DB keys
    mapped = []
    for label in labels:
        ll = label.lower().strip()
        if ll in LABEL_MAP:
            mapped.append(LABEL_MAP[ll])
        else:
            found = False
            for key, val in LABEL_MAP.items():
                if key in ll or ll in key:
                    mapped.append(val)
                    found = True
                    break
            if not found:
                for db_name in PARASITE_DB:
                    if ll in db_name.lower():
                        mapped.append(db_name)
                        found = True
                        break
            if not found:
                mapped.append(label)
    return mapped


def do_prediction(model, image):
    """✅ THE MAIN PREDICTION FUNCTION"""
    class_names = load_class_names()

    # === NO MODEL → DEMO ===
    if model is None:
        idx = random.randint(0, len(class_names) - 1)
        label = class_names[idx]
        conf = random.randint(55, 92)
        all_p = {cn: round(random.uniform(1, 12), 1) for cn in class_names}
        all_p[label] = float(conf)
        return {
            "label": label, "confidence": conf, "all_predictions": all_p,
            "is_reliable": conf >= CONFIDENCE_THRESHOLD, "is_demo": True,
            "info": PARASITE_DB.get(label, PARASITE_DB["Negative"])
        }

    # === REAL PREDICTION ===
    try:
        # Get input size from model
        input_shape = model.input_shape
        if isinstance(input_shape, list):
            input_shape = input_shape[0]
        h = input_shape[1] if input_shape[1] else 224
        w = input_shape[2] if input_shape[2] else 224

        # Preprocess EXACTLY like Teachable Machine
        img = image.convert("RGB")
        img = ImageOps.fit(img, (w, h), Image.LANCZOS)
        img_array = np.asarray(img, dtype=np.float32)
        img_array = (img_array / 127.5) - 1.0
        batch = np.expand_dims(img_array, axis=0)

        # Predict
        preds = model.predict(batch, verbose=0)[0]
        preds = np.array(preds, dtype=np.float64)

        # Check if softmax needed
        if abs(np.sum(preds) - 1.0) > 0.05:
            exp_p = np.exp(preds - np.max(preds))
            preds = exp_p / np.sum(exp_p)

        preds = np.clip(preds, 0, 1)

        # Extract result
        num_c = min(len(preds), len(class_names))
        best_idx = int(np.argmax(preds[:num_c]))
        best_conf = round(float(preds[best_idx]) * 100, 1)
        best_label = class_names[best_idx]

        all_p = {}
        for i in range(num_c):
            all_p[class_names[i]] = round(float(preds[i]) * 100, 1)

        return {
            "label": best_label, "confidence": int(best_conf),
            "all_predictions": all_p,
            "is_reliable": best_conf >= CONFIDENCE_THRESHOLD, "is_demo": False,
            "info": PARASITE_DB.get(best_label, PARASITE_DB["Negative"])
        }
    except Exception as e:
        st.error(f"❌ Prediction error: {e}")
        import traceback
        st.code(traceback.format_exc())
        return {
            "label": "Negative", "confidence": 0, "all_predictions": {},
            "is_reliable": False, "is_demo": True,
            "info": PARASITE_DB["Negative"]
        }


# ============================================
#  PDF
# ============================================
def _safe(text):
    if not text: return ""
    reps = {'é':'e','è':'e','ê':'e','ë':'e','à':'a','â':'a','ù':'u','û':'u','ô':'o','î':'i','ç':'c','É':'E','È':'E','À':'A','Ç':'C','→':'->','←':'<-','🔴':'[!]','🟠':'[!]','🟢':'[OK]','🚨':'[!!!]'}
    for o, r in reps.items():
        text = text.replace(o, r)
    return ''.join(c if ord(c) < 256 else '?' for c in text)

class MedPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 10); self.set_text_color(37, 99, 235)
        self.cell(0, 6, "DM SMART LAB AI", 0, 0, "L")
        self.set_font("Arial", "", 9); self.set_text_color(100, 116, 139)
        self.cell(0, 6, datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 1, "R")
        self.line(10, 15, 200, 15); self.ln(8)
    def footer(self):
        self.set_y(-15); self.set_font("Arial", "I", 8); self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"DM Smart Lab AI v{APP_VERSION} - Page {self.page_no()}", 0, 0, "C")
    def section(self, title):
        self.set_fill_color(37, 99, 235); self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 11); self.cell(0, 8, f"  {_safe(title)}", 0, 1, "L", True)
        self.ln(3); self.set_text_color(0, 0, 0)

def generate_pdf(patient, label, conf, info):
    pdf = MedPDF(); pdf.set_auto_page_break(True, 25); pdf.add_page()
    pdf.set_font("Arial", "B", 16); pdf.set_text_color(37, 99, 235)
    pdf.cell(0, 10, _safe(t("pdf_title")), 0, 1, "C"); pdf.ln(5)
    pdf.section(_safe(t("pdf_patient_section")))
    pdf.set_font("Arial", "", 10)
    for k, v in patient.items():
        pdf.cell(50, 7, _safe(k) + ":", 0, 0); pdf.cell(0, 7, _safe(str(v)), 0, 1)
    pdf.ln(5); pdf.section(_safe(t("pdf_result_section")))
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(22, 163, 74) if label == "Negative" else pdf.set_text_color(220, 38, 38)
    pdf.cell(0, 10, f"RESULTAT: {_safe(label)} ({conf}%)", 0, 1, "C")
    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 6, _safe(f"Morphologie: {get_p_text(info, 'morphology')}")); pdf.ln(3)
    pdf.section(_safe(t("pdf_advice_section")))
    pdf.set_font("Arial", "", 10); pdf.multi_cell(0, 6, _safe(get_p_text(info, "advice")))
    pdf.ln(10); pdf.set_font("Arial", "I", 8); pdf.set_text_color(150, 150, 150)
    pdf.multi_cell(0, 5, _safe(t("pdf_disclaimer")))
    return pdf.output(dest='S').encode('latin-1')


# ============================================
#  CSS THEME
# ============================================
def apply_theme():
    dm = st.session_state.get("dark_mode", False)
    if dm:
        bg, bg2, text, muted, border = "#050a15", "#0a1628", "#e2e8f0", "#64748b", "#1e3a5f"
        primary, accent = "#3b82f6", "#06b6d4"
        sidebar_bg, input_bg = "#030712", "#0f1d32"
        grad1, grad3 = "#0a1628", "#0f1d32"
        glass, glass_b = "rgba(15,29,50,0.85)", "rgba(59,130,246,0.15)"
        shadow = "rgba(0,0,0,0.5)"
    else:
        bg, bg2, text, muted, border = "#f0f4f8", "#ffffff", "#0f172a", "#64748b", "#e2e8f0"
        primary, accent = "#2563eb", "#0891b2"
        sidebar_bg, input_bg = "#f8fafc", "#ffffff"
        grad1, grad3 = "#dbeafe", "#e0f2fe"
        glass, glass_b = "rgba(255,255,255,0.9)", "rgba(37,99,235,0.12)"
        shadow = "rgba(0,0,0,0.06)"

    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    html,body,[class*="css"],p,span,label,div,li,td,th {{font-family:'Inter',sans-serif!important;color:{text}!important;}}
    h1,h2,h3,h4,h5,h6 {{color:{text}!important;}}
    .stApp {{background:radial-gradient(ellipse at 20% 50%,{grad1} 0%,transparent 50%),radial-gradient(ellipse at 80% 20%,{grad3} 0%,transparent 50%),linear-gradient(180deg,{bg} 0%,{bg2} 100%);background-attachment:fixed;}}
    section[data-testid="stSidebar"] {{background:linear-gradient(180deg,{sidebar_bg},{bg2})!important;}}
    section[data-testid="stSidebar"] * {{color:{text}!important;}}
    .dm-card {{background:{glass};backdrop-filter:blur(12px);border:1px solid {glass_b};border-radius:20px;padding:28px;margin:14px 0;box-shadow:0 4px 30px {shadow};position:relative;z-index:2;transition:all 0.4s ease;}}
    .dm-card:hover {{transform:translateY(-3px);}}
    .dm-card-blue {{border-left:4px solid {primary};}}
    .dm-card-green {{border-left:4px solid #22c55e;}}
    .dm-card-orange {{border-left:4px solid #f59e0b;}}
    .dm-card-purple {{border-left:4px solid #8b5cf6;}}
    .dm-metric {{background:{glass};border:1px solid {glass_b};border-radius:18px;padding:22px 16px;text-align:center;box-shadow:0 2px 16px {shadow};position:relative;overflow:hidden;}}
    .dm-metric::before {{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{primary},{accent});}}
    .dm-metric-icon {{font-size:1.8rem;margin-bottom:8px;display:block;}}
    .dm-metric-val {{font-size:2rem;font-weight:800;font-family:'JetBrains Mono',monospace!important;color:{primary}!important;}}
    .dm-metric-lbl {{font-size:0.78rem;font-weight:600;color:{muted}!important;text-transform:uppercase;letter-spacing:0.08em;margin-top:8px;}}
    div.stButton>button {{background:linear-gradient(135deg,{primary},#1d4ed8)!important;color:white!important;border:none!important;border-radius:14px!important;padding:13px 30px!important;font-weight:600!important;box-shadow:0 4px 15px rgba(37,99,235,0.3)!important;}}
    div.stButton>button:hover {{transform:translateY(-3px)!important;box-shadow:0 8px 28px rgba(37,99,235,0.45)!important;}}
    .stTextInput>div>div>input {{background:{input_bg}!important;border:2px solid {border}!important;border-radius:12px!important;color:{text}!important;}}
    .dm-step {{display:flex;align-items:center;gap:10px;padding:12px 18px;border-radius:12px;margin:6px 0;font-weight:600;}}
    .dm-step-done {{background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);color:#22c55e!important;}}
    .dm-step-active {{background:rgba(37,99,235,0.1);border:1px solid rgba(37,99,235,0.3);color:{primary}!important;}}
    .dm-step-pending {{background:rgba(100,116,139,0.05);border:1px solid rgba(100,116,139,0.15);color:{muted}!important;}}
    .dm-chat-msg {{padding:14px 18px;border-radius:16px;margin:8px 0;max-width:85%;line-height:1.6;}}
    .dm-chat-user {{background:linear-gradient(135deg,{primary},#1d4ed8);color:white!important;margin-left:auto;}}
    .dm-chat-user * {{color:white!important;}}
    .dm-chat-bot {{background:{glass};border:1px solid {glass_b};}}
    .dm-logo-wrap {{display:flex;flex-direction:column;align-items:center;padding:20px 0;z-index:5;position:relative;}}
    .dm-logo-main {{display:flex;align-items:center;gap:6px;}}
    .dm-logo-char {{font-size:3.5rem;font-weight:900;}}
    .dm-logo-d {{color:{primary};}}
    .dm-logo-m {{color:white;background:linear-gradient(135deg,{primary},{accent});padding:6px 18px;border-radius:14px;}}
    .dm-logo-tag {{font-size:0.8rem;font-weight:600;color:{muted};letter-spacing:0.35em;text-transform:uppercase;margin-top:8px;}}
    </style>""", unsafe_allow_html=True)

apply_theme()

# ============================================
#  SPLASH + AUTO LOCK
# ============================================
if not st.session_state.splash_shown:
    st.markdown("""<div style="position:fixed;top:0;left:0;right:0;bottom:0;background:#050a15;z-index:9999;display:flex;flex-direction:column;justify-content:center;align-items:center;animation:splashFade 0.5s ease 2.5s forwards;"><div style="font-size:5rem;animation:pulse 1.5s infinite;">🧬</div><h2 style="color:#e2e8f0;margin-top:16px;">DM SMART LAB AI</h2></div><style>@keyframes splashFade{to{opacity:0;pointer-events:none;}}@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.15);}}</style>""", unsafe_allow_html=True)
    st.session_state.splash_shown = True

if st.session_state.logged_in:
    check_auto_lock()

st.markdown("""<div class="dm-logo-wrap"><div class="dm-logo-main"><span class="dm-logo-char dm-logo-d">D</span><span class="dm-logo-char dm-logo-m">M</span></div><div class="dm-logo-tag">Smart Lab AI</div></div>""", unsafe_allow_html=True)

# ============================================
#  LOGIN
# ============================================
if not st.session_state.logged_in:
    if st.session_state.lockout_until:
        if datetime.now() < st.session_state.lockout_until:
            st.error(f"⏳ {t('login_locked')}. {(st.session_state.lockout_until - datetime.now()).seconds}s")
            st.stop()
        else:
            st.session_state.lockout_until = None
            st.session_state.login_attempts = 0

    _, col, _ = st.columns([1.2, 2, 1.2])
    with col:
        st.markdown(f"<div class='dm-card dm-card-blue' style='text-align:center;'><div style='font-size:3rem;'>🔐</div><h2>{t('login_title')}</h2><p style='opacity:0.6;'>{t('login_subtitle')}</p></div>", unsafe_allow_html=True)
        lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
        sl = st.selectbox(f"🌍 {t('language')}", list(lang_opts.keys()), index=list(lang_opts.values()).index(st.session_state.lang))
        if lang_opts[sl] != st.session_state.lang:
            st.session_state.lang = lang_opts[sl]; st.rerun()
        with st.form("login"):
            user = st.text_input(f"👤 {t('login_user')}")
            pwd = st.text_input(f"🔒 {t('login_pass')}", type="password")
            if st.form_submit_button(f"🔓 {t('login_btn')}", use_container_width=True):
                if pwd == APP_PASSWORD:
                    st.session_state.logged_in = True
                    st.session_state.user_name = user.strip() or "User"
                    st.session_state.login_attempts = 0
                    st.session_state.last_activity = datetime.now()
                    log_activity("Login"); st.rerun()
                else:
                    st.session_state.login_attempts += 1
                    left = MAX_LOGIN_ATTEMPTS - st.session_state.login_attempts
                    if left <= 0:
                        st.session_state.lockout_until = datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)
                        st.error(f"🔒 {t('login_locked')}")
                    else:
                        st.error(f"❌ {t('login_error')}. {left} {t('login_attempts')}")
    st.stop()

# ============================================
#  SIDEBAR
# ============================================
with st.sidebar:
    st.markdown(f"<div style='text-align:center;'><div style='font-size:2.5rem;'>🧬</div><h3>DM SMART LAB</h3><p style='font-size:0.7rem;opacity:0.4;'>v{APP_VERSION}</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"👤 **{st.session_state.user_name}**")
    lang = st.session_state.get("lang", "fr")
    tips = DAILY_TIPS.get(lang, DAILY_TIPS["fr"])
    st.info(f"**{t('daily_tip')}:**\n{tips[datetime.now().timetuple().tm_yday % len(tips)]}")
    st.markdown("---")
    lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
    sl = st.selectbox(f"🌍 {t('language')}", list(lang_opts.keys()), index=list(lang_opts.values()).index(st.session_state.lang), key="sb_lang")
    if lang_opts[sl] != st.session_state.lang:
        st.session_state.lang = lang_opts[sl]; st.rerun()
    st.markdown("---")
    nav = [f"🏠 {t('nav_home')}", f"🔬 {t('nav_scan')}", f"📘 {t('nav_encyclopedia')}", f"📊 {t('nav_dashboard')}", f"🧠 {t('nav_quiz')}", f"💬 {t('nav_chatbot')}", f"ℹ️ {t('nav_about')}"]
    menu = st.radio("📌", nav, label_visibility="collapsed")
    st.markdown("---")
    dark = st.toggle(f"🌙 {t('night_mode')}", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark; st.rerun()
    st.markdown("---")
    if st.button(f"🚪 {t('logout')}", use_container_width=True):
        log_activity("Logout")
        for k in DEFAULTS: st.session_state[k] = DEFAULTS[k]
        st.session_state.splash_shown = True; st.rerun()

st.session_state.last_activity = datetime.now()
pages = ["home", "scan", "encyclopedia", "dashboard", "quiz", "chatbot", "about"]
current = dict(zip(nav, pages)).get(menu, "home")

# ╔══════════════════════════════════╗
# ║            HOME                  ║
# ╚══════════════════════════════════╝
if current == "home":
    st.title(f"👋 {get_greeting()}, {st.session_state.user_name} !")
    c1, c2 = st.columns([1, 2.5])
    with c1: st.markdown('<div style="text-align:center;font-size:6rem;">🤖</div>', unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='dm-card dm-card-blue'><h3>🧬 DM SMART LAB — {t('app_subtitle')}</h3></div>", unsafe_allow_html=True)

    step = st.session_state.intro_step
    labels = [t("home_step1_title"), t("home_step2_title"), t("home_unlocked")]
    cols = st.columns(3)
    for i, lbl in enumerate(labels):
        with cols[i]:
            cls = "dm-step-done" if step > i else ("dm-step-active" if step == i else "dm-step-pending")
            ic = "✅" if step > i else ("⏳" if step == i else "⬜")
            st.markdown(f'<div class="dm-step {cls}">{ic} {lbl}</div>', unsafe_allow_html=True)

    if step == 0:
        st.markdown(f"<div class='dm-card dm-card-orange'><h4>🔒 {t('home_step1_title')}</h4><p>{t('home_step1_desc')}</p></div>", unsafe_allow_html=True)
        if st.button(f"🔊 {t('home_step1_btn')}", use_container_width=True, type="primary"):
            speak(t("voice_intro").format(time=datetime.now().strftime("%H:%M"), dev1=AUTHORS["dev1"]["name"], dev2=AUTHORS["dev2"]["name"]))
            with st.spinner("🔊 ..."): time.sleep(5)
            st.session_state.intro_step = 1; log_activity("Step 1"); st.rerun()
    elif step == 1:
        st.markdown(f"<div class='dm-card dm-card-orange'><h4>🔒 {t('home_step2_title')}</h4><p>{t('home_step2_desc')}</p></div>", unsafe_allow_html=True)
        if st.button(f"🔊 {t('home_step2_btn')}", use_container_width=True, type="primary"):
            speak(t("voice_title").format(title=PROJECT_TITLE))
            with st.spinner("🔊 ..."): time.sleep(5)
            st.session_state.intro_step = 2; log_activity("Step 2 - Unlocked"); st.rerun()
    elif step >= 2:
        st.markdown(f"<div class='dm-card dm-card-green'><h3>✅ {t('home_unlocked')}</h3><p>{t('home_go_scan')}</p></div>", unsafe_allow_html=True)
        if not st.session_state.get("balloons_shown"):
            st.balloons(); st.session_state.balloons_shown = True

# ╔══════════════════════════════════╗
# ║            SCAN                  ║
# ╚══════════════════════════════════╝
elif current == "scan":
    st.title(f"🔬 {t('scan_title')}")
    if st.session_state.intro_step < 2:
        st.error(f"⛔ {t('scan_blocked')}"); st.stop()

    # ✅ Load model
    model, model_name, model_error = load_ai_model()

    # ✅ Show model status CLEARLY
    if model is not None:
        st.sidebar.success(f"🧠 {model_name}")
        st.success(t("model_loaded").format(name=model_name))
    else:
        st.sidebar.error("❌ No model")
        st.error(t("model_demo"))
        if model_error:
            st.error(t("model_error").format(error=model_error))

    # Debug info
    with st.expander("🔧 Debug Info"):
        st.write(f"**Model loaded:** `{model is not None}`")
        st.write(f"**Model file:** `{model_name}`")
        st.write(f"**Error:** `{model_error}`")
        st.write(f"**Files in dir:** `{[f for f in os.listdir('.') if f.endswith(('.h5','.keras','.tflite','labels.txt'))]}`")
        if model is not None:
            st.write(f"**Input shape:** `{model.input_shape}`")
            st.write(f"**Output shape:** `{model.output_shape}`")
        class_names = load_class_names()
        st.write(f"**Class names:** `{class_names}`")
        if os.path.exists("labels.txt"):
            with open("labels.txt") as f:
                st.code(f.read(), language="text")

    # Patient info
    st.markdown(f"### 📋 {t('scan_patient_info')}")
    ca, cb = st.columns(2)
    p_nom = ca.text_input(f"{t('scan_nom')} *")
    p_prenom = cb.text_input(t("scan_prenom"))
    cc, cd, ce, cf = st.columns(4)
    p_age = cc.number_input(t("scan_age"), 0, 120, 30)
    p_sexe = cd.selectbox(t("scan_sexe"), [t("patient_sexe_h"), t("patient_sexe_f")])
    p_poids = ce.number_input(t("scan_poids"), 0, 300, 70)
    samples = [t("echantillon_selles"), t("echantillon_sang_frottis"), t("echantillon_sang_goutte"), t("echantillon_urines"), t("echantillon_lcr"), t("echantillon_autre")]
    p_type = cf.selectbox(t("scan_echantillon"), samples)

    st.markdown("---")
    st.markdown(f"### 📸 {t('scan_capture')}")
    mode = st.radio("", [f"📷 {t('scan_camera')}", f"📁 {t('scan_upload')}"], horizontal=True, label_visibility="collapsed")
    img_file = st.camera_input("cam") if t('scan_camera') in mode else st.file_uploader("img", type=["jpg", "jpeg", "png", "bmp", "tiff"])

    if img_file:
        if not p_nom.strip():
            st.error(f"⚠️ {t('scan_nom_required')}"); st.stop()

        image = Image.open(img_file).convert("RGB")
        ci, cr = st.columns(2)

        with ci:
            tabs = st.tabs(["📷 Original", "🔥 Thermal", "📐 Edges", "✨ Enhanced", "🎯 AI"])
            with tabs[0]: st.image(image, use_container_width=True)
            with tabs[1]: st.image(apply_thermal(image), use_container_width=True)
            with tabs[2]: st.image(apply_edge(image), use_container_width=True)
            with tabs[3]: st.image(apply_enhance(image), use_container_width=True)
            with tabs[4]: st.image(generate_heatmap_overlay(image), use_container_width=True)

        with cr:
            st.markdown(f"### 🧠 {t('scan_result')}")
            with st.spinner(t('scan_analyzing')):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.006); prog.progress(i + 1)
                result = do_prediction(model, image)

            label, conf, info = result["label"], result["confidence"], result["info"]
            rc = risk_color(info["risk_level"])

            if result["is_demo"]:
                st.error(f"🎲 MODE DEMO — {t('model_demo')}")
            else:
                st.success(f"🧠 RÉSULTAT RÉEL — {model_name}")

            if not result["is_reliable"]:
                st.warning(f"⚠️ {t('scan_low_conf')} ({conf}%)")

            risk_disp = get_p_text(info, "risk_display")
            morpho = get_p_text(info, "morphology")
            advice = get_p_text(info, "advice")
            funny = get_p_text(info, "funny")

            st.markdown(f"""<div class='dm-card' style='border-left:5px solid {rc};'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div><h2 style='color:{rc};margin:0;'>{label}</h2><p style='opacity:0.5;font-style:italic;'>{info['scientific_name']}</p></div>
                    <div style='text-align:center;'><div style='font-size:2.5rem;font-weight:900;color:{rc};font-family:JetBrains Mono,monospace;'>{conf}%</div><div style='font-size:0.7rem;opacity:0.4;'>{t('scan_confidence')}</div></div>
                </div>
                <hr style='opacity:0.15;margin:14px 0;'>
                <p><b>🔬 {t('scan_morphology')}:</b><br>{morpho}</p>
                <p><b>⚠️ {t('scan_risk')}:</b> <span style='color:{rc};font-weight:700;'>{risk_disp}</span></p>
                <div style='background:rgba(34,197,94,0.08);padding:12px;border-radius:12px;margin:10px 0;'><b>💡 {t('scan_advice')}:</b><br>{advice}</div>
                <div style='background:rgba(37,99,235,0.06);padding:12px;border-radius:12px;font-style:italic;'>🤖 {funny}</div>
            </div>""", unsafe_allow_html=True)

            if result["all_predictions"]:
                with st.expander(f"📊 {t('scan_all_probs')}"):
                    for cls, prob in sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True):
                        st.progress(min(prob / 100, 1.0), text=f"{cls}: {prob}%")

            extra = get_p_text(info, "extra_tests")
            if isinstance(extra, list):
                with st.expander(f"🩺 {t('scan_extra_tests')}"):
                    for test in extra: st.markdown(f"• {test}")

            lc = get_p_text(info, "lifecycle")
            if lc and lc != "N/A":
                with st.expander("🔄 Cycle"):
                    st.markdown(f"**{lc}**")

            speak(t("voice_result").format(patient=p_nom, parasite=label, funny=funny))

        st.markdown("---")
        a1, a2, a3 = st.columns(3)
        with a1:
            pat = {t("scan_nom"): p_nom, t("scan_prenom"): p_prenom, t("scan_age"): str(p_age), t("scan_sexe"): p_sexe, t("scan_poids"): str(p_poids), t("scan_echantillon"): p_type}
            try:
                pdf = generate_pdf(pat, label, conf, info)
                st.download_button(f"📥 {t('scan_download_pdf')}", pdf, f"Rapport_{p_nom}_{datetime.now().strftime('%Y%m%d')}.pdf", "application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"PDF: {e}")
        with a2:
            if st.button(f"💾 {t('scan_save')}", use_container_width=True):
                st.session_state.history.append({"Date": datetime.now().strftime("%Y-%m-%d %H:%M"), "Patient": f"{p_nom} {p_prenom}".strip(), "Age": p_age, "Parasite": label, "Confiance": f"{conf}%", "Mode": "🧠 IA" if not result["is_demo"] else "🎲 Demo", "Status": "Fiable" if result["is_reliable"] else "A verifier"})
                log_activity(f"Scan: {label} ({conf}%)"); st.success(f"✅ {t('scan_saved')}")
        with a3:
            if st.button(f"🔄 {t('scan_new')}", use_container_width=True): st.rerun()

# ╔══════════════════════════════════╗
# ║         ENCYCLOPEDIA             ║
# ╚══════════════════════════════════╝
elif current == "encyclopedia":
    st.title(f"📘 {t('enc_title')}")
    search = st.text_input(f"🔍 {t('enc_search')}")
    found = False
    for name, data in PARASITE_DB.items():
        if name == "Negative": continue
        if search.strip() and search.lower() not in (name + " " + data["scientific_name"]).lower(): continue
        found = True
        rc = risk_color(data["risk_level"])
        with st.expander(f"🔬 {name} — *{data['scientific_name']}*"):
            ci, cv = st.columns([3, 1])
            with ci:
                st.markdown(f"<div class='dm-card' style='border-left:4px solid {rc};'><h4 style='color:{rc};'>{data['scientific_name']}</h4><p><b>🔬 {t('scan_morphology')}:</b> {get_p_text(data,'morphology')}</p><p><b>📖</b> {get_p_text(data,'description')}</p><p><b>⚠️</b> {get_p_text(data,'risk_display')}</p><div style='background:rgba(22,163,74,0.08);padding:12px;border-radius:12px;margin:8px 0;'><b>💡</b> {get_p_text(data,'advice')}</div><div style='background:rgba(37,99,235,0.06);padding:12px;border-radius:12px;font-style:italic;'>🤖 {get_p_text(data,'funny')}</div></div>", unsafe_allow_html=True)
                lc = get_p_text(data, "lifecycle")
                if lc and lc != "N/A": st.markdown(f"**🔄** {lc}")
            with cv:
                rp = risk_percent(data["risk_level"])
                if rp > 0: st.progress(rp / 100)
                st.markdown(f'<div style="text-align:center;font-size:3.5rem;">{data.get("icon","🦠")}</div>', unsafe_allow_html=True)
    if search.strip() and not found:
        st.warning(t('enc_no_result'))

# ╔══════════════════════════════════╗
# ║          DASHBOARD               ║
# ╚══════════════════════════════════╝
elif current == "dashboard":
    st.title(f"📊 {t('dash_title')}")
    hist = st.session_state.history
    total = len(hist)
    if total > 0:
        df = pd.DataFrame(hist)
        fiable = df[df.get("Status", pd.Series()) == "Fiable"].shape[0] if "Status" in df.columns else total
        averif = total - fiable
        common = df["Parasite"].value_counts().idxmax() if "Parasite" in df.columns else "N/A"
    else:
        df, fiable, averif, common = pd.DataFrame(), 0, 0, "N/A"

    kc = st.columns(4)
    for col, (ic, val, lbl, clr) in zip(kc, [("🔬", total, t("dash_total"), "#3b82f6"), ("✅", fiable, t("dash_reliable"), "#22c55e"), ("⚠️", averif, t("dash_check"), "#f59e0b"), ("🦠", common, t("dash_frequent"), "#ef4444")]):
        with col:
            st.markdown(f"<div class='dm-metric'><span class='dm-metric-icon'>{ic}</span><div class='dm-metric-val' style='color:{clr}!important;'>{val}</div><div class='dm-metric-lbl'>{lbl}</div></div>", unsafe_allow_html=True)

    if not df.empty and "Parasite" in df.columns:
        st.markdown("---")
        filt = st.selectbox(t("dash_filter"), ["All"] + df["Parasite"].unique().tolist())
        filtered = df if filt == "All" else df[df["Parasite"] == filt]
        c1, c2 = st.columns(2)
        with c1: st.bar_chart(filtered["Parasite"].value_counts(), color="#3b82f6")
        with c2:
            if "Confiance" in filtered.columns:
                try: st.line_chart(filtered["Confiance"].str.rstrip('%').astype(float).reset_index(drop=True))
                except: pass
        st.dataframe(filtered, use_container_width=True)
        e1, e2, e3 = st.columns(3)
        with e1: st.download_button(t("dash_export"), filtered.to_csv(index=False).encode('utf-8-sig'), "data.csv", "text/csv", use_container_width=True)
        with e2: st.download_button(t("dash_export_json"), filtered.to_json(orient='records', force_ascii=False).encode('utf-8'), "data.json", "application/json", use_container_width=True)
    else:
        st.markdown(f"<div class='dm-card' style='text-align:center;padding:40px;'><div style='font-size:4rem;'>📊</div><h3>{t('dash_no_data')}</h3></div>", unsafe_allow_html=True)

# ╔══════════════════════════════════╗
# ║             QUIZ                 ║
# ╚══════════════════════════════════╝
elif current == "quiz":
    st.title(f"🧠 {t('quiz_title')}")
    st.markdown(f"<div class='dm-card dm-card-purple'><p>{t('quiz_desc')}</p></div>", unsafe_allow_html=True)
    questions = QUIZ_QUESTIONS.get(st.session_state.lang, QUIZ_QUESTIONS["fr"])
    qs = st.session_state.quiz_state
    if not qs["active"]:
        if st.button("🎮 Start", use_container_width=True, type="primary"):
            st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": True}; st.rerun()
    else:
        idx = qs["current"]
        if idx < len(questions):
            q = questions[idx]
            st.markdown(f"### {t('quiz_question')} {idx+1}/{len(questions)}")
            st.progress(idx / len(questions))
            st.markdown(f"<div class='dm-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)
            ak = f"qa_{idx}"
            if ak not in st.session_state:
                for i, opt in enumerate(q["options"]):
                    if st.button(opt, key=f"q{idx}_{i}", use_container_width=True):
                        ok = (i == q["answer"])
                        if ok: st.session_state.quiz_state["score"] += 1
                        st.session_state.quiz_state["answered"].append(ok)
                        st.session_state[ak] = {"ok": ok, "sel": i}; st.rerun()
            else:
                ad = st.session_state[ak]
                st.success(t("quiz_correct")) if ad["ok"] else st.error(f"{t('quiz_wrong')} → {q['options'][q['answer']]}")
                st.info(f"📖 {q['explanation']}")
                if st.button(f"➡️ {t('quiz_next')}", use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1; st.rerun()
        else:
            sc, tq = qs["score"], len(questions)
            pct = int(sc / tq * 100) if tq else 0
            emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "📚" if pct >= 40 else "💪"
            st.markdown(f"<div class='dm-card dm-card-green' style='text-align:center;'><div style='font-size:3.5rem;'>{emoji}</div><h2>{t('quiz_finish')}</h2><div style='font-size:2.5rem;font-weight:900;color:#2563eb;'>{sc}/{tq}</div><p>{pct}%</p></div>", unsafe_allow_html=True)
            if st.button(f"🔄 {t('quiz_restart')}", use_container_width=True):
                for k in [k for k in st.session_state if k.startswith("qa_")]: del st.session_state[k]
                st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": False}; st.rerun()

# ╔══════════════════════════════════╗
# ║           CHATBOT                ║
# ╚══════════════════════════════════╝
elif current == "chatbot":
    st.title(f"💬 {t('chatbot_title')}")
    kb = CHATBOT_KB.get(st.session_state.lang, CHATBOT_KB["fr"])
    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "bot", "msg": kb["greeting"]})
    for m in st.session_state.chat_history:
        cls = "dm-chat-user" if m["role"] == "user" else "dm-chat-bot"
        ic = "👤" if m["role"] == "user" else "🤖"
        st.markdown(f"<div class='dm-chat-msg {cls}'>{ic} {m['msg']}</div>", unsafe_allow_html=True)
    inp = st.chat_input(t("chatbot_placeholder"))
    if inp:
        st.session_state.chat_history.append({"role": "user", "msg": inp})
        st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(inp)})
        st.rerun()
    st.markdown("---")
    qc = st.columns(4)
    for col, q in zip(qc, ["Amoeba?", "Giardia?", "Plasmodium?", "Leishmania?"]):
        with col:
            if st.button(q, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(q)})
                st.rerun()
    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.chat_history = []; st.rerun()

# ╔══════════════════════════════════╗
# ║            ABOUT                 ║
# ╚══════════════════════════════════╝
elif current == "about":
    st.title(f"ℹ️ {t('about_title')}")
    st.markdown(f"<div class='dm-card dm-card-blue' style='text-align:center;'><h1 style='color:#2563eb;'>🧬 DM SMART LAB AI</h1><p><b>v{APP_VERSION}</b></p><p style='opacity:0.6;'>{t('about_desc')}</p></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='dm-card'><h3>📖 {PROJECT_TITLE}</h3><p>{t('about_project_desc')}</p></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='dm-card dm-card-blue'><h3>👨‍🔬 {t('about_team')}</h3><p><b>{AUTHORS['dev1']['name']}</b><br><span style='opacity:0.6;'>{AUTHORS['dev1']['role']}</span></p><p><b>{AUTHORS['dev2']['name']}</b><br><span style='opacity:0.6;'>{AUTHORS['dev2']['role']}</span></p></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='dm-card'><h3>🏫 {t('about_institution')}</h3><p><b>{INSTITUTION['name']}</b></p><p>📍 {INSTITUTION['city']}, {INSTITUTION['country']} 🇩🇿</p><h4>🎯 {t('about_objectives')}</h4><ul><li>{t('about_obj1')}</li><li>{t('about_obj2')}</li><li>{t('about_obj3')}</li><li>{t('about_obj4')}</li></ul></div>", unsafe_allow_html=True)
    st.markdown(f"### 🛠️ {t('about_tech')}")
    tc = st.columns(5)
    for col, (i, n) in zip(tc, [("🐍", "Python"), ("🧠", "TensorFlow"), ("🎨", "Streamlit"), ("📊", "Pandas"), ("📄", "FPDF")]):
        with col: st.markdown(f"<div class='dm-metric'><span class='dm-metric-icon'>{i}</span><div class='dm-metric-val' style='font-size:1rem;'>{n}</div></div>", unsafe_allow_html=True)
    st.caption(f"Made with ❤️ in {INSTITUTION['city']} — {INSTITUTION['year']}")
