# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║                  DM SMART LAB AI v7.0 - ULTIMATE PROFESSIONAL EDITION          ║
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
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from datetime import datetime, timedelta
from fpdf import FPDF
from contextlib import contextmanager

# ── Optional imports ──
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
    page_title="DM Smart Lab AI v7.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
#  CONSTANTS
# ============================================
APP_VERSION = "7.0.0"
SECRET_KEY = "dm_smart_lab_2026_ultra_secret"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)

ROLES = {
    "admin": {"level": 3, "label_fr": "Administrateur", "label_ar": "مشرف", "label_en": "Administrator", "icon": "👑"},
    "technician": {"level": 2, "label_fr": "Technicien", "label_ar": "تقني", "label_en": "Technician", "icon": "🔬"},
    "viewer": {"level": 1, "label_fr": "Observateur", "label_ar": "مراقب", "label_en": "Viewer", "icon": "👁️"}
}

AUTHORS = {
    "dev1": {"name": "Sebbag Mohamed Dhia Eddine", "role_fr": "Expert IA & Conception", "role_ar": "خبير ذكاء اصطناعي و تصميم", "role_en": "AI & Design Expert"},
    "dev2": {"name": "Ben Sghir Mohamed", "role_fr": "Expert Laboratoire & Données", "role_ar": "خبير مخبر و بيانات", "role_en": "Laboratory & Data Expert"}
}

INSTITUTION = {
    "name_fr": "Institut National de Formation Supérieure Paramédicale (INFSPM)",
    "name_ar": "المعهد الوطني للتكوين العالي شبه الطبي",
    "name_en": "National Institute of Higher Paramedical Training (INFSPM)",
    "short": "INFSPM",
    "city": "Ouargla",
    "country_fr": "Algérie",
    "country_ar": "الجزائر",
    "country_en": "Algeria",
    "year": 2026
}

PROJECT_TITLE = {
    "fr": "Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais",
    "ar": "استكشاف إمكانيات الذكاء الاصطناعي للقراءة الآلية للفحص الطفيلي المباشر",
    "en": "Exploring the potential of artificial intelligence for automatic reading of fresh parasitological examination"
}

# ── TRANSLATIONS ──
LANG = {
    "fr": {
        "app_title": "DM Smart Lab AI",
        "login": "Connexion Sécurisée",
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
        "patient_name": "Nom du Patient",
        "patient_firstname": "Prénom",
        "age": "Âge",
        "sex": "Sexe",
        "male": "Homme",
        "female": "Femme",
        "weight": "Poids (kg)",
        "sample_type": "Type d'Échantillon",
        "microscope": "Microscope",
        "magnification": "Grossissement",
        "preparation": "Préparation",
        "technician": "Technicien",
        "notes": "Notes / Observations",
        "upload_image": "Importer une image",
        "take_photo": "📸 Prendre une Photo (Caméra)",
        "or_upload": "📁 Ou importer un fichier",
        "analyze": "Analyser",
        "result": "Résultat",
        "confidence": "Confiance",
        "risk": "Risque",
        "advice": "Conseil Médical",
        "morphology": "Morphologie",
        "description": "Description",
        "extra_tests": "Examens complémentaires",
        "diagnostic_keys": "Clés Diagnostiques",
        "lifecycle": "Cycle de Vie",
        "download_pdf": "Télécharger le Rapport PDF",
        "save_db": "Sauvegarder dans la Base",
        "new_analysis": "Nouvelle Analyse",
        "total_analyses": "Total Analyses",
        "reliable": "Fiables",
        "to_verify": "À Vérifier",
        "most_frequent": "Plus Fréquent",
        "avg_confidence": "Confiance Moy.",
        "start_quiz": "Démarrer le Quiz",
        "next_question": "Question Suivante",
        "restart": "Recommencer",
        "leaderboard": "Classement",
        "search": "Rechercher...",
        "dark_mode": "Mode Nuit",
        "language": "Langue",
        "daily_tip": "Conseil du Jour",
        "system_info": "Informations Système",
        "users_management": "Gestion des Utilisateurs",
        "activity_log": "Journal d'Activité",
        "create_user": "Créer un Utilisateur",
        "similarity": "Similarité",
        "image1": "Image 1",
        "image2": "Image 2",
        "compare_btn": "Comparer",
        "no_data": "Aucune donnée disponible",
        "camera_instruction": "Placez l'oculaire du microscope devant la caméra",
        "name_required": "Le nom du patient est obligatoire",
        "saved_success": "Résultat sauvegardé",
        "demo_mode": "Mode démonstration (aucun modèle chargé)",
        "low_confidence": "Confiance faible. Vérification manuelle recommandée",
        "voice_welcome": "Bienvenue dans DM Smart Lab AI ! Nous sommes ravis de vous accueillir. Ce système d'intelligence artificielle est conçu pour vous assister dans le diagnostic parasitologique.",
        "voice_intro": "Je suis DM Smart Lab AI, version 7, système de diagnostic parasitologique par intelligence artificielle. J'ai été développé par deux techniciens supérieurs de l'INFSPM de Ouargla: Sebbag Mohamed Dhia Eddine, expert en intelligence artificielle et conception, et Ben Sghir Mohamed, expert en laboratoire et données. Ensemble, nous repoussons les limites de la parasitologie moderne!",
    },
    "ar": {
        "app_title": "مختبر DM الذكي",
        "login": "تسجيل الدخول الآمن",
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
        "about": "حول",
        "greeting_morning": "صباح الخير",
        "greeting_afternoon": "مساء الخير",
        "greeting_evening": "مساء الخير",
        "welcome_btn": "🎙️ رسالة ترحيب",
        "intro_btn": "🤖 تقديم النظام",
        "patient_name": "اسم المريض",
        "patient_firstname": "الاسم الأول",
        "age": "العمر",
        "sex": "الجنس",
        "male": "ذكر",
        "female": "أنثى",
        "weight": "الوزن (كغ)",
        "sample_type": "نوع العينة",
        "microscope": "المجهر",
        "magnification": "التكبير",
        "preparation": "نوع التحضير",
        "technician": "التقني",
        "notes": "ملاحظات",
        "upload_image": "استيراد صورة",
        "take_photo": "📸 التقاط صورة (الكاميرا)",
        "or_upload": "📁 أو استيراد ملف",
        "analyze": "تحليل",
        "result": "النتيجة",
        "confidence": "الثقة",
        "risk": "المخاطر",
        "advice": "نصيحة طبية",
        "morphology": "المورفولوجيا",
        "description": "الوصف",
        "extra_tests": "فحوصات إضافية",
        "diagnostic_keys": "مفاتيح التشخيص",
        "lifecycle": "دورة الحياة",
        "download_pdf": "تحميل التقرير PDF",
        "save_db": "حفظ في قاعدة البيانات",
        "new_analysis": "تحليل جديد",
        "total_analyses": "مجموع التحاليل",
        "reliable": "موثوقة",
        "to_verify": "للتحقق",
        "most_frequent": "الأكثر شيوعاً",
        "avg_confidence": "متوسط الثقة",
        "start_quiz": "بدء الاختبار",
        "next_question": "السؤال التالي",
        "restart": "إعادة",
        "leaderboard": "الترتيب",
        "search": "بحث...",
        "dark_mode": "الوضع الليلي",
        "language": "اللغة",
        "daily_tip": "نصيحة اليوم",
        "system_info": "معلومات النظام",
        "users_management": "إدارة المستخدمين",
        "activity_log": "سجل النشاط",
        "create_user": "إنشاء مستخدم",
        "similarity": "التشابه",
        "image1": "الصورة 1",
        "image2": "الصورة 2",
        "compare_btn": "مقارنة",
        "no_data": "لا توجد بيانات",
        "camera_instruction": "ضع عدسة المجهر أمام الكاميرا",
        "name_required": "اسم المريض مطلوب",
        "saved_success": "تم حفظ النتيجة",
        "demo_mode": "وضع تجريبي (لا يوجد نموذج)",
        "low_confidence": "ثقة منخفضة. يُنصح بالتحقق اليدوي",
        "voice_welcome": "مرحباً بكم في مختبر DM الذكي! نحن سعداء بزيارتكم. هذا النظام مصمم لمساعدتكم في التشخيص الطفيلي.",
        "voice_intro": "أنا مختبر DM الذكي، النسخة السابعة، نظام تشخيص طفيلي بالذكاء الاصطناعي. تم تطويري من طرف تقنيين ساميين من المعهد الوطني للتكوين العالي شبه الطبي بورقلة: صباغ محمد ضياء الدين، خبير في الذكاء الاصطناعي والتصميم، وبن صغير محمد، خبير في المخبر والبيانات.",
    },
    "en": {
        "app_title": "DM Smart Lab AI",
        "login": "Secure Login",
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
        "patient_name": "Patient Name",
        "patient_firstname": "First Name",
        "age": "Age",
        "sex": "Sex",
        "male": "Male",
        "female": "Female",
        "weight": "Weight (kg)",
        "sample_type": "Sample Type",
        "microscope": "Microscope",
        "magnification": "Magnification",
        "preparation": "Preparation",
        "technician": "Technician",
        "notes": "Notes / Observations",
        "upload_image": "Upload image",
        "take_photo": "📸 Take a Photo (Camera)",
        "or_upload": "📁 Or upload a file",
        "analyze": "Analyze",
        "result": "Result",
        "confidence": "Confidence",
        "risk": "Risk",
        "advice": "Medical Advice",
        "morphology": "Morphology",
        "description": "Description",
        "extra_tests": "Additional Tests",
        "diagnostic_keys": "Diagnostic Keys",
        "lifecycle": "Life Cycle",
        "download_pdf": "Download PDF Report",
        "save_db": "Save to Database",
        "new_analysis": "New Analysis",
        "total_analyses": "Total Analyses",
        "reliable": "Reliable",
        "to_verify": "To Verify",
        "most_frequent": "Most Frequent",
        "avg_confidence": "Avg. Confidence",
        "start_quiz": "Start Quiz",
        "next_question": "Next Question",
        "restart": "Restart",
        "leaderboard": "Leaderboard",
        "search": "Search...",
        "dark_mode": "Dark Mode",
        "language": "Language",
        "daily_tip": "Daily Tip",
        "system_info": "System Information",
        "users_management": "Users Management",
        "activity_log": "Activity Log",
        "create_user": "Create User",
        "similarity": "Similarity",
        "image1": "Image 1",
        "image2": "Image 2",
        "compare_btn": "Compare",
        "no_data": "No data available",
        "camera_instruction": "Place the microscope eyepiece in front of the camera",
        "name_required": "Patient name is required",
        "saved_success": "Result saved",
        "demo_mode": "Demo mode (no model loaded)",
        "low_confidence": "Low confidence. Manual verification recommended",
        "voice_welcome": "Welcome to DM Smart Lab AI! We are delighted to have you. This artificial intelligence system is designed to assist you in parasitological diagnosis.",
        "voice_intro": "I am DM Smart Lab AI, version 7, a parasitological diagnosis system powered by artificial intelligence. I was developed by two senior technicians from INFSPM Ouargla: Sebbag Mohamed Dhia Eddine, AI and Design Expert, and Ben Sghir Mohamed, Laboratory and Data Expert. Together, we push the boundaries of modern parasitology!",
    }
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
    "fr": ["Selles", "Sang (Frottis)", "Sang (Goutte épaisse)", "Urines", "LCR", "Biopsie Cutanée", "Crachat", "Autre"],
    "ar": ["براز", "دم (لطاخة)", "دم (قطرة سميكة)", "بول", "سائل دماغي شوكي", "خزعة جلدية", "بلغم", "أخرى"],
    "en": ["Stool", "Blood (Smear)", "Blood (Thick drop)", "Urine", "CSF", "Skin Biopsy", "Sputum", "Other"]
}


# ============================================
#  HELPER: Translation
# ============================================
def t(key):
    lang = st.session_state.get("lang", "fr")
    return LANG.get(lang, LANG["fr"]).get(key, LANG["fr"].get(key, key))


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
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            speciality TEXT DEFAULT 'Laboratoire',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        )""")

        conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            patient_name TEXT NOT NULL,
            patient_firstname TEXT,
            patient_age INTEGER,
            patient_sex TEXT,
            patient_weight REAL,
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
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")

        conn.execute("""CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        conn.execute("""CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            category TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        conn.execute("""CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        _create_default_users(conn)


def _hash_password(password):
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()


def _verify_password(password, hashed):
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception:
            return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest() == hashed
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest() == hashed


def _create_default_users(conn):
    defaults = [
        ("admin", "admin2026", "Administrateur Système", "admin", "Administration"),
        ("dhia", "dhia2026", "Sebbag Mohamed Dhia Eddine", "admin", "IA & Conception"),
        ("mohamed", "mohamed2026", "Ben Sghir Mohamed", "technician", "Laboratoire"),
        ("demo", "demo123", "Utilisateur Démo", "viewer", "Démonstration"),
        ("tech1", "tech2026", "Technicien Labo 1", "technician", "Parasitologie"),
    ]
    for username, pwd, name, role, spec in defaults:
        existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if not existing:
            h = _hash_password(pwd)
            conn.execute(
                "INSERT INTO users (username, password_hash, full_name, role, speciality) VALUES (?,?,?,?,?)",
                (username, h, name, role, spec))


def db_verify_user(username, password):
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username=? AND is_active=1", (username,)).fetchone()
        if not user:
            return None
        if user["locked_until"]:
            try:
                lock_time = datetime.fromisoformat(user["locked_until"])
                if datetime.now() < lock_time:
                    return {"error": "locked", "until": lock_time}
                else:
                    conn.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?", (user["id"],))
            except Exception:
                pass
        if _verify_password(password, user["password_hash"]):
            conn.execute("""UPDATE users SET last_login=?, login_count=login_count+1,
                           failed_attempts=0, locked_until=NULL WHERE id=?""",
                         (datetime.now().isoformat(), user["id"]))
            return dict(user)
        else:
            new_attempts = user["failed_attempts"] + 1
            locked = None
            if new_attempts >= MAX_LOGIN_ATTEMPTS:
                locked = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
            conn.execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?",
                         (new_attempts, locked, user["id"]))
            return {"error": "wrong_password", "attempts_left": MAX_LOGIN_ATTEMPTS - new_attempts}


def db_create_user(username, password, full_name, role="viewer", speciality=""):
    with get_db() as conn:
        if conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone():
            return {"error": "exists"}
        h = _hash_password(password)
        conn.execute("INSERT INTO users (username, password_hash, full_name, role, speciality) VALUES (?,?,?,?,?)",
                     (username, h, full_name, role, speciality))
        return {"success": True}


def db_get_all_users():
    with get_db() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT id, username, full_name, role, is_active, last_login, login_count, created_at, speciality FROM users"
        ).fetchall()]


def db_toggle_user(user_id, active):
    with get_db() as conn:
        conn.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, user_id))


def db_change_password(user_id, new_pwd):
    with get_db() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (_hash_password(new_pwd), user_id))


def db_save_analysis(user_id, data):
    with get_db() as conn:
        conn.execute("""INSERT INTO analyses
            (user_id, patient_name, patient_firstname, patient_age, patient_sex, patient_weight,
             sample_type, microscope_type, magnification, preparation_type, technician1, technician2,
             notes, parasite_detected, confidence, risk_level, is_reliable, all_predictions, image_hash, is_demo)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                     (user_id, data.get("patient_name", ""), data.get("patient_firstname", ""),
                      data.get("patient_age", 0), data.get("patient_sex", ""), data.get("patient_weight", 0),
                      data.get("sample_type", ""), data.get("microscope_type", ""), data.get("magnification", ""),
                      data.get("preparation_type", ""), data.get("technician1", ""), data.get("technician2", ""),
                      data.get("notes", ""), data.get("parasite_detected", "Negative"),
                      data.get("confidence", 0),
                      data.get("risk_level", "none"), data.get("is_reliable", 0),
                      json.dumps(data.get("all_predictions", {})), data.get("image_hash", ""),
                      data.get("is_demo", 0)))
        return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def db_get_analyses(user_id=None, limit=500):
    with get_db() as conn:
        if user_id:
            rows = conn.execute("""SELECT a.*, u.full_name as analyst_name FROM analyses a
                JOIN users u ON a.user_id=u.id WHERE a.user_id=? ORDER BY a.analysis_date DESC LIMIT ?""",
                                (user_id, limit)).fetchall()
        else:
            rows = conn.execute("""SELECT a.*, u.full_name as analyst_name FROM analyses a
                JOIN users u ON a.user_id=u.id ORDER BY a.analysis_date DESC LIMIT ?""",
                                (limit,)).fetchall()
        return [dict(r) for r in rows]


def db_get_stats(user_id=None):
    with get_db() as conn:
        w = "WHERE user_id=?" if user_id else ""
        p = (user_id,) if user_id else ()
        total = conn.execute(f"SELECT COUNT(*) FROM analyses {w}", p).fetchone()[0]
        reliable = conn.execute(
            f"SELECT COUNT(*) FROM analyses {w} {'AND' if w else 'WHERE'} is_reliable=1", p).fetchone()[0]
        parasites = conn.execute(
            f"SELECT parasite_detected, COUNT(*) as cnt FROM analyses {w} GROUP BY parasite_detected ORDER BY cnt DESC",
            p).fetchall()
        avg_conf = conn.execute(f"SELECT AVG(confidence) FROM analyses {w}", p).fetchone()[0] or 0
        daily = conn.execute(
            f"SELECT DATE(analysis_date) as day, COUNT(*) as cnt FROM analyses {w} GROUP BY DATE(analysis_date) ORDER BY day DESC LIMIT 30",
            p).fetchall()
        return {
            "total": total, "reliable": reliable, "to_verify": total - reliable,
            "parasites": [dict(x) for x in parasites],
            "avg_confidence": round(avg_conf, 1),
            "daily": [dict(x) for x in daily],
            "most_frequent": parasites[0]["parasite_detected"] if parasites else "N/A"
        }


def db_get_trends(days=30):
    with get_db() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT DATE(analysis_date) as day, parasite_detected, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM analyses WHERE analysis_date >= date('now', ?) GROUP BY day, parasite_detected ORDER BY day
        """, (f"-{days} days",)).fetchall()]


def db_log_activity(user_id, username, action, details=""):
    try:
        with get_db() as conn:
            conn.execute("INSERT INTO activity_log (user_id, username, action, details) VALUES (?,?,?,?)",
                         (user_id, username, action, details))
    except Exception:
        pass


def db_get_activity_log(limit=300):
    with get_db() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()]


def db_save_quiz_score(user_id, username, score, total, pct, category="general"):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO quiz_scores (user_id, username, score, total_questions, percentage, category) VALUES (?,?,?,?,?,?)",
            (user_id, username, score, total, pct, category))


def db_get_leaderboard(limit=20):
    with get_db() as conn:
        return [dict(r) for r in conn.execute("""
            SELECT username, score, total_questions, percentage, category, timestamp
            FROM quiz_scores ORDER BY percentage DESC, timestamp ASC LIMIT ?""", (limit,)).fetchall()]


def db_validate_analysis(analysis_id, validator):
    with get_db() as conn:
        conn.execute("UPDATE analyses SET validated=1, validated_by=?, validation_date=? WHERE id=?",
                     (validator, datetime.now().isoformat(), analysis_id))


# Init DB
init_database()


# ============================================
#  PARASITE DATABASE (Multi-language enhanced)
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {
            "fr": "Kyste sphérique (10-15μm) à 4 noyaux, corps chromatoïde en cigare. Trophozoïte (20-40μm) avec pseudopodes digitiformes et hématies phagocytées.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 أنوية، جسم كروماتيني على شكل سيجار. الطور النشط (20-40 ميكرومتر) مع أقدام كاذبة وكريات حمراء مبتلعة.",
            "en": "Spherical cyst (10-15μm) with 4 nuclei, cigar-shaped chromatoid body. Trophozoite (20-40μm) with finger-like pseudopods and phagocytosed red blood cells."
        },
        "description": {
            "fr": "Protozoaire responsable de l'amibiase intestinale (dysenterie) et extra-intestinale (abcès hépatique). Transmission féco-orale.",
            "ar": "طفيلي أولي مسؤول عن الأميبيا المعوية (الزحار) والخارج معوية (خراج الكبد). الانتقال عبر الفم-البراز.",
            "en": "Protozoan causing intestinal amebiasis (dysentery) and extra-intestinal (liver abscess). Fecal-oral transmission."
        },
        "funny": {
            "fr": "Le ninja des intestins ! Il mange des globules rouges au petit-déjeuner !",
            "ar": "نينجا الأمعاء! يأكل كريات الدم الحمراء في الفطور!",
            "en": "The ninja of intestines! It eats red blood cells for breakfast!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Métronidazole 500mg x3/j (7-10j) + Amoebicide de contact (Intetrix). Contrôle EPS J15/J30.",
            "ar": "ميترونيدازول 500 ملغ ×3/يوم (7-10 أيام) + أميبيسيد تلامسي (إنتيتريكس). مراقبة EPS ي15/ي30.",
            "en": "Metronidazole 500mg x3/d (7-10d) + Contact amoebicide (Intetrix). Follow-up stool exam D15/D30."
        },
        "extra_tests": ["Sérologie amibienne (IgG/IgM)", "Échographie hépatique", "NFS + CRP + VS", "PCR Entamoeba", "Scanner abdominal si abcès"],
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": {
            "fr": "Kyste ingéré → Excystation → Trophozoïte → Invasion tissulaire → Enkystement → Émission",
            "ar": "كيس مبتلع → انفكاس → طور نشط → غزو أنسجة → تكيس → إخراج",
            "en": "Ingested cyst → Excystation → Trophozoite → Tissue invasion → Encystation → Emission"
        },
        "diagnostic_keys": {
            "fr": "• E. histolytica vs E. dispar: seule histolytica phagocyte les hématies\n• Kyste 4 noyaux (vs E. coli 8 noyaux)\n• Corps chromatoïdes en cigare\n• Mobilité directionnelle",
            "ar": "• E. histolytica مقابل E. dispar: فقط histolytica تبتلع الكريات الحمراء\n• كيس 4 أنوية (مقابل E. coli 8 أنوية)\n• أجسام كروماتينية على شكل سيجار\n• حركة اتجاهية",
            "en": "• E. histolytica vs E. dispar: only histolytica phagocytoses RBCs\n• Cyst 4 nuclei (vs E. coli 8 nuclei)\n• Cigar-shaped chromatoid bodies\n• Directional motility"
        }
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia (intestinalis)",
        "morphology": {
            "fr": "Trophozoïte piriforme en 'cerf-volant' (12-15μm), 2 noyaux (face de hibou), disque adhésif, 4 paires de flagelles. Kyste ovoïde (8-12μm) à 4 noyaux.",
            "ar": "الطور النشط كمثري على شكل طائرة ورقية (12-15 ميكرومتر)، نواتان (وجه البومة)، قرص لاصق، 4 أزواج من الأسواط. كيس بيضاوي (8-12 ميكرومتر) بـ 4 أنوية.",
            "en": "Pear-shaped 'kite' trophozoite (12-15μm), 2 nuclei (owl face), adhesive disk, 4 pairs of flagella. Ovoid cyst (8-12μm) with 4 nuclei."
        },
        "description": {
            "fr": "Flagellé du duodénum. Diarrhée graisseuse chronique, malabsorption. Transmission hydrique.",
            "ar": "سوطي الاثني عشر. إسهال دهني مزمن، سوء امتصاص. انتقال عبر الماء.",
            "en": "Duodenal flagellate. Chronic greasy diarrhea, malabsorption. Waterborne transmission."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil ! Un touriste qui refuse de partir !",
            "ar": "ينظر إليك بنظارته الشمسية! سائح يرفض المغادرة!",
            "en": "It stares at you with sunglasses! A tourist who refuses to leave!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Métronidazole 250mg x3/j (5j) OU Tinidazole 2g dose unique. Vérifier la source d'eau.",
            "ar": "ميترونيدازول 250 ملغ ×3/يوم (5 أيام) أو تينيدازول 2غ جرعة واحدة. التحقق من مصدر الماء.",
            "en": "Metronidazole 250mg x3/d (5d) OR Tinidazole 2g single dose. Check water source."
        },
        "extra_tests": ["Antigène Giardia (ELISA)", "Test de malabsorption", "EPS x3", "PCR Giardia"],
        "color": "#ff9500", "icon": "🟠",
        "lifecycle": {
            "fr": "Kyste ingéré → Excystation duodénale → Trophozoïte → Adhésion → Multiplication → Enkystement",
            "ar": "كيس مبتلع → انفكاس اثني عشري → طور نشط → التصاق → تكاثر → تكيس",
            "en": "Ingested cyst → Duodenal excystation → Trophozoite → Adhesion → Multiplication → Encystation"
        },
        "diagnostic_keys": {
            "fr": "• Forme en cerf-volant pathognomonique\n• 2 noyaux = face de hibou\n• Disque adhésif visible au Lugol\n• Mobilité 'feuille morte'",
            "ar": "• شكل الطائرة الورقية مميز\n• نواتان = وجه البومة\n• القرص اللاصق مرئي باللوغول\n• حركة 'ورقة ميتة'",
            "en": "• Kite shape is pathognomonic\n• 2 nuclei = owl face\n• Adhesive disk visible with Lugol\n• 'Falling leaf' motility"
        }
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / major / tropica",
        "morphology": {
            "fr": "Amastigotes ovoïdes (2-5μm) intracellulaires dans les macrophages. Noyau + kinétoplaste (MGG). Promastigotes fusiformes en culture.",
            "ar": "أماستيغوت بيضاوية (2-5 ميكرومتر) داخل الخلايا في البلاعم. نواة + كينيتوبلاست (MGG). بروماستيغوت مغزلية في الزراعة.",
            "en": "Ovoid amastigotes (2-5μm) intracellular in macrophages. Nucleus + kinetoplast (MGG). Fusiform promastigotes in culture."
        },
        "description": {
            "fr": "Transmis par le phlébotome. Cutanée (bouton d'Orient), viscérale (Kala-azar). En Algérie: L. infantum (nord), L. major (sud).",
            "ar": "ينتقل عبر ذبابة الرمل. جلدية (حبة الشرق)، حشوية (كالا آزار). في الجزائر: L. infantum (شمال)، L. major (جنوب).",
            "en": "Transmitted by sandfly. Cutaneous (Oriental sore), visceral (Kala-azar). In Algeria: L. infantum (north), L. major (south)."
        },
        "funny": {
            "fr": "Petit mais costaud ! Il squatte les macrophages comme un locataire qui ne paie pas !",
            "ar": "صغير لكن قوي! يحتل البلاعم مثل مستأجر لا يدفع الإيجار!",
            "en": "Small but tough! It squats in macrophages like a tenant who doesn't pay rent!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Cutanée: Glucantime IM. Viscérale: Amphotéricine B liposomale. MDO en Algérie.",
            "ar": "جلدية: غلوكانتيم عضلياً. حشوية: أمفوتيريسين ب ليبوزومال. مرض تبليغ إجباري في الجزائر.",
            "en": "Cutaneous: Glucantime IM. Visceral: Liposomal Amphotericin B. Notifiable disease in Algeria."
        },
        "extra_tests": ["IDR Monténégro", "Sérologie Leishmania", "Ponction médullaire", "Biopsie + MGG", "PCR Leishmania", "NFS"],
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": {
            "fr": "Piqûre phlébotome → Promastigotes → Phagocytose → Amastigotes intracellulaires → Multiplication → Lyse",
            "ar": "لدغة ذبابة الرمل → بروماستيغوت → بلعمة → أماستيغوت داخل خلوية → تكاثر → تحلل",
            "en": "Sandfly bite → Promastigotes → Phagocytosis → Intracellular amastigotes → Multiplication → Lysis"
        },
        "diagnostic_keys": {
            "fr": "• Amastigotes 2-5μm intracellulaires\n• Noyau + kinétoplaste au MGG\n• Culture NNN: promastigotes\n• PCR = gold standard espèce",
            "ar": "• أماستيغوت 2-5 ميكرومتر داخل خلوية\n• نواة + كينيتوبلاست بـ MGG\n• زراعة NNN: بروماستيغوت\n• PCR = المعيار الذهبي للأنواع",
            "en": "• Amastigotes 2-5μm intracellular\n• Nucleus + kinetoplast on MGG\n• NNN culture: promastigotes\n• PCR = species gold standard"
        }
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax / ovale / malariae",
        "morphology": {
            "fr": "P. falciparum: anneau 'bague à chaton', gamétocytes en banane. P. vivax: trophozoïte amiboïde, granulations Schüffner. Schizontes en rosace.",
            "ar": "P. falciparum: حلقة 'خاتم'، خلايا جنسية على شكل موزة. P. vivax: طور نشط أميبي، حبيبات شوفنر. شيزونت وردي.",
            "en": "P. falciparum: signet ring, banana-shaped gametocytes. P. vivax: amoeboid trophozoite, Schüffner's granules. Rosette schizonts."
        },
        "description": {
            "fr": "URGENCE MÉDICALE ! Agent du paludisme. P. falciparum: le plus mortel. Transmission par l'anophèle femelle.",
            "ar": "حالة طوارئ طبية! عامل الملاريا. P. falciparum: الأكثر فتكاً. ينتقل عبر أنثى الأنوفيل.",
            "en": "MEDICAL EMERGENCY! Malaria agent. P. falciparum: most lethal. Transmitted by female Anopheles."
        },
        "funny": {
            "fr": "Il demande le mariage à tes globules ! Et ses gamétocytes en banane... le clown du microscope !",
            "ar": "يطلب الزواج من كرياتك! وخلاياه الجنسية على شكل موز... مهرج المجهر!",
            "en": "It proposes to your blood cells! And its banana gametocytes... the clown of the microscope!"
        },
        "risk_level": "critical",
        "risk_display": {"fr": "🚨 URGENCE MÉDICALE", "ar": "🚨 حالة طوارئ طبية", "en": "🚨 MEDICAL EMERGENCY"},
        "advice": {
            "fr": "HOSPITALISATION ! ACT (Artémisinine). Quinine IV si grave. Parasitémie /4-6h. Surveillance glycémie, créatinine.",
            "ar": "دخول المستشفى! ACT (أرتيميسينين). كينين وريدي إذا كان خطيراً. طفيليات الدم كل 4-6 ساعات.",
            "en": "HOSPITALIZATION! ACT (Artemisinin). IV Quinine if severe. Parasitemia /4-6h. Monitor glucose, creatinine."
        },
        "extra_tests": ["TDR Paludisme (HRP2/pLDH)", "Frottis + Goutte épaisse URGENCE", "Parasitémie quantitative", "NFS complète", "Bilan hépato-rénal", "Glycémie", "Lactates"],
        "color": "#7f1d1d", "icon": "🚨",
        "lifecycle": {
            "fr": "Piqûre anophèle → Sporozoïtes → Hépatocytes → Mérozoïtes → Hématies → Gamétocytes → Cycle sexué moustique",
            "ar": "لدغة الأنوفيل → سبوروزويت → خلايا كبدية → ميروزويت → كريات حمراء → خلايا جنسية → دورة جنسية في البعوضة",
            "en": "Anopheles bite → Sporozoites → Hepatocytes → Merozoites → RBCs → Gametocytes → Sexual cycle in mosquito"
        },
        "diagnostic_keys": {
            "fr": "• URGENCE: résultat <2h\n• Frottis: identification espèce\n• Goutte épaisse: 10x plus sensible\n• >2% parasitémie = forme grave\n• Gamétocytes en banane = P. falciparum",
            "ar": "• طوارئ: النتيجة خلال أقل من ساعتين\n• لطاخة: تحديد النوع\n• قطرة سميكة: أكثر حساسية 10 مرات\n• >2% طفيليات = شكل خطير\n• خلايا جنسية موزية = P. falciparum",
            "en": "• URGENT: result <2h\n• Smear: species ID\n• Thick drop: 10x more sensitive\n• >2% parasitemia = severe\n• Banana gametocytes = P. falciparum"
        }
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "morphology": {
            "fr": "Forme en S/C (15-30μm), flagelle libre, membrane ondulante, kinétoplaste postérieur. Coloration MGG/Giemsa.",
            "ar": "شكل S/C (15-30 ميكرومتر)، سوط حر، غشاء متموج، كينيتوبلاست خلفي. تلوين MGG/جيمزا.",
            "en": "S/C shape (15-30μm), free flagellum, undulating membrane, posterior kinetoplast. MGG/Giemsa staining."
        },
        "description": {
            "fr": "Maladie du sommeil (T. brucei, mouche tsé-tsé) ou Chagas (T. cruzi, triatome). Phase hémolymphatique puis neurologique.",
            "ar": "مرض النوم (T. brucei، ذبابة تسي تسي) أو شاغاس (T. cruzi، بق ثلاثي). مرحلة دموية لمفاوية ثم عصبية.",
            "en": "Sleeping sickness (T. brucei, tsetse fly) or Chagas (T. cruzi, triatomine). Hemolymphatic then neurological phase."
        },
        "funny": {
            "fr": "Il court comme Mahrez avec sa membrane ondulante ! Et sa tsé-tsé, c'est le pire taxi !",
            "ar": "يركض مثل محرز بغشائه المتموج! وذبابة تسي تسي أسوأ تاكسي!",
            "en": "It runs like Mahrez with its undulating membrane! And its tsetse is the worst taxi!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Phase 1: Pentamidine/Suramine. Phase 2: NECT/Mélarsoprol. Ponction lombaire OBLIGATOIRE pour staging.",
            "ar": "المرحلة 1: بنتاميدين/سورامين. المرحلة 2: NECT/ميلارسوبرول. بزل قطني إجباري للتصنيف.",
            "en": "Phase 1: Pentamidine/Suramine. Phase 2: NECT/Melarsoprol. Lumbar puncture MANDATORY for staging."
        },
        "extra_tests": ["Ponction lombaire", "Sérologie (CATT)", "IgM sérique", "Suc ganglionnaire", "NFS"],
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": {
            "fr": "Piqûre tsé-tsé → Trypomastigotes → Sang/lymphe → Phase 1 → Franchissement BHE → Phase 2 neurologique",
            "ar": "لدغة تسي تسي → تريبوماستيغوت → دم/لمف → المرحلة 1 → عبور الحاجز الدموي الدماغي → المرحلة 2 العصبية",
            "en": "Tsetse bite → Trypomastigotes → Blood/lymph → Phase 1 → BBB crossing → Phase 2 neurological"
        },
        "diagnostic_keys": {
            "fr": "• Forme S/C avec membrane ondulante\n• Kinétoplaste postérieur\n• IgM très élevée\n• Staging par PL obligatoire",
            "ar": "• شكل S/C مع غشاء متموج\n• كينيتوبلاست خلفي\n• IgM مرتفع جداً\n• تصنيف بالبزل القطني إجباري",
            "en": "• S/C shape with undulating membrane\n• Posterior kinetoplast\n• Very high IgM\n• LP staging mandatory"
        }
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni / japonicum",
        "morphology": {
            "fr": "Œuf ovoïde (115-170μm) avec éperon terminal (S. haematobium) ou latéral (S. mansoni). Miracidium mobile.",
            "ar": "بيضة بيضاوية (115-170 ميكرومتر) مع شوكة طرفية (S. haematobium) أو جانبية (S. mansoni). ميراسيديوم متحرك.",
            "en": "Ovoid egg (115-170μm) with terminal spine (S. haematobium) or lateral spine (S. mansoni). Motile miracidium."
        },
        "description": {
            "fr": "Bilharziose. S. haematobium: uro-génitale (hématurie). S. mansoni: hépato-intestinale. 2ème endémie parasitaire mondiale.",
            "ar": "البلهارسيا. S. haematobium: بولي تناسلي (بيلة دموية). S. mansoni: كبدي معوي. ثاني وباء طفيلي عالمي.",
            "en": "Schistosomiasis. S. haematobium: urogenital (hematuria). S. mansoni: hepato-intestinal. 2nd global parasitic endemic."
        },
        "funny": {
            "fr": "L'œuf avec un dard ! La baignade peut coûter cher. Les cercaires = micro-torpilles !",
            "ar": "البيضة ذات الشوكة! السباحة قد تكلفك غالياً. السركاريا = طوربيدات صغيرة!",
            "en": "The egg with a stinger! Swimming can be costly. Cercariae = micro-torpedoes!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Praziquantel 40mg/kg dose unique. S. haematobium: urines de midi. Éviter eau douce en zone d'endémie.",
            "ar": "برازيكوانتيل 40 ملغ/كغ جرعة واحدة. S. haematobium: بول الظهيرة. تجنب المياه العذبة في مناطق التوطن.",
            "en": "Praziquantel 40mg/kg single dose. S. haematobium: midday urine. Avoid freshwater in endemic areas."
        },
        "extra_tests": ["ECBU + sédiment midi", "Sérologie Schistosoma", "Écho vésicale/hépatique", "NFS + Éosinophilie", "Biopsie rectale"],
        "color": "#ff9500", "icon": "🟠",
        "lifecycle": {
            "fr": "Œuf → Miracidium → Mollusque → Cercaire → Pénétration cutanée → Schistosomule → Vers adultes → Ponte",
            "ar": "بيضة → ميراسيديوم → رخويات → سركاريا → اختراق الجلد → شيستوسوميول → ديدان بالغة → وضع البيض",
            "en": "Egg → Miracidium → Snail → Cercaria → Skin penetration → Schistosomula → Adult worms → Laying eggs"
        },
        "diagnostic_keys": {
            "fr": "• S. haematobium: éperon TERMINAL, urines MIDI\n• S. mansoni: éperon LATÉRAL, selles\n• Miracidium vivant dans l'œuf\n• Éosinophilie élevée",
            "ar": "• S. haematobium: شوكة طرفية، بول الظهيرة\n• S. mansoni: شوكة جانبية، براز\n• ميراسيديوم حي في البيضة\n• فرط الحمضات",
            "en": "• S. haematobium: TERMINAL spine, MIDDAY urine\n• S. mansoni: LATERAL spine, stool\n• Living miracidium in egg\n• High eosinophilia"
        }
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": {
            "fr": "Absence d'éléments parasitaires après examen direct et concentration. Flore bactérienne normale.",
            "ar": "غياب العناصر الطفيلية بعد الفحص المباشر والتركيز. فلورا بكتيرية طبيعية.",
            "en": "No parasitic elements after direct exam and concentration. Normal bacterial flora."
        },
        "description": {
            "fr": "Échantillon négatif. Un seul examen négatif n'exclut pas (sensibilité ~50-60%). Répéter x3.",
            "ar": "عينة سلبية. فحص سلبي واحد لا يستبعد (حساسية ~50-60%). كرر ×3.",
            "en": "Negative sample. A single negative exam doesn't exclude (sensitivity ~50-60%). Repeat x3."
        },
        "funny": {
            "fr": "Rien à signaler ! Champagne ! Mais les parasites sont des maîtres du cache-cache !",
            "ar": "لا شيء يُذكر! لكن الطفيليات أساتذة في الاختباء!",
            "en": "Nothing to report! Cheers! But parasites are hide-and-seek masters!"
        },
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {
            "fr": "RAS. Répéter x3 si suspicion clinique. Bonne hygiène alimentaire.",
            "ar": "لا شيء. كرر ×3 إذا كان هناك اشتباه سريري. نظافة غذائية جيدة.",
            "en": "Clear. Repeat x3 if clinical suspicion. Good food hygiene."
        },
        "extra_tests": ["Répéter EPS x3", "Sérologie ciblée si besoin", "NFS (éosinophilie?)"],
        "color": "#00ff88", "icon": "🟢",
        "lifecycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "diagnostic_keys": {
            "fr": "• Direct + Lugol négatif\n• Concentration négative\n• Répéter x3 si doute",
            "ar": "• مباشر + لوغول سلبي\n• تركيز سلبي\n• كرر ×3 في حالة الشك",
            "en": "• Direct + Lugol negative\n• Concentration negative\n• Repeat x3 if doubt"
        }
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())


def get_parasite_field(parasite_name, field):
    """Get multilingual parasite field"""
    lang = st.session_state.get("lang", "fr")
    data = PARASITE_DB.get(parasite_name, PARASITE_DB["Negative"])
    val = data.get(field, "")
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", ""))
    return val


# ============================================
#  QUIZ QUESTIONS (60+)
# ============================================
QUIZ_QUESTIONS = [
    {"q": {"fr": "Quel parasite présente une 'bague à chaton' dans les hématies?", "ar": "أي طفيلي يظهر شكل 'الخاتم' في كريات الدم الحمراء؟", "en": "Which parasite shows a 'signet ring' in red blood cells?"}, "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": {"fr": "Le Plasmodium montre une forme en bague à chaton au stade trophozoïte jeune.", "ar": "البلازموديوم يظهر شكل الخاتم في مرحلة الطور النشط الصغير.", "en": "Plasmodium shows a signet ring form at the young trophozoite stage."}, "category": "Hématozoaires"},
    {"q": {"fr": "Le kyste mature de Giardia possède combien de noyaux?", "ar": "كم عدد أنوية كيس الجيارديا الناضج؟", "en": "How many nuclei does a mature Giardia cyst have?"}, "options": ["2", "4", "6", "8"], "answer": 1, "explanation": {"fr": "4 noyaux. Le trophozoïte en a 2.", "ar": "4 أنوية. الطور النشط له نواتان.", "en": "4 nuclei. The trophozoite has 2."}, "category": "Protozoaires intestinaux"},
    {"q": {"fr": "Quel parasite est transmis par le phlébotome?", "ar": "أي طفيلي ينتقل عبر ذبابة الرمل؟", "en": "Which parasite is transmitted by the sandfly?"}, "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": {"fr": "Leishmania = phlébotome (mouche des sables).", "ar": "ليشمانيا = ذبابة الرمل.", "en": "Leishmania = sandfly."}, "category": "Protozoaires tissulaires"},
    {"q": {"fr": "L'éperon terminal caractérise:", "ar": "الشوكة الطرفية تميز:", "en": "The terminal spine characterizes:"}, "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": {"fr": "S. haematobium = terminal. S. mansoni = latéral.", "ar": "S. haematobium = طرفية. S. mansoni = جانبية.", "en": "S. haematobium = terminal. S. mansoni = lateral."}, "category": "Helminthes"},
    {"q": {"fr": "Examen urgent en cas de suspicion de paludisme?", "ar": "الفحص الطارئ عند الاشتباه بالملاريا؟", "en": "Urgent exam when malaria is suspected?"}, "options": ["Coproculture", "ECBU", "Goutte épaisse + Frottis", "Sérologie"], "answer": 2, "explanation": {"fr": "Goutte épaisse + frottis = référence urgente.", "ar": "قطرة سميكة + لطاخة = المرجع الطارئ.", "en": "Thick drop + smear = urgent reference."}, "category": "Diagnostic"},
    {"q": {"fr": "Le trophozoïte d'E. histolytica se distingue par:", "ar": "يتميز الطور النشط لـ E. histolytica بـ:", "en": "E. histolytica trophozoite is distinguished by:"}, "options": ["Flagelles", "Hématies phagocytées", "Membrane ondulante", "Kinétoplaste"], "answer": 1, "explanation": {"fr": "Hématies phagocytées = critère de pathogénicité.", "ar": "الكريات الحمراء المبتلعة = معيار المرضية.", "en": "Phagocytosed RBCs = pathogenicity criterion."}, "category": "Protozoaires"},
    {"q": {"fr": "La maladie de Chagas est causée par:", "ar": "مرض شاغاس يسببه:", "en": "Chagas disease is caused by:"}, "options": ["T. b. gambiense", "T. cruzi", "L. donovani", "P. vivax"], "answer": 1, "explanation": {"fr": "T. cruzi transmis par les triatomes.", "ar": "T. cruzi ينتقل عبر البق الثلاثي.", "en": "T. cruzi transmitted by triatomines."}, "category": "Protozoaires sanguins"},
    {"q": {"fr": "Colorant pour les amastigotes de Leishmania?", "ar": "الملون المستخدم لأماستيغوت الليشمانيا؟", "en": "Stain for Leishmania amastigotes?"}, "options": ["Ziehl-Neelsen", "Gram", "MGG", "Lugol"], "answer": 2, "explanation": {"fr": "MGG = noyau + kinétoplaste visibles.", "ar": "MGG = النواة + الكينيتوبلاست مرئية.", "en": "MGG = nucleus + kinetoplast visible."}, "category": "Techniques"},
    {"q": {"fr": "Traitement de référence de la bilharziose?", "ar": "العلاج المرجعي للبلهارسيا؟", "en": "Reference treatment for schistosomiasis?"}, "options": ["Chloroquine", "Métronidazole", "Praziquantel", "Albendazole"], "answer": 2, "explanation": {"fr": "Praziquantel = choix n°1.", "ar": "برازيكوانتيل = الخيار الأول.", "en": "Praziquantel = first choice."}, "category": "Thérapeutique"},
    {"q": {"fr": "La 'face de hibou' est observée chez:", "ar": "'وجه البومة' يُلاحظ عند:", "en": "The 'owl face' is observed in:"}, "options": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "answer": 1, "explanation": {"fr": "2 noyaux symétriques de Giardia.", "ar": "نواتان متماثلتان للجيارديا.", "en": "2 symmetrical Giardia nuclei."}, "category": "Morphologie"},
    {"q": {"fr": "La technique de Ritchie est une méthode de:", "ar": "تقنية ريتشي هي طريقة:", "en": "The Ritchie technique is a method of:"}, "options": ["Coloration", "Concentration diphasique", "Culture", "Sérologie"], "answer": 1, "explanation": {"fr": "Formol-éther = concentration pour œufs/kystes.", "ar": "فورمول-إيثر = تركيز للبيض/الأكياس.", "en": "Formalin-ether = concentration for eggs/cysts."}, "category": "Techniques"},
    {"q": {"fr": "Le Lugol met en évidence:", "ar": "اللوغول يُظهر:", "en": "Lugol highlights:"}, "options": ["Flagelles", "Noyaux des kystes", "Hématies", "Bactéries"], "answer": 1, "explanation": {"fr": "L'iode colore le glycogène et les noyaux.", "ar": "اليود يلون الغليكوجين والأنوية.", "en": "Iodine stains glycogen and nuclei."}, "category": "Techniques"},
    {"q": {"fr": "L'objectif x100 nécessite:", "ar": "العدسة x100 تحتاج:", "en": "The x100 objective requires:"}, "options": ["Eau", "Huile d'immersion", "Alcool", "Sérum"], "answer": 1, "explanation": {"fr": "Huile = augmente l'indice de réfraction.", "ar": "الزيت = يزيد معامل الانكسار.", "en": "Oil = increases refractive index."}, "category": "Microscopie"},
    {"q": {"fr": "Le scotch-test de Graham recherche:", "ar": "اختبار سكوتش غراهام يبحث عن:", "en": "The Graham scotch test looks for:"}, "options": ["Giardia", "Enterobius (oxyure)", "Ascaris", "Taenia"], "answer": 1, "explanation": {"fr": "Œufs d'oxyure dans les plis périanaux.", "ar": "بيض الأكسيور في الطيات حول الشرج.", "en": "Pinworm eggs in perianal folds."}, "category": "Techniques"},
    {"q": {"fr": "Coloration pour Cryptosporidium?", "ar": "التلوين المستخدم للكريبتوسبوريديوم؟", "en": "Staining for Cryptosporidium?"}, "options": ["Lugol", "Ziehl-Neelsen modifié", "MGG", "Gram"], "answer": 1, "explanation": {"fr": "ZN modifié = oocystes roses sur fond vert.", "ar": "ZN معدل = أكياس بيضية وردية على خلفية خضراء.", "en": "Modified ZN = pink oocysts on green background."}, "category": "Techniques"},
    {"q": {"fr": "L'œuf d'Ascaris est:", "ar": "بيضة الأسكاريس:", "en": "The Ascaris egg is:"}, "options": ["Avec éperon", "Mamelonné/coque épaisse", "Operculé", "En citron"], "answer": 1, "explanation": {"fr": "Ovoïde, mamelonné, coque brune épaisse.", "ar": "بيضاوي، حُلَيمي، قشرة بنية سميكة.", "en": "Ovoid, mammillated, thick brown shell."}, "category": "Helminthes"},
    {"q": {"fr": "Le scolex de T. solium possède:", "ar": "رأس T. solium يحتوي على:", "en": "The T. solium scolex has:"}, "options": ["Ventouses seules", "Crochets seuls", "Ventouses + crochets", "Bothridies"], "answer": 2, "explanation": {"fr": "Ténia armé = 4 ventouses + crochets.", "ar": "الشريطية المسلحة = 4 ممصات + خطاطيف.", "en": "Armed tapeworm = 4 suckers + hooks."}, "category": "Helminthes"},
    {"q": {"fr": "L'éosinophilie sanguine oriente vers:", "ar": "فرط الحمضات في الدم يوجه نحو:", "en": "Blood eosinophilia points to:"}, "options": ["Infection bactérienne", "Helminthiase", "Virose", "Paludisme"], "answer": 1, "explanation": {"fr": "Éosinophilie = marqueur d'helminthiase.", "ar": "فرط الحمضات = علامة الديدان الطفيلية.", "en": "Eosinophilia = helminthiasis marker."}, "category": "Diagnostic"},
    {"q": {"fr": "La cysticercose est causée par:", "ar": "الكيسات المذنبة يسببها:", "en": "Cysticercosis is caused by:"}, "options": ["T. saginata adulte", "Larve de T. solium", "Echinococcus", "Ascaris"], "answer": 1, "explanation": {"fr": "Cysticerque de T. solium chez l'homme.", "ar": "كيسة مذنبة T. solium عند الإنسان.", "en": "T. solium cysticercus in humans."}, "category": "Helminthes"},
    {"q": {"fr": "En Algérie, la leishmaniose cutanée du sud est due à:", "ar": "في الجزائر، ليشمانيا الجلدية في الجنوب تسببها:", "en": "In Algeria, southern cutaneous leishmaniasis is caused by:"}, "options": ["L. infantum", "L. major", "L. tropica", "L. braziliensis"], "answer": 1, "explanation": {"fr": "L. major = cutanée zoonotique du sud.", "ar": "L. major = جلدية حيوانية المنشأ في الجنوب.", "en": "L. major = zoonotic cutaneous in the south."}, "category": "Épidémiologie"},
    {"q": {"fr": "Vecteur du paludisme?", "ar": "ناقل الملاريا؟", "en": "Malaria vector?"}, "options": ["Aedes", "Culex", "Anopheles", "Simulium"], "answer": 2, "explanation": {"fr": "Anophèle femelle = seul vecteur du Plasmodium.", "ar": "أنثى الأنوفيل = الناقل الوحيد للبلازموديوم.", "en": "Female Anopheles = only Plasmodium vector."}, "category": "Épidémiologie"},
    {"q": {"fr": "Le kyste hydatique est dû à:", "ar": "الكيس العداري يسببه:", "en": "Hydatid cyst is caused by:"}, "options": ["T. saginata", "Echinococcus granulosus", "Fasciola", "Toxocara"], "answer": 1, "explanation": {"fr": "Echinococcus granulosus (ver du chien).", "ar": "Echinococcus granulosus (دودة الكلب).", "en": "Echinococcus granulosus (dog tapeworm)."}, "category": "Helminthes"},
    {"q": {"fr": "Corps chromatoïde 'en cigare' typique de:", "ar": "الجسم الكروماتيني على شكل 'سيجار' نموذجي لـ:", "en": "'Cigar-shaped' chromatoid body typical of:"}, "options": ["E. histolytica", "E. coli", "Giardia", "Balantidium"], "answer": 0, "explanation": {"fr": "E. histolytica = cigare. E. coli = pointu.", "ar": "E. histolytica = سيجار. E. coli = مدبب.", "en": "E. histolytica = cigar. E. coli = pointed."}, "category": "Morphologie"},
    {"q": {"fr": "Protozoaire avec macro et micronoyau?", "ar": "الطفيلي الأولي بنواة كبيرة وصغيرة؟", "en": "Protozoan with macro and micronucleus?"}, "options": ["Giardia", "Balantidium coli", "Trichomonas", "Entamoeba"], "answer": 1, "explanation": {"fr": "Seul cilié pathogène humain.", "ar": "الهدبي الممرض الوحيد للإنسان.", "en": "Only pathogenic human ciliate."}, "category": "Morphologie"},
    {"q": {"fr": "Membrane ondulante caractéristique de:", "ar": "الغشاء المتموج مميز لـ:", "en": "Undulating membrane characteristic of:"}, "options": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "answer": 1, "explanation": {"fr": "Trypanosoma = membrane ondulante + flagelle.", "ar": "تريبانوسوما = غشاء متموج + سوط.", "en": "Trypanosoma = undulating membrane + flagellum."}, "category": "Morphologie"},
    {"q": {"fr": "Gamétocyte en 'banane' typique de:", "ar": "الخلية الجنسية على شكل 'موزة' نموذجية لـ:", "en": "'Banana' gametocyte typical of:"}, "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": {"fr": "Gamétocytes falciformes = pathognomoniques.", "ar": "الخلايا الجنسية المنجلية = مميزة.", "en": "Falciform gametocytes = pathognomonic."}, "category": "Hématozoaires"},
    {"q": {"fr": "Kyste d'E. coli: combien de noyaux?", "ar": "كيس E. coli: كم نواة؟", "en": "E. coli cyst: how many nuclei?"}, "options": ["4", "6", "8", "12"], "answer": 2, "explanation": {"fr": "E. coli = 8 noyaux (vs 4 pour E. histolytica).", "ar": "E. coli = 8 أنوية (مقابل 4 لـ E. histolytica).", "en": "E. coli = 8 nuclei (vs 4 for E. histolytica)."}, "category": "Morphologie"},
    {"q": {"fr": "Le Métronidazole est inefficace contre:", "ar": "ميترونيدازول غير فعال ضد:", "en": "Metronidazole is ineffective against:"}, "options": ["E. histolytica", "Giardia", "Helminthes", "Trichomonas"], "answer": 2, "explanation": {"fr": "Anti-protozoaire. Pas anti-helminthique.", "ar": "مضاد للأوليات. ليس مضاد للديدان.", "en": "Anti-protozoal. Not anti-helminthic."}, "category": "Thérapeutique"},
    {"q": {"fr": "L'Albendazole est:", "ar": "الألبندازول هو:", "en": "Albendazole is:"}, "options": ["Anti-protozoaire", "Anti-helminthique large spectre", "Antibiotique", "Antifongique"], "answer": 1, "explanation": {"fr": "Large spectre: nématodes + cestodes.", "ar": "واسع الطيف: ديدان أسطوانية + شريطية.", "en": "Broad spectrum: nematodes + cestodes."}, "category": "Thérapeutique"},
    {"q": {"fr": "Traitement du paludisme grave?", "ar": "علاج الملاريا الخطيرة؟", "en": "Treatment of severe malaria?"}, "options": ["Chloroquine", "Artésunate IV", "Métronidazole", "Praziquantel"], "answer": 1, "explanation": {"fr": "Artésunate IV = 1ère ligne (OMS).", "ar": "أرتيسونات وريدي = الخط الأول (منظمة الصحة العالمية).", "en": "IV Artesunate = 1st line (WHO)."}, "category": "Thérapeutique"},
    {"q": {"fr": "Ivermectine: indication principale?", "ar": "إيفرمكتين: الاستعمال الرئيسي؟", "en": "Ivermectin: main indication?"}, "options": ["Filarioses/strongyloïdose", "Paludisme", "Amibiase", "Giardiose"], "answer": 0, "explanation": {"fr": "Référence pour filarioses et strongyloïdose.", "ar": "المرجع للفيلاريا وداء الأسطوانيات.", "en": "Reference for filariasis and strongyloidiasis."}, "category": "Thérapeutique"},
    {"q": {"fr": "Patient d'Afrique: fièvre + frissons + accès?", "ar": "مريض من إفريقيا: حمى + قشعريرة + نوبات؟", "en": "African patient: fever + chills + paroxysms?"}, "options": ["Amibiase", "Paludisme", "Bilharziose", "Giardiose"], "answer": 1, "explanation": {"fr": "Paludisme jusqu'à preuve du contraire.", "ar": "ملاريا حتى يثبت العكس.", "en": "Malaria until proven otherwise."}, "category": "Cas clinique"},
    {"q": {"fr": "Hématurie + baignade eau douce Afrique?", "ar": "بيلة دموية + سباحة في ماء عذب بإفريقيا؟", "en": "Hematuria + freshwater swimming in Africa?"}, "options": ["Giardiose", "Paludisme", "Bilharziose urinaire", "Amibiase"], "answer": 2, "explanation": {"fr": "S. haematobium = bilharziose urinaire.", "ar": "S. haematobium = بلهارسيا بولية.", "en": "S. haematobium = urinary schistosomiasis."}, "category": "Cas clinique"},
    {"q": {"fr": "Chancre + adénopathies cervicales + somnolence?", "ar": "قرحة + تضخم عقد لمفاوية عنقية + نعاس؟", "en": "Chancre + cervical lymphadenopathy + drowsiness?"}, "options": ["Paludisme", "Leishmaniose", "Trypanosomiase", "Toxoplasmose"], "answer": 2, "explanation": {"fr": "THA = maladie du sommeil.", "ar": "THA = مرض النوم.", "en": "HAT = sleeping sickness."}, "category": "Cas clinique"},
    {"q": {"fr": "Bouton ulcéré indolore retour du Sahara?", "ar": "قرحة جلدية غير مؤلمة بعد العودة من الصحراء؟", "en": "Painless ulcerated lesion returning from Sahara?"}, "options": ["Leishmaniose cutanée", "Furoncle", "Anthrax", "Mycose"], "answer": 0, "explanation": {"fr": "Clou de Biskra = L. major.", "ar": "حبة بسكرة = L. major.", "en": "Biskra button = L. major."}, "category": "Cas clinique"},
    {"q": {"fr": "Bilharziose: contamination par:", "ar": "البلهارسيا: العدوى عبر:", "en": "Schistosomiasis: contamination by:"}, "options": ["Ingestion d'eau", "Contact cutané eau douce", "Piqûre d'insecte", "Voie aérienne"], "answer": 1, "explanation": {"fr": "Cercaires pénètrent la peau dans l'eau.", "ar": "السركاريا تخترق الجلد في الماء.", "en": "Cercariae penetrate skin in water."}, "category": "Épidémiologie"},
    {"q": {"fr": "Niclosamide agit sur:", "ar": "نيكلوساميد يعمل على:", "en": "Niclosamide acts on:"}, "options": ["Nématodes", "Cestodes (ténias)", "Trématodes", "Protozoaires"], "answer": 1, "explanation": {"fr": "Spécifique des cestodes.", "ar": "خاص بالشريطيات.", "en": "Specific for cestodes."}, "category": "Thérapeutique"},
    {"q": {"fr": "Goutte épaisse vs frottis mince:", "ar": "القطرة السميكة مقابل اللطاخة الرقيقة:", "en": "Thick drop vs thin smear:"}, "options": ["Même sensibilité", "GE 10x plus sensible", "FM plus sensible", "Pas comparable"], "answer": 1, "explanation": {"fr": "GE = 10x plus sensible pour faibles parasitémies.", "ar": "القطرة السميكة = أكثر حساسية 10 مرات للطفيليات المنخفضة.", "en": "TD = 10x more sensitive for low parasitemia."}, "category": "Techniques"},
    {"q": {"fr": "Œufs de S. haematobium se cherchent dans:", "ar": "بيض S. haematobium يُبحث عنه في:", "en": "S. haematobium eggs are found in:"}, "options": ["Selles du matin", "Urines de midi", "Sang nocturne", "LCR"], "answer": 1, "explanation": {"fr": "Pic d'excrétion = midi.", "ar": "ذروة الإخراج = الظهيرة.", "en": "Peak excretion = midday."}, "category": "Techniques"},
    {"q": {"fr": "Toxoplasma gondii: hôte définitif?", "ar": "Toxoplasma gondii: المضيف النهائي؟", "en": "Toxoplasma gondii: definitive host?"}, "options": ["Homme", "Chat", "Chien", "Moustique"], "answer": 1, "explanation": {"fr": "Le chat héberge le cycle sexué.", "ar": "القط يستضيف الدورة الجنسية.", "en": "Cat hosts the sexual cycle."}, "category": "Épidémiologie"},
    {"q": {"fr": "Technique de Willis utilise:", "ar": "تقنية ويليس تستخدم:", "en": "Willis technique uses:"}, "options": ["Formol-éther", "Eau salée saturée (flottation)", "Acide-alcool", "Lugol"], "answer": 1, "explanation": {"fr": "Flottation dans NaCl saturé.", "ar": "تعويم في كلوريد الصوديوم المشبع.", "en": "Flotation in saturated NaCl."}, "category": "Techniques"},
    {"q": {"fr": "Quelle espèce de Plasmodium possède des hypnozoïtes?", "ar": "أي نوع من البلازموديوم يمتلك هيبنوزويت؟", "en": "Which Plasmodium species has hypnozoites?"}, "options": ["P. falciparum", "P. vivax", "P. malariae", "Aucun"], "answer": 1, "explanation": {"fr": "P. vivax et P. ovale ont des hypnozoïtes hépatiques → rechutes.", "ar": "P. vivax و P. ovale لديهما هيبنوزويت كبدية → انتكاسات.", "en": "P. vivax and P. ovale have hepatic hypnozoites → relapses."}, "category": "Hématozoaires"},
    {"q": {"fr": "Trichomonas vaginalis: nombre de flagelles?", "ar": "Trichomonas vaginalis: عدد الأسواط؟", "en": "Trichomonas vaginalis: number of flagella?"}, "options": ["2", "4 antérieurs + 1 récurrent", "6", "8"], "answer": 1, "explanation": {"fr": "4 flagelles antérieurs + 1 flagelle récurrent formant la membrane ondulante.", "ar": "4 أسواط أمامية + 1 سوط راجع يشكل الغشاء المتموج.", "en": "4 anterior flagella + 1 recurrent forming undulating membrane."}, "category": "Morphologie"},
    {"q": {"fr": "Le test CATT est utilisé pour diagnostiquer:", "ar": "اختبار CATT يُستخدم لتشخيص:", "en": "The CATT test is used to diagnose:"}, "options": ["Paludisme", "Leishmaniose", "Trypanosomiase africaine", "Toxoplasmose"], "answer": 2, "explanation": {"fr": "Card Agglutination Test for Trypanosomiasis.", "ar": "اختبار التراص البطاقي لداء المثقبيات.", "en": "Card Agglutination Test for Trypanosomiasis."}, "category": "Diagnostic"},
    {"q": {"fr": "Fasciola hepatica: localisation adulte?", "ar": "Fasciola hepatica: موضع الدودة البالغة؟", "en": "Fasciola hepatica: adult location?"}, "options": ["Intestin grêle", "Côlon", "Voies biliaires", "Poumons"], "answer": 2, "explanation": {"fr": "La grande douve du foie vit dans les voies biliaires.", "ar": "المتورقة الكبدية تعيش في القنوات الصفراوية.", "en": "The liver fluke lives in bile ducts."}, "category": "Helminthes"},
    {"q": {"fr": "Strongyloides: particularité du cycle?", "ar": "Strongyloides: خاصية الدورة؟", "en": "Strongyloides: cycle peculiarity?"}, "options": ["Pas de cycle externe", "Auto-infestation", "Nécessite 2 hôtes", "Transmission aérienne"], "answer": 1, "explanation": {"fr": "Auto-infestation endogène possible → hyperinfestation chez l'immunodéprimé.", "ar": "إمكانية العدوى الذاتية الداخلية → فرط العدوى عند ناقصي المناعة.", "en": "Endogenous auto-infection possible → hyperinfection in immunocompromised."}, "category": "Helminthes"},
    {"q": {"fr": "Quel protozoaire est le plus grand parasite humain unicellulaire?", "ar": "أي طفيلي أولي هو أكبر طفيلي بشري وحيد الخلية؟", "en": "Which protozoan is the largest unicellular human parasite?"}, "options": ["Giardia", "Balantidium coli", "Entamoeba", "Trichomonas"], "answer": 1, "explanation": {"fr": "Balantidium coli peut atteindre 200μm.", "ar": "Balantidium coli يمكن أن يصل إلى 200 ميكرومتر.", "en": "Balantidium coli can reach 200μm."}, "category": "Morphologie"},
]


def get_quiz_text(item, field):
    """Get multilingual quiz field"""
    lang = st.session_state.get("lang", "fr")
    val = item.get(field, "")
    if isinstance(val, dict):
        return val.get(lang, val.get("fr", ""))
    return val


# ============================================
#  CHATBOT KNOWLEDGE BASE (Enhanced DM Bot)
# ============================================
CHATBOT_KB = {
    "amoeba": {
        "fr": "🔬 **Entamoeba histolytica**\n\n**Morphologie:** Kyste 10-15μm (4 noyaux), Trophozoïte 20-40μm (hématophage)\n**Diagnostic:** EPS direct + Lugol, sérologie si abcès\n**Traitement:** Métronidazole + Intetrix\n**Distinction:** E. histolytica (pathogène) vs E. dispar (non pathogène) → PCR\n\n💡 **Astuce:** Le corps chromatoïde en cigare est pathognomonique!",
        "ar": "🔬 **Entamoeba histolytica**\n\n**المورفولوجيا:** كيس 10-15 ميكرومتر (4 أنوية)، طور نشط 20-40 ميكرومتر (يأكل الدم)\n**التشخيص:** EPS مباشر + لوغول، مصلية إذا خراج\n**العلاج:** ميترونيدازول + إنتيتريكس",
        "en": "🔬 **Entamoeba histolytica**\n\n**Morphology:** Cyst 10-15μm (4 nuclei), Trophozoite 20-40μm (hematophagous)\n**Diagnosis:** Direct stool exam + Lugol, serology if abscess\n**Treatment:** Metronidazole + Intetrix"
    },
    "amibe": {"fr": "🔬 Même réponse que Amoeba. Voir Entamoeba histolytica.", "ar": "🔬 نفس إجابة الأميبا.", "en": "🔬 Same as Amoeba. See Entamoeba histolytica."},
    "giardia": {
        "fr": "🔬 **Giardia lamblia**\n\n**Morphologie:** Cerf-volant (12-15μm), face de hibou, 4 paires flagelles\n**Diagnostic:** EPS + Lugol, Ag Giardia ELISA\n**Traitement:** Métronidazole 250mg x3/j (5j) OU Tinidazole 2g\n**Clinique:** Diarrhée graisseuse, malabsorption\n\n💡 **Astuce:** La mobilité en 'feuille morte' est caractéristique!",
        "ar": "🔬 **Giardia lamblia**\n\n**المورفولوجيا:** طائرة ورقية (12-15 ميكرومتر)، وجه البومة، 4 أزواج أسواط\n**التشخيص:** EPS + لوغول، مستضد الجيارديا ELISA\n**العلاج:** ميترونيدازول 250 ملغ ×3/يوم (5 أيام)",
        "en": "🔬 **Giardia lamblia**\n\n**Morphology:** Kite shape (12-15μm), owl face, 4 pairs flagella\n**Diagnosis:** Stool exam + Lugol, Giardia Ag ELISA\n**Treatment:** Metronidazole 250mg x3/d (5d) OR Tinidazole 2g"
    },
    "leishmania": {
        "fr": "🔬 **Leishmania**\n\n**Morphologie:** Amastigotes 2-5μm dans macrophages (MGG)\n**Formes:** Cutanée (L. major), Viscérale (L. infantum)\n**En Algérie:** L. major (sud), L. infantum (nord) - MDO\n**Traitement:** Glucantime (cutanée), Amphotéricine B (viscérale)\n\n💡 **En Algérie:** La leishmaniose est une maladie à déclaration obligatoire!",
        "ar": "🔬 **ليشمانيا**\n\n**المورفولوجيا:** أماستيغوت 2-5 ميكرومتر في البلاعم (MGG)\n**الأشكال:** جلدية (L. major)، حشوية (L. infantum)\n**في الجزائر:** L. major (جنوب)، L. infantum (شمال) - تبليغ إجباري",
        "en": "🔬 **Leishmania**\n\n**Morphology:** Amastigotes 2-5μm in macrophages (MGG)\n**Forms:** Cutaneous (L. major), Visceral (L. infantum)\n**In Algeria:** L. major (south), L. infantum (north) - Notifiable"
    },
    "plasmodium": {
        "fr": "🚨 **URGENCE - Plasmodium (Paludisme)**\n\n**Morphologie:** Bague à chaton, gamétocytes banane (P.f)\n**Diagnostic URGENT:** Frottis + Goutte épaisse (<2h!)\n**Seuil:** >2% = forme grave → HOSPITALISATION\n**Traitement:** ACT ou Artésunate IV\n\n⚠️ **TOUJOURS considérer le paludisme chez un voyageur fébrile!**",
        "ar": "🚨 **طوارئ - البلازموديوم (الملاريا)**\n\n**التشخيص العاجل:** لطاخة + قطرة سميكة (<2 ساعة!)\n**العتبة:** >2% = شكل خطير → دخول المستشفى\n**العلاج:** ACT أو أرتيسونات وريدي",
        "en": "🚨 **EMERGENCY - Plasmodium (Malaria)**\n\n**URGENT Diagnosis:** Smear + Thick drop (<2h!)\n**Threshold:** >2% = severe → HOSPITALIZATION\n**Treatment:** ACT or IV Artesunate"
    },
    "malaria": {"fr": "🚨 Même chose que Plasmodium. URGENCE MÉDICALE!", "ar": "🚨 نفس البلازموديوم. حالة طوارئ طبية!", "en": "🚨 Same as Plasmodium. MEDICAL EMERGENCY!"},
    "paludisme": {"fr": "🚨 Même chose que Plasmodium. URGENCE MÉDICALE!", "ar": "🚨 نفس البلازموديوم. حالة طوارئ طبية!", "en": "🚨 Same as Plasmodium. MEDICAL EMERGENCY!"},
    "trypanosoma": {
        "fr": "🔬 **Trypanosoma**\n\n**Morphologie:** Forme S/C (15-30μm), membrane ondulante, kinétoplaste\n**Maladies:** Sommeil (T. brucei, tsé-tsé), Chagas (T. cruzi)\n**Staging:** Ponction lombaire OBLIGATOIRE\n**Traitement:** Phase 1: Pentamidine. Phase 2: NECT/Mélarsoprol",
        "ar": "🔬 **تريبانوسوما**\n\n**المورفولوجيا:** شكل S/C (15-30 ميكرومتر)، غشاء متموج، كينيتوبلاست\n**الأمراض:** النوم (T. brucei)، شاغاس (T. cruzi)",
        "en": "🔬 **Trypanosoma**\n\n**Morphology:** S/C shape (15-30μm), undulating membrane, kinetoplast\n**Diseases:** Sleeping sickness (T. brucei), Chagas (T. cruzi)"
    },
    "schistosoma": {
        "fr": "🔬 **Schistosoma (Bilharziose)**\n\n**S. haematobium:** Éperon TERMINAL, urines MIDI\n**S. mansoni:** Éperon LATÉRAL, selles\n**Traitement:** Praziquantel 40mg/kg\n**Prévention:** Éviter eau douce en zone d'endémie\n\n💡 **Rappel:** Toujours chercher les œufs dans les urines de MIDI pour S. haematobium!",
        "ar": "🔬 **البلهارسيا**\n\n**S. haematobium:** شوكة طرفية، بول الظهيرة\n**S. mansoni:** شوكة جانبية، براز\n**العلاج:** برازيكوانتيل 40 ملغ/كغ",
        "en": "🔬 **Schistosoma**\n\n**S. haematobium:** TERMINAL spine, MIDDAY urine\n**S. mansoni:** LATERAL spine, stool\n**Treatment:** Praziquantel 40mg/kg"
    },
    "bilharziose": {"fr": "Même chose que Schistosoma.", "ar": "نفس البلهارسيا.", "en": "Same as Schistosoma."},
    "microscope": {
        "fr": "🔬 **Microscopie en Parasitologie:**\n\n• **x10:** Repérage général\n• **x40:** Identification œufs/kystes\n• **x100 (immersion):** Détails morphologiques (Plasmodium, Leishmania)\n\n**Types:** Optique, fluorescence, contraste de phase, fond noir\n\n💡 **Conseil:** Toujours nettoyer l'objectif x100 après utilisation de l'huile!",
        "ar": "🔬 **المجهرية في علم الطفيليات:**\n\n• **x10:** استطلاع عام\n• **x40:** تحديد البيض/الأكياس\n• **x100 (غمر):** التفاصيل المورفولوجية",
        "en": "🔬 **Microscopy in Parasitology:**\n\n• **x10:** General survey\n• **x40:** Egg/cyst identification\n• **x100 (immersion):** Morphological details"
    },
    "coloration": {
        "fr": "🎨 **Colorations:**\n\n• **Lugol:** Noyaux des kystes, glycogène\n• **MGG/Giemsa:** Parasites sanguins (Plasmodium, Leishmania)\n• **Ziehl-Neelsen modifié:** Cryptosporidium, Microsporidies\n• **Trichrome:** Parasites intestinaux\n• **Hématoxyline ferrique:** Amibes\n\n💡 **Le Lugol doit être préparé frais chaque semaine!**",
        "ar": "🎨 **التلوينات:**\n\n• **لوغول:** أنوية الأكياس\n• **MGG/جيمزا:** طفيليات الدم\n• **ZN معدل:** كريبتوسبوريديوم",
        "en": "🎨 **Stainings:**\n\n• **Lugol:** Cyst nuclei\n• **MGG/Giemsa:** Blood parasites\n• **Modified ZN:** Cryptosporidium"
    },
    "selle": {
        "fr": "**EPS Complet:**\n\n1. Examen macroscopique (consistance, couleur, sang, mucus)\n2. Examen direct (NaCl 0.9% + Lugol)\n3. Technique de concentration (Ritchie/Willis)\n\n⚠️ Examiner dans 30 min! Répéter x3 à intervalles!\n\n💡 **Selles liquides → trophozoïtes. Selles formées → kystes.**",
        "ar": "**فحص البراز الكامل:**\n\n1. فحص عياني\n2. فحص مباشر (NaCl + لوغول)\n3. تقنية تركيز (ريتشي/ويليس)\n\n⚠️ افحص خلال 30 دقيقة! كرر ×3!",
        "en": "**Complete Stool Exam:**\n\n1. Macroscopic exam\n2. Direct exam (NaCl + Lugol)\n3. Concentration technique (Ritchie/Willis)\n\n⚠️ Examine within 30 min! Repeat x3!"
    },
    "hygiene": {
        "fr": "🧼 **Prévention:**\n\n✅ Lavage des mains (30 secondes minimum)\n✅ Eau potable (filtration/ébullition)\n✅ Cuisson viande >65°C\n✅ Moustiquaires imprégnées\n✅ Éviter eaux stagnantes\n✅ Lavage fruits et légumes\n✅ Assainissement\n\n💡 **80% des parasitoses sont évitables par l'hygiène!**",
        "ar": "🧼 **الوقاية:**\n\n✅ غسل اليدين (30 ثانية على الأقل)\n✅ ماء صالح للشرب\n✅ طهي اللحم >65 درجة\n✅ ناموسيات مشربة\n✅ تجنب المياه الراكدة",
        "en": "🧼 **Prevention:**\n\n✅ Handwashing (30 seconds minimum)\n✅ Safe drinking water\n✅ Cook meat >65°C\n✅ Impregnated mosquito nets\n✅ Avoid stagnant water"
    },
    "concentration": {
        "fr": "🧪 **Techniques de concentration:**\n\n• **Ritchie (Formol-éther):** Référence, diphasique, œufs + kystes\n• **Willis (Flottation NaCl):** Simple, rapide, ankylostomes\n• **Kato-Katz:** Semi-quantitatif, épidémiologie\n• **Baermann:** Larves de Strongyloides\n• **MIF:** Fixation + coloration\n\n💡 **Ritchie = technique de référence universelle!**",
        "ar": "🧪 **تقنيات التركيز:**\n\n• **ريتشي:** المرجع، ثنائي الطور\n• **ويليس:** تعويم، بسيط وسريع\n• **كاتو-كاتز:** شبه كمي",
        "en": "🧪 **Concentration techniques:**\n\n• **Ritchie:** Reference, diphasic\n• **Willis:** Flotation, simple, rapid\n• **Kato-Katz:** Semi-quantitative"
    },
    "toxoplasma": {
        "fr": "🔬 **Toxoplasma gondii**\n\n**Morphologie:** Tachyzoïte en arc (4-8μm), bradyzoïte dans kystes tissulaires\n**Hôte définitif:** Chat (oocystes dans les fèces)\n**Risque:** Femme enceinte (séronégative) → toxoplasmose congénitale\n**Diagnostic:** Sérologie IgG/IgM, avidité des IgG\n**Prévention:** Cuisson viande, lavage crudités, éviter litière chat\n\n⚠️ **DANGER chez la femme enceinte séronégative!**",
        "ar": "🔬 **توكسوبلازما**\n\nالمضيف النهائي: القط\nالخطر: المرأة الحامل سلبية المصل\nالتشخيص: مصلية IgG/IgM",
        "en": "🔬 **Toxoplasma gondii**\n\nDefinitive host: Cat\nRisk: Seronegative pregnant woman\nDiagnosis: IgG/IgM serology"
    },
    "ascaris": {
        "fr": "🔬 **Ascaris lumbricoides**\n\n**Morphologie:** Ver rond (15-35cm!), œuf mamelonné 60-70μm\n**Cycle:** Ingestion → larve → migration hépatopulmonaire → intestin\n**Syndrome de Löffler:** Toux + éosinophilie + infiltrats pulmonaires\n**Traitement:** Albendazole 400mg dose unique\n\n💡 **Le plus grand nématode intestinal humain!**",
        "ar": "🔬 **الأسكاريس**\n\nدودة أسطوانية (15-35 سم!)\nبيضة حُلَيمية 60-70 ميكرومتر\nالعلاج: ألبندازول 400 ملغ",
        "en": "🔬 **Ascaris lumbricoides**\n\nRound worm (15-35cm!)\nMammillated egg 60-70μm\nTreatment: Albendazole 400mg single dose"
    },
    "taenia": {
        "fr": "🔬 **Taenia**\n\n**T. saginata:** Ténia inerme (bœuf), pas de crochets\n**T. solium:** Ténia armé (porc), crochets → risque cysticercose!\n**Diagnostic:** Anneaux dans les selles, scotch-test anal\n**Traitement:** Praziquantel ou Niclosamide\n\n⚠️ **T. solium = risque de cysticercose cérébrale!**",
        "ar": "🔬 **الشريطية**\n\nT. saginata: من البقر\nT. solium: من الخنزير → خطر الكيسات المذنبة!\nالعلاج: برازيكوانتيل",
        "en": "🔬 **Taenia**\n\nT. saginata: beef tapeworm\nT. solium: pork tapeworm → cysticercosis risk!\nTreatment: Praziquantel"
    },
    "oxyure": {
        "fr": "🔬 **Enterobius vermicularis (Oxyure)**\n\n**Morphologie:** Ver blanc (1cm), œuf asymétrique\n**Diagnostic:** Scotch-test de Graham (le matin avant toilette!)\n**Symptôme:** Prurit anal nocturne chez l'enfant\n**Traitement:** Flubendazole, traiter TOUTE la famille!\n\n💡 **Le scotch-test se fait le MATIN au réveil avant la toilette!**",
        "ar": "🔬 **الأكسيور**\n\nدودة بيضاء (1سم)\nالتشخيص: اختبار سكوتش غراهام صباحاً\nالعلاج: فلوبندازول، علاج كل العائلة!",
        "en": "🔬 **Enterobius (Pinworm)**\n\nWhite worm (1cm)\nDiagnosis: Graham scotch test (morning!)\nTreatment: Flubendazole, treat the WHOLE family!"
    },
    "cryptosporidium": {
        "fr": "🔬 **Cryptosporidium**\n\n**Morphologie:** Oocyste 4-6μm (très petit!)\n**Coloration:** Ziehl-Neelsen modifié (rose sur fond vert)\n**Clinique:** Diarrhée chez l'immunodéprimé (VIH)\n**Traitement:** Nitazoxanide, restauration immunitaire\n\n💡 **ZN modifié = seule coloration de référence!**",
        "ar": "🔬 **كريبتوسبوريديوم**\n\nكيس بيضي 4-6 ميكرومتر (صغير جداً!)\nالتلوين: ZN معدل\nالعلاج: نيتازوكسانيد",
        "en": "🔬 **Cryptosporidium**\n\nOocyst 4-6μm (very small!)\nStaining: Modified ZN\nTreatment: Nitazoxanide"
    },
    "bonjour": {"fr": "👋 Bonjour! Je suis **DM Bot** 🤖, votre assistant parasitologique.\n\n🔬 Parasites | 💊 Traitements | 🧪 Techniques | 🩺 Cas cliniques\n\nQue voulez-vous savoir?", "ar": "👋 مرحباً! أنا **DM Bot** 🤖، مساعدك في علم الطفيليات.\n\nماذا تريد أن تعرف؟", "en": "👋 Hello! I'm **DM Bot** 🤖, your parasitology assistant.\n\nWhat would you like to know?"},
    "salut": {"fr": "Salut! 😊 Comment puis-je vous aider?", "ar": "مرحباً! 😊 كيف أقدر أساعدك؟", "en": "Hi! 😊 How can I help?"},
    "مرحبا": {"fr": "مرحباً! أنا DM Bot!", "ar": "مرحباً! أنا **DM Bot** 🤖 مساعدك في علم الطفيليات. اكتب اسم أي طفيلي!", "en": "Hello! I'm DM Bot!"},
    "hello": {"fr": "Hello! 👋 I'm DM Bot.", "ar": "مرحباً! أنا DM Bot!", "en": "Hello! 👋 I'm **DM Bot** 🤖. How can I help?"},
    "merci": {"fr": "De rien! 😊 La parasitologie est ma passion!", "ar": "عفواً! 😊 علم الطفيليات شغفي!", "en": "You're welcome! 😊 Parasitology is my passion!"},
    "شكرا": {"fr": "عفواً!", "ar": "عفواً! 😊", "en": "You're welcome!"},
    "aide": {"fr": "📚 **Je connais:**\n\nAmoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Oxyure, Cryptosporidium, Trichomonas, Fasciola, Strongyloides, Balantidium...\n\nEt: microscopie, colorations, concentration, EPS, diagnostic, traitements, épidémiologie, hygiène!\n\n💡 Tapez un mot-clé!", "ar": "📚 **أعرف:**\n\nالأميبا، الجيارديا، الليشمانيا، البلازموديوم، التريبانوسوما، البلهارسيا، الأسكاريس، الشريطية، التوكسوبلازما...\n\nاكتب كلمة مفتاحية!", "en": "📚 **I know:**\n\nAll parasites and lab techniques. Type a keyword!"},
    "help": {"fr": "📚 I know all parasites!", "ar": "📚 أعرف كل الطفيليات!", "en": "📚 I know all parasites and lab techniques. Type a keyword!"},
    "مساعدة": {"fr": "اكتب كلمة مفتاحية!", "ar": "📚 اكتب اسم أي طفيلي أو تقنية مخبرية وسأجيبك!", "en": "Type a keyword!"},
}

DAILY_TIPS = {
    "fr": [
        "💡 Examiner les selles dans les 30 min pour voir les trophozoïtes mobiles.",
        "💡 Le Lugol met en évidence les noyaux des kystes. Dilution fraîche chaque semaine.",
        "💡 Frottis mince: angle 45° pour une monocouche parfaite.",
        "💡 La goutte épaisse est 10x plus sensible que le frottis mince.",
        "💡 Urines de midi pour S. haematobium (pic d'excrétion).",
        "💡 Répéter l'EPS x3 à quelques jours d'intervalle.",
        "💡 Métronidazole = Amoeba + Giardia + Trichomonas. Retenez ce trio!",
        "💡 Ziehl-Neelsen modifié est indispensable pour Cryptosporidium.",
        "💡 En paludisme: 1ère GE négative ne suffit pas. Répéter à 6-12h.",
        "💡 Le phlébotome est actif au crépuscule. Moustiquaires!",
        "💡 Éosinophilie = helminthiase probable. Toujours vérifier!",
        "💡 E. coli 8 noyaux vs E. histolytica 4 noyaux = critère n°1.",
        "💡 Selles liquides → trophozoïtes. Selles formées → kystes.",
        "💡 PCR = gold standard pour identifier l'espèce de Leishmania.",
    ],
    "ar": [
        "💡 افحص البراز خلال 30 دقيقة لرؤية الأطوار النشطة المتحركة.",
        "💡 اللوغول يُظهر أنوية الأكياس. تحضير طازج كل أسبوع.",
        "💡 القطرة السميكة أكثر حساسية 10 مرات من اللطاخة.",
        "💡 بول الظهيرة لـ S. haematobium (ذروة الإخراج).",
        "💡 كرر EPS ×3 بفاصل عدة أيام.",
        "💡 ميترونيدازول = أميبا + جيارديا + تريكوموناس!",
        "💡 فرط الحمضات = ديدان طفيلية محتملة. تحقق دائماً!",
    ],
    "en": [
        "💡 Examine stool within 30 min to see motile trophozoites.",
        "💡 Lugol highlights cyst nuclei. Fresh preparation weekly.",
        "💡 Thick drop is 10x more sensitive than thin smear.",
        "💡 Midday urine for S. haematobium (peak excretion).",
        "💡 Repeat stool exam x3 at intervals.",
        "💡 Metronidazole = Amoeba + Giardia + Trichomonas!",
        "💡 Eosinophilia = probable helminthiasis. Always check!",
    ]
}


# ============================================
#  SESSION STATE
# ============================================
DEFAULTS = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_role": "viewer",
    "user_full_name": "",
    "dark_mode": True,
    "lang": "fr",
    "demo_seed": None,
    "heatmap_seed": None,
    "quiz_state": {"current": 0, "score": 0, "answered": [], "active": False},
    "chat_history": [],
    "voice_playing": False,
}
for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================
#  HELPERS
# ============================================
def user_has_role(min_level):
    role = st.session_state.get("user_role", "viewer")
    return ROLES.get(role, {}).get("level", 0) >= min_level


def risk_color(level):
    return {"critical": "#ff0040", "high": "#ff3366", "medium": "#ff9500", "low": "#00e676", "none": "#00ff88"}.get(level, "#888")


def risk_percent(level):
    return {"critical": 100, "high": 80, "medium": 50, "low": 25, "none": 0}.get(level, 0)


def get_role_label():
    lang = st.session_state.get("lang", "fr")
    role = st.session_state.get("user_role", "viewer")
    return ROLES.get(role, {}).get(f"label_{lang}", ROLES.get(role, {}).get("label_fr", ""))


def chatbot_reply(user_msg):
    lang = st.session_state.get("lang", "fr")
    msg_lower = user_msg.lower().strip()

    for key, response in CHATBOT_KB.items():
        if key in msg_lower:
            if isinstance(response, dict):
                return response.get(lang, response.get("fr", ""))
            return response

    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if name.lower() in msg_lower or data["scientific_name"].lower() in msg_lower:
            morph = get_parasite_field(name, "morphology")
            desc = get_parasite_field(name, "description")
            adv = get_parasite_field(name, "advice")
            fun = get_parasite_field(name, "funny")
            return f"**{name}** ({data['scientific_name']})\n\n📋 {desc}\n\n🔬 {morph}\n\n💊 {adv}\n\n🤖 {fun}"

    defaults = {
        "fr": "🤖 Je suis **DM Bot**. Tapez un mot-clé (amoeba, giardia, microscope, coloration, aide...)\n\n💡 Je connais tous les parasites, techniques de labo, et traitements!",
        "ar": "🤖 أنا **DM Bot**. اكتب كلمة مفتاحية (amoeba, giardia, مساعدة...)\n\n💡 أعرف كل الطفيليات والتقنيات المخبرية!",
        "en": "🤖 I'm **DM Bot**. Type a keyword (amoeba, giardia, microscope, help...)\n\n💡 I know all parasites, lab techniques, and treatments!"
    }
    return defaults.get(lang, defaults["fr"])


def speak_js(text, lang_code=None):
    """Non-blocking voice using browser JS"""
    if lang_code is None:
        lang_code = st.session_state.get("lang", "fr")
    safe = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
    jl = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(lang_code, "fr-FR")
    st.markdown(
        f"""<script>
        try {{
            window.speechSynthesis.cancel();
            var m = new SpeechSynthesisUtterance('{safe}');
            m.lang = '{jl}'; m.rate = 0.9;
            window.speechSynthesis.speak(m);
        }} catch(e) {{}}
        </script>""",
        unsafe_allow_html=True
    )


def stop_speech_js():
    st.markdown("""<script>try{window.speechSynthesis.cancel();}catch(e){}</script>""", unsafe_allow_html=True)


# ============================================
#  AI ENGINE
# ============================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    model, model_name, model_type = None, None, None
    try:
        import tensorflow as tf
        files = [f for f in os.listdir(".") if os.path.isfile(f)]
        for ext in [".keras", ".h5"]:
            found = [f for f in files if f.endswith(ext)]
            if found:
                model_name = found[0]
                model = tf.keras.models.load_model(model_name, compile=False)
                model_type = "keras"
                break
        if model is None:
            tflite = [f for f in files if f.endswith(".tflite")]
            if tflite:
                model_name = tflite[0]
                model = tf.lite.Interpreter(model_path=model_name)
                model.allocate_tensors()
                model_type = "tflite"
    except Exception:
        pass
    return model, model_name, model_type


def predict_image(model, model_type, image, demo_seed=None):
    result = {"label": "Negative", "confidence": 0, "all_predictions": {}, "is_reliable": False, "is_demo": False, "risk_level": "none"}

    risk_map = {
        "Plasmodium": "critical", "Amoeba (E. histolytica)": "high",
        "Leishmania": "high", "Trypanosoma": "high",
        "Giardia": "medium", "Schistosoma": "medium", "Negative": "none"
    }

    if model is None:
        result["is_demo"] = True
        if demo_seed is None:
            demo_seed = random.randint(0, 999999)
        rng = random.Random(demo_seed)
        label = rng.choice(CLASS_NAMES)
        conf = rng.randint(55, 98)
        all_p = {}
        rem = 100.0 - conf
        others = [c for c in CLASS_NAMES if c != label]
        for cls in others:
            v = round(rng.uniform(0, rem / max(1, len(others))), 1)
            all_p[cls] = v
        all_p[label] = float(conf)
        result.update({
            "label": label, "confidence": conf, "all_predictions": all_p,
            "is_reliable": conf >= CONFIDENCE_THRESHOLD,
            "risk_level": risk_map.get(label, "none")
        })
        return result

    try:
        import tensorflow as tf
        img = ImageOps.fit(image.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
        arr = np.asarray(img).astype(np.float32) / 127.5 - 1.0
        batch = np.expand_dims(arr, 0)
        if model_type == "tflite":
            inp, out = model.get_input_details(), model.get_output_details()
            model.set_tensor(inp[0]['index'], batch)
            model.invoke()
            preds = model.get_tensor(out[0]['index'])[0]
        else:
            preds = model.predict(batch, verbose=0)[0]
        idx = int(np.argmax(preds))
        conf = int(preds[idx] * 100)
        label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else "Negative"
        all_p = {CLASS_NAMES[i]: round(float(preds[i]) * 100, 1) for i in range(min(len(preds), len(CLASS_NAMES)))}
        result.update({
            "label": label, "confidence": conf, "all_predictions": all_p,
            "is_reliable": conf >= CONFIDENCE_THRESHOLD,
            "risk_level": risk_map.get(label, "none")
        })
    except Exception as e:
        st.error(f"Prediction error: {e}")
    return result


# ============================================
#  IMAGE PROCESSING
# ============================================
def generate_heatmap(image, seed=None):
    img = image.copy().convert("RGB")
    w, h = img.size
    if seed is None:
        seed = hash(img.tobytes()[:1000]) % 1000000
    rng = random.Random(seed)
    gray = ImageOps.grayscale(img)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    ea = np.array(edges)
    bs = 32
    mx, best_cx, best_cy = 0, w // 2, h // 2
    for y in range(0, h - bs, bs // 2):
        for x in range(0, w - bs, bs // 2):
            s = np.mean(ea[y:y + bs, x:x + bs])
            if s > mx:
                mx, best_cx, best_cy = s, x + bs // 2, y + bs // 2
    best_cx += rng.randint(-w // 10, w // 10)
    best_cy += rng.randint(-h // 10, h // 10)
    best_cx = max(50, min(w - 50, best_cx))
    best_cy = max(50, min(h - 50, best_cy))
    heatmap = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(heatmap)
    max_r = min(w, h) // 3
    for r in range(max_r, 0, -2):
        alpha = max(0, min(200, int(200 * (1 - r / max_r))))
        ratio = r / max_r
        if ratio > 0.65:
            color = (0, 255, 100, alpha // 4)
        elif ratio > 0.35:
            color = (255, 255, 0, alpha // 2)
        else:
            color = (255, 0, 60, alpha)
        draw.ellipse([best_cx - r, best_cy - r, best_cx + r, best_cy + r], fill=color)
    for _ in range(rng.randint(2, 4)):
        sx = rng.randint(w // 4, 3 * w // 4)
        sy = rng.randint(h // 4, 3 * h // 4)
        sr = rng.randint(20, max_r // 3)
        for r in range(sr, 0, -3):
            a = max(0, int(80 * (1 - r / sr)))
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(255, 200, 0, a))
    return Image.alpha_composite(img.convert('RGBA'), heatmap).convert('RGB')


def apply_thermal(image):
    e = ImageEnhance.Contrast(image).enhance(1.5)
    g = ImageOps.grayscale(e).filter(ImageFilter.GaussianBlur(1))
    return ImageOps.colorize(g, black="navy", white="yellow", mid="red")


def apply_edge_detection(image):
    return ImageOps.grayscale(image).filter(ImageFilter.FIND_EDGES)


def apply_enhanced_contrast(image):
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(image).enhance(2.0)).enhance(2.0)


def apply_negative_filter(image):
    return ImageOps.invert(image.convert("RGB"))


def apply_emboss(image):
    return image.filter(ImageFilter.EMBOSS)


def apply_adjustments(image, brightness=1.0, contrast=1.0, saturation=1.0):
    img = image.copy()
    if brightness != 1.0:
        img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0:
        img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0:
        img = ImageEnhance.Color(img).enhance(saturation)
    return img


def zoom_image(image, level):
    if level <= 1.0:
        return image
    w, h = image.size
    nw, nh = int(w / level), int(h / level)
    l = (w - nw) // 2
    tt = (h - nh) // 2
    return image.crop((l, tt, l + nw, tt + nh)).resize((w, h), Image.LANCZOS)


def compare_images(img1, img2):
    a1 = np.array(img1.convert("RGB").resize((128, 128))).astype(float)
    a2 = np.array(img2.convert("RGB").resize((128, 128))).astype(float)
    mse = np.mean((a1 - a2) ** 2)
    mu1, mu2 = np.mean(a1), np.mean(a2)
    s1, s2 = np.std(a1), np.std(a2)
    s12 = np.mean((a1 - mu1) * (a2 - mu2))
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * mu1 * mu2 + c1) * (2 * s12 + c2)) / ((mu1 ** 2 + mu2 ** 2 + c1) * (s1 ** 2 + s2 ** 2 + c2))
    return {"mse": round(mse, 2), "ssim": round(float(ssim), 4), "similarity": round(float(ssim) * 100, 1)}


def get_histogram_data(image):
    r, g, b = image.convert("RGB").split()
    return {"red": list(r.histogram()), "green": list(g.histogram()), "blue": list(b.histogram())}


# ============================================
#  PDF GENERATOR
# ============================================
def _safe_pdf(text):
    if not text:
        return ""
    reps = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e', 'à': 'a', 'â': 'a', 'ä': 'a',
        'ù': 'u', 'û': 'u', 'ü': 'u', 'ô': 'o', 'ö': 'o', 'î': 'i', 'ï': 'i',
        'ç': 'c', 'É': 'E', 'È': 'E', 'Ê': 'E', 'À': 'A', 'Ù': 'U', 'Ô': 'O',
        'Î': 'I', 'Ç': 'C', '→': '->', '←': '<-', '°': 'o', 'µ': 'u', '×': 'x',
        '🔴': '[!]', '🟠': '[!]', '🟢': '[OK]', '🚨': '[!!!]'
    }
    for o, r in reps.items():
        text = text.replace(o, r)
    result = []
    for ch in text:
        try:
            ch.encode('latin-1')
            result.append(ch)
        except:
            result.append('?')
    return ''.join(result)


class ProPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(True, 30)

    def header(self):
        self.set_fill_color(0, 40, 100)
        self.rect(0, 0, 210, 3, 'F')
        self.set_fill_color(0, 200, 255)
        self.rect(0, 3, 210, 1, 'F')
        self.ln(6)
        self.set_font("Arial", "B", 12)
        self.set_text_color(0, 60, 150)
        self.cell(0, 8, f"DM SMART LAB AI v{APP_VERSION}", 0, 0, "L")
        self.set_font("Arial", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 1, "R")
        self.set_draw_color(0, 100, 200)
        self.line(10, 18, 200, 18)
        self.ln(6)

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 7)
        self.set_text_color(150, 150, 150)
        self.multi_cell(0, 4, _safe_pdf("AVERTISSEMENT: Ce rapport est genere par IA et doit etre valide par un professionnel de sante."))
        self.set_draw_color(200, 200, 200)
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(2)
        self.set_font("Arial", "", 7)
        self.cell(0, 4, f"DM Smart Lab AI v{APP_VERSION} | INFSPM Ouargla", 0, 0, "L")
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}}", 0, 0, "R")

    def section(self, title, color=(0, 60, 150)):
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)
        self.set_font("Arial", "B", 10)
        self.cell(0, 7, f"  {_safe_pdf(title)}", 0, 1, "L", True)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def field(self, label, value):
        self.set_font("Arial", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(50, 6, _safe_pdf(label), 0, 0)
        self.set_font("Arial", "", 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, _safe_pdf(str(value)), 0, 1)


def generate_pdf(patient, lab, result, info_name):
    pdf = ProPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 60, 150)
    pdf.cell(0, 12, "RAPPORT D'ANALYSE PARASITOLOGIQUE", 0, 1, "C")
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Analyse assistee par Intelligence Artificielle", 0, 1, "C")
    rid = hashlib.md5(f"{patient.get('Nom', '')}{datetime.now().isoformat()}".encode()).hexdigest()[:10].upper()
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(0, 100, 200)
    pdf.cell(0, 5, f"Ref: DM-{rid}", 0, 1, "R")
    pdf.ln(3)

    pdf.section("INFORMATIONS DU PATIENT")
    for k, v in patient.items():
        pdf.field(f"{k}:", v)
    pdf.field("Date:", datetime.now().strftime("%d/%m/%Y"))
    pdf.ln(2)

    pdf.section("INFORMATIONS DU LABORATOIRE", (0, 100, 80))
    for k, v in lab.items():
        if v:
            pdf.field(f"{k}:", v)
    pdf.ln(2)

    pdf.section("RESULTAT DE L'ANALYSE IA", (180, 0, 0))
    label = result.get("label", "Negative")
    conf = result.get("confidence", 0)
    pdf.ln(2)
    if label == "Negative":
        pdf.set_fill_color(220, 255, 220)
        pdf.set_text_color(0, 128, 0)
    else:
        pdf.set_fill_color(255, 220, 220)
        pdf.set_text_color(200, 0, 0)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, f"  RESULTAT: {_safe_pdf(label)}", 1, 1, "C", True)
    pdf.set_fill_color(240, 240, 255)
    pdf.set_text_color(0, 60, 150)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"  CONFIANCE: {conf}%", 1, 1, "C", True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    info = PARASITE_DB.get(info_name, PARASITE_DB["Negative"])
    morph = get_parasite_field(info_name, "morphology")
    desc = get_parasite_field(info_name, "description")
    adv = get_parasite_field(info_name, "advice")

    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, _safe_pdf(f"Morphologie: {morph}"))
    pdf.ln(1)
    pdf.multi_cell(0, 5, _safe_pdf(f"Description: {desc}"))
    pdf.ln(3)

    pdf.section("RECOMMANDATIONS CLINIQUES", (0, 130, 0))
    pdf.set_font("Arial", "", 9)
    pdf.multi_cell(0, 5, _safe_pdf(adv))
    pdf.ln(2)
    extra = info.get("extra_tests", [])
    if extra:
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Examens complementaires:", 0, 1)
        pdf.set_font("Arial", "", 9)
        for test in extra:
            pdf.cell(0, 5, _safe_pdf(f"  - {test}"), 0, 1)
    pdf.ln(3)

    if HAS_QRCODE:
        try:
            qr_text = f"DM-SmartLab|{label}|{conf}%|{rid}|{datetime.now().strftime('%Y%m%d')}"
            qr = qrcode.QRCode(box_size=3, border=1)
            qr.add_data(qr_text)
            qr.make(fit=True)
            qr_img = qr.make_image()
            qr_path = f"_qr_{rid}.png"
            qr_img.save(qr_path)
            pdf.image(qr_path, x=170, y=pdf.get_y(), w=28)
            try:
                os.remove(qr_path)
            except:
                pass
        except:
            pass

    pdf.ln(5)
    pdf.section("SIGNATURES ET VALIDATION", (80, 80, 80))
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    t1 = lab.get("Technicien 1", AUTHORS["dev1"]["name"])
    t2 = lab.get("Technicien 2", AUTHORS["dev2"]["name"])
    pdf.cell(95, 6, "Technicien Analyste:", 0, 0)
    pdf.cell(95, 6, "Technicien Validateur:", 0, 1)
    pdf.set_font("Arial", "", 9)
    pdf.cell(95, 6, _safe_pdf(t1), 0, 0)
    pdf.cell(95, 6, _safe_pdf(t2), 0, 1)
    pdf.ln(3)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(95, 5, "Signature: ___________________", 0, 0)
    pdf.cell(95, 5, "Signature: ___________________", 0, 1)

    return pdf.output(dest='S').encode('latin-1')


# ============================================
#  CSS THEME
# ============================================
def apply_theme():
    dm = st.session_state.get("dark_mode", True)
    lang = st.session_state.get("lang", "fr")
    is_rtl = (lang == "ar")
    direction = "rtl" if is_rtl else "ltr"

    if dm:
        bg = "linear-gradient(135deg, #030614 0%, #0a0e2a 30%, #0d1333 60%, #030614 100%)"
        card_bg = "rgba(10,15,46,0.85)"
        text = "#e0e8ff"
        primary = "#00f5ff"
        muted = "#6b7fa0"
        accent = "#ff00ff"
        accent2 = "#00ff88"
        sidebar_bg = "linear-gradient(180deg, #020410 0%, #0a0e2a 100%)"
        btn_grad = "linear-gradient(135deg,#00f5ff,#0066ff)"
        border_c = "rgba(0,245,255,0.15)"
        input_bg = "rgba(10,15,46,0.6)"
        input_text = "#e0e8ff"
        input_border = "rgba(0,245,255,0.3)"
        template = "plotly_dark"
    else:
        bg = "linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 50%, #f0f4f8 100%)"
        card_bg = "rgba(255,255,255,0.95)"
        text = "#1a202c"
        primary = "#0066ff"
        muted = "#64748b"
        accent = "#9933ff"
        accent2 = "#00cc66"
        sidebar_bg = "linear-gradient(180deg, #f8fafc 0%, #edf2f7 100%)"
        btn_grad = "linear-gradient(135deg,#0066ff,#0044cc)"
        border_c = "rgba(0,100,255,0.15)"
        input_bg = "rgba(255,255,255,0.9)"
        input_text = "#1a202c"
        input_border = "rgba(0,100,255,0.3)"
        template = "plotly_white"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap');

    html {{ direction: {direction}; }}

    .stApp {{
        background: {bg} !important;
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    /* Fix light mode text visibility */
    .stApp p, .stApp span, .stApp label, .stApp div {{
        color: {text} !important;
    }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
        color: {text} !important;
    }}

    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stNumberInput > div > div > input {{
        background: {input_bg} !important;
        color: {input_text} !important;
        border: 1px solid {input_border} !important;
        border-radius: 10px !important;
    }}

    .dm-card {{
        background: {card_bg}; backdrop-filter: blur(15px);
        border: 1px solid {border_c}; border-radius: 16px;
        padding: 24px; margin: 12px 0;
        transition: all 0.3s ease;
        color: {text} !important;
    }}
    .dm-card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 32px rgba(0,0,0,0.15); }}
    .dm-card * {{ color: {text} !important; }}
    .dm-card-cyan {{ border-left: 3px solid {primary}; }}
    .dm-card-green {{ border-left: 3px solid {accent2}; }}
    .dm-card-red {{ border-left: 3px solid #ff0040; }}
    .dm-card-orange {{ border-left: 3px solid #ff9500; }}

    .dm-metric {{
        background: {card_bg}; border: 1px solid {border_c};
        border-radius: 16px; padding: 18px 12px; text-align: center;
    }}
    .dm-metric-icon {{ font-size:1.5rem; }}
    .dm-metric-val {{
        font-size:1.7rem; font-weight:800;
        font-family:'JetBrains Mono',monospace !important;
        background: linear-gradient(135deg, {primary}, {accent});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .dm-metric-lbl {{
        font-size:0.68rem; font-weight:600; color:{muted} !important;
        -webkit-text-fill-color: {muted} !important;
        text-transform:uppercase; letter-spacing:0.08em; margin-top:4px;
    }}

    div.stButton > button {{
        background: {btn_grad} !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        padding: 10px 24px !important; font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(0,100,255,0.3) !important;
    }}
    div.stButton > button * {{ color: white !important; -webkit-text-fill-color: white !important; }}

    .dm-neon-title {{
        font-family: 'Orbitron', sans-serif; font-weight: 900;
        background: linear-gradient(135deg, {primary}, {accent}, {accent2});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    .dm-chat-msg {{ padding:12px 16px; border-radius:14px; margin:6px 0; max-width:85%; font-size:0.9rem; }}
    .dm-chat-user {{ background:{btn_grad}; color:white !important; margin-left:auto; }}
    .dm-chat-user * {{ color:white !important; -webkit-text-fill-color: white !important; }}
    .dm-chat-bot {{ background:{card_bg}; border:1px solid {border_c}; }}

    h1 {{ font-family: 'Orbitron', sans-serif !important; }}
    {"body, p, span, div, label { font-family: 'Tajawal', sans-serif !important; }" if is_rtl else ""}

    .dm-logo-container {{
        text-align: center; padding: 10px;
        background: {card_bg};
        border-radius: 20px;
        border: 1px solid {border_c};
        margin-bottom: 10px;
    }}

    /* Animated background particles for dark mode */
    {"" if not dm else '''
    .stApp::before {
        content: "";
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background:
            radial-gradient(2px 2px at 20% 30%, rgba(0,245,255,0.15), transparent),
            radial-gradient(2px 2px at 80% 70%, rgba(255,0,255,0.1), transparent),
            radial-gradient(2px 2px at 50% 50%, rgba(0,255,136,0.1), transparent),
            radial-gradient(1px 1px at 10% 90%, rgba(0,245,255,0.08), transparent),
            radial-gradient(1px 1px at 90% 10%, rgba(255,0,255,0.08), transparent);
        pointer-events: none;
        z-index: 0;
    }
    '''}
    </style>
    """, unsafe_allow_html=True)
    return template


plotly_template = apply_theme()


# ============================================
#  LOGO SVG
# ============================================
def render_logo():
    st.markdown("""
    <div class="dm-logo-container">
        <svg width="80" height="80" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#00f5ff;stop-opacity:1" />
                    <stop offset="50%" style="stop-color:#ff00ff;stop-opacity:1" />
                    <stop offset="100%" style="stop-color:#00ff88;stop-opacity:1" />
                </linearGradient>
                <filter id="glow">
                    <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                    <feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge>
                </filter>
            </defs>
            <circle cx="50" cy="50" r="45" fill="none" stroke="url(#grad1)" stroke-width="2.5" filter="url(#glow)" opacity="0.8"/>
            <circle cx="50" cy="50" r="38" fill="none" stroke="url(#grad1)" stroke-width="1" opacity="0.4"/>
            <!-- DNA Helix -->
            <path d="M35,25 C40,35 60,35 65,25" fill="none" stroke="#00f5ff" stroke-width="2" filter="url(#glow)"/>
            <path d="M35,35 C40,45 60,45 65,35" fill="none" stroke="#ff00ff" stroke-width="2" filter="url(#glow)"/>
            <path d="M35,45 C40,55 60,55 65,45" fill="none" stroke="#00ff88" stroke-width="2" filter="url(#glow)"/>
            <path d="M35,55 C40,65 60,65 65,55" fill="none" stroke="#00f5ff" stroke-width="2" filter="url(#glow)"/>
            <path d="M35,65 C40,75 60,75 65,65" fill="none" stroke="#ff00ff" stroke-width="2" filter="url(#glow)"/>
            <!-- Connecting lines -->
            <line x1="42" y1="30" x2="58" y2="30" stroke="#00f5ff" stroke-width="1.5" opacity="0.6"/>
            <line x1="42" y1="40" x2="58" y2="40" stroke="#ff00ff" stroke-width="1.5" opacity="0.6"/>
            <line x1="42" y1="50" x2="58" y2="50" stroke="#00ff88" stroke-width="1.5" opacity="0.6"/>
            <line x1="42" y1="60" x2="58" y2="60" stroke="#00f5ff" stroke-width="1.5" opacity="0.6"/>
            <line x1="42" y1="70" x2="58" y2="70" stroke="#ff00ff" stroke-width="1.5" opacity="0.6"/>
            <!-- Microscope icon small -->
            <circle cx="50" cy="88" r="5" fill="url(#grad1)" opacity="0.3"/>
            <text x="50" y="91" text-anchor="middle" fill="white" font-size="7">🔬</text>
        </svg>
        <h3 style="font-family:Orbitron,sans-serif;margin:4px 0;background:linear-gradient(135deg,#00f5ff,#ff00ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">DM SMART LAB AI</h3>
        <p style="font-size:0.55rem;opacity:0.4;letter-spacing:0.3em;text-transform:uppercase;margin:0;">v7.0 Professional Edition</p>
    </div>
    """, unsafe_allow_html=True)


# Render logo in sidebar
with st.sidebar:
    render_logo()

# ============================================
#  LOGIN SCREEN
# ============================================
if not st.session_state.logged_in:
    # Language selector on login page
    lang_col1, lang_col2, lang_col3 = st.columns([1, 2, 1])
    with lang_col2:
        login_lang = st.selectbox("🌍", ["🇫🇷 Français", "🇩🇿 العربية", "🇬🇧 English"], label_visibility="collapsed")
        if "Français" in login_lang:
            st.session_state.lang = "fr"
        elif "العربية" in login_lang:
            st.session_state.lang = "ar"
        else:
            st.session_state.lang = "en"

    col_a, col_b, col_c = st.columns([1.2, 2, 1.2])
    with col_b:
        render_logo()
        st.markdown(f"""
        <div class='dm-card dm-card-cyan' style='text-align:center;'>
            <div style='font-size:3rem;'>🔐</div>
            <h2 class='dm-neon-title'>{t('login')}</h2>
            <p style='opacity:0.5;'>Professional Authentication System</p>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            user_input = st.text_input(f"👤 {t('username')}", placeholder="admin / dhia / demo")
            pwd_input = st.text_input(f"🔒 {t('password')}", type="password")
            login_btn = st.form_submit_button(f"🚀 {t('connect')}", use_container_width=True)

            if login_btn and user_input.strip():
                result = db_verify_user(user_input.strip(), pwd_input)
                if result is None:
                    st.error("❌ User not found / Utilisateur introuvable")
                elif isinstance(result, dict) and "error" in result:
                    if result["error"] == "locked":
                        st.error("🔒 Account locked / Compte verrouillé")
                    else:
                        left = result.get("attempts_left", 0)
                        st.error(f"❌ Wrong password. {left} attempt(s) left")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_id = result["id"]
                    st.session_state.user_name = result["username"]
                    st.session_state.user_role = result["role"]
                    st.session_state.user_full_name = result["full_name"]
                    db_log_activity(result["id"], result["username"], "Login", f"Role: {result['role']}")
                    st.rerun()

        st.markdown("""
        <div style='text-align:center;opacity:0.4;font-size:0.75rem;margin-top:12px;'>
            <p>👑 admin/admin2026 | 🔬 dhia/dhia2026 | 👁️ demo/demo123</p>
        </div>""", unsafe_allow_html=True)

    st.stop()

# ============================================
#  SIDEBAR (Post-Login)
# ============================================
with st.sidebar:
    role_info = ROLES.get(st.session_state.user_role, ROLES["viewer"])
    st.markdown(f"{role_info['icon']} **{st.session_state.user_full_name}**")
    st.caption(f"@{st.session_state.user_name} - {get_role_label()}")

    lang = st.session_state.get("lang", "fr")
    tips = DAILY_TIPS.get(lang, DAILY_TIPS["fr"])
    tip_idx = datetime.now().timetuple().tm_yday % len(tips)
    st.info(f"**{t('daily_tip')}:**\n\n{tips[tip_idx]}")

    st.markdown("---")

    # Language selector
    st.markdown(f"#### 🌍 {t('language')}")
    lang_choice = st.radio("", ["🇫🇷 Français", "🇩🇿 العربية", "🇬🇧 English"], label_visibility="collapsed",
                           index=["fr", "ar", "en"].index(st.session_state.lang))
    new_lang = "fr" if "Français" in lang_choice else ("ar" if "العربية" in lang_choice else "en")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    st.markdown("---")

    nav_items = [
        f"🏠 {t('home')}",
        f"🔬 {t('scan')}",
        f"📘 {t('encyclopedia')}",
        f"📊 {t('dashboard')}",
        f"🧠 {t('quiz')}",
        f"💬 {t('chatbot')}",
        f"🔄 {t('compare')}",
    ]
    page_keys = ["home", "scan", "encyclopedia", "dashboard", "quiz", "chatbot", "compare"]

    if user_has_role(3):
        nav_items.append(f"⚙️ {t('admin')}")
        page_keys.append("admin")

    nav_items.append(f"ℹ️ {t('about')}")
    page_keys.append("about")

    menu = st.radio("Navigation", nav_items, label_visibility="collapsed")

    st.markdown("---")
    dark = st.toggle(f"🌙 {t('dark_mode')}", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")
    if st.button(f"🚪 {t('logout')}", use_container_width=True):
        db_log_activity(st.session_state.user_id, st.session_state.user_name, "Logout")
        for k in list(DEFAULTS.keys()):
            st.session_state[k] = DEFAULTS[k]
        st.rerun()

page_map = dict(zip(nav_items, page_keys))
current_page = page_map.get(menu, "home")


# ╔══════════════════════════════════════════╗
# ║            PAGE: HOME                     ║
# ╚══════════════════════════════════════════╝
if current_page == "home":
    st.title(f"👋 {get_greeting()}, {st.session_state.user_full_name} !")

    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <h3 class='dm-neon-title'>DM SMART LAB AI — {
        {"fr": "Où la Science Rencontre l'Intelligence", "ar": "حيث يلتقي العلم بالذكاء", "en": "Where Science Meets Intelligence"}.get(st.session_state.lang, "")
    }</h3>
    <p style='opacity:0.6;'>{
        {"fr": "Système de diagnostic parasitologique par intelligence artificielle", "ar": "نظام تشخيص طفيلي بالذكاء الاصطناعي", "en": "Parasitological diagnosis system powered by AI"}.get(st.session_state.lang, "")
    }</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Welcome message (optional voice)
    st.markdown(f"### 🎙️ {t('welcome_btn')}")
    wc1, wc2, wc3 = st.columns([2, 2, 1])
    with wc1:
        if st.button(t("welcome_btn"), use_container_width=True, type="primary"):
            speak_js(t("voice_welcome"), st.session_state.lang)
            st.success("✅ 🔊")
    with wc2:
        if st.button(t("intro_btn"), use_container_width=True, type="primary"):
            speak_js(t("voice_intro"), st.session_state.lang)
            st.success("✅ 🔊")
    with wc3:
        if st.button("🔇 Stop", use_container_width=True):
            stop_speech_js()

# Quick stats
st.markdown("---")

st.markdown(
    f"### 📊 { {'fr': 'Aperçu Rapide', 'ar': 'نظرة سريعة', 'en': 'Quick Overview'}.get(st.session_state.lang, 'Aperçu Rapide') }"
)

stats = db_get_stats(st.session_state.user_id)

kc = st.columns(4)

metrics = [
    ("🔬", stats["total"], t("total_analyses")),
    ("✅", stats["reliable"], t("reliable")),
    ("⚠️", stats["to_verify"], t("to_verify")),
    ("🦠", stats["most_frequent"], t("most_frequent")),
]

for col, (ic, val, lbl) in zip(kc, metrics):
    with col:
        st.markdown(f"""<div class="dm-metric">
        <span class="dm-metric-icon">{ic}</span>
        <div class="dm-metric-val">{val}</div>
        <div class="dm-metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════╗
# ║            PAGE: SCAN & ANALYSE           ║
# ╚══════════════════════════════════════════╝
elif current_page == "scan":
    st.title(f"🔬 {t('scan')}")

    model, model_name, model_type = load_ai_model()
    if model_name:
        st.sidebar.success(f"🧠 Model: {model_name}")
    else:
        st.sidebar.info(f"🧠 {t('demo_mode')}")

    # Patient Info
    st.markdown(f"### 📋 1. {t('patient_name')}")
    ca, cb = st.columns(2)
    p_nom = ca.text_input(f"{t('patient_name')} *", placeholder="Benali")
    p_prenom = cb.text_input(t("patient_firstname"), placeholder="Ahmed")
    cc, cd, ce, cf = st.columns(4)
    p_age = cc.number_input(t("age"), 0, 120, 30)
    p_sexe = cd.selectbox(t("sex"), [t("male"), t("female")])
    p_poids = ce.number_input(t("weight"), 0, 300, 70)
    lang_samples = SAMPLES.get(st.session_state.lang, SAMPLES["fr"])
    p_type = cf.selectbox(t("sample_type"), lang_samples)

    # Lab Info
    st.markdown(f"### 🔬 2. {t('microscope')}")
    la, lb, lc = st.columns(3)
    l_tech1 = la.text_input(f"{t('technician')} 1", value=st.session_state.user_full_name)
    l_tech2 = lb.text_input(f"{t('technician')} 2", placeholder="")
    l_micro = lc.selectbox(t("microscope"), MICROSCOPE_TYPES)
    ld, le = st.columns(2)
    l_mag = ld.selectbox(t("magnification"), MAGNIFICATIONS, index=3)
    l_prep = le.selectbox(t("preparation"), PREPARATION_TYPES)
    l_notes = st.text_area(t("notes"), placeholder="...", height=80)

    # Image capture
    st.markdown("---")
    st.markdown(f"### 📸 3. {t('take_photo')}")

    img_source = st.radio("", [t("take_photo"), t("or_upload")], horizontal=True, label_visibility="collapsed")

    image = None
    img_hash = None

    if t("take_photo") in img_source:
        st.info(f"📷 {t('camera_instruction')}")
        camera_photo = st.camera_input(t("take_photo"))
        if camera_photo:
            image = Image.open(camera_photo).convert("RGB")
            img_hash = hashlib.md5(camera_photo.getvalue()).hexdigest()
    else:
        img_file = st.file_uploader(t("upload_image"), type=["jpg", "jpeg", "png", "bmp", "tiff"])
        if img_file:
            image = Image.open(img_file).convert("RGB")
            img_hash = hashlib.md5(img_file.getvalue()).hexdigest()

    if image is not None:
        if not p_nom.strip():
            st.error(f"⚠️ {t('name_required')}")
            st.stop()

        if st.session_state.get("_last_img_hash") != img_hash:
            st.session_state._last_img_hash = img_hash
            st.session_state.demo_seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = random.randint(0, 999999)

        col_img, col_res = st.columns(2)

        with col_img:
            with st.expander("🎛️ Zoom & Réglages", expanded=False):
                ac1, ac2, ac3 = st.columns(3)
                zoom_lvl = ac1.slider("Zoom", 1.0, 5.0, 1.0, 0.25)
                brightness = ac2.slider("Luminosité", 0.5, 2.0, 1.0, 0.1)
                contrast_adj = ac3.slider("Contraste", 0.5, 2.0, 1.0, 0.1)
                saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
                adjusted = apply_adjustments(image, brightness, contrast_adj, saturation)
                if zoom_lvl > 1.0:
                    adjusted = zoom_image(adjusted, zoom_lvl)

            tab_orig, tab_therm, tab_edge, tab_enh, tab_neg, tab_emb, tab_heat, tab_hist = st.tabs([
                "📷 Original", "🔥 Thermal", "📐 Edges",
                "✨ Contrast+", "🔄 Negative",
                "🏔️ Relief", "🎯 Heatmap", "📊 Histogram"
            ])
            with tab_orig:
                st.image(adjusted, caption="Original" + (f" (x{zoom_lvl})" if zoom_lvl > 1 else ""), use_container_width=True)
            with tab_therm:
                st.image(apply_thermal(adjusted), caption="Thermal", use_container_width=True)
            with tab_edge:
                st.image(apply_edge_detection(adjusted), caption="Edge Detection", use_container_width=True)
            with tab_enh:
                st.image(apply_enhanced_contrast(adjusted), caption="Enhanced Contrast", use_container_width=True)
            with tab_neg:
                st.image(apply_negative_filter(adjusted), caption="Negative", use_container_width=True)
            with tab_emb:
                st.image(apply_emboss(adjusted), caption="Emboss", use_container_width=True)
            with tab_heat:
                hm = generate_heatmap(image, st.session_state.heatmap_seed)
                st.image(hm, caption="AI Region of Interest (Grad-CAM)", use_container_width=True)
            with tab_hist:
                hist_data = get_histogram_data(adjusted)
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=hist_data["red"], name="Red", line=dict(color="red", width=1)))
                    fig.add_trace(go.Scatter(y=hist_data["green"], name="Green", line=dict(color="green", width=1)))
                    fig.add_trace(go.Scatter(y=hist_data["blue"], name="Blue", line=dict(color="blue", width=1)))
                    fig.update_layout(title="Histogram", height=300, template=plotly_template, margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(pd.DataFrame(hist_data))

        with col_res:
            st.markdown(f"### 🧠 {t('result')}")
            with st.spinner("⏳ AI Analysis..."):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.005)
                    prog.progress(i + 1)
                result = predict_image(model, model_type, image, st.session_state.demo_seed)

            label = result["label"]
            conf = result["confidence"]
            rc = risk_color(result["risk_level"])

            morph = get_parasite_field(label, "morphology")
            desc = get_parasite_field(label, "description")
            adv = get_parasite_field(label, "advice")
            fun = get_parasite_field(label, "funny")
            risk_disp = get_parasite_field(label, "risk_display")
            sci_name = PARASITE_DB[label]["scientific_name"]

            if not result["is_reliable"]:
                st.warning(f"⚠️ {t('low_confidence')} ({conf}%)")
            if result["is_demo"]:
                st.info(f"ℹ️ {t('demo_mode')}")

            st.markdown(f"""
            <div class='dm-card' style='border-left:4px solid {rc};'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
                    <div>
                        <h2 style='color:{rc} !important;-webkit-text-fill-color:{rc} !important;margin:0;font-family:Orbitron,sans-serif;'>{label}</h2>
                        <p style='opacity:0.4;font-style:italic;'>{sci_name}</p>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:2.5rem;font-weight:900;font-family:JetBrains Mono,monospace;color:{rc} !important;-webkit-text-fill-color:{rc} !important;'>{conf}%</div>
                        <div style='font-size:0.7rem;opacity:0.4;text-transform:uppercase;'>{t("confidence")}</div>
                    </div>
                </div>
                <hr style='opacity:0.1;margin:14px 0;'>
                <p><b>🔬 {t("morphology")}:</b><br>{morph}</p>
                <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc} !important;-webkit-text-fill-color:{rc} !important;font-weight:700;'>{risk_disp}</span></p>
                <div style='background:rgba(0,255,136,0.06);padding:12px;border-radius:10px;margin:10px 0;'>
                    <b>💡 {t("advice")}:</b><br>{adv}
                </div>
                <div style='background:rgba(0,100,255,0.06);padding:12px;border-radius:10px;font-style:italic;'>
                    🤖 {fun}
                </div>
            </div>""", unsafe_allow_html=True)

            # Optional voice
            vc1, vc2 = st.columns(2)
            with vc1:
                if st.button("🔊 Listen", use_container_width=True):
                    speak_js(f"{t('result')}: {label}. {fun}", st.session_state.lang)
            with vc2:
                if st.button("🔇 Stop", key="stop_result", use_container_width=True):
                    stop_speech_js()

            info = PARASITE_DB.get(label, PARASITE_DB["Negative"])

            if info.get("extra_tests"):
                with st.expander(f"🩺 {t('extra_tests')}"):
                    for test in info["extra_tests"]:
                        st.markdown(f"• {test}")

            diag_keys = get_parasite_field(label, "diagnostic_keys")
            if diag_keys and diag_keys not in ["N/A", "غير متوفر"]:
                with st.expander(f"🔑 {t('diagnostic_keys')}"):
                    st.markdown(diag_keys)

            lifecycle = get_parasite_field(label, "lifecycle")
            if lifecycle and lifecycle not in ["N/A", "غير متوفر"]:
                with st.expander(f"🔄 {t('lifecycle')}"):
                    st.markdown(f"**{lifecycle}**")

            if result["all_predictions"]:
                with st.expander("📊 All Probabilities"):
                    if HAS_PLOTLY:
                        sorted_preds = dict(sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True))
                        fig = px.bar(x=list(sorted_preds.values()), y=list(sorted_preds.keys()),
                                     orientation='h', color=list(sorted_preds.values()),
                                     color_continuous_scale='RdYlGn_r',
                                     labels={"x": "Probability (%)", "y": "Parasite"})
                        fig.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=20),
                                          template=plotly_template, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        for cls, prob in sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True):
                            st.progress(min(prob / 100, 1.0), text=f"{cls}: {prob}%")

        # Actions
        st.markdown("---")
        a1, a2, a3 = st.columns(3)

        with a1:
            pat_data = {"Nom": p_nom, "Prenom": p_prenom, "Age": str(p_age),
                        "Sexe": p_sexe, "Poids": str(p_poids), "Echantillon": p_type}
            lab_data = {"Microscope": l_micro, "Grossissement": l_mag,
                        "Preparation": l_prep, "Technicien 1": l_tech1,
                        "Technicien 2": l_tech2, "Notes": l_notes}
            try:
                pdf = generate_pdf(pat_data, lab_data, result, label)
                st.download_button(f"📥 {t('download_pdf')}", pdf,
                                   f"Rapport_{p_nom}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                   "application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"PDF Error: {e}")

        with a2:
            if user_has_role(2):
                if st.button(f"💾 {t('save_db')}", use_container_width=True):
                    analysis_data = {
                        "patient_name": p_nom, "patient_firstname": p_prenom,
                        "patient_age": p_age, "patient_sex": p_sexe,
                        "patient_weight": p_poids, "sample_type": p_type,
                        "microscope_type": l_micro, "magnification": l_mag,
                        "preparation_type": l_prep, "technician1": l_tech1,
                        "technician2": l_tech2, "notes": l_notes,
                        "parasite_detected": label, "confidence": conf,
                        "risk_level": result["risk_level"],
                        "is_reliable": 1 if result["is_reliable"] else 0,
                        "all_predictions": result["all_predictions"],
                        "image_hash": img_hash, "is_demo": 1 if result["is_demo"] else 0
                    }
                    aid = db_save_analysis(st.session_state.user_id, analysis_data)
                    db_log_activity(st.session_state.user_id, st.session_state.user_name,
                                    "Analysis saved", f"ID:{aid} Patient:{p_nom} Result:{label}")
                    st.success(f"✅ {t('saved_success')} (ID: {aid})")

        with a3:
            if st.button(f"🔄 {t('new_analysis')}", use_container_width=True):
                st.session_state.demo_seed = None
                st.session_state.heatmap_seed = None
                st.session_state._last_img_hash = None
                st.rerun()


# ╔══════════════════════════════════════════╗
# ║          PAGE: ENCYCLOPEDIA               ║
# ╚══════════════════════════════════════════╝
elif current_page == "encyclopedia":
    st.title(f"📘 {t('encyclopedia')}")
    search = st.text_input(f"🔍 {t('search')}", placeholder="amoeba, giardia...")
    st.markdown("---")

    found = False
    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if search.strip() and search.lower() not in (name + " " + data["scientific_name"]).lower():
            continue
        found = True
        rc = risk_color(data["risk_level"])
        risk_disp = get_parasite_field(name, "risk_display")
        morph = get_parasite_field(name, "morphology")
        desc = get_parasite_field(name, "description")
        adv = get_parasite_field(name, "advice")
        fun = get_parasite_field(name, "funny")

        with st.expander(f"{data['icon']} {name} — *{data['scientific_name']}* | {risk_disp}", expanded=not search.strip()):
            ci, cv = st.columns([2.5, 1])
            with ci:
                st.markdown(f"""<div class='dm-card' style='border-left:3px solid {rc};'>
                <h4 style='color:{rc} !important;-webkit-text-fill-color:{rc} !important;font-family:Orbitron,sans-serif;'>{data['scientific_name']}</h4>
                <p><b>🔬 {t("morphology")}:</b><br>{morph}</p>
                <p><b>📖 {t("description")}:</b><br>{desc}</p>
                <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc} !important;-webkit-text-fill-color:{rc} !important;font-weight:700;'>{risk_disp}</span></p>
                <div style='background:rgba(0,255,136,0.06);padding:12px;border-radius:10px;margin:8px 0;'>
                    <b>💡 {t("advice")}:</b><br>{adv}
                </div>
                <div style='background:rgba(0,100,255,0.06);padding:12px;border-radius:10px;font-style:italic;'>
                    🤖 {fun}
                </div>
                </div>""", unsafe_allow_html=True)

                lifecycle = get_parasite_field(name, "lifecycle")
                diag_keys = get_parasite_field(name, "diagnostic_keys")
                if lifecycle and lifecycle not in ["N/A", "غير متوفر"]:
                    st.markdown(f"**🔄 {t('lifecycle')}:** {lifecycle}")
                if diag_keys:
                    st.markdown(f"**🔑 {t('diagnostic_keys')}:**\n{diag_keys}")
                if data.get("extra_tests"):
                    st.markdown(f"**🩺 {t('extra_tests')}:** {', '.join(data['extra_tests'])}")

            with cv:
                rp = risk_percent(data["risk_level"])
                if rp > 0:
                    st.progress(rp / 100, text=f"{rp}%")
                st.markdown(f'<div style="text-align:center;font-size:4rem;">{data["icon"]}</div>', unsafe_allow_html=True)
                if st.button(f"🔊 Listen", key=f"enc_voice_{name}"):
                    speak_js(f"{name}. {desc}", st.session_state.lang)

    if search.strip() and not found:
        st.warning(f"🔍 {t('no_data')}")


# ╔══════════════════════════════════════════╗
# ║          PAGE: DASHBOARD                  ║
# ╚══════════════════════════════════════════╝
elif current_page == "dashboard":
    st.title(f"📊 {t('dashboard')}")

    if user_has_role(3):
        stats = db_get_stats()
        analyses = db_get_analyses()
    else:
        stats = db_get_stats(st.session_state.user_id)
        analyses = db_get_analyses(st.session_state.user_id)

    total = stats["total"]
    kc = st.columns(5)
    metric_data = [
        ("🔬", stats["total"], t("total_analyses")),
        ("✅", stats["reliable"], t("reliable")),
        ("⚠️", stats["to_verify"], t("to_verify")),
        ("🦠", stats["most_frequent"], t("most_frequent")),
        ("📈", f"{stats['avg_confidence']}%", t("avg_confidence")),
    ]
    for col, (ic, val, lbl) in zip(kc, metric_data):
        with col:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">{ic}</span>
            <div class="dm-metric-val">{val}</div>
            <div class="dm-metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    if total > 0:
        df = pd.DataFrame(analyses)
        st.markdown("---")
        cc1, cc2 = st.columns(2)
        with cc1:
            if HAS_PLOTLY and "parasite_detected" in df.columns:
                para_counts = df["parasite_detected"].value_counts()
                fig = px.pie(values=para_counts.values, names=para_counts.index, hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=350, template=plotly_template, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
        with cc2:
            if HAS_PLOTLY and "confidence" in df.columns:
                fig = px.histogram(df, x="confidence", nbins=20, color_discrete_sequence=[NEON["cyan"]])
                fig.update_layout(height=350, template=plotly_template, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        trends = db_get_trends(30)
        if trends and HAS_PLOTLY:
            tdf = pd.DataFrame(trends)
            fig = px.line(tdf, x="day", y="count", color="parasite_detected", markers=True)
            fig.update_layout(height=300, template=plotly_template, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        display_cols = [c for c in ["id", "analysis_date", "patient_name", "parasite_detected", "confidence",
                                     "risk_level", "is_reliable", "analyst_name", "validated"] if c in df.columns]
        st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)

        if user_has_role(2) and "validated" in df.columns:
            unvalidated = df[df["validated"] == 0]
            if not unvalidated.empty:
                val_id = st.selectbox("ID:", unvalidated["id"].tolist())
                if st.button(f"✅ Validate #{val_id}"):
                    db_validate_analysis(val_id, st.session_state.user_full_name)
                    st.success(f"✅ #{val_id}")
                    st.rerun()

        st.markdown("---")
        ex1, ex2 = st.columns(2)
        with ex1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("⬇️ CSV", csv, "analyses.csv", "text/csv", use_container_width=True)
        with ex2:
            jd = df.to_json(orient='records', force_ascii=False).encode('utf-8')
            st.download_button("⬇️ JSON", jd, "analyses.json", "application/json", use_container_width=True)
    else:
        st.markdown(f"""<div class='dm-card' style='text-align:center;padding:50px;'>
        <div style='font-size:4rem;'>📊</div><h3>{t('no_data')}</h3></div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║            PAGE: QUIZ                     ║
# ╚══════════════════════════════════════════╝
elif current_page == "quiz":
    st.title(f"🧠 {t('quiz')}")

    questions = QUIZ_QUESTIONS
    qs = st.session_state.quiz_state

    with st.expander(f"🏆 {t('leaderboard')}"):
        lb = db_get_leaderboard()
        if lb:
            for i, entry in enumerate(lb[:10]):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i + 1}"
                st.markdown(f"{medal} **{entry['username']}** — {entry['score']}/{entry['total_questions']} ({entry['percentage']:.0f}%)")
        else:
            st.info(t("no_data"))

    if not qs["active"]:
        if st.button(f"🎮 {t('start_quiz')}", use_container_width=True, type="primary"):
            shuffled = list(range(len(questions)))
            random.shuffle(shuffled)
            st.session_state.quiz_state = {
                "current": 0, "score": 0, "answered": [],
                "active": True, "order": shuffled[:min(15, len(questions))]
            }
            st.rerun()
    else:
        idx = qs["current"]
        order = qs.get("order", list(range(len(questions))))

        if idx < len(order):
            q_idx = order[idx]
            q = questions[q_idx]
            total_q = len(order)

            st.markdown(f"### Question {idx + 1}/{total_q}")
            st.progress(idx / total_q)

            cat = q.get("category", "")
            if cat:
                st.caption(f"📂 {cat}")

            q_text = get_quiz_text(q, "q")
            st.markdown(f"<div class='dm-card'><h4>{q_text}</h4></div>", unsafe_allow_html=True)

            answer_key = f"quiz_ans_{idx}"
            if answer_key not in st.session_state:
                for i, opt in enumerate(q["options"]):
                    if st.button(opt, key=f"qz_{idx}_{i}", use_container_width=True):
                        is_correct = (i == q["answer"])
                        if is_correct:
                            st.session_state.quiz_state["score"] += 1
                        st.session_state.quiz_state["answered"].append(is_correct)
                        st.session_state[answer_key] = {"correct": is_correct, "selected": i}
                        st.rerun()
            else:
                ad = st.session_state[answer_key]
                expl = get_quiz_text(q, "explanation")
                if ad["correct"]:
                    st.success("✅ !")
                else:
                    st.error(f"❌ → {q['options'][q['answer']]}")
                st.info(f"📖 {expl}")

                if st.button(f"➡️ {t('next_question')}", use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1
                    st.rerun()
        else:
            score = qs["score"]
            total_q = len(order)
            pct = int(score / total_q * 100) if total_q > 0 else 0

            if pct >= 80:
                emoji, msg = "🏆", "Excellent!"
            elif pct >= 60:
                emoji, msg = "👍", "Good!"
            elif pct >= 40:
                emoji, msg = "📚", "Keep going!"
            else:
                emoji, msg = "💪", "Study more!"

            st.markdown(f"""<div class='dm-card dm-card-green' style='text-align:center;'>
            <div style='font-size:4rem;'>{emoji}</div>
            <h2>{t('result')}</h2>
            <div class='dm-neon-title' style='font-size:3rem;'>{score}/{total_q}</div>
            <p style='font-size:1.2rem;'>{pct}% — {msg}</p>
            </div>""", unsafe_allow_html=True)

            db_save_quiz_score(st.session_state.user_id, st.session_state.user_name, score, total_q, pct)

            if st.button(f"🔄 {t('restart')}", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("quiz_ans_"):
                        del st.session_state[key]
                st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": False}
                st.rerun()


# ╔══════════════════════════════════════════╗
# ║            PAGE: CHATBOT (DM Bot)         ║
# ╚══════════════════════════════════════════╝
elif current_page == "chatbot":
    st.title(f"💬 DM Bot - {{'fr': 'Assistant Médical IA', 'ar': 'المساعد الطبي الذكي', 'en': 'AI Medical Assistant'}.get(st.session_state.lang, 'AI Assistant')}")

    if not st.session_state.chat_history:
        welcome = {
            "fr": "👋 Bonjour! Je suis **DM Bot** 🤖 votre assistant parasitologique intelligent.\n\n💡 Essayez: amoeba, giardia, plasmodium, microscope, coloration, toxoplasma, ascaris, taenia, oxyure, cryptosporidium, aide",
            "ar": "👋 مرحباً! أنا **DM Bot** 🤖 مساعدك الذكي في علم الطفيليات.\n\n💡 جرب: amoeba, giardia, plasmodium, مساعدة",
            "en": "👋 Hello! I'm **DM Bot** 🤖 your intelligent parasitology assistant.\n\n💡 Try: amoeba, giardia, plasmodium, microscope, help"
        }
        st.session_state.chat_history.append({
            "role": "bot",
            "msg": welcome.get(st.session_state.lang, welcome["fr"])
        })

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='dm-chat-msg dm-chat-user'>👤 {msg['msg']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='dm-chat-msg dm-chat-bot'>🤖 {msg['msg']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input({"fr": "Posez votre question...", "ar": "اطرح سؤالك...", "en": "Ask your question..."}.get(st.session_state.lang, "..."))
    if user_input:
        st.session_state.chat_history.append({"role": "user", "msg": user_input})
        reply = chatbot_reply(user_input)
        st.session_state.chat_history.append({"role": "bot", "msg": reply})
        db_log_activity(st.session_state.user_id, st.session_state.user_name, "Chat", user_input[:80])
        st.rerun()

    st.markdown("---")
    qc = st.columns(7)
    quick_q = ["Amoeba?", "Giardia?", "Plasmodium?", "Leishmania?", "Microscope?", "Coloration?",
               {"fr": "Aide", "ar": "مساعدة", "en": "Help"}.get(st.session_state.lang, "Aide")]
    for col, q in zip(qc, quick_q):
        with col:
            if st.button(q, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(q)})
                st.rerun()

    if st.button("🗑️ Clear", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ╔══════════════════════════════════════════╗
# ║        PAGE: IMAGE COMPARISON             ║
# ╚══════════════════════════════════════════╝
elif current_page == "compare":
    st.title(f"🔄 {t('compare')}")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"### 📷 {t('image1')}")
        img1_file = st.file_uploader(t("image1"), type=["jpg", "jpeg", "png"], key="cmp1")
    with c2:
        st.markdown(f"### 📷 {t('image2')}")
        img2_file = st.file_uploader(t("image2"), type=["jpg", "jpeg", "png"], key="cmp2")

    if img1_file and img2_file:
        img1 = Image.open(img1_file).convert("RGB")
        img2 = Image.open(img2_file).convert("RGB")
        c1, c2 = st.columns(2)
        with c1:
            st.image(img1, caption=t("image1"), use_container_width=True)
        with c2:
            st.image(img2, caption=t("image2"), use_container_width=True)

        if st.button(f"🔍 {t('compare_btn')}", use_container_width=True, type="primary"):
            metrics = compare_images(img1, img2)
            mc = st.columns(3)
            with mc[0]:
                st.markdown(f"""<div class='dm-metric'><span class='dm-metric-icon'>📊</span>
                <div class='dm-metric-val'>{metrics['similarity']}%</div>
                <div class='dm-metric-lbl'>{t('similarity')}</div></div>""", unsafe_allow_html=True)
            with mc[1]:
                st.markdown(f"""<div class='dm-metric'><span class='dm-metric-icon'>🎯</span>
                <div class='dm-metric-val'>{metrics['ssim']}</div>
                <div class='dm-metric-lbl'>SSIM</div></div>""", unsafe_allow_html=True)
            with mc[2]:
                st.markdown(f"""<div class='dm-metric'><span class='dm-metric-icon'>📐</span>
                <div class='dm-metric-val'>{metrics['mse']}</div>
                <div class='dm-metric-lbl'>MSE</div></div>""", unsafe_allow_html=True)

            filters = [("Thermal", apply_thermal), ("Edges", apply_edge_detection), ("Enhanced", apply_enhanced_contrast)]
            for fname, ffunc in filters:
                fc1, fc2 = st.columns(2)
                with fc1:
                    st.image(ffunc(img1), caption=f"{t('image1')} - {fname}", use_container_width=True)
                with fc2:
                    st.image(ffunc(img2), caption=f"{t('image2')} - {fname}", use_container_width=True)


# ╔══════════════════════════════════════════╗
# ║        PAGE: ADMINISTRATION               ║
# ╚══════════════════════════════════════════╝
elif current_page == "admin":
    st.title(f"⚙️ {t('admin')}")

    if not user_has_role(3):
        st.error("🔒 Admin only")
        st.stop()

    tab_users, tab_log, tab_system = st.tabs([f"👥 {t('users_management')}", f"📜 {t('activity_log')}", f"🖥️ {t('system_info')}"])

    with tab_users:
        users = db_get_all_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
            tc1, tc2 = st.columns(2)
            u_id = tc1.number_input("User ID", min_value=1, step=1)
            u_active = tc2.selectbox("Status", ["Active", "Disabled"])
            if st.button("Apply"):
                db_toggle_user(u_id, u_active == "Active")
                st.success(f"✅ #{u_id} → {u_active}")
                st.rerun()

        st.markdown("---")
        st.markdown(f"### ➕ {t('create_user')}")
        with st.form("create_user_form"):
            nu = st.text_input(f"{t('username')} *")
            np_ = st.text_input(f"{t('password')} *", type="password")
            nf = st.text_input("Full Name *")
            nr = st.selectbox("Role", list(ROLES.keys()))
            ns = st.text_input("Speciality", "Laboratoire")
            if st.form_submit_button(t("create_user"), use_container_width=True):
                if nu and np_ and nf:
                    res = db_create_user(nu, np_, nf, nr, ns)
                    if "success" in res:
                        st.success(f"✅ '{nu}' created!")
                        st.rerun()
                    else:
                        st.error(f"❌ {res.get('error', 'Error')}")

        st.markdown("---")
        cp_id = st.number_input("User ID", min_value=1, step=1, key="cp_id")
        cp_new = st.text_input("New Password", type="password", key="cp_new")
        if st.button("Change Password"):
            if cp_new:
                db_change_password(cp_id, cp_new)
                st.success(f"✅ Password changed for #{cp_id}")

    with tab_log:
        logs = db_get_activity_log(300)
        if logs:
            ldf = pd.DataFrame(logs)
            if "username" in ldf.columns:
                filt = st.selectbox("Filter:", ["All"] + ldf["username"].dropna().unique().tolist())
                if filt != "All":
                    ldf = ldf[ldf["username"] == filt]
            st.dataframe(ldf, use_container_width=True)

    with tab_system:
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""<div class='dm-card dm-card-green'>
            <h4>🟢 System OK</h4>
            <p>Version: {APP_VERSION}</p>
            <p>Bcrypt: {'✅' if HAS_BCRYPT else '❌'}</p>
            <p>Plotly: {'✅' if HAS_PLOTLY else '❌'}</p>
            <p>QR Code: {'✅' if HAS_QRCODE else '❌'}</p>
            </div>""", unsafe_allow_html=True)
        with sc2:
            st.markdown(f"""<div class='dm-card dm-card-cyan'>
            <h4>📊 Stats</h4>
            <p>Users: {len(db_get_all_users())}</p>
            <p>Analyses: {db_get_stats()['total']}</p>
            </div>""", unsafe_allow_html=True)
        with sc3:
            db_size = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
            st.markdown(f"""<div class='dm-card'>
            <h4>💾 Storage</h4>
            <p>DB: {db_size:.1f} KB</p>
            </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║            PAGE: ABOUT                    ║
# ╚══════════════════════════════════════════╝
elif current_page == "about":
    st.title(f"ℹ️ {t('about')}")

    lang = st.session_state.lang

    st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
    <h1 class='dm-neon-title'>🧬 DM SMART LAB AI</h1>
    <p style='font-size:1.1rem;font-family:Orbitron,sans-serif;'><b>v{APP_VERSION} — Professional Edition</b></p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='dm-card'>
    <h3>📖 {PROJECT_TITLE.get(lang, PROJECT_TITLE['fr'])}</h3>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        dev1_role = AUTHORS['dev1'].get(f'role_{lang}', AUTHORS['dev1']['role_fr'])
        dev2_role = AUTHORS['dev2'].get(f'role_{lang}', AUTHORS['dev2']['role_fr'])
        st.markdown(f"""<div class='dm-card dm-card-cyan'>
        <h3>👨‍🔬 {'فريق التطوير' if lang == 'ar' else 'Development Team' if lang == 'en' else 'Équipe de Développement'}</h3><br>
        <p><b>🧑‍💻 {AUTHORS['dev1']['name']}</b><br><span style='opacity:0.5;'>{dev1_role}</span></p><br>
        <p><b>🔬 {AUTHORS['dev2']['name']}</b><br><span style='opacity:0.5;'>{dev2_role}</span></p>
        </div>""", unsafe_allow_html=True)
    with c2:
        inst_name = INSTITUTION.get(f'name_{lang}', INSTITUTION['name_fr'])
        country = INSTITUTION.get(f'country_{lang}', INSTITUTION['country_fr'])
        st.markdown(f"""<div class='dm-card'>
        <h3>🏫 {'المؤسسة' if lang == 'ar' else 'Institution' if lang == 'en' else 'Établissement'}</h3><br>
        <p><b>{inst_name}</b></p>
        <p>📍 {INSTITUTION['city']}, {country} 🇩🇿</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    tc = st.columns(8)
    techs = [("🐍", "Python", "Core"), ("🧠", "TensorFlow", "AI"), ("🎨", "Streamlit", "UI"),
             ("📊", "Plotly", "Charts"), ("🗄️", "SQLite", "DB"), ("🔒", "Bcrypt", "Security"),
             ("📄", "FPDF", "PDF"), ("📱", "QR", "Verify")]
    for col, (i, n, d) in zip(tc, techs):
        with col:
            st.markdown(f"""<div class="dm-metric"><span class="dm-metric-icon">{i}</span>
            <div class="dm-metric-val" style="font-size:0.85rem;">{n}</div>
            <div class="dm-metric-lbl">{d}</div></div>""", unsafe_allow_html=True)

    st.caption(f"Made with ❤️ in {INSTITUTION['city']} — {INSTITUTION['year']} 🇩🇿")
