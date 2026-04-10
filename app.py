# ╔══════════════════════════════════════════════════════════════════════╗
# ║                      DM SMART LAB AI — PRO REBUILD                  ║
# ║                 Single-file Streamlit app.py (2026)                 ║
# ║  - Works on Streamlit Cloud + Windows                               ║
# ║  - FR / AR / EN + RTL                                               ║
# ║  - Scanner (AI model auto-detect) + Dashboard + Quiz + Chatbot      ║
# ║  - PDF + QR + Plotly (when available)                               ║
# ╚══════════════════════════════════════════════════════════════════════╝

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
from contextlib import contextmanager
from collections import defaultdict

# PDF
try:
    from fpdf import FPDF  # fpdf2 provides this import too
    HAS_FPDF = True
except Exception:
    HAS_FPDF = False

# Password hashing
try:
    import bcrypt
    HAS_BCRYPT = True
except Exception:
    HAS_BCRYPT = False

# Charts
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except Exception:
    HAS_PLOTLY = False

# QR
try:
    import qrcode
    HAS_QRCODE = True
except Exception:
    HAS_QRCODE = False

# TensorFlow (AI model)
try:
    import tensorflow as tf
    HAS_TF = True
except Exception:
    HAS_TF = False


# ============================================
# PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="🧬 DM Smart Lab AI — PRO",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "9.0 PRO (Rebuild)"
DB_PATH = "dm_smartlab_pro.db"
SECRET_KEY = "dm_smart_lab_2026_pro_rebuild_secret"

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)


ROLES = {
    "admin": {"level": 3, "icon": "👑", "label": {"fr": "Administrateur", "ar": "مدير النظام", "en": "Administrator"}},
    "technician": {"level": 2, "icon": "🔬", "label": {"fr": "Technicien", "ar": "تقني مخبر", "en": "Technician"}},
    "viewer": {"level": 1, "icon": "👁️", "label": {"fr": "Observateur", "ar": "مراقب", "en": "Viewer"}},
}


# ============================================
# i18n (we keep it compact هنا، ونكمل في PART 2)
# ============================================
TR = {
    "fr": {
        "app_title": "DM Smart Lab AI",
        "login_title": "Connexion sécurisée",
        "login_subtitle": "Système professionnel",
        "username": "Identifiant",
        "password": "Mot de passe",
        "connect": "SE CONNECTER",
        "logout": "Déconnexion",
        "home": "Accueil",
        "scan": "Scan & Analyse",
        "encyclopedia": "Encyclopédie",
        "dashboard": "Tableau de bord",
        "quiz": "Quiz",
        "chatbot": "DM Bot",
        "compare": "Comparaison",
        "admin": "Administration",
        "about": "À propos",
        "processing": "Traitement...",
        "analyzing": "Analyse...",
        "demo_mode": "Mode démo (pas de modèle trouvé)",
        "daily_tip": "Astuce du jour",
        "error_need_login": "Veuillez vous connecter.",
    },
    "ar": {
        "app_title": "DM Smart Lab AI",
        "login_title": "تسجيل دخول آمن",
        "login_subtitle": "نظام احترافي",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "connect": "دخول",
        "logout": "تسجيل الخروج",
        "home": "الرئيسية",
        "scan": "الفحص والتحليل",
        "encyclopedia": "الموسوعة",
        "dashboard": "لوحة التحكم",
        "quiz": "اختبار",
        "chatbot": "المساعد",
        "compare": "المقارنة",
        "admin": "الإدارة",
        "about": "حول",
        "processing": "جارٍ المعالجة...",
        "analyzing": "جارٍ التحليل...",
        "demo_mode": "وضع تجريبي (لا يوجد نموذج)",
        "daily_tip": "نصيحة اليوم",
        "error_need_login": "الرجاء تسجيل الدخول.",
    },
    "en": {
        "app_title": "DM Smart Lab AI",
        "login_title": "Secure Login",
        "login_subtitle": "Professional system",
        "username": "Username",
        "password": "Password",
        "connect": "SIGN IN",
        "logout": "Logout",
        "home": "Home",
        "scan": "Scan & Analyze",
        "encyclopedia": "Encyclopedia",
        "dashboard": "Dashboard",
        "quiz": "Quiz",
        "chatbot": "DM Bot",
        "compare": "Compare",
        "admin": "Admin",
        "about": "About",
        "processing": "Processing...",
        "analyzing": "Analyzing...",
        "demo_mode": "Demo mode (no model found)",
        "daily_tip": "Daily tip",
        "error_need_login": "Please login.",
    },
}


def t(key: str) -> str:
    lang = st.session_state.get("lang", "fr")
    return TR.get(lang, TR["fr"]).get(key, TR["fr"].get(key, key))


def tl(d) -> str:
    if not isinstance(d, dict):
        return str(d)
    lang = st.session_state.get("lang", "fr")
    return d.get(lang, d.get("fr", ""))


def is_rtl() -> bool:
    return st.session_state.get("lang", "fr") == "ar"


def now_iso() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


# ============================================
# CSS — PRO + fix input visibility (typing issue)
# ============================================
def apply_css():
    rtl = is_rtl()
    direction = "rtl" if rtl else "ltr"

    theme = st.session_state.get("theme", "dark")

    if theme == "light":
        bg = "#f5f7fb"
        card = "rgba(255,255,255,0.92)"
        text = "#0f172a"
        muted = "#64748b"
        border = "rgba(15,23,42,0.12)"
        accent = "#2563eb"
        accent2 = "#06b6d4"
    else:
        bg = "#060814"
        card = "rgba(11, 18, 38, 0.72)"
        text = "#e5e7eb"
        muted = "#9ca3af"
        border = "rgba(255,255,255,0.10)"
        accent = "#22d3ee"
        accent2 = "#a78bfa"

    st.markdown(
        f"""
        <style>
        html {{ direction: {direction}; }}
        .stApp {{
            background:
              radial-gradient(1200px 600px at 15% 10%, rgba(34,211,238,0.14), transparent 60%),
              radial-gradient(1000px 500px at 85% 15%, rgba(167,139,250,0.12), transparent 55%),
              linear-gradient(180deg, {bg}, {bg});
            color: {text};
        }}

        /* Critical fix: typing visibility */
        input, textarea {{
            color: {text} !important;
            caret-color: {accent} !important;
        }}
        ::placeholder {{
            color: {muted} !important;
            opacity: 0.9 !important;
        }}

        section[data-testid="stSidebar"] {{
            border-{ "left" if rtl else "right" }: 1px solid {border};
            background: linear-gradient(180deg, rgba(255,255,255,0.03), rgba(255,255,255,0.00));
        }}

        .dm-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 14px 40px rgba(0,0,0,0.18);
        }}

        .dm-title {{
            font-weight: 900;
            text-align: center;
            background: linear-gradient(90deg, {accent}, {accent2});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 0.02em;
        }}

        .dm-muted {{ color: {muted}; }}
        .dm-chip {{
            display:inline-block; padding: 4px 10px; border-radius:999px;
            border: 1px solid {border}; background: rgba(255,255,255,0.03);
            font-size: 0.78rem;
        }}

        /* Mobile */
        @media (max-width: 768px) {{
            .dm-card {{ padding: 12px; border-radius: 16px; }}
            h1 {{ font-size: 1.6rem !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================
# DB
# ============================================
@contextmanager
def db():
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _hp(pw: str) -> str:
    """hash password (bcrypt if available)"""
    pw = pw or ""
    if HAS_BCRYPT:
        h = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())
        return h.decode("utf-8")
    return hashlib.sha256((pw + SECRET_KEY).encode("utf-8")).hexdigest()


def _vp(pw: str, stored_hash: str) -> bool:
    """verify password supporting bcrypt or sha256 fallback"""
    pw = pw or ""
    stored_hash = stored_hash or ""

    if stored_hash.startswith("$2a$") or stored_hash.startswith("$2b$") or stored_hash.startswith("$2y$"):
        if not HAS_BCRYPT:
            return False
        try:
            return bcrypt.checkpw(pw.encode("utf-8"), stored_hash.encode("utf-8"))
        except Exception:
            return False

    # sha256 fallback
    return hashlib.sha256((pw + SECRET_KEY).encode("utf-8")).hexdigest() == stored_hash


def init_db():
    with db() as c:
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT UNIQUE NOT NULL,
              password_hash TEXT NOT NULL,
              full_name TEXT NOT NULL,
              role TEXT NOT NULL DEFAULT 'viewer',
              speciality TEXT,
              email TEXT,
              is_active INTEGER NOT NULL DEFAULT 1,
              created_at TEXT NOT NULL,
              last_login TEXT,
              login_count INTEGER NOT NULL DEFAULT 0,
              failed_attempts INTEGER NOT NULL DEFAULT 0,
              locked_until TEXT,
              achievements TEXT DEFAULT '[]',
              total_points INTEGER DEFAULT 0
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              analysis_date TEXT NOT NULL,
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
              is_reliable INTEGER NOT NULL,
              demo INTEGER NOT NULL,
              all_predictions TEXT,
              image_hash TEXT,
              model_name TEXT,
              processing_time REAL,
              validated INTEGER DEFAULT 0,
              validated_by TEXT,
              validation_date TEXT,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_scores(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              username TEXT,
              timestamp TEXT NOT NULL,
              score INTEGER NOT NULL,
              total_questions INTEGER NOT NULL,
              percentage REAL NOT NULL,
              category TEXT,
              difficulty TEXT,
              time_taken INTEGER DEFAULT 0
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              message TEXT NOT NULL,
              response TEXT NOT NULL,
              timestamp TEXT NOT NULL
            )
            """
        )

        c.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_log(
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              username TEXT,
              action TEXT NOT NULL,
              details TEXT,
              timestamp TEXT NOT NULL
            )
            """
        )

        # Indexes
        c.execute("CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(analysis_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_logs_time ON activity_log(timestamp)")

        # Default users (idempotent)
        defaults = [
            ("admin", "admin2026", "Administrateur Système", "admin", "Administration", "admin@dmlab.dz"),
            ("dhia", "dhia2026", "Sebbag Mohamed Dhia Eddine", "admin", "IA & Conception", "dhia@dmlab.dz"),
            ("mohamed", "mohamed2026", "Ben Sghir Mohamed", "technician", "Laboratoire", "mohamed@dmlab.dz"),
            ("demo", "demo123", "Utilisateur Démo", "viewer", "Demo", "demo@dmlab.dz"),
            ("tech1", "tech2026", "Technicien Labo 1", "technician", "Parasitologie", "tech1@dmlab.dz"),
        ]
        for u, p, fn, role, spec, email in defaults:
            exists = c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone()
            if not exists:
                c.execute(
                    """INSERT INTO users(username,password_hash,full_name,role,speciality,email,created_at)
                       VALUES(?,?,?,?,?,?,?)""",
                    (u, _hp(p), fn, role, spec, email, now_iso()),
                )


def db_log(user_id, username, action, details=""):
    try:
        with db() as c:
            c.execute(
                "INSERT INTO activity_log(user_id,username,action,details,timestamp) VALUES(?,?,?,?,?)",
                (user_id, username, action, details, now_iso()),
            )
    except Exception:
        pass


def has_role(level: int) -> bool:
    role = st.session_state.get("user_role", "viewer")
    return ROLES.get(role, ROLES["viewer"]).get("level", 1) >= level


def db_login(username: str, password: str):
    username = (username or "").strip()
    password = password or ""

    with db() as c:
        row = c.execute(
            "SELECT * FROM users WHERE username=? AND is_active=1",
            (username,),
        ).fetchone()
        if not row:
            return None

        if row["locked_until"]:
            try:
                lock_dt = datetime.fromisoformat(row["locked_until"])
                if datetime.now() < lock_dt:
                    minutes_left = int((lock_dt - datetime.now()).total_seconds() / 60) + 1
                    return {"error": "locked", "minutes": minutes_left}
            except Exception:
                pass

        if _vp(password, row["password_hash"]):
            c.execute(
                """UPDATE users SET last_login=?, login_count=login_count+1,
                   failed_attempts=0, locked_until=NULL WHERE id=?""",
                (now_iso(), row["id"]),
            )
            return dict(row)

        # wrong
        attempts = int(row["failed_attempts"] or 0) + 1
        locked_until = None
        if attempts >= MAX_LOGIN_ATTEMPTS:
            locked_until = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).replace(microsecond=0).isoformat()

        c.execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?", (attempts, locked_until, row["id"]))
        return {"error": "wrong", "attempts_left": max(0, MAX_LOGIN_ATTEMPTS - attempts)}


# ============================================
# Session defaults
# ============================================
DEFAULTS = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_full_name": "",
    "user_role": "viewer",
    "lang": "fr",
    "theme": "dark",
    "current_page": "home",
    "voice_text": None,
    "voice_lang": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# Init
init_db()
apply_css()


# ============================================
# Sidebar: Logo + Language + Theme + Nav + User
# ============================================
with st.sidebar:
    st.markdown(f"<h2 class='dm-title'>🧬 {t('app_title')}</h2>", unsafe_allow_html=True)
    st.caption(f"v{APP_VERSION}")

    # language
    lang_options = ["🇫🇷 Français", "🇩🇿 العربية", "🇬🇧 English"]
    current_idx = ["fr", "ar", "en"].index(st.session_state.lang)
    picked = st.selectbox("Language", lang_options, index=current_idx, label_visibility="collapsed")
    new_lang = "fr" if "🇫🇷" in picked else ("ar" if "🇩🇿" in picked else "en")
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    # theme
    if st.button("🌓 Toggle theme", use_container_width=True):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

    st.markdown("---")

    # nav (after login)
    if st.session_state.logged_in:
        menu = [
            ("home", f"🏠 {t('home')}"),
            ("scan", f"🔬 {t('scan')}"),
            ("encyclopedia", f"📘 {t('encyclopedia')}"),
            ("dashboard", f"📊 {t('dashboard')}"),
            ("quiz", f"🧠 {t('quiz')}"),
            ("chatbot", f"💬 {t('chatbot')}"),
            ("compare", f"🔄 {t('compare')}"),
        ]
        if has_role(3):
            menu.append(("admin", f"⚙️ {t('admin')}"))
        menu.append(("about", f"ℹ️ {t('about')}"))

        keys = [m[0] for m in menu]
        labels = [m[1] for m in menu]
        idx = keys.index(st.session_state.current_page) if st.session_state.current_page in keys else 0
        pick = st.radio("MENU", labels, index=idx, label_visibility="collapsed")
        st.session_state.current_page = keys[labels.index(pick)]

        st.markdown("---")
        role_info = ROLES.get(st.session_state.user_role, ROLES["viewer"])
        st.markdown(
            f"<div class='dm-card'>"
            f"<div style='font-size:2rem; line-height:1;'>{role_info['icon']}</div>"
            f"<div style='margin-top:8px;'><b>{st.session_state.user_full_name}</b><br>"
            f"<span class='dm-muted'>@{st.session_state.user_name}</span><br>"
            f"<span class='dm-chip'>{tl(role_info['label'])}</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            db_log(st.session_state.user_id, st.session_state.user_name, "Logout")
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.rerun()
    else:
        st.info(t("error_need_login"))


# ============================================
# Login page
# ============================================
if not st.session_state.logged_in:
    c1, c2, c3 = st.columns([1, 1.4, 1])
    with c2:
        st.markdown(
            f"<div class='dm-card' style='text-align:center;'>"
            f"<div style='font-size:3.2rem'>🔐</div>"
            f"<h2 class='dm-title' style='margin:0;'>{t('login_title')}</h2>"
            f"<p class='dm-muted' style='margin:6px 0 0 0;'>{t('login_subtitle')}</p>"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input(f"👤 {t('username')}", placeholder="admin / dhia / mohamed / demo / tech1")
            password = st.text_input(f"🔑 {t('password')}", type="password", placeholder="••••••••")
            submit = st.form_submit_button(f"🚀 {t('connect')}", use_container_width=True)

        st.caption("Test accounts: admin/admin2026 | dhia/dhia2026 | mohamed/mohamed2026 | demo/demo123 | tech1/tech2026")

        if submit:
            with st.spinner(t("processing")):
                res = db_login(username, password)

            if res is None:
                st.error("❌ User not found / المستخدم غير موجود")
                st.stop()

            if isinstance(res, dict) and res.get("error") == "locked":
                st.error(f"🔒 Account locked: {res.get('minutes', LOCKOUT_MINUTES)} min")
                st.stop()

            if isinstance(res, dict) and res.get("error") == "wrong":
                st.error(f"❌ Wrong password — {res.get('attempts_left', 0)} attempts left")
                st.stop()

            st.session_state.logged_in = True
            st.session_state.user_id = res["id"]
            st.session_state.user_name = res["username"]
            st.session_state.user_full_name = res["full_name"]
            st.session_state.user_role = res["role"]
            st.session_state.current_page = "home"
            db_log(res["id"], res["username"], "Login")

            st.success(f"✅ {res['full_name']}")
            time.sleep(0.6)
            st.rerun()

    st.stop()


# ============================================
# Authenticated area entrypoint (pages later)
# ============================================
selected_page = st.session_state.current_page
# ============================================================
# PRO DATA + AI ENGINE + IMAGE TOOLS + VOICE + CHATBOT KB
# ============================================================

# ---- Extend translations needed by next pages ----
TR["fr"].update({
    "patient_name": "Nom *",
    "patient_firstname": "Prénom",
    "age": "Âge",
    "sex": "Sexe",
    "male": "Homme",
    "female": "Femme",
    "weight": "Poids (kg)",
    "sample_type": "Type d'échantillon",
    "microscope": "Microscope",
    "magnification": "Grossissement",
    "preparation": "Préparation",
    "technician": "Technicien",
    "notes": "Notes",
    "upload_hint": "Téléversez une image (JPG/PNG) prise au microscope.",
    "camera_hint": "Utilisez la caméra si disponible.",
    "result_card": "Résultat IA",
    "low_conf_warn": "Confiance faible: résultat à vérifier.",
    "save_db": "Enregistrer dans la base",
    "saved_ok": "Analyse enregistrée",
    "download_pdf": "Télécharger PDF",
    "download_report": "Télécharger rapport",
    "export_excel": "Exporter Excel",
    "history": "Historique",
    "search": "Rechercher",
    "no_results": "Aucun résultat",
    "quick_actions": "Actions rapides",
    "new_analysis": "Nouvelle analyse",
    "listen": "Écouter",
    "stop_voice": "Stop",
    "all_probabilities": "Toutes les probabilités",
    "risk_none": "Négatif",
    "risk_low": "Faible",
    "risk_medium": "Moyen",
    "risk_high": "Élevé",
    "risk_critical": "URGENCE",
    "chat_not_found": "Je n'ai pas trouvé de réponse exacte. Essayez: amoeba, giardia, plasmodium, microscope, coloration, concentration, traitement, aide.",
})

TR["ar"].update({
    "patient_name": "اللقب *",
    "patient_firstname": "الاسم",
    "age": "العمر",
    "sex": "الجنس",
    "male": "ذكر",
    "female": "أنثى",
    "weight": "الوزن (كغ)",
    "sample_type": "نوع العينة",
    "microscope": "المجهر",
    "magnification": "التكبير",
    "preparation": "التحضير",
    "technician": "التقني",
    "notes": "ملاحظات",
    "upload_hint": "ارفع صورة (JPG/PNG) ملتقطة بالمجهر.",
    "camera_hint": "استعمل الكاميرا إن كانت متاحة.",
    "result_card": "نتيجة الذكاء الاصطناعي",
    "low_conf_warn": "ثقة منخفضة: النتيجة تحتاج مراجعة.",
    "save_db": "حفظ في قاعدة البيانات",
    "saved_ok": "تم حفظ التحليل",
    "download_pdf": "تحميل PDF",
    "download_report": "تحميل التقرير",
    "export_excel": "تصدير Excel",
    "history": "السجل",
    "search": "بحث",
    "no_results": "لا توجد نتائج",
    "quick_actions": "إجراءات سريعة",
    "new_analysis": "تحليل جديد",
    "listen": "استماع",
    "stop_voice": "إيقاف",
    "all_probabilities": "كل الاحتمالات",
    "risk_none": "سلبي",
    "risk_low": "منخفض",
    "risk_medium": "متوسط",
    "risk_high": "مرتفع",
    "risk_critical": "طوارئ",
    "chat_not_found": "لم أجد جواباً مطابقاً. جرّب: amoeba, giardia, plasmodium, microscope, coloration, concentration, traitement, aide.",
})

TR["en"].update({
    "patient_name": "Last name *",
    "patient_firstname": "First name",
    "age": "Age",
    "sex": "Sex",
    "male": "Male",
    "female": "Female",
    "weight": "Weight (kg)",
    "sample_type": "Sample type",
    "microscope": "Microscope",
    "magnification": "Magnification",
    "preparation": "Preparation",
    "technician": "Technician",
    "notes": "Notes",
    "upload_hint": "Upload a microscope image (JPG/PNG).",
    "camera_hint": "Use camera if available.",
    "result_card": "AI Result",
    "low_conf_warn": "Low confidence: needs verification.",
    "save_db": "Save to database",
    "saved_ok": "Analysis saved",
    "download_pdf": "Download PDF",
    "download_report": "Download report",
    "export_excel": "Export Excel",
    "history": "History",
    "search": "Search",
    "no_results": "No results",
    "quick_actions": "Quick actions",
    "new_analysis": "New analysis",
    "listen": "Listen",
    "stop_voice": "Stop",
    "all_probabilities": "All probabilities",
    "risk_none": "Negative",
    "risk_low": "Low",
    "risk_medium": "Medium",
    "risk_high": "High",
    "risk_critical": "EMERGENCY",
    "chat_not_found": "No exact answer found. Try: amoeba, giardia, plasmodium, microscope, staining, concentration, treatment, help.",
})


# ---- Utility: risk mapping ----
def risk_color(level: str) -> str:
    return {
        "critical": "#ef4444",
        "high": "#fb7185",
        "medium": "#f59e0b",
        "low": "#22c55e",
        "none": "#10b981",
    }.get(level or "none", "#94a3b8")


def risk_label(level: str) -> str:
    level = (level or "none").lower()
    key = f"risk_{level}"
    return t(key)


def risk_percentage(level: str) -> int:
    return {
        "critical": 100,
        "high": 80,
        "medium": 50,
        "low": 25,
        "none": 0,
    }.get((level or "none").lower(), 0)


def fmt_dt(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        return datetime.fromisoformat(iso_str).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_str


def time_ago(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str)
        diff = datetime.now() - dt
        if diff.days > 365:
            return f"{diff.days//365}y"
        if diff.days > 30:
            return f"{diff.days//30}mo"
        if diff.days > 0:
            return f"{diff.days}d"
        s = diff.seconds
        if s > 3600:
            return f"{s//3600}h"
        if s > 60:
            return f"{s//60}min"
        return "now"
    except Exception:
        return ""


# ---- Reference lists (as your old program) ----
MICROSCOPE_TYPES = [
    "Microscope Optique Standard",
    "Microscope Binoculaire",
    "Microscope Trinoculaire",
    "Microscope Inversé",
    "Microscope à Fluorescence",
    "Microscope Contraste de Phase",
    "Microscope Fond Noir",
    "Microscope Numérique",
    "Microscope Confocal",
    "Microscope Électronique",
]

MAGNIFICATIONS = ["x4", "x10", "x20", "x40", "x60", "x100 (Immersion)", "x400", "x1000"]

PREPARATION_TYPES = [
    "État Frais (Direct)",
    "Coloration au Lugol",
    "MIF (Merthiolate-Iode-Formol)",
    "Concentration Ritchie (Formol-Éther)",
    "Kato-Katz (Quantitatif)",
    "Coloration MGG (May-Grünwald-Giemsa)",
    "Coloration Giemsa",
    "Ziehl-Neelsen Modifié",
    "Coloration Trichrome",
    "Goutte Épaisse",
    "Frottis Mince",
    "Scotch-Test (Graham)",
    "Technique Baermann",
    "Flottation Willis",
    "Technique Knott",
    "Coloration Hématoxyline Ferrique",
]

SAMPLES = {
    "fr": ["Selles", "Sang (Frottis)", "Sang (Goutte épaisse)", "Urines", "LCR", "Biopsie Cutanée", "Crachat", "Aspiration Duodénale", "Liquide Péritonéal", "Autre"],
    "ar": ["براز", "دم (لطاخة)", "دم (قطرة سميكة)", "بول", "سائل دماغي شوكي", "خزعة جلدية", "بلغم", "شفط اثني عشري", "سائل بريتوني", "أخرى"],
    "en": ["Stool", "Blood (Smear)", "Blood (Thick drop)", "Urine", "CSF", "Skin Biopsy", "Sputum", "Duodenal Aspirate", "Peritoneal Fluid", "Other"],
}


# ============================================================
# PARASITE DB (kept content style from your previous app)
# ============================================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "sci": "Entamoeba histolytica",
        "morph": {
            "fr": "Kyste sphérique (10-15µm) à 4 noyaux, corps chromatoïde en cigare. Trophozoïte (20-40µm) avec pseudopodes et hématies phagocytées.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 أنوية، جسم كروماتيني سيجاري. طور نشط (20-40) مع أقدام كاذبة وكريات حمراء مبتلعة.",
            "en": "Spherical cyst (10-15µm) with 4 nuclei, cigar-shaped chromatoid body. Trophozoite (20-40µm) with pseudopods and phagocytosed RBCs.",
        },
        "desc": {
            "fr": "Protozoaire responsable de l'amibiase intestinale et extra-intestinale. Transmission féco-orale.",
            "ar": "طفيلي أولي يسبب الأميبيا المعوية والخارج معوية. انتقال فم-براز.",
            "en": "Protozoan causing intestinal and extra-intestinal amebiasis. Fecal-oral transmission.",
        },
        "funny": {
            "fr": "Le ninja des intestins ! Il mange des globules rouges au petit-déjeuner !",
            "ar": "نينجا الأمعاء! يأكل كريات الدم الحمراء في الفطور!",
            "en": "The intestinal ninja! Eats red blood cells for breakfast!",
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Métronidazole 500mg x3/j (7-10j) + amoebicide de contact. Contrôle EPS J15/J30.",
            "ar": "ميترونيدازول 500 ملغ 3 مرات/يوم (7-10 أيام) + أميبيسيد تلامسي. متابعة 15/30 يوم.",
            "en": "Metronidazole 500mg x3/d (7-10d) + contact amoebicide. Follow-up D15/D30.",
        },
        "tests": ["Sérologie amibienne", "Échographie hépatique", "NFS+CRP", "PCR Entamoeba", "Scanner abdominal"],
        "icon": "🔴",
        "cycle": {
            "fr": "Kyste ingéré → Excystation → Trophozoïte → Invasion → Enkystement → Émission",
            "ar": "كيس مبتلع → انفكاس → طور نشط → غزو → تكيس → طرح",
            "en": "Ingested cyst → Excystation → Trophozoite → Invasion → Encystation → Emission",
        },
        "keys": {
            "fr": "Seule histolytica phagocyte les hématies\nKyste 4 noyaux (vs E. coli 8)\nCorps chromatoïdes en cigare",
            "ar": "فقط histolytica تبتلع الكريات\nكيس 4 أنوية (مقابل 8 لـ E. coli)\nأجسام كروماتينية سيجارية",
            "en": "Only histolytica phagocytoses RBCs\n4 nuclei cyst (vs E. coli 8)\nCigar chromatoid bodies",
        },
    },
    "Giardia": {
        "sci": "Giardia lamblia (intestinalis)",
        "morph": {
            "fr": "Trophozoïte piriforme (12-15µm), 2 noyaux (face de hibou), disque adhésif, 4 paires de flagelles. Kyste (8-12µm) à 4 noyaux.",
            "ar": "طور نشط كمثري (12-15) بنواتين (وجه البومة) وقرص لاصق. الكيس 4 أنوية.",
            "en": "Pear-shaped trophozoite (12-15µm), 2 nuclei (owl face), adhesive disk. Cyst has 4 nuclei.",
        },
        "desc": {
            "fr": "Flagellé du duodénum. Diarrhée graisseuse, malabsorption. Transmission hydrique.",
            "ar": "طفيلي سوطي بالاثني عشر. إسهال دهني وسوء امتصاص. انتقال عبر الماء.",
            "en": "Duodenal flagellate. Greasy diarrhea, malabsorption. Waterborne.",
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes ! Un touriste qui refuse de partir !",
            "ar": "ينظر إليك كأنه بنظارة! سائح يرفض المغادرة!",
            "en": "Stares at you like wearing sunglasses! A tourist that won't leave!",
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "advice": {
            "fr": "Métronidazole 250mg x3/j (5j) OU Tinidazole 2g dose unique.",
            "ar": "ميترونيدازول 250 ملغ 3 مرات/يوم (5 أيام) أو تينيدازول 2غ جرعة واحدة.",
            "en": "Metronidazole 250mg x3/d (5d) OR Tinidazole 2g single dose.",
        },
        "tests": ["Ag Giardia ELISA", "EPS x3", "PCR Giardia"],
        "icon": "🟠",
        "cycle": {
            "fr": "Kyste ingéré → Excystation → Trophozoïte → Adhésion → Multiplication → Enkystement",
            "ar": "كيس مبتلع → انفكاس → طور نشط → التصاق → تكاثر → تكيس",
            "en": "Ingested cyst → Excystation → Trophozoite → Adhesion → Multiplication → Encystation",
        },
        "keys": {
            "fr": "2 noyaux = face de hibou\nMobilité feuille morte\nKyste à 4 noyaux",
            "ar": "نواتان = وجه البومة\nحركة ورقة ميتة\nكيس 4 أنوية",
            "en": "2 nuclei = owl face\nFalling leaf motility\n4 nuclei cyst",
        },
    },
    "Leishmania": {
        "sci": "Leishmania infantum / major / tropica",
        "morph": {
            "fr": "Amastigotes (2-5µm) dans macrophages. Noyau + kinétoplaste (MGG/Giemsa).",
            "ar": "أماستيغوت (2-5) داخل البلاعم. نواة + كينيتوبلاست (MGG/جيمزا).",
            "en": "Amastigotes (2-5µm) in macrophages. Nucleus + kinetoplast (MGG/Giemsa).",
        },
        "desc": {
            "fr": "Transmis par phlébotome. Formes cutanée ou viscérale.",
            "ar": "ينتقل بذبابة الرمل. جلدية أو حشوية.",
            "en": "Sandfly-transmitted. Cutaneous or visceral forms.",
        },
        "funny": {
            "fr": "Petit mais costaud ! Il squatte les macrophages !",
            "ar": "صغير لكنه قوي! يحتل البلاعم!",
            "en": "Small but tough! Squats macrophages!",
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Cutanée: antimoniaux (selon protocole). Viscérale: Amphotericine B liposomale. Déclaration selon contexte.",
            "ar": "جلدية: علاج حسب البروتوكول. حشوية: أمفوتيريسين B.",
            "en": "Cutaneous: antimonials per protocol. Visceral: liposomal Amphotericin B.",
        },
        "tests": ["Biopsie+MGG", "PCR Leishmania", "NFS", "Sérologie"],
        "icon": "🔴",
        "cycle": {
            "fr": "Piqûre phlébotome → Promastigotes → Macrophages → Amastigotes → Multiplication",
            "ar": "لدغة ذبابة الرمل → بروماستيغوت → بلاعم → أماستيغوت → تكاثر",
            "en": "Sandfly bite → Promastigotes → Macrophages → Amastigotes → Multiplication",
        },
        "keys": {
            "fr": "Noyau + kinétoplaste\nIntracellulaire\nMGG/Giemsa",
            "ar": "نواة + كينيتوبلاست\nداخل خلوي\nMGG/جيمزا",
            "en": "Nucleus + kinetoplast\nIntracellular\nMGG/Giemsa",
        },
    },
    "Plasmodium": {
        "sci": "Plasmodium falciparum / vivax / ovale / malariae",
        "morph": {
            "fr": "Anneau (bague à chaton). P. falciparum: gamétocytes en banane. GE plus sensible.",
            "ar": "حلقة (خاتم). falciparum: خلايا جنسية موزية. القطرة السميكة أكثر حساسية.",
            "en": "Ring form. P. falciparum: banana gametocytes. Thick drop more sensitive.",
        },
        "desc": {
            "fr": "URGENCE médicale. Paludisme. Anophèle femelle.",
            "ar": "طوارئ طبية: ملاريا. أنثى الأنوفيل.",
            "en": "MEDICAL EMERGENCY: malaria. Female Anopheles.",
        },
        "funny": {
            "fr": "Il demande le mariage à tes globules ! Gamétocytes banane = clown du microscope !",
            "ar": "يخطب كرياتك! خلايا موزية = مهرج المجهر!",
            "en": "Proposes to your RBCs! Banana gametocytes = microscope clown!",
        },
        "risk": "critical",
        "risk_d": {"fr": "URGENCE", "ar": "طوارئ", "en": "EMERGENCY"},
        "advice": {
            "fr": "Hospitalisation si grave. ACT selon protocole. Surveiller parasitémie et complications.",
            "ar": "دخول المستشفى إذا خطير. علاج حسب البروتوكول. مراقبة الطفيليات والمضاعفات.",
            "en": "Hospitalize if severe. ACT per protocol. Monitor parasitemia/complications.",
        },
        "tests": ["TDR Paludisme", "Frottis + Goutte épaisse", "Parasitémie", "NFS", "Bilan hépatique/rénal", "Glycémie"],
        "icon": "🚨",
        "cycle": {
            "fr": "Piqûre anophèle → Sporozoïtes → Foie → Mérozoïtes → Hématies → Gamétocytes",
            "ar": "لدغة الأنوفيل → سبوروزويت → كبد → ميروزويت → كريات حمراء → خلايا جنسية",
            "en": "Anopheles bite → Sporozoites → Liver → Merozoites → RBCs → Gametocytes",
        },
        "keys": {
            "fr": "URGENCE <2h\nGE 10x plus sensible\nBanane = falciparum\n>2% parasitémie = grave",
            "ar": "طوارئ < ساعتين\nالقطرة السميكة أكثر حساسية\nالموز = falciparum\nأكثر من 2% = خطير",
            "en": "URGENT <2h\nThick drop 10x sensitivity\nBanana = falciparum\n>2% parasitemia = severe",
        },
    },
    "Trypanosoma": {
        "sci": "Trypanosoma brucei / cruzi",
        "morph": {
            "fr": "Forme allongée (15-30µm), flagelle, membrane ondulante, kinétoplaste.",
            "ar": "شكل طويل (15-30) مع سوط وغشاء متموج وكينيتوبلاست.",
            "en": "Elongated form (15-30µm) with flagellum, undulating membrane, kinetoplast.",
        },
        "desc": {
            "fr": "Maladie du sommeil (tsé-tsé) ou Chagas (triatome).",
            "ar": "مرض النوم (تسي تسي) أو شاغاس (بق ثلاثي).",
            "en": "Sleeping sickness (tsetse) or Chagas (triatomine).",
        },
        "funny": {
            "fr": "Il court avec sa membrane ondulante !",
            "ar": "يجري بغشائه المتموج!",
            "en": "Runs with its undulating membrane!",
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Prise en charge spécialisée. PL pour stadification si maladie du sommeil.",
            "ar": "علاج تخصصي. بزل قطني لتحديد المرحلة عند مرض النوم.",
            "en": "Specialized management. LP for staging in sleeping sickness.",
        },
        "tests": ["Ponction lombaire", "Sérologie", "NFS"],
        "icon": "🔴",
        "cycle": {"fr": "Vecteur → Sang → (SNC selon stade)", "ar": "ناقل → دم → (جهاز عصبي حسب المرحلة)", "en": "Vector → Blood → (CNS by stage)"},
        "keys": {"fr": "Membrane ondulante\nKinétoplaste", "ar": "غشاء متموج\nكينيتوبلاست", "en": "Undulating membrane\nKinetoplast"},
    },
    "Schistosoma": {
        "sci": "Schistosoma haematobium / mansoni",
        "morph": {
            "fr": "Œuf 115-170µm: éperon terminal (haematobium) ou latéral (mansoni).",
            "ar": "بيضة 115-170: شوكة طرفية (haematobium) أو جانبية (mansoni).",
            "en": "Egg 115-170µm: terminal spine (haematobium) or lateral spine (mansoni).",
        },
        "desc": {
            "fr": "Bilharziose. Uro-génitale (haematobium) ou intestinale/hépatique (mansoni).",
            "ar": "بلهارسيا بولية تناسلية أو معوية/كبدية.",
            "en": "Schistosomiasis: urogenital or intestinal/hepatic.",
        },
        "funny": {"fr": "L'œuf avec un dard !", "ar": "بيضة بشوكة!", "en": "An egg with a stinger!"},
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "advice": {"fr": "Praziquantel حسب الجرعة الموصى بها.", "ar": "برازيكوانتيل حسب الجرعة.", "en": "Praziquantel per recommended dosing."},
        "tests": ["ECBU (midi)", "NFS (éosinophilie)", "Sérologie"],
        "icon": "🟠",
        "cycle": {"fr": "Œuf → Mollusque → Cercaire → Pénétration cutanée → Vers adultes", "ar": "بيضة → حلزون → سركاريا → اختراق الجلد → ديدان", "en": "Egg → Snail → Cercaria → Skin penetration → Adult worms"},
        "keys": {"fr": "Éperon terminal vs latéral\nUrines de midi (haematobium)", "ar": "شوكة طرفية/جانبية\nبول الظهيرة", "en": "Terminal vs lateral spine\nMidday urine (haematobium)"},
    },
    "Negative": {
        "sci": "N/A",
        "morph": {"fr": "Absence d'éléments parasitaires.", "ar": "غياب عناصر طفيلية.", "en": "No parasitic elements."},
        "desc": {
            "fr": "Un seul examen négatif n'exclut pas. Répéter selon contexte clinique.",
            "ar": "فحص سلبي واحد لا ينفي. كرر حسب الحالة.",
            "en": "Single negative does not exclude. Repeat per clinical context.",
        },
        "funny": {"fr": "Rien à signaler… mais les parasites jouent à cache-cache !", "ar": "لا شيء… لكن الطفيليات تختبئ!", "en": "Nothing found… but parasites play hide-and-seek!"},
        "risk": "none",
        "risk_d": {"fr": "Négatif", "ar": "سلبي", "en": "Negative"},
        "advice": {"fr": "RAS. Répéter si suspicion.", "ar": "لا شيء. كرر إذا اشتباه.", "en": "No action. Repeat if suspicion."},
        "tests": ["Répéter x3 si suspicion", "Techniques de concentration"],
        "icon": "🟢",
        "cycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "keys": {"fr": "Direct + concentration\nRépéter x3", "ar": "مباشر + تركيز\nكرر 3 مرات", "en": "Direct + concentration\nRepeat x3"},
    },
}

CLASS_NAMES = list(PARASITE_DB.keys())

RISK_MAP = {
    "Plasmodium": "critical",
    "Amoeba (E. histolytica)": "high",
    "Leishmania": "high",
    "Trypanosoma": "high",
    "Giardia": "medium",
    "Schistosoma": "medium",
    "Negative": "none",
}


# ============================================================
# AI MODEL LOADER (auto detect .keras/.h5/.tflite)
# ============================================================
@st.cache_resource(show_spinner=False)
def load_model():
    model = None
    model_name = None
    model_type = None

    if not HAS_TF:
        return None, None, None

    # Prefer tflite (lighter) if exists
    exts = [".tflite", ".keras", ".h5"]
    files = []
    for fn in os.listdir("."):
        low = fn.lower()
        if any(low.endswith(e) for e in exts) and os.path.isfile(fn):
            files.append(fn)

    # reorder so tflite first
    files.sort(key=lambda x: 0 if x.lower().endswith(".tflite") else 1)

    for fn in files:
        try:
            if fn.lower().endswith(".tflite"):
                interpreter = tf.lite.Interpreter(model_path=fn)
                interpreter.allocate_tensors()
                model = interpreter
                model_name = fn
                model_type = "tflite"
                break
            else:
                model = tf.keras.models.load_model(fn, compile=False)
                model_name = fn
                model_type = "keras"
                break
        except Exception:
            continue

    return model, model_name, model_type


def _preprocess_image_pil(img: Image.Image) -> np.ndarray:
    img = ImageOps.fit(img.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
    arr = np.asarray(img).astype(np.float32)
    # normalization to [-1, 1] (same style as Teachable Machine models)
    arr = arr / 127.5 - 1.0
    arr = np.expand_dims(arr, 0)
    return arr


def predict_image(model, model_type, image: Image.Image, seed=None):
    """
    Returns:
    {
      label, conf(int), preds(dict), rel(bool), demo(bool), risk(str)
    }
    """
    result = {"label": "Negative", "conf": 0, "preds": {}, "rel": False, "demo": True, "risk": "none"}

    # --- Demo fallback (always works) ---
    if model is None or (not HAS_TF):
        if seed is None:
            seed = random.randint(0, 999999)
        rng = random.Random(seed)

        label = rng.choice(CLASS_NAMES)
        conf = rng.randint(55, 98)
        preds = {}
        rest = 100.0 - conf
        for cls in CLASS_NAMES:
            if cls == label:
                preds[cls] = float(conf)
            else:
                preds[cls] = round(rng.uniform(0, rest / max(1, len(CLASS_NAMES) - 1)), 1)

        result.update({
            "label": label,
            "conf": int(conf),
            "preds": preds,
            "rel": conf >= CONFIDENCE_THRESHOLD,
            "demo": True,
            "risk": RISK_MAP.get(label, "none"),
        })
        return result

    # --- Real prediction ---
    try:
        x = _preprocess_image_pil(image)

        if model_type == "tflite":
            inp = model.get_input_details()[0]
            out = model.get_output_details()[0]
            model.set_tensor(inp["index"], x)
            model.invoke()
            y = model.get_tensor(out["index"])[0]
        else:
            y = model.predict(x, verbose=0)[0]

        y = np.array(y).astype(np.float32)
        if y.ndim != 1:
            y = y.reshape(-1)

        # handle mismatch lengths safely
        n = min(len(y), len(CLASS_NAMES))
        y = y[:n]
        # softmax safety (in case outputs are logits)
        if np.max(y) > 1.0 or np.min(y) < 0.0:
            exp = np.exp(y - np.max(y))
            y = exp / (np.sum(exp) + 1e-9)

        idx = int(np.argmax(y))
        label = CLASS_NAMES[idx] if idx < len(CLASS_NAMES) else "Negative"
        conf = int(float(y[idx]) * 100)

        preds = {CLASS_NAMES[i]: round(float(y[i]) * 100, 1) for i in range(n)}

        result.update({
            "label": label,
            "conf": conf,
            "preds": preds,
            "rel": conf >= CONFIDENCE_THRESHOLD,
            "demo": False,
            "risk": RISK_MAP.get(label, "none"),
        })
        return result

    except Exception:
        # fallback demo if anything breaks
        return predict_image(None, None, image, seed=seed)


# ============================================================
# IMAGE TOOLS (filters + heatmap + compare)
# ============================================================
def adjust_image(img, brightness=1.0, contrast=1.0, saturation=1.0):
    out = img.copy().convert("RGB")
    out = ImageEnhance.Brightness(out).enhance(brightness)
    out = ImageEnhance.Contrast(out).enhance(contrast)
    out = ImageEnhance.Color(out).enhance(saturation)
    return out


def zoom_image(img, level: float):
    if level <= 1.0:
        return img
    w, h = img.size
    new_w, new_h = int(w / level), int(h / level)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    return img.crop((left, top, left + new_w, top + new_h)).resize((w, h), Image.LANCZOS)


def thermal_view(img):
    gray = ImageOps.grayscale(ImageEnhance.Contrast(img).enhance(1.6)).filter(ImageFilter.GaussianBlur(1))
    return ImageOps.colorize(gray, black="navy", white="yellow", mid="red")


def edges_filter(img):
    return ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)


def enhanced_filter(img):
    return ImageEnhance.Contrast(ImageEnhance.Sharpness(img).enhance(2.0)).enhance(1.8)


def negative_filter(img):
    return ImageOps.invert(img.convert("RGB"))


def emboss_filter(img):
    return img.filter(ImageFilter.EMBOSS)


def generate_heatmap(image: Image.Image, seed=None):
    """Heuristic heatmap (visual) - fast and stable"""
    img = image.copy().convert("RGB")
    w, h = img.size

    if seed is None:
        seed = int(hashlib.md5(img.tobytes()[:2000]).hexdigest()[:8], 16)
    rng = random.Random(seed)

    edges = np.array(ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)).astype(np.float32)

    block = max(24, min(w, h) // 12)
    best_x, best_y = w // 2, h // 2
    best = -1

    step = max(8, block // 2)
    for y in range(0, h - block, step):
        for x in range(0, w - block, step):
            score = float(np.mean(edges[y:y + block, x:x + block]))
            if score > best:
                best = score
                best_x, best_y = x + block // 2, y + block // 2

    best_x = max(50, min(w - 50, best_x + rng.randint(-w // 10, w // 10)))
    best_y = max(50, min(h - 50, best_y + rng.randint(-h // 10, h // 10)))

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    max_r = min(w, h) // 3

    for r in range(max_r, 0, -2):
        alpha = int(200 * (1 - r / max_r))
        ratio = r / max_r
        if ratio > 0.65:
            col = (0, 255, 120, alpha // 4)
        elif ratio > 0.35:
            col = (255, 255, 0, alpha // 2)
        else:
            col = (255, 0, 60, alpha)
        d.ellipse([best_x - r, best_y - r, best_x + r, best_y + r], fill=col)

    out = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return out


def compare_images(img1: Image.Image, img2: Image.Image):
    """Returns MSE + simple SSIM-like score (no extra deps)"""
    a = np.array(img1.convert("RGB").resize((128, 128))).astype(np.float32)
    b = np.array(img2.convert("RGB").resize((128, 128))).astype(np.float32)

    mse = float(np.mean((a - b) ** 2))

    mean1, mean2 = float(np.mean(a)), float(np.mean(b))
    std1, std2 = float(np.std(a)), float(np.std(b))
    std12 = float(np.mean((a - mean1) * (b - mean2)))
    c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    ssim = ((2 * mean1 * mean2 + c1) * (2 * std12 + c2)) / ((mean1**2 + mean2**2 + c1) * (std1**2 + std2**2 + c2) + 1e-9)
    ssim = float(max(-1.0, min(1.0, ssim)))

    similarity = float(max(0.0, min(100.0, ssim * 100.0)))
    return {"mse": round(mse, 2), "ssim": round(ssim, 4), "similarity": round(similarity, 1)}


def pixel_difference(img1: Image.Image, img2: Image.Image):
    a = np.array(img1.convert("RGB").resize((256, 256))).astype(np.int16)
    b = np.array(img2.convert("RGB").resize((256, 256))).astype(np.int16)
    diff = np.abs(a - b).astype(np.uint8)
    diff = np.clip(diff * 3, 0, 255).astype(np.uint8)
    return Image.fromarray(diff)


def get_histogram(img: Image.Image):
    r, g, b = img.convert("RGB").split()
    return {"red": list(r.histogram()), "green": list(g.histogram()), "blue": list(b.histogram())}


# ============================================================
# VOICE — Web Speech API (3 languages)
# ============================================================
def render_voice_player():
    if st.session_state.get("voice_text"):
        txt = str(st.session_state.voice_text)
        txt = txt.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"').replace("\n", " ").replace("\r", " ")
        lang = st.session_state.get("voice_lang") or st.session_state.get("lang", "fr")
        lang_code = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(lang, "fr-FR")

        st.components.v1.html(
            f"""
            <div style="display:none">
              <script>
                (function() {{
                  try {{
                    if ('speechSynthesis' in window) {{
                      window.speechSynthesis.cancel();
                      setTimeout(function(){{
                        var u = new SpeechSynthesisUtterance('{txt}');
                        u.lang = '{lang_code}';
                        u.rate = 0.95;
                        u.pitch = 1.0;
                        u.volume = 1.0;

                        var voices = window.speechSynthesis.getVoices();
                        if (voices && voices.length) {{
                          for (var i=0;i<voices.length;i++) {{
                            if (voices[i].lang && voices[i].lang.toLowerCase().startsWith('{lang_code.split("-")[0].lower()}')) {{
                              u.voice = voices[i];
                              break;
                            }}
                          }}
                        }}
                        window.speechSynthesis.speak(u);
                      }}, 120);
                    }}
                  }} catch(e) {{}}
                }})();
              </script>
            </div>
            """,
            height=0,
        )
        st.session_state.voice_text = None
        st.session_state.voice_lang = None


def speak(text: str, lang=None):
    st.session_state.voice_text = text
    st.session_state.voice_lang = lang or st.session_state.get("lang", "fr")


def stop_speech():
    st.session_state.voice_text = None
    st.session_state.voice_lang = None
    st.components.v1.html("<script>try{window.speechSynthesis.cancel()}catch(e){}</script>", height=0)


# ============================================================
# CHATBOT KB (from parasites + extra topics) — no API
# ============================================================
CHAT_KB = {}

for pname, pdata in PARASITE_DB.items():
    if pname == "Negative":
        continue
    key = pname.lower().split("(")[0].strip().split(" ")[0].lower()
    CHAT_KB[key] = {
        "fr": f"**{pname}** ({pdata['sci']})\n\n**Morphologie:** {pdata['morph'].get('fr','')}\n\n**Description:** {pdata['desc'].get('fr','')}\n\n**Traitement:** {pdata['advice'].get('fr','')}\n\n**Examens:** {', '.join(pdata.get('tests',[]))}\n\n💡 {pdata['funny'].get('fr','')}",
        "ar": f"**{pname}** ({pdata['sci']})\n\n**المورفولوجيا:** {pdata['morph'].get('ar','')}\n\n**الوصف:** {pdata['desc'].get('ar','')}\n\n**العلاج:** {pdata['advice'].get('ar','')}\n\n**فحوصات:** {', '.join(pdata.get('tests',[]))}\n\n💡 {pdata['funny'].get('ar','')}",
        "en": f"**{pname}** ({pdata['sci']})\n\n**Morphology:** {pdata['morph'].get('en','')}\n\n**Description:** {pdata['desc'].get('en','')}\n\n**Treatment:** {pdata['advice'].get('en','')}\n\n**Tests:** {', '.join(pdata.get('tests',[]))}\n\n💡 {pdata['funny'].get('en','')}",
    }

CHAT_KB.update({
    "microscope": {
        "fr": "**Microscopie:**\n- x10: repérage\n- x40: œufs/kystes\n- x100: Plasmodium/Leishmania\n⚠️ Nettoyer l'objectif x100 après l'huile.",
        "ar": "**المجهر:**\n- x10 استطلاع\n- x40 أكياس/بيض\n- x100 بلازموديوم/ليشمانيا\n⚠️ نظف عدسة x100 بعد الزيت.",
        "en": "**Microscopy:**\n- x10 overview\n- x40 eggs/cysts\n- x100 Plasmodium/Leishmania\n⚠️ Clean x100 lens after oil.",
    },
    "coloration": {
        "fr": "**Colorations:**\n- Lugol: noyaux kystes\n- MGG/Giemsa: parasites sanguins\n- ZN modifié: coccidies",
        "ar": "**التلوين:**\n- لوغول: أنوية الأكياس\n- MGG/جيمزا: طفيليات الدم\n- ZN معدل: كوكسيديا",
        "en": "**Staining:**\n- Lugol: cyst nuclei\n- MGG/Giemsa: blood parasites\n- Modified ZN: coccidia",
    },
    "concentration": {
        "fr": "**Concentration:** Ritchie (formol-éther) معيار مهم لرفع الحساسية.",
        "ar": "**التركيز:** تقنية ريتشي (فورمول-إيثر) ترفع الحساسية.",
        "en": "**Concentration:** Ritchie (formalin-ether) increases sensitivity.",
    },
    "traitement": {
        "fr": "**Traitements (rappel):**\n- Métronidazole: amoeba/giardia\n- Praziquantel: schistosoma\n- ACT: paludisme حسب البروتوكول",
        "ar": "**العلاج (تذكير):**\n- ميترونيدازول: أميبا/جيارديا\n- برازيكوانتيل: بلهارسيا\n- ACT: ملاريا حسب البروتوكول",
        "en": "**Treatments (reminder):**\n- Metronidazole: amoeba/giardia\n- Praziquantel: schistosoma\n- ACT: malaria per protocol",
    },
    "aide": {
        "fr": "**DM Bot:** Essayez un mot-clé: amoeba, giardia, plasmodium, microscope, coloration, concentration, traitement.",
        "ar": "**المساعد:** جرّب كلمة: amoeba, giardia, plasmodium, microscope, coloration, concentration, traitement.",
        "en": "**DM Bot:** Try: amoeba, giardia, plasmodium, microscope, coloration, concentration, treatment.",
    },
    "help": {
        "fr": "**DM Bot:** Tapez 'aide' أو parasite name.",
        "ar": "**المساعد:** اكتب 'aide' أو اسم طفيلي.",
        "en": "**DM Bot:** Type 'help' or a parasite name.",
    },
})


def chatbot_reply(message: str) -> str:
    lang = st.session_state.get("lang", "fr")
    msg = (message or "").strip().lower()
    if not msg:
        return t("chat_not_found")

    # direct keys
    for k, v in CHAT_KB.items():
        if k in msg:
            return v.get(lang, v.get("fr", "")) if isinstance(v, dict) else str(v)

    # fuzzy on keys
    keys = list(CHAT_KB.keys())
    close = difflib.get_close_matches(msg.split()[0], keys, n=1, cutoff=0.78)
    if close:
        v = CHAT_KB[close[0]]
        return v.get(lang, v.get("fr", "")) if isinstance(v, dict) else str(v)

    # fuzzy on parasite names + scientific names
    for pname, pdata in PARASITE_DB.items():
        if pname == "Negative":
            continue
        hay = (pname + " " + pdata.get("sci", "")).lower()
        # any long token match
        for token in re.findall(r"[a-zA-ZÀ-ÿ]+", hay):
            if len(token) >= 4 and token in msg:
                key = pname.lower().split("(")[0].strip().split(" ")[0].lower()
                if key in CHAT_KB:
                    v = CHAT_KB[key]
                    return v.get(lang, v.get("fr", ""))

    return t("chat_not_found")


# ============================================================
# DAILY TIPS (3 languages)
# ============================================================
TIPS = {
    "fr": [
        "🔬 Examiner les selles dans les 30 min pour voir les trophozoïtes mobiles.",
        "💧 Lugol met en évidence les noyaux des kystes (préparation fraîche).",
        "🔍 Goutte épaisse = plus sensible pour paludisme.",
        "🔁 Répéter EPS x3 améliore la sensibilité.",
        "🕐 Urines de midi pour S. haematobium.",
    ],
    "ar": [
        "🔬 افحص البراز خلال 30 دقيقة لرؤية الأطوار المتحركة.",
        "💧 اللوغول يوضح أنوية الأكياس (تحضير طازج).",
        "🔍 القطرة السميكة أكثر حساسية للملاريا.",
        "🔁 تكرار الفحص 3 مرات يرفع الحساسية.",
        "🕐 بول الظهيرة لـ S. haematobium.",
    ],
    "en": [
        "🔬 Examine stool within 30 min to see motile trophozoites.",
        "💧 Lugol highlights cyst nuclei (fresh prep).",
        "🔍 Thick drop is more sensitive for malaria.",
        "🔁 Repeat stool exam x3 to improve sensitivity.",
        "🕐 Midday urine for S. haematobium.",
    ],
}


# Render voice player once per run (safe)
render_voice_player()


# ============================================================
# Quick helper card (for KPIs)
# ============================================================
def metric_card(icon: str, value: str, label: str, color="#22d3ee"):
    st.markdown(
        f"""
        <div class="dm-card" style="padding:14px;">
          <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">
            <div style="font-size:1.8rem;">{icon}</div>
            <div style="text-align:right;">
              <div style="font-weight:900;font-size:1.35rem;color:{color};line-height:1;">{value}</div>
              <div class="dm-muted" style="font-size:0.85rem;margin-top:4px;">{label}</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
# ============================================================
# DATABASE OPERATIONS — PRO
# ============================================================

def _j(obj) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"


def db_save_analysis(user_id: int, data: dict):
    """
    data keys expected (safe if missing):
    patient_name, patient_firstname, patient_age, patient_sex, patient_weight,
    sample_type, microscope_type, magnification, preparation_type,
    technician1, technician2, notes,
    parasite_detected, confidence, risk_level, is_reliable, demo,
    all_predictions, image_hash, model_name, processing_time
    """
    with db() as c:
        c.execute(
            """
            INSERT INTO analyses(
              user_id, analysis_date,
              patient_name, patient_firstname, patient_age, patient_sex, patient_weight,
              sample_type, microscope_type, magnification, preparation_type,
              technician1, technician2, notes,
              parasite_detected, confidence, risk_level, is_reliable, demo,
              all_predictions, image_hash, model_name, processing_time
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                int(user_id),
                now_iso(),
                str(data.get("patient_name", "")).strip(),
                str(data.get("patient_firstname", "")).strip(),
                int(data.get("patient_age", 0) or 0),
                str(data.get("patient_sex", "")).strip(),
                float(data.get("patient_weight", 0) or 0),
                str(data.get("sample_type", "")).strip(),
                str(data.get("microscope_type", "")).strip(),
                str(data.get("magnification", "")).strip(),
                str(data.get("preparation_type", "")).strip(),
                str(data.get("technician1", "")).strip(),
                str(data.get("technician2", "")).strip(),
                str(data.get("notes", "")).strip(),
                str(data.get("parasite_detected", "Negative")).strip(),
                float(data.get("confidence", 0) or 0),
                str(data.get("risk_level", "none")).strip(),
                1 if bool(data.get("is_reliable")) else 0,
                1 if bool(data.get("demo")) else 0,
                _j(data.get("all_predictions", {})),
                str(data.get("image_hash", "")).strip(),
                str(data.get("model_name", "")).strip(),
                float(data.get("processing_time", 0) or 0),
            ),
        )
        rid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        return int(rid)


def db_analyses(user_id=None, limit=500, filters=None):
    """
    filters:
      parasite: str
      validated: 0/1/None
      date_from: 'YYYY-MM-DD' or iso
      date_to: 'YYYY-MM-DD' or iso
    """
    filters = filters or {}
    params = []
    where = []

    base = """
      SELECT a.*, u.full_name as analyst, u.username as analyst_username
      FROM analyses a
      JOIN users u ON a.user_id = u.id
    """

    if user_id:
        where.append("a.user_id=?")
        params.append(int(user_id))

    if filters.get("parasite"):
        where.append("a.parasite_detected=?")
        params.append(str(filters["parasite"]))

    if filters.get("validated") in (0, 1):
        where.append("a.validated=?")
        params.append(int(filters["validated"]))

    if filters.get("date_from"):
        where.append("a.analysis_date>=?")
        params.append(str(filters["date_from"]))

    if filters.get("date_to"):
        where.append("a.analysis_date<=?")
        params.append(str(filters["date_to"]))

    q = base
    if where:
        q += " WHERE " + " AND ".join(where)
    q += " ORDER BY a.analysis_date DESC LIMIT ?"
    params.append(int(limit))

    with db() as c:
        rows = c.execute(q, tuple(params)).fetchall()
        return [dict(r) for r in rows]


def db_stats(user_id=None):
    with db() as c:
        params = []
        where = ""
        if user_id:
            where = "WHERE user_id=?"
            params = [int(user_id)]

        total = c.execute(f"SELECT COUNT(*) FROM analyses {where}", tuple(params)).fetchone()[0]

        reliable = c.execute(
            f"SELECT COUNT(*) FROM analyses {where + (' AND ' if where else 'WHERE ') if total or where else 'WHERE '}"
            f"{'user_id=? AND ' if user_id else ''}is_reliable=1",
            tuple(params),
        ).fetchone()[0] if (user_id or total >= 0) else 0

        validated = c.execute(
            f"SELECT COUNT(*) FROM analyses {where + (' AND ' if where else 'WHERE ') if total or where else 'WHERE '}"
            f"{'user_id=? AND ' if user_id else ''}validated=1",
            tuple(params),
        ).fetchone()[0] if (user_id or total >= 0) else 0

        avg_conf = c.execute(f"SELECT AVG(confidence) FROM analyses {where}", tuple(params)).fetchone()[0]
        avg_conf = float(avg_conf or 0.0)

        avg_time = c.execute(f"SELECT AVG(processing_time) FROM analyses {where}", tuple(params)).fetchone()[0]
        avg_time = float(avg_time or 0.0)

        parasites = c.execute(
            f"""
            SELECT parasite_detected, COUNT(*) as count
            FROM analyses {where}
            GROUP BY parasite_detected
            ORDER BY count DESC
            """,
            tuple(params),
        ).fetchall()

        top = parasites[0]["parasite_detected"] if parasites else "N/A"

        # monthly trend (last 12)
        monthly = c.execute(
            f"""
            SELECT strftime('%Y-%m', analysis_date) as month,
                   COUNT(*) as count,
                   AVG(confidence) as avg_conf
            FROM analyses {where}
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
            """,
            tuple(params),
        ).fetchall()

        return {
            "total": int(total),
            "reliable": int(reliable),
            "validated": int(validated),
            "to_verify": int(total - reliable),
            "avg_confidence": round(avg_conf, 1),
            "avg_time": round(avg_time, 2),
            "top": top,
            "parasites": [dict(p) for p in parasites],
            "monthly": [dict(m) for m in monthly],
        }


def db_validate_analysis(analysis_id: int, validator_name: str):
    with db() as c:
        c.execute(
            """
            UPDATE analyses
            SET validated=1, validated_by=?, validation_date=?
            WHERE id=?
            """,
            (str(validator_name), now_iso(), int(analysis_id)),
        )


def db_trends(days=30):
    # note: analysis_date is ISO; sqlite can parse many ISO formats
    with db() as c:
        rows = c.execute(
            """
            SELECT DATE(analysis_date) as day,
                   parasite_detected,
                   COUNT(*) as count,
                   AVG(confidence) as avg_conf,
                   SUM(CASE WHEN is_reliable=1 THEN 1 ELSE 0 END) as reliable_count
            FROM analyses
            WHERE analysis_date >= datetime('now', ?)
            GROUP BY day, parasite_detected
            ORDER BY day DESC
            """,
            (f"-{int(days)} days",),
        ).fetchall()
        return [dict(r) for r in rows]


# -------------------------
# Quiz
# -------------------------
def db_quiz_save(user_id, username, score, total, percentage, category="general", difficulty="medium", time_taken=0):
    with db() as c:
        c.execute(
            """
            INSERT INTO quiz_scores(user_id, username, timestamp, score, total_questions, percentage, category, difficulty, time_taken)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (
                int(user_id) if user_id else None,
                str(username or ""),
                now_iso(),
                int(score),
                int(total),
                float(percentage),
                str(category or "general"),
                str(difficulty or "medium"),
                int(time_taken or 0),
            ),
        )


def db_leaderboard(limit=20, category=None, difficulty=None):
    params = []
    where = []
    q = """
      SELECT username, score, total_questions, percentage, category, difficulty, timestamp
      FROM quiz_scores
    """
    if category:
        where.append("category=?")
        params.append(str(category))
    if difficulty:
        where.append("difficulty=?")
        params.append(str(difficulty))
    if where:
        q += " WHERE " + " AND ".join(where)

    q += " ORDER BY percentage DESC, timestamp ASC LIMIT ?"
    params.append(int(limit))

    with db() as c:
        rows = c.execute(q, tuple(params)).fetchall()
        return [dict(r) for r in rows]


# -------------------------
# Chat
# -------------------------
def db_save_chat(user_id, message, response):
    with db() as c:
        c.execute(
            "INSERT INTO chat_history(user_id, message, response, timestamp) VALUES(?,?,?,?)",
            (int(user_id) if user_id else None, str(message), str(response), now_iso()),
        )


def db_get_chat_history(user_id, limit=50):
    with db() as c:
        rows = c.execute(
            """
            SELECT message, response, timestamp
            FROM chat_history
            WHERE user_id=?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (int(user_id), int(limit)),
        ).fetchall()
        return [dict(r) for r in rows]


# -------------------------
# Users (Admin)
# -------------------------
def db_users():
    with db() as c:
        rows = c.execute(
            """
            SELECT id, username, full_name, role, speciality, email, is_active,
                   last_login, login_count, total_points, created_at
            FROM users
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [dict(r) for r in rows]


def db_toggle_user(uid: int, active: bool):
    with db() as c:
        c.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, int(uid)))


def db_change_password(uid: int, new_password: str):
    with db() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (_hp(new_password), int(uid)))


def db_create_user(username, password, full_name, role="viewer", speciality="", email=""):
    username = (username or "").strip()
    full_name = (full_name or "").strip()
    role = role if role in ROLES else "viewer"
    if not username or not password or not full_name:
        return False

    with db() as c:
        if c.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            return False
        c.execute(
            """INSERT INTO users(username,password_hash,full_name,role,speciality,email,created_at)
               VALUES(?,?,?,?,?,?,?)""",
            (username, _hp(password), full_name, role, speciality, email, now_iso()),
        )
        return True


# -------------------------
# Logs
# -------------------------
def db_logs(limit=300, user_id=None):
    q = "SELECT * FROM activity_log"
    params = []
    if user_id:
        q += " WHERE user_id=?"
        params.append(int(user_id))
    q += " ORDER BY timestamp DESC LIMIT ?"
    params.append(int(limit))

    with db() as c:
        rows = c.execute(q, tuple(params)).fetchall()
        return [dict(r) for r in rows]
# ============================================================
# PAGES — HOME / SCAN / ENCYCLOPEDIA (PRO)
# ============================================================

def _make_conf_chart(preds: dict):
    """Return a chart (plotly if available else vega-lite)"""
    if not preds:
        st.info(t("no_data"))
        return

    sorted_items = sorted(preds.items(), key=lambda x: x[1], reverse=True)
    labels = [k for k, _ in sorted_items]
    values = [float(v) for _, v in sorted_items]

    if HAS_PLOTLY:
        fig = px.bar(
            x=values,
            y=labels,
            orientation="h",
            color=values,
            color_continuous_scale="RdYlGn_r",
            labels={"x": "Confidence (%)", "y": "Class"},
        )
        fig.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False,
            xaxis_title="Confidence (%)",
            yaxis_title="",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        data = [{"label": l, "value": v} for l, v in zip(labels, values)]
        spec = {
            "mark": {"type": "bar", "cornerRadiusEnd": 6},
            "encoding": {
                "y": {"field": "label", "type": "nominal", "sort": "-x"},
                "x": {"field": "value", "type": "quantitative"},
                "color": {
                    "field": "value",
                    "type": "quantitative",
                    "scale": {"scheme": "redyellowgreen"},
                },
                "tooltip": [{"field": "label"}, {"field": "value"}],
            },
            "height": min(380, 28 * len(data) + 40),
        }
        st.vega_lite_chart(data, spec, use_container_width=True)


def _sanitize_pdf_text(txt: str) -> str:
    """Basic sanitizer for PDF fonts (keeps app stable)"""
    if txt is None:
        return ""
    txt = str(txt)
    # Replace common unicode to ascii-ish
    rep = {
        "→": "->", "×": "x", "µ": "u", "°": "o", "–": "-", "—": "-",
        "é": "e", "è": "e", "ê": "e", "ë": "e",
        "à": "a", "â": "a", "ä": "a",
        "ù": "u", "û": "u", "ü": "u",
        "ô": "o", "ö": "o",
        "î": "i", "ï": "i",
        "ç": "c",
        "É": "E", "È": "E", "Ê": "E", "Ë": "E",
        "À": "A", "Â": "A", "Ä": "A",
        "Ù": "U", "Û": "U", "Ü": "U",
        "Ô": "O", "Ö": "O",
        "Î": "I", "Ï": "I",
        "Ç": "C",
    }
    out = []
    for ch in txt:
        if ord(ch) < 128:
            out.append(ch)
        else:
            out.append(rep.get(ch, "?"))
    return "".join(out)


def generate_pdf_basic(patient: dict, lab: dict, prediction: dict, label: str, model_name: str = "") -> bytes:
    """Simple classic PDF (works if FPDF available)."""
    if not HAS_FPDF:
        raise RuntimeError("FPDF not available")

    class PDF(FPDF):
        def header(self):
            self.set_fill_color(30, 64, 175)
            self.rect(0, 0, 210, 8, "F")
            self.ln(12)
            self.set_font("Arial", "B", 14)
            self.set_text_color(30, 64, 175)
            self.cell(0, 8, _sanitize_pdf_text(f"DM SMART LAB AI — {APP_VERSION}"), 0, 1, "C")
            self.set_font("Arial", "", 10)
            self.set_text_color(80, 80, 80)
            self.cell(0, 5, _sanitize_pdf_text("Rapport d'analyse (IA)"), 0, 1, "C")
            self.set_text_color(0, 0, 0)
            self.ln(3)

        def footer(self):
            self.set_y(-18)
            self.set_font("Arial", "I", 7)
            self.set_text_color(120, 120, 120)
            self.cell(0, 5, _sanitize_pdf_text("Avertissement: validation médicale requise."), 0, 1, "C")
            self.cell(0, 5, _sanitize_pdf_text(f"Page {self.page_no()}"), 0, 0, "C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(True, 20)

    ref = hashlib.md5((patient.get("Nom", "") + now_iso()).encode("utf-8")).hexdigest()[:10].upper()
    conf = int(prediction.get("conf", 0) or 0)
    risk = prediction.get("risk", "none")

    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 6, _sanitize_pdf_text(f"Référence: DM-{ref}"), 0, 1, "R")
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, _sanitize_pdf_text(f"Date: {fmt_dt(now_iso())} | Model: {model_name or 'N/A'}"), 0, 1, "R")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    def section(title):
        pdf.set_fill_color(30, 64, 175)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(0, 7, _sanitize_pdf_text("  " + title), 0, 1, "L", True)
        pdf.ln(2)
        pdf.set_text_color(0, 0, 0)

    def field(k, v):
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(55, 6, _sanitize_pdf_text(str(k) + ":"), 0, 0)
        pdf.set_font("Arial", "", 9)
        pdf.set_text_color(0, 0, 0)
        pdf.multi_cell(0, 6, _sanitize_pdf_text(str(v)))

    section("INFORMATIONS PATIENT")
    for k, v in patient.items():
        if v:
            field(k, v)

    pdf.ln(2)
    section("INFORMATIONS LABORATOIRE")
    for k, v in lab.items():
        if v:
            field(k, v)

    pdf.ln(2)
    section("RESULTAT IA")
    # result box
    if label == "Negative" or risk == "none":
        pdf.set_fill_color(220, 255, 220)
        pdf.set_text_color(0, 120, 0)
    else:
        pdf.set_fill_color(255, 220, 220)
        pdf.set_text_color(160, 0, 0)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, _sanitize_pdf_text(f"{label} — Confiance: {conf}%"), 1, 1, "C", True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    info = PARASITE_DB.get(label, PARASITE_DB["Negative"])
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, _sanitize_pdf_text("Nom scientifique: " + info.get("sci", "N/A")), 0, 1)

    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, _sanitize_pdf_text("Morphologie:"), 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, _sanitize_pdf_text(info["morph"].get("fr", "")))

    pdf.ln(1)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 6, _sanitize_pdf_text("Conseil:"), 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, _sanitize_pdf_text(info["advice"].get("fr", "")))

    # Optional QR
    if HAS_QRCODE:
        try:
            qr = qrcode.QRCode(box_size=2, border=1)
            qr.add_data(f"DM|{ref}|{label}|{conf}|{now_iso()}")
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            # fpdf needs a path, so write temp file
            tmp = f"_qr_{ref}.png"
            with open(tmp, "wb") as f:
                f.write(buf.read())
            y = pdf.get_y()
            pdf.image(tmp, x=170, y=y, w=25)
            try:
                os.remove(tmp)
            except Exception:
                pass
        except Exception:
            pass

    return bytes(pdf.output(dest="S").encode("latin-1", errors="ignore"))


def make_html_report(patient: dict, lab: dict, pred: dict, label: str, model_name: str = "") -> bytes:
    info = PARASITE_DB.get(label, PARASITE_DB["Negative"])
    risk = pred.get("risk", "none")
    conf = int(pred.get("conf", 0) or 0)
    color = risk_color(risk)

    html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>DM Smart Lab AI Report</title>
<style>
body{{font-family:Arial,Helvetica,sans-serif;margin:30px;color:#0f172a;}}
h1{{margin:0;color:#1e40af}}
.badge{{display:inline-block;padding:6px 10px;border-radius:999px;background:{color}22;border:1px solid {color}55;color:{color};font-weight:700}}
.card{{border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin:14px 0}}
small{{color:#64748b}}
</style>
</head>
<body>
<h1>DM SMART LAB AI</h1>
<small>Version {APP_VERSION} — {fmt_dt(now_iso())} — Model: {model_name or 'N/A'}</small>

<div class="card">
  <h2 style="margin:0;color:{color}">{label} — {conf}%</h2>
  <div class="badge">{risk.upper()}</div>
  <p><b>Scientific:</b> {info.get('sci','N/A')}</p>
</div>

<div class="card">
  <h3>Patient</h3>
  <pre>{json.dumps(patient, ensure_ascii=False, indent=2)}</pre>
</div>

<div class="card">
  <h3>Lab</h3>
  <pre>{json.dumps(lab, ensure_ascii=False, indent=2)}</pre>
</div>

<div class="card">
  <h3>Morphology</h3>
  <p>{tl(info.get('morph',{}))}</p>
  <h3>Advice</h3>
  <p>{tl(info.get('advice',{}))}</p>
  <h3>Extra tests</h3>
  <ul>
    {''.join([f'<li>{x}</li>' for x in info.get('tests',[])])}
  </ul>
</div>

<div class="card">
  <h3>All probabilities</h3>
  <pre>{json.dumps(pred.get('preds',{}), ensure_ascii=False, indent=2)}</pre>
</div>

<hr>
<small><b>Disclaimer:</b> AI-generated result. Medical validation required.</small>
</body></html>
"""
    return html.encode("utf-8")


# ============================================================
# HOME
# ============================================================
if selected_page == "home":
    st.markdown(f"<h1 class='dm-title'>🧬 {t('home')}</h1>", unsafe_allow_html=True)

    # Daily tip
    tips = TIPS.get(st.session_state.lang, TIPS["fr"])
    tip = tips[datetime.now().timetuple().tm_yday % len(tips)]
    st.info(f"**{t('daily_tip')}** — {tip}")

    stats = db_stats(st.session_state.user_id)

    st.markdown("### " + t("quick_stats"))
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("🔬 " + t("total_analyses"), stats["total"])
    with c2:
        st.metric("✅ " + t("reliable"), stats["reliable"])
    with c3:
        st.metric("⚠️ " + t("to_verify"), stats["to_verify"])
    with c4:
        st.metric("🦠 " + t("most_frequent"), stats["top"])
    with c5:
        st.metric("📈 " + t("avg_confidence"), f"{stats['avg_confidence']}%")

    st.markdown("---")
    st.markdown("### " + t("recent_activity"))
    recent = db_analyses(st.session_state.user_id, limit=6)
    if not recent:
        st.info(t("no_recent"))
    else:
        for a in recent:
            risk = a.get("risk_level", "none")
            clr = risk_color(risk)
            title = f"#{a['id']} — {a['parasite_detected']} — {int(a['confidence'])}% — {fmt_dt(a['analysis_date'])}"
            with st.expander(title):
                cc1, cc2, cc3 = st.columns([1.2, 1, 1])
                with cc1:
                    st.markdown(f"**Patient:** {a.get('patient_name','')}")
                    st.markdown(f"**Sample:** {a.get('sample_type','')}")
                    st.markdown(f"**Analyst:** {a.get('analyst','')}")
                with cc2:
                    st.markdown(f"**Risk:** <span style='color:{clr};font-weight:800'>{risk_label(risk)}</span>", unsafe_allow_html=True)
                    st.progress(risk_percentage(risk) / 100.0)
                with cc3:
                    st.markdown(f"**Reliable:** {'✅' if a.get('is_reliable') else '⚠️'}")
                    st.markdown(f"**Validated:** {'✅' if a.get('validated') else '⏳'}")

    st.markdown("---")
    st.markdown("### " + t("quick_actions"))
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("🔬 " + t("scan"), use_container_width=True, type="primary"):
            st.session_state.current_page = "scan"
            st.rerun()
    with qa2:
        if st.button("📊 " + t("dashboard"), use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    with qa3:
        if st.button("🧠 " + t("quiz"), use_container_width=True):
            st.session_state.current_page = "quiz"
            st.rerun()
    with qa4:
        if st.button("💬 " + t("chatbot"), use_container_width=True):
            st.session_state.current_page = "chatbot"
            st.rerun()


# ============================================================
# SCAN & ANALYZE
# ============================================================
elif selected_page == "scan":
    st.markdown(f"<h1 class='dm-title'>🔬 {t('scan')}</h1>", unsafe_allow_html=True)

    # Load AI model once (cached)
    model, model_name, model_type = load_model()

    # show model status in a nice card
    if model_name:
        st.success(f"🧠 Model loaded: **{model_name}** ({model_type})")
    else:
        st.info("🧠 " + t("demo_mode"))
        if not HAS_TF:
            st.warning("TensorFlow not available (requirements not installed).")

    st.markdown("### 1) " + t("patient_info"))
    with st.expander("👤 " + t("patient_info"), expanded=True):
        p1, p2 = st.columns(2)
        with p1:
            patient_name = st.text_input(t("patient_name"), key="p_name")
            patient_firstname = st.text_input(t("patient_firstname"), key="p_firstname")
            patient_age = st.number_input(t("age"), min_value=0, max_value=120, value=30, key="p_age")
        with p2:
            patient_sex = st.selectbox(t("sex"), [t("male"), t("female")], key="p_sex")
            patient_weight = st.number_input(t("weight"), min_value=0.0, max_value=300.0, value=70.0, step=0.5, key="p_weight")
            sample_type = st.selectbox(t("sample_type"), SAMPLES.get(st.session_state.lang, SAMPLES["fr"]), key="p_sample")

    st.markdown("### 2) " + t("lab_info"))
    with st.expander("🔬 " + t("lab_info"), expanded=True):
        l1, l2, l3 = st.columns(3)
        with l1:
            tech1 = st.text_input(f"{t('technician')} 1", value=st.session_state.user_full_name, key="tech1")
            microscope_type = st.selectbox(t("microscope"), MICROSCOPE_TYPES, key="microscope_type")
        with l2:
            tech2 = st.text_input(f"{t('technician')} 2", key="tech2")
            magnification = st.selectbox(t("magnification"), MAGNIFICATIONS, index=3, key="magnification")
        with l3:
            preparation_type = st.selectbox(t("preparation"), PREPARATION_TYPES, key="preparation")
        notes = st.text_area(t("notes"), height=80, key="notes")

    st.markdown("### 3) " + t("image_capture"))
    st.caption(t("upload_hint"))

    source = st.radio("Source", [t("upload_file"), t("take_photo")], horizontal=True, label_visibility="collapsed")
    img = None
    img_hash = None

    if source == t("take_photo"):
        st.info(t("camera_hint"))
        cam = st.camera_input("Camera", key="camera")
        if cam:
            img = Image.open(cam).convert("RGB")
            img_hash = hashlib.md5(cam.getvalue()).hexdigest()
    else:
        up = st.file_uploader(t("upload_file"), type=["jpg", "jpeg", "png", "bmp", "tiff"], key="upload")
        if up:
            img = Image.open(up).convert("RGB")
            img_hash = hashlib.md5(up.getvalue()).hexdigest()

    if img is None:
        st.stop()

    # patient name required
    if not str(patient_name or "").strip():
        st.error("⚠️ " + t("name_required"))
        st.stop()

    # stable seeds for same image
    if st.session_state.get("_scan_hash") != img_hash:
        st.session_state["_scan_hash"] = img_hash
        st.session_state["_demo_seed"] = random.randint(0, 999999)
        st.session_state["_heat_seed"] = random.randint(0, 999999)

    # Layout: Image left, result right
    col_img, col_res = st.columns([1.1, 1.0], vertical_alignment="top")

    with col_img:
        with st.expander("🎛️ Adjustments", expanded=False):
            zoom = st.slider("Zoom", 1.0, 5.0, 1.0, 0.25)
            brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.05)
            contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.05)
            saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.05)

        adj = adjust_image(img, brightness, contrast, saturation)
        if zoom > 1:
            adj = zoom_image(adj, zoom)

        tabs = st.tabs(["📷 Original", "🔥 Thermal", "📐 Edges", "✨ Enhanced", "🔄 Negative", "🏔️ Emboss", "🎯 Heatmap"])
        with tabs[0]:
            st.image(adj, use_container_width=True)
        with tabs[1]:
            st.image(thermal_view(adj), use_container_width=True)
        with tabs[2]:
            st.image(edges_filter(adj), use_container_width=True)
        with tabs[3]:
            st.image(enhanced_filter(adj), use_container_width=True)
        with tabs[4]:
            st.image(negative_filter(adj), use_container_width=True)
        with tabs[5]:
            st.image(emboss_filter(adj), use_container_width=True)
        with tabs[6]:
            st.image(generate_heatmap(img, st.session_state["_heat_seed"]), use_container_width=True)

    with col_res:
        st.markdown("### 🧠 " + t("result"))

        # progress + prediction
        with st.spinner(t("analyzing")):
            p = st.progress(0)
            for i in range(40):
                time.sleep(0.01)
                p.progress((i + 1) / 40)

            start = time.time()
            pred = predict_image(model, model_type, img, seed=st.session_state["_demo_seed"])
            elapsed = time.time() - start

        label = pred["label"]
        conf = int(pred["conf"] or 0)
        risk = pred.get("risk", "none")
        info = PARASITE_DB.get(label, PARASITE_DB["Negative"])
        clr = risk_color(risk)

        # Reliability warning
        if not pred.get("rel"):
            st.warning("⚠️ " + t("low_conf_warn"))
        if pred.get("demo"):
            st.info("ℹ️ " + t("demo_mode"))

        # KPIs (st.metric requirement)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("🧬 Label", label)
        with m2:
            st.metric("📈 " + t("confidence"), f"{conf}%")
        with m3:
            st.metric("⚠️ " + t("risk"), risk_label(risk))

        # Result Card
        st.markdown(
            f"""
            <div class="dm-card" style="border-left: 6px solid {clr};">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;">
                <div>
                  <div style="font-size:1.35rem;font-weight:900;color:{clr};">{label}</div>
                  <div class="dm-muted" style="margin-top:2px;"><i>{info.get('sci','')}</i></div>
                </div>
                <div style="text-align:center;">
                  <div style="font-size:2.2rem;font-weight:900;color:{clr};line-height:1;">{conf}%</div>
                  <div class="dm-muted" style="font-size:0.85rem;">{t('confidence')}</div>
                </div>
              </div>
              <hr style="opacity:0.15;margin:14px 0;">
              <div><b>🔬 {t('morphology')}:</b><br>{tl(info.get('morph',{}))}</div>
              <div style="margin-top:10px;"><b>⚠️ {t('risk')}:</b>
                <span style="color:{clr};font-weight:900;"> {tl(info.get('risk_d',{}))}</span>
              </div>
              <div style="margin-top:12px;padding:12px;border-radius:12px;background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.20);">
                <b>💡 {t('advice')}:</b><br>{tl(info.get('advice',{}))}
              </div>
              <div style="margin-top:12px;padding:12px;border-radius:12px;background:rgba(59,130,246,0.10);border:1px solid rgba(59,130,246,0.18);">
                🤖 {tl(info.get('funny',{}))}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Risk progress
        st.progress(risk_percentage(risk) / 100.0)

        # Voice buttons (3 langs)
        v1, v2 = st.columns(2)
        with v1:
            if st.button("🔊 " + t("listen"), use_container_width=True):
                speak(f"{label}. {tl(info.get('funny',{}))}")
                st.rerun()
        with v2:
            if st.button("🔇 " + t("stop_voice"), use_container_width=True):
                stop_speech()

        # Extra sections
        with st.expander("🩺 " + t("extra_tests"), expanded=False):
            for x in info.get("tests", []):
                st.markdown(f"- {x}")

        keys_txt = tl(info.get("keys", {}))
        if keys_txt and keys_txt not in ("N/A", "غير متوفر"):
            with st.expander("🔑 " + t("diagnostic_keys"), expanded=False):
                st.code(keys_txt)

        cyc_txt = tl(info.get("cycle", {}))
        if cyc_txt and cyc_txt not in ("N/A", "غير متوفر"):
            with st.expander("🔄 " + t("lifecycle"), expanded=False):
                st.write(cyc_txt)

        # Confidence chart
        with st.expander("📊 " + t("all_probabilities"), expanded=False):
            _make_conf_chart(pred.get("preds", {}))

        # Compare with previous results (last 10 for user)
        with st.expander("📊 مقارنة مع نتائج سابقة / Previous results", expanded=False):
            prev = db_analyses(st.session_state.user_id, limit=10)
            if not prev:
                st.info(t("no_data"))
            else:
                dfp = pd.DataFrame(prev)[["id", "analysis_date", "patient_name", "parasite_detected", "confidence", "risk_level", "validated"]]
                dfp["analysis_date"] = dfp["analysis_date"].apply(fmt_dt)
                dfp["validated"] = dfp["validated"].apply(lambda x: "✅" if x else "⏳")
                st.dataframe(dfp, use_container_width=True, height=260)

    st.markdown("---")
    a1, a2, a3, a4 = st.columns(4)

    # Build patient/lab dicts
    patient_dict = {
        "Nom": patient_name,
        "Prenom": patient_firstname,
        "Age": str(patient_age),
        "Sexe": patient_sex,
        "Poids": f"{patient_weight} kg",
        "Echantillon": sample_type,
    }
    lab_dict = {
        "Microscope": microscope_type,
        "Grossissement": magnification,
        "Preparation": preparation_type,
        "Technicien 1": tech1,
        "Technicien 2": tech2,
        "Notes": notes,
    }

    # Always provide HTML report
    with a1:
        html_bytes = make_html_report(patient_dict, lab_dict, pred, label, model_name=model_name or "")
        st.download_button(
            "📄 " + t("download_report"),
            data=html_bytes,
            file_name=f"Report_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True,
        )

    # PDF if available
    with a2:
        if HAS_FPDF:
            try:
                pdf_bytes = generate_pdf_basic(patient_dict, lab_dict, pred, label, model_name=model_name or "")
                st.download_button(
                    "📥 " + t("download_pdf"),
                    data=pdf_bytes,
                    file_name=f"Rapport_{patient_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF error: {e}")
        else:
            st.info("PDF disabled (fpdf missing).")

    # Save to DB (technician+)
    with a3:
        if has_role(2):
            if st.button("💾 " + t("save_db"), use_container_width=True, type="primary"):
                payload = {
                    "patient_name": patient_name,
                    "patient_firstname": patient_firstname,
                    "patient_age": patient_age,
                    "patient_sex": patient_sex,
                    "patient_weight": patient_weight,
                    "sample_type": sample_type,
                    "microscope_type": microscope_type,
                    "magnification": magnification,
                    "preparation_type": preparation_type,
                    "technician1": tech1,
                    "technician2": tech2,
                    "notes": notes,
                    "parasite_detected": label,
                    "confidence": conf,
                    "risk_level": risk,
                    "is_reliable": bool(pred.get("rel")),
                    "demo": bool(pred.get("demo")),
                    "all_predictions": pred.get("preds", {}),
                    "image_hash": img_hash,
                    "model_name": model_name or "",
                    "processing_time": float(elapsed),
                }
                aid = db_save_analysis(st.session_state.user_id, payload)
                db_log(st.session_state.user_id, st.session_state.user_name, "Analysis saved", f"ID:{aid} label={label} conf={conf}")
                st.success(f"✅ {t('saved_ok')} (ID: #{aid})")
        else:
            st.info("Save disabled (role).")

    # New analysis
    with a4:
        if st.button("🔄 " + t("new_analysis"), use_container_width=True):
            st.session_state["_scan_hash"] = None
            st.session_state["_demo_seed"] = None
            st.session_state["_heat_seed"] = None
            st.rerun()


# ============================================================
# ENCYCLOPEDIA
# ============================================================
elif selected_page == "encyclopedia":
    st.markdown(f"<h1 class='dm-title'>📘 {t('encyclopedia')}</h1>", unsafe_allow_html=True)

    q = st.text_input("🔍 " + t("search"), placeholder="Amoeba, Giardia, Plasmodium...")
    st.markdown("---")

    found = False
    for pname, pdata in PARASITE_DB.items():
        if pname == "Negative":
            continue

        if q and q.strip():
            hay = (pname + " " + pdata.get("sci", "")).lower()
            if q.strip().lower() not in hay:
                continue

        found = True
        risk = pdata.get("risk", "none")
        clr = risk_color(risk)

        title = f"{pdata.get('icon','🦠')}  {pname} — {pdata.get('sci','')} | {tl(pdata.get('risk_d',{}))}"
        with st.expander(title, expanded=(not q)):
            left, right = st.columns([2.4, 1], vertical_alignment="top")

            with left:
                st.markdown(
                    f"""
                    <div class="dm-card" style="border-left:6px solid {clr};">
                      <div style="font-weight:900;color:{clr};font-size:1.1rem;">{pdata.get('sci','')}</div>
                      <p><b>🔬 {t('morphology')}:</b><br>{tl(pdata.get('morph',{}))}</p>
                      <p><b>📖 {t('description')}:</b><br>{tl(pdata.get('desc',{}))}</p>
                      <p><b>⚠️ {t('risk')}:</b> <span style="color:{clr};font-weight:900;">{tl(pdata.get('risk_d',{}))}</span></p>
                      <div style="margin-top:10px;padding:12px;border-radius:12px;background:rgba(34,197,94,0.10);border:1px solid rgba(34,197,94,0.18);">
                        <b>💡 {t('advice')}:</b><br>{tl(pdata.get('advice',{}))}
                      </div>
                      <div style="margin-top:10px;padding:12px;border-radius:12px;background:rgba(59,130,246,0.10);border:1px solid rgba(59,130,246,0.18);">
                        🤖 {tl(pdata.get('funny',{}))}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                cyc = tl(pdata.get("cycle", {}))
                if cyc and cyc not in ("N/A", "غير متوفر"):
                    st.markdown(f"**🔄 {t('lifecycle')}:** {cyc}")

                keys_txt = tl(pdata.get("keys", {}))
                if keys_txt:
                    st.markdown(f"**🔑 {t('diagnostic_keys')}:**")
                    st.code(keys_txt)

                if pdata.get("tests"):
                    st.markdown(f"**🩺 {t('extra_tests')}:** " + ", ".join(pdata["tests"]))

            with right:
                st.markdown(f"<div class='dm-card' style='text-align:center;'>"
                            f"<div style='font-size:4.5rem;line-height:1.1'>{pdata.get('icon','🦠')}</div>"
                            f"<div class='dm-muted' style='margin-top:6px'>{risk_label(risk)}</div>"
                            f"</div>", unsafe_allow_html=True)
                st.progress(risk_percentage(risk) / 100.0)

                if st.button("🔊 " + t("listen"), key=f"listen_{pname}", use_container_width=True):
                    speak(f"{pname}. {tl(pdata.get('desc',{}))}")
                    st.rerun()

    if q and not found:
        st.warning(t("no_results"))
# ============================================================
# PAGES — DASHBOARD / QUIZ / CHATBOT / COMPARE (PRO)
# ============================================================

# ---- Patch: db_stats FIX (override previous to avoid SQL duplication bugs) ----
def db_stats(user_id=None):
    with db() as c:
        params = []
        where = []
        if user_id:
            where.append("user_id=?")
            params.append(int(user_id))

        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        total = c.execute(f"SELECT COUNT(*) FROM analyses {where_sql}", tuple(params)).fetchone()[0]

        where_rel = where[:] + ["is_reliable=1"]
        rel_sql = "WHERE " + " AND ".join(where_rel) if where_rel else "WHERE is_reliable=1"
        reliable = c.execute(f"SELECT COUNT(*) FROM analyses {rel_sql}", tuple(params)).fetchone()[0]

        where_val = where[:] + ["validated=1"]
        val_sql = "WHERE " + " AND ".join(where_val) if where_val else "WHERE validated=1"
        validated = c.execute(f"SELECT COUNT(*) FROM analyses {val_sql}", tuple(params)).fetchone()[0]

        avg_conf = c.execute(f"SELECT AVG(confidence) FROM analyses {where_sql}", tuple(params)).fetchone()[0]
        avg_conf = float(avg_conf or 0.0)

        avg_time = c.execute(f"SELECT AVG(processing_time) FROM analyses {where_sql}", tuple(params)).fetchone()[0]
        avg_time = float(avg_time or 0.0)

        parasites = c.execute(
            f"""
            SELECT parasite_detected, COUNT(*) as count
            FROM analyses {where_sql}
            GROUP BY parasite_detected
            ORDER BY count DESC
            """,
            tuple(params),
        ).fetchall()

        top = parasites[0]["parasite_detected"] if parasites else "N/A"

        monthly = c.execute(
            f"""
            SELECT strftime('%Y-%m', analysis_date) as month,
                   COUNT(*) as count,
                   AVG(confidence) as avg_conf
            FROM analyses {where_sql}
            GROUP BY month
            ORDER BY month DESC
            LIMIT 12
            """,
            tuple(params),
        ).fetchall()

        return {
            "total": int(total),
            "reliable": int(reliable),
            "validated": int(validated),
            "to_verify": int(total - reliable),
            "avg_confidence": round(avg_conf, 1),
            "avg_time": round(avg_time, 2),
            "top": top,
            "parasites": [dict(p) for p in parasites],
            "monthly": [dict(m) for m in monthly],
        }


# ---- Export helpers ----
def export_excel_bytes(df: pd.DataFrame) -> bytes:
    out = io.BytesIO()
    try:
        with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Analyses", index=False)
            wb = writer.book
            ws = writer.sheets["Analyses"]
            header_fmt = wb.add_format({"bold": True, "bg_color": "#1e40af", "font_color": "white"})
            for col, name in enumerate(df.columns):
                ws.write(0, col, name, header_fmt)
                ws.set_column(col, col, 18)
        return out.getvalue()
    except Exception:
        # fallback: csv bytes if excel fails
        return df.to_csv(index=False).encode("utf-8-sig")


def export_json_bytes(data) -> bytes:
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")


# ---- Session init for Quiz + Chat ----
if "quiz_state" not in st.session_state:
    st.session_state.quiz_state = {
        "active": False,
        "finished": False,
        "current": 0,
        "score": 0,
        "order": [],
        "wrong": [],
        "answered": [],
        "total_q": 0,
        "selected_answer": None,
        "show_result": False,
        "start_time": None,
        "difficulty": "Tous",
        "category": "All",
        "timed": False,
    }

if "chat_ui" not in st.session_state:
    st.session_state.chat_ui = {"history": []}


# ---- Quiz questions (fixed set; يمكنك تزيد لاحقاً بسهولة) ----
def mq(fr, ar, en):
    return {"fr": fr, "ar": ar, "en": en}


QUIZ_QUESTIONS = [
    {
        "q": mq("Quel parasite présente une bague à chaton dans les hématies?",
                "أي طفيلي يظهر شكل الخاتم في كريات الدم الحمراء؟",
                "Which parasite shows a signet ring in RBCs?"),
        "opts": ["Giardia", "Plasmodium", "Leishmania", "Amoeba"],
        "ans": 1,
        "cat": "Hématozoaires",
        "difficulty": "easy",
        "expl": mq("Plasmodium: bague à chaton au stade trophozoïte jeune.",
                   "البلازموديوم: شكل الخاتم في الطور النشط المبكر.",
                   "Plasmodium: signet ring at young trophozoite stage."),
    },
    {
        "q": mq("Le kyste mature de Giardia possède combien de noyaux?",
                "كم عدد أنوية كيس الجيارديا الناضج؟",
                "How many nuclei does a mature Giardia cyst have?"),
        "opts": ["2", "4", "6", "8"],
        "ans": 1,
        "cat": "Protozoaires",
        "difficulty": "easy",
        "expl": mq("4 noyaux. Le trophozoïte en a 2.", "4 أنوية. الطور النشط له نواتان.", "4 nuclei. Trophozoite has 2."),
    },
    {
        "q": mq("Quel parasite est transmis par le phlébotome?",
                "أي طفيلي ينتقل عبر ذبابة الرمل؟",
                "Which parasite is sandfly-transmitted?"),
        "opts": ["Plasmodium", "Trypanosoma", "Leishmania", "Schistosoma"],
        "ans": 2,
        "cat": "Vecteurs",
        "difficulty": "medium",
        "expl": mq("Leishmania = phlébotome.", "ليشمانيا = ذبابة الرمل.", "Leishmania = sandfly."),
    },
    {
        "q": mq("Examen urgent suspicion paludisme?",
                "الفحص الطارئ عند الاشتباه بالملاريا؟",
                "Urgent exam for malaria?"),
        "opts": ["Coproculture", "ECBU", "Goutte épaisse + Frottis", "Sérologie"],
        "ans": 2,
        "cat": "Diagnostic",
        "difficulty": "easy",
        "expl": mq("GE + frottis = référence urgente.", "قطرة سميكة + لطاخة = المرجع.", "Thick drop + smear = urgent reference."),
    },
    {
        "q": mq("E. histolytica se distingue par:",
                "يتميز E. histolytica بـ:",
                "E. histolytica is distinguished by:"),
        "opts": ["Flagelles", "Hématies phagocytées", "Membrane ondulante", "Kinétoplaste"],
        "ans": 1,
        "cat": "Morphologie",
        "difficulty": "medium",
        "expl": mq("Hématies phagocytées = pathogénicité.", "ابتلاع الكريات = معيار المرضية.", "Phagocytosed RBCs indicate pathogenicity."),
    },
    {
        "q": mq("Colorant pour amastigotes Leishmania?",
                "ملون أماستيغوت الليشمانيا؟",
                "Stain for Leishmania amastigotes?"),
        "opts": ["Ziehl-Neelsen", "Gram", "MGG/Giemsa", "Lugol"],
        "ans": 2,
        "cat": "Techniques",
        "difficulty": "medium",
        "expl": mq("MGG/Giemsa: noyau + kinétoplaste.", "MGG/جيمزا: نواة + كينيتوبلاست.", "MGG/Giemsa: nucleus + kinetoplast."),
    },
    {
        "q": mq("Traitement de référence bilharziose?",
                "العلاج المرجعي للبلهارسيا؟",
                "Reference treatment for schistosomiasis?"),
        "opts": ["Chloroquine", "Métronidazole", "Praziquantel", "Albendazole"],
        "ans": 2,
        "cat": "Thérapeutique",
        "difficulty": "easy",
        "expl": mq("Praziquantel = choix n°1.", "برازيكوانتيل = الخيار الأول.", "Praziquantel is first-line."),
    },
    {
        "q": mq("Face de hibou observée chez:",
                "وجه البومة عند:",
                "Owl-face appearance is seen in:"),
        "opts": ["Plasmodium", "Giardia", "Amoeba", "Trypanosoma"],
        "ans": 1,
        "cat": "Morphologie",
        "difficulty": "easy",
        "expl": mq("Giardia: 2 noyaux symétriques.", "الجيارديا: نواتان متناظرتان.", "Giardia: 2 symmetric nuclei."),
    },
]

# Duplicate questions to simulate a larger bank if you want (optional)
# This keeps app functional even if you later paste 60+ questions.
if len(QUIZ_QUESTIONS) < 30:
    base = QUIZ_QUESTIONS[:]
    while len(QUIZ_QUESTIONS) < 30:
        for q in base:
            if len(QUIZ_QUESTIONS) >= 30:
                break
            qq = dict(q)
            QUIZ_QUESTIONS.append(qq)


# ============================================================
# DASHBOARD
# ============================================================
elif selected_page == "dashboard":
    st.markdown(f"<h1 class='dm-title'>📊 {t('dashboard')}</h1>", unsafe_allow_html=True)

    is_admin = has_role(3)
    stats = db_stats(None if is_admin else st.session_state.user_id)
    analyses = db_analyses(None if is_admin else st.session_state.user_id, limit=1500)

    # KPIs
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("🔬 " + t("total_analyses"), stats["total"])
    with c2:
        st.metric("✅ " + t("reliable"), stats["reliable"])
    with c3:
        st.metric("⚠️ " + t("to_verify"), stats["to_verify"])
    with c4:
        st.metric("🦠 " + t("most_frequent"), stats["top"])
    with c5:
        st.metric("📈 " + t("avg_confidence"), f"{stats['avg_confidence']}%")

    st.markdown("---")
    if not analyses:
        st.info(t("no_data"))
        st.stop()

    df = pd.DataFrame(analyses)

    # Charts row
    left, right = st.columns(2, vertical_alignment="top")

    with left:
        st.markdown("#### 🥧 Parasite distribution")
        if HAS_PLOTLY:
            counts = df["parasite_detected"].value_counts()
            fig = px.pie(values=counts.values, names=counts.index, hole=0.55)
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            counts = df["parasite_detected"].value_counts().reset_index()
            counts.columns = ["parasite", "count"]
            st.vega_lite_chart(
                counts,
                {
                    "mark": {"type": "arc", "innerRadius": 70},
                    "encoding": {
                        "theta": {"field": "count", "type": "quantitative"},
                        "color": {"field": "parasite", "type": "nominal"},
                        "tooltip": [{"field": "parasite"}, {"field": "count"}],
                    },
                },
                use_container_width=True,
            )

    with right:
        st.markdown("#### 📊 Confidence levels")
        if HAS_PLOTLY:
            fig = px.histogram(df, x="confidence", nbins=20, color_discrete_sequence=["#22d3ee"])
            fig.add_vline(x=CONFIDENCE_THRESHOLD, line_dash="dash", line_color="#22c55e")
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            # vega histogram
            st.vega_lite_chart(
                df,
                {
                    "mark": "bar",
                    "encoding": {
                        "x": {"field": "confidence", "type": "quantitative", "bin": {"maxbins": 20}},
                        "y": {"aggregate": "count", "type": "quantitative"},
                        "tooltip": [{"aggregate": "count"}, {"field": "confidence", "bin": True}],
                    },
                    "height": 300,
                },
                use_container_width=True,
            )
            st.caption(f"Threshold: {CONFIDENCE_THRESHOLD}%")

    # Trends
    st.markdown("---")
    st.markdown("#### 📈 Trends (30 days)")
    tr = db_trends(30)
    if tr:
        dft = pd.DataFrame(tr)
        if HAS_PLOTLY:
            fig = px.line(dft, x="day", y="count", color="parasite_detected", markers=True)
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.vega_lite_chart(
                dft,
                {
                    "mark": {"type": "line", "point": True},
                    "encoding": {
                        "x": {"field": "day", "type": "temporal"},
                        "y": {"field": "count", "type": "quantitative"},
                        "color": {"field": "parasite_detected", "type": "nominal"},
                        "tooltip": [{"field": "day"}, {"field": "parasite_detected"}, {"field": "count"}],
                    },
                    "height": 300,
                },
                use_container_width=True,
            )
    else:
        st.info(t("no_data"))

    # Table + Filters
    st.markdown("---")
    st.markdown("### 📋 " + t("history"))

    with st.expander("🔍 Filters", expanded=False):
        f1, f2, f3 = st.columns(3)
        with f1:
            parasite_filter = st.selectbox("Parasite", ["All"] + sorted(df["parasite_detected"].unique().tolist()))
        with f2:
            validated_filter = st.selectbox("Status", ["All", "Validated", "Not validated"])
        with f3:
            min_conf = st.slider("Min confidence", 0, 100, 0, 5)

    fdf = df.copy()
    if parasite_filter != "All":
        fdf = fdf[fdf["parasite_detected"] == parasite_filter]
    if validated_filter == "Validated":
        fdf = fdf[fdf["validated"] == 1]
    elif validated_filter == "Not validated":
        fdf = fdf[fdf["validated"] == 0]
    fdf = fdf[fdf["confidence"] >= min_conf]

    show_cols = [c for c in ["id", "analysis_date", "patient_name", "parasite_detected", "confidence", "risk_level", "analyst", "validated"] if c in fdf.columns]
    out_df = fdf[show_cols].copy()
    if "analysis_date" in out_df.columns:
        out_df["analysis_date"] = out_df["analysis_date"].apply(fmt_dt)
    if "validated" in out_df.columns:
        out_df["validated"] = out_df["validated"].apply(lambda x: "✅" if x else "⏳")
    st.dataframe(out_df, use_container_width=True, height=420)

    # Validation (tech+)
    if has_role(2) and "validated" in fdf.columns and not fdf.empty:
        unv = fdf[fdf["validated"] == 0]
        if not unv.empty:
            st.markdown("---")
            st.markdown("### ✅ " + t("validate"))
            vv1, vv2 = st.columns([3, 1])
            with vv1:
                vid = st.selectbox(
                    "Select analysis",
                    unv["id"].tolist(),
                    format_func=lambda x: f"#{x} — {unv[unv['id']==x]['patient_name'].values[0]} — {unv[unv['id']==x]['parasite_detected'].values[0]}",
                )
            with vv2:
                if st.button("✅ " + t("validate"), use_container_width=True, type="primary"):
                    db_validate_analysis(int(vid), st.session_state.user_full_name)
                    db_log(st.session_state.user_id, st.session_state.user_name, "Validated analysis", f"ID:{vid}")
                    st.success(f"Validated #{vid}")
                    time.sleep(0.6)
                    st.rerun()

    # Exports
    st.markdown("---")
    st.markdown("### 📥 " + t("export"))
    e1, e2, e3 = st.columns(3)
    with e1:
        st.download_button(
            "📄 CSV",
            data=fdf.to_csv(index=False).encode("utf-8-sig"),
            file_name=f"analyses_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    with e2:
        st.download_button(
            "📈 Excel",
            data=export_excel_bytes(fdf),
            file_name=f"analyses_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True,
        )
    with e3:
        st.download_button(
            "🧾 JSON",
            data=export_json_bytes(fdf.to_dict(orient="records")),
            file_name=f"analyses_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
        )


# ============================================================
# QUIZ (Gamified)
# ============================================================
elif selected_page == "quiz":
    st.markdown(f"<h1 class='dm-title'>🧠 {t('quiz')}</h1>", unsafe_allow_html=True)

    qs = st.session_state.quiz_state

    # Leaderboard
    with st.expander("🏆 " + t("leaderboard"), expanded=False):
        lb = db_leaderboard(20)
        if not lb:
            st.info(t("no_data"))
        else:
            for i, row in enumerate(lb):
                medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
                st.markdown(
                    f"<div class='dm-card' style='padding:12px;margin:8px 0;'>"
                    f"{medal} <b>{row['username']}</b> — {row['score']}/{row['total_questions']} "
                    f"({row['percentage']:.0f}%) <span class='dm-muted'>— {time_ago(row['timestamp'])}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Start screen
    if not qs.get("active") and not qs.get("finished"):
        st.markdown(
            f"<div class='dm-card' style='text-align:center;padding:22px;'>"
            f"<div style='font-size:4rem'>🎮</div>"
            f"<div style='font-weight:900;font-size:1.3rem;margin-top:8px;'>Parasitology Quiz</div>"
            f"<div class='dm-muted' style='margin-top:6px;'>{len(QUIZ_QUESTIONS)}+ questions</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        c1, c2 = st.columns(2)
        with c1:
            n_q = st.slider("Questions", 5, min(30, len(QUIZ_QUESTIONS)), 10)
            diff = st.selectbox("Difficulty", ["Tous", "easy", "medium", "hard"])
        with c2:
            cats = sorted(list(set([q.get("cat", "General") for q in QUIZ_QUESTIONS])))
            cat = st.selectbox("Category", ["All"] + cats)
            timed = st.checkbox("⏱️ Timed (60s/question)", value=False)

        if st.button("🚀 " + t("start_quiz"), use_container_width=True, type="primary"):
            pool = list(range(len(QUIZ_QUESTIONS)))
            if cat != "All":
                pool = [i for i in pool if QUIZ_QUESTIONS[i].get("cat") == cat]
            if diff != "Tous":
                pool = [i for i in pool if QUIZ_QUESTIONS[i].get("difficulty") == diff]
            if not pool:
                pool = list(range(len(QUIZ_QUESTIONS)))

            random.shuffle(pool)
            order = pool[: min(n_q, len(pool))]

            st.session_state.quiz_state = {
                "active": True,
                "finished": False,
                "current": 0,
                "score": 0,
                "order": order,
                "wrong": [],
                "answered": [],
                "total_q": len(order),
                "selected_answer": None,
                "show_result": False,
                "start_time": time.time() if timed else None,
                "difficulty": diff,
                "category": cat,
                "timed": timed,
            }
            db_log(st.session_state.user_id, st.session_state.user_name, "Quiz started", f"n={len(order)} diff={diff} cat={cat}")
            st.rerun()

    # Active quiz
    elif qs.get("active") and not qs.get("finished"):
        cur = qs["current"]
        order = qs["order"]
        total = qs["total_q"]

        qidx = order[cur]
        q = QUIZ_QUESTIONS[qidx]

        st.progress((cur + 1) / total)
        h1, h2 = st.columns([3, 1])
        with h1:
            st.markdown(f"### Q {cur+1}/{total}")
            st.caption(f"📂 {q.get('cat','General')} — ⚡ {q.get('difficulty','')}")
        with h2:
            if qs.get("timed") and qs.get("start_time"):
                elapsed = int(time.time() - qs["start_time"])
                remain = 60 - (elapsed % 60)
                st.metric("⏱️", f"{remain}s")

        st.markdown(
            f"<div class='dm-card' style='padding:18px;'><div style='font-size:1.1rem;font-weight:800;line-height:1.6'>{tl(q['q'])}</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        if not qs.get("show_result"):
            cols = st.columns(2)
            for i, opt in enumerate(q["opts"]):
                with cols[i % 2]:
                    if st.button(f"{['A','B','C','D'][i]}. {opt}", key=f"opt_{cur}_{i}", use_container_width=True):
                        correct = (i == q["ans"])
                        st.session_state.quiz_state["selected_answer"] = i
                        st.session_state.quiz_state["show_result"] = True
                        st.session_state.quiz_state["answered"].append(correct)
                        if correct:
                            st.session_state.quiz_state["score"] += 1
                        else:
                            st.session_state.quiz_state["wrong"].append({
                                "q": tl(q["q"]),
                                "your": opt,
                                "correct": q["opts"][q["ans"]],
                            })
                        st.rerun()
        else:
            selected = qs.get("selected_answer", -1)
            correct_idx = q["ans"]
            ok = selected == correct_idx
            if ok:
                st.success("✅ Correct")
            else:
                st.error(f"❌ Correct answer: **{q['opts'][correct_idx]}**")

            expl = tl(q.get("expl", {}))
            if expl:
                st.info("📖 " + expl)

            # next
            if cur + 1 < total:
                if st.button("➡️ " + t("next_question"), use_container_width=True, type="primary"):
                    st.session_state.quiz_state["current"] += 1
                    st.session_state.quiz_state["show_result"] = False
                    st.session_state.quiz_state["selected_answer"] = None
                    st.rerun()
            else:
                if st.button("🏁 Finish", use_container_width=True, type="primary"):
                    st.session_state.quiz_state["active"] = False
                    st.session_state.quiz_state["finished"] = True
                    st.rerun()

    # Finished
    elif qs.get("finished"):
        score = int(qs.get("score", 0))
        total = int(qs.get("total_q", 1))
        pct = int((score / total) * 100) if total > 0 else 0

        badge = "🏆" if pct >= 90 else "🥇" if pct >= 75 else "🥈" if pct >= 60 else "🥉" if pct >= 40 else "💪"
        msg = "EXCELLENT" if pct >= 75 else "GOOD" if pct >= 60 else "KEEP PRACTICING"

        st.markdown(
            f"<div class='dm-card' style='text-align:center;padding:26px;'>"
            f"<div style='font-size:5rem'>{badge}</div>"
            f"<div class='dm-title' style='font-size:2rem'>Results</div>"
            f"<div style='font-size:3.2rem;font-weight:900;margin:10px 0'>{score}/{total}</div>"
            f"<div class='dm-muted' style='font-size:1.2rem'>{pct}% — {msg}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        # Save score once
        if not qs.get("_saved"):
            time_taken = int(time.time() - qs["start_time"]) if qs.get("start_time") else 0
            db_quiz_save(st.session_state.user_id, st.session_state.user_name, score, total, pct,
                        qs.get("category", "general"), qs.get("difficulty", "medium"), time_taken)
            db_log(st.session_state.user_id, st.session_state.user_name, "Quiz completed", f"{score}/{total}={pct}%")
            st.session_state.quiz_state["_saved"] = True

        wrong = qs.get("wrong", [])
        if wrong:
            st.markdown("---")
            st.markdown(f"### ❌ Review ({len(wrong)})")
            for i, w in enumerate(wrong, 1):
                with st.expander(f"Question {i}"):
                    st.markdown(f"**{w['q']}**")
                    st.markdown(f"- ❌ Your answer: ~~{w['your']}~~")
                    st.markdown(f"- ✅ Correct: **{w['correct']}**")

        st.markdown("---")
        if st.button("🔄 " + t("restart"), use_container_width=True, type="primary"):
            st.session_state.quiz_state = {
                "active": False, "finished": False, "current": 0, "score": 0,
                "order": [], "wrong": [], "answered": [], "total_q": 0,
                "selected_answer": None, "show_result": False, "start_time": None,
                "difficulty": "Tous", "category": "All", "timed": False,
            }
            st.rerun()


# ============================================================
# CHATBOT
# ============================================================
elif selected_page == "chatbot":
    st.markdown(f"<h1 class='dm-title'>💬 {t('chatbot')}</h1>", unsafe_allow_html=True)

    st.markdown(
        "<div class='dm-card'>"
        "<div style='display:flex;gap:12px;align-items:center;'>"
        "<div style='font-size:2.8rem'>🤖</div>"
        "<div><div style='font-weight:900;font-size:1.2rem'>DM Bot</div>"
        "<div class='dm-muted'>Rule-based assistant (no API)</div></div>"
        "</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    hist = st.session_state.chat_ui["history"]
    if not hist:
        hist.append({"role": "bot", "msg": t("chat_welcome")})

    # show chat
    for m in hist[-30:]:
        if m["role"] == "user":
            st.markdown(
                f"<div style='display:flex;justify-content:flex-end;margin:10px 0;'>"
                f"<div class='dm-card' style='max-width:85%;border-left:5px solid #22d3ee;'>"
                f"<b>👤</b><br>{m['msg']}</div></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div style='display:flex;justify-content:flex-start;margin:10px 0;'>"
                f"<div class='dm-card' style='max-width:85%;border-left:5px solid #a78bfa;'>"
                f"<b>🤖</b><br>{m['msg']}</div></div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    with st.form("chat_form", clear_on_submit=True):
        user_txt = st.text_input(t("chat_placeholder"), label_visibility="collapsed", placeholder=t("chat_placeholder"))
        c1, c2, c3 = st.columns([3, 1, 1])
        with c1:
            send = st.form_submit_button("📨 " + t("send"), use_container_width=True)
        with c2:
            clear = st.form_submit_button("🗑️ " + t("clear"), use_container_width=True)
        with c3:
            listen = st.form_submit_button("🔊 " + t("listen"), use_container_width=True)

    if send and user_txt and user_txt.strip():
        msg = user_txt.strip()
        hist.append({"role": "user", "msg": msg})
        rep = chatbot_reply(msg)
        hist.append({"role": "bot", "msg": rep})
        st.session_state.chat_ui["history"] = hist

        db_save_chat(st.session_state.user_id, msg, rep)
        db_log(st.session_state.user_id, st.session_state.user_name, "Chat", msg[:120])
        st.rerun()

    if clear:
        st.session_state.chat_ui["history"] = []
        st.rerun()

    if listen:
        last = [x for x in reversed(hist) if x["role"] == "bot"]
        if last:
            speak(last[0]["msg"])
            st.rerun()

    st.markdown("---")
    st.markdown("### " + t("quick_questions"))
    row1 = ["amoeba", "giardia", "plasmodium", "leishmania", "trypanosoma", "schistosoma"]
    cols = st.columns(len(row1))
    for col, kw in zip(cols, row1):
        with col:
            if st.button(kw.title(), use_container_width=True):
                hist.append({"role": "user", "msg": kw})
                hist.append({"role": "bot", "msg": chatbot_reply(kw)})
                st.session_state.chat_ui["history"] = hist
                st.rerun()

    row2 = ["microscope", "coloration", "concentration", "traitement", "aide"]
    cols2 = st.columns(len(row2))
    for col, kw in zip(cols2, row2):
        with col:
            if st.button(kw.title(), key=f"kw_{kw}", use_container_width=True):
                hist.append({"role": "user", "msg": kw})
                hist.append({"role": "bot", "msg": chatbot_reply(kw)})
                st.session_state.chat_ui["history"] = hist
                st.rerun()


# ============================================================
# COMPARE IMAGES
# ============================================================
elif selected_page == "compare":
    st.markdown(f"<h1 class='dm-title'>🔄 {t('compare')}</h1>", unsafe_allow_html=True)
    st.markdown(
        "<div class='dm-card'>Compare two microscope images (SSIM-like, MSE, pixel diff, histograms).</div>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    c1, c2 = st.columns(2)
    with c1:
        f1 = st.file_uploader("Image 1", type=["jpg", "jpeg", "png", "bmp"], key="cmp1")
    with c2:
        f2 = st.file_uploader("Image 2", type=["jpg", "jpeg", "png", "bmp"], key="cmp2")

    if not f1 or not f2:
        st.stop()

    img1 = Image.open(f1).convert("RGB")
    img2 = Image.open(f2).convert("RGB")

    p1, p2 = st.columns(2)
    with p1:
        st.image(img1, caption="Image 1", use_container_width=True)
    with p2:
        st.image(img2, caption="Image 2", use_container_width=True)

    st.markdown("---")
    if st.button("🔍 " + t("compare_btn"), use_container_width=True, type="primary"):
        with st.spinner(t("analyzing")):
            met = compare_images(img1, img2)

        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.metric("📊 " + t("similarity"), f"{met['similarity']}%")
        with s2:
            st.metric("🎯 SSIM", f"{met['ssim']}")
        with s3:
            st.metric("📐 MSE", f"{met['mse']}")
        with s4:
            sim = met["similarity"]
            verdict = "Very similar" if sim >= 90 else "Similar" if sim >= 70 else "Somewhat different" if sim >= 50 else "Very different"
            st.metric("🧾 Verdict", verdict)

        st.markdown("---")
        st.markdown("### 🔍 Pixel difference")
        diff = pixel_difference(img1, img2)
        d1, d2, d3 = st.columns(3)
        with d1:
            st.image(img1, caption="Image 1", use_container_width=True)
        with d2:
            st.image(diff, caption="Diff", use_container_width=True)
        with d3:
            st.image(img2, caption="Image 2", use_container_width=True)

        st.markdown("---")
        st.markdown("### 🎨 Filter comparison")
        filters = [("Thermal", thermal_view), ("Edges", edges_filter), ("Enhanced", enhanced_filter), ("Negative", negative_filter), ("Emboss", emboss_filter)]
        for name, fn in filters:
            with st.expander(name, expanded=False):
                cc1, cc2 = st.columns(2)
                with cc1:
                    st.image(fn(img1), caption=f"Image 1 — {name}", use_container_width=True)
                with cc2:
                    st.image(fn(img2), caption=f"Image 2 — {name}", use_container_width=True)

        st.markdown("---")
        st.markdown("### 📊 RGB Histograms")
        h1 = get_histogram(img1)
        h2 = get_histogram(img2)
        if HAS_PLOTLY:
            fig = go.Figure()
            fig.add_trace(go.Scatter(y=h1["red"], name="Img1-R", line=dict(color="rgba(255,0,0,0.5)")))
            fig.add_trace(go.Scatter(y=h1["green"], name="Img1-G", line=dict(color="rgba(0,255,0,0.5)")))
            fig.add_trace(go.Scatter(y=h1["blue"], name="Img1-B", line=dict(color="rgba(0,0,255,0.5)")))
            fig.add_trace(go.Scatter(y=h2["red"], name="Img2-R", line=dict(color="rgba(255,0,0,0.9)", dash="dash")))
            fig.add_trace(go.Scatter(y=h2["green"], name="Img2-G", line=dict(color="rgba(0,255,0,0.9)", dash="dash")))
            fig.add_trace(go.Scatter(y=h2["blue"], name="Img2-B", line=dict(color="rgba(0,0,255,0.9)", dash="dash")))
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)
        else:
            # Simple table fallback
            st.info("Plotly not available; histogram overlay disabled.")
            st.write("Histogram computed (R/G/B).")

        db_log(st.session_state.user_id, st.session_state.user_name, "Image comparison", f"Similarity: {met['similarity']}%")
# ============================================================
# PAGES — ADMIN / ABOUT + GLOBAL FOOTER (FINAL)
# ============================================================

# ---- Extra metadata (from your previous app spirit) ----
AUTHORS = [
    {"name": "Sebbag Mohamed Dhia Eddine", "role": {"fr": "Expert IA & Conception", "ar": "خبير ذكاء اصطناعي وتصميم", "en": "AI & Design Expert"}},
    {"name": "Ben Sghir Mohamed", "role": {"fr": "Expert Laboratoire & Données", "ar": "خبير مخبر وبيانات", "en": "Laboratory & Data Expert"}},
]

INSTITUTION = {
    "name": {
        "fr": "Institut National de Formation Supérieure Paramédicale",
        "ar": "المعهد الوطني للتكوين العالي شبه الطبي",
        "en": "National Institute of Higher Paramedical Training",
    },
    "short": "INFSPM",
    "city": "Ouargla",
    "country": {"fr": "Algérie", "ar": "الجزائر", "en": "Algeria"},
    "year": 2026,
}

PROJECT_TITLE = {
    "fr": "Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais",
    "ar": "استكشاف إمكانيات الذكاء الاصطناعي للقراءة الآلية للفحص الطفيلي المباشر",
    "en": "Exploring AI potential for automatic reading of fresh parasitological examination",
}

TR["fr"].update({
    "admin_access_required": "Accès administrateur requis.",
    "system_info": "Infos système",
    "activity_log": "Journal d'activité",
    "users_mgmt": "Gestion utilisateurs",
})
TR["ar"].update({
    "admin_access_required": "صلاحيات المدير مطلوبة.",
    "system_info": "معلومات النظام",
    "activity_log": "سجل النشاط",
    "users_mgmt": "إدارة المستخدمين",
})
TR["en"].update({
    "admin_access_required": "Admin access required.",
    "system_info": "System info",
    "activity_log": "Activity log",
    "users_mgmt": "User management",
})


# ============================================================
# ADMIN
# ============================================================
elif selected_page == "admin":
    st.markdown(f"<h1 class='dm-title'>⚙️ {t('admin')}</h1>", unsafe_allow_html=True)

    if not has_role(3):
        st.error("🔒 " + t("admin_access_required"))
        st.stop()

    tab1, tab2, tab3, tab4 = st.tabs([
        f"👥 {t('users_mgmt')}",
        f"📜 {t('activity_log')}",
        f"🖥️ {t('system_info')}",
        f"📊 {t('statistics')}",
    ])

    # --- TAB 1: Users ---
    with tab1:
        st.markdown("### 👥 Users")
        users = db_users()
        if users:
            udf = pd.DataFrame(users)
            show = udf.copy()
            if "is_active" in show.columns:
                show["is_active"] = show["is_active"].apply(lambda x: "✅" if x else "❌")
            if "last_login" in show.columns:
                show["last_login"] = show["last_login"].apply(lambda x: fmt_dt(x) if x else "—")
            st.dataframe(show, use_container_width=True, height=320)
        else:
            st.info(t("no_data"))

        st.markdown("---")
        st.markdown("#### ⚙️ Actions")

        a1, a2, a3 = st.columns(3, vertical_alignment="top")

        with a1:
            st.markdown("**Activate / Disable**")
            uid = st.number_input("User ID", min_value=1, step=1, value=1, key="adm_uid_toggle")
            status = st.selectbox("Status", ["Active", "Inactive"], key="adm_status_toggle")
            if st.button("Apply", use_container_width=True, key="adm_apply_toggle"):
                db_toggle_user(int(uid), status == "Active")
                db_log(st.session_state.user_id, st.session_state.user_name, "User toggled", f"#{uid} -> {status}")
                st.success("Updated")
                time.sleep(0.4)
                st.rerun()

        with a2:
            st.markdown("**Change password**")
            uid2 = st.number_input("User ID ", min_value=1, step=1, value=1, key="adm_uid_pwd")
            new_pw = st.text_input("New password", type="password", key="adm_new_pw")
            if st.button("Change", use_container_width=True, key="adm_apply_pwd"):
                if not new_pw:
                    st.warning("Enter password")
                else:
                    db_change_password(int(uid2), new_pw)
                    db_log(st.session_state.user_id, st.session_state.user_name, "Password changed", f"#{uid2}")
                    st.success("Password updated")

        with a3:
            st.markdown("**User statistics**")
            if users:
                ulist = [u["id"] for u in users]
                pick = st.selectbox("User", ulist, format_func=lambda x: f"#{x}", key="adm_stats_user")
                if st.button("Show", use_container_width=True, key="adm_show_user_stats"):
                    s = db_stats(int(pick))
                    c1, c2, c3, c4 = st.columns(4)
                    with c1:
                        st.metric("Total", s["total"])
                    with c2:
                        st.metric("Reliable", s["reliable"])
                    with c3:
                        st.metric("To verify", s["to_verify"])
                    with c4:
                        st.metric("Avg conf", f"{s['avg_confidence']}%")

        st.markdown("---")
        st.markdown("### ➕ Create user")
        with st.form("adm_create_user"):
            c1, c2 = st.columns(2)
            with c1:
                nu = st.text_input("Username *")
                nf = st.text_input("Full name *")
                ne = st.text_input("Email")
            with c2:
                npw = st.text_input("Password *", type="password")
                nr = st.selectbox("Role", list(ROLES.keys()))
                ns = st.text_input("Speciality", value="Laboratoire")
            submit = st.form_submit_button("Create", use_container_width=True)
        if submit:
            ok = db_create_user(nu, npw, nf, nr, ns, ne)
            if ok:
                db_log(st.session_state.user_id, st.session_state.user_name, "User created", nu)
                st.success("User created")
                time.sleep(0.4)
                st.rerun()
            else:
                st.error("Username exists or missing fields")

    # --- TAB 2: Activity log ---
    with tab2:
        st.markdown("### 📜 Logs")
        c1, c2 = st.columns([3, 1])
        with c1:
            logs = db_logs(800)
            names = sorted({(l.get("username") or "—") for l in logs})
            pick = st.selectbox("Filter by user", ["All"] + names, key="adm_log_user")
        with c2:
            limit = st.number_input("Limit", min_value=50, max_value=1000, value=200, step=50, key="adm_log_limit")

        logs = db_logs(int(limit))
        if pick != "All":
            logs = [l for l in logs if (l.get("username") or "—") == pick]

        if not logs:
            st.info(t("no_data"))
        else:
            for l in logs:
                action = l.get("action", "—")
                base = action.split()[0] if action else ""
                color = {
                    "Login": "#22c55e",
                    "Logout": "#f59e0b",
                    "Analysis": "#22d3ee",
                    "Validated": "#10b981",
                    "Quiz": "#a78bfa",
                    "Chat": "#fb7185",
                    "Image": "#60a5fa",
                    "User": "#f97316",
                    "Password": "#ef4444",
                }.get(base, "#94a3b8")

                st.markdown(
                    f"<div class='dm-card' style='padding:12px;margin:8px 0;border-left:5px solid {color};'>"
                    f"<div style='display:flex;justify-content:space-between;gap:10px;'>"
                    f"<div><b style='color:{color}'>{action}</b> <span class='dm-muted'>— {l.get('username','—')}</span></div>"
                    f"<div class='dm-muted'>{time_ago(l.get('timestamp',''))}</div></div>"
                    f"{f\"<div class='dm-muted' style='margin-top:6px'>{l.get('details','')}</div>\" if l.get('details') else ''}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # --- TAB 3: System info + maintenance ---
    with tab3:
        st.markdown("### 🖥️ System")

        s1, s2, s3 = st.columns(3, vertical_alignment="top")

        with s1:
            st.markdown(
                "<div class='dm-card'>"
                "<h4 style='margin:0'>🧩 Runtime</h4>"
                f"<div class='dm-muted' style='margin-top:10px'>"
                f"<b>Version:</b> {APP_VERSION}<br>"
                f"<b>Python:</b> {os.sys.version.split()[0]}<br>"
                f"<b>Streamlit:</b> {st.__version__}<br>"
                f"<b>TensorFlow:</b> {'✅' if HAS_TF else '❌'}<br>"
                f"<b>Plotly:</b> {'✅' if HAS_PLOTLY else '❌'}<br>"
                f"<b>FPDF:</b> {'✅' if HAS_FPDF else '❌'}<br>"
                f"<b>QR:</b> {'✅' if HAS_QRCODE else '❌'}<br>"
                f"<b>Bcrypt:</b> {'✅' if HAS_BCRYPT else '❌ (SHA256 fallback)'}"
                "</div></div>",
                unsafe_allow_html=True,
            )

        with s2:
            total_stats = db_stats()
            total_users = len(db_users())
            st.markdown(
                "<div class='dm-card'>"
                "<h4 style='margin:0'>🗄️ Database</h4>"
                f"<div class='dm-muted' style='margin-top:10px'>"
                f"<b>Users:</b> {total_users}<br>"
                f"<b>Analyses:</b> {total_stats['total']}<br>"
                f"<b>Reliable:</b> {total_stats['reliable']}<br>"
                f"<b>Validated:</b> {total_stats['validated']}<br>"
                f"<b>Quiz scores:</b> {len(db_leaderboard(2000))}<br>"
                f"<b>Logs:</b> {len(db_logs(5000))}"
                "</div></div>",
                unsafe_allow_html=True,
            )

        with s3:
            db_size_kb = (os.path.getsize(DB_PATH) / 1024.0) if os.path.exists(DB_PATH) else 0.0
            st.markdown(
                "<div class='dm-card'>"
                "<h4 style='margin:0'>💾 Storage</h4>"
                f"<div class='dm-muted' style='margin-top:10px'>"
                f"<b>DB size:</b> {db_size_kb:.1f} KB<br>"
                f"<b>Parasites:</b> {len(CLASS_NAMES)}<br>"
                f"<b>Quiz questions:</b> {len(QUIZ_QUESTIONS)}<br>"
                f"<b>Chat KB:</b> {len(CHAT_KB)}"
                "</div></div>",
                unsafe_allow_html=True,
            )

        st.markdown("---")
        st.markdown("### 🔧 Maintenance")
        m1, m2, m3 = st.columns(3)
        with m1:
            if st.button("🔄 VACUUM / Optimize DB", use_container_width=True):
                with st.spinner("Optimizing..."):
                    with db() as c:
                        c.execute("VACUUM")
                        c.execute("ANALYZE")
                st.success("Done")
        with m2:
            if st.button("🗑️ Keep last 1000 logs", use_container_width=True):
                with st.spinner("Cleaning..."):
                    with db() as c:
                        c.execute("""
                          DELETE FROM activity_log
                          WHERE id NOT IN (
                            SELECT id FROM activity_log
                            ORDER BY timestamp DESC
                            LIMIT 1000
                          )
                        """)
                st.success("Done")
        with m3:
            if st.button("📦 Backup (download DB)", use_container_width=True):
                if os.path.exists(DB_PATH):
                    with open(DB_PATH, "rb") as f:
                        st.download_button(
                            "⬇️ Download DB",
                            data=f.read(),
                            file_name=DB_PATH,
                            mime="application/octet-stream",
                            use_container_width=True,
                        )
                else:
                    st.warning("DB not found")

    # --- TAB 4: Advanced statistics ---
    with tab4:
        st.markdown("### 📊 Advanced statistics")
        all_analyses = db_analyses(limit=5000)
        if not all_analyses:
            st.info(t("no_data"))
        else:
            df_all = pd.DataFrame(all_analyses)

            # Per-user performance
            st.markdown("#### 👥 Performance by analyst")
            if "analyst" in df_all.columns:
                grp = df_all.groupby("analyst").agg(
                    total=("id", "count"),
                    avg_conf=("confidence", "mean"),
                    reliable=("is_reliable", "sum"),
                    validated=("validated", "sum"),
                ).reset_index()
                grp["avg_conf"] = grp["avg_conf"].round(1)

                if HAS_PLOTLY:
                    fig = px.bar(grp, x="analyst", y=["total", "reliable", "validated"], barmode="group")
                    fig.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                st.dataframe(grp, use_container_width=True, height=240)

            # Time-of-day analysis (if parseable)
            st.markdown("---")
            st.markdown("#### ⏰ Time distribution (hour)")
            try:
                dt = pd.to_datetime(df_all["analysis_date"], errors="coerce")
                df_all["hour"] = dt.dt.hour
                hour = df_all.groupby("hour").size().reset_index(name="count")
                if HAS_PLOTLY:
                    fig = px.line(hour, x="hour", y="count", markers=True)
                    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.vega_lite_chart(
                        hour,
                        {"mark": {"type": "line", "point": True},
                         "encoding": {"x": {"field": "hour", "type": "quantitative"},
                                      "y": {"field": "count", "type": "quantitative"}}},
                        use_container_width=True,
                    )
            except Exception:
                st.info("Time parsing not available.")


# ============================================================
# ABOUT
# ============================================================
elif selected_page == "about":
    st.markdown(f"<h1 class='dm-title'>ℹ️ {t('about')}</h1>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='dm-card' style='text-align:center;padding:22px;'>"
        f"<div style='font-size:3.2rem'>🧬</div>"
        f"<div style='font-weight:900;font-size:1.6rem;margin-top:8px;'>DM SMART LAB AI</div>"
        f"<div class='dm-muted'>Version {APP_VERSION}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 📖 Project")
    st.info(f"**{tl(PROJECT_TITLE)}**")

    st.markdown("---")
    c1, c2 = st.columns(2, vertical_alignment="top")

    with c1:
        st.markdown("### 👨‍💻 Team")
        for a in AUTHORS:
            st.success(f"**{a['name']}**\n\n{tl(a['role'])}")

    with c2:
        st.markdown("### 🏛️ Institution")
        st.markdown(
            f"**{tl(INSTITUTION['name'])}**  \n"
            f"**{INSTITUTION['short']} — {INSTITUTION['city']}**, {tl(INSTITUTION['country'])}  \n"
            f"📅 {INSTITUTION['year']}"
        )
        st.markdown("#### 🎯 Objectives")
        st.markdown(
            "- Automate microscope reading\n"
            "- Reduce diagnostic errors\n"
            "- Speed up workflow\n"
            "- Assist training and reporting"
        )

    st.markdown("---")
    st.markdown("### 🛠️ Tech stack")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("🐍 Python", os.sys.version.split()[0])
    with m2:
        st.metric("🎨 Streamlit", st.__version__)
    with m3:
        st.metric("🧠 TensorFlow", (tf.__version__ if HAS_TF else "N/A"))
    with m4:
        st.metric("📊 Plotly", ("OK" if HAS_PLOTLY else "N/A"))

    st.markdown("---")
    st.markdown("### 📈 System stats")
    try:
        s = db_stats()
        x1, x2, x3, x4, x5 = st.columns(5)
        with x1:
            st.metric("🔬 Analyses", s["total"])
        with x2:
            st.metric("✅ Reliable", s["reliable"])
        with x3:
            st.metric("🧾 Validated", s["validated"])
        with x4:
            st.metric("🦠 Parasites", len(CLASS_NAMES) - 1)
        with x5:
            st.metric("⭐ Avg conf", f"{s['avg_confidence']}%")
    except Exception:
        st.info("Stats available after first runs.")


# ============================================================
# GLOBAL FOOTER (always)
# ============================================================
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center;opacity:0.55;font-size:0.82rem;padding:10px 0;">
      DM Smart Lab AI v{APP_VERSION} — {INSTITUTION['short']} {INSTITUTION['city']} 🇩🇿 — {INSTITUTION['year']}<br>
      Developed by {AUTHORS[0]['name']} &amp; {AUTHORS[1]['name']}
    </div>
    """,
    unsafe_allow_html=True,
)
