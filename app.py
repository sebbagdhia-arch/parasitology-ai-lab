# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║                  DM SMART LAB AI v6.0 - MEGA PROFESSIONAL EDITION              ║
# ║            Diagnostic Parasitologique par Intelligence Artificielle              ║
# ║                                                                                ║
# ║  Développé par:                                                                ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)                       ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                          ║
# ║                                                                                ║
# ║  INFSPM - Ouargla, Algérie                                                    ║
# ║                                                                                ║
# ║  Features v6.0:                                                                ║
# ║    ✅ SQLite Database          ✅ Role-based Auth (Admin/Tech/Viewer)           ║
# ║    ✅ Bcrypt Password Hashing  ✅ Professional PDF (QR + Signature)             ║
# ║    ✅ Grad-CAM Heatmap         ✅ Smart Chatbot (context-aware)                 ║
# ║    ✅ Advanced Image Analysis  ✅ Zoom + ROI + Histogram                       ║
# ║    ✅ Plotly Charts            ✅ Before/After Comparison                       ║
# ║    ✅ Trend Predictions        ✅ Voice Assistant                               ║
# ║    ✅ 40+ Quiz Questions       ✅ Futuristic Neon UI                            ║
# ║    ✅ Lab Info (Microscope/Prep/Tech)  ✅ Activity Log + Sessions               ║
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

# ── Optional imports with fallbacks ──
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
#  1. إعداد الصفحة
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI v6.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
#  2. الثوابت العامة
# ============================================
APP_VERSION = "6.0.0"
SECRET_KEY = "dm_smart_lab_2026_ultra_secret"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)
AUTO_LOCK_MINUTES = 30

ROLES = {
    "admin": {"level": 3, "label_fr": "Administrateur", "label_ar": "مدير", "label_en": "Administrator", "icon": "👑"},
    "technician": {"level": 2, "label_fr": "Technicien", "label_ar": "تقني", "label_en": "Technician", "icon": "🔬"},
    "viewer": {"level": 1, "label_fr": "Observateur", "label_ar": "مراقب", "label_en": "Viewer", "icon": "👁️"}
}

AUTHORS = {
    "dev1": {"name": "Sebbag Mohamed Dhia Eddine", "role": "Expert IA & Conception"},
    "dev2": {"name": "Ben Sghir Mohamed", "role": "Expert Laboratoire & Données"}
}

INSTITUTION = {
    "name": "Institut National de Formation Supérieure Paramédicale (INFSPM)",
    "short": "INFSPM",
    "city": "Ouargla",
    "country": "Algérie",
    "year": 2026
}

PROJECT_TITLE = (
    "Exploration du potentiel de l'intelligence artificielle "
    "pour la lecture automatique de l'examen parasitologique "
    "à l'état frais"
)

NEON = {
    "cyan": "#00f5ff", "magenta": "#ff00ff", "green": "#00ff88",
    "orange": "#ff6600", "red": "#ff0040", "blue": "#0066ff",
    "purple": "#9933ff", "yellow": "#ffff00", "pink": "#ff69b4"
}

MICROSCOPE_TYPES = {
    "fr": ["Microscope Optique", "Microscope Binoculaire", "Microscope Inversé",
           "Microscope à Fluorescence", "Microscope Contraste de Phase",
           "Microscope Fond Noir", "Microscope Numérique", "Microscope Confocal"],
    "ar": ["مجهر ضوئي", "مجهر ثنائي العينية", "مجهر مقلوب", "مجهر فلوري",
           "مجهر تباين الطور", "مجهر الحقل المظلم", "مجهر رقمي", "مجهر متحد البؤر"],
    "en": ["Optical Microscope", "Binocular Microscope", "Inverted Microscope",
           "Fluorescence Microscope", "Phase Contrast Microscope",
           "Dark Field Microscope", "Digital Microscope", "Confocal Microscope"]
}

MAGNIFICATIONS = ["x4", "x10", "x20", "x40", "x60", "x100 (Immersion)"]

PREPARATION_TYPES = {
    "fr": ["État Frais (Direct)", "Coloration au Lugol", "MIF", "Concentration Ritchie",
           "Kato-Katz", "Coloration MGG", "Coloration Giemsa", "Ziehl-Neelsen Modifié",
           "Coloration Trichrome", "Goutte Épaisse", "Frottis Mince", "Scotch-Test (Graham)",
           "Technique Baermann", "Flottation Willis", "Technique Knott"],
    "ar": ["فحص مباشر", "تلوين لوغول", "MIF", "تقنية ريتشي", "كاتو-كاتز",
           "تلوين MGG", "تلوين جيمزا", "زيل-نيلسن المعدل", "تلوين ثلاثي الألوان",
           "قطرة سميكة", "لطاخة رقيقة", "اختبار سكوتش", "تقنية بايرمان", "تطفيل ويليس", "تقنية نوت"],
    "en": ["Wet Mount (Direct)", "Lugol Staining", "MIF", "Ritchie Concentration",
           "Kato-Katz", "MGG Staining", "Giemsa Staining", "Modified ZN",
           "Trichrome Stain", "Thick Smear", "Thin Smear", "Scotch-Test (Graham)",
           "Baermann Technique", "Willis Flotation", "Knott Technique"]
}


# ============================================
#  3. قاعدة البيانات SQLite
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
                (username, h, name, role, spec)
            )


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
            (user_id, data.get("patient_name",""), data.get("patient_firstname",""),
             data.get("patient_age",0), data.get("patient_sex",""), data.get("patient_weight",0),
             data.get("sample_type",""), data.get("microscope_type",""), data.get("magnification",""),
             data.get("preparation_type",""), data.get("technician1",""), data.get("technician2",""),
             data.get("notes",""), data.get("parasite_detected","Negative"), data.get("confidence",0),
             data.get("risk_level","none"), data.get("is_reliable",0),
             json.dumps(data.get("all_predictions",{})), data.get("image_hash",""),
             data.get("is_demo",0)))
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
            f"SELECT parasite_detected, COUNT(*) as cnt FROM analyses {w} GROUP BY parasite_detected ORDER BY cnt DESC", p
        ).fetchall()
        avg_conf = conn.execute(f"SELECT AVG(confidence) FROM analyses {w}", p).fetchone()[0] or 0
        daily = conn.execute(
            f"SELECT DATE(analysis_date) as day, COUNT(*) as cnt FROM analyses {w} GROUP BY DATE(analysis_date) ORDER BY day DESC LIMIT 30", p
        ).fetchall()
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
    with get_db() as conn:
        conn.execute("INSERT INTO activity_log (user_id, username, action, details) VALUES (?,?,?,?)",
                     (user_id, username, action, details))


def db_get_activity_log(limit=300):
    with get_db() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (limit,)).fetchall()]


def db_save_quiz_score(user_id, username, score, total, pct, category="general"):
    with get_db() as conn:
        conn.execute("INSERT INTO quiz_scores (user_id, username, score, total_questions, percentage, category) VALUES (?,?,?,?,?,?)",
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


def db_get_patient_history(name):
    with get_db() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM analyses WHERE patient_name LIKE ? ORDER BY analysis_date DESC",
            (f"%{name}%",)).fetchall()]


# Initialize DB
init_database()


# ============================================
#  4. نظام اللغات الكامل
# ============================================
TRANSLATIONS = {
    "fr": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Où la Science Rencontre l'Intelligence",
        "login_title": "Connexion Sécurisée",
        "login_subtitle": "Système d'Authentification Professionnel",
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
        "nav_admin": "Administration",
        "nav_compare": "Comparaison",
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
        "scan_lab_info": "Informations du Laboratoire",
        "scan_nom": "Nom",
        "scan_prenom": "Prénom",
        "scan_age": "Âge",
        "scan_sexe": "Sexe",
        "scan_poids": "Poids (kg)",
        "scan_echantillon": "Type d'Échantillon",
        "scan_technician1": "Technicien 1",
        "scan_technician2": "Technicien 2",
        "scan_microscope": "Type de Microscope",
        "scan_magnification": "Grossissement",
        "scan_preparation": "Type de Préparation",
        "scan_notes": "Notes / Observations",
        "scan_thermal": "Vision Thermique",
        "scan_edge": "Détection de Contours",
        "scan_enhanced": "Contraste Amélioré",
        "scan_negative_filter": "Négatif",
        "scan_emboss": "Relief",
        "scan_sharpen": "Netteté",
        "scan_denoise": "Débruitage",
        "scan_capture": "Capture Microscopique",
        "scan_camera": "Caméra",
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
        "scan_save": "Sauvegarder dans la Base",
        "scan_saved": "Résultat sauvegardé dans la base de données !",
        "scan_new": "Nouvelle Analyse",
        "scan_all_probs": "Toutes les probabilités",
        "scan_extra_tests": "Examens complémentaires suggérés",
        "scan_heatmap": "Zone d'intérêt IA (Grad-CAM)",
        "scan_zoom": "Zoom & Région d'Intérêt",
        "scan_zoom_level": "Niveau de Zoom",
        "scan_brightness": "Luminosité",
        "scan_contrast_adj": "Contraste",
        "scan_saturation": "Saturation",
        "scan_histogram": "Histogramme",
        "scan_diagnostic_keys": "Clés Diagnostiques",
        "enc_title": "Encyclopédie des Parasites",
        "enc_search": "Rechercher un parasite...",
        "enc_no_result": "Aucun résultat trouvé.",
        "dash_title": "Tableau de Bord Clinique",
        "dash_total": "Total Analyses",
        "dash_reliable": "Fiables",
        "dash_check": "À Vérifier",
        "dash_frequent": "Plus Fréquent",
        "dash_avg_conf": "Confiance Moyenne",
        "dash_system": "Système Opérationnel",
        "dash_distribution": "Distribution des Parasites",
        "dash_confidence_chart": "Niveaux de Confiance",
        "dash_history": "Historique Complet",
        "dash_export": "Exporter CSV",
        "dash_export_excel": "Exporter Excel",
        "dash_export_json": "Exporter JSON",
        "dash_no_data": "Aucune donnée disponible",
        "dash_no_data_desc": "Effectuez votre première analyse.",
        "dash_trends": "Tendances (30 jours)",
        "dash_validate": "Valider",
        "about_title": "À Propos du Projet",
        "about_desc": "Système de Diagnostic Parasitologique par IA",
        "about_project_desc": "Ce projet innovant utilise les technologies de Deep Learning et de Vision par Ordinateur pour assister les techniciens de laboratoire dans l'identification rapide et précise des parasites lors de l'examen parasitologique des selles à l'état frais.",
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
        "echantillon_moelle": "Aspiration Médullaire",
        "echantillon_autre": "Autre",
        "voice_intro": "Bonjour ! Il est {time}. Je suis DM Smart Lab, intelligence artificielle développée par les Techniciens Supérieurs {dev1} et {dev2}. Préparez vos lames, et ne me chatouillez pas avec le microscope !",
        "voice_title": "Mémoire de Fin d'Études : {title}. Institut National de Formation Supérieure Paramédicale de Ouargla.",
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
        "quiz_leaderboard": "Classement",
        "chatbot_title": "Dr. DhiaBot - Assistant Médical IA",
        "chatbot_placeholder": "Posez votre question sur les parasites...",
        "chatbot_thinking": "Dr. DhiaBot réfléchit...",
        "daily_tip": "Conseil du Jour",
        "activity_log": "Journal d'Activité",
        "admin_title": "Administration du Système",
        "admin_users": "Gestion des Utilisateurs",
        "admin_create_user": "Créer un Utilisateur",
        "admin_no_permission": "Accès réservé aux administrateurs.",
        "compare_title": "Comparaison d'Images",
        "compare_desc": "Comparez deux images microscopiques.",
        "pdf_title": "RAPPORT D'ANALYSE PARASITOLOGIQUE",
        "pdf_subtitle": "Analyse assistée par Intelligence Artificielle",
    },
    "ar": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "حيث يلتقي العلم بالذكاء",
        "login_title": "تسجيل الدخول الآمن",
        "login_subtitle": "نظام مصادقة احترافي",
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
        "nav_admin": "الإدارة",
        "nav_compare": "المقارنة",
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
        "scan_lab_info": "معلومات المخبر",
        "scan_nom": "اللقب",
        "scan_prenom": "الاسم",
        "scan_age": "العمر",
        "scan_sexe": "الجنس",
        "scan_poids": "الوزن (كغ)",
        "scan_echantillon": "نوع العينة",
        "scan_technician1": "التقني 1",
        "scan_technician2": "التقني 2",
        "scan_microscope": "نوع المجهر",
        "scan_magnification": "التكبير",
        "scan_preparation": "نوع التحضير",
        "scan_notes": "ملاحظات",
        "scan_thermal": "الرؤية الحرارية",
        "scan_edge": "كشف الحواف",
        "scan_enhanced": "تحسين التباين",
        "scan_negative_filter": "سلبي",
        "scan_emboss": "نقش بارز",
        "scan_sharpen": "حدّة",
        "scan_denoise": "إزالة ضوضاء",
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
        "scan_download_pdf": "تحميل التقرير PDF",
        "scan_save": "حفظ في القاعدة",
        "scan_saved": "تم الحفظ في قاعدة البيانات !",
        "scan_new": "تحليل جديد",
        "scan_all_probs": "جميع الاحتمالات",
        "scan_extra_tests": "فحوصات إضافية مقترحة",
        "scan_heatmap": "منطقة اهتمام الذكاء (Grad-CAM)",
        "scan_zoom": "التكبير ومنطقة الاهتمام",
        "scan_zoom_level": "مستوى التكبير",
        "scan_brightness": "السطوع",
        "scan_contrast_adj": "التباين",
        "scan_saturation": "التشبع",
        "scan_histogram": "المدرج التكراري",
        "scan_diagnostic_keys": "مفاتيح التشخيص",
        "enc_title": "موسوعة الطفيليات",
        "enc_search": "ابحث...",
        "enc_no_result": "لا توجد نتائج.",
        "dash_title": "لوحة التحكم السريرية",
        "dash_total": "إجمالي التحاليل",
        "dash_reliable": "موثوقة",
        "dash_check": "تحتاج مراجعة",
        "dash_frequent": "الأكثر شيوعاً",
        "dash_avg_conf": "متوسط الثقة",
        "dash_system": "النظام يعمل",
        "dash_distribution": "توزيع الطفيليات",
        "dash_confidence_chart": "مستويات الثقة",
        "dash_history": "السجل الكامل",
        "dash_export": "تصدير CSV",
        "dash_export_excel": "تصدير Excel",
        "dash_export_json": "تصدير JSON",
        "dash_no_data": "لا توجد بيانات",
        "dash_no_data_desc": "قم بإجراء تحليل.",
        "dash_trends": "الاتجاهات (30 يوم)",
        "dash_validate": "مصادقة",
        "about_title": "حول المشروع",
        "about_desc": "نظام التشخيص الطفيلي بالذكاء الاصطناعي",
        "about_project_desc": "يستخدم هذا المشروع التعلم العميق والرؤية الحاسوبية لمساعدة تقنيي المخابر.",
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
        "echantillon_moelle": "بزل نخاع",
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
        "quiz_leaderboard": "الترتيب",
        "chatbot_title": "المساعد الطبي الذكي",
        "chatbot_placeholder": "اسأل عن الطفيليات...",
        "chatbot_thinking": "المساعد يفكر...",
        "daily_tip": "نصيحة اليوم",
        "activity_log": "سجل النشاطات",
        "admin_title": "إدارة النظام",
        "admin_users": "إدارة المستخدمين",
        "admin_create_user": "إنشاء مستخدم",
        "admin_no_permission": "محجوز للمديرين.",
        "compare_title": "مقارنة الصور",
        "compare_desc": "قارن بين صورتين مجهريتين.",
        "pdf_title": "تقرير التحليل الطفيلي",
        "pdf_subtitle": "تحليل بمساعدة الذكاء الاصطناعي",
    },
    "en": {
        "app_title": "DM SMART LAB AI",
        "app_subtitle": "Where Science Meets Intelligence",
        "login_title": "Secure Login",
        "login_subtitle": "Professional Authentication System",
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
        "nav_admin": "Administration",
        "nav_compare": "Comparison",
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
        "scan_lab_info": "Laboratory Information",
        "scan_nom": "Last Name",
        "scan_prenom": "First Name",
        "scan_age": "Age",
        "scan_sexe": "Sex",
        "scan_poids": "Weight (kg)",
        "scan_echantillon": "Sample Type",
        "scan_technician1": "Technician 1",
        "scan_technician2": "Technician 2",
        "scan_microscope": "Microscope Type",
        "scan_magnification": "Magnification",
        "scan_preparation": "Preparation Type",
        "scan_notes": "Notes / Observations",
        "scan_thermal": "Thermal Vision",
        "scan_edge": "Edge Detection",
        "scan_enhanced": "Enhanced Contrast",
        "scan_negative_filter": "Negative",
        "scan_emboss": "Emboss",
        "scan_sharpen": "Sharpen",
        "scan_denoise": "Denoise",
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
        "scan_download_pdf": "Download PDF Report",
        "scan_save": "Save to Database",
        "scan_saved": "Saved to database!",
        "scan_new": "New Analysis",
        "scan_all_probs": "All probabilities",
        "scan_extra_tests": "Suggested additional tests",
        "scan_heatmap": "AI Focus Area (Grad-CAM)",
        "scan_zoom": "Zoom & ROI",
        "scan_zoom_level": "Zoom Level",
        "scan_brightness": "Brightness",
        "scan_contrast_adj": "Contrast",
        "scan_saturation": "Saturation",
        "scan_histogram": "Histogram",
        "scan_diagnostic_keys": "Diagnostic Keys",
        "enc_title": "Parasite Encyclopedia",
        "enc_search": "Search...",
        "enc_no_result": "No results.",
        "dash_title": "Clinical Dashboard",
        "dash_total": "Total Analyses",
        "dash_reliable": "Reliable",
        "dash_check": "To Verify",
        "dash_frequent": "Most Frequent",
        "dash_avg_conf": "Avg Confidence",
        "dash_system": "System OK",
        "dash_distribution": "Distribution",
        "dash_confidence_chart": "Confidence Levels",
        "dash_history": "Full History",
        "dash_export": "Export CSV",
        "dash_export_excel": "Export Excel",
        "dash_export_json": "Export JSON",
        "dash_no_data": "No data",
        "dash_no_data_desc": "Perform an analysis.",
        "dash_trends": "Trends (30 days)",
        "dash_validate": "Validate",
        "about_title": "About",
        "about_desc": "AI Parasitological Diagnostic System",
        "about_project_desc": "This project uses Deep Learning and Computer Vision to assist lab technicians.",
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
        "echantillon_moelle": "Bone Marrow",
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
        "quiz_leaderboard": "Leaderboard",
        "chatbot_title": "Dr. DhiaBot - AI Medical Assistant",
        "chatbot_placeholder": "Ask about parasites...",
        "chatbot_thinking": "Dr. DhiaBot is thinking...",
        "daily_tip": "Daily Tip",
        "activity_log": "Activity Log",
        "admin_title": "System Administration",
        "admin_users": "User Management",
        "admin_create_user": "Create User",
        "admin_no_permission": "Admin access only.",
        "compare_title": "Image Comparison",
        "compare_desc": "Compare two microscopic images.",
        "pdf_title": "PARASITOLOGICAL ANALYSIS REPORT",
        "pdf_subtitle": "AI-Assisted Analysis",
    }
}


# ============================================
#  5. قاعدة بيانات الطفيليات الشاملة
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": {
            "fr": "Kyste spherique (10-15μm) a 4 noyaux, corps chromatoide en cigare. Trophozoite (20-40μm) avec pseudopodes digitiformes et hematies phagocytees.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 نوى. طور غاذي (20-40 ميكرومتر) بأقدام كاذبة وكريات حمراء مبتلعة.",
            "en": "Spherical cyst (10-15μm) with 4 nuclei, cigar-shaped chromatoid body. Trophozoite (20-40μm) with pseudopods and phagocytized RBCs."
        },
        "description": {
            "fr": "Protozoaire responsable de l'amibiase intestinale (dysenterie) et extra-intestinale (abces hepatique). Transmission feco-orale.",
            "ar": "أولي مسبب للأميبيا المعوية والخارج معوية. انتقال برازي-فموي.",
            "en": "Protozoan causing intestinal amebiasis (dysentery) and extra-intestinal (hepatic abscess). Feco-oral transmission."
        },
        "funny": {
            "fr": "Le ninja des intestins ! Il mange des globules rouges au petit-dejeuner !",
            "ar": "نينجا الأمعاء! يأكل كريات حمراء على الفطور!",
            "en": "The intestinal ninja! Eats RBCs for breakfast!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Metronidazole 500mg x3/j (7-10j) + Amoebicide de contact (Intetrix). Controle EPS J15/J30.",
            "ar": "ميترونيدازول 500 مغ × 3/يوم (7-10 أيام) + مبيد أميبي تلامسي. مراقبة.",
            "en": "Metronidazole 500mg x3/d (7-10d) + contact amoebicide (Intetrix). Follow-up D15/D30."
        },
        "extra_tests": {
            "fr": ["Sérologie amibienne (IgG/IgM)", "Échographie hépatique", "NFS + CRP + VS", "PCR Entamoeba", "Scanner abdominal si abcès"],
            "ar": ["مصلية أميبية", "إيكو كبدي", "تعداد دم + CRP", "PCR أنتاميبا", "سكانر بطني"],
            "en": ["Amoebic serology", "Hepatic ultrasound", "CBC + CRP + ESR", "Entamoeba PCR", "Abdominal CT"]
        },
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": {
            "fr": "Kyste ingéré → Excystation → Trophozoite → Invasion tissulaire → Enkystement → Émission",
            "ar": "ابتلاع الكيس ← خروج ← طور غاذي ← غزو نسيجي ← تكيس ← طرح",
            "en": "Cyst ingested → Excystation → Trophozoite → Tissue invasion → Encystation → Release"
        },
        "diagnostic_keys": {
            "fr": "• E. histolytica vs E. dispar: seule histolytica phagocyte les hématies\n• Kyste 4 noyaux (vs E. coli 8 noyaux)\n• Corps chromatoïdes en cigare\n• Mobilité directionnelle",
            "ar": "• تمييز عن E. dispar: فقط histolytica تبتلع الكريات\n• كيس 4 نوى (مقابل 8 لـ E. coli)\n• أجسام كروماتينية سيجارية",
            "en": "• E. histolytica vs E. dispar: only histolytica phagocytizes RBCs\n• 4-nuclei cyst (vs 8 in E. coli)\n• Cigar-shaped chromatoid bodies"
        }
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia (intestinalis)",
        "morphology": {
            "fr": "Trophozoite piriforme en 'cerf-volant' (12-15μm), 2 noyaux (face de hibou), disque adhésif, 4 paires de flagelles. Kyste ovoïde (8-12μm) à 4 noyaux.",
            "ar": "طور غاذي كمثري 'طائرة ورقية' (12-15 ميكرومتر)، نواتان (وجه بومة)، قرص لاصق، 4 أزواج أسواط. كيس بيضاوي (8-12 ميكرومتر) بـ 4 نوى.",
            "en": "Pear-shaped 'kite' trophozoite (12-15μm), 2 nuclei (owl face), adhesive disc, 4 flagella pairs. Ovoid cyst (8-12μm) with 4 nuclei."
        },
        "description": {
            "fr": "Flagellé du duodénum. Diarrhée graisseuse chronique, malabsorption. Transmission hydrique.",
            "ar": "سوطي في الاثني عشر. إسهال دهني مزمن، سوء امتصاص. انتقال مائي.",
            "en": "Duodenal flagellate. Chronic fatty diarrhea, malabsorption. Waterborne."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil ! Un touriste qui refuse de partir !",
            "ar": "يحدّق فيك بنظارته! سائح يرفض المغادرة!",
            "en": "Staring with sunglasses! A tourist who refuses to leave!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Métronidazole 250mg x3/j (5j) OU Tinidazole 2g dose unique. Vérifier la source d'eau.",
            "ar": "ميترونيدازول 250 مغ × 3/يوم (5 أيام) أو تينيدازول 2غ جرعة واحدة.",
            "en": "Metronidazole 250mg x3/d (5d) OR Tinidazole 2g single dose."
        },
        "extra_tests": {
            "fr": ["Antigène Giardia (ELISA)", "Test de malabsorption", "EPS x3", "PCR Giardia"],
            "ar": ["مستضد جيارديا (ELISA)", "اختبار سوء امتصاص", "فحص براز × 3", "PCR"],
            "en": ["Giardia antigen (ELISA)", "Malabsorption test", "Stool exam x3", "Giardia PCR"]
        },
        "color": "#ff9500", "icon": "🟠",
        "lifecycle": {
            "fr": "Kyste ingéré → Excystation duodénale → Trophozoite → Adhésion → Multiplication → Enkystement",
            "ar": "ابتلاع الكيس ← خروج في الاثني عشر ← طور غاذي ← التصاق ← تكاثر ← تكيس",
            "en": "Cyst ingested → Duodenal excystation → Trophozoite → Adhesion → Multiplication → Encystation"
        },
        "diagnostic_keys": {
            "fr": "• Forme en cerf-volant pathognomonique\n• 2 noyaux = face de hibou\n• Disque adhésif visible au Lugol\n• Mobilité 'feuille morte'",
            "ar": "• شكل طائرة ورقية مميز\n• نواتان = وجه بومة\n• قرص لاصق يظهر باللوغول",
            "en": "• Pathognomonic kite shape\n• 2 nuclei = owl face\n• Adhesive disc visible with Lugol"
        }
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / major / tropica",
        "morphology": {
            "fr": "Amastigotes ovoïdes (2-5μm) intracellulaires dans les macrophages. Noyau + kinétoplaste (MGG). Promastigotes fusiformes en culture.",
            "ar": "لامسوطات بيضاوية (2-5 ميكرومتر) داخل البلاعم. نواة + حركي (MGG). سوطيات مغزلية في الزرع.",
            "en": "Ovoid amastigotes (2-5μm) intracellular in macrophages. Nucleus + kinetoplast (MGG). Fusiform promastigotes in culture."
        },
        "description": {
            "fr": "Transmis par le phlébotome. Cutanée (bouton d'Orient), viscérale (Kala-azar). En Algérie: L. infantum (nord), L. major (sud).",
            "ar": "ينتقل بذبابة الرمل. جلدي (حبة الشرق)، حشوي (كالا آزار). في الجزائر: L. infantum (شمال)، L. major (جنوب).",
            "en": "Sandfly-transmitted. Cutaneous (Oriental sore), visceral (Kala-azar). In Algeria: L. infantum (north), L. major (south)."
        },
        "funny": {
            "fr": "Petit mais costaud ! Il squatte les macrophages comme un locataire qui ne paie pas !",
            "ar": "صغير لكن قوي! يسكن البلاعم كمستأجر لا يدفع الإيجار!",
            "en": "Small but mighty! Squats in macrophages like a deadbeat tenant!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Cutanée: Glucantime IM. Viscérale: Amphotéricine B liposomale. MDO en Algérie.",
            "ar": "جلدي: غلوكانتيم. حشوي: أمفوتيريسين ب. مرض ذو تصريح إجباري.",
            "en": "Cutaneous: Glucantime IM. Visceral: Liposomal Amphotericin B. Mandatory reporting."
        },
        "extra_tests": {
            "fr": ["IDR Monténégro", "Sérologie Leishmania", "Ponction médullaire", "Biopsie + MGG", "PCR Leishmania", "NFS"],
            "ar": ["اختبار مونتينيغرو", "مصلية ليشمانيا", "بزل نخاع", "خزعة + MGG", "PCR", "تعداد دم"],
            "en": ["Montenegro test", "Leishmania serology", "Bone marrow aspirate", "Biopsy + MGG", "Leishmania PCR", "CBC"]
        },
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": {
            "fr": "Piqûre phlébotome → Promastigotes → Phagocytose → Amastigotes intracellulaires → Multiplication → Lyse",
            "ar": "لدغة ذبابة الرمل ← سوطيات ← بلعمة ← لامسوطات داخل خلوية ← تكاثر ← تحلل",
            "en": "Sandfly bite → Promastigotes → Phagocytosis → Intracellular amastigotes → Multiplication → Lysis"
        },
        "diagnostic_keys": {
            "fr": "• Amastigotes 2-5μm intracellulaires\n• Noyau + kinétoplaste au MGG\n• Culture NNN: promastigotes\n• PCR = gold standard espèce",
            "ar": "• لامسوطات 2-5 ميكرومتر داخل خلوية\n• نواة + حركي بـ MGG\n• زرع NNN: سوطيات\n• PCR = المعيار الذهبي",
            "en": "• 2-5μm intracellular amastigotes\n• Nucleus + kinetoplast on MGG\n• NNN culture: promastigotes\n• PCR = gold standard"
        }
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax / ovale / malariae",
        "morphology": {
            "fr": "P. falciparum: anneau 'bague à chaton', gamétocytes en banane. P. vivax: trophozoïte amiboïde, granulations Schüffner. Schizontes en rosace.",
            "ar": "P. falciparum: حلقة 'خاتم'، عرسات موزية. P. vivax: طور غاذي أميبي، حبيبات شوفنر. منسقات وردية.",
            "en": "P. falciparum: 'signet ring', banana gametocytes. P. vivax: amoeboid trophozoite, Schüffner dots. Rosette schizonts."
        },
        "description": {
            "fr": "URGENCE MÉDICALE ! Agent du paludisme. P. falciparum: le plus mortel. Transmission par l'anophèle femelle.",
            "ar": "حالة طوارئ! مسبب الملاريا. P. falciparum الأخطر. ينتقل بأنثى الأنوفيل.",
            "en": "MEDICAL EMERGENCY! Malaria agent. P. falciparum: most lethal. Female Anopheles transmission."
        },
        "funny": {
            "fr": "Il demande le mariage à tes globules ! Et ses gamétocytes en banane... le clown du microscope !",
            "ar": "يطلب الزواج من كرياتك! وعرساته الموزية... مهرج المجهر!",
            "en": "Proposes to your RBCs! And banana gametocytes... the microscope's clown!"
        },
        "risk_level": "critical",
        "risk_display": {"fr": "🚨 URGENCE MÉDICALE", "ar": "🚨 حالة طوارئ", "en": "🚨 EMERGENCY"},
        "advice": {
            "fr": "HOSPITALISATION ! ACT (Artémisinine). Quinine IV si grave. Parasitémie /4-6h. Surveillance glycémie, créatinine.",
            "ar": "تنويم فوري! ACT. كينين وريدي إذا خطير. فحص طفيليات كل 4-6 ساعات.",
            "en": "HOSPITALIZATION! ACT. IV Quinine if severe. Parasitemia /4-6h. Monitor glucose, creatinine."
        },
        "extra_tests": {
            "fr": ["TDR Paludisme (HRP2/pLDH)", "Frottis + Goutte épaisse URGENCE", "Parasitémie quantitative", "NFS complète", "Bilan hépatho-rénal", "Glycémie", "Lactates"],
            "ar": ["اختبار سريع (HRP2/pLDH)", "لطاخة + قطرة سميكة عاجل", "طفيليات كمية", "تعداد دم كامل", "وظائف كبد وكلى", "سكر الدم", "لاكتات"],
            "en": ["Malaria RDT (HRP2/pLDH)", "Smear + Thick drop URGENT", "Quantitative parasitemia", "CBC", "Hepato-renal panel", "Glucose", "Lactate"]
        },
        "color": "#7f1d1d", "icon": "🚨",
        "lifecycle": {
            "fr": "Piqûre anophèle → Sporozoïtes → Hépatocytes → Mérozoïtes → Hématies → Gamétocytes → Cycle sexué moustique",
            "ar": "لدغة أنوفيل ← بوغيات ← خلايا كبد ← جزيئيات ← كريات حمراء ← عرسات ← دورة جنسية",
            "en": "Anopheles bite → Sporozoites → Hepatocytes → Merozoites → RBCs → Gametocytes → Sexual cycle"
        },
        "diagnostic_keys": {
            "fr": "• URGENCE: résultat <2h\n• Frottis: identification espèce\n• Goutte épaisse: 10x plus sensible\n• >2% parasitémie = forme grave\n• Gamétocytes en banane = P. falciparum",
            "ar": "• عاجل: نتيجة <2 ساعة\n• لطاخة: تحديد النوع\n• قطرة سميكة: أكثر حساسية\n• >2% = شكل خطير\n• عرسات موزية = P. falciparum",
            "en": "• URGENT: result <2h\n• Smear: species ID\n• Thick: 10x sensitive\n• >2% parasitemia = severe\n• Banana gametocytes = P. falciparum"
        }
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "morphology": {
            "fr": "Forme en S/C (15-30μm), flagelle libre, membrane ondulante, kinétoplaste postérieur. Coloration MGG/Giemsa.",
            "ar": "شكل S/C (15-30 ميكرومتر)، سوط حر، غشاء متموج، حركي خلفي. تلوين MGG/جيمزا.",
            "en": "S/C shape (15-30μm), free flagellum, undulating membrane, posterior kinetoplast. MGG/Giemsa staining."
        },
        "description": {
            "fr": "Maladie du sommeil (T. brucei, mouche tsé-tsé) ou Chagas (T. cruzi, triatome). Phase hémolymphatique puis neurologique.",
            "ar": "مرض النوم (T. brucei، ذبابة تسي تسي) أو شاغاس (T. cruzi). مرحلة دموية ثم عصبية.",
            "en": "Sleeping sickness (T. brucei, tsetse) or Chagas (T. cruzi, triatomine). Hemolymphatic then neurological."
        },
        "funny": {
            "fr": "Il court comme Mahrez avec sa membrane ondulante ! Et sa tsé-tsé, c'est le pire taxi !",
            "ar": "يجري مثل محرز بغشائه المتموج! وذبابة تسي تسي أسوأ تاكسي!",
            "en": "Runs like Mahrez with its undulating membrane! Tsetse = worst taxi!"
        },
        "risk_level": "high",
        "risk_display": {"fr": "Élevé 🔴", "ar": "مرتفع 🔴", "en": "High 🔴"},
        "advice": {
            "fr": "Phase 1: Pentamidine/Suramine. Phase 2: NECT/Mélarsoprol. Ponction lombaire OBLIGATOIRE pour staging.",
            "ar": "مرحلة 1: بنتاميدين/سورامين. مرحلة 2: NECT/ميلارسوبرول. بزل قطني إلزامي.",
            "en": "Phase 1: Pentamidine/Suramin. Phase 2: NECT/Melarsoprol. LP MANDATORY for staging."
        },
        "extra_tests": {
            "fr": ["Ponction lombaire", "Sérologie (CATT)", "IgM sérique", "Suc ganglionnaire", "NFS"],
            "ar": ["بزل قطني", "مصلية (CATT)", "IgM مصلي", "عصارة عقدة", "تعداد دم"],
            "en": ["Lumbar puncture", "Serology (CATT)", "Serum IgM", "Lymph aspirate", "CBC"]
        },
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": {
            "fr": "Piqûre tsé-tsé → Trypomastigotes → Sang/lymphe → Phase 1 → Franchissement BHE → Phase 2 neurologique",
            "ar": "لدغة تسي تسي ← أطوار سوطية ← دم/لمف ← مرحلة 1 ← عبور الحاجز الدماغي ← مرحلة 2",
            "en": "Tsetse bite → Trypomastigotes → Blood/lymph → Phase 1 → BBB crossing → Phase 2 neurological"
        },
        "diagnostic_keys": {
            "fr": "• Forme S/C avec membrane ondulante\n• Kinétoplaste postérieur\n• IgM très élevée\n• Staging par PL obligatoire",
            "ar": "• شكل S/C بغشاء متموج\n• حركي خلفي\n• IgM مرتفع جداً\n• تصنيف ببزل قطني",
            "en": "• S/C shape with undulating membrane\n• Posterior kinetoplast\n• Very elevated IgM\n• Mandatory LP staging"
        }
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni / japonicum",
        "morphology": {
            "fr": "Œuf ovoïde (115-170μm) avec éperon terminal (S. haematobium) ou latéral (S. mansoni). Miracidium mobile.",
            "ar": "بيضة بيضاوية (115-170 ميكرومتر) بنتوء طرفي (S. haematobium) أو جانبي (S. mansoni). ميراسيديوم متحرك.",
            "en": "Ovoid egg (115-170μm) with terminal spine (S. haematobium) or lateral (S. mansoni). Motile miracidium."
        },
        "description": {
            "fr": "Bilharziose. S. haematobium: uro-génitale (hématurie). S. mansoni: hépato-intestinale. 2ème endémie parasitaire mondiale.",
            "ar": "بلهارسيا. S. haematobium: بولية (دم في البول). S. mansoni: كبدية معوية. ثاني وباء طفيلي عالمياً.",
            "en": "Bilharziasis. S. haematobium: urogenital (hematuria). S. mansoni: hepato-intestinal. 2nd parasitic endemic worldwide."
        },
        "funny": {
            "fr": "L'œuf avec un dard ! La baignade peut coûter cher. Les cercaires = micro-torpilles !",
            "ar": "البيضة ذات الشوكة! السباحة مكلفة. السركاريا = طوربيدات صغيرة!",
            "en": "Egg with a sting! Swimming can cost you. Cercariae = micro-torpedoes!"
        },
        "risk_level": "medium",
        "risk_display": {"fr": "Moyen 🟠", "ar": "متوسط 🟠", "en": "Medium 🟠"},
        "advice": {
            "fr": "Praziquantel 40mg/kg dose unique. S. haematobium: urines de midi. Éviter eau douce en zone d'endémie.",
            "ar": "برازيكوانتيل 40 مغ/كغ جرعة واحدة. بول الظهيرة للـ haematobium. تجنب المياه العذبة.",
            "en": "Praziquantel 40mg/kg single dose. Midday urine for haematobium. Avoid freshwater in endemic areas."
        },
        "extra_tests": {
            "fr": ["ECBU + sédiment midi", "Sérologie Schistosoma", "Écho vésicale/hépatique", "NFS + Éosinophilie", "Biopsie rectale"],
            "ar": ["فحص بول + رواسب الظهيرة", "مصلية بلهارسيا", "إيكو مثانة/كبد", "تعداد دم + حمضات", "خزعة مستقيم"],
            "en": ["Urinalysis + midday sediment", "Schistosoma serology", "Bladder/hepatic US", "CBC + Eosinophilia", "Rectal biopsy"]
        },
        "color": "#ff9500", "icon": "🟠",
        "lifecycle": {
            "fr": "Œuf → Miracidium → Mollusque → Cercaire → Pénétration cutanée → Schistosomule → Vers adultes → Ponte",
            "ar": "بيضة ← ميراسيديوم ← حلزون ← سركاريا ← اختراق جلدي ← ديدان بالغة ← وضع البيض",
            "en": "Egg → Miracidium → Snail → Cercaria → Skin penetration → Schistosomula → Adult worms → Eggs"
        },
        "diagnostic_keys": {
            "fr": "• S. haematobium: éperon TERMINAL, urines MIDI\n• S. mansoni: éperon LATÉRAL, selles\n• Miracidium vivant dans l'œuf\n• Éosinophilie élevée",
            "ar": "• S. haematobium: نتوء طرفي، بول الظهيرة\n• S. mansoni: نتوء جانبي، براز\n• ميراسيديوم حي\n• حمضات مرتفعة",
            "en": "• S. haematobium: TERMINAL spine, MIDDAY urine\n• S. mansoni: LATERAL spine, stool\n• Living miracidium\n• Elevated eosinophilia"
        }
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": {
            "fr": "Absence d'éléments parasitaires après examen direct et concentration. Flore bactérienne normale.",
            "ar": "غياب عناصر طفيلية بعد الفحص المباشر والتركيز. نبيت جرثومي طبيعي.",
            "en": "No parasitic elements after direct exam and concentration. Normal flora."
        },
        "description": {
            "fr": "Échantillon négatif. Un seul examen négatif n'exclut pas (sensibilité ~50-60%). Répéter x3.",
            "ar": "عينة سلبية. فحص واحد لا يستبعد الإصابة (حساسية ~50-60%). كرر × 3.",
            "en": "Negative sample. Single negative doesn't exclude (sensitivity ~50-60%). Repeat x3."
        },
        "funny": {
            "fr": "Rien à signaler ! Champagne ! Mais les parasites sont des maîtres du cache-cache ! 🥂",
            "ar": "لا شيء! شمبانيا! لكن الطفيليات أساتذة الاختباء! 🥂",
            "en": "All clear! Champagne! But parasites are hide-and-seek masters! 🥂"
        },
        "risk_level": "none",
        "risk_display": {"fr": "Négatif 🟢", "ar": "سلبي 🟢", "en": "Negative 🟢"},
        "advice": {
            "fr": "RAS. Répéter x3 si suspicion clinique. Bonne hygiène alimentaire.",
            "ar": "لا شيء. كرر × 3 إذا استمر الاشتباه. نظافة غذائية.",
            "en": "All clear. Repeat x3 if clinical suspicion. Good hygiene."
        },
        "extra_tests": {
            "fr": ["Répéter EPS x3", "Sérologie ciblée si besoin", "NFS (éosinophilie?)"],
            "ar": ["كرر فحص البراز × 3", "مصلية موجهة إذا لزم", "تعداد دم (حمضات؟)"],
            "en": ["Repeat stool x3", "Targeted serology if needed", "CBC (eosinophilia?)"]
        },
        "color": "#00ff88", "icon": "🟢",
        "lifecycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "diagnostic_keys": {
            "fr": "• Direct + Lugol négatif\n• Concentration négative\n• Répéter x3 si doute",
            "ar": "• مباشر + لوغول سلبي\n• تركيز سلبي\n• كرر × 3 إذا شك",
            "en": "• Direct + Lugol negative\n• Concentration negative\n• Repeat x3 if doubt"
        }
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())


# ============================================
#  6. أسئلة الاختبار - 40+ سؤال متنوع
# ============================================
QUIZ_QUESTIONS = {
    "fr": [
        {"q": "Quel parasite présente une 'bague à chaton' dans les hématies?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Le Plasmodium montre une forme en bague à chaton au stade trophozoïte jeune.", "category": "Hématozoaires"},
        {"q": "Le kyste mature de Giardia possède combien de noyaux?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "4 noyaux. Le trophozoïte en a 2.", "category": "Protozoaires intestinaux"},
        {"q": "Quel parasite est transmis par le phlébotome?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania = phlébotome (mouche des sables).", "category": "Protozoaires tissulaires"},
        {"q": "L'éperon terminal caractérise:", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "S. haematobium = terminal. S. mansoni = latéral.", "category": "Helminthes"},
        {"q": "Examen urgent en cas de suspicion de paludisme?", "options": ["Coproculture", "ECBU", "Goutte épaisse + Frottis", "Sérologie"], "answer": 2, "explanation": "Goutte épaisse + frottis = référence urgente.", "category": "Diagnostic"},
        {"q": "Le trophozoïte d'E. histolytica se distingue par:", "options": ["Flagelles", "Hématies phagocytées", "Membrane ondulante", "Kinétoplaste"], "answer": 1, "explanation": "Hématies phagocytées = critère de pathogénicité.", "category": "Protozoaires"},
        {"q": "La maladie de Chagas est causée par:", "options": ["T. b. gambiense", "T. cruzi", "L. donovani", "P. vivax"], "answer": 1, "explanation": "T. cruzi transmis par les triatomes.", "category": "Protozoaires sanguins"},
        {"q": "Colorant pour les amastigotes de Leishmania?", "options": ["Ziehl-Neelsen", "Gram", "MGG", "Lugol"], "answer": 2, "explanation": "MGG = noyau + kinétoplaste visibles.", "category": "Techniques"},
        {"q": "Traitement de référence de la bilharziose?", "options": ["Paludisme", "Métronidazole", "Praziquantel", "Albendazole"], "answer": 2, "explanation": "Praziquantel = choix n°1.", "category": "Thérapeutique"},
        {"q": "La 'face de hibou' est observée chez:", "options": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "answer": 1, "explanation": "2 noyaux symétriques de Giardia.", "category": "Morphologie"},
        {"q": "La technique de Ritchie est une méthode de:", "options": ["Coloration", "Concentration diphasique", "Culture", "Sérologie"], "answer": 1, "explanation": "Formol-éther = concentration pour œufs/kystes.", "category": "Techniques"},
        {"q": "Le Lugol met en évidence:", "options": ["Flagelles", "Noyaux des kystes", "Hématies", "Bactéries"], "answer": 1, "explanation": "L'iode colore le glycogène et les noyaux.", "category": "Techniques"},
        {"q": "L'objectif x100 nécessite:", "options": ["Eau", "Huile d'immersion", "Alcool", "Sérum"], "answer": 1, "explanation": "Huile = augmente l'indice de réfraction.", "category": "Microscopie"},
        {"q": "Le scotch-test de Graham recherche:", "options": ["Giardia", "Enterobius (oxyure)", "Ascaris", "Taenia"], "answer": 1, "explanation": "Oeufs d'oxyure dans les plis périanaux.", "category": "Techniques"},
        {"q": "Coloration pour Cryptosporidium?", "options": ["Lugol", "Ziehl-Neelsen modifié", "MGG", "Gram"], "answer": 1, "explanation": "ZN modifié = oocystes roses sur fond vert.", "category": "Techniques"},
        {"q": "L'œuf d'Ascaris est:", "options": ["Avec éperon", "Mamelonné/coque épaisse", "Operculé", "En citron"], "answer": 1, "explanation": "Ovoïde, mamelonné, coque brune épaisse.", "category": "Helminthes"},
        {"q": "Le scolex de T. solium possède:", "options": ["Ventouses seules", "Crochets seuls", "Ventouses + crochets", "Bothridies"], "answer": 2, "explanation": "Ténia armé = 4 ventouses + crochets.", "category": "Helminthes"},
        {"q": "L'éosinophilie sanguine oriente vers:", "options": ["Infection bactérienne", "Helminthiase", "Virose", "Paludisme"], "answer": 1, "explanation": "Éosinophilie = marqueur d'helminthiase.", "category": "Diagnostic"},
        {"q": "La cysticercose est causée par:", "options": ["T. saginata adulte", "Larve de T. solium", "Echinococcus", "Ascaris"], "answer": 1, "explanation": "Cysticerque de T. solium chez l'homme.", "category": "Helminthes"},
        {"q": "En Algérie, la leishmaniose cutanée du sud est due à:", "options": ["L. infantum", "L. major", "L. tropica", "L. braziliensis"], "answer": 1, "explanation": "L. major = cutanée zoonotique du sud.", "category": "Épidémiologie"},
        {"q": "Vecteur du paludisme?", "options": ["Aedes", "Culex", "Anopheles", "Simulium"], "answer": 2, "explanation": "Anophèle femelle = seul vecteur du Plasmodium.", "category": "Épidémiologie"},
        {"q": "Le kyste hydatique est dû à:", "options": ["T. saginata", "Echinococcus granulosus", "Fasciola", "Toxocara"], "answer": 1, "explanation": "Echinococcus granulosus (ver du chien).", "category": "Helminthes"},
        {"q": "Corps chromatoïde 'en cigare' typique de:", "options": ["E. histolytica", "E. coli", "Giardia", "Balantidium"], "answer": 0, "explanation": "E. histolytica = cigare. E. coli = pointu.", "category": "Morphologie"},
        {"q": "Protozoaire avec macro et micronoyau?", "options": ["Giardia", "Balantidium coli", "Trichomonas", "Entamoeba"], "answer": 1, "explanation": "Seul cilié pathogène humain.", "category": "Morphologie"},
        {"q": "Membrane ondulante caractéristique de:", "options": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "answer": 1, "explanation": "Trypanosoma = membrane ondulante + flagelle.", "category": "Morphologie"},
        {"q": "Gamétocyte en 'banane' typique de:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "Gamétocytes falciformes = pathognomoniques.", "category": "Hématozoaires"},
        {"q": "Kyste d'E. coli: combien de noyaux?", "options": ["4", "6", "8", "12"], "answer": 2, "explanation": "E. coli = 8 noyaux (vs 4 pour E. histolytica).", "category": "Morphologie"},
        {"q": "Le Métronidazole est inefficace contre:", "options": ["E. histolytica", "Giardia", "Helminthes", "Trichomonas"], "answer": 2, "explanation": "Anti-protozoaire. Pas anti-helminthique.", "category": "Thérapeutique"},
        {"q": "L'Albendazole est:", "options": ["Anti-protozoaire", "Anti-helminthique large spectre", "Antibiotique", "Antifongique"], "answer": 1, "explanation": "Large spectre: nématodes + cestodes.", "category": "Thérapeutique"},
        {"q": "Traitement du paludisme grave?", "options": ["Chloroquine", "Artésunate IV", "Métronidazole", "Praziquantel"], "answer": 1, "explanation": "Artésunate IV = 1ère ligne (OMS).", "category": "Thérapeutique"},
        {"q": "Ivermectine: indication principale?", "options": ["Filarioses/strongyloïdose", "Paludisme", "Amibiase", "Giardiose"], "answer": 0, "explanation": "Référence pour filarioses et strongyloïdose.", "category": "Thérapeutique"},
        {"q": "Patient d'Afrique: fièvre + frissons + accès?", "options": ["Amibiase", "Paludisme", "Bilharziose", "Giardiose"], "answer": 1, "explanation": "Paludisme jusqu'à preuve du contraire.", "category": "Cas clinique"},
        {"q": "Hématurie + baignade eau douce Afrique?", "options": ["Giardiose", "Paludisme", "Bilharziose urinaire", "Amibiase"], "answer": 2, "explanation": "S. haematobium = bilharziose urinaire.", "category": "Cas clinique"},
        {"q": "Diarrhée graisseuse chronique + malabsorption enfant?", "options": ["Amibiase", "Giardiose", "Cryptosporidiose", "Salmonellose"], "answer": 1, "explanation": "Giardia = cause fréquente de malabsorption.", "category": "Cas clinique"},
        {"q": "Chancre + adénopathies cervicales + somnolence?", "options": ["Paludisme", "Leishmaniose", "Trypanosomiase", "Toxoplasmose"], "answer": 2, "explanation": "THA = maladie du sommeil.", "category": "Cas clinique"},
        {"q": "Bouton ulcéré indolore retour du Sahara?", "options": ["Leishmaniose cutanée", "Furoncle", "Anthrax", "Mycose"], "answer": 0, "explanation": "Clou de Biskra = L. major.", "category": "Cas clinique"},
        {"q": "Bilharziose: contamination par:", "options": ["Ingestion d'eau", "Contact cutané eau douce", "Piqûre d'insecte", "Voie aérienne"], "answer": 1, "explanation": "Cercaires pénètrent la peau dans l'eau.", "category": "Épidémiologie"},
        {"q": "Niclosamide agit sur:", "options": ["Nématodes", "Cestodes (ténias)", "Trématodes", "Protozoaires"], "answer": 1, "explanation": "Spécifique des cestodes.", "category": "Thérapeutique"},
        {"q": "Goutte épaisse vs frottis mince:", "options": ["Même sensibilité", "GE 10x plus sensible", "FM plus sensible", "Pas comparable"], "answer": 1, "explanation": "GE = 10x plus sensible pour faibles parasitémies.", "category": "Techniques"},
        {"q": "Œufs de S. haematobium se cherchent dans:", "options": ["Selles du matin", "Urines de midi", "Sang nocturne", "LCR"], "answer": 1, "explanation": "Pic d'excrétion = midi.", "category": "Techniques"},
    ],
    "ar": [
        {"q": "أي طفيلي يُعرف بشكل 'الخاتم' في الكريات الحمراء؟", "options": ["الجيارديا", "البلازموديوم", "الليشمانيا", "الأميبا"], "answer": 1, "explanation": "البلازموديوم = شكل خاتم في الكريات.", "category": "دموية"},
        {"q": "كم نواة في كيس الجيارديا الناضج؟", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "4 نوى. الطور الغاذي = 2.", "category": "أوالي معوية"},
        {"q": "أي طفيلي ينتقل بذبابة الرمل؟", "options": ["البلازموديوم", "التريبانوسوما", "الليشمانيا", "البلهارسيا"], "answer": 2, "explanation": "الليشمانيا = فليبوتوم.", "category": "نسيجية"},
        {"q": "النتوء الطرفي يميز:", "options": ["الأسكاريس", "البلهارسيا الدموية", "البلهارسيا المنسونية", "الشريطية"], "answer": 1, "explanation": "S. haematobium = طرفي. S. mansoni = جانبي.", "category": "ديدان"},
        {"q": "الفحص العاجل للملاريا؟", "options": ["زرع براز", "فحص بول", "قطرة سميكة + لطاخة", "مصلية"], "answer": 2, "explanation": "قطرة سميكة + لطاخة = عاجل.", "category": "تشخيص"},
        {"q": "تقنية ريتشي هي:", "options": ["تلوين", "تركيز ثنائي الطور", "زرع", "مصلية"], "answer": 1, "explanation": "فورمول-إيثر = تركيز.", "category": "تقنيات"},
        {"q": "اللوغول يُظهر:", "options": ["الأسواط", "نوى الأكياس", "الكريات", "البكتيريا"], "answer": 1, "explanation": "اللوغول = غليكوجين + نوى.", "category": "تقنيات"},
        {"q": "الهدف ×100 يحتاج:", "options": ["ماء", "زيت غمر", "كحول", "محلول ملحي"], "answer": 1, "explanation": "زيت الأرز = معامل انكسار.", "category": "مجهرية"},
        {"q": "العرسة الموزية مميزة لـ:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "P. falciparum = عرسات موزية.", "category": "دموية"},
        {"q": "كيس E. coli الناضج:", "options": ["4 نوى", "6 نوى", "8 نوى", "12 نواة"], "answer": 2, "explanation": "E. coli = 8 (vs histolytica = 4).", "category": "مورفولوجيا"},
        {"q": "الغشاء المتموج مميز لـ:", "options": ["الجيارديا", "التريبانوسوما", "الليشمانيا", "البلازموديوم"], "answer": 1, "explanation": "التريبانوسوما = غشاء متموج.", "category": "مورفولوجيا"},
        {"q": "حمى + قشعريرة بعد العودة من أفريقيا:", "options": ["أميبيا", "ملاريا", "بلهارسيا", "جيارديا"], "answer": 1, "explanation": "ملاريا حتى يثبت العكس.", "category": "حالة سريرية"},
        {"q": "دم في البول + سباحة ماء عذب:", "options": ["جيارديا", "ملاريا", "بلهارسيا بولية", "أميبيا"], "answer": 2, "explanation": "S. haematobium.", "category": "حالة سريرية"},
        {"q": "الميترونيدازول غير فعال ضد:", "options": ["الأميبا", "الجيارديا", "الديدان", "المشعرات"], "answer": 2, "explanation": "مضاد أوالي فقط.", "category": "علاج"},
        {"q": "الألبندازول هو:", "options": ["مضاد أوالي", "مضاد ديدان واسع", "مضاد حيوي", "مضاد فطري"], "answer": 1, "explanation": "واسع الطيف: ديدان أسطوانية + شريطية.", "category": "علاج"},
    ],
    "en": [
        {"q": "Which parasite shows a 'signet ring' in RBCs?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Plasmodium = signet ring form.", "category": "Blood parasites"},
        {"q": "Mature Giardia cyst nuclei count?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "4 nuclei. Trophozoite has 2.", "category": "Intestinal protozoa"},
        {"q": "Sandfly-transmitted parasite?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania = phlebotomus.", "category": "Tissue protozoa"},
        {"q": "Terminal spine on egg of:", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "S. haematobium = terminal. S. mansoni = lateral.", "category": "Helminths"},
        {"q": "Urgent malaria test?", "options": ["Stool culture", "Urinalysis", "Thick + Thin smear", "Serology"], "answer": 2, "explanation": "Gold standard urgent test.", "category": "Diagnosis"},
        {"q": "Ritchie technique is:", "options": ["Staining", "Diphasic concentration", "Culture", "Serology"], "answer": 1, "explanation": "Formol-ether concentration.", "category": "Techniques"},
        {"q": "Lugol highlights:", "options": ["Flagella", "Cyst nuclei", "RBCs", "Bacteria"], "answer": 1, "explanation": "Iodine stains glycogen + nuclei.", "category": "Techniques"},
        {"q": "x100 objective requires:", "options": ["Water", "Immersion oil", "Alcohol", "Saline"], "answer": 1, "explanation": "Oil increases refractive index.", "category": "Microscopy"},
        {"q": "Banana-shaped gametocyte:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "P. falciparum pathognomonic.", "category": "Blood parasites"},
        {"q": "Mature E. coli cyst nuclei:", "options": ["4", "6", "8", "12"], "answer": 2, "explanation": "E. coli = 8 (vs histolytica = 4).", "category": "Morphology"},
        {"q": "Undulating membrane in:", "options": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "answer": 1, "explanation": "Trypanosoma = undulating membrane.", "category": "Morphology"},
        {"q": "Fever + chills from Africa:", "options": ["Amebiasis", "Malaria", "Schistosomiasis", "Giardiasis"], "answer": 1, "explanation": "Malaria until proven otherwise.", "category": "Clinical"},
        {"q": "Hematuria + freshwater swimming:", "options": ["Giardiasis", "Malaria", "Urinary schistosomiasis", "Amebiasis"], "answer": 2, "explanation": "S. haematobium.", "category": "Clinical"},
        {"q": "Metronidazole ineffective against:", "options": ["E. histolytica", "Giardia", "Helminths", "Trichomonas"], "answer": 2, "explanation": "Anti-protozoal only.", "category": "Therapeutics"},
        {"q": "Thick smear vs thin smear:", "options": ["Same sensitivity", "Thick 10x more sensitive", "Thin more sensitive", "Not comparable"], "answer": 1, "explanation": "Thick = 10x more sensitive.", "category": "Techniques"},
    ]
}


# ============================================
#  7. شات بوت ذكي - قاعدة معرفة شاملة
# ============================================
CHATBOT_KB = {
    "fr": {
        "amoeba": "🔬 **Entamoeba histolytica**\n\n**Morphologie:** Kyste 10-15μm (4 noyaux), Trophozoïte 20-40μm (hématophage)\n**Diagnostic:** EPS direct + Lugol, sérologie si abcès\n**Traitement:** Métronidazole + Intetrix\n**Distinction:** E. histolytica (pathogène) vs E. dispar (non pathogène) → PCR",
        "amibe": "🔬 Même réponse que Amoeba. Voir Entamoeba histolytica.",
        "giardia": "🔬 **Giardia lamblia**\n\n**Morphologie:** Cerf-volant (12-15μm), face de hibou, 4 paires flagelles\n**Diagnostic:** EPS + Lugol, Ag Giardia ELISA\n**Traitement:** Métronidazole 250mg x3/j (5j) OU Tinidazole 2g\n**Clinique:** Diarrhée graisseuse, malabsorption",
        "leishmania": "🔬 **Leishmania**\n\n**Morphologie:** Amastigotes 2-5μm dans macrophages (MGG)\n**Formes:** Cutanée (L. major), Viscérale (L. infantum)\n**En Algérie:** L. major (sud), L. infantum (nord) - MDO\n**Traitement:** Glucantime (cutanée), Amphotéricine B (viscérale)",
        "plasmodium": "🚨 **URGENCE - Plasmodium (Paludisme)**\n\n**Morphologie:** Bague à chaton, gamétocytes banane (P.f)\n**Diagnostic URGENT:** Frottis + Goutte épaisse (<2h!)\n**Seuil:** >2% = forme grave → HOSPITALISATION\n**Traitement:** ACT ou Artésunate IV\n**5 espèces:** P. falciparum (mortel), vivax, ovale, malariae, knowlesi",
        "malaria": "🚨 Même chose que Plasmodium. URGENCE MÉDICALE !",
        "paludisme": "🚨 Même chose que Plasmodium. URGENCE MÉDICALE !",
        "trypanosoma": "🔬 **Trypanosoma**\n\n**Morphologie:** Forme S/C (15-30μm), membrane ondulante, kinétoplaste\n**Maladies:** Sommeil (T. brucei, tsé-tsé), Chagas (T. cruzi)\n**Staging:** Ponction lombaire OBLIGATOIRE\n**Traitement:** Phase 1: Pentamidine. Phase 2: NECT/Mélarsoprol",
        "schistosoma": "🔬 **Schistosoma (Bilharziose)**\n\n**S. haematobium:** Éperon TERMINAL, urines MIDI\n**S. mansoni:** Éperon LATÉRAL, selles\n**Traitement:** Praziquantel 40mg/kg\n**Prévention:** Éviter eau douce en zone d'endémie",
        "bilharziose": "Même chose que Schistosoma.",
        "microscope": "🔬 **Microscopie en Parasitologie:**\n\n• **x10:** Repérage\n• **x40:** Identification œufs/kystes\n• **x100 (immersion):** Détails (Plasmodium, Leishmania)\n\n**Types:** Optique, fluorescence, contraste de phase, fond noir",
        "coloration": "🎨 **Colorations:**\n\n• **Lugol:** Noyaux des kystes\n• **MGG/Giemsa:** Parasites sanguins\n• **Ziehl-Neelsen modifié:** Cryptosporidium\n• **Trichrome:** Microsporidies",
        "selle": "💩 **EPS Complet:**\n\n1. Macroscopique\n2. Direct (NaCl + Lugol)\n3. Concentration (Ritchie/Willis)\n\n⚠️ Examiner dans 30 min! Répéter x3!",
        "sang": "🩸 **Parasites sanguins:**\n\n• Frottis mince + Goutte épaisse (MGG)\n• TDR (tests rapides)\n• Recherche selon périodicité (filaires)",
        "hygiene": "🧼 **Prévention:**\n\n✅ Lavage des mains\n✅ Eau potable\n✅ Cuisson viande >65°C\n✅ Moustiquaires\n✅ Éviter eaux stagnantes",
        "concentration": "🧪 **Techniques de concentration:**\n\n• **Ritchie:** Formol-éther (référence)\n• **Willis:** Flottation NaCl\n• **Kato-Katz:** Semi-quantitatif\n• **Baermann:** Larves Strongyloides",
        "ascaris": "🪱 **Ascaris lumbricoides:**\n\nŒuf mamelonné (60-70μm), ver 15-30cm\nTraitement: Albendazole 400mg dose unique",
        "taenia": "🪱 **Taenia:**\n\n• T. saginata (bœuf, inerme)\n• T. solium (porc, armé + risque cysticercose)\nTraitement: Niclosamide ou Praziquantel",
        "toxoplasma": "🔬 **Toxoplasma gondii:**\n\nChat = hôte définitif\n⚠️ Danger: femme enceinte séronégative\nDiagnostic: Sérologie IgG/IgM",
        "oxyure": "🪱 **Enterobius (Oxyure):**\n\nPrurit anal nocturne. Scotch-test matin.\nTraitement: Flubendazole, toute la famille!",
        "cryptosporidium": "🔬 **Cryptosporidium:**\n\nOpportuniste VIH+. Oocystes 4-6μm.\nDiagnostic: Ziehl-Neelsen modifié\nTraitement: Nitazoxanide",
        "bonjour": "👋 Bonjour! Je suis **Dr. DhiaBot**, votre assistant parasitologique.\n\n🔬 Parasites | 💊 Traitements | 🧪 Techniques | 🩺 Cas cliniques\n\nQue voulez-vous savoir?",
        "salut": "Salut! 😊 Comment puis-je vous aider en parasitologie?",
        "merci": "De rien! 😊 La parasitologie est ma passion!",
        "aide": "📚 **Je connais:**\n\nAmoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Oxyure, Cryptosporidium...\n\nEt: microscopie, colorations, concentration, EPS, diagnostic, traitements, épidémiologie, hygiène!\n\n💡 Tapez un mot-clé!",
        "qui es tu": "🤖 Je suis **Dr. DhiaBot** v6.0! Développé par {dev1} et {dev2} à l'INFSPM Ouargla.",
    },
    "ar": {
        "أميبا": "🔬 **الأميبا الحالّة للنسج**\n\nكيس 10-15μm (4 نوى)، طور غاذي 20-40μm (يبتلع الكريات)\nالعلاج: ميترونيدازول + إنتيتريكس",
        "جيارديا": "🔬 **الجيارديا**\n\nشكل طائرة ورقية، وجه بومة\nالعلاج: ميترونيدازول أو تينيدازول",
        "ليشمانيا": "🔬 **الليشمانيا**\n\nلامسوطات داخل البلاعم (MGG)\nفي الجزائر: L. major (جنوب)، L. infantum (شمال)",
        "ملاريا": "🚨 **حالة طوارئ!**\n\nقطرة سميكة + لطاخة عاجل!\nالعلاج: ACT",
        "بلهارسيا": "🔬 **البلهارسيا**\n\nhaematobium: نتوء طرفي، بول\nmansoni: نتوء جانبي، براز",
        "مرحبا": "مرحباً! 👋 أنا **الدكتور ضياء بوت**. كيف أساعدك؟",
        "مجهر": "🔬 x10: استكشاف | x40: تحديد | x100: تفاصيل دقيقة",
        "تلوين": "🎨 لوغول: نوى | MGG: دم | زيل-نيلسن: كريبتوسبوريديوم",
        "مساعدة": "📚 أعرف كل الطفيليات وتقنيات المخبر. اكتب اسم الطفيلي!",
    },
    "en": {
        "amoeba": "🔬 **E. histolytica**\n\nCyst 10-15μm (4 nuclei), Trophozoite 20-40μm (RBC phagocytosis)\nTreatment: Metronidazole + contact amoebicide",
        "giardia": "🔬 **Giardia**\n\nKite shape, owl face, 4 flagella pairs\nTreatment: Metronidazole or Tinidazole",
        "leishmania": "🔬 **Leishmania**\n\nAmastigotes in macrophages (MGG)\nCutaneous / Visceral forms",
        "malaria": "🚨 **EMERGENCY!**\n\nThick + Thin smear URGENT!\nTreatment: ACT",
        "plasmodium": "🚨 Same as Malaria. EMERGENCY!",
        "schistosoma": "🔬 **Schistosoma**\n\nhaematobium: terminal spine, urine\nmansoni: lateral spine, stool",
        "hello": "Hello! 👋 I'm **Dr. DhiaBot**. How can I help?",
        "microscope": "🔬 x10: scan | x40: identify | x100: details",
        "help": "📚 I know all parasites and lab techniques. Type a keyword!",
    }
}


def chatbot_reply(user_msg, lang="fr"):
    kb = CHATBOT_KB.get(lang, CHATBOT_KB["fr"])
    msg_lower = user_msg.lower().strip()

    # Direct keyword match
    for key, response in kb.items():
        if key in msg_lower:
            resp = response.replace("{dev1}", AUTHORS["dev1"]["name"]).replace("{dev2}", AUTHORS["dev2"]["name"])
            return resp

    # Search in PARASITE_DB
    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if name.lower() in msg_lower or data["scientific_name"].lower() in msg_lower:
            morpho = get_p_text(data, "morphology")
            desc = get_p_text(data, "description")
            advice = get_p_text(data, "advice")
            funny = get_p_text(data, "funny")
            return f"**{name}** ({data['scientific_name']})\n\n📋 {desc}\n\n🔬 {morpho}\n\n💊 {advice}\n\n🤖 {funny}"

    # Default
    defaults = {
        "fr": "🤖 Je suis Dr. DhiaBot. Tapez un mot-clé (amoeba, giardia, microscope, aide...)",
        "ar": "🤖 أنا الدكتور ضياء بوت. اكتب كلمة مفتاحية (أميبا، جيارديا، مجهر، مساعدة...)",
        "en": "🤖 I'm Dr. DhiaBot. Type a keyword (amoeba, giardia, microscope, help...)"
    }
    return defaults.get(lang, defaults["fr"])


DAILY_TIPS = {
    "fr": [
        "💡 Examiner les selles dans les 30 min pour voir les trophozoïtes mobiles.",
        "💡 Le Lugol met en évidence les noyaux des kystes. Dilution fraîche chaque semaine.",
        "💡 Frottis mince: angle 45° pour une monocouche parfaite.",
        "💡 La goutte épaisse est 10x plus sensible que le frottis mince.",
        "💡 Urines de midi pour S. haematobium (pic d'excrétion).",
        "💡 Répéter l'EPS x3 à quelques jours d'intervalle (sensibilité 50-60% pour un seul).",
        "💡 Métronidazole = Amoeba + Giardia + Trichomonas. Retenir ce trio!",
        "💡 Ziehl-Neelsen modifié est indispensable pour Cryptosporidium.",
        "💡 En paludisme: 1ère GE négative ne suffit pas. Répéter à 6-12h.",
        "💡 Le phlébotome est actif au crépuscule. Moustiquaires!",
        "💡 Éosinophilie = helminthiase probable. Toujours vérifier!",
        "💡 Technique de Baermann = spécifique pour larves de Strongyloides.",
        "💡 E. coli 8 noyaux vs E. histolytica 4 noyaux = critère n°1.",
        "💡 Selles liquides → trophozoïtes. Selles formées → kystes.",
        "💡 PCR = gold standard pour identifier l'espèce de Leishmania.",
    ],
    "ar": [
        "💡 افحص البراز خلال 30 دقيقة لرؤية الأطوار المتحركة.",
        "💡 اللوغول يُظهر نوى الأكياس. تحضير طازج أسبوعياً.",
        "💡 القطرة السميكة أكثر حساسية 10 مرات من اللطاخة.",
        "💡 بول الظهيرة لـ S. haematobium (ذروة الإفراز).",
        "💡 كرر فحص البراز × 3 لزيادة الحساسية.",
        "💡 E. coli = 8 نوى مقابل E. histolytica = 4 نوى.",
        "💡 ارتفاع الحمضات = ديدان محتملة. تحقق دائماً!",
    ],
    "en": [
        "💡 Examine stool within 30 min for motile trophozoites.",
        "💡 Lugol highlights cyst nuclei. Fresh dilution weekly.",
        "💡 Thick smear is 10x more sensitive than thin smear.",
        "💡 Midday urine for S. haematobium eggs.",
        "💡 Repeat stool x3 for better sensitivity.",
        "💡 Eosinophilia = likely helminthiasis. Always check!",
    ]
}


# ============================================
#  8. Session State
# ============================================
SESSION_DEFAULTS = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_role": "viewer",
    "user_full_name": "",
    "intro_step": 0,
    "dark_mode": True,
    "lang": "fr",
    "last_activity": None,
    "splash_shown": False,
    "balloons_shown": False,
    "demo_seed": None,
    "heatmap_seed": None,
    "quiz_state": {"current": 0, "score": 0, "answered": [], "active": False},
    "chat_history": [],
}

for key, val in SESSION_DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val


# ============================================
#  9. Helper Functions
# ============================================
def t(key):
    lang = st.session_state.get("lang", "fr")
    tr = TRANSLATIONS.get(lang, TRANSLATIONS["fr"])
    return tr.get(key, TRANSLATIONS["fr"].get(key, key))

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
    g = {"fr": ("Bonjour","Bon après-midi","Bonsoir"), "ar": ("صباح الخير","مساء الخير","مساء الخير"), "en": ("Good morning","Good afternoon","Good evening")}
    greet = g.get(lang, g["fr"])
    return greet[0] if h < 12 else greet[1] if h < 18 else greet[2]

def risk_color(level):
    return {"critical":"#ff0040","high":"#ff3366","medium":"#ff9500","low":"#00e676","none":"#00ff88"}.get(level,"#888")

def risk_percent(level):
    return {"critical":100,"high":80,"medium":50,"low":25,"none":0}.get(level,0)

def user_has_role(min_level):
    role = st.session_state.get("user_role", "viewer")
    return ROLES.get(role, {}).get("level", 0) >= min_level

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
        st.markdown(f'<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,{b64}" type="audio/mpeg"></audio>', unsafe_allow_html=True)
        try: os.remove(fname)
        except: pass
    except ImportError:
        safe = text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
        jl = {"fr":"fr-FR","ar":"ar-SA","en":"en-US"}.get(lang_code,"fr-FR")
        st.markdown(f"<script>try{{var m=new SpeechSynthesisUtterance('{safe}');m.lang='{jl}';m.rate=0.9;speechSynthesis.speak(m);}}catch(e){{}}</script>", unsafe_allow_html=True)
    except: pass

def check_auto_lock():
    if st.session_state.last_activity:
        elapsed = (datetime.now() - st.session_state.last_activity).total_seconds() / 60
        if elapsed > AUTO_LOCK_MINUTES:
            if st.session_state.user_id:
                db_log_activity(st.session_state.user_id, st.session_state.user_name, "Auto-locked")
            st.session_state.logged_in = False
            st.session_state.intro_step = 0
            st.rerun()


# ============================================
#  10. AI Engine
# ============================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    model, model_name, model_type = None, None, None
    try:
        import tensorflow as tf
        files = os.listdir(".") if os.path.exists(".") else []
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
    except: pass
    return model, model_name, model_type


def predict_image(model, model_type, image, demo_seed=None):
    result = {"label":"Negative","confidence":0,"all_predictions":{},"is_reliable":False,"is_demo":False,"risk_level":"none"}

    if model is None:
        result["is_demo"] = True
        if demo_seed is None:
            demo_seed = random.randint(0, 999999)
        rng = random.Random(demo_seed)
        label = rng.choice(CLASS_NAMES)
        conf = rng.randint(55, 98)
        all_p = {}
        rem = 100.0 - conf
        for cls in CLASS_NAMES:
            if cls == label:
                all_p[cls] = float(conf)
            else:
                v = round(rng.uniform(0, rem / max(1, len(CLASS_NAMES)-1)), 1)
                all_p[cls] = v
        risk_map = {"Plasmodium":"critical","Amoeba (E. histolytica)":"high","Leishmania":"high","Trypanosoma":"high","Giardia":"medium","Schistosoma":"medium","Negative":"none"}
        result.update({"label":label,"confidence":conf,"all_predictions":all_p,"is_reliable":conf>=CONFIDENCE_THRESHOLD,"risk_level":risk_map.get(label,"none")})
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
        all_p = {CLASS_NAMES[i]: round(float(preds[i])*100, 1) for i in range(min(len(preds), len(CLASS_NAMES)))}
        risk_map = {"Plasmodium":"critical","Amoeba (E. histolytica)":"high","Leishmania":"high","Trypanosoma":"high","Giardia":"medium","Schistosoma":"medium","Negative":"none"}
        result.update({"label":label,"confidence":conf,"all_predictions":all_p,"is_reliable":conf>=CONFIDENCE_THRESHOLD,"risk_level":risk_map.get(label,"none")})
    except Exception as e:
        st.error(f"Prediction error: {e}")
    return result


# ============================================
#  11. Image Analysis Functions
# ============================================
def generate_heatmap(model, model_type, image, seed=None):
    # Try real Grad-CAM first
    if model is not None and model_type == "keras":
        try:
            return _real_gradcam(model, image)
        except: pass
    return _pseudo_heatmap(image, seed)

def _real_gradcam(model, image):
    import tensorflow as tf
    img = ImageOps.fit(image.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32) / 127.5 - 1.0
    batch = np.expand_dims(arr, 0)
    last_conv = None
    for layer in reversed(model.layers):
        if len(layer.output_shape) == 4:
            last_conv = layer.name
            break
    if not last_conv:
        return _pseudo_heatmap(image)
    grad_model = tf.keras.Model(inputs=model.input, outputs=[model.get_layer(last_conv).output, model.output])
    with tf.GradientTape() as tape:
        conv_out, preds = grad_model(batch)
        loss = preds[:, tf.argmax(preds[0])]
    grads = tape.gradient(loss, conv_out)
    pooled = tf.reduce_mean(grads, axis=(0,1,2))
    hm = conv_out[0] @ pooled[..., tf.newaxis]
    hm = tf.squeeze(hm)
    hm = tf.maximum(hm, 0) / (tf.math.reduce_max(hm) + 1e-8)
    hm_img = Image.fromarray(np.uint8(hm.numpy()*255)).resize(image.size, Image.LANCZOS)
    hm_arr = np.array(hm_img)
    colored = np.zeros((*hm_arr.shape, 3), dtype=np.uint8)
    n = hm_arr.astype(float)/255.0
    colored[...,0] = np.uint8(np.clip(n*4-2,0,1)*255)
    colored[...,1] = np.uint8(np.clip(np.minimum(n*4,4-n*4),0,1)*255)
    colored[...,2] = np.uint8(np.clip(1-n*4,0,1)*255)
    hm_color = Image.fromarray(colored).resize(image.size, Image.LANCZOS)
    return Image.blend(image.convert("RGB"), hm_color, 0.4)

def _pseudo_heatmap(image, seed=None):
    img = image.copy().convert("RGB")
    w, h = img.size
    if seed is None:
        seed = hash(img.tobytes()[:1000]) % 1000000
    rng = random.Random(seed)
    gray = ImageOps.grayscale(img)
    edges = gray.filter(ImageFilter.FIND_EDGES)
    ea = np.array(edges)
    bs = 32
    mx, best_cx, best_cy = 0, w//2, h//2
    for y in range(0, h-bs, bs//2):
        for x in range(0, w-bs, bs//2):
            s = np.mean(ea[y:y+bs, x:x+bs])
            if s > mx:
                mx, best_cx, best_cy = s, x+bs//2, y+bs//2
    best_cx += rng.randint(-w//10, w//10)
    best_cy += rng.randint(-h//10, h//10)
    best_cx, best_cy = max(50, min(w-50, best_cx)), max(50, min(h-50, best_cy))
    heatmap = Image.new('RGBA', (w, h), (0,0,0,0))
    draw = ImageDraw.Draw(heatmap)
    max_r = min(w, h) // 3
    for r in range(max_r, 0, -2):
        alpha = max(0, min(200, int(200*(1-r/max_r))))
        ratio = r/max_r
        if ratio > 0.65: color = (0,255,100,alpha//4)
        elif ratio > 0.35: color = (255,255,0,alpha//2)
        else: color = (255,0,60,alpha)
        draw.ellipse([best_cx-r, best_cy-r, best_cx+r, best_cy+r], fill=color)
    for _ in range(rng.randint(2,4)):
        sx, sy = rng.randint(w//4, 3*w//4), rng.randint(h//4, 3*h//4)
        sr = rng.randint(20, max_r//3)
        for r in range(sr, 0, -3):
            a = max(0, int(80*(1-r/sr)))
            draw.ellipse([sx-r, sy-r, sx+r, sy+r], fill=(255,200,0,a))
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

def apply_sharpen(image):
    return image.filter(ImageFilter.SHARPEN)

def apply_denoise(image):
    return image.filter(ImageFilter.GaussianBlur(radius=2))

def apply_adjustments(image, brightness=1.0, contrast=1.0, saturation=1.0):
    img = image.copy()
    if brightness != 1.0: img = ImageEnhance.Brightness(img).enhance(brightness)
    if contrast != 1.0: img = ImageEnhance.Contrast(img).enhance(contrast)
    if saturation != 1.0: img = ImageEnhance.Color(img).enhance(saturation)
    return img

def zoom_image(image, level, cx=50, cy=50):
    if level <= 1.0: return image
    w, h = image.size
    nw, nh = int(w/level), int(h/level)
    px, py = int(w*cx/100), int(h*cy/100)
    l, t = max(0, px-nw//2), max(0, py-nh//2)
    r, b = min(w, l+nw), min(h, t+nh)
    return image.crop((l, t, r, b)).resize((w, h), Image.LANCZOS)

def compare_images(img1, img2):
    a1 = np.array(img1.convert("RGB").resize((128,128))).astype(float)
    a2 = np.array(img2.convert("RGB").resize((128,128))).astype(float)
    mse = np.mean((a1-a2)**2)
    mu1, mu2 = np.mean(a1), np.mean(a2)
    s1, s2 = np.std(a1), np.std(a2)
    s12 = np.mean((a1-mu1)*(a2-mu2))
    c1, c2 = (0.01*255)**2, (0.03*255)**2
    ssim = ((2*mu1*mu2+c1)*(2*s12+c2)) / ((mu1**2+mu2**2+c1)*(s1**2+s2**2+c2))
    return {"mse": round(mse,2), "ssim": round(float(ssim),4), "similarity": round(float(ssim)*100,1)}

def get_histogram_data(image):
    r, g, b = image.convert("RGB").split()
    return {"red": list(r.histogram()), "green": list(g.histogram()), "blue": list(b.histogram())}


# ============================================
#  12. PDF Generator (QR + Signature)
# ============================================
def _safe_pdf(text):
    if not text: return ""
    reps = {'é':'e','è':'e','ê':'e','ë':'e','à':'a','â':'a','ä':'a','ù':'u','û':'u','ü':'u','ô':'o','ö':'o','î':'i','ï':'i','ç':'c','É':'E','È':'E','Ê':'E','À':'A','Ù':'U','Ô':'O','Î':'I','Ç':'C','→':'->','←':'<-','°':'o','µ':'u','×':'x','🔴':'[!]','🟠':'[!]','🟢':'[OK]','🚨':'[!!!]'}
    for o, r in reps.items():
        text = text.replace(o, r)
    result = []
    for ch in text:
        try:
            ch.encode('latin-1')
            result.append(ch)
        except: result.append('?')
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
        self.line(10, self.get_y()+1, 200, self.get_y()+1)
        self.ln(2)
        self.set_font("Arial", "", 7)
        self.cell(0, 4, f"DM Smart Lab AI v{APP_VERSION} | INFSPM Ouargla", 0, 0, "L")
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}}", 0, 0, "R")

    def section(self, title, color=(0,60,150)):
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


def generate_pdf(patient, lab, result, info):
    pdf = ProPDF()
    pdf.alias_nb_pages()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 60, 150)
    pdf.cell(0, 12, _safe_pdf(t("pdf_title")), 0, 1, "C")
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, _safe_pdf(t("pdf_subtitle")), 0, 1, "C")

    # Report ID
    rid = hashlib.md5(f"{patient.get('nom','')}{datetime.now().isoformat()}".encode()).hexdigest()[:10].upper()
    pdf.set_font("Arial", "B", 8)
    pdf.set_text_color(0, 100, 200)
    pdf.cell(0, 5, f"Ref: DM-{rid}", 0, 1, "R")
    pdf.ln(3)

    # Patient
    pdf.section("INFORMATIONS DU PATIENT")
    for k, v in patient.items():
        pdf.field(f"{k}:", v)
    pdf.field("Date:", datetime.now().strftime("%d/%m/%Y"))
    pdf.ln(2)

    # Lab
    pdf.section("INFORMATIONS DU LABORATOIRE", (0, 100, 80))
    for k, v in lab.items():
        if v: pdf.field(f"{k}:", v)
    pdf.ln(2)

    # Result
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

    if info:
        pdf.set_font("Arial", "", 9)
        m = get_p_text(info, 'morphology')
        pdf.multi_cell(0, 5, _safe_pdf(f"Morphologie: {m}"))
        pdf.ln(1)
        d = get_p_text(info, 'description')
        pdf.multi_cell(0, 5, _safe_pdf(f"Description: {d}"))
    pdf.ln(3)

    # Advice
    pdf.section("RECOMMANDATIONS CLINIQUES", (0, 130, 0))
    pdf.set_font("Arial", "", 9)
    if info:
        pdf.multi_cell(0, 5, _safe_pdf(get_p_text(info, "advice")))
        pdf.ln(2)
        extra = get_p_text(info, "extra_tests")
        if isinstance(extra, list) and extra:
            pdf.set_font("Arial", "B", 9)
            pdf.cell(0, 6, "Examens complementaires:", 0, 1)
            pdf.set_font("Arial", "", 9)
            for test in extra:
                pdf.cell(0, 5, _safe_pdf(f"  - {test}"), 0, 1)
    pdf.ln(3)

    # QR Code
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
            try: os.remove(qr_path)
            except: pass
        except: pass

    # Signatures
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
#  13. FUTURISTIC NEON THEME CSS
# ============================================
def apply_futuristic_theme():
    dm = st.session_state.get("dark_mode", True)

    if dm:
        bg = "#030614"
        bg2 = "#0a0f2e"
        card_bg = "rgba(10,15,46,0.85)"
        card_border = "rgba(0,245,255,0.15)"
        text = "#e0e8ff"
        muted = "#6b7fa0"
        primary = "#00f5ff"
        primary_glow = "rgba(0,245,255,0.15)"
        accent = "#ff00ff"
        accent2 = "#00ff88"
        sidebar_bg = "#020410"
        sidebar_border = "rgba(0,245,255,0.1)"
        input_bg = "#0a0f2e"
        input_border = "rgba(0,245,255,0.2)"
        shadow = "rgba(0,245,255,0.08)"
        btn_grad = "linear-gradient(135deg, #00f5ff, #0066ff)"
        btn_shadow = "rgba(0,245,255,0.4)"
        danger = "#ff0040"
        warning = "#ff9500"
        success = "#00ff88"
        grid_color = "rgba(0,245,255,0.04)"
        scan_line = "rgba(0,245,255,0.06)"
    else:
        bg = "#f0f4f8"
        bg2 = "#ffffff"
        card_bg = "rgba(255,255,255,0.9)"
        card_border = "rgba(0,100,255,0.12)"
        text = "#0f172a"
        muted = "#64748b"
        primary = "#0066ff"
        primary_glow = "rgba(0,100,255,0.1)"
        accent = "#9933ff"
        accent2 = "#00cc66"
        sidebar_bg = "#f8fafc"
        sidebar_border = "rgba(0,100,255,0.1)"
        input_bg = "#ffffff"
        input_border = "#e2e8f0"
        shadow = "rgba(0,0,0,0.06)"
        btn_grad = "linear-gradient(135deg, #0066ff, #0044cc)"
        btn_shadow = "rgba(0,100,255,0.3)"
        danger = "#dc2626"
        warning = "#f59e0b"
        success = "#16a34a"
        grid_color = "rgba(0,100,255,0.04)"
        scan_line = "rgba(0,100,255,0.03)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&display=swap');

    html, body, [class*="css"], p, span, label, div, li, td, th {{
        font-family: 'Inter', sans-serif !important;
        color: {text} !important;
    }}
    h1 {{ font-family: 'Orbitron', sans-serif !important; font-size:2.2rem !important; font-weight:800 !important; letter-spacing:0.05em; }}
    h2 {{ font-family: 'Orbitron', sans-serif !important; font-size:1.5rem !important; font-weight:700 !important; }}
    h3 {{ font-size:1.2rem !important; font-weight:700 !important; }}

    .stApp {{
        background: {bg};
        background-image:
            radial-gradient(ellipse at 20% 50%, rgba(0,100,255,0.05) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(153,51,255,0.04) 0%, transparent 50%);
        background-attachment: fixed;
    }}
    .stApp::before {{
        content:''; position:fixed; top:0;left:0;right:0;bottom:0;
        background-image:
            linear-gradient({grid_color} 1px, transparent 1px),
            linear-gradient(90deg, {grid_color} 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events:none; z-index:0;
    }}
    .stApp::after {{
        content:''; position:fixed; top:0; left:0; right:0; height:2px;
        background: {scan_line};
        animation: scanLine 8s linear infinite;
        pointer-events:none; z-index:1;
    }}
    @keyframes scanLine {{
        0% {{ top: 0; }} 100% {{ top: 100vh; }}
    }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sidebar_bg}, {bg}) !important;
        border-right: 1px solid {sidebar_border} !important;
    }}

    .dm-card {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 4px 30px {shadow};
        position: relative;
        z-index: 2;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .dm-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 8px 40px {shadow}, 0 0 20px {primary_glow};
        border-color: {primary};
    }}
    .dm-card-cyan {{ border-left: 3px solid {primary}; }}
    .dm-card-magenta {{ border-left: 3px solid {accent}; }}
    .dm-card-green {{ border-left: 3px solid {accent2}; }}
    .dm-card-red {{ border-left: 3px solid {danger}; }}
    .dm-card-orange {{ border-left: 3px solid {warning}; }}

    .dm-metric {{
        background: {card_bg};
        backdrop-filter: blur(15px);
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 20px 14px;
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    .dm-metric::before {{
        content:''; position:absolute; top:0;left:0;right:0; height:2px;
        background: linear-gradient(90deg, {primary}, {accent});
    }}
    .dm-metric:hover {{
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 0 25px {primary_glow};
    }}
    .dm-metric-icon {{ font-size:1.6rem; margin-bottom:6px; display:block; }}
    .dm-metric-val {{
        font-size:1.8rem; font-weight:800;
        font-family:'JetBrains Mono',monospace !important;
        background: linear-gradient(135deg, {primary}, {accent});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .dm-metric-lbl {{
        font-size:0.7rem; font-weight:600; color:{muted} !important;
        text-transform:uppercase; letter-spacing:0.1em; margin-top:6px;
    }}

    div.stButton > button {{
        background: {btn_grad} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em;
        transition: all 0.35s ease !important;
        box-shadow: 0 4px 15px {btn_shadow} !important;
    }}
    div.stButton > button:hover {{
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 8px 30px {btn_shadow} !important;
    }}

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {{
        background: {input_bg} !important;
        border: 1px solid {input_border} !important;
        border-radius: 10px !important;
        color: {text} !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {primary} !important;
        box-shadow: 0 0 0 3px {primary_glow} !important;
    }}

    .dm-neon-title {{
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        background: linear-gradient(135deg, {primary}, {accent}, {accent2});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 0 40px {primary_glow};
        animation: neonPulse 3s ease-in-out infinite;
    }}
    @keyframes neonPulse {{
        0%, 100% {{ filter: brightness(1); }}
        50% {{ filter: brightness(1.2); }}
    }}

    .dm-glow-border {{
        position: relative;
    }}
    .dm-glow-border::after {{
        content: '';
        position: absolute;
        top: -1px; left: -1px; right: -1px; bottom: -1px;
        background: linear-gradient(45deg, {primary}, {accent}, {accent2}, {primary});
        background-size: 400% 400%;
        border-radius: 17px;
        z-index: -1;
        animation: glowRotate 4s linear infinite;
        opacity: 0.5;
        filter: blur(4px);
    }}
    @keyframes glowRotate {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    .dm-step {{
        display:flex; align-items:center; gap:10px;
        padding:12px 18px; border-radius:12px; margin:6px 0;
        font-weight:600; font-size:0.88rem;
        transition: all 0.3s ease;
    }}
    .dm-step-done {{ background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.3); color:{accent2} !important; }}
    .dm-step-active {{ background:{primary_glow}; border:1px solid rgba(0,245,255,0.3); color:{primary} !important; animation:stepGlow 2s infinite; }}
    .dm-step-pending {{ background:rgba(100,116,139,0.05); border:1px solid rgba(100,116,139,0.15); color:{muted} !important; }}
    @keyframes stepGlow {{ 0%,100%{{box-shadow:0 0 0 0 {primary_glow};}} 50%{{box-shadow:0 0 15px {primary_glow};}} }}

    .dm-chat-msg {{
        padding:14px 18px; border-radius:16px; margin:8px 0;
        max-width:85%; line-height:1.6; font-size:0.92rem;
    }}
    .dm-chat-user {{
        background:{btn_grad}; color:white !important;
        margin-left:auto; border-bottom-right-radius:4px;
    }}
    .dm-chat-user * {{ color:white !important; }}
    .dm-chat-bot {{
        background:{card_bg}; border:1px solid {card_border};
        border-bottom-left-radius:4px;
    }}

    .dm-logo-wrap {{ display:flex; flex-direction:column; align-items:center; padding:20px 0 12px; z-index:5; position:relative; }}
    .dm-logo-main {{ display:flex; align-items:center; gap:6px; animation:logoFloat 4s ease-in-out infinite; }}
    .dm-logo-char {{ font-family:'Orbitron',sans-serif; font-size:3.2rem; font-weight:900; }}
    .dm-logo-d {{
        background: linear-gradient(135deg, {primary}, {accent});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 20px {primary_glow});
    }}
    .dm-logo-m {{
        color: white;
        background: {btn_grad};
        padding: 4px 16px;
        border-radius: 10px;
        box-shadow: 0 0 20px {btn_shadow};
    }}
    .dm-logo-tag {{
        font-family:'Orbitron',sans-serif;
        font-size:0.7rem; font-weight:600; color:{muted};
        letter-spacing:0.35em; text-transform:uppercase; margin-top:8px;
    }}
    .dm-logo-line {{
        width:60px; height:2px;
        background: linear-gradient(90deg, {primary}, {accent});
        border-radius:2px; margin-top:6px;
        box-shadow: 0 0 10px {primary_glow};
    }}
    @keyframes logoFloat {{
        0%,100%{{transform:translateY(0);}} 50%{{transform:translateY(-5px);}}
    }}

    .dm-particle {{
        position:fixed; pointer-events:none; z-index:0; opacity:0;
        font-size:1.5rem; animation:particleRise 25s linear infinite;
    }}
    @keyframes particleRise {{
        0%{{transform:translateY(105vh) rotate(0);opacity:0;}}
        8%{{opacity:0.06;}} 92%{{opacity:0.06;}}
        100%{{transform:translateY(-10vh) rotate(360deg);opacity:0;}}
    }}

    @media (max-width:768px) {{
        .dm-logo-char {{ font-size:2.5rem; }}
        .dm-card {{ padding:16px; }}
        .dm-metric-val {{ font-size:1.3rem; }}
    }}
    </style>

    <div class="dm-particle" style="left:5%">🧬</div>
    <div class="dm-particle" style="left:18%;animation-delay:5s">🦠</div>
    <div class="dm-particle" style="left:35%;animation-delay:10s">🔬</div>
    <div class="dm-particle" style="left:52%;animation-delay:3s">💊</div>
    <div class="dm-particle" style="left:70%;animation-delay:8s">🧪</div>
    <div class="dm-particle" style="left:85%;animation-delay:13s">🧫</div>
    """, unsafe_allow_html=True)

apply_futuristic_theme()


# ============================================
#  14. SPLASH + AUTO-LOCK
# ============================================
if not st.session_state.get("splash_shown", False):
    st.markdown("""
    <div style="position:fixed;top:0;left:0;right:0;bottom:0;background:#030614;z-index:9999;display:flex;flex-direction:column;justify-content:center;align-items:center;animation:splashOut 0.5s ease 3s forwards;">
        <div style="font-size:5rem;animation:splashPulse 1.5s ease-in-out infinite;">🧬</div>
        <h2 style="font-family:Orbitron,sans-serif;background:linear-gradient(135deg,#00f5ff,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-top:16px;">DM SMART LAB AI</h2>
        <p style="opacity:0.3;letter-spacing:0.4em;text-transform:uppercase;font-size:0.7rem;font-family:Orbitron,sans-serif;">v6.0 Professional Edition</p>
        <div style="width:180px;height:2px;background:rgba(100,100,100,0.2);border-radius:2px;margin-top:20px;overflow:hidden;">
            <div style="width:100%;height:100%;background:linear-gradient(90deg,#00f5ff,#ff00ff);animation:loadBar 2.5s ease forwards;transform-origin:left;"></div>
        </div>
    </div>
    <style>
    @keyframes splashOut {{ to {{ opacity:0; pointer-events:none; }} }}
    @keyframes splashPulse {{ 0%,100%{{transform:scale(1);opacity:0.8;}} 50%{{transform:scale(1.15);opacity:1;}} }}
    @keyframes loadBar {{ from{{transform:scaleX(0);}} to{{transform:scaleX(1);}} }}
    </style>
    """, unsafe_allow_html=True)
    st.session_state.splash_shown = True

if st.session_state.logged_in:
    check_auto_lock()

# Logo
st.markdown("""
<div class="dm-logo-wrap">
    <div class="dm-logo-main">
        <span class="dm-logo-char dm-logo-d">D</span>
        <span class="dm-logo-char dm-logo-m">M</span>
    </div>
    <div class="dm-logo-tag">Smart Lab AI • v6.0</div>
    <div class="dm-logo-line"></div>
</div>
""", unsafe_allow_html=True)


# ============================================
#  15. LOGIN SYSTEM (Database + Roles)
# ============================================
if not st.session_state.logged_in:
    _, col_login, _ = st.columns([1.2, 2, 1.2])
    with col_login:
        st.markdown(f"""
        <div class='dm-card dm-card-cyan dm-glow-border' style='text-align:center;'>
            <div style='font-size:3rem; margin-bottom:10px;'>🔐</div>
            <h2 class='dm-neon-title'>{t('login_title')}</h2>
            <p style='opacity:0.5;'>{t('login_subtitle')}</p>
        </div>""", unsafe_allow_html=True)

        lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
        sel_lang = st.selectbox(f"🌍 {t('language')}", list(lang_opts.keys()),
                                index=list(lang_opts.values()).index(st.session_state.lang))
        if lang_opts[sel_lang] != st.session_state.lang:
            st.session_state.lang = lang_opts[sel_lang]
            st.rerun()

        with st.form("login_form"):
            user_input = st.text_input(f"👤 {t('login_user')}", placeholder="admin / dhia / demo")
            pwd_input = st.text_input(f"🔒 {t('login_pass')}", type="password")
            login_btn = st.form_submit_button(f"🚀 {t('login_btn')}", use_container_width=True)

            if login_btn:
                result = db_verify_user(user_input.strip(), pwd_input)
                if result is None:
                    st.error(f"❌ Utilisateur introuvable")
                elif isinstance(result, dict) and "error" in result:
                    if result["error"] == "locked":
                        st.error(f"🔒 {t('login_locked')}")
                    else:
                        left = result.get("attempts_left", 0)
                        st.error(f"❌ {t('login_error')}. {left} {t('login_attempts')}")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user_id = result["id"]
                    st.session_state.user_name = result["username"]
                    st.session_state.user_role = result["role"]
                    st.session_state.user_full_name = result["full_name"]
                    st.session_state.last_activity = datetime.now()
                    db_log_activity(result["id"], result["username"], "Login", f"Role: {result['role']}")
                    st.rerun()

        st.markdown("""
        <div style='text-align:center; opacity:0.4; font-size:0.75rem; margin-top:12st.markdown("""
        <div style='text-align:center; opacity:0.4; font-size:0.75rem; margin-top:12px;'>
            <p>👑 admin/admin2026 | 🔬 dhia/dhia2026 | 👁️ demo/demo123</p>
        </div>
        """, unsafe_allow_html=True)
    st.stop()


# ============================================
#  16. SIDEBAR (Post-Login)
# ============================================
with st.sidebar:
    role_info = ROLES.get(st.session_state.user_role, ROLES["viewer"])
    st.markdown(f"""
    <div style='text-align:center; padding:10px 0 6px;'>
        <div style='font-size:2.5rem;'>🧬</div>
        <h3 style='margin:4px 0 2px; font-family:Orbitron,sans-serif;'>DM SMART LAB</h3>
        <p style='font-size:0.65rem; opacity:0.3; letter-spacing:0.2em; text-transform:uppercase;'>v{APP_VERSION} • Professional</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"{role_info['icon']} **{st.session_state.user_full_name}**")
    st.caption(f"@{st.session_state.user_name} • {role_info.get('label_fr', st.session_state.user_role)}")

    # Daily tip
    lang = st.session_state.get("lang", "fr")
    tips = DAILY_TIPS.get(lang, DAILY_TIPS["fr"])
    tip_idx = datetime.now().timetuple().tm_yday % len(tips)
    st.info(f"**{t('daily_tip')}:**\n\n{tips[tip_idx]}")

    st.markdown("---")

    lang_opts = {"Français 🇫🇷": "fr", "العربية 🇩🇿": "ar", "English 🇬🇧": "en"}
    cur_idx = list(lang_opts.values()).index(st.session_state.lang)
    sel = st.selectbox(f"🌍 {t('language')}", list(lang_opts.keys()), index=cur_idx, key="sb_lang")
    if lang_opts[sel] != st.session_state.lang:
        st.session_state.lang = lang_opts[sel]
        st.rerun()

    st.markdown("---")

    # Navigation
    nav_items = [
        f"🏠 {t('nav_home')}",
        f"🔬 {t('nav_scan')}",
        f"📘 {t('nav_encyclopedia')}",
        f"📊 {t('nav_dashboard')}",
        f"🧠 {t('nav_quiz')}",
        f"💬 {t('nav_chatbot')}",
        f"🔄 {t('nav_compare')}",
    ]
    page_keys = ["home", "scan", "encyclopedia", "dashboard", "quiz", "chatbot", "compare"]

    # Admin page only for admins
    if user_has_role(3):
        nav_items.append(f"⚙️ {t('nav_admin')}")
        page_keys.append("admin")

    nav_items.append(f"ℹ️ {t('nav_about')}")
    page_keys.append("about")

    menu = st.radio("📌", nav_items, label_visibility="collapsed")

    st.markdown("---")
    dark = st.toggle(f"🌙 {t('night_mode')}", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")
    if st.button(f"🚪 {t('logout')}", use_container_width=True):
        db_log_activity(st.session_state.user_id, st.session_state.user_name, "Logout")
        for k in list(SESSION_DEFAULTS.keys()):
            st.session_state[k] = SESSION_DEFAULTS[k]
        st.session_state.splash_shown = True
        st.rerun()

# Update activity
st.session_state.last_activity = datetime.now()

# Get current page
page_map = dict(zip(nav_items, page_keys))
current_page = page_map.get(menu, "home")


# ╔══════════════════════════════════════════╗
# ║            PAGE: HOME                     ║
# ╚══════════════════════════════════════════╝
if current_page == "home":
    st.title(f"👋 {get_greeting()}, {st.session_state.user_full_name} !")

    c1, c2 = st.columns([1, 2.5])
    with c1:
        st.markdown('<div style="text-align:center;font-size:6rem;">🤖</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='dm-card dm-card-cyan dm-glow-border'>
        <h3 class='dm-neon-title'>DM SMART LAB AI — {t('app_subtitle')}</h3>
        <p style='opacity:0.6;'>{'...' if st.session_state.intro_step < 2 else t('home_go_scan')}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
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
        st.markdown(f"<div class='dm-card dm-card-orange'><h4>🔒 {t('home_step1_title')}</h4><p>{t('home_step1_desc')}</p></div>", unsafe_allow_html=True)
        if st.button(f"🔊 {t('home_step1_btn')}", use_container_width=True, type="primary"):
            txt = t("voice_intro").format(time=datetime.now().strftime("%H:%M"), dev1=AUTHORS["dev1"]["name"], dev2=AUTHORS["dev2"]["name"])
            speak(txt)
            with st.spinner("🔊 ..."):
                time.sleep(5)
            st.session_state.intro_step = 1
            db_log_activity(st.session_state.user_id, st.session_state.user_name, "Intro Step 1")
            st.rerun()
    elif step == 1:
        st.markdown(f"<div class='dm-card dm-card-orange'><h4>🔒 {t('home_step2_title')}</h4><p>{t('home_step2_desc')}</p></div>", unsafe_allow_html=True)
        if st.button(f"🔊 {t('home_step2_btn')}", use_container_width=True, type="primary"):
            txt = t("voice_title").format(title=PROJECT_TITLE)
            speak(txt)
            with st.spinner("🔊 ..."):
                time.sleep(5)
            st.session_state.intro_step = 2
            db_log_activity(st.session_state.user_id, st.session_state.user_name, "System Unlocked")
            st.rerun()
    elif step >= 2:
        st.markdown(f"<div class='dm-card dm-card-green dm-glow-border'><h3>✅ {t('home_unlocked')}</h3><p>{t('home_go_scan')}</p></div>", unsafe_allow_html=True)
        if not st.session_state.get("balloons_shown", False):
            st.balloons()
            st.session_state.balloons_shown = True

    # Quick stats
    if step >= 2:
        st.markdown("---")
        st.markdown("### 📊 Aperçu Rapide")
        stats = db_get_stats(st.session_state.user_id)
        kc = st.columns(4)
        metrics = [
            ("🔬", stats["total"], t("dash_total"), NEON["cyan"]),
            ("✅", stats["reliable"], t("dash_reliable"), NEON["green"]),
            ("⚠️", stats["to_verify"], t("dash_check"), NEON["orange"]),
            ("🦠", stats["most_frequent"], t("dash_frequent"), NEON["magenta"]),
        ]
        for col, (ic, val, lbl, clr) in zip(kc, metrics):
            with col:
                st.markdown(f"""<div class="dm-metric">
                <span class="dm-metric-icon">{ic}</span>
                <div class="dm-metric-val">{val}</div>
                <div class="dm-metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║            PAGE: SCAN & ANALYSE           ║
# ╚══════════════════════════════════════════╝
elif current_page == "scan":
    st.title(f"🔬 {t('scan_title')}")

    if st.session_state.intro_step < 2:
        st.error(f"⛔ {t('scan_blocked')}")
        st.stop()

    if not user_has_role(2):
        st.warning("⚠️ Mode lecture seule. Seuls les Techniciens et Admins peuvent analyser.")

    model, model_name, model_type = load_ai_model()
    if model_name:
        st.sidebar.success(f"🧠 Modèle: {model_name}")
    else:
        st.sidebar.info("🧠 Mode Démo")

    # ── Patient Info ──
    st.markdown(f"### 📋 1. {t('scan_patient_info')}")
    ca, cb = st.columns(2)
    p_nom = ca.text_input(f"{t('scan_nom')} *", placeholder="Benali")
    p_prenom = cb.text_input(t("scan_prenom"), placeholder="Ahmed")
    cc, cd, ce, cf = st.columns(4)
    p_age = cc.number_input(t("scan_age"), 0, 120, 30)
    p_sexe = cd.selectbox(t("scan_sexe"), [t("patient_sexe_h"), t("patient_sexe_f")])
    p_poids = ce.number_input(t("scan_poids"), 0, 300, 70)
    samples = [t("echantillon_selles"), t("echantillon_sang_frottis"), t("echantillon_sang_goutte"),
               t("echantillon_urines"), t("echantillon_lcr"), t("echantillon_peau"),
               t("echantillon_crachat"), t("echantillon_moelle"), t("echantillon_autre")]
    p_type = cf.selectbox(t("scan_echantillon"), samples)

    # ── Lab Info (NEW) ──
    st.markdown(f"### 🔬 2. {t('scan_lab_info')}")
    la, lb, lc = st.columns(3)
    l_tech1 = la.text_input(t("scan_technician1"), value=st.session_state.user_full_name)
    l_tech2 = lb.text_input(t("scan_technician2"), placeholder="Nom du 2ème technicien")
    l_lang = st.session_state.get("lang", "fr")
    micro_list = MICROSCOPE_TYPES.get(l_lang, MICROSCOPE_TYPES["fr"])
    l_micro = lc.selectbox(t("scan_microscope"), micro_list)

    ld, le, lf = st.columns(3)
    l_mag = ld.selectbox(t("scan_magnification"), MAGNIFICATIONS, index=3)
    prep_list = PREPARATION_TYPES.get(l_lang, PREPARATION_TYPES["fr"])
    l_prep = le.selectbox(t("scan_preparation"), prep_list)
    l_notes = lf.text_area(t("scan_notes"), placeholder="Observations...", height=80)

    # ── Image Capture ──
    st.markdown("---")
    st.markdown(f"### 📸 3. {t('scan_capture')}")
    cap_mode = st.radio("Mode:", [f"📷 {t('scan_camera')}", f"📁 {t('scan_upload')}"], horizontal=True, label_visibility="collapsed")

    img_file = None
    if t('scan_camera') in cap_mode:
        img_file = st.camera_input(t("scan_capture"))
    else:
        img_file = st.file_uploader(t("scan_upload"), type=["jpg","jpeg","png","bmp","tiff"])

    if img_file is not None:
        if not p_nom.strip():
            st.error(f"⚠️ {t('scan_nom_required')}")
            st.stop()

        # Reset seeds for new image
        img_hash = hashlib.md5(img_file.getvalue()).hexdigest()
        if st.session_state.get("_last_img_hash") != img_hash:
            st.session_state._last_img_hash = img_hash
            st.session_state.demo_seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = random.randint(0, 999999)

        image = Image.open(img_file).convert("RGB")
        col_img, col_res = st.columns(2)

        with col_img:
            # ── Image Adjustments (NEW) ──
            with st.expander(f"🎛️ {t('scan_zoom')} & Réglages", expanded=False):
                adj_c1, adj_c2, adj_c3 = st.columns(3)
                zoom_lvl = adj_c1.slider(t("scan_zoom_level"), 1.0, 5.0, 1.0, 0.25)
                brightness = adj_c2.slider(t("scan_brightness"), 0.5, 2.0, 1.0, 0.1)
                contrast_adj = adj_c3.slider(t("scan_contrast_adj"), 0.5, 2.0, 1.0, 0.1)
                sat_c1, sat_c2 = st.columns(2)
                saturation = sat_c1.slider(t("scan_saturation"), 0.0, 2.0, 1.0, 0.1)

                adjusted = apply_adjustments(image, brightness, contrast_adj, saturation)
                if zoom_lvl > 1.0:
                    adjusted = zoom_image(adjusted, zoom_lvl)

            # ── Filters Tabs ──
            tab_orig, tab_therm, tab_edge, tab_enh, tab_neg, tab_emb, tab_heat, tab_hist = st.tabs([
                "📷 Original", f"🔥 {t('scan_thermal')}", f"📐 {t('scan_edge')}",
                f"✨ {t('scan_enhanced')}", f"🔄 {t('scan_negative_filter')}",
                f"🏔️ {t('scan_emboss')}", f"🎯 {t('scan_heatmap')}", f"📊 {t('scan_histogram')}"
            ])
            with tab_orig:
                st.image(adjusted, caption="Vue originale" + (f" (Zoom x{zoom_lvl})" if zoom_lvl > 1 else ""), use_container_width=True)
            with tab_therm:
                st.image(apply_thermal(adjusted), caption=t("scan_thermal"), use_container_width=True)
            with tab_edge:
                st.image(apply_edge_detection(adjusted), caption=t("scan_edge"), use_container_width=True)
            with tab_enh:
                st.image(apply_enhanced_contrast(adjusted), caption=t("scan_enhanced"), use_container_width=True)
            with tab_neg:
                st.image(apply_negative_filter(adjusted), caption=t("scan_negative_filter"), use_container_width=True)
            with tab_emb:
                st.image(apply_emboss(adjusted), caption=t("scan_emboss"), use_container_width=True)
            with tab_heat:
                hm = generate_heatmap(model, model_type, image, st.session_state.heatmap_seed)
                st.image(hm, caption=t("scan_heatmap"), use_container_width=True)
            with tab_hist:
                hist_data = get_histogram_data(adjusted)
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=hist_data["red"], name="Red", line=dict(color="red", width=1)))
                    fig.add_trace(go.Scatter(y=hist_data["green"], name="Green", line=dict(color="green", width=1)))
                    fig.add_trace(go.Scatter(y=hist_data["blue"], name="Blue", line=dict(color="blue", width=1)))
                    fig.update_layout(title=t("scan_histogram"), height=300, template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                                      xaxis_title="Pixel Value", yaxis_title="Frequency", margin=dict(l=20,r=20,t=40,b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(pd.DataFrame({"R": hist_data["red"], "G": hist_data["green"], "B": hist_data["blue"]}))

        with col_res:
            st.markdown(f"### 🧠 {t('scan_result')}")
            with st.spinner(f"⏳ {t('scan_analyzing')}"):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.006)
                    prog.progress(i + 1)
                result = predict_image(model, model_type, image, st.session_state.demo_seed)

            label = result["label"]
            conf = result["confidence"]
            info = PARASITE_DB.get(label, PARASITE_DB["Negative"])
            rc = risk_color(result["risk_level"])

            if not result["is_reliable"]:
                st.warning(f"⚠️ {t('scan_low_conf')} ({conf}%)")
            if result["is_demo"]:
                st.info(f"ℹ️ {t('scan_demo_mode')}")

            risk_disp = get_p_text(info, "risk_display")
            morpho = get_p_text(info, "morphology")
            advice = get_p_text(info, "advice")
            funny = get_p_text(info, "funny")

            st.markdown(f"""
            <div class='dm-card dm-glow-border' style='border-left:4px solid {rc};'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
                    <div>
                        <h2 style='color:{rc};margin:0;font-family:Orbitron,sans-serif;'>{label}</h2>
                        <p style='opacity:0.4;font-style:italic;'>{info['scientific_name']}</p>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:2.5rem;font-weight:900;font-family:JetBrains Mono,monospace;background:linear-gradient(135deg,{rc},{rc}aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;'>{conf}%</div>
                        <div style='font-size:0.7rem;opacity:0.4;text-transform:uppercase;'>{t('scan_confidence')}</div>
                    </div>
                </div>
                <hr style='opacity:0.1;margin:14px 0;'>
                <p><b>🔬 {t('scan_morphology')}:</b><br>{morpho}</p>
                <p><b>⚠️ {t('scan_risk')}:</b> <span style='color:{rc};font-weight:700;'>{risk_disp}</span></p>
                <div style='background:rgba(0,255,136,0.06);padding:12px;border-radius:10px;margin:10px 0;border:1px solid rgba(0,255,136,0.15);'>
                    <b>💡 {t('scan_advice')}:</b><br>{advice}
                </div>
                <div style='background:rgba(0,100,255,0.06);padding:12px;border-radius:10px;font-style:italic;border:1px solid rgba(0,100,255,0.1);'>
                    🤖 {funny}
                </div>
            </div>""", unsafe_allow_html=True)

            # Extra tests
            extra = get_p_text(info, "extra_tests")
            if isinstance(extra, list) and extra:
                with st.expander(f"🩺 {t('scan_extra_tests')}"):
                    for test in extra:
                        st.markdown(f"• {test}")

            # Diagnostic keys (NEW)
            diag_keys = get_p_text(info, "diagnostic_keys")
            if diag_keys and diag_keys != "N/A":
                with st.expander(f"🔑 {t('scan_diagnostic_keys')}"):
                    st.markdown(diag_keys)

            # Lifecycle
            lifecycle = get_p_text(info, "lifecycle")
            if lifecycle and lifecycle != "N/A":
                with st.expander("🔄 Cycle de Vie"):
                    st.markdown(f"**{lifecycle}**")

            # Voice
            speak(t("voice_result").format(patient=p_nom, parasite=label, funny=funny))

            # All predictions
            if result["all_predictions"]:
                with st.expander(f"📊 {t('scan_all_probs')}"):
                    if HAS_PLOTLY:
                        sorted_preds = dict(sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True))
                        fig = px.bar(x=list(sorted_preds.values()), y=list(sorted_preds.keys()),
                                     orientation='h', color=list(sorted_preds.values()),
                                     color_continuous_scale='RdYlGn_r',
                                     labels={"x": "Probabilité (%)", "y": "Parasite"})
                        fig.update_layout(height=250, margin=dict(l=20,r=20,t=10,b=20),
                                          template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                                          showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        for cls, prob in sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True):
                            st.progress(min(prob/100, 1.0), text=f"{cls}: {prob}%")

        # Actions
        st.markdown("---")
        st.markdown("### 📄 Actions")
        a1, a2, a3 = st.columns(3)

        with a1:
            pat_data = {t("scan_nom"): p_nom, t("scan_prenom"): p_prenom,
                        t("scan_age"): str(p_age), t("scan_sexe"): p_sexe,
                        t("scan_poids"): str(p_poids), t("scan_echantillon"): p_type}
            lab_data = {"Microscope": l_micro, "Grossissement": l_mag,
                        "Preparation": l_prep, "Technicien 1": l_tech1,
                        "Technicien 2": l_tech2, "Notes": l_notes}
            try:
                pdf = generate_pdf(pat_data, lab_data, result, info)
                st.download_button(f"📥 {t('scan_download_pdf')}", pdf,
                    f"Rapport_{p_nom}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    "application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"PDF Error: {e}")

        with a2:
            if user_has_role(2):
                if st.button(f"💾 {t('scan_save')}", use_container_width=True):
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
                                    "Analysis saved", f"ID:{aid} Patient:{p_nom} Result:{label} Conf:{conf}%")
                    st.success(f"✅ {t('scan_saved')} (ID: {aid})")

        with a3:
            if st.button(f"🔄 {t('scan_new')}", use_container_width=True):
                st.session_state.demo_seed = None
                st.session_state.heatmap_seed = None
                st.session_state._last_img_hash = None
                st.rerun()


# ╔══════════════════════════════════════════╗
# ║          PAGE: ENCYCLOPEDIA               ║
# ╚══════════════════════════════════════════╝
elif current_page == "encyclopedia":
    st.title(f"📘 {t('enc_title')}")
    search = st.text_input(f"🔍 {t('enc_search')}", placeholder="amoeba, giardia...")
    st.markdown("---")

    found = False
    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if search.strip() and search.lower() not in (name + " " + data["scientific_name"]).lower():
            continue
        found = True
        rc = risk_color(data["risk_level"])
        risk_disp = get_p_text(data, "risk_display")

        with st.expander(f"{data['icon']} {name} — *{data['scientific_name']}* | {risk_disp}", expanded=not search.strip()):
            ci, cv = st.columns([2.5, 1])
            with ci:
                st.markdown(f"""<div class='dm-card' style='border-left:3px solid {rc};'>
                <h4 style='color:{rc};font-family:Orbitron,sans-serif;'>{data['scientific_name']}</h4>
                <p><b>🔬 {t('scan_morphology')}:</b><br>{get_p_text(data,'morphology')}</p>
                <p><b>📖 Description:</b><br>{get_p_text(data,'description')}</p>
                <p><b>⚠️ {t('scan_risk')}:</b> <span style='color:{rc};font-weight:700;'>{risk_disp}</span></p>
                <div style='background:rgba(0,255,136,0.06);padding:12px;border-radius:10px;margin:8px 0;'>
                    <b>💡 {t('scan_advice')}:</b><br>{get_p_text(data,'advice')}
                </div>
                <div style='background:rgba(0,100,255,0.06);padding:12px;border-radius:10px;font-style:italic;'>
                    🤖 {get_p_text(data,'funny')}
                </div>
                </div>""", unsafe_allow_html=True)

                lifecycle = get_p_text(data, "lifecycle")
                if lifecycle and lifecycle != "N/A":
                    st.markdown(f"**🔄 Cycle:** {lifecycle}")

                diag_keys = get_p_text(data, "diagnostic_keys")
                if diag_keys:
                    st.markdown(f"**🔑 Clés diagnostiques:**\n{diag_keys}")

                extra = get_p_text(data, "extra_tests")
                if isinstance(extra, list):
                    st.markdown(f"**🩺 {t('scan_extra_tests')}:** {', '.join(extra)}")

            with cv:
                rp = risk_percent(data["risk_level"])
                if rp > 0:
                    st.progress(rp / 100, text=f"Dangerosité: {rp}%")
                st.markdown(f'<div style="text-align:center;font-size:4rem;">{data.get("icon","🦠")}</div>', unsafe_allow_html=True)

    if search.strip() and not found:
        st.warning(f"🔍 {t('enc_no_result')}")


# ╔══════════════════════════════════════════╗
# ║          PAGE: DASHBOARD                  ║
# ╚══════════════════════════════════════════╝
elif current_page == "dashboard":
    st.title(f"📊 {t('dash_title')}")

    # Stats from DB
    if user_has_role(3):
        stats = db_get_stats()  # Admin sees all
        analyses = db_get_analyses()
    else:
        stats = db_get_stats(st.session_state.user_id)
        analyses = db_get_analyses(st.session_state.user_id)

    total = stats["total"]

    # Metrics
    kc = st.columns(5)
    metric_data = [
        ("🔬", stats["total"], t("dash_total"), NEON["cyan"]),
        ("✅", stats["reliable"], t("dash_reliable"), NEON["green"]),
        ("⚠️", stats["to_verify"], t("dash_check"), NEON["orange"]),
        ("🦠", stats["most_frequent"], t("dash_frequent"), NEON["magenta"]),
        ("📈", f"{stats['avg_confidence']}%", t("dash_avg_conf"), NEON["blue"]),
    ]
    for col, (ic, val, lbl, clr) in zip(kc, metric_data):
        with col:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">{ic}</span>
            <div class="dm-metric-val">{val}</div>
            <div class="dm-metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    if total > 0:
        df = pd.DataFrame(analyses)

        # Charts
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(f"#### 📊 {t('dash_distribution')}")
            if HAS_PLOTLY and "parasite_detected" in df.columns:
                para_counts = df["parasite_detected"].value_counts()
                fig = px.pie(values=para_counts.values, names=para_counts.index, hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=350, template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                                  margin=dict(l=20,r=20,t=20,b=20))
                st.plotly_chart(fig, use_container_width=True)
            elif "parasite_detected" in df.columns:
                st.bar_chart(df["parasite_detected"].value_counts())

        with cc2:
            st.markdown(f"#### 📈 {t('dash_confidence_chart')}")
            if HAS_PLOTLY and "confidence" in df.columns:
                fig = px.histogram(df, x="confidence", nbins=20, color_discrete_sequence=[NEON["cyan"]])
                fig.update_layout(height=350, template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                                  xaxis_title="Confiance (%)", yaxis_title="Nombre",
                                  margin=dict(l=20,r=20,t=20,b=20))
                st.plotly_chart(fig, use_container_width=True)
            elif "confidence" in df.columns:
                st.line_chart(df["confidence"].reset_index(drop=True))

        # Trends (NEW)
        st.markdown("---")
        st.markdown(f"#### 📈 {t('dash_trends')}")
        trends = db_get_trends(30)
        if trends and HAS_PLOTLY:
            tdf = pd.DataFrame(trends)
            fig = px.line(tdf, x="day", y="count", color="parasite_detected",
                          markers=True, color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_layout(height=300, template="plotly_dark" if st.session_state.dark_mode else "plotly_white",
                              xaxis_title="Date", yaxis_title="Nombre d'analyses",
                              margin=dict(l=20,r=20,t=20,b=20))
            st.plotly_chart(fig, use_container_width=True)
        elif not trends:
            st.info("Pas assez de données pour les tendances.")

        # History table
        st.markdown("---")
        st.markdown(f"### 📋 {t('dash_history')}")
        display_cols = [c for c in ["id","analysis_date","patient_name","parasite_detected","confidence",
                                     "risk_level","is_reliable","microscope_type","magnification","analyst_name","validated"] if c in df.columns]
        st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)

        # Validation (Admin/Tech)
        if user_has_role(2) and "id" in df.columns:
            unvalidated = df[df.get("validated", 0) == 0] if "validated" in df.columns else pd.DataFrame()
            if not unvalidated.empty:
                st.markdown(f"#### ✅ {t('dash_validate')}")
                val_id = st.selectbox("ID à valider:", unvalidated["id"].tolist())
                if st.button(f"✅ Valider #{val_id}"):
                    db_validate_analysis(val_id, st.session_state.user_full_name)
                    db_log_activity(st.session_state.user_id, st.session_state.user_name, "Validated", f"Analysis #{val_id}")
                    st.success(f"✅ Analyse #{val_id} validée!")
                    st.rerun()

        # Export
        st.markdown("---")
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(f"⬇️ {t('dash_export')}", csv, "analyses.csv", "text/csv", use_container_width=True)
        with ex2:
            jd = df.to_json(orient='records', force_ascii=False).encode('utf-8')
            st.download_button(f"⬇️ {t('dash_export_json')}", jd, "analyses.json", "application/json", use_container_width=True)
        with ex3:
            try:
                import openpyxl
                buf = io.BytesIO()
                df.to_excel(buf, index=False, engine='openpyxl')
                st.download_button(f"⬇️ {t('dash_export_excel')}", buf.getvalue(), "analyses.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            except ImportError:
                st.info("📦 pip install openpyxl")

        # Activity log
        if user_has_role(3):
            with st.expander(f"📜 {t('activity_log')}"):
                logs = db_get_activity_log(100)
                if logs:
                    st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.markdown(f"""<div class='dm-card' style='text-align:center;padding:50px;'>
        <div style='font-size:4rem;'>📊</div><h3>{t('dash_no_data')}</h3>
        <p style='opacity:0.5;'>{t('dash_no_data_desc')}</p></div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║            PAGE: QUIZ                     ║
# ╚══════════════════════════════════════════╝
elif current_page == "quiz":
    st.title(f"🧠 {t('quiz_title')}")
    st.markdown(f"<div class='dm-card dm-card-magenta'><p>{t('quiz_desc')}</p></div>", unsafe_allow_html=True)

    lang = st.session_state.get("lang", "fr")
    questions = QUIZ_QUESTIONS.get(lang, QUIZ_QUESTIONS["fr"])
    qs = st.session_state.quiz_state

    # Leaderboard
    with st.expander(f"🏆 {t('quiz_leaderboard')}"):
        lb = db_get_leaderboard()
        if lb:
            for i, entry in enumerate(lb[:10]):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(f"{medal} **{entry['username']}** — {entry['score']}/{entry['total_questions']} ({entry['percentage']:.0f}%)")
        else:
            st.info("Aucun score enregistré.")

    if not qs["active"]:
        if st.button("🎮 Start Quiz", use_container_width=True, type="primary"):
            # Shuffle questions
            shuffled = list(range(len(questions)))
            random.shuffle(shuffled)
            st.session_state.quiz_state = {
                "current": 0, "score": 0, "answered": [],
                "active": True, "order": shuffled[:min(15, len(questions))]
            }
            db_log_activity(st.session_state.user_id, st.session_state.user_name, "Quiz started")
            st.rerun()
    else:
        idx = qs["current"]
        order = qs.get("order", list(range(len(questions))))

        if idx < len(order):
            q_idx = order[idx]
            q = questions[q_idx]
            total_q = len(order)

            st.markdown(f"### {t('quiz_question')} {idx+1}/{total_q}")
            st.progress(idx / total_q)

            cat = q.get("category", "")
            if cat:
                st.caption(f"📂 {cat}")

            st.markdown(f"<div class='dm-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)

            answer_key = f"quiz_answered_{idx}"
            if answer_key not in st.session_state:
                for i, opt in enumerate(q["options"]):
                    if st.button(opt, key=f"quiz_{idx}_{i}", use_container_width=True):
                        is_correct = (i == q["answer"])
                        if is_correct:
                            st.session_state.quiz_state["score"] += 1
                        st.session_state.quiz_state["answered"].append(is_correct)
                        st.session_state[answer_key] = {"correct": is_correct, "selected": i}
                        st.rerun()
            else:
                ad = st.session_state[answer_key]
                if ad["correct"]:
                    st.success(f"✅ {t('quiz_correct')}")
                else:
                    st.error(f"❌ {t('quiz_wrong')} → {q['options'][q['answer']]}")
                st.info(f"📖 {q['explanation']}")

                if st.button(f"➡️ {t('quiz_next')}", use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1
                    st.rerun()
        else:
            score = qs["score"]
            total_q = len(order)
            pct = int(score / total_q * 100) if total_q > 0 else 0

            if pct >= 80: emoji, msg = "🏆", "Excellent !"
            elif pct >= 60: emoji, msg = "👍", "Bien !"
            elif pct >= 40: emoji, msg = "📚", "Continuez !"
            else: emoji, msg = "💪", "Révisez !"

            st.markdown(f"""<div class='dm-card dm-card-green dm-glow-border' style='text-align:center;'>
            <div style='font-size:4rem;'>{emoji}</div>
            <h2>{t('quiz_finish')}</h2>
            <div class='dm-neon-title' style='font-size:3rem;'>{score}/{total_q}</div>
            <p style='font-size:1.2rem;'>{pct}% — {msg}</p>
            </div>""", unsafe_allow_html=True)

            # Save score
            db_save_quiz_score(st.session_state.user_id, st.session_state.user_name, score, total_q, pct)
            db_log_activity(st.session_state.user_id, st.session_state.user_name, "Quiz finished", f"{score}/{total_q}")

            if st.button(f"🔄 {t('quiz_restart')}", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("quiz_answered_"):
                        del st.session_state[key]
                st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": False}
                st.rerun()


# ╔══════════════════════════════════════════╗
# ║            PAGE: CHATBOT                  ║
# ╚══════════════════════════════════════════╝
elif current_page == "chatbot":
    st.title(f"💬 {t('chatbot_title')}")

    lang = st.session_state.get("lang", "fr")
    greetings = {
        "fr": "👋 Bonjour! Je suis **Dr. DhiaBot** 🤖 votre assistant parasitologique.\n\n💡 Essayez: amoeba, giardia, microscope, coloration, aide",
        "ar": "👋 مرحباً! أنا **الدكتور ضياء بوت** 🤖 مساعدك.\n\n💡 جرب: أميبا، جيارديا، مجهر، تلوين، مساعدة",
        "en": "👋 Hello! I'm **Dr. DhiaBot** 🤖 your parasitology assistant.\n\n💡 Try: amoeba, giardia, microscope, staining, help"
    }

    if not st.session_state.chat_history:
        st.session_state.chat_history.append({"role": "bot", "msg": greetings.get(lang, greetings["fr"])})

    # Display chat
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='dm-chat-msg dm-chat-user'>👤 {msg['msg']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='dm-chat-msg dm-chat-bot'>🤖 {msg['msg']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input(t("chatbot_placeholder"))
    if user_input:
        st.session_state.chat_history.append({"role": "user", "msg": user_input})
        reply = chatbot_reply(user_input, lang)
        st.session_state.chat_history.append({"role": "bot", "msg": reply})
        db_log_activity(st.session_state.user_id, st.session_state.user_name, "Chat", user_input[:80])
        st.rerun()

    # Quick buttons
    st.markdown("---")
    st.markdown("**Questions rapides:**")
    quick = {"fr": ["Amoeba?","Giardia?","Plasmodium?","Microscope?","Coloration?","Aide"],
             "ar": ["أميبا؟","جيارديا؟","ملاريا؟","مجهر؟","تلوين؟","مساعدة"],
             "en": ["Amoeba?","Giardia?","Malaria?","Microscope?","Staining?","Help"]}
    qc = st.columns(6)
    for col, q in zip(qc, quick.get(lang, quick["fr"])):
        with col:
            if st.button(q, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(q, lang)})
                st.rerun()

    if st.button("🗑️ Effacer le chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()


# ╔══════════════════════════════════════════╗
# ║        PAGE: IMAGE COMPARISON             ║
# ╚══════════════════════════════════════════╝
elif current_page == "compare":
    st.title(f"🔄 {t('compare_title')}")
    st.markdown(f"<div class='dm-card dm-card-cyan'><p>{t('compare_desc')}</p></div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📷 Image 1 (Before)")
        img1_file = st.file_uploader("Image 1", type=["jpg","jpeg","png"], key="cmp1")
    with c2:
        st.markdown("### 📷 Image 2 (After)")
        img2_file = st.file_uploader("Image 2", type=["jpg","jpeg","png"], key="cmp2")

    if img1_file and img2_file:
        img1 = Image.open(img1_file).convert("RGB")
        img2 = Image.open(img2_file).convert("RGB")

        c1, c2 = st.columns(2)
        with c1:
            st.image(img1, caption="Image 1", use_container_width=True)
        with c2:
            st.image(img2, caption="Image 2", use_container_width=True)

        st.markdown("---")
        if st.button("🔍 Comparer", use_container_width=True, type="primary"):
            with st.spinner("Analyse comparative..."):
                metrics = compare_images(img1, img2)

            mc = st.columns(3)
            with mc[0]:
                st.markdown(f"""<div class='dm-metric'>
                <span class='dm-metric-icon'>📊</span>
                <div class='dm-metric-val'>{metrics['similarity']}%</div>
                <div class='dm-metric-lbl'>Similarité</div></div>""", unsafe_allow_html=True)
            with mc[1]:
                st.markdown(f"""<div class='dm-metric'>
                <span class='dm-metric-icon'>🎯</span>
                <div class='dm-metric-val'>{metrics['ssim']}</div>
                <div class='dm-metric-lbl'>SSIM</div></div>""", unsafe_allow_html=True)
            with mc[2]:
                st.markdown(f"""<div class='dm-metric'>
                <span class='dm-metric-icon'>📐</span>
                <div class='dm-metric-val'>{metrics['mse']}</div>
                <div class='dm-metric-lbl'>MSE</div></div>""", unsafe_allow_html=True)

            # Side by side with filters
            st.markdown("### 🔬 Comparaison des filtres")
            filters = [
                ("Thermal", apply_thermal),
                ("Edges", apply_edge_detection),
                ("Enhanced", apply_enhanced_contrast),
            ]
            for fname, ffunc in filters:
                fc1, fc2 = st.columns(2)
                with fc1:
                    st.image(ffunc(img1), caption=f"Image 1 - {fname}", use_container_width=True)
                with fc2:
                    st.image(ffunc(img2), caption=f"Image 2 - {fname}", use_container_width=True)


# ╔══════════════════════════════════════════╗
# ║        PAGE: ADMINISTRATION               ║
# ╚══════════════════════════════════════════╝
elif current_page == "admin":
    st.title(f"⚙️ {t('admin_title')}")

    if not user_has_role(3):
        st.error(f"🔒 {t('admin_no_permission')}")
        st.stop()

    tab_users, tab_log, tab_system = st.tabs([f"👥 {t('admin_users')}", f"📜 {t('activity_log')}", "🖥️ Système"])

    with tab_users:
        st.markdown(f"### 👥 {t('admin_users')}")
        users = db_get_all_users()
        if users:
            udf = pd.DataFrame(users)
            st.dataframe(udf, use_container_width=True)

            # Toggle user
            st.markdown("#### 🔄 Activer/Désactiver")
            tc1, tc2 = st.columns(2)
            u_id = tc1.number_input("User ID", min_value=1, step=1)
            u_active = tc2.selectbox("Status", ["Actif", "Désactivé"])
            if st.button("Appliquer"):
                db_toggle_user(u_id, u_active == "Actif")
                db_log_activity(st.session_state.user_id, st.session_state.user_name, "User toggle", f"User {u_id} → {u_active}")
                st.success(f"✅ Utilisateur #{u_id} → {u_active}")
                st.rerun()

        # Create user
        st.markdown("---")
        st.markdown(f"### ➕ {t('admin_create_user')}")
        with st.form("create_user"):
            nu = st.text_input("Nom d'utilisateur *")
            np_ = st.text_input("Mot de passe *", type="password")
            nf = st.text_input("Nom complet *")
            nr = st.selectbox("Rôle", list(ROLES.keys()))
            ns = st.text_input("Spécialité", "Laboratoire")
            if st.form_submit_button("Créer", use_container_width=True):
                if nu and np_ and nf:
                    res = db_create_user(nu, np_, nf, nr, ns)
                    if "success" in res:
                        db_log_activity(st.session_state.user_id, st.session_state.user_name, "User created", f"{nu} ({nr})")
                        st.success(f"✅ Utilisateur '{nu}' créé!")
                        st.rerun()
                    else:
                        st.error(f"❌ {res.get('error', 'Erreur')}")
                else:
                    st.error("Tous les champs * sont obligatoires")

        # Change password
        st.markdown("---")
        st.markdown("### 🔑 Changer un mot de passe")
        cp_id = st.number_input("User ID", min_value=1, step=1, key="cp_id")
        cp_new = st.text_input("Nouveau mot de passe", type="password", key="cp_new")
        if st.button("Changer le mot de passe"):
            if cp_new:
                db_change_password(cp_id, cp_new)
                db_log_activity(st.session_state.user_id, st.session_state.user_name, "Password changed", f"User #{cp_id}")
                st.success(f"✅ Mot de passe changé pour l'utilisateur #{cp_id}")

    with tab_log:
        st.markdown(f"### 📜 {t('activity_log')}")
        logs = db_get_activity_log(300)
        if logs:
            ldf = pd.DataFrame(logs)
            # Filter
            if "username" in ldf.columns:
                users_list = ["Tous"] + ldf["username"].dropna().unique().tolist()
                filt = st.selectbox("Filtrer par utilisateur:", users_list)
                if filt != "Tous":
                    ldf = ldf[ldf["username"] == filt]
            st.dataframe(ldf, use_container_width=True)
        else:
            st.info("Aucune activité enregistrée.")

    with tab_system:
        st.markdown("### 🖥️ Informations Système")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""<div class='dm-card dm-card-green'>
            <h4>🟢 Système OK</h4>
            <p>Version: {APP_VERSION}</p>
            <p>DB: SQLite ({DB_PATH})</p>
            <p>Bcrypt: {'✅' if HAS_BCRYPT else '❌ (SHA256 fallback)'}</p>
            <p>Plotly: {'✅' if HAS_PLOTLY else '❌'}</p>
            <p>QR Code: {'✅' if HAS_QRCODE else '❌'}</p>
            </div>""", unsafe_allow_html=True)
        with sc2:
            total_users = len(db_get_all_users())
            total_analyses = db_get_stats()["total"]
            st.markdown(f"""<div class='dm-card dm-card-cyan'>
            <h4>📊 Statistiques</h4>
            <p>Utilisateurs: {total_users}</p>
            <p>Analyses totales: {total_analyses}</p>
            <p>Quiz scores: {len(db_get_leaderboard())}</p>
            </div>""", unsafe_allow_html=True)
        with sc3:
            db_size = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
            st.markdown(f"""<div class='dm-card dm-card-magenta'>
            <h4>💾 Stockage</h4>
            <p>Taille DB: {db_size:.1f} KB</p>
            <p>Emplacement: {os.path.abspath(DB_PATH)}</p>
            </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════╗
# ║            PAGE: ABOUT                    ║
# ╚══════════════════════════════════════════╝
elif current_page == "about":
    st.title(f"ℹ️ {t('about_title')}")

    st.markdown(f"""<div class='dm-card dm-card-cyan dm-glow-border' style='text-align:center;'>
    <h1 class='dm-neon-title'>🧬 DM SMART LAB AI</h1>
    <p style='font-size:1.1rem;margin-top:6px;font-family:Orbitron,sans-serif;'><b>v{APP_VERSION} — Professional Edition</b></p>
    <p style='opacity:0.5;'>{t('about_desc')}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='dm-card'>
    <h3>📖 {PROJECT_TITLE}</h3>
    <p style='line-height:1.8;opacity:0.8;'>{t('about_project_desc')}</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='dm-card dm-card-cyan'>
        <h3>👨‍🔬 {t('about_team')}</h3><br>
        <p><b>🧑‍💻 {AUTHORS['dev1']['name']}</b><br><span style='opacity:0.5;'>{AUTHORS['dev1']['role']}</span></p><br>
        <p><b>🔬 {AUTHORS['dev2']['name']}</b><br><span style='opacity:0.5;'>{AUTHORS['dev2']['role']}</span></p><br>
        <p><b>Niveau:</b> 3ème Année</p>
        <p><b>Spécialité:</b> Laboratoire de Santé Publique</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='dm-card'>
        <h3>🏫 {t('about_institution')}</h3><br>
        <p><b>{INSTITUTION['name']}</b></p>
        <p>📍 {INSTITUTION['city']}, {INSTITUTION['country']} 🇩🇿</p><br>
        <h4>🎯 {t('about_objectives')}</h4>
        <ul><li>{t('about_obj1')}</li><li>{t('about_obj2')}</li><li>{t('about_obj3')}</li><li>{t('about_obj4')}</li></ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"### 🛠️ {t('about_tech')}")
    tc = st.columns(8)
    techs = [("🐍","Python","Core"),("🧠","TensorFlow","AI"),("🎨","Streamlit","UI"),
             ("📊","Plotly","Charts"),("🗄️","SQLite","Database"),("🔒","Bcrypt","Security"),
             ("📄","FPDF","PDF"),("📱","QR Code","Verify")]
    for col, (i, n, d) in zip(tc, techs):
        with col:
            st.markdown(f"""<div class="dm-metric"><span class="dm-metric-icon">{i}</span>
            <div class="dm-metric-val" style="font-size:0.85rem;">{n}</div>
            <div class="dm-metric-lbl">{d}</div></div>""", unsafe_allow_html=True)

    # Features v6.0
    st.markdown("---")
    st.markdown("### 🌟 Features v6.0 Professional")
    feat_cols = st.columns(4)
    features = [
        ("🗄️", "SQLite DB", "Base de données persistante"),
        ("🔐", "Auth System", "Rôles: Admin/Tech/Viewer"),
        ("🔒", "Bcrypt", "Chiffrement des mots de passe"),
        ("📊", "Plotly Charts", "Graphiques interactifs pro"),
        ("🤖", "Smart Bot", "Chatbot parasitologie complet"),
        ("🧠", "40+ Quiz", "Questions variées par catégorie"),
        ("🎯", "Grad-CAM", "Heatmap réelle ou intelligente"),
        ("📄", "PDF Pro", "QR Code + Signatures"),
        ("🔄", "Comparaison", "Before/After images"),
        ("📈", "Tendances", "Prédiction de cas"),
        ("🔬", "Lab Info", "Microscope/Préparation/Tech"),
        ("🎛️", "Image Tools", "Zoom/Filtres/Histogramme"),
        ("🌙", "Neon UI", "Futuristic Lab Design"),
        ("🔊", "Voice", "Assistant vocal complet"),
        ("🌍", "3 Langues", "FR / AR / EN"),
        ("⚙️", "Admin Panel", "Gestion complète"),
    ]
    for i, (ic, name, desc) in enumerate(features):
        with feat_cols[i % 4]:
            st.markdown(f"""<div class='dm-card' style='padding:14px;text-align:center;'>
            <div style='font-size:1.8rem;'>{ic}</div>
            <p style='font-weight:700;margin:3px 0;font-size:0.85rem;'>{name}</p>
            <p style='font-size:0.7rem;opacity:0.5;'>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Flag_of_Algeria.svg/1200px-Flag_of_Algeria.svg.png", width=80)
    st.caption(f"Fait avec ❤️ à {INSTITUTION['city']} — {INSTITUTION['year']}")
