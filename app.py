# ╔════════════════════════════════════════════════════════════════════════════════════╗
# ║                  DM SMART LAB AI v7.5 - COMPLETE PROFESSIONAL EDITION             ║
# ║            Diagnostic Parasitologique par Intelligence Artificielle               ║
# ║                                                                                    ║
# ║  Développé par:                                                                   ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)                          ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                             ║
# ║                                                                                    ║
# ║  INFSPM - Ouargla, Algérie 🇩🇿                                                    ║
# ║                                                                                    ║
# ║  ✨ VERSION 7.5 FEATURES:                                                          ║
# ║  ✅ 7000+ lignes de code optimisé                                                 ║
# ║  ✅ Cache système avancé (zéro freeze)                                            ║
# ║  ✅ State Management centralisé                                                   ║
# ║  ✅ 9 pages complètes avec animations                                             ║
# ║  ✅ 3 langues (FR/AR/EN)                                                          ║
# ║  ✅ BD SQLite optimisée                                                           ║
# ║  ✅ PDF professionnel + QR                                                        ║
# ║  ✅ Comparaison d'images avancée                                                  ║
# ║  ✅ Quiz complet avec leaderboard                                                 ║
# ║  ✅ Chatbot intelligent 30+ réponses                                              ║
# ║  ✅ Dashboard temps réel avec Plotly                                              ║
# ║  ✅ Administration multi-usagers                                                  ║
# ║  ✅ Logging & Activity tracking                                                   ║
# ║  ✅ Exportation multi-formats                                                     ║
# ║  ✅ Validation d'analyses                                                         ║
# ║  ✅ Statistiques avancées                                                         ║
# ║  ✅ Système de caching N-level                                                    ║
# ║  ✅ Dark space theme animé                                                        ║
# ║  ✅ Sécurité: Bcrypt, Rate limiting                                              ║
# ║  ✅ Voice synthesis (TTS)                                                         ║
# ║  ✅ Image processing 15+ filtres                                                  ║
# ║  ✅ Heatmap & Thermal vision                                                      ║
# ║  ✅ Performance optimisée                                                         ║
# ╚════════════════════════════════════════════════════════════════════════════════════╝

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
import re
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw
from datetime import datetime, timedelta
from fpdf import FPDF
from contextlib import contextmanager
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict, Counter
from functools import wraps
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

# ════════════════════════════════════════════════════════════════════════════════════
#  CONFIGURATION & CONSTANTS
# ════════════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="DM Smart Lab AI v7.5 - Professional Edition",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "DM Smart Lab AI v7.5 - Parasitology Diagnosis System"}
)

APP_VERSION = "7.5.0-PRO"
BUILD_DATE = "2026-01-15"
SECRET_KEY = "dm_smart_lab_2026_ultra_secret_key_v7_5"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)
DB_PATH = "dm_smartlab.db"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
CACHE_TTL = 3600  # 1 hour

# ════════════════════════════════════════════════════════════════════════════════════
#  ROLES & PERMISSIONS
# ════════════════════════════════════════════════════════════════════════════════════

ROLES = {
    "admin": {
        "level": 3,
        "icon": "👑",
        "label": {"fr": "Administrateur Système", "ar": "مدير النظام", "en": "System Administrator"},
        "permissions": ["read", "write", "delete", "admin", "validate", "export", "manage_users", "view_logs"],
        "color": "#ff0040"
    },
    "technician": {
        "level": 2,
        "icon": "🔬",
        "label": {"fr": "Technicien Laboratoire", "ar": "تقني مخبر", "en": "Lab Technician"},
        "permissions": ["read", "write", "validate", "export"],
        "color": "#00f5ff"
    },
    "viewer": {
        "level": 1,
        "icon": "👁️",
        "label": {"fr": "Observateur", "ar": "مراقب", "en": "Viewer"},
        "permissions": ["read", "export"],
        "color": "#00ff88"
    }
}

AUTHORS = {
    "dev1": {
        "name": "Sebbag Mohamed Dhia Eddine",
        "email": "sebbag.dhia@infspm.dz",
        "role": {"fr": "Expert IA & Conception", "ar": "خبير ذكاء اصطناعي و تصميم", "en": "AI & Design Expert"},
        "avatar": "👨‍🔬"
    },
    "dev2": {
        "name": "Ben Sghir Mohamed",
        "email": "bensghir.mohamed@infspm.dz",
        "role": {"fr": "Expert Laboratoire & Données", "ar": "خبير مخبر و بيانات", "en": "Laboratory & Data Expert"},
        "avatar": "👨‍⚕️"
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
    "year": 2026,
    "website": "www.infspm.dz",
    "phone": "+213 29 70 00 00",
    "address": "Ouargla, Wilaya de Ouargla, Algérie"
}

# ════════════════════════════════════════════════════════════════════════════════════
#  COLOR SCHEME
# ════════════════════════════════════════════════════════════════════════════════════

NEON = {
    "cyan": "#00f5ff",
    "magenta": "#ff00ff",
    "green": "#00ff88",
    "orange": "#ff6600",
    "red": "#ff0040",
    "blue": "#0066ff",
    "purple": "#9933ff",
    "yellow": "#ffff00",
    "pink": "#ff69b4",
    "lime": "#00ff00",
    "aqua": "#00ffff",
    "darkred": "#7f1d1d",
    "darkblue": "#001f3f"
}

COLORS_RISK = {
    "critical": "#ff0040",
    "high": "#ff3366",
    "medium": "#ff9500",
    "low": "#00e676",
    "none": "#00ff88"
}

# ════════════════════════════════════════════════════════════════════════════════════
#  LABORATORY EQUIPMENT & SAMPLES
# ════════════════════════════════════════════════════════════════════════════════════

MICROSCOPE_TYPES = [
    "Microscope Optique",
    "Microscope Binoculaire",
    "Microscope Inversé",
    "Microscope à Fluorescence",
    "Microscope Contraste de Phase",
    "Microscope Fond Noir",
    "Microscope Numérique",
    "Microscope Confocal",
    "Microscope Polarisé",
    "Microscope Électronique"
]

MAGNIFICATIONS = ["x4", "x10", "x20", "x40", "x60", "x100 (Immersion oil)", "x100 (Water)", "x100 (Air)"]

PREPARATION_TYPES = [
    "État Frais (Direct)",
    "Coloration au Lugol",
    "MIF (Merthiolate-Iodine-Formaldehyde)",
    "Concentration Ritchie (Formol-Éther)",
    "Concentration Willis (Flottation NaCl)",
    "Kato-Katz",
    "Coloration MGG",
    "Coloration Giemsa",
    "Ziehl-Neelsen Modifié",
    "Coloration Trichrome",
    "Goutte Épaisse",
    "Frottis Mince",
    "Scotch-Test (Graham)",
    "Technique Baermann",
    "Flottation Willis",
    "Technique Knott",
    "Fixation à l'alcool 70%",
    "Coloration Wright",
    "Coloration Acridine Orange",
    "Immunofluorescence"
]

SAMPLES = {
    "fr": [
        "Selles", "Sang (Frottis)", "Sang (Goutte épaisse)",
        "Urines", "LCR (Liquide Céphalo-Rachidien)", "Biopsie Cutanée",
        "Crachat", "Liquide pleural", "Liquide péritonéal",
        "Liquide articulaire", "Liquide synovial", "Pus",
        "Bile", "Liquide folliculaire", "Sperme", "Autre"
    ],
    "ar": [
        "براز", "دم (لطاخة)", "دم (قطرة سميكة)", "بول",
        "سائل دماغي شوكي", "خزعة جلدية", "بلغم",
        "سائل جنبي", "سائل بريتواني", "سائل مفصلي", "أخرى"
    ],
    "en": [
        "Stool", "Blood (Smear)", "Blood (Thick drop)", "Urine", "CSF",
        "Skin Biopsy", "Sputum", "Pleural fluid", "Peritoneal fluid",
        "Joint fluid", "Synovial fluid", "Pus", "Bile", "Other"
    ]
}

# ════════════════════════════════════════════════════════════════════════════════════
#  COMPLETE TRANSLATION SYSTEM (3 LANGUES)
# ════════════════════════════════════════════════════════════════════════════════════

TR = {
    "fr": {
        # Navigation & General
        "app_title": "DM Smart Lab AI",
        "app_subtitle": "Diagnostic Parasitologique Intelligent",
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
        "settings": "Paramètres",
        "help": "Aide",
        "documentation": "Documentation",
        "contact": "Contact",
        
        # Greetings
        "greeting_morning": "Bonjour",
        "greeting_afternoon": "Bon après-midi",
        "greeting_evening": "Bonsoir",
        "welcome_msg": "Bienvenue dans DM Smart Lab AI",
        "welcome_btn": "Message de Bienvenue",
        "intro_btn": "Présentation du Système",
        "stop_voice": "Arrêter la voix",
        
        # Patient Information
        "patient_info": "Informations du Patient",
        "patient_name": "Nom du Patient",
        "patient_firstname": "Prénom",
        "patient_age": "Âge",
        "age": "Âge",
        "sex": "Sexe",
        "male": "Homme",
        "female": "Femme",
        "weight": "Poids (kg)",
        "height": "Taille (cm)",
        "sample_type": "Type d'Échantillon",
        "patient_history": "Antécédents médicaux",
        "clinical_symptoms": "Symptômes cliniques",
        
        # Laboratory
        "lab_info": "Informations du Laboratoire",
        "microscope": "Microscope",
        "magnification": "Grossissement",
        "preparation": "Préparation",
        "technician": "Technicien",
        "notes": "Notes / Observations",
        "sample_collection_date": "Date de prélèvement",
        "sample_processing_date": "Date de traitement",
        
        # Image Analysis
        "image_capture": "Capture Microscopique",
        "take_photo": "Prendre une Photo (Caméra)",
        "upload_file": "Importer un fichier",
        "camera_hint": "Placez l'oculaire du microscope devant la caméra",
        "image_quality_check": "Vérification de qualité",
        "image_too_dark": "Image trop sombre",
        "image_too_bright": "Image trop claire",
        "image_blurry": "Image floue",
        
        # Results
        "result": "Résultat",
        "confidence": "Confiance",
        "confidence_score": "Score de confiance",
        "risk": "Risque",
        "risk_level": "Niveau de risque",
        "morphology": "Morphologie",
        "description": "Description",
        "advice": "Conseil Médical",
        "extra_tests": "Examens complémentaires suggérés",
        "diagnostic_keys": "Clés Diagnostiques",
        "lifecycle": "Cycle de Vie",
        "all_probabilities": "Toutes les probabilités",
        "top_3_matches": "Top 3 correspondances",
        
        # Actions
        "download_pdf": "Télécharger PDF",
        "download_report": "Télécharger le rapport",
        "save_db": "Sauvegarder en base",
        "new_analysis": "Nouvelle Analyse",
        "listen": "Écouter",
        "print": "Imprimer",
        "share": "Partager",
        "export": "Exporter",
        "delete": "Supprimer",
        "edit": "Modifier",
        "view": "Voir",
        "back": "Retour",
        
        # Statistics & Dashboard
        "total_analyses": "Analyses totales",
        "reliable": "Fiables",
        "to_verify": "À vérifier",
        "most_frequent": "Parasite le plus fréquent",
        "avg_confidence": "Confiance moyenne",
        "parasite_distribution": "Distribution des parasites",
        "confidence_levels": "Niveaux de confiance",
        "trends": "Tendances (30 derniers jours)",
        "history": "Historique complet",
        "statistics": "Statistiques",
        "reports": "Rapports",
        
        # Database Actions
        "validate": "Valider",
        "validated": "Validé",
        "pending_validation": "En attente de validation",
        "export_csv": "Exporter CSV",
        "export_json": "Exporter JSON",
        "export_excel": "Exporter Excel",
        "export_pdf": "Exporter PDF",
        
        # Quiz
        "start_quiz": "Démarrer le Quiz",
        "next_question": "Question Suivante",
        "previous_question": "Question Précédente",
        "restart": "Recommencer",
        "finish_quiz": "Terminer le Quiz",
        "skip_question": "Passer la question",
        "leaderboard": "Classement",
        "your_score": "Votre score",
        "high_score": "Meilleur score",
        "score_excellent": "Excellent ! Vous maîtrisez la parasitologie !",
        "score_good": "Bien joué ! Continuez à apprendre !",
        "score_average": "Pas mal ! Révisez encore un peu !",
        "score_low": "Courage ! La parasitologie s'apprend avec la pratique !",
        "question_number": "Question",
        "of": "de",
        "correct_answers": "Bonnes réponses",
        "wrong_answers": "Mauvaises réponses",
        
        # Chat & Search
        "search": "Rechercher...",
        "search_results": "Résultats de recherche",
        "no_results": "Aucun résultat trouvé",
        "no_data": "Aucune donnée disponible",
        "chat_welcome": "Bonjour ! Je suis **DM Bot**, votre assistant parasitologique intelligent.",
        "chat_placeholder": "Posez votre question sur les parasites...",
        "chat_not_found": "Je n'ai pas trouvé de réponse exacte. Essayez avec un mot-clé.",
        "clear_chat": "Effacer le chat",
        "quick_questions": "Questions rapides :",
        
        # Settings & Preferences
        "language": "Langue",
        "theme": "Thème",
        "dark_mode": "Mode sombre",
        "light_mode": "Mode clair",
        "daily_tip": "Conseil du Jour",
        "notifications": "Notifications",
        "privacy": "Confidentialité",
        "preferences": "Préférences",
        
        # User Management
        "users_mgmt": "Gestion des Utilisateurs",
        "user_list": "Liste des utilisateurs",
        "create_user": "Créer un utilisateur",
        "edit_user": "Modifier l'utilisateur",
        "delete_user": "Supprimer l'utilisateur",
        "user_active": "Utilisateur actif",
        "user_inactive": "Utilisateur inactif",
        "last_login": "Dernière connexion",
        "login_count": "Nombre de connexions",
        "speciality": "Spécialité",
        "activity_log": "Journal d'activité",
        "system_info": "Informations système",
        "change_pwd": "Changer le mot de passe",
        "current_password": "Mot de passe actuel",
        "new_password": "Nouveau mot de passe",
        "confirm_password": "Confirmer le mot de passe",
        
        # Comparison
        "compare": "Comparer",
        "image1": "Image 1 (Avant)",
        "image2": "Image 2 (Après)",
        "compare_btn": "Comparer les images",
        "similarity": "Similarité",
        "filter_comparison": "Comparaison des filtres",
        "pixel_diff": "Différence pixel à pixel",
        "ssim_score": "Score SSIM",
        "mse_score": "Score MSE",
        
        # Image Processing
        "brightness": "Luminosité",
        "contrast": "Contraste",
        "saturation": "Saturation",
        "zoom": "Zoom",
        "filters": "Filtres",
        "thermal": "Thermique",
        "edges": "Contours",
        "enhanced": "Amélioré",
        "negative": "Négatif",
        "emboss": "Relief",
        "heatmap": "Carte thermique",
        "gray_scale": "Échelle de gris",
        
        # Errors & Validation
        "error": "Erreur",
        "warning": "Avertissement",
        "success": "Succès",
        "info": "Information",
        "name_required": "Le nom du patient est obligatoire !",
        "saved_ok": "Résultat sauvegardé avec succès !",
        "saved_error": "Erreur lors de la sauvegarde",
        "demo_mode": "Mode démonstration (aucun modèle IA chargé)",
        "low_conf_warn": "Confiance faible. Vérification manuelle recommandée !",
        "file_too_large": "Le fichier est trop volumineux",
        "invalid_file_type": "Type de fichier non supporté",
        
        # Professional Aspects
        "quick_overview": "Aperçu rapide",
        "where_science": "Où la Science Rencontre l'Intelligence",
        "system_desc": "Système de diagnostic parasitologique assisté par IA",
        "dev_team": "Équipe de Développement",
        "institution": "Établissement",
        "technologies": "Technologies utilisées",
        
        # Voice Messages
        "voice_welcome": "Bienvenue dans DM Smart Lab AI ! Nous sommes ravis de vous accueillir dans ce système d'intelligence artificielle dédié au diagnostic parasitologique.",
        "voice_intro": "Je suis DM Smart Lab AI, version 7 point 5, système de diagnostic parasitologique par intelligence artificielle. Développé par Sebbag Mohamed Dhia Eddine et Ben Sghir Mohamed au sein de l'Institut National de Formation Supérieure Paramédicale de Ouargla.",
        "voice_analysis_started": "Analyse en cours. Veuillez patienter.",
        "voice_analysis_complete": "Analyse terminée.",
    },
    "ar": {
        # Navigation & General
        "app_title": "مختبر DM الذكي",
        "app_subtitle": "التشخيص الطفيلي الذكي",
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
        "settings": "الإعدادات",
        "help": "مساعدة",
        
        # Greetings
        "greeting_morning": "صباح الخير",
        "greeting_afternoon": "مساء الخير",
        "greeting_evening": "مساء الخير",
        "welcome_msg": "مرحباً في مختبر DM الذكي",
        "welcome_btn": "رسالة ترحيبية",
        "intro_btn": "تقديم النظام",
        "stop_voice": "إيقاف الصوت",
        
        # Patient Information
        "patient_info": "معلومات المريض",
        "patient_name": "اسم المريض",
        "patient_firstname": "الاسم الأول",
        "patient_age": "العمر",
        "age": "العمر",
        "sex": "الجنس",
        "male": "ذكر",
        "female": "أنثى",
        "weight": "الوزن (كغ)",
        "height": "الطول (سم)",
        "sample_type": "نوع العينة",
        
        # Laboratory
        "lab_info": "معلومات المخبر",
        "microscope": "المجهر",
        "magnification": "التكبير",
        "preparation": "نوع التحضير",
        "technician": "التقني",
        "notes": "ملاحظات",
        
        # Image Analysis
        "image_capture": "التقاط مجهري",
        "take_photo": "التقاط صورة (الكاميرا)",
        "upload_file": "استيراد ملف",
        "camera_hint": "ضع عدسة المجهر أمام الكاميرا",
        
        # Results
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
        
        # Actions
        "download_pdf": "تحميل PDF",
        "save_db": "حفظ",
        "new_analysis": "تحليل جديد",
        "listen": "استماع",
        
        # Statistics
        "total_analyses": "مجموع التحاليل",
        "reliable": "موثوقة",
        "to_verify": "للتحقق",
        "most_frequent": "الأكثر شيوعاً",
        "avg_confidence": "متوسط الثقة",
        "parasite_distribution": "توزيع الطفيليات",
        "confidence_levels": "مستويات الثقة",
        "trends": "الاتجاهات (30 يوم)",
        "history": "السجل الكامل",
        
        # Database
        "validate": "مصادقة",
        "export_csv": "CSV",
        "export_json": "JSON",
        
        # Quiz
        "start_quiz": "بدء الاختبار",
        "next_question": "السؤال التالي",
        "restart": "إعادة",
        "leaderboard": "الترتيب",
        "score_excellent": "ممتاز ! أنت خبير في علم الطفيليات !",
        "score_good": "أحسنت ! واصل التعلم !",
        "score_average": "لا بأس ! راجع قليلاً !",
        "score_low": "شجاعة ! علم الطفيليات يُتعلم بالممارسة !",
        
        # Chat
        "search": "بحث...",
        "no_data": "لا توجد بيانات",
        "no_results": "لا توجد نتائج",
        "chat_welcome": "مرحباً! أنا **DM Bot**، مساعدك الذكي.",
        "chat_placeholder": "اطرح سؤالك عن الطفيليات...",
        "chat_not_found": "لم أجد إجابة دقيقة.",
        "clear_chat": "مسح المحادثة",
        
        # Settings
        "language": "اللغة",
        "daily_tip": "نصيحة اليوم",
        
        # User Management
        "users_mgmt": "إدارة المستخدمين",
        "activity_log": "سجل النشاط",
        "system_info": "النظام",
        "create_user": "إنشاء مستخدم",
        "change_pwd": "تغيير كلمة المرور",
        
        # Comparison
        "image1": "الصورة 1 (قبل)",
        "image2": "الصورة 2 (بعد)",
        "compare_btn": "مقارنة الصور",
        "similarity": "التشابه",
        
        # General
        "name_required": "اسم المريض مطلوب !",
        "saved_ok": "تم الحفظ بنجاح !",
        "demo_mode": "وضع تجريبي",
        "low_conf_warn": "ثقة منخفضة. يُنصح بالتحقق اليدوي !",
        
        # Professional
        "quick_overview": "نظرة سريعة",
        "where_science": "حيث يلتقي العلم بالذكاء",
        "system_desc": "نظام تشخيص طفيلي بالذكاء الاصطناعي",
        "dev_team": "فريق التطوير",
        "institution": "المؤسسة",
        "technologies": "التقنيات المستخدمة",
    },
    "en": {
        # Navigation & General
        "app_title": "DM Smart Lab AI",
        "app_subtitle": "Intelligent Parasitological Diagnosis",
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
        "settings": "Settings",
        
        # Greetings
        "greeting_morning": "Good morning",
        "greeting_afternoon": "Good afternoon",
        "greeting_evening": "Good evening",
        "welcome_msg": "Welcome to DM Smart Lab AI",
        "welcome_btn": "Welcome Message",
        "intro_btn": "System Introduction",
        "stop_voice": "Stop voice",
        
        # Patient Information
        "patient_info": "Patient Information",
        "patient_name": "Patient Name",
        "patient_firstname": "First Name",
        "patient_age": "Age",
        "age": "Age",
        "sex": "Sex",
        "male": "Male",
        "female": "Female",
        "weight": "Weight (kg)",
        "height": "Height (cm)",
        "sample_type": "Sample Type",
        
        # Laboratory
        "lab_info": "Laboratory Information",
        "microscope": "Microscope",
        "magnification": "Magnification",
        "preparation": "Preparation",
        "technician": "Technician",
        "notes": "Notes / Observations",
        
        # Image Analysis
        "image_capture": "Microscopic Capture",
        "take_photo": "Take a Photo (Camera)",
        "upload_file": "Upload a file",
        "camera_hint": "Place the microscope eyepiece in front of the camera",
        
        # Results
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
        
        # Actions
        "download_pdf": "Download PDF",
        "save_db": "Save",
        "new_analysis": "New Analysis",
        "listen": "Listen",
        
        # Statistics
        "total_analyses": "Total Analyses",
        "reliable": "Reliable",
        "to_verify": "To Verify",
        "most_frequent": "Most Frequent",
        "avg_confidence": "Avg. Confidence",
        "parasite_distribution": "Parasite Distribution",
        "confidence_levels": "Confidence Levels",
        "trends": "Trends (30 days)",
        "history": "Complete History",
        
        # Database
        "validate": "Validate",
        "export_csv": "CSV",
        "export_json": "JSON",
        
        # Quiz
        "start_quiz": "Start Quiz",
        "next_question": "Next Question",
        "restart": "Restart",
        "leaderboard": "Leaderboard",
        "score_excellent": "Excellent! You master parasitology!",
        "score_good": "Well done! Keep learning!",
        "score_average": "Not bad! Review a bit more!",
        "score_low": "Courage! Parasitology is learned through practice!",
        
        # Chat
        "search": "Search...",
        "no_data": "No data available",
        "no_results": "No results found",
        "chat_welcome": "Hello! I'm **DM Bot**, your intelligent parasitology assistant.",
        "chat_placeholder": "Ask your question about parasites...",
        "chat_not_found": "I couldn't find an exact answer.",
        "clear_chat": "Clear chat",
        
        # Settings
        "language": "Language",
        "daily_tip": "Daily Tip",
        
        # User Management
        "users_mgmt": "Users Management",
        "activity_log": "Activity Log",
        "system_info": "System",
        "create_user": "Create User",
        "change_pwd": "Change Password",
        
        # Comparison
        "image1": "Image 1 (Before)",
        "image2": "Image 2 (After)",
        "compare_btn": "Compare Images",
        "similarity": "Similarity",
        
        # General
        "name_required": "Patient name is required!",
        "saved_ok": "Result saved successfully!",
        "demo_mode": "Demo mode (no AI model loaded)",
        "low_conf_warn": "Low confidence. Manual verification recommended!",
        
        # Professional
        "quick_overview": "Quick Overview",
        "where_science": "Where Science Meets Intelligence",
        "system_desc": "AI-powered parasitological diagnosis system",
        "dev_team": "Development Team",
        "institution": "Institution",
        "technologies": "Technologies Used",
    }
}

def t(key: str) -> str:
    """Get translated string by key"""
    lang = st.session_state.get("lang", "fr")
    return TR.get(lang, TR["fr"]).get(key, TR["fr"].get(key, f"[{key}]"))

def tl(d: Dict[str, str]) -> str:
    """Get localized value from dict"""
    if not isinstance(d, dict):
        return str(d)
    lang = st.session_state.get("lang", "fr")
    return d.get(lang, d.get("fr", str(d)))

def get_greeting() -> str:
    """Get greeting based on time"""
    h = datetime.now().hour
    if h < 12:
        return t("greeting_morning")
    elif h < 18:
        return t("greeting_afternoon")
    return t("greeting_evening")

# ════════════════════════════════════════════════════════════════════════════════════
#  PARASITE DATABASE (COMPLETE 6 SPECIES + NEGATIVE)
# ════════════════════════════════════════════════════════════════════════════════════

PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "sci": "Entamoeba histolytica",
        "family": "Endamoebidae",
        "type": "Protozoan",
        "category": "Intestinal parasite",
        "morphology": {
            "trophozoite": {
                "size": "20-40 µm",
                "shape": "Irregular, amoeboid",
                "nucleus": "1 (eccentric, karyosome visible)",
                "movement": "Directional pseudopods",
                "features": "RBC phagocytosis (pathognomonic)"
            },
            "cyst": {
                "size": "10-15 µm",
                "shape": "Spherical",
                "nuclei": "4 (immature/mature)",
                "chromatoid": "Cigar-shaped bodies",
                "features": "Clear distinction from E. dispar"
            }
        },
        "morph": {
            "fr": "Kyste spherique (10-15µm) à 4 noyaux, corps chromatoïde en cigare. Trophozoite (20-40µm) avec pseudopodes digitiformes et hématies phagocytées.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 أنوية، جسم كروماتيني على شكل سيجار. الطور النشط (20-40 ميكرومتر) مع أقدام كاذبة وكريات حمراء مبتلعة.",
            "en": "Spherical cyst (10-15µm) with 4 nuclei, cigar-shaped chromatoid body. Trophozoite (20-40µm) with pseudopods and phagocytosed RBCs."
        },
        "desc": {
            "fr": "Protozoaire responsable de l'amibiase intestinale et extra-intestinale. Transmission fécal-orale via eau contaminée.",
            "ar": "طفيلي أولي مسؤول عن الأميبيا المعوية والخارج معوية. الانتقال عبر الفم-البراز عبر ماء ملوث.",
            "en": "Protozoan causing intestinal and extra-intestinal amebiasis. Fecal-oral transmission via contaminated water."
        },
        "funny": {
            "fr": "Le ninja des intestins! Il mange des globules rouges au petit-déjeuner!",
            "ar": "نينجا الأمعاء! يأكل كريات الدم الحمراء في الفطور!",
            "en": "The intestinal ninja! Eats red blood cells for breakfast!"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "epidemiology": {
            "prevalence": "Worldwide, endemic in tropical regions",
            "transmission": "Fecal-oral",
            "incidence": "~40 million cases annually",
            "mortality": "40,000-110,000 deaths per year"
        },
        "pathogenesis": "Tissue invasion by trophozoites, mucosal ulceration, secondary bacterial infection",
        "clinical_presentation": {
            "asymptomatic": "90% of infected individuals",
            "intestinal": "Dysentery, bloody diarrhea, abdominal pain",
            "extraintestinal": "Liver abscess (most common), brain, lung, heart involvement"
        },
        "advice": {
            "fr": "Métronidazole 500mg x3/j (7-10j) + Amœbicide de contact (Intetrix 650mg x3/j 20j). Contrôle EPS J15/J30. Repos alimentaire.",
            "ar": "ميترونيدازول 500 ملغ 3 مرات يوميا (7-10 أيام) + أميبيسيد تلامسي (إنتيتريكس). مراقبة بعد 15 و 30 يوم. حمية غذائية.",
            "en": "Metronidazole 500mg x3/d (7-10d) + Luminal agent (Iodoquinol 650mg x3/d 20d). Follow-up D15/D30. Bland diet."
        },
        "tests": [
            "Stool exam (x3, days apart)",
            "Serological test (IHA, ELISA)",
            "Liver ultrasound if suspicion of abscess",
            "CT abdomen",
            "Colonoscopy with biopsy if needed",
            "PCR for species identification"
        ],
        "color": "#ff0040",
        "icon": "🔴",
        "cycle": {
            "fr": "Kyste ingéré → Excystation → Trophozoite → Invasion tissulaire → Enkystement → Émission",
            "ar": "كيس مبتلع ثم انفكاس ثم طور نشط ثم غزو أنسجة ثم تكيس ثم إخراج",
            "en": "Ingested cyst → Excystation → Trophozoite → Tissue invasion → Encystation → Emission"
        },
        "keys": {
            "fr": "RBC phagocytose = pathognomonie\nKyste 4 noyaux (vs E. coli 8)\nCorps chromatoïdes en cigare\nMobilité directionnelle",
            "ar": "بلع كريات الدم = دليل مميز\nكيس 4 أنوية مقابل 8 لـ E. coli\nأجسام كروماتينية سيجارية\nحركة اتجاهية",
            "en": "RBC phagocytosis = pathognomonic\n4 nuclei cyst (vs E. coli 8)\nCigar chromatoid bodies\nDirectional motility"
        },
        "complications": [
            "Fulminant colitis",
            "Toxic megacolon",
            "Perforation",
            "Peritonitis",
            "Liver abscess",
            "Brain abscess",
            "Lung abscess",
            "Myocarditis",
            "Pericarditis"
        ],
        "prognosis": "Good with prompt treatment; mortality high without treatment",
        "prevention": "Safe water, sanitation, food hygiene, hand washing"
    },
    
    "Giardia": {
        "sci": "Giardia lamblia (intestinalis/duodenalis)",
        "family": "Giardiidae",
        "type": "Protozoan flagellate",
        "category": "Intestinal parasite",
        "morphology": {
            "trophozoite": {
                "size": "12-15 µm",
                "shape": "Pear-shaped (kite-like)",
                "nucleus": "2 (anterior)",
                "flagella": "4 pairs (8 total)",
                "adhesive_disc": "Ventral, used for attachment",
                "movement": "Falling leaf pattern"
            },
            "cyst": {
                "size": "8-12 µm",
                "shape": "Ovoid/elliptical",
                "nuclei": "4",
                "fibrils": "Median and parabasal fibrils visible",
                "features": "Infectious form"
            }
        },
        "morph": {
            "fr": "Trophozoite piriforme en cerf-volant (12-15µm), 2 noyaux (face de hibou), disque adhésif, 4 paires de flagelles. Kyste ovoïde (8-12µm) à 4 noyaux.",
            "ar": "الطور النشط كمثري شكل طائرة ورقية (12-15 ميكرومتر)، نواتان (وجه البومة)، قرص لاصق، 4 أزواج أسواط. كيس بيضاوي (8-12 ميكرومتر) بـ 4 أنوية.",
            "en": "Pear-shaped kite trophozoite (12-15µm), 2 nuclei (owl face), adhesive disk, 4 flagella pairs. Ovoid cyst (8-12µm) with 4 nuclei."
        },
        "desc": {
            "fr": "Flagellé du duodénum. Diarrhée graisseuse chronique, malabsorption. Transmission hydrique (principalement).",
            "ar": "سوطي الاثني عشر. إسهال دهني مزمن، سوء امتصاص. انتقال عبر الماء (بشكل أساسي).",
            "en": "Duodenal flagellate. Chronic greasy diarrhea, malabsorption. Waterborne transmission (primarily)."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil! Un touriste qui refuse de partir!",
            "ar": "ينظر إليك بنظارته الشمسية! سائح يرفض المغادرة!",
            "en": "It stares at you with sunglasses! A tourist who refuses to leave!"
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "epidemiology": {
            "prevalence": "~280 million cases worldwide",
            "transmission": "Waterborne, person-to-person",
            "risk_groups": "Daycare children, hikers, immunocompromised",
            "geography": "Worldwide, endemic in tropical regions"
        },
        "clinical_presentation": {
            "acute": "Watery diarrhea, cramping, nausea, vomiting",
            "chronic": "Greasy stools, steatorrhea, weight loss, malnutrition",
            "asymptomatic": "Common",
            "lactose_intolerance": "Can develop secondary LI"
        },
        "advice": {
            "fr": "Métronidazole 250mg x3/j (5-7j) OU Tinidazole 2g dose unique OU Nitazoxanide 500mg x2/j (3j).",
            "ar": "ميترونيدازول 250 ملغ 3 مرات يوميا (5-7 أيام) أو تينيدازول 2 غرام جرعة واحدة أو نيتازوكسانيد.",
            "en": "Metronidazole 250mg x3/d (5-7d) OR Tinidazole 2g single dose OR Nitazoxanide 500mg x2/d (3d)."
        },
        "tests": [
            "Stool antigen (ELISA) - most sensitive",
            "Stool microscopy (cysts, trophozoites)",
            "Duodenal aspiration/biopsy",
            "Intestinal biopsy with trophozoites",
            "Immunofluorescence antibody",
            "PCR (gold standard)"
        ],
        "color": "#ff9500",
        "icon": "🟠",
        "cycle": {
            "fr": "Kyste ingéré → Excystation duodénale → Trophozoite → Adhésion → Multiplication → Enkystement",
            "ar": "كيس مبتلع ثم انفكاس ثم طور نشط ثم التصاق ثم تكاثر ثم تكيس",
            "en": "Ingested cyst → Duodenal excystation → Trophozoite → Adhesion → Multiplication → Encystation"
        },
        "keys": {
            "fr": "Forme cerf-volant pathognomonique\n2 noyaux = face de hibou\nDisque adhésif au Lugol\nMobilité feuille morte",
            "ar": "شكل طائرة ورقية مميز\nنواتان = وجه البومة\nالقرص اللاصق باللوغول\nحركة ورقة ميتة",
            "en": "Pathognomonic kite shape\n2 nuclei = owl face\nAdhesive disk on Lugol\nFalling leaf motility"
        },
        "complications": [
            "Secondary lactose intolerance",
            "Nutrient malabsorption",
            "Fat-soluble vitamin deficiencies",
            "Growth retardation in children",
            "Reactive arthropathy"
        ],
        "prognosis": "Good; spontaneous resolution possible",
        "prevention": "Safe water, handwashing, food safety, boil/filter water in endemic areas"
    },

    "Leishmania": {
        "sci": "Leishmania infantum / major / tropica / braziliensis",
        "family": "Trypanosomatidae",
        "type": "Protozoan",
        "category": "Vector-borne parasite",
        "morphology": {
            "amastigote": {
                "location": "Intracellular (macrophages)",
                "size": "2-5 µm",
                "shape": "Oval",
                "nucleus": "Central",
                "kinetoplast": "Rod-shaped, visible on stains",
                "staining": "MGG, Giemsa, Ziehl-Neelsen"
            },
            "promastigote": {
                "location": "Insect vector (sandfly)",
                "size": "10-20 µm",
                "shape": "Elongated with flagellum",
                "flagella": "Single anterior flagellum"
            }
        },
        "morph": {
            "fr": "Amastigotes ovoïdes (2-5µm) intracellulaires dans macrophages. Noyau + kinétoplaste (MGG). Promastigotes dans vecteur.",
            "ar": "أماستيغوت بيضاوية (2-5 ميكرومتر) داخل البلاعم. نواة + كينيتوبلاست. بروماستيغوت في الناقل.",
            "en": "Ovoid amastigotes (2-5µm) intracellular in macrophages. Nucleus + kinetoplast (MGG). Promastigotes in vector."
        },
        "desc": {
            "fr": "Transmis par phlébotome femelle. Cutanée ou viscérale. Algérie: L. infantum (nord), L. major (sud).",
            "ar": "ينتقل عبر ذبابة الرمل الأنثى. جلدية أو حشوية. الجزائر: L. infantum (شمال)، L. major (جنوب).",
            "en": "Sandfly-transmitted (female Phlebotomus). Cutaneous or visceral. Algeria: L. infantum (north), L. major (south)."
        },
        "funny": {
            "fr": "Petit mais costaud! Il squatte les macrophages!",
            "ar": "صغير لكن قوي! يحتل البلاعم!",
            "en": "Small but tough! Squats in macrophages!"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "epidemiology": {
            "prevalence": "~2 million cases annually",
            "transmission": "Sandfly (female, nocturnal)",
            "vectors": "Phlebotomus (Old World), Lutzomyia (New World)",
            "endemic_regions": "Mediterranean, Middle East, Africa, Central/South America"
        },
        "clinical_presentation": {
            "cutaneous": "Papule → ulcer, typically on exposed areas",
            "visceral": "Fever, hepatosplenomegaly, pancytopenia, fatal if untreated",
            "mucocutaneous": "Metastatic lesions, disfiguring"
        },
        "advice": {
            "fr": "Cutanée: Glucantime 15mg/kg IM quotidien (20j). Viscérale: Amphotéricine B liposomale IV. MDO (Maladie à Déclaration Obligatoire) en Algérie.",
            "ar": "جلدية: غلوكانتيم 15 ملغ/كغ عضليا يوميا (20 يوم). حشوية: أمفوتيريسين ب. تبليغ إجباري.",
            "en": "Cutaneous: Glucantime 15mg/kg IM daily (20d). Visceral: Liposomal Amphotericin B IV. Notifiable disease."
        },
        "tests": [
            "Montenegro intradermal test (IDR)",
            "Serology (IFA, ELISA, Western blot)",
            "Bone marrow aspiration & culture",
            "Tissue biopsy + MGG stain",
            "PCR (most sensitive)",
            "Xenodiagnosis (culture in sandfly)"
        ],
        "color": "#ff0040",
        "icon": "🔴",
        "cycle": {
            "fr": "Piqûre phlébotome → Promastigotes → Phagocytose → Amastigotes → Multiplication → Lyse",
            "ar": "لدغة ذبابة رمل ثم بروماستيغوت ثم بلعمة ثم أماستيغوت ثم تكاثر ثم تحلل",
            "en": "Sandfly bite → Promastigotes → Phagocytosis → Amastigotes → Multiplication → Lysis"
        },
        "keys": {
            "fr": "Amastigotes 2-5µm intracellulaires\nNoyau + kinétoplaste MGG\nCulture NNN\nPCR = gold standard",
            "ar": "أماستيغوت 2-5 ميكرومتر داخل خلوية\nنواة + كينيتوبلاست\nزراعة NNN\nPCR المعيار الذهبي",
            "en": "2-5µm intracellular amastigotes\nNucleus + kinetoplast MGG\nNNN culture\nPCR = gold standard"
        },
        "complications": [
            "Secondary bacterial infection",
            "Scarring (cutaneous)",
            "Organ failure (visceral)",
            "Post-kala-azar dermal leishmaniasis"
        ],
        "prognosis": "Good if treated early; fatal if visceral untreated",
        "prevention": "Insecticide spraying, bed nets, protective clothing, avoid sand flies"
    },

    "Plasmodium": {
        "sci": "Plasmodium falciparum / vivax / ovale / malariae",
        "family": "Plasmodiidae",
        "type": "Protozoan",
        "category": "Vector-borne parasite - MEDICAL EMERGENCY",
        "morphology": {
            "p_falciparum": {
                "ring": "Signet ring, multiple rings per RBC",
                "gametocyte": "Crescent/banana-shaped (pathognomonic)",
                "Maurer_dots": "Visible",
                "Schuffner_dots": "Absent"
            },
            "p_vivax": {
                "ring": "Larger rings, pale cytoplasm",
                "infected_rbc": "Enlarged, pale, distorted",
                "Schuffner_dots": "Prominent stippling",
                "gametocyte": "Round"
            }
        },
        "morph": {
            "fr": "P. falciparum: anneau bague à chaton, gamétocytes en banane. P. vivax: trophozoite amiboïde, granulations Schüffner.",
            "ar": "P. falciparum: حلقة خاتم، خلايا جنسية موزية. P. vivax: طور نشط أميبي، حبيبات شوفنر.",
            "en": "P. falciparum: signet ring, banana gametocytes. P. vivax: amoeboid trophozoite, Schuffner dots."
        },
        "desc": {
            "fr": "🚨 URGENCE MÉDICALE ! Paludisme. P. falciparum = le plus mortel. Anophèle femelle.",
            "ar": "⚠️ حالة طوارئ طبية! ملاريا. P. falciparum = الأكثر فتكا. أنثى الأنوفيل.",
            "en": "🚨 MEDICAL EMERGENCY! Malaria. P. falciparum = most lethal. Female Anopheles."
        },
        "funny": {
            "fr": "Il demande le mariage à tes globules! Gamétocytes en banane = le clown du microscope!",
            "ar": "يطلب الزواج من كرياتك! خلايا جنسية موزية = مهرج المجهر!",
            "en": "Proposes to your blood cells! Banana gametocytes = microscope clown!"
        },
        "risk": "critical",
        "risk_d": {"fr": "🚨 URGENCE", "ar": "⚠️ طوارئ", "en": "🚨 EMERGENCY"},
        "epidemiology": {
            "deaths_yearly": "627,000 (2022 estimate)",
            "cases_yearly": "249 million",
            "high_risk": "Africa, SE Asia, pregnant women, children <5y",
            "transmission": "Anopheles mosquito (female, nocturnal)"
        },
        "clinical_presentation": {
            "early": "Fever, malaise, headache, muscle pain",
            "fever_patterns": "Tertian (P.vivax, ovale, malariae), quotidian (P.falciparum)",
            "severe": "Cerebral malaria, severe anemia, renal failure, pulmonary edema",
            "pregnant": "Placental sequestration, LBW, fetal loss"
        },
        "advice": {
            "fr": "🚨 HOSPITALISATION IMMÉDIATE! ACTs (Artésunate IV préféré). Quinine IV si grave. Monitoring parasitémie /4-6h.",
            "ar": "⚠️ دخول المستشفى الفوري! ACT. كينين وريدي إذا خطير. مراقبة كل 4-6 ساعات.",
            "en": "🚨 IMMEDIATE HOSPITALIZATION! ACTs (IV Artesunate preferred). IV Quinine if severe. Monitor parasitemia /4-6h."
        },
        "tests": [
            "Rapid Diagnostic Test (RDT) - URGENT",
            "Thick blood smear + thin smear - URGENT",
            "FBC (full blood count)",
            "Liver function tests",
            "Renal function",
            "Glucose",
            "Lactate (severity assessment)",
            "Parasite density quantification",
            "PCR (species confirmation)"
        ],
        "color": "#7f1d1d",
        "icon": "🚨",
        "cycle": {
            "fr": "Piqûre anophèle → Sporozoïtes → Hépatocytes → Mérozoïtes → Hématies → Gamétocytes",
            "ar": "لدغة الأنوفيل ثم سبوروزويت ثم خلايا كبدية ثم ميروزويت ثم كريات حمراء ثم خلايا جنسية",
            "en": "Anopheles bite → Sporozoites → Hepatocytes → Merozoites → RBCs → Gametocytes"
        },
        "keys": {
            "fr": "🚨 URGENCE <2h\nFrottis: espèce\nGE: 10x sensible\n>2% = grave\nBanane = P. falciparum",
            "ar": "⚠️ طوارئ أقل من ساعتين\nلطاخة: النوع\nGE: أكثر حساسية 10 مرات\nأكثر من 2% = خطير\nموز = P. falciparum",
            "en": "🚨 URGENT <2h\nSmear: species\nThick drop: 10x sensitive\n>2% = severe\nBanana = P. falciparum"
        },
        "complications": [
            "Cerebral malaria (15-20% mortality)",
            "Acute renal failure",
            "Severe anemia",
            "Acute respiratory distress",
            "Hypoglycemia",
            "Acidosis",
            "Spontaneous bleeding",
            "Death if untreated"
        ],
        "prognosis": "Excellent if treated early; high mortality if delayed",
        "prevention": "Bed nets, insecticides, antimalarial prophylaxis in endemic areas"
    },

    "Trypanosoma": {
        "sci": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "family": "Trypanosomatidae",
        "type": "Protozoan flagellate",
        "category": "Vector-borne parasite",
        "morphology": {
            "general": {
                "size": "15-30 µm",
                "shape": "S-shaped, C-shaped",
                "flagellum": "Single, free anteriorly",
                "membrane": "Undulating membrane",
                "kinetoplast": "Posterior, rod-shaped"
            }
        },
        "morph": {
            "fr": "Forme S/C (15-30µm), flagelle libre, membrane ondulante, kinétoplaste postérieur.",
            "ar": "شكل S/C (15-30 ميكرومتر)، سوط حر، غشاء متموج، كينيتوبلاست خلفي.",
            "en": "S/C shape (15-30µm), free flagellum, undulating membrane, posterior kinetoplast."
        },
        "desc": {
            "fr": "Maladie du sommeil (tse-tse) ou Chagas (triatome). Phase hémolymphatique puis neurologique.",
            "ar": "مرض النوم (تسي تسي) أو شاغاس (بق ثلاثي). مرحلة دموية ثم عصبية.",
            "en": "Sleeping sickness (tsetse) or Chagas (triatomine). Hemolymphatic then neurological phase."
        },
        "funny": {
            "fr": "Il court avec sa membrane ondulante! La tse-tse = le pire taxi!",
            "ar": "يركض بغشائه المتموج! ذبابة تسي تسي = أسوأ تاكسي!",
            "en": "Runs with its undulating membrane! Tsetse = worst taxi!"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "epidemiology": {
            "hat_cases": "~3000 reported (actual ~15000)",
            "chagas_cases": "~6-7 million",
            "vectors": "Tsetse fly (HAT), triatomine bug (Chagas)",
            "endemic": "Sub-Saharan Africa (HAT), Central/South America (Chagas)"
        },
        "clinical_presentation": {
            "phase1": "Chancre, fever, lymphadenopathy, hepatosplenomegaly",
            "phase2": "Neurological: sleep disturbance, confusion, ataxia, seizures, coma",
            "chagas_acute": "Romaña's sign, fever, edema",
            "chagas_chronic": "Cardiac (dilated cardiomyopathy), GI megaorgans"
        },
        "advice": {
            "fr": "Phase 1: Pentamidine 4mg/kg IV/IM quotidien (7j). Phase 2: NECT (nifurtimox-éflornithine) ou Mélarsoprol. PL (ponction lombaire) obligatoire.",
            "ar": "المرحلة 1: بنتاميدين 4 ملغ/كغ عضليا يوميا (7 أيام). المرحلة 2: NECT أو ميلارسوبرول. بزل قطني إجباري.",
            "en": "Phase 1: Pentamidine 4mg/kg IV/IM daily (7d). Phase 2: NECT (nifurtimox-eflornithine) or Melarsoprol. CSF puncture mandatory."
        },
        "tests": [
            "Parasitemia (thick/thin smear, concentration)",
            "CATT (Card Agglutination Test)",
            "Serology (IgM elevated in Phase 1)",
            "CSF analysis (staging)",
            "Lumbar puncture (cell count, glucose, proteins)",
            "PCR",
            "Culture (Tobie Medium)"
        ],
        "color": "#ff0040",
        "icon": "🔴",
        "cycle": {
            "fr": "Piqûre tse-tse → Trypomastigotes → Sang → Phase 1 → BHE → Phase 2 neurologique",
            "ar": "لدغة تسي تسي ثم تريبوماستيغوت ثم دم ثم مرحلة 1 ثم حاجز دماغي ثم مرحلة 2 عصبية",
            "en": "Tsetse bite → Trypomastigotes → Blood → Phase 1 → BBB → Phase 2 neurological"
        },
        "keys": {
            "fr": "Forme S/C + membrane ondulante\nKinétoplaste postérieur\nIgM très élevée\nPL staging",
            "ar": "شكل S/C + غشاء متموج\nكينيتوبلاست خلفي\nIgM مرتفع جدا\nتصنيف بالبزل القطني",
            "en": "S/C + undulating membrane\nPosterior kinetoplast\nVery high IgM\nLP staging"
        },
        "complications": [
            "Coma",
            "Seizures",
            "Cardiac failure (Chagas)",
            "Megaesophagus (Chagas)",
            "Megacolon (Chagas)",
            "Death if untreated"
        ],
        "prognosis": "Poor if CNS involved; good in Phase 1",
        "prevention": "Vector control, insecticides, bed nets, avoid vector habitats"
    },

    "Schistosoma": {
        "sci": "Schistosoma haematobium / mansoni / japonicum",
        "family": "Schistosomatidae",
        "type": "Helminth (trematode)",
        "category": "Water-borne parasite",
        "morphology": {
            "egg_haematobium": {
                "size": "115-170 µm",
                "shape": "Ovoid",
                "spine": "Terminal (pathognomonic)",
                "miracidium": "Mobile ciliate"
            },
            "egg_mansoni": {
                "size": "115-170 µm",
                "spine": "Lateral",
                "miracidium": "Mobile"
            },
            "adult": {
                "males": "20-22 mm length",
                "females": "26 mm",
                "copula": "Male holds female in gynecophoral canal",
                "eggs_per_day": "Hundreds to thousands"
            }
        },
        "morph": {
            "fr": "Œuf ovoïde (115-170µm): éperon terminal (S. haematobium) ou latéral (S. mansoni). Miracidium mobile.",
            "ar": "بيضة بيضاوية (115-170 ميكرومتر): شوكة طرفية (S. haematobium) أو جانبية (S. mansoni). ميراسيديوم متحرك.",
            "en": "Ovoid egg (115-170µm): terminal spine (S. haematobium) or lateral (S. mansoni). Motile miracidium."
        },
        "desc": {
            "fr": "Bilharziose. S. haematobium: uro-génitale. S. mansoni: hépato-intestinale.",
            "ar": "البلهارسيا. S. haematobium: بولي تناسلي. S. mansoni: كبدي معوي.",
            "en": "Schistosomiasis. S. haematobium: urogenital. S. mansoni: hepato-intestinal."
        },
        "funny": {
            "fr": "L'œuf avec un dard! Les cercaires = micro-torpilles!",
            "ar": "البيضة ذات الشوكة! السركاريا = طوربيدات صغيرة!",
            "en": "Egg with a stinger! Cercariae = micro-torpedoes!"
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "epidemiology": {
            "cases": "~220 million infections",
            "deaths": "~200,000 annually",
            "endemic": "Sub-Saharan Africa (S. mansoni), North Africa (S. haematobium), Asia (S. japonicum)",
            "water_transmission": "Requires specific snail vectors"
        },
        "clinical_presentation": {
            "cercarial_dermatitis": "Itching at penetration site",
            "acute_phase": "Fever, malaise, eosinophilia (2-8 weeks)",
            "chronic": "S. haematobium: hematuria, dysuria, chronic cystitis → bladder cancer\nS. mansoni: diarrhea, hepatomegaly, liver fibrosis → cirrhosis"
        },
        "advice": {
            "fr": "Praziquantel 40mg/kg dose unique (peut répéter à J7). S. haematobium: urines de midi pour diagnostic.",
            "ar": "برازيكوانتيل 40 ملغ لكل كغ جرعة واحدة (يمكن تكرار اليوم 7). S. haematobium: بول الظهيرة للتشخيص.",
            "en": "Praziquantel 40mg/kg single dose (can repeat D7). S. haematobium: midday urine for diagnosis."
        },
        "tests": [
            "Stool microscopy (eggs, quantification)",
            "Midday urine (S. haematobium)",
            "Serology (IHA, ELISA antibodies)",
            "Ultrasound (liver fibrosis assessment)",
            "Cystoscopy (S. haematobium pathology)",
            "Rectal snip biopsy (eggs visualization)"
        ],
        "color": "#ff9500",
        "icon": "🟠",
        "cycle": {
            "fr": "Œuf → Miracidium → Mollusque → Cercaire → Pénétration cutanée → Vers adultes → Ponte",
            "ar": "بيضة ثم ميراسيديوم ثم رخويات ثم سركاريا ثم اختراق الجلد ثم ديدان بالغة ثم وضع البيض",
            "en": "Egg → Miracidium → Snail → Cercaria → Skin penetration → Adult worms → Egg laying"
        },
        "keys": {
            "fr": "S.h: éperon TERMINAL, urines MIDI\nS.m: éperon LATERAL, selles\nMiracidium vivant\nÉosinophilie élevée",
            "ar": "S.h: شوكة طرفية، بول الظهيرة\nS.m: شوكة جانبية، براز\nميراسيديوم حي\nفرط الحمضات",
            "en": "S.h: TERMINAL spine, MIDDAY urine\nS.m: LATERAL spine, stool\nLiving miracidium\nHigh eosinophilia"
        },
        "complications": [
            "Chronic kidney disease",
            "Bladder cancer (S. haematobium)",
            "Liver cirrhosis (S. mansoni)",
            "Pulmonary hypertension",
            "Splenomegaly",
            "Portal hypertension"
        ],
        "prognosis": "Good with prompt treatment; chronic disease if long-standing",
        "prevention": "Safe water access, sanitation, avoid contaminated water, water treatment"
    },

    "Negative": {
        "sci": "N/A",
        "morph": {
            "fr": "Absence d'éléments parasitaires. Flore bactérienne normale.",
            "ar": "غياب العناصر الطفيلية. فلورا بكتيرية طبيعية.",
            "en": "No parasitic elements. Normal bacterial flora."
        },
        "desc": {
            "fr": "Échantillon négatif. Un seul négatif n'exclut pas (sensibilité 50-60%). Répéter x3.",
            "ar": "عينة سلبية. فحص واحد سلبي لا يستبعد (حساسية 50-60%). كرر 3 مرات.",
            "en": "Negative sample. Single negative doesn't exclude (50-60% sensitivity). Repeat x3."
        },
        "funny": {
            "fr": "Rien à signaler! Mais les parasites sont des maîtres du cache-cache!",
            "ar": "لا شيء يذكر! لكن الطفيليات أساتذة في الاختباء!",
            "en": "Nothing to report! But parasites are hide-and-seek masters!"
        },
        "risk": "none",
        "risk_d": {"fr": "Négatif", "ar": "سلبي", "en": "Negative"},
        "advice": {
            "fr": "RAS. Répéter x3 si suspicion clinique.",
            "ar": "لا شيء. كرر 3 مرات إذا كان هناك اشتباه.",
            "en": "Clear. Repeat x3 if clinical suspicion."
        },
        "tests": ["Repeat EPS x3", "Targeted serology", "FBC (eosinophilia check)"],
        "color": "#00ff88",
        "icon": "🟢",
        "cycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "keys": {
            "fr": "Direct+Lugol négatif\nConcentration négative\nRépéter x3",
            "ar": "مباشر+لوغول سلبي\nتركيز سلبي\nكرر 3 مرات",
            "en": "Direct+Lugol negative\nConcentration negative\nRepeat x3"
        }
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())

# ════════════════════════════════════════════════════════════════════════════════════
#  TIPS (CONSEIL DU JOUR)
# ════════════════════════════════════════════════════════════════════════════════════

TIPS = {
    "fr": [
        "Examiner les selles dans les 30 min pour voir les trophozoïtes mobiles.",
        "Le Lugol met en évidence les noyaux des kystes. Fraîchement préparé!",
        "Frottis mince: angle 45 degrés pour monocouche parfaite.",
        "Goutte épaisse = 10x plus sensible que frottis mince.",
        "Urines de midi pour S. haematobium (pic d'excrétion).",
        "Répéter EPS x3 à quelques jours d'intervalle.",
        "Métronidazole = Amoeba + Giardia + Trichomonas!",
        "ZN modifié indispensable pour Cryptosporidium.",
        "1ère GE négative ne suffit pas. Répéter à 6-12h.",
        "Éosinophilie = helminthiase. Toujours vérifier!",
        "Kyste vs trophozoite: état des selles (formées vs liquides).",
        "Immersion à l'huile obligatoire pour x100.",
        "Scotch-test MATIN avant toilette pour Oxyures.",
        "Giemsa pour parasites sanguins, pas pour intestinaux.",
        "Technique stérile indispensable pour LCR et liquides.",
        "Concentration Ritchie RÉFÉRENCE pour sensibilité.",
        "Formol 10% minimum pour fixation.",
        "Microscope entretenu = diagnostics fiables.",
        "Contrôle qualité internes obligatoires.",
        "Traçabilité des échantillons CRITIQUE!",
    ],
    "ar": [
        "افحص البراز خلال 30 دقيقة لرؤية الأطوار النشطة المتحركة.",
        "اللوغول يظهر أنوية الأكياس. تحضير طازج!",
        "القطرة السميكة أكثر حساسية 10 مرات من اللطاخة.",
        "بول الظهيرة لـ S. haematobium.",
        "كرر EPS 3 مرات بفاصل عدة أيام.",
        "ميترونيدازول = أميبا + جيارديا + تريكوموناس!",
        "الزيت الغاطس إجباري لـ x100.",
        "الصيانة الدورية للمجهر ضرورية.",
    ],
    "en": [
        "Examine stool within 30 min to see motile trophozoites.",
        "Lugol highlights cyst nuclei. Freshly prepared!",
        "Thick drop = 10x more sensitive than thin smear.",
        "Midday urine for S. haematobium.",
        "Repeat stool exam x3 at intervals.",
        "Metronidazole = Amoeba + Giardia + Trichomonas!",
        "Immersion oil mandatory for x100.",
        "Regular microscope maintenance ensures reliability.",
    ]
}

# ════════════════════════════════════════════════════════════════════════════════════
#  QUIZ QUESTIONS (COMPLETE 30+ QUESTIONS)
# ════════════════════════════════════════════════════════════════════════════════════

def create_quiz_questions():
    return [
        {"q": {"fr": "Quel parasite présente une bague à chaton dans les hématies?", "ar": "أي طفيلي يظهر شكل الخاتم في كريات الدم الحمراء؟", "en": "Which parasite shows a signet ring in RBCs?"}, "opts": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "ans": 1, "cat": "Hematozoaires", "expl": {"fr": "Plasmodium: bague à chaton au stade trophozoïte jeune.", "ar": "البلازموديوم: شكل الخاتم في مرحلة الطور النشط.", "en": "Plasmodium: signet ring at young trophozoite stage."}},
        {"q": {"fr": "Le kyste mature de Giardia possède combien de noyaux?", "ar": "كم عدد أنوية كيس الجيارديا الناضج؟", "en": "How many nuclei does a mature Giardia cyst have?"}, "opts": ["2", "4", "6", "8"], "ans": 1, "cat": "Protozoaires", "expl": {"fr": "4 noyaux. Le trophozoïte en a 2.", "ar": "4 أنوية. الطور النشط له نواتان.", "en": "4 nuclei. Trophozoite has 2."}},
        {"q": {"fr": "Quel parasite est transmis par le phlébotome?", "ar": "أي طفيلي ينتقل عبر ذبابة الرمل?", "en": "Which parasite is sandfly-transmitted?"}, "opts": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "ans": 2, "cat": "Vecteurs", "expl": {"fr": "Leishmania = phlébotome.", "ar": "ليشمانيا = ذبابة الرمل.", "en": "Leishmania = sandfly."}},
        {"q": {"fr": "L'éperon terminal caractérise:", "ar": "الشوكة الطرفية تميز:", "en": "Terminal spine characterizes:"}, "opts": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "ans": 1, "cat": "Helminthes", "expl": {"fr": "S. haematobium=terminal, S. mansoni=latéral.", "ar": "S. haematobium=طرفية, S. mansoni=جانبية.", "en": "S. haematobium=terminal, S. mansoni=lateral."}},
        {"q": {"fr": "Examen urgent suspicion paludisme?", "ar": "الفحص الطارئ عند الاشتباه بالملاريا?", "en": "Urgent exam for malaria?"}, "opts": ["Coproculture", "ECBU", "Goutte épaisse+Frottis", "Sérologie"], "ans": 2, "cat": "Diagnostic", "expl": {"fr": "GE+Frottis = référence urgente.", "ar": "قطرة سميكة+لطاخة = المرجع.", "en": "Thick drop+Smear = urgent reference."}},
        {"q": {"fr": "E. histolytica se distingue par:", "ar": "يتميز E. histolytica بـ:", "en": "E. histolytica distinguished by:"}, "opts": ["Flagelles", "Hématies phagocytées", "Membrane ondulante", "Kinétoplaste"], "ans": 1, "cat": "Morphologie", "expl": {"fr": "Hématies phagocytées = pathogénicité.", "ar": "الكريات المبتلعة = معيار المرضية.", "en": "Phagocytosed RBCs = pathogenicity."}},
        {"q": {"fr": "Chagas est causée par:", "ar": "مرض شاغاس يسببه:", "en": "Chagas is caused by:"}, "opts": ["T. b. gambiense", "T. cruzi", "L. donovani", "P. vivax"], "ans": 1, "cat": "Protozoaires", "expl": {"fr": "T. cruzi transmis par triatomes.", "ar": "T. cruzi عبر البق الثلاثي.", "en": "T. cruzi by triatomines."}},
        {"q": {"fr": "Colorant pour amastigotes Leishmania?", "ar": "ملون أماستيغوت الليشمانيا?", "en": "Stain for Leishmania amastigotes?"}, "opts": ["Ziehl-Neelsen", "Gram", "MGG/Giemsa", "Lugol"], "ans": 2, "cat": "Techniques", "expl": {"fr": "MGG = noyau + kinétoplaste.", "ar": "MGG = نواة + كينيتوبلاست.", "en": "MGG = nucleus + kinetoplast."}},
        {"q": {"fr": "Traitement référence bilharziose?", "ar": "العلاج المرجعي للبلهارسيا?", "en": "Reference treatment schistosomiasis?"}, "opts": ["Chloroquine", "Métronidazole", "Praziquantel", "Albendazole"], "ans": 2, "cat": "Thérapeutique", "expl": {"fr": "Praziquantel = choix numéro 1.", "ar": "برازيكوانتيل = الخيار الأول.", "en": "Praziquantel = 1st choice."}},
        {"q": {"fr": "Face de hibou observée chez:", "ar": "وجه البومة عند:", "en": "Owl face observed in:"}, "opts": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "ans": 1, "cat": "Morphologie", "expl": {"fr": "2 noyaux symétriques Giardia.", "ar": "نواتان متماثلتان للجيارديا.", "en": "2 symmetrical Giardia nuclei."}},
        {"q": {"fr": "Technique de Ritchie:", "ar": "تقنية ريتشي:", "en": "Ritchie technique:"}, "opts": ["Coloration", "Concentration diphasique", "Culture", "Sérologie"], "ans": 1, "cat": "Techniques", "expl": {"fr": "Formol-éther = concentration.", "ar": "فورمول-إيثر = تركيز.", "en": "Formalin-ether = concentration."}},
        {"q": {"fr": "Le Lugol met en évidence:", "ar": "اللوغول يظهر:", "en": "Lugol highlights:"}, "opts": ["Flagelles", "Noyaux des kystes", "Hématies", "Bactéries"], "ans": 1, "cat": "Techniques", "expl": {"fr": "Iode colore glycogène et noyaux.", "ar": "اليود يلون الغليكوجين والأنوية.", "en": "Iodine stains glycogen+nuclei."}},
        {"q": {"fr": "x100 nécessite:", "ar": "العدسة x100 تحتاج:", "en": "x100 requires:"}, "opts": ["Eau", "Huile d'immersion", "Alcool", "Sérum"], "ans": 1, "cat": "Microscopie", "expl": {"fr": "Huile augmente indice réfraction.", "ar": "الزيت يزيد معامل الانكسار.", "en": "Oil increases refractive index."}},
        {"q": {"fr": "Scotch-test Graham recherche:", "ar": "اختبار غراهام يبحث عن:", "en": "Graham test looks for:"}, "opts": ["Giardia", "Enterobius", "Ascaris", "Taenia"], "ans": 1, "cat": "Techniques", "expl": {"fr": "Œufs d'oxyure péri-anaux.", "ar": "بيض الأكسيور حول الشرج.", "en": "Pinworm eggs perianal."}},
        {"q": {"fr": "Coloration Cryptosporidium?", "ar": "تلوين الكريبتوسبوريديوم?", "en": "Cryptosporidium staining?"}, "opts": ["Lugol", "Ziehl-Neelsen modifié", "MGG", "Gram"], "ans": 1, "cat": "Techniques", "expl": {"fr": "ZN modifié = oocystes roses.", "ar": "ZN معدل = أكياس بيضية وردية.", "en": "Modified ZN = pink oocysts."}},
        {"q": {"fr": "Œuf d'Ascaris:", "ar": "بيضة الأسكاريس:", "en": "Ascaris egg:"}, "opts": ["Avec éperon", "Mamelonnée", "Opercule", "En citron"], "ans": 1, "cat": "Helminthes", "expl": {"fr": "Ovoïde, mamelonnée, coque épaisse.", "ar": "بيضاوي، حليمي، قشرة سميكة.", "en": "Ovoid, mammillated, thick shell."}},
        {"q": {"fr": "Scolex T. solium possède:", "ar": "رأس T. solium يحتوي:", "en": "T. solium scolex has:"}, "opts": ["Ventouses seules", "Crochets seuls", "Ventouses+crochets", "Bothridies"], "ans": 2, "cat": "Helminthes", "expl": {"fr": "Armée = ventouses + crochets.", "ar": "مسلحة = ممصات + خطاطيف.", "en": "Armed = suckers + hooks."}},
        {"q": {"fr": "Éosinophilie sanguine oriente vers:", "ar": "فرط الحمضات يوجه نحو:", "en": "Eosinophilia points to:"}, "opts": ["Bactéries", "Helminthiase", "Virose", "Paludisme"], "ans": 1, "cat": "Diagnostic", "expl": {"fr": "Éosinophilie = helminthiase.", "ar": "فرط الحمضات = ديدان.", "en": "Eosinophilia = helminthiasis."}},
        {"q": {"fr": "Vecteur du paludisme?", "ar": "ناقل الملاريا?", "en": "Malaria vector?"}, "opts": ["Aedes", "Culex", "Anopheles", "Simulium"], "ans": 2, "cat": "Épidémiologie", "expl": {"fr": "Anophèle femelle.", "ar": "أنثى الأنوفيل.", "en": "Female Anopheles."}},
        {"q": {"fr": "Kyste hydatique dû à:", "ar": "الكيس العداري يسببه:", "en": "Hydatid cyst caused by:"}, "opts": ["T. saginata", "E. granulosus", "Fasciola", "Toxocara"], "ans": 1, "cat": "Helminthes", "expl": {"fr": "Echinococcus granulosus (chien).", "ar": "Echinococcus granulosus (كلب).", "en": "Echinococcus granulosus (dog)."}},
        {"q": {"fr": "Membrane ondulante:", "ar": "الغشاء المتموج:", "en": "Undulating membrane:"}, "opts": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "ans": 1, "cat": "Morphologie", "expl": {"fr": "Trypanosoma = membrane ondulante.", "ar": "تريبانوسوما = غشاء متموج.", "en": "Trypanosoma = undulating membrane."}},
        {"q": {"fr": "Gamétocyte banane:", "ar": "خلية جنسية موز:", "en": "Banana gametocyte:"}, "opts": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "ans": 1, "cat": "Hematozoaires", "expl": {"fr": "Pathognomique P. falciparum.", "ar": "مميز لـ P. falciparum.", "en": "Pathognomonic P. falciparum."}},
        {"q": {"fr": "Kyste E. coli: noyaux?", "ar": "كيس E. coli: أنوية?", "en": "E. coli cyst: nuclei?"}, "opts": ["4", "6", "8", "12"], "ans": 2, "cat": "Morphologie", "expl": {"fr": "E. coli=8, E. histolytica=4.", "ar": "E. coli=8, E. histolytica=4.", "en": "E. coli=8, E. histolytica=4."}},
        {"q": {"fr": "Métronidazole inefficace contre:", "ar": "ميترونيدازول غير فعال ضد:", "en": "Metronidazole ineffective against:"}, "opts": ["E. histolytica", "Giardia", "Helminthes", "Trichomonas"], "ans": 2, "cat": "Thérapeutique", "expl": {"fr": "Anti-protozoaire, pas anti-helminthique.", "ar": "مضاد أوليات، ليس مضاد ديدان.", "en": "Anti-protozoal, not anti-helminthic."}},
        {"q": {"fr": "Albendazole est:", "ar": "الألبندازول:", "en": "Albendazole is:"}, "opts": ["Anti-protozoaire", "Anti-helminthique", "Antibiotique", "Antifongique"], "ans": 1, "cat": "Thérapeutique", "expl": {"fr": "Large spectre helminthes.", "ar": "واسع الطيف ضد الديدان.", "en": "Broad spectrum anti-helminthic."}},
        {"q": {"fr": "Paludisme grave:", "ar": "ملاريا خطيرة:", "en": "Severe malaria:"}, "opts": ["Chloroquine", "Artésunate IV", "Métronidazole", "Praziquantel"], "ans": 1, "cat": "Thérapeutique", "expl": {"fr": "Artésunate IV = 1ère ligne OMS.", "ar": "أرتيسونات وريدي = الخط الأول.", "en": "IV Artesunate = WHO 1st line."}},
        {"q": {"fr": "Fièvre+frissons retour Afrique?", "ar": "حمى+قشعريرة بعد العودة من إفريقيا?", "en": "Fever+chills returning from Africa?"}, "opts": ["Amibiase", "Paludisme", "Bilharziose", "Giardiose"], "ans": 1, "cat": "Cas clinique", "expl": {"fr": "Paludisme jusqu'à preuve du contraire.", "ar": "ملاريا حتى يثبت العكس.", "en": "Malaria until proven otherwise."}},
        {"q": {"fr": "Hématurie+baignade eau douce:", "ar": "بيلة دموية+سباحة ماء عذب:", "en": "Hematuria+freshwater swimming:"}, "opts": ["Giardiose", "Paludisme", "Bilharziose urinaire", "Amibiase"], "ans": 2, "cat": "Cas clinique", "expl": {"fr": "S. haematobium.", "ar": "S. haematobium.", "en": "S. haematobium."}},
        {"q": {"fr": "Diarrhée graisseuse enfant:", "ar": "إسهال دهني عند طفل:", "en": "Greasy diarrhea child:"}, "opts": ["Amibiase", "Giardiose", "Cryptosporidiose", "Salmonellose"], "ans": 1, "cat": "Cas clinique", "expl": {"fr": "Giardia = malabsorption fréquente.", "ar": "الجيارديا = سوء امتصاص شائع.", "en": "Giardia = common malabsorption."}},
        {"q": {"fr": "Toxoplasma: hôte définitif?", "ar": "التوكسوبلازما: المضيف النهائي?", "en": "Toxoplasma: definitive host?"}, "opts": ["Homme", "Chat", "Chien", "Moustique"], "ans": 1, "cat": "Épidémiologie", "expl": {"fr": "Chat = cycle sexué.", "ar": "القط = الدورة الجنسية.", "en": "Cat = sexual cycle."}},
    ]

QUIZ_QUESTIONS = create_quiz_questions()

# ════════════════════════════════════════════════════════════════════════════════════
#  CHATBOT KNOWLEDGE BASE (30+ RÉPONSES)
# ════════════════════════════════════════════════════════════════════════════════════

def create_chat_kb():
    kb = {}
    for pname, pdata in PARASITE_DB.items():
        if pname == "Negative":
            continue
        key = pname.lower().split("(")[0].strip().split(" ")[0].lower()
        kb[key] = {
            "fr": f"**{pname}** ({pdata['sci']})\n\n**Morphologie:** {pdata['morph'].get('fr','')}\n\n**Description:** {pdata['desc'].get('fr','')}\n\n**Traitement:** {pdata['advice'].get('fr','')}\n\n**Examens:** {', '.join(pdata.get('tests',[]))}\n\n{pdata['funny'].get('fr','')}",
            "ar": f"**{pname}** ({pdata['sci']})\n\n**المورفولوجيا:** {pdata['morph'].get('ar','')}\n\n**الوصف:** {pdata['desc'].get('ar','')}\n\n**العلاج:** {pdata['advice'].get('ar','')}\n\n{pdata['funny'].get('ar','')}",
            "en": f"**{pname}** ({pdata['sci']})\n\n**Morphology:** {pdata['morph'].get('en','')}\n\n**Description:** {pdata['desc'].get('en','')}\n\n**Treatment:** {pdata['advice'].get('en','')}\n\n{pdata['funny'].get('en','')}"
        }
    
    kb.update({
        "microscope": {
            "fr": "**Microscopie:**\n\n- **x10:** Repérage\n- **x40:** Œufs/kystes\n- **x100 (immersion):** Plasmodium, Leishmania\n\nNettoyer l'objectif x100 après l'huile!\n\n**Types:** Optique, Fluorescence, Contraste de phase, Fond noir, Confocal",
            "ar": "**المجهرية:**\n\n- **x10:** استطلاع\n- **x40:** بيض/أكياس\n- **x100 (غمر):** بلازموديوم، ليشمانيا\n\nنظف العدسة x100 بعد الزيت!",
            "en": "**Microscopy:**\n\n- **x10:** Survey\n- **x40:** Eggs/cysts\n- **x100 (immersion):** Plasmodium, Leishmania\n\nClean x100 after oil!"
        },
        "coloration": {
            "fr": "**Colorations:**\n\n- **Lugol:** Noyaux kystes, glycogène\n- **MGG/Giemsa:** Parasites sanguins\n- **Ziehl-Neelsen modifié:** Cryptosporidium\n- **Trichrome:** Parasites intestinaux\n- **Hématoxyline ferrique:** Amibes\n\nLugol frais chaque semaine!",
            "ar": "**التلوينات:**\n\n- **لوغول:** أنوية الأكياس\n- **MGG/جيمزا:** طفيليات الدم\n- **ZN معدل:** كريبتوسبوريديوم",
            "en": "**Staining:**\n\n- **Lugol:** Cyst nuclei\n- **MGG/Giemsa:** Blood parasites\n- **Modified ZN:** Cryptosporidium"
        },
        "concentration": {
            "fr": "**Techniques concentration:**\n\n- **Ritchie (Formol-éther):** RÉFÉRENCE\n- **Willis (NaCl saturé):** Flottation\n- **Kato-Katz:** Semi-quantitatif\n- **Baermann:** Larves Strongyloides\n- **MIF:** Fixation+coloration",
            "ar": "**تقنيات التركيز:**\n\n- **ريتشي:** المرجع\n- **ويليس:** تعويم\n- **كاتو-كاتز:** شبه كمي",
            "en": "**Concentration:**\n\n- **Ritchie:** REFERENCE\n- **Willis:** Flotation\n- **Kato-Katz:** Semi-quantitative"
        },
        "selle": {
            "fr": "**EPS Complet:**\n\n1. **Macroscopique:** Consistance, couleur, sang, mucus\n2. **Direct:** NaCl 0.9% + Lugol\n3. **Concentration:** Ritchie/Willis\n\nExaminer dans 30 min!\nRépéter x3!\n\nSelles liquides = trophozoïtes, Formées = kystes",
            "ar": "**فحص البراز:**\n\n1. عياني\n2. مباشر: NaCl + لوغول\n3. تركيز: ريتشي/ويليس\n\nفحص خلال 30 دقيقة!\nكرر 3 مرات!",
            "en": "**Complete Stool Exam:**\n\n1. Macroscopic\n2. Direct: NaCl + Lugol\n3. Concentration: Ritchie/Willis\n\nExamine within 30 min!\nRepeat x3!"
        },
        "hygiene": {
            "fr": "**Prévention:**\n\n- Lavage mains 30s\n- Eau potable\n- Cuisson viande plus de 65°C\n- Moustiquaires\n- Éviter eaux stagnantes\n- Lavage fruits/légumes\n\n80% des parasitoses sont évitables!",
            "ar": "**الوقاية:**\n\n- غسل اليدين 30 ثانية\n- ماء صالح للشرب\n- طهي اللحم أكثر من 65 درجة\n- ناموسيات\n\n80% من الطفيليات يمكن الوقاية منها!",
            "en": "**Prevention:**\n\n- Handwashing 30s\n- Safe water\n- Cook meat over 65C\n- Mosquito nets\n\n80% of parasitoses are preventable!"
        },
        "traitement": {
            "fr": "**Traitements:**\n\n- **Métronidazole:** Amoeba+Giardia+Trichomonas\n- **Albendazole:** Helminthes large spectre\n- **Praziquantel:** Schistosoma+Cestodes\n- **Artésunate/ACT:** Paludisme\n- **Glucantime:** Leishmaniose cutanée\n- **Ivermectine:** Filarioses\n- **Niclosamide:** Tenias",
            "ar": "**العلاجات:**\n\n- **ميترونيدازول:** أميبا+جيارديا\n- **ألبندازول:** ديدان\n- **برازيكوانتيل:** بلهارسيا+شريطيات\n- **أرتيسونات:** ملاريا",
            "en": "**Treatments:**\n\n- **Metronidazole:** Amoeba+Giardia+Trichomonas\n- **Albendazole:** Broad spectrum helminths\n- **Praziquantel:** Schistosoma+Cestodes\n- **Artesunate/ACT:** Malaria"
        },
        "aide": {
            "fr": "**Je connais:**\n\nParasites: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Toxoplasma, Ascaris, Taenia, Oxyure, Cryptosporidium...\n\nTechniques: microscope, coloration, concentration, selle\n\nTraitements: traitement\n\nPrévention: hygiene\n\nTapez un mot-clé!",
            "ar": "**أعرف:**\n\nالطفيليات: الأميبا، الجيارديا، البلازموديوم، الليشمانيا...\n\nالتقنيات: microscope, coloration, concentration\n\nاكتب كلمة مفتاحية!",
            "en": "**I know:**\n\nParasites: Amoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma...\n\nTechniques: microscope, staining, concentration\n\nType a keyword!"
        },
        "bonjour": {"fr": "Bonjour! Comment puis-je vous aider?", "ar": "مرحبا! كيف أقدر أساعدك؟", "en": "Hello! How can I help?"},
        "merci": {"fr": "De rien!", "ar": "عفوا!", "en": "You're welcome!"},
    })
    
    return kb

CHAT_KB = create_chat_kb()

def chatbot_reply(msg: str) -> str:
    """Réponse du chatbot intelligent"""
    lang = st.session_state.get("lang", "fr")
    low = msg.lower().strip()
    
    for key, resp in CHAT_KB.items():
        if key in low:
            if isinstance(resp, dict):
                return resp.get(lang, resp.get("fr", str(resp)))
            return str(resp)
    
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

# ════════════════════════════════════════════════════════════════════════════════════
#  SESSION STATE INITIALIZATION
# ════════════════════════════════════════════════════════════════════════════════════

DEFAULTS = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_role": "viewer",
    "user_full_name": "",
    "lang": "fr",
    "theme": "dark",
    "demo_seed": None,
    "heatmap_seed": None,
    "quiz_state": {
        "current": 0,
        "score": 0,
        "answered": [],
        "active": False,
        "order": [],
        "wrong": [],
        "total_q": 0,
        "finished": False,
        "selected_answer": None,
        "show_result": False
    },
    "chat_history": [],
    "voice_text": None,
    "voice_lang": None,
    "_ih": None,
    "page": "home",
    "notifications": [],
    "bookmarks": [],
    "search_history": [],
    "session_start": datetime.now().isoformat(),
    "last_activity": datetime.now().isoformat(),
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ════════════════════════════════════════════════════════════════════════════════════
#  DATABASE MODULE
# ════════════════════════════════════════════════════════════════════════════════════

@contextmanager
def get_db():
    """Context manager pour la base de données"""
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_database():
    """Initialiser la base de données"""
    with get_db() as c:
        # Table users
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'viewer',
            speciality TEXT DEFAULT 'Laboratoire',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            preferences TEXT
        )""")
        
        # Table analyses
        c.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            patient_firstname TEXT,
            patient_age INTEGER,
            patient_sex TEXT,
            patient_weight REAL,
            patient_height REAL,
            sample_type TEXT,
            microscope_type TEXT,
            magnification TEXT,
            preparation_type TEXT,
            technician1 TEXT,
            technician2 TEXT,
            notes TEXT,
            parasite_detected TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT,
            is_reliable INTEGER,
            all_predictions TEXT,
            image_hash TEXT,
            is_demo INTEGER DEFAULT 0,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            validated INTEGER DEFAULT 0,
            validated_by TEXT,
            validation_date TIMESTAMP,
            report_path TEXT,
            quality_score REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Table activity_log
        c.execute("""CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Table quiz_scores
        c.execute("""CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            category TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Table bookmarks
        c.execute("""CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_id INTEGER,
            bookmark_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (analysis_id) REFERENCES analyses(id)
        )""")
        
        # Table system_config
        c.execute("""CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            config_key TEXT UNIQUE,
            config_value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        _make_defaults(c)

def _hp(pw: str) -> str:
    """Hash password"""
    if HAS_BCRYPT:
        return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    return hashlib.sha256((pw + SECRET_KEY).encode()).hexdigest()

def _vp(pw: str, h: str) -> bool:
    """Verify password"""
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(pw.encode(), h.encode())
        except Exception:
            pass
    return hashlib.sha256((pw + SECRET_KEY).encode()).hexdigest() == h

def _make_defaults(c):
    """Créer les utilisateurs par défaut"""
    for u, p, n, r, s in [
        ("admin", "admin2026", "Administrateur Système", "admin", "Administration"),
        ("dhia", "dhia2026", "Sebbag Mohamed Dhia Eddine", "admin", "IA & Conception"),
        ("mohamed", "mohamed2026", "Ben Sghir Mohamed", "technician", "Laboratoire"),
        ("demo", "demo123", "Utilisateur Démo", "viewer", "Démonstration"),
        ("tech1", "tech2026", "Technicien Labo 1", "technician", "Parasitologie"),
        ("tech2", "tech2026", "Technicien Labo 2", "technician", "Parasitologie"),
    ]:
        if not c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            c.execute("""INSERT INTO users(username,password_hash,full_name,role,speciality)
                        VALUES(?,?,?,?,?)""",
                      (u, _hp(p), n, r, s))

def db_login(u: str, p: str) -> Optional[Dict]:
    """Authentification utilisateur"""
    with get_db() as c:
        row = c.execute(
            "SELECT * FROM users WHERE username=? AND is_active=1", (u,)
        ).fetchone()
        
        if not row:
            return None
        
        # Vérifier le verrouillage
        if row["locked_until"]:
            try:
                if datetime.now() < datetime.fromisoformat(row["locked_until"]):
                    return {"error": "locked"}
                c.execute("UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?",
                          (row["id"],))
            except Exception:
                pass
        
        # Vérifier le mot de passe
        if _vp(p, row["password_hash"]):
            c.execute("""UPDATE users
                        SET last_login=?,login_count=login_count+1,failed_attempts=0,locked_until=NULL
                        WHERE id=?""",
                      (datetime.now().isoformat(), row["id"]))
            return dict(row)
        
        # Incrémenter les tentatives échouées
        na = row["failed_attempts"] + 1
        lk = None
        if na >= MAX_LOGIN_ATTEMPTS:
            lk = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
        
        c.execute("UPDATE users SET failed_attempts=?,locked_until=? WHERE id=?",
                  (na, lk, row["id"]))
        
        return {"error": "wrong", "left": MAX_LOGIN_ATTEMPTS - na}

def db_create_user(u: str, p: str, n: str, r: str = "viewer", s: str = "") -> bool:
    """Créer un nouvel utilisateur"""
    with get_db() as c:
        if c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            return False
        c.execute("""INSERT INTO users(username,password_hash,full_name,role,speciality)
                    VALUES(?,?,?,?,?)""",
                  (u, _hp(p), n, r, s))
        return True

def db_users() -> List[Dict]:
    """Récupérer tous les utilisateurs"""
    with get_db() as c:
        return [dict(r) for r in c.execute(
            "SELECT id,username,full_name,role,is_active,last_login,login_count,speciality FROM users"
        ).fetchall()]

def db_toggle(uid: int, active: bool):
    """Activer/Désactiver un utilisateur"""
    with get_db() as c:
        c.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, uid))

def db_chpw(uid: int, pw: str):
    """Changer le mot de passe"""
    with get_db() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (_hp(pw), uid))

def db_save_analysis(uid: int, d: Dict) -> int:
    """Sauvegarder une analyse"""
    with get_db() as c:
        c.execute("""INSERT INTO analyses(
            user_id,patient_name,patient_firstname,patient_age,patient_sex,
            patient_weight,patient_height,sample_type,microscope_type,magnification,
            preparation_type,technician1,technician2,notes,parasite_detected,confidence,
            risk_level,is_reliable,all_predictions,image_hash,is_demo
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (uid, d.get("pn", ""), d.get("pf", ""), d.get("pa", 0), d.get("ps", ""),
                   d.get("pw", 0), d.get("ph", 0), d.get("st", ""), d.get("mt", ""), d.get("mg", ""),
                   d.get("pt", ""), d.get("t1", ""), d.get("t2", ""), d.get("nt", ""),
                   d.get("label", "Negative"), d.get("conf", 0), d.get("risk", "none"),
                   d.get("rel", 0), json.dumps(d.get("preds", {})), d.get("hash", ""),
                   d.get("demo", 0)))
        return c.execute("SELECT last_insert_rowid()").fetchone()[0]

def db_analyses(uid: Optional[int] = None, lim: int = 500) -> List[Dict]:
    """Récupérer les analyses"""
    with get_db() as c:
        if uid:
            q = """SELECT a.*,u.full_name as analyst FROM analyses a
                  JOIN users u ON a.user_id=u.id
                  WHERE a.user_id=? ORDER BY a.analysis_date DESC LIMIT ?"""
            rows = c.execute(q, (uid, lim)).fetchall()
        else:
            q = """SELECT a.*,u.full_name as analyst FROM analyses a
                  JOIN users u ON a.user_id=u.id
                  ORDER BY a.analysis_date DESC LIMIT ?"""
            rows = c.execute(q, (lim,)).fetchall()
        return [dict(r) for r in rows]

def db_stats(uid: Optional[int] = None) -> Dict:
    """Récupérer les statistiques"""
    with get_db() as c:
        w = "WHERE user_id=?" if uid else ""
        p = (uid,) if uid else ()
        
        tot = c.execute(f"SELECT COUNT(*) FROM analyses {w}", p).fetchone()[0]
        if uid:
            rel = c.execute(
                "SELECT COUNT(*) FROM analyses WHERE user_id=? AND is_reliable=1",
                (uid,)
            ).fetchone()[0]
        else:
            rel = c.execute(
                "SELECT COUNT(*) FROM analyses WHERE is_reliable=1"
            ).fetchone()[0]
        
        para = c.execute(f"""SELECT parasite_detected,COUNT(*) as n FROM analyses {w}
                           GROUP BY parasite_detected ORDER BY n DESC""", p).fetchall()
        
        avg = c.execute(f"SELECT AVG(confidence) FROM analyses {w}", p).fetchone()[0] or 0
        
        return {
            "total": tot,
            "reliable": rel,
            "verify": tot - rel,
            "parasites": [dict(x) for x in para],
            "avg": round(avg, 1),
            "top": para[0]["parasite_detected"] if para else "N/A"
        }

def db_trends(days: int = 30) -> List[Dict]:
    """Récupérer les tendances"""
    with get_db() as c:
        return [dict(r) for r in c.execute("""
            SELECT DATE(analysis_date) as day,parasite_detected,COUNT(*) as count,
                   AVG(confidence) as avg_conf
            FROM analyses WHERE analysis_date>=date('now',?)
            GROUP BY day,parasite_detected ORDER BY day
        """, (f"-{days} days",)).fetchall()]

def db_log(uid: Optional[int], uname: str, action: str, details: str = ""):
    """Logger une action"""
    try:
        with get_db() as c:
            c.execute("""INSERT INTO activity_log(user_id,username,action,details)
                        VALUES(?,?,?,?)""",
                      (uid, uname, action, details))
    except Exception:
        pass

def db_logs(lim: int = 300) -> List[Dict]:
    """Récupérer les logs"""
    with get_db() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (lim,)
        ).fetchall()]

def db_quiz_save(uid: int, un: str, sc: int, tot: int, pct: float, cat: str = "general"):
    """Sauvegarder un score de quiz"""
    with get_db() as c:
        c.execute("""INSERT INTO quiz_scores(user_id,username,score,total_questions,percentage,category)
                    VALUES(?,?,?,?,?,?)""",
                  (uid, un, sc, tot, pct, cat))

def db_leaderboard(lim: int = 20) -> List[Dict]:
    """Récupérer le classement"""
    with get_db() as c:
        return [dict(r) for r in c.execute(
            """SELECT username,score,total_questions,percentage,timestamp
              FROM quiz_scores ORDER BY percentage DESC,timestamp ASC LIMIT ?""",
            (lim,)
        ).fetchall()]

def db_validate(aid: int, who: str):
    """Valider une analyse"""
    with get_db() as c:
        c.execute("""UPDATE analyses SET validated=1,validated_by=?,validation_date=? WHERE id=?""",
                  (who, datetime.now().isoformat(), aid))

init_database()

# ════════════════════════════════════════════════════════════════════════════════════
#  CSS STYLING (SPACE DARK THEME WITH ANIMATIONS)
# ════════════════════════════════════════════════════════════════════════════════════

def apply_css():
    """Appliquer le thème CSS"""
    rtl = st.session_state.get("lang") == "ar"
    d = "rtl" if rtl else "ltr"
    
    bg = "#030614"
    cbg = "rgba(10,15,46,0.85)"
    tx = "#e0e8ff"
    pr = "#00f5ff"
    mu = "#6b7fa0"
    ac = "#ff00ff"
    ac2 = "#00ff88"
    sbg = "#020410"
    btn_bg = "linear-gradient(135deg,#00f5ff,#0066ff)"
    brd = "rgba(0,245,255,0.15)"
    ibg = "rgba(10,15,46,0.6)"
    
    st.markdown(f"""<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;600&family=Tajawal:wght@400;500;700;800&display=swap');
    
    html {{ direction: {d}; }}
    
    /* ====== ANIMATED SPACE BACKGROUND ====== */
    .stApp {{
        background: {bg} !important;
        color: {tx} !important;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(0,245,255,0.3), transparent),
            radial-gradient(2px 2px at 40px 70px, rgba(255,0,255,0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(0,255,136,0.3), transparent),
            radial-gradient(1px 1px at 130px 80px, rgba(0,245,255,0.2), transparent),
            radial-gradient(2px 2px at 160px 30px, rgba(255,0,255,0.15), transparent),
            radial-gradient(1px 1px at 200px 60px, rgba(0,255,136,0.2), transparent);
        background-size: 250px 150px;
        animation: sparkle 8s linear infinite;
    }}
    
    @keyframes sparkle {{
        0% {{ background-position: 0 0; }}
        100% {{ background-position: 250px 150px; }}
    }}
    
    /* ====== SIDEBAR ====== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sbg} 0%, rgba(5,10,30,0.98) 100%) !important;
        border-right: 1px solid rgba(0,245,255,0.1) !important;
    }}
    section[data-testid="stSidebar"] * {{ color: {tx} !important; }}
    
    /* ====== TEXT ====== */
    .stApp p, .stApp span, .stApp label, .stApp div {{ color: {tx} !important; }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{ color: {tx} !important; }}
    
    /* ====== INPUTS ====== */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background: {ibg} !important;
        color: {tx} !important;
        border: 1px solid {brd} !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
    }}
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {pr} !important;
        box-shadow: 0 0 15px rgba(0,245,255,0.2) !important;
    }}
    
    /* ====== SELECTBOX ====== */
    .stSelectbox > div > div {{
        background: {ibg} !important;
        border: 1px solid {brd} !important;
        border-radius: 12px !important;
    }}
    
    /* ====== CARDS ====== */
    .dm-card {{
        background: {cbg};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {brd};
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: {tx} !important;
        position: relative;
        overflow: hidden;
    }}
    .dm-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(0,245,255,0.03), transparent);
        transition: left 0.6s ease;
    }}
    .dm-card:hover::before {{
        left: 100%;
    }}
    .dm-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,245,255,0.1), 0 4px 15px rgba(255,0,255,0.05);
        border-color: rgba(0,245,255,0.3);
    }}
    .dm-card * {{ color: {tx} !important; }}
    
    /* ====== METRIC CARDS ====== */
    .dm-m {{
        background: {cbg};
        border: 1px solid {brd};
        border-radius: 18px;
        padding: 20px 12px;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }}
    .dm-m:hover {{
        border-color: {pr};
        box-shadow: 0 0 20px rgba(0,245,255,0.1);
    }}
    .dm-m-i {{ font-size: 1.6rem; }}
    .dm-m-v {{
        font-size: 1.8rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace !important;
        background: linear-gradient(135deg, {pr}, {ac});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: glow-text 3s ease-in-out infinite;
    }}
    @keyframes glow-text {{
        0%, 100% {{ filter: brightness(1); }}
        50% {{ filter: brightness(1.3); }}
    }}
    .dm-m-l {{
        font-size: .7rem;
        font-weight: 600;
        color: {mu} !important;
        -webkit-text-fill-color: {mu} !important;
        text-transform: uppercase;
        letter-spacing: .1em;
        margin-top: 6px;
    }}
    
    /* ====== BUTTONS ====== */
    div.stButton > button {{
        background: {btn_bg} !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.03em !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
    }}
    div.stButton > button::before {{
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent) !important;
        transition: left 0.5s ease !important;
    }}
    div.stButton > button:hover::before {{
        left: 100% !important;
    }}
    div.stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0,245,255,0.3), 0 0 40px rgba(0,102,255,0.15) !important;
    }}
    div.stButton > button * {{
        color: white !important;
        -webkit-text-fill-color: white !important;
    }}
    
    /* ====== NEON TITLE ====== */
    .dm-nt {{
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        background: linear-gradient(135deg, {pr}, {ac}, {ac2});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: gradient-shift 4s ease infinite;
    }}
    @keyframes gradient-shift {{
        0% {{ background-position: 0% center; }}
        50% {{ background-position: 100% center; }}
        100% {{ background-position: 0% center; }}
    }}
    
    /* ====== SCROLLBAR ====== */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    ::-webkit-scrollbar-track {{
        background: {bg};
    }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {pr}, {ac});
        border-radius: 10px;
    }}
    
    /* ====== EXPANDER ====== */
    .streamlit-expanderHeader {{
        background: rgba(10,15,46,0.5) !important;
        border-radius: 12px !important;
        border: 1px solid {brd} !important;
    }}
    
    /* ====== TABS ====== */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: rgba(10,15,46,0.5);
        border-radius: 14px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px;
        color: {tx} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(0,245,255,0.2), rgba(0,102,255,0.2)) !important;
    }}
    
    /* ====== PROGRESS BAR ====== */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {pr}, {ac}, {ac2}) !important;
        border-radius: 10px !important;
    }}
    
    /* ====== DATAFRAME ====== */
    .stDataFrame {{
        border-radius: 14px !important;
        overflow: hidden !important;
    }}
    
    /* ====== RTL SUPPORT ====== */
    {"body {{ font-family: 'Tajawal', sans-serif !important; }}" if rtl else ""}
    
    </style>""", unsafe_allow_html=True)

apply_css()

# ════════════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════════════

def has_role(lvl: int) -> bool:
    """Vérifier le niveau de rôle"""
    return ROLES.get(st.session_state.get("user_role", "viewer"), {}).get("level", 0) >= lvl

def risk_color(lv: str) -> str:
    """Couleur du risque"""
    return COLORS_RISK.get(lv, "#888")

def risk_pct(lv: str) -> int:
    """Pourcentage du risque"""
    return {"critical": 100, "high": 80, "medium": 50, "low": 25, "none": 0}.get(lv, 0)

def format_date(dt: datetime) -> str:
    """Formater une date"""
    lang = st.session_state.get("lang", "fr")
    if lang == "ar":
        return dt.strftime("%Y-%m-%d %H:%M")
    return dt.strftime("%d/%m/%Y %H:%M")

def is_mobile() -> bool:
    """Vérifier si c'est mobile"""
    return False  # Simplifiée pour ce démo

# ════════════════════════════════════════════════════════════════════════════════════
#  IMAGE PROCESSING (15+ FILTERS)
# ════════════════════════════════════════════════════════════════════════════════════

def adjust(img: Image.Image, br: float = 1.0, co: float = 1.0, sa: float = 1.0) -> Image.Image:
    """Ajuster l'image"""
    r = img.copy()
    if br != 1.0:
        r = ImageEnhance.Brightness(r).enhance(br)
    if co != 1.0:
        r = ImageEnhance.Contrast(r).enhance(co)
    if sa != 1.0:
        r = ImageEnhance.Color(r).enhance(sa)
    return r

def zoom_img(img: Image.Image, lv: float) -> Image.Image:
    """Zoom l'image"""
    if lv <= 1.0:
        return img
    w, h = img.size
    nw, nh = int(w / lv), int(h / lv)
    l, tp = (w - nw) // 2, (h - nh) // 2
    return img.crop((l, tp, l + nw, tp + nh)).resize((w, h), Image.LANCZOS)

def thermal(img: Image.Image) -> Image.Image:
    """Filtre thermique"""
    return ImageOps.colorize(
        ImageOps.grayscale(ImageEnhance.Contrast(img).enhance(1.5)),
        black="navy", white="yellow", mid="red"
    )

def edges_filter(img: Image.Image) -> Image.Image:
    """Filtre des contours"""
    return ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)

def enhanced_filter(img: Image.Image) -> Image.Image:
    """Filtre amélioré"""
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(img).enhance(2.0)).enhance(2.0)

def negative_filter(img: Image.Image) -> Image.Image:
    """Filtre négatif"""
    return ImageOps.invert(img.convert("RGB"))

def emboss_filter(img: Image.Image) -> Image.Image:
    """Filtre relief"""
    return img.filter(ImageFilter.EMBOSS)

def blur_filter(img: Image.Image, radius: int = 5) -> Image.Image:
    """Filtre flou"""
    return img.filter(ImageFilter.GaussianBlur(radius=radius))

def sharpen_filter(img: Image.Image) -> Image.Image:
    """Filtre netteté"""
    return img.filter(ImageFilter.SHARPEN)

def detail_filter(img: Image.Image) -> Image.Image:
    """Filtre détail"""
    return img.filter(ImageFilter.DETAIL)

def smooth_filter(img: Image.Image) -> Image.Image:
    """Filtre lissage"""
    return img.filter(ImageFilter.SMOOTH)

def edge_enhance(img: Image.Image) -> Image.Image:
    """Amélioration des contours"""
    return img.filter(ImageFilter.EDGE_ENHANCE)

def gen_heatmap(img: Image.Image, seed: Optional[int] = None) -> Image.Image:
    """Générer une heatmap"""
    im = img.copy().convert("RGB")
    w, h = im.size
    if seed is None:
        seed = hash(im.tobytes()[:1000]) % 1000000
    rng = random.Random(seed)
    
    ea = np.array(ImageOps.grayscale(im).filter(ImageFilter.FIND_EDGES))
    bs, mx, bx, by = 32, 0, w // 2, h // 2
    
    for y in range(0, h - bs, bs // 2):
        for x in range(0, w - bs, bs // 2):
            s = np.mean(ea[y:y + bs, x:x + bs])
            if s > mx:
                mx, bx, by = s, x + bs // 2, y + bs // 2
    
    bx = max(50, min(w - 50, bx + rng.randint(-w // 10, w // 10)))
    by = max(50, min(h - 50, by + rng.randint(-h // 10, h // 10)))
    
    hm = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(hm)
    mr = min(w, h) // 3
    
    for r in range(mr, 0, -2):
        a = max(0, min(200, int(200 * (1 - r / mr))))
        rat = r / mr
        if rat > 0.65:
            c = (0, 255, 100, a // 4)
        elif rat > 0.35:
            c = (255, 255, 0, a // 2)
        else:
            c = (255, 0, 60, a)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=c)
    
    return Image.alpha_composite(im.convert('RGBA'), hm).convert('RGB')

def compare_imgs(i1: Image.Image, i2: Image.Image) -> Dict:
    """Comparer deux images"""
    a1 = np.array(i1.convert("RGB").resize((128, 128))).astype(float)
    a2 = np.array(i2.convert("RGB").resize((128, 128))).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    m1, m2, s1, s2 = np.mean(a1), np.mean(a2), np.std(a1), np.std(a2)
    s12 = np.mean((a1 - m1) * (a2 - m2))
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * m1 * m2 + c1) * (2 * s12 + c2)) / (
        (m1 ** 2 + m2 ** 2 + c1) * (s1 ** 2 + s2 ** 2 + c2)
    )
    return {"mse": round(mse, 2), "ssim": round(float(ssim), 4), "sim": round(float(ssim) * 100, 1)}

def pixel_diff(i1: Image.Image, i2: Image.Image) -> Image.Image:
    """Différence pixel"""
    a1 = np.array(i1.convert("RGB").resize((256, 256))).astype(float)
    a2 = np.array(i2.convert("RGB").resize((256, 256))).astype(float)
    diff = np.abs(a1 - a2).astype(np.uint8)
    diff = np.clip(diff * 3, 0, 255).astype(np.uint8)
    return Image.fromarray(diff)

def histogram(img: Image.Image) -> Dict:
    """Histogramme"""
    r, g, b = img.convert("RGB").split()
    return {"red": list(r.histogram()), "green": list(g.histogram()), "blue": list(b.histogram())}

# ════════════════════════════════════════════════════════════════════════════════════
#  AI ENGINE
# ════════════════════════════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner=False)
def load_model():
    """Charger le modèle IA"""
    m, mn, mt = None, None, None
    try:
        import tensorflow as tf
        for ext in [".keras", ".h5"]:
            ff = [f for f in os.listdir(".") if f.endswith(ext) and os.path.isfile(f)]
            if ff:
                mn = ff[0]
                m = tf.keras.models.load_model(mn, compile=False)
                mt = "keras"
                break
        if m is None:
            ff = [f for f in os.listdir(".") if f.endswith(".tflite") and os.path.isfile(f)]
            if ff:
                mn = ff[0]
                m = tf.lite.Interpreter(model_path=mn)
                m.allocate_tensors()
                mt = "tflite"
    except Exception:
        pass
    return m, mn, mt

def predict(model, mt, img: Image.Image, seed: Optional[int] = None) -> Dict:
    """Prédire le parasite"""
    res = {"label": "Negative", "conf": 0, "preds": {}, "rel": False, "demo": False, "risk": "none"}
    rm = {
        "Plasmodium": "critical",
        "Amoeba (E. histolytica)": "high",
        "Leishmania": "high",
        "Trypanosoma": "high",
        "Giardia": "medium",
        "Schistosoma": "medium",
        "Negative": "none"
    }
    
    if model is None:
        res["demo"] = True
        if seed is None:
            seed = random.randint(0, 999999)
        rng = random.Random(seed)
        lb = rng.choice(CLASS_NAMES)
        cf = rng.randint(55, 98)
        ap = {}
        rem = 100.0 - cf
        for c in CLASS_NAMES:
            ap[c] = float(cf) if c == lb else round(
                rng.uniform(0, rem / max(1, len(CLASS_NAMES) - 1)), 1
            )
        res.update({"label": lb, "conf": cf, "preds": ap, "rel": cf >= CONFIDENCE_THRESHOLD, "risk": rm.get(lb, "none")})
        return res
    
    try:
        import tensorflow as tf
        im = ImageOps.fit(img.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
        arr = np.expand_dims(np.asarray(im).astype(np.float32) / 127.5 - 1.0, 0)
        if mt == "tflite":
            inp, out = model.get_input_details(), model.get_output_details()
            model.set_tensor(inp[0]['index'], arr)
            model.invoke()
            pr = model.get_tensor(out[0]['index'])[0]
        else:
            pr = model.predict(arr, verbose=0)[0]
        ix = int(np.argmax(pr))
        cf = int(pr[ix] * 100)
        lb = CLASS_NAMES[ix] if ix < len(CLASS_NAMES) else "Negative"
        ap = {CLASS_NAMES[i]: round(float(pr[i]) * 100, 1) for i in range(min(len(pr), len(CLASS_NAMES)))}
        res.update({"label": lb, "conf": cf, "preds": ap, "rel": cf >= CONFIDENCE_THRESHOLD, "risk": rm.get(lb, "none")})
    except Exception as e:
        st.error(f"❌ {str(e)[:100]}")
    
    return res

# ════════════════════════════════════════════════════════════════════════════════════
#  PDF GENERATION
# ════════════════════════════════════════════════════════════════════════════════════

def _sp(text: str) -> str:
    """Convertir texte pour PDF"""
    if not text:
        return ""
    result = ""
    for c in str(text):
        if ord(c) < 128:
            result += c
        elif c in 'éèêë':
            result += 'e'
        elif c in 'àâä':
            result += 'a'
        elif c in 'ùûü':
            result += 'u'
        elif c in 'ôö':
            result += 'o'
        elif c in 'îï':
            result += 'i'
        elif c == 'ç':
            result += 'c'
        elif c == '→':
            result += '->'
        elif c == '°':
            result += 'o'
        else:
            result += '?'
    return result

class PDF(FPDF):
    """Classe PDF personnalisée"""
    
    def header(self):
        self.set_fill_color(0, 20, 60)
        self.rect(0, 0, 210, 4, 'F')
        self.set_fill_color(0, 180, 255)
        self.rect(0, 4, 210, 1, 'F')
        self.ln(8)
        
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 60, 150)
        self.cell(0, 8, f"DM SMART LAB AI v{APP_VERSION}", 0, 0, "L")
        self.set_font("Arial", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 0, 1, "R")
        
        self.set_font("Arial", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, "Diagnostic Parasitologique par Intelligence Artificielle", 0, 1, "L")
        self.cell(0, 4, f"{INSTITUTION['short']} - {INSTITUTION['city']}, {tl(INSTITUTION['country'])}", 0, 1, "L")
        
        self.set_draw_color(0, 180, 255)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        self.set_y(-20)
        self.set_fill_color(0, 20, 60)
        self.rect(0, 282, 210, 15, 'F')
        self.set_y(-15)
        self.set_font("Arial", "I", 7)
        self.set_text_color(200, 200, 200)
        self.cell(0, 4, _sp("AVERTISSEMENT: Rapport généré par IA - Validation par professionnel de santé requise"), 0, 1, "C")
        self.set_font("Arial", "", 6)
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}} | DM Smart Lab AI v{APP_VERSION} | Sebbag & Ben Sghir", 0, 0, "C")

    def section(self, title: str, color: Tuple = (0, 60, 150)):
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        self.cell(0, 8, f"  {_sp(title)}", 0, 1, "L", True)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def field(self, label: str, val):
        self.set_font("Arial", "B", 9)
        self.set_text_color(60, 60, 60)
        self.cell(55, 6, _sp(label), 0, 0)
        self.set_font("Arial", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, _sp(str(val)), 0, 1)

def make_pdf(pat: Dict, lab: Dict, result: Dict, lbl: str) -> bytes:
    """Générer un PDF"""
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(True, 25)

    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 40, 100)
    pdf.cell(0, 12, "RAPPORT D'ANALYSE PARASITOLOGIQUE", 0, 1, "C")

    rid = hashlib.md5(f"{pat.get('Nom', '')}{datetime.now().isoformat()}".encode()).hexdigest()[:10].upper()
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Référence: DM-{rid} | Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "R")
    pdf.ln(3)

    pdf.section("INFORMATIONS DU PATIENT")
    for k, v in pat.items():
        if v:
            pdf.field(f"{k}:", v)
    pdf.ln(5)

    pdf.section("INFORMATIONS LABORATOIRE", (0, 100, 80))
    for k, v in lab.items():
        if v:
            pdf.field(f"{k}:", v)
    pdf.ln(5)

    cf = result.get("conf", 0)
    if lbl == "Negative":
        pdf.section("RÉSULTAT DE L'ANALYSE IA", (0, 150, 80))
    else:
        pdf.section("RÉSULTAT DE L'ANALYSE IA", (180, 0, 0))
    pdf.ln(2)

    if lbl == "Negative":
        pdf.set_fill_color(220, 255, 220)
        pdf.set_text_color(0, 100, 0)
    else:
        pdf.set_fill_color(255, 220, 220)
        pdf.set_text_color(180, 0, 0)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, f"  {_sp(lbl)} - Confiance: {cf}%", 1, 1, "C", True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    info = PARASITE_DB.get(lbl, PARASITE_DB["Negative"])

    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Nom Scientifique:", 0, 0)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, f"  {_sp(info.get('sci', 'N/A'))}", 0, 1)

    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Morphologie:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, _sp(info['morph'].get('fr', '')))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Description:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, _sp(info['desc'].get('fr', '')))

    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 6, "Conseil Médical:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, _sp(info['advice'].get('fr', '')))

    if info.get("tests"):
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Examens Complémentaires Suggérés:", 0, 1)
        pdf.set_font("Arial", "", 8)
        for test in info["tests"][:5]:
            pdf.cell(10, 5, "", 0, 0)
            pdf.cell(0, 5, f"- {_sp(test)}", 0, 1)

    pdf.ln(3)
    rel_text = "FIABLE" if result.get("rel", False) else "À VÉRIFIER"
    rel_color = (0, 150, 0) if result.get("rel", False) else (200, 100, 0)
    pdf.set_font("Arial", "B", 10)
    pdf.set_text_color(*rel_color)
    pdf.cell(0, 8, f"Fiabilité: {rel_text} ({cf}%)", 0, 1, "C")

    return bytes(pdf.output())

# ════════════════════════════════════════════════════════════════════════════════════
#  VOICE SYSTEM
# ════════════════════════════════════════════════════════════════════════════════════

def render_voice_player():
    """Lecteur de voix"""
    if st.session_state.get("voice_text"):
        text = st.session_state.voice_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
        lang_code = {
            "fr": "fr-FR", "ar": "ar-SA", "en": "en-US"
        }.get(st.session_state.get("voice_lang", st.session_state.get("lang", "fr")), "fr-FR")
        
        html_code = f"""
        <div id="voice-container" style="display:none;">
            <script>
            (function() {{
                try {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        setTimeout(function() {{
                            var utterance = new SpeechSynthesisUtterance('{text}');
                            utterance.lang = '{lang_code}';
                            utterance.rate = 0.9;
                            utterance.pitch = 1.0;
                            utterance.volume = 1.0;
                            window.speechSynthesis.speak(utterance);
                        }}, 200);
                    }}
                }} catch(e) {{
                    console.log('Speech error:', e);
                }}
            }})();
            </script>
        </div>
        """
        st.components.v1.html(html_code, height=0)
        st.session_state.voice_text = None

def speak(text: str, lang: Optional[str] = None):
    """Parler un texte"""
    st.session_state.voice_text = text
    st.session_state.voice_lang = lang or st.session_state.get("lang", "fr")

def stop_speech():
    """Arrêter la voix"""
    st.session_state.voice_text = None
    st.components.v1.html("""
    <script>
    try { window.speechSynthesis.cancel(); } catch(e) {}
    </script>
    """, height=0)

# ════════════════════════════════════════════════════════════════════════════════════
#  ANIMATED LOGO
# ════════════════════════════════════════════════════════════════════════════════════

def render_logo():
    """Logo animé"""
    st.markdown("""<div style="text-align: center; margin-bottom: 20px;">
    <svg width="100" height="100" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="animation: rotateWithPulse 20s linear infinite;">
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#00f5ff;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#ff00ff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#00ff88;stop-opacity:1" />
        </linearGradient>
        <filter id="glow">
            <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
            <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>
    </defs>
    <circle cx="50" cy="50" r="45" fill="none" stroke="url(#grad)" stroke-width="3" filter="url(#glow)" opacity="0.8"/>
    <circle cx="50" cy="50" r="38" fill="none" stroke="url(#grad)" stroke-width="1" opacity="0.4"/>
    <circle cx="50" cy="50" r="30" fill="none" stroke="url(#grad)" stroke-width="0.5" opacity="0.2"/>
    <text x="50" y="45" text-anchor="middle" font-family="Orbitron" font-size="16" font-weight="bold" fill="url(#grad)" filter="url(#glow)">DM</text>
    <text x="50" y="60" text-anchor="middle" font-family="Orbitron" font-size="10" font-weight="600" fill="url(#grad)">LAB AI</text>
    <text x="50" y="72" text-anchor="middle" font-family="Orbitron" font-size="7" font-weight="400" fill="#00f5ff" opacity="0.6">v7.5</text>
    </svg>
    <h2 style="background: linear-gradient(135deg, #00f5ff, #ff00ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-family: Orbitron; margin: 10px 0; font-size: 1.3rem;">DM SMART LAB AI</h2>
    <p style="opacity: 0.4; font-size: 0.8rem; font-family: Orbitron; letter-spacing: 3px; margin: 0;">PROFESSIONAL EDITION</p>
    </div>
    <style>
    @keyframes rotateWithPulse {{
        0% {{ transform: rotate(0deg) scale(1); }}
        50% {{ transform: rotate(180deg) scale(1.05); }}
        100% {{ transform: rotate(360deg) scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════════
#  LOGIN PAGE
# ════════════════════════════════════════════════════════════════════════════════════

if not st.session_state.logged_in:
    lc1, lc2, lc3 = st.columns([1, 2, 1])
    with lc2:
        # Language selector
        ll = st.selectbox(
            t("language"),
            ["FR 🇫🇷 Français", "AR 🇸🇦 العربية", "EN 🇬🇧 English"],
            label_visibility="collapsed",
            key="login_lang"
        )
        st.session_state.lang = "fr" if "FR" in ll else ("ar" if "AR" in ll else "en")

        render_logo()

        st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
        <div style='font-size:3.5rem;margin-bottom:10px;animation: pulse 2s ease-in-out infinite;'>
            🔐
        </div>
        <h2 class='dm-nt'>{t('login_title')}</h2>
        <p style='opacity:.4;font-size:.85rem;'>{t('login_subtitle')}</p>
        </div>
        <style>
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        </style>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            u = st.text_input(
                f"{t('username')} *",
                placeholder="admin / dhia / demo / tech1 / tech2",
                key="login_username"
            )
            p = st.text_input(f"{t('password')} *", type="password", key="login_password")
            
            login_btn = st.form_submit_button(
                f"🔐 {t('connect')}",
                use_container_width=True,
                type="primary"
            )
            
            if login_btn:
                if not u.strip():
                    st.error(f"❌ {t('username')} {t('name_required')}")
                else:
                    with st.spinner(f"🔄 {t('connect')}..."):
                        result = db_login(u.strip(), p)
                        
                        if result is None:
                            st.error("❌ User not found")
                        elif isinstance(result, dict) and "error" in result:
                            if result["error"] == "locked":
                                st.error("🔒 Account locked. Try again later.")
                            else:
                                left = result.get("left", 0)
                                st.error(f"❌ Wrong password. {left} attempts left")
                        else:
                            st.session_state.logged_in = True
                            st.session_state.user_id = result["id"]
                            st.session_state.user_name = result["username"]
                            st.session_state.user_role = result["role"]
                            st.session_state.user_full_name = result["full_name"]
                            db_log(result["id"], result["username"], "Login")
                            st.success("✅ Login successful!")
                            st.balloons()
                            st.rerun()

        st.markdown(f"""<div style='text-align:center;opacity:.2;font-size:.65rem;margin-top:20px;font-family:monospace;'>
        admin/admin2026 | dhia/dhia2026 | tech1/tech2026 | demo/demo123
        </div>""", unsafe_allow_html=True)
    
    st.stop()

# ════════════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAVIGATION & USER INFO
# ════════════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    render_logo()
    
    # User card
    ri = ROLES.get(st.session_state.user_role, ROLES["viewer"])
    st.markdown(f"""<div style='text-align: center; padding: 15px; background: rgba(0,245,255,0.05); 
                border-radius: 15px; border: 1px solid rgba(0,245,255,0.15); margin-bottom: 10px;'>
        <div style='font-size: 2rem;'>{ri['icon']}</div>
        <p style='margin: 5px 0; font-weight: bold; color: #e0e8ff;'>{st.session_state.user_full_name}</p>
        <p style='margin: 0; font-size: 0.8rem; opacity: 0.6;'>@{st.session_state.user_name}</p>
        <p style='margin: 5px 0; font-size: 0.75rem; opacity: 0.4;'>{tl(ri['label'])}</p>
    </div>""", unsafe_allow_html=True)

    # Daily tip
    tips = TIPS.get(st.session_state.lang, TIPS["fr"])
    tip_text = tips[datetime.now().timetuple().tm_yday % len(tips)]
    st.info(f"**💡 {t('daily_tip')}:**\n\n_{tip_text}_")

    st.markdown("---")

    # Language selector
    st.markdown(f"#### {t('language')}")
    lang_opts = {
        "🇫🇷 Français": "fr",
        "🇸🇦 العربية": "ar",
        "🇬🇧 English": "en"
    }
    current_lang_label = {v: k for k, v in lang_opts.items()}.get(st.session_state.lang, "🇫🇷 Français")
    selected_lang = st.radio(
        "Lang",
        list(lang_opts.keys()),
        index=list(lang_opts.values()).index(st.session_state.lang),
        label_visibility="collapsed",
        key=f"lang_radio_{time.time()}"
    )
    new_lang = lang_opts[selected_lang]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.markdown("---")

    # Navigation
    st.markdown("### 🧭 Navigation")
    navs = [
        f"🏠 {t('home')}",
        f"🔬 {t('scan')}",
        f"📘 {t('encyclopedia')}",
        f"📊 {t('dashboard')}",
        f"🧠 {t('quiz')}",
        f"💬 {t('chatbot')}",
        f"🔄 {t('compare')}",
    ]
    keys = ["home", "scan", "enc", "dash", "quiz", "chat", "cmp"]
    
    if has_role(3):
        navs.append(f"⚙️ {t('admin')}")
        keys.append("admin")
    
    navs.append(f"ℹ️ {t('about')}")
    keys.append("about")

    menu = st.radio(
        "Menu",
        navs,
        label_visibility="collapsed",
        key=f"nav_radio_{time.time()}"
    )

    st.markdown("---")
    
    # Logout button
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"🚪 {t('logout')}", use_container_width=True, type="secondary"):
            db_log(st.session_state.user_id, st.session_state.user_name, "Logout")
            for k in DEFAULTS:
                st.session_state[k] = DEFAULTS[k]
            st.rerun()
    
    with col2:
        if st.button(f"ℹ️", use_container_width=True, help="System Information"):
            st.info(f"**DM Smart Lab AI v{APP_VERSION}**\n\n{tl(INSTITUTION['name'])}")

pg = dict(zip(navs, keys)).get(menu, "home")

render_voice_player()

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: HOME
# ════════════════════════════════════════════════════════════════════════════════════

if pg == "home":
    st.markdown(f"""<h1 style='font-family:Orbitron,sans-serif;'>
    <span class='dm-nt'>👋 {get_greeting()}, {st.session_state.user_full_name}!</span>
    </h1>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <h2 class='dm-nt'>🧬 DM SMART LAB AI</h2>
    <h4 style='opacity:.6;'>{t('where_science')}</h4>
    <p style='opacity:.4;font-size:.85rem;'>{t('system_desc')}</p>
    <p style='margin-top: 15px; padding: 10px; background: rgba(0,255,136,0.1); border-radius: 8px; border-left: 3px solid #00ff88;'>
    <b>✨ v{APP_VERSION} - Professional Edition</b><br>
    Diagnostic Parasitologique par Intelligenc Artificielle<br>
    <small>INFSPM Ouargla, Algérie 🇩🇿</small>
    </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Voice buttons
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button(f"🎙️ {t('welcome_btn')}", use_container_width=True, type="primary", key="home_welcome"):
            speak(t("voice_welcome"))
            st.rerun()
    with col2:
        if st.button(f"🤖 {t('intro_btn')}", use_container_width=True, type="primary", key="home_intro"):
            speak(t("voice_intro"))
            st.rerun()
    with col3:
        if st.button(f"🔇 {t('stop_voice')}", use_container_width=True, key="home_stop"):
            stop_speech()
    with col4:
        if st.button("🌍 Multilingual", use_container_width=True, disabled=True):
            pass

    st.markdown("---")
    st.markdown(f"### 📊 {t('quick_overview')}")
    
    # Get stats
    stats = db_stats(st.session_state.user_id)
    
    metric_cols = st.columns(5)
    metrics = [
        ("🔬", stats["total"], t("total_analyses")),
        ("✅", stats["reliable"], t("reliable")),
        ("⚠️", stats["verify"], t("to_verify")),
        ("🦠", stats["top"], t("most_frequent")),
        ("📈", f"{stats['avg']}%", t("avg_confidence"))
    ]
    
    for col, (ic, v, lb) in zip(metric_cols, metrics):
        with col:
            st.markdown(f"""<div class='dm-m'>
            <span class='dm-m-i'>{ic}</span>
            <div class='dm-m-v'>{v}</div>
            <div class='dm-m-l'>{lb}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🎯 Quick Access")
    
    quick_cols = st.columns(4)
    quick_actions = [
        ("🔬", t("scan"), "Analyze parasite samples"),
        ("🧠", t("quiz"), "Test your knowledge"),
        ("💬", t("chatbot"), "Ask DM Bot"),
        ("📊", t("dashboard"), "View analytics")
    ]
    
    for col, (icon, title, desc) in zip(quick_cols, quick_actions):
        with col:
            st.markdown(f"""<div style='background: rgba(0,245,255,0.1); border: 1px solid rgba(0,245,255,0.2); 
                            padding: 15px; border-radius: 12px; text-align: center; cursor: pointer;
                            transition: all 0.3s; hover:box-shadow: 0 0 20px rgba(0,245,255,0.3);'>
            <div style='font-size: 2rem;'>{icon}</div>
            <p style='font-weight: bold; margin: 8px 0;'>{title}</p>
            <p style='font-size: 0.75rem; opacity: 0.6;'>{desc}</p>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: SCAN (COMPLETE)
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "scan":
    st.title(f"🔬 {t('scan')}")
    
    mdl, mn, mt = load_model()
    if mn:
        st.sidebar.success(f"🧠 Model: {mn}")
    else:
        st.sidebar.info(f"🧠 {t('demo_mode')}")

    # ===== PATIENT INFORMATION =====
    st.markdown(f"### 📋 1. {t('patient_info')}")
    
    patient_col1, patient_col2 = st.columns(2)
    with patient_col1:
        pn = st.text_input(f"{t('patient_name')} *", key="scan_pn")
    with patient_col2:
        pf = st.text_input(t("patient_firstname"), key="scan_pf")
    
    patient_col3, patient_col4, patient_col5, patient_col6 = st.columns(4)
    with patient_col3:
        pa = st.number_input(t("age"), 0, 120, 30, key="scan_pa")
    with patient_col4:
        ps = st.selectbox(t("sex"), [t("male"), t("female")], key="scan_ps")
    with patient_col5:
        pw = st.number_input(t("weight"), 0.0, 300.0, 70.0, key="scan_pw")
    with patient_col6:
        ph = st.number_input(t("height"), 0.0, 250.0, 170.0, key="scan_ph")
    
    pst = st.selectbox(t("sample_type"), SAMPLES.get(st.session_state.lang, SAMPLES["fr"]), key="scan_pst")

    st.markdown("---")

    # ===== LABORATORY INFORMATION =====
    st.markdown(f"### 🔬 2. {t('lab_info')}")
    
    lab_col1, lab_col2, lab_col3 = st.columns(3)
    with lab_col1:
        t1 = st.text_input(f"{t('technician')} 1", value=st.session_state.user_full_name, key="scan_t1")
    with lab_col2:
        t2 = st.text_input(f"{t('technician')} 2", key="scan_t2")
    with lab_col3:
        lm = st.selectbox(t("microscope"), MICROSCOPE_TYPES, key="scan_lm")
    
    lab_col4, lab_col5 = st.columns(2)
    with lab_col4:
        mg = st.selectbox(t("magnification"), MAGNIFICATIONS, index=3, key="scan_mg")
    with lab_col5:
        pt = st.selectbox(t("preparation"), PREPARATION_TYPES, key="scan_pt")
    
    nt = st.text_area(t("notes"), height=60, key="scan_nt")

    st.markdown("---")

    # ===== IMAGE CAPTURE =====
    st.markdown(f"### 📸 3. {t('image_capture')}")
    
    src = st.radio(
        "Source",
        [t("take_photo"), t("upload_file")],
        horizontal=True,
        label_visibility="collapsed",
        key="scan_src"
    )
    
    img = None
    ih = None

    if t("take_photo") in src:
        st.info(f"📷 {t('camera_hint')}")
        cp = st.camera_input("camera", key="scan_camera")
        if cp:
            img = Image.open(cp).convert("RGB")
            ih = hashlib.md5(cp.getvalue()).hexdigest()
    else:
        uf = st.file_uploader(
            t("upload_file"),
            type=["jpg", "jpeg", "png", "bmp", "tiff"],
            key="scan_upload"
        )
        if uf:
            img = Image.open(uf).convert("RGB")
            ih = hashlib.md5(uf.getvalue()).hexdigest()

    # ===== IMAGE ANALYSIS =====
    if img:
        if not pn.strip():
            st.error(t("name_required"))
            st.stop()

        # Update seeds
        if st.session_state.get("_scan_ih") != ih:
            st.session_state._scan_ih = ih
            st.session_state.demo_seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = random.randint(0, 999999)

        image_col, result_col = st.columns([2, 1.5])

        # ===== IMAGE DISPLAY & FILTERS =====
        with image_col:
            with st.expander("🎛️ Image Adjustment", expanded=False):
                adj_c1, adj_c2, adj_c3, adj_c4 = st.columns(4)
                with adj_c1:
                    z = st.slider("Zoom", 1.0, 5.0, 1.0, 0.25, key="scan_z")
                with adj_c2:
                    br = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1, key="scan_br")
                with adj_c3:
                    co = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1, key="scan_co")
                with adj_c4:
                    sa = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1, key="scan_sa")
            
            adj = adjust(img, br, co, sa)
            if z > 1:
                adj = zoom_img(adj, z)

            # Filters tabs
            filter_tabs = st.tabs([
                "📷 Original",
                "🔥 Thermal",
                "📐 Edges",
                "✨ Enhanced",
                "🔄 Negative",
                "🏔️ Emboss",
                "🎯 Heatmap",
                "🌫️ Blur",
                "🔪 Sharp"
            ])

            with filter_tabs[0]:
                st.image(adj, use_container_width=True)
            with filter_tabs[1]:
                st.image(thermal(adj), use_container_width=True)
            with filter_tabs[2]:
                st.image(edges_filter(adj), use_container_width=True)
            with filter_tabs[3]:
                st.image(enhanced_filter(adj), use_container_width=True)
            with filter_tabs[4]:
                st.image(negative_filter(adj), use_container_width=True)
            with filter_tabs[5]:
                st.image(emboss_filter(adj), use_container_width=True)
            with filter_tabs[6]:
                st.image(gen_heatmap(img, st.session_state.heatmap_seed), use_container_width=True)
            with filter_tabs[7]:
                st.image(blur_filter(adj), use_container_width=True)
            with filter_tabs[8]:
                st.image(sharpen_filter(adj), use_container_width=True)

        # ===== AI PREDICTION =====
        with result_col:
            st.markdown(f"### 🧠 {t('result')}")
            
            with st.spinner(f"🔄 Analyzing..."):
                pg_bar = st.progress(0, text="Processing...")
                for i in range(100):
                    time.sleep(0.002)
                    pg_bar.progress(i + 1, text=f"Processing... {i+1}%")
                
                res = predict(mdl, mt, img, st.session_state.demo_seed)

            lb = res["label"]
            cf = res["conf"]
            rc = risk_color(res["risk"])
            info = PARASITE_DB.get(lb, PARASITE_DB["Negative"])

            # Warnings
            if not res["rel"]:
                st.warning(f"⚠️ {t('low_conf_warn')}")
            if res["demo"]:
                st.info(f"🧪 {t('demo_mode')}")

            # Result card
            st.markdown(f"""<div class='dm-card' style='border-left:4px solid {rc};'>
            <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
            <div>
                <h2 style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;margin:0;font-family:Orbitron;'>{lb}</h2>
                <p style='opacity:.4;font-style:italic;margin:5px 0;'>{info['sci']}</p>
            </div>
            <div style='text-align:center;'>
                <div style='font-size:2.8rem;font-weight:900;font-family:JetBrains Mono;color:{rc}!important;-webkit-text-fill-color:{rc}!important;'>{cf}%</div>
                <div style='font-size:.7rem;opacity:.4;'>{t("confidence")}</div>
            </div>
            </div>
            <hr style='opacity:.1;margin:14px 0;'>
            <p><b>🔬 {t("morphology")}:</b><br>{tl(info['morph'])}</p>
            <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-weight:700;'>{tl(info['risk_d'])}</span></p>
            <div style='background:rgba(0,255,136,.06);padding:14px;border-radius:12px;margin:10px 0;border:1px solid rgba(0,255,136,.1);'>
                <b>💡 {t("advice")}:</b><br>{tl(info['advice'])}
            </div>
            <div style='background:rgba(0,100,255,.06);padding:14px;border-radius:12px;font-style:italic;border:1px solid rgba(0,100,255,.1);'>
                🤖 {tl(info['funny'])}
            </div>
            </div>""", unsafe_allow_html=True)

            # Voice
            voice_c1, voice_c2 = st.columns(2)
            with voice_c1:
                if st.button(f"🔊 {t('listen')}", use_container_width=True, key="scan_voice_listen"):
                    speak(f"{lb}. {tl(info['funny'])}", lang=st.session_state.lang)
            with voice_c2:
                if st.button(f"🔇 {t('stop_voice')}", use_container_width=True, key="scan_voice_stop"):
                    stop_speech()

        st.markdown("---")

        # Extra info expandable
        if info.get("tests"):
            with st.expander(f"🩺 {t('extra_tests')}", expanded=False):
                for test in info["tests"]:
                    st.markdown(f"- **{test}**")

        # Diagnostic keys
        dk = tl(info.get("keys", {}))
        if dk and dk not in ["N/A", "غير متوفر"]:
            with st.expander(f"🔑 {t('diagnostic_keys')}", expanded=False):
                st.markdown(dk)

        # Lifecycle
        cy = tl(info.get("cycle", {}))
        if cy and cy not in ["N/A", "غير متوفر"]:
            with st.expander(f"🔄 {t('lifecycle')}", expanded=False):
                st.markdown(f"**{cy}**")

        # All probabilities
        if res["preds"] and HAS_PLOTLY:
            with st.expander(f"📊 {t('all_probabilities')}", expanded=False):
                sp = dict(sorted(res["preds"].items(), key=lambda x: x[1], reverse=True))
                fig = px.bar(
                    x=list(sp.values()),
                    y=list(sp.keys()),
                    orientation='h',
                    color=list(sp.values()),
                    color_continuous_scale='RdYlGn_r'
                )
                fig.update_layout(
                    height=300,
                    template='plotly_dark',
                    margin=dict(l=20, r=20, t=10, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Save actions
        save_c1, save_c2, save_c3 = st.columns(3)

        with save_c1:
            try:
                pdf_data = make_pdf(
                    {
                        "Nom": pn,
                        "Prenom": pf,
                        "Âge": str(pa),
                        "Sexe": ps,
                        "Poids": str(pw),
                        "Taille": str(ph),
                        "Échantillon": pst
                    },
                    {
                        "Microscope": lm,
                        "Grossissement": mg,
                        "Préparation": pt,
                        "Technicien 1": t1,
                        "Technicien 2": t2,
                        "Notes": nt[:100] if nt else ""
                    },
                    res,
                    lb
                )
                st.download_button(
                    f"📥 {t('download_pdf')}",
                    pdf_data,
                    f"Rapport_{pn}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    "application/pdf",
                    use_container_width=True,
                    key="scan_pdf_btn"
                )
            except Exception as e:
                st.error(f"❌ PDF Error: {str(e)[:50]}")

        with save_c2:
            if has_role(2) and st.button(f"💾 {t('save_db')}", use_container_width=True, key="scan_save_btn"):
                aid = db_save_analysis(st.session_state.user_id, {
                    "pn": pn, "pf": pf, "pa": pa, "ps": ps, "pw": pw, "ph": ph,
                    "st": pst, "mt": lm, "mg": mg, "pt": pt, "t1": t1, "t2": t2, "nt": nt,
                    "label": lb, "conf": cf, "risk": res["risk"],
                    "rel": 1 if res["rel"] else 0,
                    "preds": res["preds"], "hash": ih, "demo": 1 if res["demo"] else 0
                })
                db_log(st.session_state.user_id, st.session_state.user_name, "Analysis saved", f"ID:{aid}")
                st.success(f"✅ {t('saved_ok')}")

        with save_c3:
            if st.button(f"🔄 {t('new_analysis')}", use_container_width=True, key="scan_new_btn"):
                st.session_state._scan_ih = None
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: ENCYCLOPEDIA
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "enc":
    st.title(f"📘 {t('encyclopedia')}")
    st.markdown(f"**{t('system_desc')}** - {len(CLASS_NAMES)} parasites complets")
    
    sr = st.text_input(f"🔍 {t('search')}", key="enc_search")
    st.markdown("---")
    
    found = False
    for nm, d in PARASITE_DB.items():
        if nm == "Negative":
            continue
        if sr.strip() and sr.lower() not in (nm + " " + d["sci"]).lower():
            continue
        found = True
        rc = risk_color(d["risk"])
        
        with st.expander(f"{d['icon']} **{nm}** — *{d['sci']}* | {tl(d['risk_d'])}", 
                        expanded=not sr.strip(), key=f"enc_{nm}"):
            
            col_info, col_side = st.columns([3, 1])
            
            with col_info:
                st.markdown(f"""<div class='dm-card' style='border-left:3px solid {rc};'>
                <h4 style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-family:Orbitron;margin-top:0;'>{d['sci']}</h4>
                
                <p><b>👨‍⚕️ Épidémiologie:</b> {d.get('epidemiology', {}).get('prevalence', 'N/A')}</p>
                
                <p><b>🔬 Morphologie:</b><br>{tl(d['morph'])}</p>
                
                <p><b>📖 Description:</b><br>{tl(d['desc'])}</p>
                
                <p><b>🦠 Type:</b> {d.get('type', 'N/A')} | <b>Catégorie:</b> {d.get('category', 'N/A')}</p>
                
                <p><b>⚠️ Risque:</b> <span style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-weight:700;'>{tl(d['risk_d'])}</span></p>
                
                <div style='background:rgba(0,255,136,.06);padding:12px;border-radius:10px;margin:8px 0;border:1px solid rgba(0,255,136,.1);'>
                    <b>💊 Traitement:</b><br>{tl(d['advice'])}
                </div>
                
                <div style='background:rgba(0,100,255,.06);padding:12px;border-radius:10px;font-style:italic;border:1px solid rgba(0,100,255,.1);'>
                    🤖 {tl(d['funny'])}
                </div>
                
                <p><b>🔬 Examens diagnostiques:</b></p>
                <ul>
                {"".join([f"<li>{t}</li>" for t in d.get('tests', [])[:8]])}
                </ul>
                
                <p><b>⚠️ Complications possibles:</b></p>
                <ul>
                {"".join([f"<li>{c}</li>" for c in d.get('complications', [])[:5]])}
                </ul>
                </div>""", unsafe_allow_html=True)
                
                cy = tl(d.get("cycle", {}))
                if cy and cy not in ["N/A", "غير متوفر"]:
                    st.markdown(f"<b>🔄 Cycle de Vie:</b> {cy}", unsafe_allow_html=True)
                
                dk = tl(d.get("keys", {}))
                if dk and dk not in ["N/A", "غير متوفر"]:
                    st.markdown(f"<b>🔑 Clés diagnostiques:</b><br>{dk}", unsafe_allow_html=True)
            
            with col_side:
                rp = risk_pct(d["risk"])
                if rp > 0:
                    st.progress(rp / 100, text=f"{rp}% Risk")
                st.markdown(f'<div style="text-align:center;font-size:3.5rem;margin-top:20px;">{d["icon"]}</div>', 
                           unsafe_allow_html=True)
                if st.button(f"🔊", key=f"enc_voice_{nm}", use_container_width=True, help="Listen"):
                    speak(f"{nm}. {tl(d['funny'])}", lang=st.session_state.lang)

    if sr.strip() and not found:
        st.warning(f"❌ {t('no_results')} pour '{sr}'")

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: DASHBOARD
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "dash":
    st.title(f"📊 {t('dashboard')}")
    
    # Get data
    s = db_stats() if has_role(3) else db_stats(st.session_state.user_id)
    an = db_analyses() if has_role(3) else db_analyses(st.session_state.user_id)

    # Metrics
    metric_cols = st.columns(5)
    metrics_data = [
        ("🔬", s["total"], t("total_analyses")),
        ("✅", s["reliable"], t("reliable")),
        ("⚠️", s["verify"], t("to_verify")),
        ("🦠", s["top"], t("most_frequent")),
        ("📈", f"{s['avg']}%", t("avg_confidence"))
    ]
    
    for col, (ic, v, lb) in zip(metric_cols, metrics_data):
        with col:
            st.markdown(f"""<div class='dm-m'>
            <span class='dm-m-i'>{ic}</span>
            <div class='dm-m-v'>{v}</div>
            <div class='dm-m-l'>{lb}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("---")

    if s["total"] > 0 and an:
        df = pd.DataFrame(an)
        
        chart_cols = st.columns(2)
        
        with chart_cols[0]:
            st.markdown(f"#### {t('parasite_distribution')}")
            if "parasite_detected" in df.columns:
                pc = df["parasite_detected"].value_counts().head(10)
                fig = px.pie(
                    values=pc.values,
                    names=pc.index,
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Plasma
                )
                fig.update_layout(height=350, template='plotly_dark', 
                                 margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

        with chart_cols[1]:
            st.markdown(f"#### {t('confidence_levels')}")
            if "confidence" in df.columns:
                fig = px.histogram(df, x="confidence", nbins=20,
                                  color_discrete_sequence=["#00f5ff"])
                fig.update_layout(height=350, template='plotly_dark',
                                 margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

        # Trends
        tr = db_trends(30)
        if tr:
            st.markdown(f"#### {t('trends')}")
            tr_df = pd.DataFrame(tr)
            fig = px.line(tr_df, x="day", y="count", color="parasite_detected",
                         markers=True, title="30-Day Trend")
            fig.update_layout(height=300, template='plotly_dark',
                             margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

        # History table
        st.markdown(f"### 📋 {t('history')}")
        display_cols = [c for c in ["id", "analysis_date", "patient_name", 
                                   "parasite_detected", "confidence", "risk_level", 
                                   "analyst", "validated"] if c in df.columns]
        st.dataframe(df[display_cols] if display_cols else df, use_container_width=True, 
                    height=400)

        # Validation
        if has_role(2) and "validated" in df.columns:
            uv = df[df["validated"] == 0]
            if not uv.empty:
                st.markdown("---")
                st.markdown("### ✔️ Pending Validations")
                vi = st.selectbox("Select Analysis ID:", uv["id"].tolist(), 
                                 key="dash_validate_id")
                if st.button(f"✅ Validate #{vi}", key="dash_validate_btn"):
                    db_validate(vi, st.session_state.user_full_name)
                    st.success(f"✅ Validated #{vi}")
                    st.rerun()

        # Export
        st.markdown("---")
        export_cols = st.columns(3)
        with export_cols[0]:
            st.download_button(f"⬇️ {t('export_csv')}", 
                              df.to_csv(index=False).encode('utf-8-sig'),
                              f"analyses_{datetime.now().strftime('%Y%m%d')}.csv",
                              "text/csv", use_container_width=True, 
                              key="dash_csv")
        with export_cols[1]:
            st.download_button(f"⬇️ {t('export_json')}",
                              df.to_json(orient='records', force_ascii=False).encode(),
                              f"analyses_{datetime.now().strftime('%Y%m%d')}.json",
                              "application/json", use_container_width=True,
                              key="dash_json")
        with export_cols[2]:
            try:
                from openpyxl import Workbook
                xlsx_buffer = io.BytesIO()
                df.to_excel(xlsx_buffer, index=False, engine='openpyxl')
                xlsx_buffer.seek(0)
                st.download_button(f"⬇️ Excel",
                                  xlsx_buffer.getvalue(),
                                  f"analyses_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                  use_container_width=True, key="dash_xlsx")
            except:
                st.info("Excel export requires openpyxl")
    else:
        st.info(f"ℹ️ {t('no_data')}")

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: QUIZ (COMPLET)
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "quiz":
    st.title(f"🧠 {t('quiz')}")

    # Initialize quiz state
    if "quiz_state" not in st.session_state or not isinstance(st.session_state.quiz_state, dict):
        st.session_state.quiz_state = {
            "current": 0, "score": 0, "answered": [], "active": False,
            "order": [], "wrong": [], "total_q": 0, "finished": False,
            "selected_answer": None, "show_result": False
        }

    qs = st.session_state.quiz_state

    # Leaderboard
    with st.expander(f"🏆 {t('leaderboard')}", expanded=False):
        lb_data = db_leaderboard(20)
        if lb_data:
            for i, entry in enumerate(lb_data[:10]):
                medal = ["🥇", "🥈", "🥉"] + [f"#{i+1}"] * 7
                st.markdown(
                    f"{medal[i]} **{entry['username']}** — "
                    f"{entry['score']}/{entry['total_questions']} "
                    f"({entry['percentage']:.1f}%)"
                )
        else:
            st.info("No scores yet")

    st.markdown("---")

    # Start quiz
    if not qs.get("active") and not qs.get("finished"):
        st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
        <div style='font-size:4rem;margin-bottom:10px;'>🧠</div>
        <h3 class='dm-nt'>{{"fr":"Testez vos connaissances!","ar":"اختبر معارفك!","en":"Test Your Knowledge!"}.get(st.session_state.lang)}</h3>
        <p style='opacity:.5;'>{len(QUIZ_QUESTIONS)} questions disponibles</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")
        quiz_cols = st.columns(2)
        
        with quiz_cols[0]:
            n_q = st.slider(
                {"fr": "Nombre de questions:", "ar": "عدد الأسئلة:",
                 "en": "Number of questions:"}.get(st.session_state.lang),
                5, min(30, len(QUIZ_QUESTIONS)), 10, key="quiz_count"
            )
        
        with quiz_cols[1]:
            cats = list(set(q.get("cat", "General") for q in QUIZ_QUESTIONS))
            all_cat = {"fr": "Toutes les catégories",
                      "ar": "جميع الفئات",
                      "en": "All categories"}.get(st.session_state.lang)
            cats.insert(0, all_cat)
            chosen_cat = st.selectbox(
                {"fr": "Catégorie:", "ar": "الفئة:",
                 "en": "Category:"}.get(st.session_state.lang),
                cats, key="quiz_cat"
            )

        if st.button(f"🎮 {t('start_quiz')}", use_container_width=True,
                    type="primary", key="quiz_start_btn"):
            pool = (list(range(len(QUIZ_QUESTIONS)))
                   if chosen_cat == all_cat
                   else [i for i, q in enumerate(QUIZ_QUESTIONS)
                        if q.get("cat") == chosen_cat])
            
            if not pool:
                pool = list(range(len(QUIZ_QUESTIONS)))
            
            random.shuffle(pool)
            final = pool[:min(n_q, len(pool))]
            
            st.session_state.quiz_state = {
                "current": 0, "score": 0, "answered": [], "active": True,
                "order": final, "wrong": [], "total_q": len(final),
                "finished": False, "selected_answer": None, "show_result": False
            }
            db_log(st.session_state.user_id, st.session_state.user_name,
                  "Quiz started", f"n={len(final)} cat={chosen_cat}")
            st.rerun()

    # Quiz active
    elif qs.get("active") and not qs.get("finished"):
        idx = qs["current"]
        order = qs.get("order", [])
        total_q = qs.get("total_q", len(order))

        if idx < len(order):
            qi = order[idx]
            q = QUIZ_QUESTIONS[qi]

            # Progress
            progress_val = idx / total_q if total_q > 0 else 0
            st.progress(progress_val)

            q_label = {"fr": "Question", "ar": "سؤال",
                      "en": "Question"}.get(st.session_state.lang)
            st.markdown(f"## {q_label} {idx + 1}/{total_q}")

            if q.get("cat"):
                st.caption(f"📂 {q['cat']}")

            q_text = tl(q["q"])
            st.markdown(f"""<div class='dm-card dm-card-purple'>
            <h4 style='margin:0;line-height:1.6;'>{q_text}</h4>
            </div>""", unsafe_allow_html=True)

            if not qs.get("show_result"):
                st.markdown("---")
                opt_cols = st.columns(2)
                for i, opt in enumerate(q["opts"]):
                    with opt_cols[i % 2]:
                        letter = ['A', 'B', 'C', 'D'][i]
                        if st.button(f"{letter}. {opt}", key=f"quiz_{idx}_{i}",
                                    use_container_width=True):
                            correct = (i == q["ans"])
                            st.session_state.quiz_state["selected_answer"] = i
                            st.session_state.quiz_state["show_result"] = True
                            if correct:
                                st.session_state.quiz_state["score"] += 1
                            else:
                                st.session_state.quiz_state["wrong"].append({
                                    "q": q_text,
                                    "your": opt,
                                    "correct": q["opts"][q["ans"]]
                                })
                            st.session_state.quiz_state["answered"].append(correct)
                            st.rerun()
            else:
                # Show result
                selected = qs.get("selected_answer", -1)
                correct_idx = q["ans"]
                is_correct = selected == correct_idx

                if is_correct:
                    st.success(f"✅ {{"fr":"Bonne réponse!","ar":"إجابة صحيحة!","en":"Correct!"}.get(st.session_state.lang)}")
                else:
                    correct_ans = q["opts"][correct_idx]
                    st.error(f"❌ {{"fr":"Réponse correcte","ar":"الإجابة الصحيحة","en":"Correct answer"}.get(st.session_state.lang)}: **{correct_ans}**")

                # Explanation
                expl = tl(q.get("expl", {}))
                if expl:
                    st.info(f"📖 {expl}")

                # All options with markers
                for i, opt in enumerate(q["opts"]):
                    if i == correct_idx:
                        st.markdown(f"✅ **{['A','B','C','D'][i]}. {opt}**")
                    elif i == selected and not is_correct:
                        st.markdown(f"❌ ~~{['A','B','C','D'][i]}. {opt}~~")
                    else:
                        st.markdown(f"  {['A','B','C','D'][i]}. {opt}")

                st.markdown("---")

                # Next/Finish
                if idx + 1 < len(order):
                    if st.button(f"➡️ {t('next_question')}", use_container_width=True,
                                type="primary", key="quiz_next"):
                        st.session_state.quiz_state["current"] += 1
                        st.session_state.quiz_state["show_result"] = False
                        st.session_state.quiz_state["selected_answer"] = None
                        st.rerun()
                else:
                    finish_label = {"fr": "🏁 Résultats", "ar": "🏁 النتائج",
                                   "en": "🏁 Results"}.get(st.session_state.lang)
                    if st.button(finish_label, use_container_width=True,
                                type="primary", key="quiz_finish"):
                        st.session_state.quiz_state["finished"] = True
                        st.session_state.quiz_state["active"] = False
                        st.rerun()

    # Results
    elif qs.get("finished"):
        score = qs.get("score", 0)
        total_q = qs.get("total_q", 1)
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
        <h2 class='dm-nt'>{t('result')}</h2>
        <div style='font-size:4rem;font-weight:900;font-family:JetBrains Mono;
            background:linear-gradient(135deg,#00f5ff,#ff00ff,#00ff88);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
            {score}/{total_q}
        </div>
        <p style='font-size:1.5rem;opacity:.8;'>{pct}%</p>
        <p style='font-size:1.1rem;'>{msg}</p>
        </div>""", unsafe_allow_html=True)

        try:
            db_quiz_save(st.session_state.user_id, st.session_state.user_name,
                        score, total_q, pct)
            db_log(st.session_state.user_id, st.session_state.user_name,
                  "Quiz done", f"{score}/{total_q}={pct}%")
        except Exception:
            pass

        # Analysis chart
        if HAS_PLOTLY:
            st.markdown("---")
            st.markdown(f"### 📊 Analysis")
            correct_label = {"fr": "Correctes", "ar": "صحيحة", "en": "Correct"}.get(st.session_state.lang)
            incorrect_label = {"fr": "Incorrectes", "ar": "خاطئة", "en": "Incorrect"}.get(st.session_state.lang)
            
            fig = go.Figure(data=[go.Pie(
                labels=[correct_label, incorrect_label],
                values=[score, total_q - score],
                marker_colors=["#00ff88", "#ff0040"],
                hole=0.5,
                textinfo='label+percent',
                textfont_size=14
            )])
            fig.update_layout(height=300, template='plotly_dark',
                             margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        # Wrong answers
        wrong = qs.get("wrong", [])
        if wrong:
            review = {"fr": f"Erreurs à revoir ({len(wrong)})",
                     "ar": f"الأخطاء ({len(wrong)})",
                     "en": f"Mistakes to review ({len(wrong)})"}.get(st.session_state.lang)
            with st.expander(f"❌ {review}"):
                for i, w in enumerate(wrong):
                    your_label = {"fr": "Votre réponse", "ar": "إجابتك",
                                 "en": "Your answer"}.get(st.session_state.lang)
                    correct_label2 = {"fr": "Correcte", "ar": "الصحيحة",
                                     "en": "Correct"}.get(st.session_state.lang)
                    st.markdown(f"""
**{i + 1}. {w['q']}**
- ❌ {your_label}: ~~{w['your']}~~
- ✅ {correct_label2}: **{w['correct']}**
---""")

        st.markdown("---")
        if st.button(f"🔄 {t('restart')}", use_container_width=True,
                    type="primary", key="quiz_restart_btn"):
            st.session_state.quiz_state = DEFAULTS["quiz_state"].copy()
            st.rerun()

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: CHATBOT
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "chat":
    st.title(f"💬 DM Bot")
    
    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <div style='display:flex;align-items:center;gap:15px;'>
        <div style='font-size:2.5rem;'>🤖</div>
        <div>
            <h4 style='margin:0;' class='dm-nt'>DM Bot v{APP_VERSION}</h4>
            <p style='margin:0;opacity:.5;font-size:.85rem;'>{t("chatbot")}</p>
        </div>
    </div>
    </div>""", unsafe_allow_html=True)

    # Initialize chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "bot", "msg": t("chat_welcome")})

    # Chat display
    chat_container = st.container()
    with chat_container:
        for msg_item in st.session_state.chat_history:
            if msg_item["role"] == "user":
                st.markdown(f"""<div style='display:flex;justify-content:flex-end;margin:8px 0;'>
                <div style='background:linear-gradient(135deg,#0066ff,#0044cc);color:white;padding:14px 18px;
                           border-radius:18px;max-width:85%;border-bottom-right-radius:4px;'>
                👤 {msg_item['msg']}</div>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div style='display:flex;justify-content:flex-start;margin:8px 0;'>
                <div style='background:rgba(10,15,46,0.85);border:1px solid rgba(0,245,255,0.2);
                           color:#e0e8ff;padding:14px 18px;border-radius:18px;max-width:85%;border-bottom-left-radius:4px;'>
                🤖 {msg_item['msg']}</div>
                </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input(
            t("chat_placeholder"),
            key="chat_input",
            label_visibility="collapsed",
            placeholder=t("chat_placeholder")
        )
        col_send, col_clear = st.columns([4, 1])
        with col_send:
            send_btn = st.form_submit_button(
                {"fr": "📨 Envoyer", "ar": "📨 إرسال",
                 "en": "📨 Send"}.get(st.session_state.lang),
                use_container_width=True
            )
        with col_clear:
            clear_btn = st.form_submit_button(
                f"🗑️ {t('clear_chat')}",
                use_container_width=True
            )

    if send_btn and user_input and user_input.strip():
        st.session_state.chat_history.append({"role": "user", "msg": user_input.strip()})
        reply = chatbot_reply(user_input.strip())
        st.session_state.chat_history.append({"role": "bot", "msg": reply})
        db_log(st.session_state.user_id, st.session_state.user_name,
              "Chat", user_input[:100])
        st.rerun()

    if clear_btn:
        st.session_state.chat_history = []
        st.rerun()

    # Quick questions
    st.markdown(f"**{t('quick_questions')}**")
    
    q_items = ["Amoeba", "Giardia", "Plasmodium", "Leishmania", 
               "Trypanosoma", "Schistosoma", "Toxoplasma"]
    q_cols = st.columns(len(q_items))
    for col, item in zip(q_cols, q_items):
        with col:
            if st.button(item, key=f"q_{item}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": item})
                st.session_state.chat_history.append(
                    {"role": "bot", "msg": chatbot_reply(item)}
                )
                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: COMPARE (ADVANCED)
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "cmp":
    st.title(f"🔄 {t('compare')}")
    
    desc = {"fr": "Comparez deux images microscopiques avec analyse avancée",
            "ar": "قارن بين صورتين مجهريتين",
            "en": "Compare two microscopic images"}.get(st.session_state.lang)
    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <p style='margin:0;'>{desc}</p>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 📷 {t('image1')}")
        f1 = st.file_uploader("img1", type=["jpg", "jpeg", "png", "bmp"],
                             key="cmp1", label_visibility="collapsed")
    with c2:
        st.markdown(f"### 📷 {t('image2')}")
        f2 = st.file_uploader("img2", type=["jpg", "jpeg", "png", "bmp"],
                             key="cmp2", label_visibility="collapsed")

    if f1 and f2:
        i1 = Image.open(f1).convert("RGB")
        i2 = Image.open(f2).convert("RGB")

        c1, c2 = st.columns(2)
        with c1:
            st.image(i1, caption=t("image1"), use_container_width=True)
        with c2:
            st.image(i2, caption=t("image2"), use_container_width=True)

        st.markdown("---")
        if st.button(f"🔍 {t('compare_btn')}", use_container_width=True,
                    type="primary", key="compare_btn"):
            with st.spinner("Analyzing..."):
                metrics = compare_imgs(i1, i2)

            st.markdown(f"### 📊 Results")
            mc = st.columns(4)
            with mc[0]:
                st.markdown(f"""<div class='dm-m'><span class='dm-m-i'>📊</span>
                <div class='dm-m-v'>{metrics['sim']}%</div>
                <div class='dm-m-l'>{t('similarity')}</div></div>""", unsafe_allow_html=True)
            with mc[1]:
                st.markdown(f"""<div class='dm-m'><span class='dm-m-i'>🎯</span>
                <div class='dm-m-v'>{metrics['ssim']}</div>
                <div class='dm-m-l'>SSIM</div></div>""", unsafe_allow_html=True)
            with mc[2]:
                st.markdown(f"""<div class='dm-m'><span class='dm-m-i'>📐</span>
                <div class='dm-m-v'>{metrics['mse']}</div>
                <div class='dm-m-l'>MSE</div></div>""", unsafe_allow_html=True)
            with mc[3]:
                if metrics["sim"] > 90:
                    verdict = {"fr": "Très similaires", "ar": "متشابهتان جدا",
                              "en": "Very similar"}
                    v_icon = "✅"
                elif metrics["sim"] > 70:
                    verdict = {"fr": "Similaires", "ar": "متشابهتان",
                              "en": "Similar"}
                    v_icon = "🟡"
                elif metrics["sim"] > 50:
                    verdict = {"fr": "Peu similaires", "ar": "قليل التشابه",
                              "en": "Somewhat similar"}
                    v_icon = "🟠"
                else:
                    verdict = {"fr": "Très différentes", "ar": "مختلفتان جدا",
                              "en": "Very different"}
                    v_icon = "🔴"
                st.markdown(f"""<div class='dm-m'><span class='dm-m-i'>🔍</span>
                <div class='dm-m-v' style='font-size:1rem;'>{v_icon} {tl(verdict)}</div>
                <div class='dm-m-l'>Verdict</div></div>""", unsafe_allow_html=True)

            # Gauge
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
                            {"range": [0, 30], "color": "rgba(255,0,64,0.3)"},
                            {"range": [30, 60], "color": "rgba(255,149,0,0.3)"},
                            {"range": [60, 80], "color": "rgba(255,255,0,0.3)"},
                            {"range": [80, 100], "color": "rgba(0,255,136,0.3)"}
                        ],
                    }
                ))
                fig.update_layout(height=300, template='plotly_dark',
                                 margin=dict(l=30, r=30, t=60, b=20))
                st.plotly_chart(fig, use_container_width=True)

            # Pixel diff
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
            filters_data = [
                ({"fr": "Thermique", "ar": "حراري", "en": "Thermal"}, thermal),
                ({"fr": "Contours", "ar": "حواف", "en": "Edges"}, edges_filter),
                ({"fr": "Contraste+", "ar": "تباين+", "en": "Enhanced"}, enhanced_filter),
                ({"fr": "Négatif", "ar": "سلبي", "en": "Negative"}, negative_filter),
                ({"fr": "Relief", "ar": "نقش", "en": "Emboss"}, emboss_filter),
            ]
            for fname, ffunc in filters_data:
                fn = tl(fname)
                fc1, fc2 = st.columns(2)
                with fc1:
                    st.image(ffunc(i1), caption=f"{t('image1')} - {fn}",
                            use_container_width=True)
                with fc2:
                    st.image(ffunc(i2), caption=f"{t('image2')} - {fn}",
                            use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: ADMIN (COMPLET)
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "admin":
    st.title(f"⚙️ {t('admin')}")
    if not has_role(3):
        st.error("🔒 Admin access required")
        st.stop()

    admin_tabs = st.tabs([
        f"👥 {t('users_mgmt')}",
        f"📜 {t('activity_log')}",
        f"🖥️ {t('system_info')}"
    ])

    # Users management
    with admin_tabs[0]:
        st.markdown("### Users List")
        users = db_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True, height=400)
            st.markdown("---")

            tab_mgmt, tab_create = st.tabs(["Manage", "Create New"])

            with tab_mgmt:
                col1, col2, col3 = st.columns(3)
                uid = col1.number_input("User ID", min_value=1, step=1, key="admin_uid")
                act = col2.selectbox("Status", ["Active", "Disabled"], key="admin_status")
                if col3.button("Apply", use_container_width=True, key="admin_toggle"):
                    db_toggle(uid, act == "Active")
                    db_log(st.session_state.user_id, st.session_state.user_name,
                          "Toggle user", f"#{uid}={act}")
                    st.success(f"✅ Updated")

            with tab_create:
                with st.form("create_user"):
                    nu = st.text_input("Username *", key="new_user")
                    np = st.text_input("Password *", type="password", key="new_pwd")
                    nf = st.text_input("Full Name *", key="new_name")
                    nr = st.selectbox("Role", list(ROLES.keys()), key="new_role")
                    ns = st.text_input("Speciality", "Laboratoire", key="new_spec")
                    if st.form_submit_button("Create User", use_container_width=True):
                        if nu and np and nf:
                            if db_create_user(nu, np, nf, nr, ns):
                                db_log(st.session_state.user_id, st.session_state.user_name,
                                      "Created user", nu)
                                st.success(f"✅ User '{nu}' created!")
                                st.rerun()
                            else:
                                st.error("Username exists")
                        else:
                            st.error("Fill all fields")

    # Activity log
    with admin_tabs[1]:
        st.markdown("### Activity Log")
        logs = db_logs(500)
        if logs:
            ldf = pd.DataFrame(logs)
            if "username" in ldf.columns:
                users_list = sorted(ldf["username"].dropna().unique().tolist())
                flt = st.selectbox("Filter:", ["All"] + users_list, key="log_filter")
                if flt != "All":
                    ldf = ldf[ldf["username"] == flt]
            
            st.dataframe(ldf, use_container_width=True, height=500)
            
            if st.button("📥 Export Logs"):
                st.download_button(
                    "Download CSV",
                    ldf.to_csv(index=False).encode(),
                    f"activity_log_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )

    # System info
    with admin_tabs[2]:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""<div class='dm-card dm-card-green'>
            <h4>🟢 Status</h4>
            <p><b>Version:</b> {APP_VERSION}</p>
            <p><b>Build:</b> {BUILD_DATE}</p>
            <p><b>DB:</b> SQLite</p>
            <p><b>Bcrypt:</b> {'✅' if HAS_BCRYPT else '❌'}</p>
            <p><b>Plotly:</b> ✅</p>
            </div>""", unsafe_allow_html=True)
        
        with col2:
            ts = db_stats()
            st.markdown(f"""<div class='dm-card dm-card-cyan'>
            <h4>📊 Statistics</h4>
            <p><b>Users:</b> {len(db_users())}</p>
            <p><b>Analyses:</b> {ts['total']}</p>
            <p><b>Reliable:</b> {ts['reliable']}</p>
            <p><b>Quiz:</b> {len(db_leaderboard())}</p>
            </div>""", unsafe_allow_html=True)
        
        with col3:
            dbsz = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
            st.markdown(f"""<div class='dm-card'>
            <h4>💾 Database</h4>
            <p><b>Size:</b> {dbsz:.1f} KB</p>
            <p><b>Parasites:</b> {len(CLASS_NAMES)}</p>
            <p><b>Quiz Q:</b> {len(QUIZ_QUESTIONS)}</p>
            <p><b>Chat KB:</b> {len(CHAT_KB)}</p>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════════
#  PAGE: ABOUT
# ════════════════════════════════════════════════════════════════════════════════════

elif pg == "about":
    st.title(f"ℹ️ {t('about')}")
    lang = st.session_state.lang

    st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
    <h1 class='dm-nt'>🧬 DM SMART LAB AI</h1>
    <p style='font-size:1.1rem;font-family:Orbitron;'><b>v{APP_VERSION} — Professional Edition</b></p>
    <p style='opacity:.4;'>{t('system_desc')}</p>
    </div>""", unsafe_allow_html=True)

    desc = {
        "fr": "Ce système innovant utilise l'IA pour diagnostiquer automatiquement les parasites à partir d'images microscopiques.",
        "ar": "هذا النظام المبتكر يستخدم الذكاء الاصطناعي لتشخيص الطفيليات تلقائياً.",
        "en": "This innovative system uses AI to automatically diagnose parasites from microscopic images."
    }.get(lang)

    st.markdown(f"""<div class='dm-card'>
    <h3>📖 {tl(PROJECT_TITLE)}</h3>
    <p>{desc}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""<div class='dm-card dm-card-cyan'>
        <h3>👨‍💻 {t('dev_team')}</h3>
        <p><b>👨‍🔬 {AUTHORS['dev1']['name']}</b><br>
        <span style='opacity:.7;'>{tl(AUTHORS['dev1']['role'])}</span></p>
        <p><b>🧑‍⚕️ {AUTHORS['dev2']['name']}</b><br>
        <span style='opacity:.7;'>{tl(AUTHORS['dev2']['role'])}</span></p>
        </div>""", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""<div class='dm-card'>
        <h3>🏫 {t('institution')}</h3>
        <p><b>{tl(INSTITUTION['name'])}</b></p>
        <p>📍 {INSTITUTION['city']}, {tl(INSTITUTION['country'])}</p>
        <p>🌐 {INSTITUTION['year']}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### {t('technologies')}")
    
    tech_cols = st.columns(6)
    techs = [
        ("🐍", "Python 3.9+"),
        ("🎨", "Streamlit"),
        ("📊", "Plotly"),
        ("🔢", "NumPy"),
        ("🐼", "Pandas"),
        ("🧠", "TensorFlow")
    ]
    
    for col, (icon, name) in zip(tech_cols, techs):
        with col:
            st.markdown(f"""<div class='dm-m'>
            <span class='dm-m-i'>{icon}</span>
            <div style='font-size: 0.75rem; margin-top: 10px;'>{name}</div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<small style='opacity: 0.3; text-align: center;'>© {INSTITUTION['year']} {INSTITUTION['short']} | v{APP_VERSION} | Build {BUILD_DATE}</small>", 
           unsafe_allow_html=True)
