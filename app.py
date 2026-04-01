# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║                  DM SMART LAB AI v6.0 - FIXED PROFESSIONAL EDITION             ║
# ║            Diagnostic Parasitologique par Intelligence Artificielle              ║
# ║                                                                                ║
# ║  Développé par:                                                                ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)                       ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                          ║
# ║                                                                                ║
# ║  INFSPM - Ouargla, Algérie                                                    ║
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
    page_title="DM Smart Lab AI v6.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
#  CONSTANTS
# ============================================
APP_VERSION = "6.0.0"
SECRET_KEY = "dm_smart_lab_2026_ultra_secret"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)

ROLES = {
    "admin": {"level": 3, "label": "Administrateur", "icon": "👑"},
    "technician": {"level": 2, "label": "Technicien", "icon": "🔬"},
    "viewer": {"level": 1, "label": "Observateur", "icon": "👁️"}
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
#  PARASITE DATABASE
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "scientific_name": "Entamoeba histolytica",
        "morphology": "Kyste spherique (10-15um) a 4 noyaux, corps chromatoide en cigare. Trophozoite (20-40um) avec pseudopodes digitiformes et hematies phagocytees.",
        "description": "Protozoaire responsable de l'amibiase intestinale (dysenterie) et extra-intestinale (abces hepatique). Transmission feco-orale.",
        "funny": "Le ninja des intestins ! Il mange des globules rouges au petit-dejeuner !",
        "risk_level": "high",
        "risk_display": "Élevé 🔴",
        "advice": "Metronidazole 500mg x3/j (7-10j) + Amoebicide de contact (Intetrix). Controle EPS J15/J30.",
        "extra_tests": ["Serologie amibienne (IgG/IgM)", "Echographie hepatique", "NFS + CRP + VS", "PCR Entamoeba", "Scanner abdominal si abces"],
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": "Kyste ingere → Excystation → Trophozoite → Invasion tissulaire → Enkystement → Emission",
        "diagnostic_keys": "• E. histolytica vs E. dispar: seule histolytica phagocyte les hematies\n• Kyste 4 noyaux (vs E. coli 8 noyaux)\n• Corps chromatoides en cigare\n• Mobilite directionnelle"
    },
    "Giardia": {
        "scientific_name": "Giardia lamblia (intestinalis)",
        "morphology": "Trophozoite piriforme en 'cerf-volant' (12-15um), 2 noyaux (face de hibou), disque adhesif, 4 paires de flagelles. Kyste ovoide (8-12um) a 4 noyaux.",
        "description": "Flagelle du duodenum. Diarrhee graisseuse chronique, malabsorption. Transmission hydrique.",
        "funny": "Il te fixe avec ses lunettes de soleil ! Un touriste qui refuse de partir !",
        "risk_level": "medium",
        "risk_display": "Moyen 🟠",
        "advice": "Metronidazole 250mg x3/j (5j) OU Tinidazole 2g dose unique. Verifier la source d'eau.",
        "extra_tests": ["Antigene Giardia (ELISA)", "Test de malabsorption", "EPS x3", "PCR Giardia"],
        "color": "#ff9500", "icon": "🟠",
        "lifecycle": "Kyste ingere → Excystation duodenale → Trophozoite → Adhesion → Multiplication → Enkystement",
        "diagnostic_keys": "• Forme en cerf-volant pathognomonique\n• 2 noyaux = face de hibou\n• Disque adhesif visible au Lugol\n• Mobilite 'feuille morte'"
    },
    "Leishmania": {
        "scientific_name": "Leishmania infantum / major / tropica",
        "morphology": "Amastigotes ovoides (2-5um) intracellulaires dans les macrophages. Noyau + kinetoplaste (MGG). Promastigotes fusiformes en culture.",
        "description": "Transmis par le phlebotome. Cutanee (bouton d'Orient), viscerale (Kala-azar). En Algerie: L. infantum (nord), L. major (sud).",
        "funny": "Petit mais costaud ! Il squatte les macrophages comme un locataire qui ne paie pas !",
        "risk_level": "high",
        "risk_display": "Élevé 🔴",
        "advice": "Cutanee: Glucantime IM. Viscerale: Amphotericine B liposomale. MDO en Algerie.",
        "extra_tests": ["IDR Montenegro", "Serologie Leishmania", "Ponction medullaire", "Biopsie + MGG", "PCR Leishmania", "NFS"],
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": "Piqure phlebotome → Promastigotes → Phagocytose → Amastigotes intracellulaires → Multiplication → Lyse",
        "diagnostic_keys": "• Amastigotes 2-5um intracellulaires\n• Noyau + kinetoplaste au MGG\n• Culture NNN: promastigotes\n• PCR = gold standard espece"
    },
    "Plasmodium": {
        "scientific_name": "Plasmodium falciparum / vivax / ovale / malariae",
        "morphology": "P. falciparum: anneau 'bague a chaton', gametocytes en banane. P. vivax: trophozoite amiboide, granulations Schuffner. Schizontes en rosace.",
        "description": "URGENCE MEDICALE ! Agent du paludisme. P. falciparum: le plus mortel. Transmission par l'anophele femelle.",
        "funny": "Il demande le mariage a tes globules ! Et ses gametocytes en banane... le clown du microscope !",
        "risk_level": "critical",
        "risk_display": "🚨 URGENCE MEDICALE",
        "advice": "HOSPITALISATION ! ACT (Artemisinine). Quinine IV si grave. Parasitemie /4-6h. Surveillance glycemie, creatinine.",
        "extra_tests": ["TDR Paludisme (HRP2/pLDH)", "Frottis + Goutte epaisse URGENCE", "Parasitemie quantitative", "NFS complete", "Bilan hepatho-renal", "Glycemie", "Lactates"],
        "color": "#7f1d1d", "icon": "🚨",
        "lifecycle": "Piqure anophele → Sporozoites → Hepatocytes → Merozoites → Hematies → Gametocytes → Cycle sexue moustique",
        "diagnostic_keys": "• URGENCE: resultat <2h\n• Frottis: identification espece\n• Goutte epaisse: 10x plus sensible\n• >2% parasitemie = forme grave\n• Gametocytes en banane = P. falciparum"
    },
    "Trypanosoma": {
        "scientific_name": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "morphology": "Forme en S/C (15-30um), flagelle libre, membrane ondulante, kinetoplaste posterieur. Coloration MGG/Giemsa.",
        "description": "Maladie du sommeil (T. brucei, mouche tse-tse) ou Chagas (T. cruzi, triatome). Phase hemolymphatique puis neurologique.",
        "funny": "Il court comme Mahrez avec sa membrane ondulante ! Et sa tse-tse, c'est le pire taxi !",
        "risk_level": "high",
        "risk_display": "Élevé 🔴",
        "advice": "Phase 1: Pentamidine/Suramine. Phase 2: NECT/Melarsoprol. Ponction lombaire OBLIGATOIRE pour staging.",
        "extra_tests": ["Ponction lombaire", "Serologie (CATT)", "IgM serique", "Suc ganglionnaire", "NFS"],
        "color": "#ff0040", "icon": "🔴",
        "lifecycle": "Piqure tse-tse → Trypomastigotes → Sang/lymphe → Phase 1 → Franchissement BHE → Phase 2 neurologique",
        "diagnostic_keys": "• Forme S/C avec membrane ondulante\n• Kinetoplaste posterieur\n• IgM tres elevee\n• Staging par PL obligatoire"
    },
    "Schistosoma": {
        "scientific_name": "Schistosoma haematobium / mansoni / japonicum",
        "morphology": "Oeuf ovoide (115-170um) avec eperon terminal (S. haematobium) ou lateral (S. mansoni). Miracidium mobile.",
        "description": "Bilharziose. S. haematobium: uro-genitale (hematurie). S. mansoni: hepato-intestinale. 2eme endemie parasitaire mondiale.",
        "funny": "L'oeuf avec un dard ! La baignade peut couter cher. Les cercaires = micro-torpilles !",
        "risk_level": "medium",
        "risk_display": "Moyen 🟠",
        "advice": "Praziquantel 40mg/kg dose unique. S. haematobium: urines de midi. Eviter eau douce en zone d'endemie.",
        "extra_tests": ["ECBU + sediment midi", "Serologie Schistosoma", "Echo vesicale/hepatique", "NFS + Eosinophilie", "Biopsie rectale"],
        "color": "#ff9500", "icon": "🟠",
        "lifecycle": "Oeuf → Miracidium → Mollusque → Cercaire → Penetration cutanee → Schistosomule → Vers adultes → Ponte",
        "diagnostic_keys": "• S. haematobium: eperon TERMINAL, urines MIDI\n• S. mansoni: eperon LATERAL, selles\n• Miracidium vivant dans l'oeuf\n• Eosinophilie elevee"
    },
    "Negative": {
        "scientific_name": "N/A",
        "morphology": "Absence d'elements parasitaires apres examen direct et concentration. Flore bacterienne normale.",
        "description": "Echantillon negatif. Un seul examen negatif n'exclut pas (sensibilite ~50-60%). Repeter x3.",
        "funny": "Rien a signaler ! Champagne ! Mais les parasites sont des maitres du cache-cache !",
        "risk_level": "none",
        "risk_display": "Négatif 🟢",
        "advice": "RAS. Repeter x3 si suspicion clinique. Bonne hygiene alimentaire.",
        "extra_tests": ["Repeter EPS x3", "Serologie ciblee si besoin", "NFS (eosinophilie?)"],
        "color": "#00ff88", "icon": "🟢",
        "lifecycle": "N/A",
        "diagnostic_keys": "• Direct + Lugol negatif\n• Concentration negative\n• Repeter x3 si doute"
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())

# ============================================
#  QUIZ QUESTIONS (40+)
# ============================================
QUIZ_QUESTIONS = [
    {"q": "Quel parasite presente une 'bague a chaton' dans les hematies?", "options": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"], "answer": 1, "explanation": "Le Plasmodium montre une forme en bague a chaton au stade trophozoite jeune.", "category": "Hematozoaires"},
    {"q": "Le kyste mature de Giardia possede combien de noyaux?", "options": ["2", "4", "6", "8"], "answer": 1, "explanation": "4 noyaux. Le trophozoite en a 2.", "category": "Protozoaires intestinaux"},
    {"q": "Quel parasite est transmis par le phlebotome?", "options": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"], "answer": 2, "explanation": "Leishmania = phlebotome (mouche des sables).", "category": "Protozoaires tissulaires"},
    {"q": "L'eperon terminal caracterise:", "options": ["Ascaris", "S. haematobium", "S. mansoni", "Taenia"], "answer": 1, "explanation": "S. haematobium = terminal. S. mansoni = lateral.", "category": "Helminthes"},
    {"q": "Examen urgent en cas de suspicion de paludisme?", "options": ["Coproculture", "ECBU", "Goutte epaisse + Frottis", "Serologie"], "answer": 2, "explanation": "Goutte epaisse + frottis = reference urgente.", "category": "Diagnostic"},
    {"q": "Le trophozoite d'E. histolytica se distingue par:", "options": ["Flagelles", "Hematies phagocytees", "Membrane ondulante", "Kinetoplaste"], "answer": 1, "explanation": "Hematies phagocytees = critere de pathogenicite.", "category": "Protozoaires"},
    {"q": "La maladie de Chagas est causee par:", "options": ["T. b. gambiense", "T. cruzi", "L. donovani", "P. vivax"], "answer": 1, "explanation": "T. cruzi transmis par les triatomes.", "category": "Protozoaires sanguins"},
    {"q": "Colorant pour les amastigotes de Leishmania?", "options": ["Ziehl-Neelsen", "Gram", "MGG", "Lugol"], "answer": 2, "explanation": "MGG = noyau + kinetoplaste visibles.", "category": "Techniques"},
    {"q": "Traitement de reference de la bilharziose?", "options": ["Chloroquine", "Metronidazole", "Praziquantel", "Albendazole"], "answer": 2, "explanation": "Praziquantel = choix n1.", "category": "Therapeutique"},
    {"q": "La 'face de hibou' est observee chez:", "options": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"], "answer": 1, "explanation": "2 noyaux symetriques de Giardia.", "category": "Morphologie"},
    {"q": "La technique de Ritchie est une methode de:", "options": ["Coloration", "Concentration diphasique", "Culture", "Serologie"], "answer": 1, "explanation": "Formol-ether = concentration pour oeufs/kystes.", "category": "Techniques"},
    {"q": "Le Lugol met en evidence:", "options": ["Flagelles", "Noyaux des kystes", "Hematies", "Bacteries"], "answer": 1, "explanation": "L'iode colore le glycogene et les noyaux.", "category": "Techniques"},
    {"q": "L'objectif x100 necessite:", "options": ["Eau", "Huile d'immersion", "Alcool", "Serum"], "answer": 1, "explanation": "Huile = augmente l'indice de refraction.", "category": "Microscopie"},
    {"q": "Le scotch-test de Graham recherche:", "options": ["Giardia", "Enterobius (oxyure)", "Ascaris", "Taenia"], "answer": 1, "explanation": "Oeufs d'oxyure dans les plis perianaux.", "category": "Techniques"},
    {"q": "Coloration pour Cryptosporidium?", "options": ["Lugol", "Ziehl-Neelsen modifie", "MGG", "Gram"], "answer": 1, "explanation": "ZN modifie = oocystes roses sur fond vert.", "category": "Techniques"},
    {"q": "L'oeuf d'Ascaris est:", "options": ["Avec eperon", "Mamelonne/coque epaisse", "Opercule", "En citron"], "answer": 1, "explanation": "Ovoide, mamelonne, coque brune epaisse.", "category": "Helminthes"},
    {"q": "Le scolex de T. solium possede:", "options": ["Ventouses seules", "Crochets seuls", "Ventouses + crochets", "Bothridies"], "answer": 2, "explanation": "Tenia arme = 4 ventouses + crochets.", "category": "Helminthes"},
    {"q": "L'eosinophilie sanguine oriente vers:", "options": ["Infection bacterienne", "Helminthiase", "Virose", "Paludisme"], "answer": 1, "explanation": "Eosinophilie = marqueur d'helminthiase.", "category": "Diagnostic"},
    {"q": "La cysticercose est causee par:", "options": ["T. saginata adulte", "Larve de T. solium", "Echinococcus", "Ascaris"], "answer": 1, "explanation": "Cysticerque de T. solium chez l'homme.", "category": "Helminthes"},
    {"q": "En Algerie, la leishmaniose cutanee du sud est due a:", "options": ["L. infantum", "L. major", "L. tropica", "L. braziliensis"], "answer": 1, "explanation": "L. major = cutanee zoonotique du sud.", "category": "Epidemiologie"},
    {"q": "Vecteur du paludisme?", "options": ["Aedes", "Culex", "Anopheles", "Simulium"], "answer": 2, "explanation": "Anophele femelle = seul vecteur du Plasmodium.", "category": "Epidemiologie"},
    {"q": "Le kyste hydatique est du a:", "options": ["T. saginata", "Echinococcus granulosus", "Fasciola", "Toxocara"], "answer": 1, "explanation": "Echinococcus granulosus (ver du chien).", "category": "Helminthes"},
    {"q": "Corps chromatoide 'en cigare' typique de:", "options": ["E. histolytica", "E. coli", "Giardia", "Balantidium"], "answer": 0, "explanation": "E. histolytica = cigare. E. coli = pointu.", "category": "Morphologie"},
    {"q": "Protozoaire avec macro et micronoyau?", "options": ["Giardia", "Balantidium coli", "Trichomonas", "Entamoeba"], "answer": 1, "explanation": "Seul cilie pathogene humain.", "category": "Morphologie"},
    {"q": "Membrane ondulante caracteristique de:", "options": ["Giardia", "Trypanosoma", "Leishmania", "Plasmodium"], "answer": 1, "explanation": "Trypanosoma = membrane ondulante + flagelle.", "category": "Morphologie"},
    {"q": "Gametocyte en 'banane' typique de:", "options": ["P. vivax", "P. falciparum", "P. malariae", "P. ovale"], "answer": 1, "explanation": "Gametocytes falciformes = pathognomoniques.", "category": "Hematozoaires"},
    {"q": "Kyste d'E. coli: combien de noyaux?", "options": ["4", "6", "8", "12"], "answer": 2, "explanation": "E. coli = 8 noyaux (vs 4 pour E. histolytica).", "category": "Morphologie"},
    {"q": "Le Metronidazole est inefficace contre:", "options": ["E. histolytica", "Giardia", "Helminthes", "Trichomonas"], "answer": 2, "explanation": "Anti-protozoaire. Pas anti-helminthique.", "category": "Therapeutique"},
    {"q": "L'Albendazole est:", "options": ["Anti-protozoaire", "Anti-helminthique large spectre", "Antibiotique", "Antifongique"], "answer": 1, "explanation": "Large spectre: nematodes + cestodes.", "category": "Therapeutique"},
    {"q": "Traitement du paludisme grave?", "options": ["Chloroquine", "Artesunate IV", "Metronidazole", "Praziquantel"], "answer": 1, "explanation": "Artesunate IV = 1ere ligne (OMS).", "category": "Therapeutique"},
    {"q": "Ivermectine: indication principale?", "options": ["Filarioses/strongyloidose", "Paludisme", "Amibiase", "Giardiose"], "answer": 0, "explanation": "Reference pour filarioses et strongyloidose.", "category": "Therapeutique"},
    {"q": "Patient d'Afrique: fievre + frissons + acces?", "options": ["Amibiase", "Paludisme", "Bilharziose", "Giardiose"], "answer": 1, "explanation": "Paludisme jusqu'a preuve du contraire.", "category": "Cas clinique"},
    {"q": "Hematurie + baignade eau douce Afrique?", "options": ["Giardiose", "Paludisme", "Bilharziose urinaire", "Amibiase"], "answer": 2, "explanation": "S. haematobium = bilharziose urinaire.", "category": "Cas clinique"},
    {"q": "Diarrhee graisseuse chronique + malabsorption enfant?", "options": ["Amibiase", "Giardiose", "Cryptosporidiose", "Salmonellose"], "answer": 1, "explanation": "Giardia = cause frequente de malabsorption.", "category": "Cas clinique"},
    {"q": "Chancre + adenopathies cervicales + somnolence?", "options": ["Paludisme", "Leishmaniose", "Trypanosomiase", "Toxoplasmose"], "answer": 2, "explanation": "THA = maladie du sommeil.", "category": "Cas clinique"},
    {"q": "Bouton ulcere indolore retour du Sahara?", "options": ["Leishmaniose cutanee", "Furoncle", "Anthrax", "Mycose"], "answer": 0, "explanation": "Clou de Biskra = L. major.", "category": "Cas clinique"},
    {"q": "Bilharziose: contamination par:", "options": ["Ingestion d'eau", "Contact cutane eau douce", "Piqure d'insecte", "Voie aerienne"], "answer": 1, "explanation": "Cercaires penetrent la peau dans l'eau.", "category": "Epidemiologie"},
    {"q": "Niclosamide agit sur:", "options": ["Nematodes", "Cestodes (tenias)", "Trematodes", "Protozoaires"], "answer": 1, "explanation": "Specifique des cestodes.", "category": "Therapeutique"},
    {"q": "Goutte epaisse vs frottis mince:", "options": ["Meme sensibilite", "GE 10x plus sensible", "FM plus sensible", "Pas comparable"], "answer": 1, "explanation": "GE = 10x plus sensible pour faibles parasitemies.", "category": "Techniques"},
    {"q": "Oeufs de S. haematobium se cherchent dans:", "options": ["Selles du matin", "Urines de midi", "Sang nocturne", "LCR"], "answer": 1, "explanation": "Pic d'excretion = midi.", "category": "Techniques"},
]

# ============================================
#  CHATBOT KNOWLEDGE BASE
# ============================================
CHATBOT_KB = {
    "amoeba": "🔬 **Entamoeba histolytica**\n\n**Morphologie:** Kyste 10-15um (4 noyaux), Trophozoite 20-40um (hematophage)\n**Diagnostic:** EPS direct + Lugol, serologie si abces\n**Traitement:** Metronidazole + Intetrix\n**Distinction:** E. histolytica (pathogene) vs E. dispar (non pathogene) → PCR",
    "amibe": "🔬 Meme reponse que Amoeba. Voir Entamoeba histolytica.",
    "giardia": "🔬 **Giardia lamblia**\n\n**Morphologie:** Cerf-volant (12-15um), face de hibou, 4 paires flagelles\n**Diagnostic:** EPS + Lugol, Ag Giardia ELISA\n**Traitement:** Metronidazole 250mg x3/j (5j) OU Tinidazole 2g\n**Clinique:** Diarrhee graisseuse, malabsorption",
    "leishmania": "🔬 **Leishmania**\n\n**Morphologie:** Amastigotes 2-5um dans macrophages (MGG)\n**Formes:** Cutanee (L. major), Viscerale (L. infantum)\n**En Algerie:** L. major (sud), L. infantum (nord) - MDO\n**Traitement:** Glucantime (cutanee), Amphotericine B (viscerale)",
    "plasmodium": "🚨 **URGENCE - Plasmodium (Paludisme)**\n\n**Morphologie:** Bague a chaton, gametocytes banane (P.f)\n**Diagnostic URGENT:** Frottis + Goutte epaisse (<2h!)\n**Seuil:** >2% = forme grave → HOSPITALISATION\n**Traitement:** ACT ou Artesunate IV",
    "malaria": "🚨 Meme chose que Plasmodium. URGENCE MEDICALE !",
    "paludisme": "🚨 Meme chose que Plasmodium. URGENCE MEDICALE !",
    "trypanosoma": "🔬 **Trypanosoma**\n\n**Morphologie:** Forme S/C (15-30um), membrane ondulante, kinetoplaste\n**Maladies:** Sommeil (T. brucei, tse-tse), Chagas (T. cruzi)\n**Staging:** Ponction lombaire OBLIGATOIRE\n**Traitement:** Phase 1: Pentamidine. Phase 2: NECT/Melarsoprol",
    "schistosoma": "🔬 **Schistosoma (Bilharziose)**\n\n**S. haematobium:** Eperon TERMINAL, urines MIDI\n**S. mansoni:** Eperon LATERAL, selles\n**Traitement:** Praziquantel 40mg/kg\n**Prevention:** Eviter eau douce en zone d'endemie",
    "bilharziose": "Meme chose que Schistosoma.",
    "microscope": "🔬 **Microscopie en Parasitologie:**\n\n• **x10:** Reperage\n• **x40:** Identification oeufs/kystes\n• **x100 (immersion):** Details (Plasmodium, Leishmania)\n\n**Types:** Optique, fluorescence, contraste de phase, fond noir",
    "coloration": "🎨 **Colorations:**\n\n• **Lugol:** Noyaux des kystes\n• **MGG/Giemsa:** Parasites sanguins\n• **Ziehl-Neelsen modifie:** Cryptosporidium\n• **Trichrome:** Microsporidies",
    "selle": "**EPS Complet:**\n\n1. Macroscopique\n2. Direct (NaCl + Lugol)\n3. Concentration (Ritchie/Willis)\n\n⚠️ Examiner dans 30 min! Repeter x3!",
    "hygiene": "🧼 **Prevention:**\n\n✅ Lavage des mains\n✅ Eau potable\n✅ Cuisson viande >65C\n✅ Moustiquaires\n✅ Eviter eaux stagnantes",
    "concentration": "🧪 **Techniques de concentration:**\n\n• **Ritchie:** Formol-ether (reference)\n• **Willis:** Flottation NaCl\n• **Kato-Katz:** Semi-quantitatif\n• **Baermann:** Larves Strongyloides",
    "bonjour": "👋 Bonjour! Je suis **Dr. DhiaBot**, votre assistant parasitologique.\n\n🔬 Parasites | 💊 Traitements | 🧪 Techniques | 🩺 Cas cliniques\n\nQue voulez-vous savoir?",
    "salut": "Salut! 😊 Comment puis-je vous aider en parasitologie?",
    "hello": "Hello! 👋 I'm Dr. DhiaBot. How can I help?",
    "merci": "De rien! 😊 La parasitologie est ma passion!",
    "aide": "📚 **Je connais:**\n\nAmoeba, Giardia, Leishmania, Plasmodium, Trypanosoma, Schistosoma, Ascaris, Taenia, Toxoplasma, Oxyure, Cryptosporidium...\n\nEt: microscopie, colorations, concentration, EPS, diagnostic, traitements, epidemiologie, hygiene!\n\n💡 Tapez un mot-cle!",
    "help": "📚 I know all parasites and lab techniques. Type a keyword!",
}

DAILY_TIPS = [
    "💡 Examiner les selles dans les 30 min pour voir les trophozoites mobiles.",
    "💡 Le Lugol met en evidence les noyaux des kystes. Dilution fraiche chaque semaine.",
    "💡 Frottis mince: angle 45 pour une monocouche parfaite.",
    "💡 La goutte epaisse est 10x plus sensible que le frottis mince.",
    "💡 Urines de midi pour S. haematobium (pic d'excretion).",
    "💡 Repeter l'EPS x3 a quelques jours d'intervalle.",
    "💡 Metronidazole = Amoeba + Giardia + Trichomonas. Retenir ce trio!",
    "💡 Ziehl-Neelsen modifie est indispensable pour Cryptosporidium.",
    "💡 En paludisme: 1ere GE negative ne suffit pas. Repeter a 6-12h.",
    "💡 Le phlebotome est actif au crepuscule. Moustiquaires!",
    "💡 Eosinophilie = helminthiase probable. Toujours verifier!",
    "💡 E. coli 8 noyaux vs E. histolytica 4 noyaux = critere n1.",
    "💡 Selles liquides → trophozoites. Selles formees → kystes.",
    "💡 PCR = gold standard pour identifier l'espece de Leishmania.",
]

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
    "system_unlocked": False,
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
    return {"critical": "#ff0040", "high": "#ff3366", "medium": "#ff9500", "low": "#00e676", "none": "#00ff88"}.get(
        level, "#888")


def risk_percent(level):
    return {"critical": 100, "high": 80, "medium": 50, "low": 25, "none": 0}.get(level, 0)


def get_greeting():
    h = datetime.now().hour
    if h < 12:
        return "Bonjour"
    elif h < 18:
        return "Bon apres-midi"
    return "Bonsoir"


def chatbot_reply(user_msg):
    msg_lower = user_msg.lower().strip()

    for key, response in CHATBOT_KB.items():
        if key in msg_lower:
            return response

    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if name.lower() in msg_lower or data["scientific_name"].lower() in msg_lower:
            return f"**{name}** ({data['scientific_name']})\n\n📋 {data['description']}\n\n🔬 {data['morphology']}\n\n💊 {data['advice']}\n\n🤖 {data['funny']}"

    return "🤖 Je suis Dr. DhiaBot. Tapez un mot-cle (amoeba, giardia, microscope, aide...)"


def speak_js(text, lang_code="fr"):
    """Non-blocking voice using browser JS"""
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
    result = {"label": "Negative", "confidence": 0, "all_predictions": {}, "is_reliable": False, "is_demo": False,
              "risk_level": "none"}

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


def apply_sharpen(image):
    return image.filter(ImageFilter.SHARPEN)


def apply_denoise(image):
    return image.filter(ImageFilter.GaussianBlur(radius=2))


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
    t = (h - nh) // 2
    return image.crop((l, t, l + nw, t + nh)).resize((w, h), Image.LANCZOS)


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
        self.multi_cell(0, 4, _safe_pdf(
            "AVERTISSEMENT: Ce rapport est genere par IA et doit etre valide par un professionnel de sante."))
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


def generate_pdf(patient, lab, result, info):
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

    if info:
        pdf.set_font("Arial", "", 9)
        pdf.multi_cell(0, 5, _safe_pdf(f"Morphologie: {info.get('morphology', '')}"))
        pdf.ln(1)
        pdf.multi_cell(0, 5, _safe_pdf(f"Description: {info.get('description', '')}"))
    pdf.ln(3)

    pdf.section("RECOMMANDATIONS CLINIQUES", (0, 130, 0))
    pdf.set_font("Arial", "", 9)
    if info:
        pdf.multi_cell(0, 5, _safe_pdf(info.get("advice", "")))
        pdf.ln(2)
        extra = info.get("extra_tests", [])
        if extra:
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
            try:
                os.remove(qr_path)
            except:
                pass
        except:
            pass

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
#  CSS THEME (Optimized)
# ============================================
def apply_theme():
    dm = st.session_state.get("dark_mode", True)
    if dm:
        bg, card_bg, text, primary, muted = "#030614", "rgba(10,15,46,0.85)", "#e0e8ff", "#00f5ff", "#6b7fa0"
        accent, accent2, sidebar_bg = "#ff00ff", "#00ff88", "#020410"
        btn_grad, border_c = "linear-gradient(135deg,#00f5ff,#0066ff)", "rgba(0,245,255,0.15)"
        template = "plotly_dark"
    else:
        bg, card_bg, text, primary, muted = "#f0f4f8", "rgba(255,255,255,0.9)", "#0f172a", "#0066ff", "#64748b"
        accent, accent2, sidebar_bg = "#9933ff", "#00cc66", "#f8fafc"
        btn_grad, border_c = "linear-gradient(135deg,#0066ff,#0044cc)", "rgba(0,100,255,0.12)"
        template = "plotly_white"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap');

    .stApp {{ background: {bg}; }}
    section[data-testid="stSidebar"] {{ background: {sidebar_bg} !important; }}

    .dm-card {{
        background: {card_bg}; backdrop-filter: blur(15px);
        border: 1px solid {border_c}; border-radius: 16px;
        padding: 24px; margin: 12px 0;
        transition: all 0.3s ease;
    }}
    .dm-card:hover {{ transform: translateY(-2px); }}
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
        text-transform:uppercase; letter-spacing:0.08em; margin-top:4px;
    }}

    div.stButton > button {{
        background: {btn_grad} !important; color: white !important;
        border: none !important; border-radius: 12px !important;
        padding: 10px 24px !important; font-weight: 600 !important;
    }}
    div.stButton > button:hover {{ transform: translateY(-2px) !important; }}

    .dm-neon-title {{
        font-family: 'Orbitron', sans-serif; font-weight: 900;
        background: linear-gradient(135deg, {primary}, {accent}, {accent2});
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}

    .dm-chat-msg {{ padding:12px 16px; border-radius:14px; margin:6px 0; max-width:85%; font-size:0.9rem; }}
    .dm-chat-user {{ background:{btn_grad}; color:white !important; margin-left:auto; }}
    .dm-chat-user * {{ color:white !important; }}
    .dm-chat-bot {{ background:{card_bg}; border:1px solid {border_c}; }}

    h1 {{ font-family: 'Orbitron', sans-serif !important; }}
    </style>
    """, unsafe_allow_html=True)

    return template


plotly_template = apply_theme()

# ============================================
#  LOGO
# ============================================
st.markdown("""
<div style="text-align:center;padding:10px 0;">
    <div style="font-size:2.5rem;">🧬</div>
    <h3 style="font-family:Orbitron,sans-serif;margin:2px 0;">DM SMART LAB AI</h3>
    <p style="font-size:0.6rem;opacity:0.3;letter-spacing:0.3em;text-transform:uppercase;">v6.0 Professional</p>
</div>
""", unsafe_allow_html=True)

# ============================================
#  LOGIN
# ============================================
if not st.session_state.logged_in:
    col_a, col_b, col_c = st.columns([1.2, 2, 1.2])
    with col_b:
        st.markdown("""
        <div class='dm-card dm-card-cyan' style='text-align:center;'>
            <div style='font-size:3rem;'>🔐</div>
            <h2 class='dm-neon-title'>Connexion Securisee</h2>
            <p style='opacity:0.5;'>Systeme d'Authentification Professionnel</p>
        </div>""", unsafe_allow_html=True)

        with st.form("login_form"):
            user_input = st.text_input("👤 Identifiant", placeholder="admin / dhia / demo")
            pwd_input = st.text_input("🔒 Mot de Passe", type="password")
            login_btn = st.form_submit_button("🚀 SE CONNECTER", use_container_width=True)

            if login_btn and user_input.strip():
                result = db_verify_user(user_input.strip(), pwd_input)
                if result is None:
                    st.error("❌ Utilisateur introuvable")
                elif isinstance(result, dict) and "error" in result:
                    if result["error"] == "locked":
                        st.error("🔒 Compte verrouille temporairement")
                    else:
                        left = result.get("attempts_left", 0)
                        st.error(f"❌ Mot de passe incorrect. {left} tentative(s) restante(s)")
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
    st.caption(f"@{st.session_state.user_name} - {role_info['label']}")

    tip_idx = datetime.now().timetuple().tm_yday % len(DAILY_TIPS)
    st.info(f"**Conseil du Jour:**\n\n{DAILY_TIPS[tip_idx]}")

    st.markdown("---")

    nav_items = [
        "🏠 Accueil",
        "🔬 Scan & Analyse",
        "📘 Encyclopedie",
        "📊 Tableau de Bord",
        "🧠 Quiz Medical",
        "💬 Dr. DhiaBot",
        "🔄 Comparaison",
    ]
    page_keys = ["home", "scan", "encyclopedia", "dashboard", "quiz", "chatbot", "compare"]

    if user_has_role(3):
        nav_items.append("⚙️ Administration")
        page_keys.append("admin")

    nav_items.append("ℹ️ A Propos")
    page_keys.append("about")

    menu = st.radio("Navigation", nav_items, label_visibility="collapsed")

    st.markdown("---")
    dark = st.toggle("🌙 Mode Nuit", value=st.session_state.dark_mode)
    if dark != st.session_state.dark_mode:
        st.session_state.dark_mode = dark
        st.rerun()

    st.markdown("---")
    if st.button("🚪 Deconnexion", use_container_width=True):
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
    <h3 class='dm-neon-title'>DM SMART LAB AI — Ou la Science Rencontre l'Intelligence</h3>
    <p style='opacity:0.6;'>Systeme de diagnostic parasitologique par intelligence artificielle</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # Step 1: Presentation
    st.markdown("### 🎤 Etape 1 : Presentation du Systeme")
    if st.button("🔊 LANCER LA PRESENTATION", use_container_width=True, type="primary"):
        txt = f"Bonjour! Il est {datetime.now().strftime('%H:%M')}. Je suis DM Smart Lab, intelligence artificielle developpee par les Techniciens Superieurs {AUTHORS['dev1']['name']} et {AUTHORS['dev2']['name']}. Preparez vos lames, et ne me chatouillez pas avec le microscope!"
        speak_js(txt, "fr")
        st.success("✅ Presentation lancee!")

    st.markdown("### 📖 Etape 2 : Titre du Memoire")
    if st.button("🔊 LIRE LE TITRE DU PROJET", use_container_width=True, type="primary"):
        txt = f"Memoire de Fin d'Etudes: {PROJECT_TITLE}. Institut National de Formation Superieure Paramedicale de Ouargla."
        speak_js(txt, "fr")
        st.success("✅ Titre lu!")
        st.session_state.system_unlocked = True

    if st.session_state.system_unlocked:
        st.markdown("""<div class='dm-card dm-card-green'>
        <h3>✅ SYSTEME DEVERROUILLE AVEC SUCCES !</h3>
        <p>Passez au module de diagnostic dans le menu lateral.</p>
        </div>""", unsafe_allow_html=True)
        st.balloons()

    # Quick stats
    st.markdown("---")
    st.markdown("### 📊 Apercu Rapide")
    stats = db_get_stats(st.session_state.user_id)
    kc = st.columns(4)
    metrics = [
        ("🔬", stats["total"], "Total Analyses"),
        ("✅", stats["reliable"], "Fiables"),
        ("⚠️", stats["to_verify"], "A Verifier"),
        ("🦠", stats["most_frequent"], "Plus Frequent"),
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
    st.title("🔬 Unite de Diagnostic Parasitologique")

    model, model_name, model_type = load_ai_model()
    if model_name:
        st.sidebar.success(f"🧠 Modele: {model_name}")
    else:
        st.sidebar.info("🧠 Mode Demo (pas de modele)")

    # Patient Info
    st.markdown("### 📋 1. Informations du Patient")
    ca, cb = st.columns(2)
    p_nom = ca.text_input("Nom *", placeholder="Benali")
    p_prenom = cb.text_input("Prenom", placeholder="Ahmed")
    cc, cd, ce, cf = st.columns(4)
    p_age = cc.number_input("Age", 0, 120, 30)
    p_sexe = cd.selectbox("Sexe", ["Homme", "Femme"])
    p_poids = ce.number_input("Poids (kg)", 0, 300, 70)
    samples = ["Selles", "Sang (Frottis)", "Sang (Goutte epaisse)", "Urines", "LCR", "Biopsie Cutanee", "Crachat",
               "Autre"]
    p_type = cf.selectbox("Type d'Echantillon", samples)

    # Lab Info
    st.markdown("### 🔬 2. Informations du Laboratoire")
    la, lb, lc = st.columns(3)
    l_tech1 = la.text_input("Technicien 1", value=st.session_state.user_full_name)
    l_tech2 = lb.text_input("Technicien 2", placeholder="Nom du 2eme technicien")
    l_micro = lc.selectbox("Type de Microscope", MICROSCOPE_TYPES)
    ld, le = st.columns(2)
    l_mag = ld.selectbox("Grossissement", MAGNIFICATIONS, index=3)
    l_prep = le.selectbox("Type de Preparation", PREPARATION_TYPES)
    l_notes = st.text_area("Notes / Observations", placeholder="Observations...", height=80)

    # Image
    st.markdown("---")
    st.markdown("### 📸 3. Capture Microscopique")
    img_file = st.file_uploader("Importer une image", type=["jpg", "jpeg", "png", "bmp", "tiff"])

    if img_file is not None:
        if not p_nom.strip():
            st.error("⚠️ Le nom du patient est obligatoire !")
            st.stop()

        img_hash = hashlib.md5(img_file.getvalue()).hexdigest()
        if st.session_state.get("_last_img_hash") != img_hash:
            st.session_state._last_img_hash = img_hash
            st.session_state.demo_seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = random.randint(0, 999999)

        image = Image.open(img_file).convert("RGB")
        col_img, col_res = st.columns(2)

        with col_img:
            # Adjustments
            with st.expander("🎛️ Zoom & Reglages", expanded=False):
                ac1, ac2, ac3 = st.columns(3)
                zoom_lvl = ac1.slider("Zoom", 1.0, 5.0, 1.0, 0.25)
                brightness = ac2.slider("Luminosite", 0.5, 2.0, 1.0, 0.1)
                contrast_adj = ac3.slider("Contraste", 0.5, 2.0, 1.0, 0.1)
                saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
                adjusted = apply_adjustments(image, brightness, contrast_adj, saturation)
                if zoom_lvl > 1.0:
                    adjusted = zoom_image(adjusted, zoom_lvl)

            # Filter tabs
            tab_orig, tab_therm, tab_edge, tab_enh, tab_neg, tab_emb, tab_heat, tab_hist = st.tabs([
                "📷 Original", "🔥 Thermique", "📐 Contours",
                "✨ Contraste+", "🔄 Negatif",
                "🏔️ Relief", "🎯 Heatmap", "📊 Histogramme"
            ])
            with tab_orig:
                st.image(adjusted, caption="Vue originale" + (f" (x{zoom_lvl})" if zoom_lvl > 1 else ""),
                         use_container_width=True)
            with tab_therm:
                st.image(apply_thermal(adjusted), caption="Vision Thermique", use_container_width=True)
            with tab_edge:
                st.image(apply_edge_detection(adjusted), caption="Detection de Contours", use_container_width=True)
            with tab_enh:
                st.image(apply_enhanced_contrast(adjusted), caption="Contraste Ameliore", use_container_width=True)
            with tab_neg:
                st.image(apply_negative_filter(adjusted), caption="Negatif", use_container_width=True)
            with tab_emb:
                st.image(apply_emboss(adjusted), caption="Relief", use_container_width=True)
            with tab_heat:
                hm = generate_heatmap(image, st.session_state.heatmap_seed)
                st.image(hm, caption="Zone d'interet IA (Grad-CAM)", use_container_width=True)
            with tab_hist:
                hist_data = get_histogram_data(adjusted)
                if HAS_PLOTLY:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(y=hist_data["red"], name="Red", line=dict(color="red", width=1)))
                    fig.add_trace(go.Scatter(y=hist_data["green"], name="Green", line=dict(color="green", width=1)))
                    fig.add_trace(go.Scatter(y=hist_data["blue"], name="Blue", line=dict(color="blue", width=1)))
                    fig.update_layout(title="Histogramme", height=300, template=plotly_template,
                                      margin=dict(l=20, r=20, t=40, b=20))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.bar_chart(pd.DataFrame(hist_data))

        with col_res:
            st.markdown("### 🧠 Resultat de l'IA")
            with st.spinner("⏳ Analyse IA en cours..."):
                prog = st.progress(0)
                for i in range(100):
                    time.sleep(0.005)
                    prog.progress(i + 1)
                result = predict_image(model, model_type, image, st.session_state.demo_seed)

            label = result["label"]
            conf = result["confidence"]
            info = PARASITE_DB.get(label, PARASITE_DB["Negative"])
            rc = risk_color(result["risk_level"])

            if not result["is_reliable"]:
                st.warning(f"⚠️ Confiance faible ({conf}%). Verification manuelle recommandee !")
            if result["is_demo"]:
                st.info("ℹ️ Mode demonstration (aucun modele charge)")

            st.markdown(f"""
            <div class='dm-card' style='border-left:4px solid {rc};'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
                    <div>
                        <h2 style='color:{rc};margin:0;font-family:Orbitron,sans-serif;'>{label}</h2>
                        <p style='opacity:0.4;font-style:italic;'>{info['scientific_name']}</p>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:2.5rem;font-weight:900;font-family:JetBrains Mono,monospace;color:{rc};'>{conf}%</div>
                        <div style='font-size:0.7rem;opacity:0.4;text-transform:uppercase;'>Confiance</div>
                    </div>
                </div>
                <hr style='opacity:0.1;margin:14px 0;'>
                <p><b>🔬 Morphologie:</b><br>{info['morphology']}</p>
                <p><b>⚠️ Risque:</b> <span style='color:{rc};font-weight:700;'>{info['risk_display']}</span></p>
                <div style='background:rgba(0,255,136,0.06);padding:12px;border-radius:10px;margin:10px 0;'>
                    <b>💡 Conseil Medical:</b><br>{info['advice']}
                </div>
                <div style='background:rgba(0,100,255,0.06);padding:12px;border-radius:10px;font-style:italic;'>
                    🤖 {info['funny']}
                </div>
            </div>""", unsafe_allow_html=True)

            # Voice result
            speak_js(f"Resultat pour {p_nom}: {label}. {info['funny']}", "fr")

            # Extra tests
            if info.get("extra_tests"):
                with st.expander("🩺 Examens complementaires suggeres"):
                    for test in info["extra_tests"]:
                        st.markdown(f"• {test}")

            # Diagnostic keys
            if info.get("diagnostic_keys") and info["diagnostic_keys"] != "N/A":
                with st.expander("🔑 Cles Diagnostiques"):
                    st.markdown(info["diagnostic_keys"])

            # Lifecycle
            if info.get("lifecycle") and info["lifecycle"] != "N/A":
                with st.expander("🔄 Cycle de Vie"):
                    st.markdown(f"**{info['lifecycle']}**")

            # All predictions
            if result["all_predictions"]:
                with st.expander("📊 Toutes les probabilites"):
                    if HAS_PLOTLY:
                        sorted_preds = dict(sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True))
                        fig = px.bar(x=list(sorted_preds.values()), y=list(sorted_preds.keys()),
                                     orientation='h', color=list(sorted_preds.values()),
                                     color_continuous_scale='RdYlGn_r',
                                     labels={"x": "Probabilite (%)", "y": "Parasite"})
                        fig.update_layout(height=250, margin=dict(l=20, r=20, t=10, b=20),
                                          template=plotly_template, showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        for cls, prob in sorted(result["all_predictions"].items(), key=lambda x: x[1], reverse=True):
                            st.progress(min(prob / 100, 1.0), text=f"{cls}: {prob}%")

        # Actions
        st.markdown("---")
        st.markdown("### 📄 Actions")
        a1, a2, a3 = st.columns(3)

        with a1:
            pat_data = {"Nom": p_nom, "Prenom": p_prenom, "Age": str(p_age),
                        "Sexe": p_sexe, "Poids": str(p_poids), "Echantillon": p_type}
            lab_data = {"Microscope": l_micro, "Grossissement": l_mag,
                        "Preparation": l_prep, "Technicien 1": l_tech1,
                        "Technicien 2": l_tech2, "Notes": l_notes}
            try:
                pdf = generate_pdf(pat_data, lab_data, result, info)
                st.download_button("📥 Telecharger le Rapport PDF", pdf,
                                   f"Rapport_{p_nom}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                                   "application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Erreur PDF: {e}")

        with a2:
            if user_has_role(2):
                if st.button("💾 Sauvegarder dans la Base", use_container_width=True):
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
                    st.success(f"✅ Resultat sauvegarde ! (ID: {aid})")

        with a3:
            if st.button("🔄 Nouvelle Analyse", use_container_width=True):
                st.session_state.demo_seed = None
                st.session_state.heatmap_seed = None
                st.session_state._last_img_hash = None
                st.rerun()

# ╔══════════════════════════════════════════╗
# ║          PAGE: ENCYCLOPEDIA               ║
# ╚══════════════════════════════════════════╝
elif current_page == "encyclopedia":
    st.title("📘 Encyclopedie des Parasites")
    search = st.text_input("🔍 Rechercher un parasite...", placeholder="amoeba, giardia...")
    st.markdown("---")

    found = False
    for name, data in PARASITE_DB.items():
        if name == "Negative":
            continue
        if search.strip() and search.lower() not in (name + " " + data["scientific_name"]).lower():
            continue
        found = True
        rc = risk_color(data["risk_level"])

        with st.expander(f"{data['icon']} {name} — *{data['scientific_name']}* | {data['risk_display']}",
                         expanded=not search.strip()):
            ci, cv = st.columns([2.5, 1])
            with ci:
                st.markdown(f"""<div class='dm-card' style='border-left:3px solid {rc};'>
                <h4 style='color:{rc};font-family:Orbitron,sans-serif;'>{data['scientific_name']}</h4>
                <p><b>🔬 Morphologie:</b><br>{data['morphology']}</p>
                <p><b>📖 Description:</b><br>{data['description']}</p>
                <p><b>⚠️ Risque:</b> <span style='color:{rc};font-weight:700;'>{data['risk_display']}</span></p>
                <div style='background:rgba(0,255,136,0.06);padding:12px;border-radius:10px;margin:8px 0;'>
                    <b>💡 Conseil:</b><br>{data['advice']}
                </div>
                <div style='background:rgba(0,100,255,0.06);padding:12px;border-radius:10px;font-style:italic;'>
                    🤖 {data['funny']}
                </div>
                </div>""", unsafe_allow_html=True)

                if data.get("lifecycle") and data["lifecycle"] != "N/A":
                    st.markdown(f"**🔄 Cycle:** {data['lifecycle']}")
                if data.get("diagnostic_keys"):
                    st.markdown(f"**🔑 Cles diagnostiques:**\n{data['diagnostic_keys']}")
                if data.get("extra_tests"):
                    st.markdown(f"**🩺 Examens:** {', '.join(data['extra_tests'])}")

            with cv:
                rp = risk_percent(data["risk_level"])
                if rp > 0:
                    st.progress(rp / 100, text=f"Dangerosite: {rp}%")
                st.markdown(f'<div style="text-align:center;font-size:4rem;">{data["icon"]}</div>',
                            unsafe_allow_html=True)

    if search.strip() and not found:
        st.warning("🔍 Aucun resultat trouve.")

# ╔══════════════════════════════════════════╗
# ║          PAGE: DASHBOARD                  ║
# ╚══════════════════════════════════════════╝
elif current_page == "dashboard":
    st.title("📊 Tableau de Bord Clinique")

    if user_has_role(3):
        stats = db_get_stats()
        analyses = db_get_analyses()
    else:
        stats = db_get_stats(st.session_state.user_id)
        analyses = db_get_analyses(st.session_state.user_id)

    total = stats["total"]

    kc = st.columns(5)
    metric_data = [
        ("🔬", stats["total"], "Total Analyses"),
        ("✅", stats["reliable"], "Fiables"),
        ("⚠️", stats["to_verify"], "A Verifier"),
        ("🦠", stats["most_frequent"], "Plus Frequent"),
        ("📈", f"{stats['avg_confidence']}%", "Confiance Moy."),
    ]
    for col, (ic, val, lbl) in zip(kc, metric_data):
        with col:
            st.markdown(f"""<div class="dm-metric">
            <span class="dm-metric-icon">{ic}</span>
            <div class="dm-metric-val">{val}</div>
            <div class="dm-metric-lbl">{lbl}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")

    if total > 0:
        df = pd.DataFrame(analyses)

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("#### 📊 Distribution des Parasites")
            if HAS_PLOTLY and "parasite_detected" in df.columns:
                para_counts = df["parasite_detected"].value_counts()
                fig = px.pie(values=para_counts.values, names=para_counts.index, hole=0.4,
                             color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(height=350, template=plotly_template, margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            elif "parasite_detected" in df.columns:
                st.bar_chart(df["parasite_detected"].value_counts())

        with cc2:
            st.markdown("#### 📈 Niveaux de Confiance")
            if HAS_PLOTLY and "confidence" in df.columns:
                fig = px.histogram(df, x="confidence", nbins=20, color_discrete_sequence=[NEON["cyan"]])
                fig.update_layout(height=350, template=plotly_template,
                                  xaxis_title="Confiance (%)", yaxis_title="Nombre",
                                  margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
            elif "confidence" in df.columns:
                st.line_chart(df["confidence"].reset_index(drop=True))

        # Trends
        st.markdown("---")
        st.markdown("#### 📈 Tendances (30 jours)")
        trends = db_get_trends(30)
        if trends and HAS_PLOTLY:
            tdf = pd.DataFrame(trends)
            fig = px.line(tdf, x="day", y="count", color="parasite_detected",
                          markers=True, color_discrete_sequence=px.colors.qualitative.Set1)
            fig.update_layout(height=300, template=plotly_template,
                              xaxis_title="Date", yaxis_title="Nombre",
                              margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        elif not trends:
            st.info("Pas assez de donnees pour les tendances.")

        # History
        st.markdown("---")
        st.markdown("### 📋 Historique Complet")
        display_cols = [c for c in
                        ["id", "analysis_date", "patient_name", "parasite_detected", "confidence",
                         "risk_level", "is_reliable", "microscope_type", "magnification", "analyst_name",
                         "validated"]
                        if c in df.columns]
        st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)

        # Validation
        if user_has_role(2) and "validated" in df.columns:
            unvalidated = df[df["validated"] == 0]
            if not unvalidated.empty:
                st.markdown("#### ✅ Valider des Analyses")
                val_id = st.selectbox("ID a valider:", unvalidated["id"].tolist())
                if st.button(f"✅ Valider #{val_id}"):
                    db_validate_analysis(val_id, st.session_state.user_full_name)
                    db_log_activity(st.session_state.user_id, st.session_state.user_name, "Validated",
                                    f"Analysis #{val_id}")
                    st.success(f"✅ Analyse #{val_id} validee!")
                    st.rerun()

        # Export
        st.markdown("---")
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("⬇️ Exporter CSV", csv, "analyses.csv", "text/csv", use_container_width=True)
        with ex2:
            jd = df.to_json(orient='records', force_ascii=False).encode('utf-8')
            st.download_button("⬇️ Exporter JSON", jd, "analyses.json", "application/json", use_container_width=True)
        with ex3:
            try:
                buf = io.BytesIO()
                df.to_excel(buf, index=False, engine='openpyxl')
                st.download_button("⬇️ Exporter Excel", buf.getvalue(), "analyses.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)
            except Exception:
                st.info("📦 pip install openpyxl pour Excel")

        # Activity log
        if user_has_role(3):
            with st.expander("📜 Journal d'Activite"):
                logs = db_get_activity_log(100)
                if logs:
                    st.dataframe(pd.DataFrame(logs), use_container_width=True)
    else:
        st.markdown("""<div class='dm-card' style='text-align:center;padding:50px;'>
        <div style='font-size:4rem;'>📊</div><h3>Aucune donnee disponible</h3>
        <p style='opacity:0.5;'>Effectuez votre premiere analyse.</p></div>""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════╗
# ║            PAGE: QUIZ                     ║
# ╚══════════════════════════════════════════╝
elif current_page == "quiz":
    st.title("🧠 Quiz Parasitologique")
    st.markdown("<div class='dm-card'><p>Testez vos connaissances en parasitologie !</p></div>",
                unsafe_allow_html=True)

    questions = QUIZ_QUESTIONS
    qs = st.session_state.quiz_state

    with st.expander("🏆 Classement"):
        lb = db_get_leaderboard()
        if lb:
            for i, entry in enumerate(lb[:10]):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i + 1}"
                st.markdown(
                    f"{medal} **{entry['username']}** — {entry['score']}/{entry['total_questions']} ({entry['percentage']:.0f}%)")
        else:
            st.info("Aucun score enregistre.")

    if not qs["active"]:
        if st.button("🎮 Demarrer le Quiz", use_container_width=True, type="primary"):
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

            st.markdown(f"### Question {idx + 1}/{total_q}")
            st.progress(idx / total_q)

            cat = q.get("category", "")
            if cat:
                st.caption(f"📂 {cat}")

            st.markdown(f"<div class='dm-card'><h4>{q['q']}</h4></div>", unsafe_allow_html=True)

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
                if ad["correct"]:
                    st.success("✅ Bonne reponse !")
                else:
                    st.error(f"❌ Mauvaise reponse. → {q['options'][q['answer']]}")
                st.info(f"📖 {q['explanation']}")

                if st.button("➡️ Question Suivante", use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1
                    st.rerun()
        else:
            score = qs["score"]
            total_q = len(order)
            pct = int(score / total_q * 100) if total_q > 0 else 0

            if pct >= 80:
                emoji, msg = "🏆", "Excellent !"
            elif pct >= 60:
                emoji, msg = "👍", "Bien !"
            elif pct >= 40:
                emoji, msg = "📚", "Continuez !"
            else:
                emoji, msg = "💪", "Revisez !"

            st.markdown(f"""<div class='dm-card dm-card-green' style='text-align:center;'>
            <div style='font-size:4rem;'>{emoji}</div>
            <h2>Resultat Final</h2>
            <div class='dm-neon-title' style='font-size:3rem;'>{score}/{total_q}</div>
            <p style='font-size:1.2rem;'>{pct}% — {msg}</p>
            </div>""", unsafe_allow_html=True)

            db_save_quiz_score(st.session_state.user_id, st.session_state.user_name, score, total_q, pct)
            db_log_activity(st.session_state.user_id, st.session_state.user_name, "Quiz finished",
                            f"{score}/{total_q}")

            if st.button("🔄 Recommencer", use_container_width=True):
                for key in list(st.session_state.keys()):
                    if key.startswith("quiz_ans_"):
                        del st.session_state[key]
                st.session_state.quiz_state = {"current": 0, "score": 0, "answered": [], "active": False}
                st.rerun()

# ╔══════════════════════════════════════════╗
# ║            PAGE: CHATBOT                  ║
# ╚══════════════════════════════════════════╝
elif current_page == "chatbot":
    st.title("💬 Dr. DhiaBot - Assistant Medical IA")

    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "bot",
            "msg": "👋 Bonjour! Je suis **Dr. DhiaBot** 🤖 votre assistant parasitologique.\n\n💡 Essayez: amoeba, giardia, microscope, coloration, aide"
        })

    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='dm-chat-msg dm-chat-user'>👤 {msg['msg']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='dm-chat-msg dm-chat-bot'>🤖 {msg['msg']}</div>", unsafe_allow_html=True)

    user_input = st.chat_input("Posez votre question sur les parasites...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "msg": user_input})
        reply = chatbot_reply(user_input)
        st.session_state.chat_history.append({"role": "bot", "msg": reply})
        db_log_activity(st.session_state.user_id, st.session_state.user_name, "Chat", user_input[:80])
        st.rerun()

    st.markdown("---")
    st.markdown("**Questions rapides:**")
    qc = st.columns(6)
    quick_q = ["Amoeba?", "Giardia?", "Plasmodium?", "Microscope?", "Coloration?", "Aide"]
    for col, q in zip(qc, quick_q):
        with col:
            if st.button(q, use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "msg": q})
                st.session_state.chat_history.append({"role": "bot", "msg": chatbot_reply(q)})
                st.rerun()

    if st.button("🗑️ Effacer le chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# ╔══════════════════════════════════════════╗
# ║        PAGE: IMAGE COMPARISON             ║
# ╚══════════════════════════════════════════╝
elif current_page == "compare":
    st.title("🔄 Comparaison d'Images")
    st.markdown("<div class='dm-card dm-card-cyan'><p>Comparez deux images microscopiques.</p></div>",
                unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📷 Image 1 (Avant)")
        img1_file = st.file_uploader("Image 1", type=["jpg", "jpeg", "png"], key="cmp1")
    with c2:
        st.markdown("### 📷 Image 2 (Apres)")
        img2_file = st.file_uploader("Image 2", type=["jpg", "jpeg", "png"], key="cmp2")

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
                <div class='dm-metric-lbl'>Similarite</div></div>""", unsafe_allow_html=True)
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

            st.markdown("### 🔬 Comparaison des filtres")
            filters = [("Thermal", apply_thermal), ("Edges", apply_edge_detection),
                       ("Enhanced", apply_enhanced_contrast)]
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
    st.title("⚙️ Administration du Systeme")

    if not user_has_role(3):
        st.error("🔒 Acces reserve aux administrateurs.")
        st.stop()

    tab_users, tab_log, tab_system = st.tabs(["👥 Utilisateurs", "📜 Journal", "🖥️ Systeme"])

    with tab_users:
        st.markdown("### 👥 Gestion des Utilisateurs")
        users = db_get_all_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)

            st.markdown("#### 🔄 Activer/Desactiver")
            tc1, tc2 = st.columns(2)
            u_id = tc1.number_input("User ID", min_value=1, step=1)
            u_active = tc2.selectbox("Status", ["Actif", "Desactive"])
            if st.button("Appliquer"):
                db_toggle_user(u_id, u_active == "Actif")
                db_log_activity(st.session_state.user_id, st.session_state.user_name, "User toggle",
                                f"User {u_id} → {u_active}")
                st.success(f"✅ Utilisateur #{u_id} → {u_active}")
                st.rerun()

        st.markdown("---")
        st.markdown("### ➕ Creer un Utilisateur")
        with st.form("create_user_form"):
            nu = st.text_input("Nom d'utilisateur *")
            np_ = st.text_input("Mot de passe *", type="password")
            nf = st.text_input("Nom complet *")
            nr = st.selectbox("Role", list(ROLES.keys()))
            ns = st.text_input("Specialite", "Laboratoire")
            if st.form_submit_button("Creer", use_container_width=True):
                if nu and np_ and nf:
                    res = db_create_user(nu, np_, nf, nr, ns)
                    if "success" in res:
                        db_log_activity(st.session_state.user_id, st.session_state.user_name, "User created",
                                        f"{nu} ({nr})")
                        st.success(f"✅ Utilisateur '{nu}' cree!")
                        st.rerun()
                    else:
                        st.error(f"❌ {res.get('error', 'Erreur')}")
                else:
                    st.error("Tous les champs * sont obligatoires")

        st.markdown("---")
        st.markdown("### 🔑 Changer un mot de passe")
        cp_id = st.number_input("User ID", min_value=1, step=1, key="cp_id")
        cp_new = st.text_input("Nouveau mot de passe", type="password", key="cp_new")
        if st.button("Changer le mot de passe"):
            if cp_new:
                db_change_password(cp_id, cp_new)
                db_log_activity(st.session_state.user_id, st.session_state.user_name, "Password changed",
                                f"User #{cp_id}")
                st.success(f"✅ Mot de passe change pour #{cp_id}")

    with tab_log:
        st.markdown("### 📜 Journal d'Activite")
        logs = db_get_activity_log(300)
        if logs:
            ldf = pd.DataFrame(logs)
            if "username" in ldf.columns:
                users_list = ["Tous"] + ldf["username"].dropna().unique().tolist()
                filt = st.selectbox("Filtrer par utilisateur:", users_list)
                if filt != "Tous":
                    ldf = ldf[ldf["username"] == filt]
            st.dataframe(ldf, use_container_width=True)
        else:
            st.info("Aucune activite enregistree.")

    with tab_system:
        st.markdown("### 🖥️ Informations Systeme")
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            st.markdown(f"""<div class='dm-card dm-card-green'>
            <h4>🟢 Systeme OK</h4>
            <p>Version: {APP_VERSION}</p>
            <p>DB: SQLite</p>
            <p>Bcrypt: {'✅' if HAS_BCRYPT else '❌ (SHA256)'}</p>
            <p>Plotly: {'✅' if HAS_PLOTLY else '❌'}</p>
            <p>QR Code: {'✅' if HAS_QRCODE else '❌'}</p>
            </div>""", unsafe_allow_html=True)
        with sc2:
            total_users = len(db_get_all_users())
            total_analyses = db_get_stats()["total"]
            st.markdown(f"""<div class='dm-card dm-card-cyan'>
            <h4>📊 Statistiques</h4>
            <p>Utilisateurs: {total_users}</p>
            <p>Analyses: {total_analyses}</p>
            <p>Quiz: {len(db_get_leaderboard())}</p>
            </div>""", unsafe_allow_html=True)
        with sc3:
            db_size = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
            st.markdown(f"""<div class='dm-card'>
            <h4>💾 Stockage</h4>
            <p>Taille DB: {db_size:.1f} KB</p>
            <p>Emplacement: {os.path.abspath(DB_PATH)}</p>
            </div>""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════╗
# ║            PAGE: ABOUT                    ║
# ╚══════════════════════════════════════════╝
elif current_page == "about":
    st.title("ℹ️ A Propos du Projet")

    st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
    <h1 class='dm-neon-title'>🧬 DM SMART LAB AI</h1>
    <p style='font-size:1.1rem;font-family:Orbitron,sans-serif;'><b>v{APP_VERSION} — Professional Edition</b></p>
    <p style='opacity:0.5;'>Systeme de Diagnostic Parasitologique par IA</p>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""<div class='dm-card'>
    <h3>📖 {PROJECT_TITLE}</h3>
    <p style='line-height:1.8;opacity:0.8;'>Ce projet innovant utilise les technologies de Deep Learning et de Vision par Ordinateur pour assister les techniciens de laboratoire dans l'identification rapide et precise des parasites lors de l'examen parasitologique des selles a l'etat frais.</p>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class='dm-card dm-card-cyan'>
        <h3>👨‍🔬 Equipe de Developpement</h3><br>
        <p><b>🧑‍💻 {AUTHORS['dev1']['name']}</b><br><span style='opacity:0.5;'>{AUTHORS['dev1']['role']}</span></p><br>
        <p><b>🔬 {AUTHORS['dev2']['name']}</b><br><span style='opacity:0.5;'>{AUTHORS['dev2']['role']}</span></p><br>
        <p><b>Niveau:</b> 3eme Annee</p>
        <p><b>Specialite:</b> Laboratoire de Sante Publique</p>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class='dm-card'>
        <h3>🏫 Etablissement</h3><br>
        <p><b>{INSTITUTION['name']}</b></p>
        <p>📍 {INSTITUTION['city']}, {INSTITUTION['country']} 🇩🇿</p><br>
        <h4>🎯 Objectifs</h4>
        <ul>
        <li>Automatiser la lecture microscopique</li>
        <li>Reduire les erreurs diagnostiques</li>
        <li>Accelerer le processus d'analyse</li>
        <li>Assister les professionnels de sante</li>
        </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🛠️ Technologies Utilisees")
    tc = st.columns(8)
    techs = [("🐍", "Python", "Core"), ("🧠", "TensorFlow", "AI"), ("🎨", "Streamlit", "UI"),
             ("📊", "Plotly", "Charts"), ("🗄️", "SQLite", "Database"), ("🔒", "Bcrypt", "Security"),
             ("📄", "FPDF", "PDF"), ("📱", "QR Code", "Verify")]
    for col, (i, n, d) in zip(tc, techs):
        with col:
            st.markdown(f"""<div class="dm-metric"><span class="dm-metric-icon">{i}</span>
            <div class="dm-metric-val" style="font-size:0.85rem;">{n}</div>
            <div class="dm-metric-lbl">{d}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🌟 Features v6.0")
    feat_cols = st.columns(4)
    features = [
        ("🗄️", "SQLite DB", "Base persistante"),
        ("🔐", "Auth System", "Admin/Tech/Viewer"),
        ("🔒", "Bcrypt", "Chiffrement MDP"),
        ("📊", "Plotly Charts", "Graphiques pro"),
        ("🤖", "Smart Bot", "Chatbot complet"),
        ("🧠", "40+ Quiz", "Par categorie"),
        ("🎯", "Grad-CAM", "Heatmap IA"),
        ("📄", "PDF Pro", "QR + Signatures"),
        ("🔄", "Comparaison", "Before/After"),
        ("📈", "Tendances", "Predictions"),
        ("🔬", "Lab Info", "Microscope/Prep"),
        ("🎛️", "Image Tools", "Zoom/Filtres"),
        ("🌙", "Neon UI", "Design futuriste"),
        ("🔊", "Voice", "Assistant vocal"),
        ("⚙️", "Admin Panel", "Gestion complete"),
        ("✅", "Validation", "Workflow pro"),
    ]
    for i, (ic, name, desc) in enumerate(features):
        with feat_cols[i % 4]:
            st.markdown(f"""<div class='dm-card' style='padding:12px;text-align:center;'>
            <div style='font-size:1.6rem;'>{ic}</div>
            <p style='font-weight:700;margin:2px 0;font-size:0.83rem;'>{name}</p>
            <p style='font-size:0.68rem;opacity:0.5;'>{desc}</p>
            </div>""", unsafe_allow_html=True)

    st.caption(f"Fait avec ❤️ a {INSTITUTION['city']} — {INSTITUTION['year']} 🇩🇿")
