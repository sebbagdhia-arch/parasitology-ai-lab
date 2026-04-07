"""
╔══════════════════════════════════════════════════════════════════════════════════╗
║                  DM SMART LAB AI v8.0 - ULTIMATE EDITION                        ║
║            Advanced Parasitological Diagnosis System with AI                      ║
║                                                                                    ║
║  Developers:                                                                       ║
║    • Sebbag Mohamed Dhia Eddine (AI & System Architecture)                       ║
║    • Ben Sghir Mohamed (Laboratory & Data Science)                               ║
║                                                                                    ║
║  INFSPM - Ouargla, Algeria 🇩🇿                                                   ║
║  Copyright © 2026 - All Rights Reserved                                          ║
╚══════════════════════════════════════════════════════════════════════════════════╝
"""

# ============================================
#  IMPORTS
# ============================================
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
import secrets
from PIL import Image, ImageOps, ImageFilter, ImageEnhance, ImageDraw, ImageFont
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import re

# Optional imports with fallbacks
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    st.warning("⚠️ bcrypt not installed. Using SHA256 fallback.")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    st.warning("⚠️ Plotly not installed. Charts disabled.")

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False
    st.warning("⚠️ FPDF not installed. PDF export disabled.")

try:
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from openpyxl.chart import BarChart, PieChart, Reference
    HAS_EXCEL = True
except ImportError:
    HAS_EXCEL = False

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

# ============================================
#  PAGE CONFIG
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI v8.0 Ultimate",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/dmsmartlab',
        'Report a bug': 'https://github.com/dmsmartlab/issues',
        'About': "DM Smart Lab AI v8.0 - Ultimate Edition"
    }
)

# ============================================
#  CONSTANTS
# ============================================
APP_VERSION = "8.0.0"
APP_NAME = "DM Smart Lab AI"
BUILD_DATE = "2026-01-15"
SECRET_KEY = "dm_smart_lab_2026_ultra_secret_key_v8"

# Security
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
SESSION_TIMEOUT = 120

# AI Model
MODEL_INPUT_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 60
HIGH_CONFIDENCE = 80
LOW_CONFIDENCE = 40

# Files
MAX_FILE_SIZE_MB = 10
MAX_BATCH_UPLOAD = 50
ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "bmp", "tiff"]

# Database
DB_PATH = "dm_smartlab_v8.db"

# Roles
ROLES = {
    "admin": {
        "level": 5, "icon": "👑",
        "label": {"fr": "Administrateur", "ar": "مدير", "en": "Administrator"},
        "permissions": ["all"]
    },
    "supervisor": {
        "level": 4, "icon": "👨‍⚕️",
        "label": {"fr": "Superviseur", "ar": "مشرف", "en": "Supervisor"},
        "permissions": ["view_all", "validate", "export", "reports"]
    },
    "technician": {
        "level": 3, "icon": "🔬",
        "label": {"fr": "Technicien", "ar": "تقني", "en": "Technician"},
        "permissions": ["scan", "view_own", "save", "export_own"]
    },
    "trainee": {
        "level": 2, "icon": "🎓",
        "label": {"fr": "Stagiaire", "ar": "متدرب", "en": "Trainee"},
        "permissions": ["scan", "view_own", "training"]
    },
    "viewer": {
        "level": 1, "icon": "👁️",
        "label": {"fr": "Observateur", "ar": "مراقب", "en": "Viewer"},
        "permissions": ["view_own"]
    }
}

# Colors
NEON = {
    "cyan": "#00f5ff", "magenta": "#ff00ff", "green": "#00ff88",
    "orange": "#ff6600", "red": "#ff0040", "blue": "#0066ff",
    "purple": "#9933ff", "yellow": "#ffff00", "pink": "#ff69b4"
}

RISK_COLORS = {
    "critical": "#ff0040", "high": "#ff3366", "medium": "#ff9500",
    "low": "#00e676", "none": "#00ff88"
}

# Laboratory
MICROSCOPE_TYPES = [
    "Microscope Optique Standard", "Microscope Binoculaire", "Microscope Trinoculaire",
    "Microscope Inversé", "Microscope à Fluorescence", "Microscope Contraste de Phase",
    "Microscope Fond Noir", "Microscope Numérique", "Microscope Confocal"
]

MAGNIFICATIONS = ["x4", "x10", "x20", "x40", "x60", "x100 (Immersion)"]

PREPARATION_TYPES = [
    "État Frais (Direct)", "État Frais + Lugol", "Concentration Ritchie (Formol-Éther)",
    "Concentration MIF", "Concentration Willis (Flottation)", "Kato-Katz",
    "Coloration MGG", "Coloration Giemsa", "Ziehl-Neelsen Modifié",
    "Coloration Trichrome", "Goutte Épaisse + Frottis", "Scotch-Test (Graham)",
    "Technique Baermann", "Culture NNN", "PCR Parasitaire"
]

SAMPLE_TYPES = {
    "fr": ["Selles", "Sang (Frottis)", "Sang (Goutte épaisse)", "Urines", "LCR",
           "Biopsie Cutanée", "Suc Ganglionnaire", "Crachat", "Moelle Osseuse", "Autre"],
    "ar": ["براز", "دم (لطاخة)", "دم (قطرة سميكة)", "بول", "سائل دماغي شوكي",
           "خزعة جلدية", "عصارة عقدية", "بلغم", "نقي عظم", "أخرى"],
    "en": ["Stool", "Blood (Smear)", "Blood (Thick drop)", "Urine", "CSF",
           "Skin Biopsy", "Lymph Node", "Sputum", "Bone Marrow", "Other"]
}

# Parasite Database
CLASS_NAMES = [
    "Amoeba (E. histolytica)", "Giardia", "Plasmodium",
    "Leishmania", "Trypanosoma", "Schistosoma", "Negative"
]

PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "sci": "Entamoeba histolytica",
        "morph": {
            "fr": "Kyste sphérique 10-15μm à 4 noyaux, corps chromatoïdes en cigare. Trophozoïte 20-40μm avec pseudopodes et hématies phagocytées.",
            "ar": "كيس كروي 10-15 ميكرومتر بـ 4 أنوية، جسم كروماتيني سيجاري. طور نشط 20-40 ميكرومتر مع أقدام كاذبة وكريات حمراء مبتلعة.",
            "en": "Spherical cyst 10-15μm with 4 nuclei, cigar-shaped chromatoid bodies. Trophozoite 20-40μm with pseudopods and phagocytosed RBCs."
        },
        "desc": {
            "fr": "Protozoaire responsable de l'amibiase intestinale et hépatique. Transmission féco-orale. Forme invasive = E. histolytica, forme commensale = E. dispar.",
            "ar": "طفيلي أولي مسؤول عن الأميبيا المعوية والكبدية. الانتقال عبر الفم-البراز. الشكل الغازي = E. histolytica.",
            "en": "Protozoan causing intestinal and hepatic amebiasis. Fecal-oral transmission. Invasive form = E. histolytica."
        },
        "funny": {
            "fr": "Le ninja des intestins ! Adore grignoter les globules rouges au petit-déjeuner ! 🥷🔴",
            "ar": "نينجا الأمعاء! يحب قضم كريات الدم الحمراء في الفطور! 🥷🔴",
            "en": "The intestinal ninja! Loves munching red blood cells for breakfast! 🥷🔴"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Métronidazole 500mg x3/j (7-10j) + Tiliquinol (Intetrix) 2cp x3/j. Contrôle EPS J15/J30. Éviter aliments crus.",
            "ar": "ميترونيدازول 500 ملغ 3 مرات يومياً (7-10 أيام) + Tiliquinol. مراقبة بعد 15 و 30 يوم. تجنب الطعام النيء.",
            "en": "Metronidazole 500mg x3/d (7-10d) + Tiliquinol (Intetrix). Follow-up D15/D30. Avoid raw food."
        },
        "tests": ["Sérologie amibienne (Elisa)", "Échographie hépatique", "NFS + CRP", "Coproculture", "PCR E. histolytica"],
        "color": "#ff0040", "icon": "🔴",
        "cycle": {
            "fr": "Kyste ingéré → Excystation intestin grêle → Trophozoïte → Colonisation côlon → Invasion (parfois) → Enkystement → Émission selles",
            "ar": "كيس مبتلع ← انفكاس أمعاء دقيقة ← طور نشط ← استعمار القولون ← غزو (أحياناً) ← تكيس ← إفراز في البراز",
            "en": "Ingested cyst → Excystation small intestine → Trophozoite → Colon colonization → Invasion (sometimes) → Encystation → Stool emission"
        },
        "keys": {
            "fr": "• E. histolytica vs E. dispar: seule histolytica phagocyte hématies\n• Kyste 4 noyaux (vs E. coli 8 noyaux)\n• Corps chromatoïdes en cigare (vs baguette)\n• Mobilité directionnelle active",
            "ar": "• E. histolytica مقابل E. dispar: فقط histolytica تبتلع الكريات\n• كيس 4 أنوية (مقابل 8 لـ E. coli)\n• أجسام كروماتينية سيجارية\n• حركة اتجاهية نشطة",
            "en": "• E. histolytica vs E. dispar: only histolytica phagocytoses RBCs\n• 4-nuclei cyst (vs E. coli 8)\n• Cigar-shaped chromatoid bodies\n• Active directional motility"
        }
    },
    "Giardia": {
        "sci": "Giardia lamblia (intestinalis)",
        "morph": {
            "fr": "Trophozoïte piriforme 12-15μm en cerf-volant, 2 noyaux (face de hibou), disque ventral adhésif, 4 paires de flagelles. Kyste ovoïde 8-12μm à 4 noyaux.",
            "ar": "طور نشط كمثري 12-15 ميكرومتر شكل طائرة ورقية، نواتان (وجه البومة)، قرص بطني لاصق، 4 أزواج أسواط. كيس بيضاوي 8-12 ميكرومتر بـ 4 أنوية.",
            "en": "Pear-shaped trophozoite 12-15μm kite-like, 2 nuclei (owl face), ventral adhesive disk, 4 flagella pairs. Ovoid cyst 8-12μm with 4 nuclei."
        },
        "desc": {
            "fr": "Flagellé du duodénum. Diarrhée graisseuse chronique, malabsorption, ballonnements. Transmission hydrique (eau contaminée). Très fréquent chez enfants.",
            "ar": "سوطي الاثني عشر. إسهال دهني مزمن، سوء امتصاص، انتفاخ. انتقال عبر الماء الملوث. شائع جداً عند الأطفال.",
            "en": "Duodenal flagellate. Chronic greasy diarrhea, malabsorption, bloating. Waterborne transmission. Very common in children."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil (2 noyaux) ! Un touriste collant qui refuse de partir ! 🕶️😄",
            "ar": "ينظر إليك بنظارته الشمسية (نواتان)! سائح لزج يرفض المغادرة! 🕶️😄",
            "en": "Stares at you with sunglasses (2 nuclei)! A clingy tourist who refuses to leave! 🕶️😄"
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "advice": {
            "fr": "Métronidazole 250mg x3/j (5-7j) OU Tinidazole 2g dose unique. Traiter toute la famille. Désinfecter eau (ébullition 10 min).",
            "ar": "ميترونيدازول 250 ملغ 3 مرات يومياً (5-7 أيام) أو تينيدازول 2 غرام جرعة واحدة. علاج كل العائلة. تعقيم الماء (غلي 10 دقائق).",
            "en": "Metronidazole 250mg x3/d (5-7d) OR Tinidazole 2g single dose. Treat whole family. Disinfect water (boil 10 min)."
        },
        "tests": ["Antigène Giardia (ELISA selles)", "Test malabsorption (D-xylose)", "EPS x3 jours consécutifs", "PCR Giardia"],
        "color": "#ff9500", "icon": "🟠",
        "cycle": {
            "fr": "Kyste ingéré → Excystation duodénale → Trophozoïte binucléé → Adhésion villosités → Multiplication asexuée → Enkystement iléon → Émission",
            "ar": "كيس مبتلع ← انفكاس في الاثني عشر ← طور نشط ثنائي النواة ← التصاق بالزغابات ← تكاثر لاجنسي ← تكيس في اللفائفي ← إفراز",
            "en": "Ingested cyst → Duodenal excystation → Binucleate trophozoite → Villi adhesion → Asexual multiplication → Ileum encystation → Emission"
        },
        "keys": {
            "fr": "• Forme cerf-volant = PATHOGNOMONIQUE\n• 2 noyaux symétriques = face de hibou\n• Disque ventral visible au Lugol\n• Mobilité feuille morte (oscillante)\n• État frais < 30 min crucial",
            "ar": "• شكل طائرة ورقية = مميز جداً\n• نواتان متماثلتان = وجه البومة\n• القرص البطني مرئي باللوغول\n• حركة ورقة ميتة (متذبذبة)\n• الفحص المباشر < 30 دقيقة حاسم",
            "en": "• Kite shape = PATHOGNOMONIC\n• 2 symmetrical nuclei = owl face\n• Ventral disk visible with Lugol\n• Falling leaf motility\n• Fresh exam < 30 min crucial"
        }
    },
    "Plasmodium": {
        "sci": "Plasmodium falciparum / vivax / ovale / malariae",
        "morph": {
            "fr": "P. falciparum: anneau en bague à chaton, gamétocytes en banane. P. vivax: trophozoïte amœboïde, granulations de Schüffner, hématies augmentées de volume.",
            "ar": "P. falciparum: حلقة خاتم، خلايا جنسية موزية. P. vivax: طور نشط أميبي، حبيبات شوفنر، كريات حمراء متضخمة.",
            "en": "P. falciparum: signet ring, banana gametocytes. P. vivax: amoeboid trophozoite, Schüffner's dots, enlarged RBCs."
        },
        "desc": {
            "fr": "⚠️ URGENCE MÉDICALE ! Paludisme = 1ère cause mortalité parasitaire mondiale. P. falciparum = le plus mortel (accès pernicieux). Anophèle femelle = vecteur.",
            "ar": "⚠️ حالة طوارئ طبية! الملاريا = السبب الأول لوفيات الطفيليات عالمياً. P. falciparum = الأكثر فتكاً. أنثى الأنوفيل = الناقل.",
            "en": "⚠️ MEDICAL EMERGENCY! Malaria = 1st cause parasitic mortality worldwide. P. falciparum = most lethal. Female Anopheles = vector."
        },
        "funny": {
            "fr": "Le champion olympique du saut ! Saute du moustique à ton foie en 0.001 seconde ! 🏅🦟",
            "ar": "بطل الأولمبياد في القفز! يقفز من البعوضة إلى كبدك في 0.001 ثانية! 🏅🦟",
            "en": "Olympic jump champion! Jumps from mosquito to your liver in 0.001 second! 🏅🦟"
        },
        "risk": "critical",
        "risk_d": {"fr": "CRITIQUE - URGENCE", "ar": "حرج - طوارئ", "en": "CRITICAL - EMERGENCY"},
        "advice": {
            "fr": "🚨 HOSPITALISATION IMMÉDIATE ! ACT (Artemether-Lumefantrine) 1ère ligne. Quinine IV si accès grave. Parasitémie /4-6h. Surveillance réanimation si >2%.",
            "ar": "🚨 دخول المستشفى فوراً! ACT خط أول. كينين وريدي إذا خطير. فحص الطفيليات كل 4-6 ساعات. مراقبة مشددة إذا > 2%.",
            "en": "🚨 IMMEDIATE HOSPITALIZATION! ACT 1st line. IV Quinine if severe. Parasitemia /4-6h. ICU monitoring if >2%."
        },
        "tests": ["TDR Paludisme (HRP2/pLDH) URGENCE", "Frottis + Goutte épaisse /4-6h", "Parasitémie quantitative", "NFS", "Bilan hépato-rénal", "Glycémie", "Lactates"],
        "color": "#7f1d1d", "icon": "🚨",
        "cycle": {
            "fr": "Piqûre anophèle → Sporozoïtes (sang) → Hépatocytes (cycle exo-érythrocytaire) → Mérozoïtes → Hématies (cycle érythrocytaire) → Gamétocytes → Anophèle",
            "ar": "لدغة الأنوفيل ← سبوروزويت (دم) ← خلايا كبدية (دورة خارج كريات) ← ميروزويت ← كريات حمراء (دورة داخل كريات) ← خلايا جنسية ← الأنوفيل",
            "en": "Anopheles bite → Sporozoites (blood) → Hepatocytes (exo-erythrocytic cycle) → Merozoites → RBCs (erythrocytic cycle) → Gametocytes → Anopheles"
        },
        "keys": {
            "fr": "• URGENCE < 2H diagnostic\n• Frottis mince = espèce / Goutte épaisse = sensibilité 10x\n• Parasitémie > 2% = ACCÈS GRAVE\n• Banane (gamétocyte) = P. falciparum\n• Schüffner + hématie ↑ = P. vivax\n• TDR positif ≠ paludisme actif (peut rester + 2 semaines)",
            "ar": "• طوارئ < ساعتين للتشخيص\n• لطاخة = النوع / قطرة سميكة = حساسية × 10\n• طفيليات > 2% = حالة خطيرة\n• موز (خلية جنسية) = P. falciparum\n• شوفنر + كرية ↑ = P. vivax",
            "en": "• URGENT < 2H diagnosis\n• Thin smear = species / Thick drop = 10x sensitivity\n• Parasitemia > 2% = SEVERE ACCESS\n• Banana = P. falciparum\n• Schüffner + RBC ↑ = P. vivax"
        }
    },
    "Leishmania": {
        "sci": "Leishmania infantum / major / tropica",
        "morph": {
            "fr": "Amastigotes ovoïdes intracellulaires 2-5μm dans macrophages. Noyau + kinétoplaste visible MGG/Giemsa. Promastigotes flagellés en culture NNN.",
            "ar": "أماستيغوت بيضاوية داخل خلوية 2-5 ميكرومتر في البلاعم. نواة + كينيتوبلاست مرئي MGG/جيمزا. بروماستيغوت سوطية في زراعة NNN.",
            "en": "Intracellular ovoid amastigotes 2-5μm in macrophages. Nucleus + kinetoplast visible MGG/Giemsa. Flagellated promastigotes in NNN culture."
        },
        "desc": {
            "fr": "Transmis par phlébotome. Forme cutanée (bouton d'Orient) ou viscérale (Kala-azar). Algérie: L. infantum (nord), L. major (sud). MDO (Maladie à Déclaration Obligatoire).",
            "ar": "ينتقل عبر ذبابة الرمل. شكل جلدي (حبة حلب) أو حشوي. الجزائر: L. infantum (شمال)، L. major (جنوب). مرض تبليغ إجباري.",
            "en": "Sandfly-transmitted. Cutaneous (Oriental sore) or visceral (Kala-azar). Algeria: L. infantum (north), L. major (south). Notifiable disease."
        },
        "funny": {
            "fr": "Petit mais costaud ! S'installe dans les macrophages comme dans un hôtel 5 étoiles ! 🏨⭐",
            "ar": "صغير لكن قوي! يستقر في البلاعم كأنه في فندق 5 نجوم! 🏨⭐",
            "en": "Small but mighty! Settles in macrophages like a 5-star hotel! 🏨⭐"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Cutanée: Glucantime (antimoine) IM 20mg/kg/j (20-30j) OU cryothérapie azote. Viscérale: Amphotéricine B liposomale IV. MDO = déclarer ARS.",
            "ar": "جلدية: غلوكانتيم عضلياً 20 ملغ/كغ/يوم (20-30 يوم) أو معالجة بالتبريد. حشوية: أمفوتيريسين ب وريدياً. تبليغ إجباري.",
            "en": "Cutaneous: Glucantime IM 20mg/kg/d (20-30d) OR cryotherapy. Visceral: Liposomal Amphotericin B IV. Notifiable disease."
        },
        "tests": ["IDR Montenegro (léishmanine)", "Sérologie Leishmania (ELISA, IFI)", "Ponction ganglion/rate/moelle + MGG", "Biopsie cutanée + Giemsa", "Culture NNN", "PCR Leishmania (gold standard)"],
        "color": "#ff0040", "icon": "🔴",
        "cycle": {
            "fr": "Piqûre phlébotome → Promastigotes → Phagocytose macrophages → Transformation amastigotes → Multiplication intracellulaire → Lyse cellule → Dissémination → Repas sanguin phlébotome",
            "ar": "لدغة ذبابة رمل ← بروماستيغوت ← بلعمة بالبلاعم ← تحول لأماستيغوت ← تكاثر داخل خلوي ← تحلل الخلية ← انتشار ← وجبة دم ذبابة الرمل",
            "en": "Sandfly bite → Promastigotes → Macrophage phagocytosis → Amastigote transformation → Intracellular multiplication → Cell lysis → Dissemination → Sandfly blood meal"
        },
        "keys": {
            "fr": "• Amastigotes 2-5μm intracellulaires obligatoires\n• Noyau + kinétoplaste (barre) en MGG/Giemsa\n• Culture NNN = transformation promastigotes\n• PCR = sensibilité/spécificité maximale\n• IDR Montenegro + si contact antérieur",
            "ar": "• أماستيغوت 2-5 ميكرومتر داخل خلوية إلزامياً\n• نواة + كينيتوبلاست (عصا) في MGG\n• زراعة NNN = تحول لبروماستيغوت\n• PCR = أعلى حساسية/نوعية",
            "en": "• 2-5μm obligate intracellular amastigotes\n• Nucleus + kinetoplast (bar) in MGG\n• NNN culture = promastigote transformation\n• PCR = maximum sensitivity/specificity"
        }
    },
    "Trypanosoma": {
        "sci": "Trypanosoma brucei gambiense / rhodesiense / cruzi",
        "morph": {
            "fr": "Forme S/C allongée 15-30μm, flagelle libre, membrane ondulante latérale, kinétoplaste postérieur. Noyau central. MGG: bleu + kinétoplaste violet foncé.",
            "ar": "شكل S/C ممدود 15-30 ميكرومتر، سوط حر، غشاء متموج جانبي، كينيتوبلاست خلفي. نواة مركزية. MGG: أزرق + كينيتوبلاست بنفسجي غامق.",
            "en": "Elongated S/C shape 15-30μm, free flagellum, lateral undulating membrane, posterior kinetoplast. Central nucleus. MGG: blue + dark purple kinetoplast."
        },
        "desc": {
            "fr": "Maladie du sommeil africaine (T. brucei, vecteur glossine/tsé-tsé) ou maladie de Chagas américaine (T. cruzi, vecteur triatome). Phase hémolymphatique puis neurologique (franchissement BHE).",
            "ar": "مرض النوم الأفريقي (T. brucei، ناقل ذبابة تسي تسي) أو مرض شاغاس الأمريكي (T. cruzi، ناقل بق ثلاثي). مرحلة دموية لمفاوية ثم عصبية.",
            "en": "African sleeping sickness (T. brucei, tsetse vector) or American Chagas disease (T. cruzi, triatomine vector). Hemolymphatic then neurological phase (BBB crossing)."
        },
        "funny": {
            "fr": "Le sprinteur du sang ! Court à 100 km/h avec sa membrane ondulante comme une cape de super-héros ! 🦸‍♂️💨",
            "ar": "عداء الدم السريع! يركض بـ 100 كم/ساعة بغشائه المتموج كعباءة بطل خارق! 🦸‍♂️💨",
            "en": "The blood sprinter! Runs 100 km/h with undulating membrane like a superhero cape! 🦸‍♂️💨"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Phase 1 (hémolymphatique): Pentamidine/Suramine. Phase 2 (neurologique): NECT (Nifurtimox-Eflornithine) ou Mélarsoprol. PL OBLIGATOIRE staging. Hospitalisation spécialisée.",
            "ar": "المرحلة 1: بنتاميدين/سورامين. المرحلة 2: NECT أو ميلارسوبرول. بزل قطني إجباري للتصنيف. دخول المستشفى المتخصص.",
            "en": "Phase 1: Pentamidine/Suramine. Phase 2: NECT or Melarsoprol. LP MANDATORY staging. Specialized hospitalization."
        },
        "tests": ["Ponction lombaire (PL) + cytologie", "Sérologie CATT (Card Agglutination Test)", "IgM LCR très élevées", "Ganglion lymphatique ponction", "Frottis sanguin + Goutte épaisse", "Mini Anion Exchange Centrifugation (mAECT)"],
        "color": "#ff0040", "icon": "🔴",
        "cycle": {
            "fr": "Piqûre tsé-tsé/triatome → Trypomastigotes sanguins → Multiplication → Invasion SNC (phase 2) → Chronicité → Piqûre vecteur → Cycle chez vecteur",
            "ar": "لدغة تسي تسي/بق ثلاثي ← تريبوماستيغوت دموية ← تكاثر ← غزو الجهاز العصبي (مرحلة 2) ← تمزمن ← لدغة ناقل ← دورة في الناقل",
            "en": "Tsetse/triatomine bite → Blood trypomastigotes → Multiplication → CNS invasion (phase 2) → Chronicity → Vector bite → Cycle in vector"
        },
        "keys": {
            "fr": "• Forme S/C + membrane ondulante = DIAGNOSTIC\n• Kinétoplaste postérieur (vs Leishmania)\n• PL OBLIGATOIRE = staging phase 1/2\n• IgM LCR >>> 10 mg/L = neuro\n• Ganglion cervical postérieur palpable\n• mAECT = concentration trypanosomes",
            "ar": "• شكل S/C + غشاء متموج = تشخيصي\n• كينيتوبلاست خلفي (مقابل ليشمانيا)\n• بزل قطني إجباري = تصنيف مرحلة 1/2\n• IgM سائل دماغي شوكي >>> 10 ملغ/لتر = عصبي",
            "en": "• S/C shape + undulating membrane = DIAGNOSTIC\n• Posterior kinetoplast (vs Leishmania)\n• LP MANDATORY = phase 1/2 staging\n• CSF IgM >>> 10 mg/L = neuro\n• Palpable posterior cervical lymph node"
        }
    },
    "Schistosoma": {
        "sci": "Schistosoma haematobium / mansoni / japonicum",
        "morph": {
            "fr": "Œuf ovoïde 115-170μm avec éperon: terminal proéminent (S. haematobium) ou latéral (S. mansoni). Miracidium mobile cilié visible à l'intérieur si œuf viable.",
            "ar": "بيضة بيضاوية 115-170 ميكرومتر مع شوكة: طرفية بارزة (S. haematobium) أو جانبية (S. mansoni). ميراسيديوم متحرك هدبي مرئي داخلياً إذا البيضة حية.",
            "en": "Ovoid egg 115-170μm with spine: prominent terminal (S. haematobium) or lateral (S. mansoni). Motile ciliated miracidium visible inside if viable egg."
        },
        "desc": {
            "fr": "Bilharziose (schistosomiase). S. haematobium: uro-génitale (hématurie terminale). S. mansoni: hépato-intestinale. Transmission: baignade eau douce contaminée (cercaires pénètrent peau).",
            "ar": "البلهارسيا. S. haematobium: بولي تناسلي (بيلة دموية نهائية). S. mansoni: كبدي معوي. الانتقال: السباحة في ماء عذب ملوث (سركاريا تخترق الجلد).",
            "en": "Bilharziasis (schistosomiasis). S. haematobium: urogenital (terminal hematuria). S. mansoni: hepato-intestinal. Transmission: freshwater swimming (cercariae penetrate skin)."
        },
        "funny": {
            "fr": "L'œuf avec un dard dangereux ! Les cercaires = micro-torpilles nageuses qui adorent ta peau ! 🏊‍♂️🎯",
            "ar": "البيضة ذات الشوكة الخطيرة! السركاريا = طوربيدات صغيرة سابحة تعشق جلدك! 🏊‍♂️🎯",
            "en": "Egg with dangerous spine! Cercariae = micro-torpedoes swimmers who love your skin! 🏊‍♂️🎯"
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "advice": {
            "fr": "Praziquantel 40mg/kg dose unique (adultes/enfants >4 ans). S. haematobium: prélever urines de MIDI (10h-14h = pic excrétion). Éviter baignades eaux douces stagnantes zones endémiques.",
            "ar": "برازيكوانتيل 40 ملغ/كغ جرعة واحدة (بالغين/أطفال >4 سنوات). S. haematobium: جمع بول الظهيرة (10ص-2م = ذروة الإفراز). تجنب السباحة في المياه العذبة الراكدة بالمناطق الموبوءة.",
            "en": "Praziquantel 40mg/kg single dose (adults/children >4y). S. haematobium: collect MIDDAY urine (10am-2pm = excretion peak). Avoid swimming stagnant freshwater endemic areas."
        },
        "tests": ["ECBU urines de midi (S. haematobium)", "EPS concentration Kato-Katz (S. mansoni)", "Sérologie bilharziose", "Échographie vésicale/hépatique", "NFS (éosinophilie +++)", "Biopsie rectale (S. mansoni)"],
        "color": "#ff9500", "icon": "🟠",
        "cycle": {
            "fr": "Œuf émis urines/selles → Eau douce → Miracidium → Mollusque (Bulinus/Biomphalaria) → Cercaires → Pénétration cutanée homme → Schistosomules → Migration → Vers adultes (vaisseaux) → Ponte œufs",
            "ar": "بيضة مفرزة بول/براز ← ماء عذب ← ميراسيديوم ← رخويات ← سركاريا ← اختراق جلد الإنسان ← شيستوسومول ← هجرة ← ديدان بالغة (أوعية) ← وضع البيض",
            "en": "Egg shed urine/stool → Freshwater → Miracidium → Snail (Bulinus/Biomphalaria) → Cercariae → Human skin penetration → Schistosomules → Migration → Adult worms (vessels) → Egg laying"
        },
        "keys": {
            "fr": "• S. haematobium: éperon TERMINAL + urines MIDI (10-14h)\n• S. mansoni: éperon LATÉRAL + selles\n• Miracidium mobile = œuf VIABLE\n• Éosinophilie sanguine élevée (20-40%)\n• Échographie: épaississement paroi vessie (S. h.)",
            "ar": "• S. haematobium: شوكة طرفية + بول الظهيرة (10-14 ساعة)\n• S. mansoni: شوكة جانبية + براز\n• ميراسيديوم متحرك = بيضة حية\n• فرط حمضات مرتفع (20-40%)\n• إيكو: سماكة جدار المثانة",
            "en": "• S. haematobium: TERMINAL spine + MIDDAY urine (10-14h)\n• S. mansoni: LATERAL spine + stool\n• Motile miracidium = VIABLE egg\n• High eosinophilia (20-40%)\n• Ultrasound: bladder wall thickening"
        }
    },
    "Negative": {
        "sci": "N/A",
        "morph": {
            "fr": "Absence d'éléments parasitaires. Flore bactérienne normale. Leucocytes/hématies éventuels. Débris alimentaires/cellulaires.",
            "ar": "غياب العناصر الطفيلية. فلورا بكتيرية طبيعية. كريات بيضاء/حمراء محتملة. بقايا طعامية/خلوية.",
            "en": "No parasitic elements. Normal bacterial flora. Possible leucocytes/RBCs. Food/cellular debris."
        },
        "desc": {
            "fr": "Échantillon négatif. ATTENTION: un seul examen négatif N'EXCLUT PAS le diagnostic (sensibilité EPS direct 50-60%). RÉPÉTER x3 jours consécutifs si suspicion clinique forte.",
            "ar": "عينة سلبية. تحذير: فحص واحد سلبي لا يستبعد التشخيص (حساسية الفحص المباشر 50-60%). كرر 3 أيام متتالية إذا كان هناك اشتباه سريري قوي.",
            "en": "Negative sample. WARNING: single negative exam DOES NOT EXCLUDE diagnosis (direct EPS sensitivity 50-60%). REPEAT x3 consecutive days if strong clinical suspicion."
        },
        "funny": {
            "fr": "Rien à signaler ! Mais les parasites sont des ninjas du cache-cache... Prudence ! 🥷🔍",
            "ar": "لا شيء يذكر! لكن الطفيليات نينجا في الاختباء... حذر! 🥷🔍",
            "en": "Nothing to report! But parasites are hide-and-seek ninjas... Be careful! 🥷🔍"
        },
        "risk": "none",
        "risk_d": {"fr": "Négatif", "ar": "سلبي", "en": "Negative"},
        "advice": {
            "fr": "RAS (Rien À Signaler) sur cet examen. Si symptômes persistent: RÉPÉTER EPS x3 jours consécutifs + envisager sérologies ciblées + autres examens (coproculture, recherche toxines, etc.).",
            "ar": "لا شيء على هذا الفحص. إذا استمرت الأعراض: كرر الفحص 3 أيام متتالية + فكر في فحوصات مصلية مستهدفة + فحوصات أخرى.",
            "en": "NAD (Nothing Abnormal Detected) on this exam. If symptoms persist: REPEAT EPS x3 consecutive days + consider targeted serologies + other exams."
        },
        "tests": ["Répéter EPS x3 jours consécutifs", "Sérologies ciblées selon clinique", "Coproculture bactérienne", "Recherche toxines Clostridium difficile", "NFS (éosinophilie?)"],
        "color": "#00ff88", "icon": "🟢",
        "cycle": {"fr": "N/A", "ar": "غير متوفر", "en": "N/A"},
        "keys": {
            "fr": "• État frais + Lugol = négatif\n• Concentration (Ritchie/Willis) = négative\n• RÉPÉTER x3 si clinique évocatrice\n• Sensibilité 1 seul EPS = 50-60%\n• 3 EPS consécutifs = 90% sensibilité",
            "ar": "• فحص مباشر + لوغول = سلبي\n• تركيز (ريتشي/ويليس) = سلبي\n• كرر 3 مرات إذا كانت الأعراض موحية\n• حساسية فحص واحد = 50-60%\n• 3 فحوصات متتالية = 90% حساسية",
            "en": "• Fresh + Lugol = negative\n• Concentration = negative\n• REPEAT x3 if suggestive symptoms\n• Single EPS sensitivity = 50-60%\n• 3 consecutive EPS = 90% sensitivity"
        }
    }
}

# Tips
DAILY_TIPS = {
    "fr": [
        "💡 Examiner selles < 30 min pour trophozoïtes mobiles.",
        "💡 Lugol frais chaque semaine pour noyaux nets.",
        "💡 Frottis mince angle 45° = monocouche parfaite.",
        "💡 Goutte épaisse 10x plus sensible que frottis.",
        "💡 Urines MIDI (10-14h) pour S. haematobium.",
        "💡 Répéter EPS x3 jours consécutifs obligatoire.",
        "💡 Métronidazole = Amoeba + Giardia + Trichomonas.",
        "💡 ZN modifié indispensable Cryptosporidium.",
        "💡 1ère GE négative insuffisante. Répéter 6-12h.",
        "💡 Éosinophilie = helminthiase. Toujours vérifier.",
        "💡 Nettoyer objectif x100 après huile immersion.",
        "💡 Calibrer microscope hebdomadairement.",
        "💡 Température salle optimale: 20-25°C.",
        "💡 Lumière naturelle = meilleure qualité image.",
        "💡 Laver lames: détergent puis alcool 70°.",
    ],
    "ar": [
        "💡 فحص البراز < 30 دقيقة للأطوار المتحركة.",
        "💡 لوغول طازج كل أسبوع للأنوية الواضحة.",
        "💡 اللطاخة الرقيقة زاوية 45° = طبقة واحدة.",
        "💡 القطرة السميكة أكثر حساسية 10 مرات.",
        "💡 بول الظهيرة (10-14 ساعة) لـ S. haematobium.",
        "💡 تكرار الفحص 3 أيام متتالية إجباري.",
        "💡 ميترونيدازول = أميبا + جيارديا.",
        "💡 ZN معدل ضروري للكريبتوسبوريديوم.",
        "💡 قطرة سميكة سلبية واحدة غير كافية.",
        "💡 فرط الحمضات = ديدان. تحقق دائماً.",
    ],
    "en": [
        "💡 Examine stool < 30 min for motile trophozoites.",
        "💡 Fresh Lugol weekly for clear nuclei.",
        "💡 Thin smear 45° angle = perfect monolayer.",
        "💡 Thick drop 10x more sensitive than smear.",
        "💡 MIDDAY urine (10-14h) for S. haematobium.",
        "💡 Repeat EPS x3 consecutive days mandatory.",
        "💡 Metronidazole = Amoeba + Giardia + Trichomonas.",
        "💡 Modified ZN essential for Cryptosporidium.",
        "💡 1st negative thick drop insufficient.",
        "💡 Eosinophilia = helminthiasis. Always check.",
    ]
}

# ============================================
#  SESSION STATE DEFAULTS
# ============================================
DEFAULTS = {
    "logged_in": False,
    "user_id": None,
    "user_name": "",
    "user_role": "viewer",
    "user_full_name": "",
    "user_email": "",
    "lang": "fr",
    "theme": "dark",
    "demo_seed": None,
    "heatmap_seed": None,
    "notifications": [],
    "unread_count": 0,
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
    "batch_images": [],
    "batch_results": [],
    "current_patient": None,
    "training_session": None,
}

for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ============================================
#  DATABASE SETUP
# ============================================
@contextmanager
def get_db():
    """Database context manager"""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        # Users table
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            role TEXT DEFAULT 'viewer',
            speciality TEXT DEFAULT 'Laboratoire',
            phone TEXT,
            is_active INTEGER DEFAULT 1,
            is_verified INTEGER DEFAULT 0,
            is_2fa_enabled INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            total_analyses INTEGER DEFAULT 0,
            accurate_analyses INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            language TEXT DEFAULT 'fr',
            theme TEXT DEFAULT 'dark',
            notifications_enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Patients table
        conn.execute("""CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth TIMESTAMP,
            age INTEGER,
            sex TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            city TEXT,
            medical_history TEXT,
            allergies TEXT,
            medications TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_visit TIMESTAMP
        )""")
        
        # Analyses table
        conn.execute("""CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            analysis_id TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            patient_id INTEGER,
            sample_type TEXT,
            collection_date TIMESTAMP,
            reception_date TIMESTAMP,
            microscope_type TEXT,
            magnification TEXT,
            preparation_type TEXT,
            technician1 TEXT,
            technician2 TEXT,
            parasite_detected TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT,
            is_reliable INTEGER DEFAULT 0,
            all_predictions TEXT,
            image_hash TEXT,
            image_path TEXT,
            heatmap_path TEXT,
            model_version TEXT,
            model_name TEXT,
            is_demo INTEGER DEFAULT 0,
            validated INTEGER DEFAULT 0,
            validated_by TEXT,
            validation_date TIMESTAMP,
            validation_notes TEXT,
            reviewed INTEGER DEFAULT 0,
            reviewed_by TEXT,
            review_date TIMESTAMP,
            review_status TEXT,
            clinical_notes TEXT,
            treatment_prescribed TEXT,
            follow_up_required INTEGER DEFAULT 0,
            follow_up_date TIMESTAMP,
            status TEXT DEFAULT 'pending',
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (patient_id) REFERENCES patients(id)
        )""")
        
        # Notifications table
        conn.execute("""CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            action_url TEXT,
            action_label TEXT,
            is_read INTEGER DEFAULT 0,
            read_at TIMESTAMP,
            priority INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Activity log table
        conn.execute("""CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Quiz scores table
        conn.execute("""CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            category TEXT DEFAULT 'general',
            difficulty TEXT DEFAULT 'mixed',
            time_taken INTEGER,
            correct_answers TEXT,
            wrong_answers TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Appointments table
        conn.execute("""CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            appointment_date TIMESTAMP NOT NULL,
            appointment_type TEXT,
            status TEXT DEFAULT 'scheduled',
            notes TEXT,
            reminder_sent INTEGER DEFAULT 0,
            created_by INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )""")
        
        # Badges table
        conn.execute("""CREATE TABLE IF NOT EXISTS badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            badge_key TEXT UNIQUE NOT NULL,
            name_fr TEXT,
            name_ar TEXT,
            name_en TEXT,
            description_fr TEXT,
            description_ar TEXT,
            description_en TEXT,
            icon TEXT,
            color TEXT,
            requirement TEXT,
            points INTEGER DEFAULT 10
        )""")
        
        # User badges junction table
        conn.execute("""CREATE TABLE IF NOT EXISTS user_badges (
            user_id INTEGER NOT NULL,
            badge_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, badge_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (badge_id) REFERENCES badges(id)
        )""")
        
        _create_default_data(conn)

def _hash_password(password: str) -> str:
    """Hash password"""
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()

def _verify_password(password: str, hashed: str) -> bool:
    """Verify password"""
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
            pass
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest() == hashed

def _create_default_data(conn):
    """Create default users and badges"""
    cursor = conn.cursor()
    
    # Check if admin exists
    if cursor.execute("SELECT 1 FROM users WHERE username='admin'").fetchone():
        return
    
    # Create default users
    default_users = [
        ('admin', 'admin2026', 'Administrateur Système', 'admin@dmsmartlab.dz', 'admin', 'Administration'),
        ('dhia', 'dhia2026', 'Sebbag Mohamed Dhia Eddine', 'dhia@dmsmartlab.dz', 'admin', 'IA & Architecture'),
        ('mohamed', 'mohamed2026', 'Ben Sghir Mohamed', 'mohamed@dmsmartlab.dz', 'supervisor', 'Laboratoire & Data'),
        ('tech1', 'tech2026', 'Technicien Labo 1', 'tech1@dmsmartlab.dz', 'technician', 'Parasitologie'),
        ('trainee1', 'trainee123', 'Stagiaire 1', 'trainee1@dmsmartlab.dz', 'trainee', 'Formation'),
        ('demo', 'demo123', 'Utilisateur Démo', 'demo@dmsmartlab.dz', 'viewer', 'Démonstration'),
    ]
    
    for username, password, full_name, email, role, speciality in default_users:
        cursor.execute("""INSERT INTO users 
            (username, password_hash, full_name, email, role, speciality, is_active, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, 1, 1)""",
            (username, _hash_password(password), full_name, email, role, speciality))
    
    # Create default badges
    default_badges = [
        ('first_analysis', 'Premier Pas', 'الخطوة الأولى', 'First Step', '🎯', 'Première analyse', 10),
        ('hundred_analyses', 'Centurion', 'المائوي', 'Centurion', '💯', '100 analyses', 100),
        ('perfect_month', 'Mois Parfait', 'شهر مثالي', 'Perfect Month', '⭐', 'Mois sans erreur', 50),
        ('speed_master', 'Flash', 'البرق', 'Flash', '⚡', '10 analyses en 1h', 30),
        ('critical_finder', 'Détective', 'المحقق', 'Detective', '🔍', '5 cas critiques', 40),
    ]
    
    for badge_data in default_badges:
        cursor.execute("""INSERT INTO badges 
            (badge_key, name_fr, name_ar, name_en, icon, description_fr, points)
            VALUES (?, ?, ?, ?, ?, ?, ?)""", badge_data)
    
    conn.commit()

# Initialize database
init_database()

# ============================================
#  DATABASE OPERATIONS
# ============================================
def db_login(username: str, password: str) -> Optional[Dict]:
    """Authenticate user"""
    with get_db() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND is_active=1",
            (username,)
        ).fetchone()
        
        if not user:
            return None
        
        # Check lockout
        if user['locked_until']:
            try:
                if datetime.now() < datetime.fromisoformat(user['locked_until']):
                    return {"error": "locked", "until": user['locked_until']}
                conn.execute(
                    "UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?",
                    (user['id'],)
                )
            except:
                pass
        
        # Verify password
        if not _verify_password(password, user['password_hash']):
            new_attempts = user['failed_attempts'] + 1
            locked = None
            if new_attempts >= MAX_LOGIN_ATTEMPTS:
                locked = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
            conn.execute(
                "UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?",
                (new_attempts, locked, user['id'])
            )
            return {"error": "wrong", "attempts_left": MAX_LOGIN_ATTEMPTS - new_attempts}
        
        # Success - update login info
        conn.execute("""UPDATE users SET 
            failed_attempts=0, locked_until=NULL, last_login=?, login_count=login_count+1
            WHERE id=?""",
            (datetime.now().isoformat(), user['id'])
        )
        
        return dict(user)

def db_create_user(username: str, password: str, full_name: str, 
                   email: str = None, role: str = "viewer", speciality: str = "") -> bool:
    """Create new user"""
    with get_db() as conn:
        if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
            return False
        
        conn.execute("""INSERT INTO users 
            (username, password_hash, full_name, email, role, speciality)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (username, _hash_password(password), full_name, email, role, speciality))
        return True

def db_get_users() -> List[Dict]:
    """Get all users"""
    with get_db() as conn:
        users = conn.execute("""SELECT id, username, full_name, email, role, speciality,
            is_active, last_login, login_count, total_analyses, points, level
            FROM users ORDER BY created_at DESC""").fetchall()
        return [dict(u) for u in users]

def db_toggle_user(user_id: int, active: bool):
    """Toggle user active status"""
    with get_db() as conn:
        conn.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, user_id))

def db_change_password(user_id: int, new_password: str):
    """Change user password"""
    with get_db() as conn:
        conn.execute("UPDATE users SET password_hash=? WHERE id=?",
                    (_hash_password(new_password), user_id))

def db_create_patient(first_name: str, last_name: str, **kwargs) -> str:
    """Create new patient"""
    with get_db() as conn:
        patient_id = f"PAT-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(4).upper()}"
        
        conn.execute("""INSERT INTO patients 
            (patient_id, first_name, last_name, age, sex, phone, email, address, city)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (patient_id, first_name, last_name,
             kwargs.get('age'), kwargs.get('sex'), kwargs.get('phone'),
             kwargs.get('email'), kwargs.get('address'), kwargs.get('city')))
        
        return patient_id

def db_search_patients(query: str) -> List[Dict]:
    """Search patients"""
    with get_db() as conn:
        search = f"%{query}%"
        patients = conn.execute("""SELECT * FROM patients WHERE
            patient_id LIKE ? OR first_name LIKE ? OR last_name LIKE ?
            ORDER BY last_visit DESC LIMIT 50""",
            (search, search, search)).fetchall()
        return [dict(p) for p in patients]

def db_create_analysis(user_id: int, data: Dict) -> str:
    """Create new analysis"""
    with get_db() as conn:
        analysis_id = f"ANA-{datetime.now().strftime('%Y%m%d%H%M%S')}-{secrets.token_hex(3).upper()}"
        
        conn.execute("""INSERT INTO analyses
            (analysis_id, user_id, patient_id, sample_type, microscope_type, magnification,
             preparation_type, technician1, technician2, parasite_detected, confidence,
             risk_level, is_reliable, all_predictions, image_hash, model_version, is_demo, clinical_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (analysis_id, user_id, data.get('patient_id'), data.get('sample_type'),
             data.get('microscope_type'), data.get('magnification'), data.get('preparation_type'),
             data.get('technician1'), data.get('technician2'), data.get('parasite_detected'),
             data.get('confidence'), data.get('risk_level'), data.get('is_reliable', 0),
             json.dumps(data.get('all_predictions', {})), data.get('image_hash'),
             data.get('model_version', 'v8.0'), data.get('is_demo', 0), data.get('clinical_notes')))
        
        # Update user stats
        conn.execute("""UPDATE users SET total_analyses = total_analyses + 1,
            accurate_analyses = accurate_analyses + ?
            WHERE id = ?""", (1 if data.get('is_reliable') else 0, user_id))
        
        return analysis_id

def db_get_analyses(user_id: Optional[int] = None, limit: int = 500,
                   filters: Optional[Dict] = None) -> List[Dict]:
    """Get analyses with filters"""
    with get_db() as conn:
        query = """SELECT a.*, u.full_name as analyst, p.first_name, p.last_name
                   FROM analyses a
                   LEFT JOIN users u ON a.user_id = u.id
                   LEFT JOIN patients p ON a.patient_id = p.id"""
        
        conditions = []
        params = []
        
        if user_id:
            conditions.append("a.user_id = ?")
            params.append(user_id)
        
        if filters:
            if filters.get('parasite'):
                conditions.append("a.parasite_detected = ?")
                params.append(filters['parasite'])
            if filters.get('date_from'):
                conditions.append("a.analysis_date >= ?")
                params.append(filters['date_from'])
            if filters.get('date_to'):
                conditions.append("a.analysis_date <= ?")
                params.append(filters['date_to'])
            if filters.get('status'):
                conditions.append("a.status = ?")
                params.append(filters['status'])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY a.analysis_date DESC LIMIT ?"
        params.append(limit)
        
        analyses = conn.execute(query, params).fetchall()
        return [dict(a) for a in analyses]

def db_get_statistics(user_id: Optional[int] = None) -> Dict:
    """Get statistics"""
    with get_db() as conn:
        where = "WHERE user_id = ?" if user_id else ""
        params = (user_id,) if user_id else ()
        
        total = conn.execute(f"SELECT COUNT(*) FROM analyses {where}", params).fetchone()[0]
        reliable = conn.execute(f"SELECT COUNT(*) FROM analyses {where} AND is_reliable = 1", params).fetchone()[0]
        
        top_row = conn.execute(f"""SELECT parasite_detected, COUNT(*) as cnt
            FROM analyses {where} GROUP BY parasite_detected
            ORDER BY cnt DESC LIMIT 1""", params).fetchone()
        top_parasite = top_row['parasite_detected'] if top_row else 'N/A'
        
        avg_conf = conn.execute(f"SELECT AVG(confidence) FROM analyses {where}", params).fetchone()[0] or 0
        
        parasites = conn.execute(f"""SELECT parasite_detected, COUNT(*) as count
            FROM analyses {where} GROUP BY parasite_detected""", params).fetchall()
        
        return {
            'total': total,
            'reliable': reliable,
            'to_verify': total - reliable,
            'top_parasite': top_parasite,
            'avg_confidence': round(avg_conf, 1),
            'parasite_distribution': [dict(p) for p in parasites]
        }

def db_get_trends(days: int = 30) -> List[Dict]:
    """Get analysis trends"""
    with get_db() as conn:
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        trends = conn.execute("""SELECT DATE(analysis_date) as date,
            parasite_detected, COUNT(*) as count, AVG(confidence) as avg_conf
            FROM analyses WHERE analysis_date >= ?
            GROUP BY DATE(analysis_date), parasite_detected
            ORDER BY date""", (cutoff,)).fetchall()
        return [dict(t) for t in trends]

def db_validate_analysis(analysis_id: int, validator: str, notes: str = ""):
    """Validate analysis"""
    with get_db() as conn:
        conn.execute("""UPDATE analyses SET validated = 1, validated_by = ?,
            validation_date = ?, validation_notes = ?, status = 'validated'
            WHERE id = ?""",
            (validator, datetime.now().isoformat(), notes, analysis_id))

def db_create_notification(user_id: int, type: str, title: str, message: str,
                          action_url: str = None, priority: int = 1):
    """Create notification"""
    with get_db() as conn:
        conn.execute("""INSERT INTO notifications
            (user_id, type, title, message, action_url, priority)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, type, title, message, action_url, priority))

def db_get_notifications(user_id: int, unread_only: bool = False) -> List[Dict]:
    """Get user notifications"""
    with get_db() as conn:
        where = "WHERE user_id = ?"
        if unread_only:
            where += " AND is_read = 0"
        notifs = conn.execute(f"""SELECT * FROM notifications {where}
            ORDER BY created_at DESC LIMIT 50""", (user_id,)).fetchall()
        return [dict(n) for n in notifs]

def db_mark_notification_read(notif_id: int):
    """Mark notification as read"""
    with get_db() as conn:
        conn.execute("UPDATE notifications SET is_read = 1, read_at = ? WHERE id = ?",
                    (datetime.now().isoformat(), notif_id))

def db_get_unread_count(user_id: int) -> int:
    """Get unread notifications count"""
    with get_db() as conn:
        return conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0",
            (user_id,)
        ).fetchone()[0]

def db_log_activity(user_id: int, username: str, action: str, details: str = "",
                   entity_type: str = None, entity_id: int = None):
    """Log user activity"""
    with get_db() as conn:
        conn.execute("""INSERT INTO activity_logs
            (user_id, username, action, entity_type, entity_id, details)
            VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, username, action, entity_type, entity_id, details))

def db_get_activity_logs(limit: int = 300, user_id: Optional[int] = None) -> List[Dict]:
    """Get activity logs"""
    with get_db() as conn:
        where = "WHERE user_id = ?" if user_id else ""
        params = (user_id, limit) if user_id else (limit,)
        logs = conn.execute(f"""SELECT * FROM activity_logs {where}
            ORDER BY timestamp DESC LIMIT ?""", params).fetchall()
        return [dict(log) for log in logs]

def db_save_quiz_score(user_id: int, username: str, score: int, total: int,
                      percentage: float, **kwargs):
    """Save quiz score"""
    with get_db() as conn:
        conn.execute("""INSERT INTO quiz_scores
            (user_id, username, score, total_questions, percentage, category, difficulty, time_taken)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (user_id, username, score, total, percentage,
             kwargs.get('category', 'general'), kwargs.get('difficulty', 'mixed'),
             kwargs.get('time_taken')))
        
        # Update user points
        conn.execute("UPDATE users SET points = points + ? WHERE id = ?",
                    (score * 10, user_id))

def db_get_leaderboard(limit: int = 20) -> List[Dict]:
    """Get quiz leaderboard"""
    with get_db() as conn:
        scores = conn.execute("""SELECT * FROM quiz_scores
            ORDER BY percentage DESC, timestamp ASC LIMIT ?""", (limit,)).fetchall()
        return [dict(s) for s in scores]

# ============================================
#  TRANSLATION SYSTEM
# ============================================
def t(key: str) -> str:
    """Translate key"""
    lang = st.session_state.get("lang", "fr")
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"]).get(key, TRANSLATIONS["fr"].get(key, key))

def tl(d: Any) -> str:
    """Translate dict"""
    if not isinstance(d, dict):
        return str(d)
    lang = st.session_state.get("lang", "fr")
    return d.get(lang, d.get("fr", str(d)))

TRANSLATIONS = {
    "fr": {
        "app_title": "DM Smart Lab AI",
        "login": "Connexion",
        "logout": "Déconnexion",
        "home": "Accueil",
        "scan": "Scan & Analyse",
        "batch": "Analyse par Lots",
        "patients": "Patients",
        "encyclopedia": "Encyclopédie",
        "dashboard": "Tableau de Bord",
        "quiz": "Quiz",
        "chatbot": "DM Bot",
        "compare": "Comparaison",
        "training": "Formation",
        "admin": "Administration",
        "about": "À Propos",
        "username": "Identifiant",
        "password": "Mot de passe",
        "connect": "SE CONNECTER",
        "patient_info": "Informations Patient",
        "lab_info": "Informations Laboratoire",
        "result": "Résultat",
        "confidence": "Confiance",
        "download_pdf": "Télécharger PDF",
        "save": "Sauvegarder",
        "language": "Langue",
        "notifications": "Notifications",
        "settings": "Paramètres",
        "search": "Rechercher",
        "filter": "Filtrer",
        "export": "Exporter",
        "import": "Importer",
    },
    "ar": {
        "app_title": "مختبر DM الذكي",
        "login": "تسجيل الدخول",
        "logout": "تسجيل الخروج",
        "home": "الرئيسية",
        "scan": "مسح وتحليل",
        "batch": "تحليل دفعات",
        "patients": "المرضى",
        "encyclopedia": "الموسوعة",
        "dashboard": "لوحة التحكم",
        "quiz": "اختبار",
        "chatbot": "DM بوت",
        "compare": "مقارنة",
        "training": "تدريب",
        "admin": "الإدارة",
        "about": "حول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "connect": "تسجيل الدخول",
        "patient_info": "معلومات المريض",
        "lab_info": "معلومات المخبر",
        "result": "النتيجة",
        "confidence": "الثقة",
        "download_pdf": "تحميل PDF",
        "save": "حفظ",
        "language": "اللغة",
        "notifications": "الإشعارات",
        "settings": "الإعدادات",
        "search": "بحث",
        "filter": "تصفية",
        "export": "تصدير",
        "import": "استيراد",
    },
    "en": {
        "app_title": "DM Smart Lab AI",
        "login": "Login",
        "logout": "Logout",
        "home": "Home",
        "scan": "Scan & Analysis",
        "batch": "Batch Analysis",
        "patients": "Patients",
        "encyclopedia": "Encyclopedia",
        "dashboard": "Dashboard",
        "quiz": "Quiz",
        "chatbot": "DM Bot",
        "compare": "Comparison",
        "training": "Training",
        "admin": "Administration",
        "about": "About",
        "username": "Username",
        "password": "Password",
        "connect": "CONNECT",
        "patient_info": "Patient Information",
        "lab_info": "Laboratory Information",
        "result": "Result",
        "confidence": "Confidence",
        "download_pdf": "Download PDF",
        "save": "Save",
        "language": "Language",
        "notifications": "Notifications",
        "settings": "Settings",
        "search": "Search",
        "filter": "Filter",
        "export": "Export",
        "import": "Import",
    }
}

# ============================================
#  HELPER FUNCTIONS
# ============================================
def has_permission(permission: str) -> bool:
    """Check if user has permission"""
    role = st.session_state.get("user_role", "viewer")
    permissions = ROLES.get(role, {}).get("permissions", [])
    return "all" in permissions or permission in permissions

def get_role_level() -> int:
    """Get user role level"""
    role = st.session_state.get("user_role", "viewer")
    return ROLES.get(role, {}).get("level", 0)

def risk_color(level: str) -> str:
    """Get risk color"""
    return RISK_COLORS.get(level, "#888")

def get_greeting() -> str:
    """Get time-based greeting"""
    h = datetime.now().hour
    if h < 12:
        return {"fr": "Bonjour", "ar": "صباح الخير", "en": "Good morning"}.get(st.session_state.lang, "Bonjour")
    elif h < 18:
        return {"fr": "Bon après-midi", "ar": "مساء الخير", "en": "Good afternoon"}.get(st.session_state.lang, "Bonjour")
    return {"fr": "Bonsoir", "ar": "مساء الخير", "en": "Good evening"}.get(st.session_state.lang, "Bonsoir")

# Continue in Part 2...
# ============================================
#  IMAGE PROCESSING FUNCTIONS
# ============================================
def process_image(img: Image.Image, brightness: float = 1.0, 
                 contrast: float = 1.0, saturation: float = 1.0) -> Image.Image:
    """Apply image adjustments"""
    result = img.copy()
    if brightness != 1.0:
        result = ImageEnhance.Brightness(result).enhance(brightness)
    if contrast != 1.0:
        result = ImageEnhance.Contrast(result).enhance(contrast)
    if saturation != 1.0:
        result = ImageEnhance.Color(result).enhance(saturation)
    return result

def zoom_image(img: Image.Image, zoom_level: float) -> Image.Image:
    """Zoom into image"""
    if zoom_level <= 1.0:
        return img
    w, h = img.size
    new_w, new_h = int(w / zoom_level), int(h / zoom_level)
    left = (w - new_w) // 2
    top = (h - new_h) // 2
    return img.crop((left, top, left + new_w, top + new_h)).resize((w, h), Image.LANCZOS)

def apply_filter_thermal(img: Image.Image) -> Image.Image:
    """Apply thermal filter"""
    gray = ImageOps.grayscale(ImageEnhance.Contrast(img).enhance(1.5))
    return ImageOps.colorize(gray.filter(ImageFilter.GaussianBlur(1)), 
                            black="navy", white="yellow", mid="red")

def apply_filter_edges(img: Image.Image) -> Image.Image:
    """Apply edge detection filter"""
    return ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)

def apply_filter_enhanced(img: Image.Image) -> Image.Image:
    """Apply enhancement filter"""
    return ImageEnhance.Contrast(
        ImageEnhance.Sharpness(img).enhance(2.0)
    ).enhance(2.0)

def apply_filter_negative(img: Image.Image) -> Image.Image:
    """Apply negative filter"""
    return ImageOps.invert(img.convert("RGB"))

def apply_filter_emboss(img: Image.Image) -> Image.Image:
    """Apply emboss filter"""
    return img.filter(ImageFilter.EMBOSS)

def generate_heatmap(img: Image.Image, seed: Optional[int] = None) -> Image.Image:
    """Generate AI attention heatmap"""
    im = img.copy().convert("RGB")
    w, h = im.size
    
    if seed is None:
        seed = hash(im.tobytes()[:1000]) % 1000000
    
    rng = random.Random(seed)
    
    # Edge detection for focus areas
    edges_array = np.array(ImageOps.grayscale(im).filter(ImageFilter.FIND_EDGES))
    
    # Find hotspot
    block_size = 32
    max_score = 0
    best_x, best_y = w // 2, h // 2
    
    for y in range(0, h - block_size, block_size // 2):
        for x in range(0, w - block_size, block_size // 2):
            score = np.mean(edges_array[y:y+block_size, x:x+block_size])
            if score > max_score:
                max_score = score
                best_x = x + block_size // 2
                best_y = y + block_size // 2
    
    # Add randomness
    best_x = max(50, min(w - 50, best_x + rng.randint(-w // 10, w // 10)))
    best_y = max(50, min(h - 50, best_y + rng.randint(-h // 10, h // 10)))
    
    # Create heatmap overlay
    heatmap = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(heatmap)
    
    max_radius = min(w, h) // 3
    
    for radius in range(max_radius, 0, -2):
        alpha = max(0, min(200, int(200 * (1 - radius / max_radius))))
        ratio = radius / max_radius
        
        if ratio > 0.65:
            color = (0, 255, 100, alpha // 4)
        elif ratio > 0.35:
            color = (255, 255, 0, alpha // 2)
        else:
            color = (255, 0, 60, alpha)
        
        draw.ellipse([best_x - radius, best_y - radius, 
                     best_x + radius, best_y + radius], fill=color)
    
    return Image.alpha_composite(im.convert('RGBA'), heatmap).convert('RGB')

def compare_images(img1: Image.Image, img2: Image.Image) -> Dict:
    """Compare two images"""
    # Resize for comparison
    size = (128, 128)
    a1 = np.array(img1.convert("RGB").resize(size)).astype(float)
    a2 = np.array(img2.convert("RGB").resize(size)).astype(float)
    
    # MSE
    mse = np.mean((a1 - a2) ** 2)
    
    # SSIM calculation
    mean1, mean2 = np.mean(a1), np.mean(a2)
    std1, std2 = np.std(a1), np.std(a2)
    covariance = np.mean((a1 - mean1) * (a2 - mean2))
    
    c1 = (0.01 * 255) ** 2
    c2 = (0.03 * 255) ** 2
    
    ssim = ((2 * mean1 * mean2 + c1) * (2 * covariance + c2)) / \
           ((mean1**2 + mean2**2 + c1) * (std1**2 + std2**2 + c2))
    
    return {
        "mse": round(mse, 2),
        "ssim": round(float(ssim), 4),
        "similarity": round(float(ssim) * 100, 1)
    }

def pixel_difference(img1: Image.Image, img2: Image.Image) -> Image.Image:
    """Calculate pixel-wise difference"""
    size = (256, 256)
    a1 = np.array(img1.convert("RGB").resize(size)).astype(float)
    a2 = np.array(img2.convert("RGB").resize(size)).astype(float)
    
    diff = np.abs(a1 - a2).astype(np.uint8)
    diff = np.clip(diff * 3, 0, 255).astype(np.uint8)
    
    return Image.fromarray(diff)

# ============================================
#  AI ENGINE
# ============================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    """Load AI model"""
    model = None
    model_name = None
    model_type = None
    
    try:
        import tensorflow as tf
        
        # Try to load .keras or .h5 model
        for ext in [".keras", ".h5"]:
            files = [f for f in os.listdir(".") if f.endswith(ext) and os.path.isfile(f)]
            if files:
                model_name = files[0]
                model = tf.keras.models.load_model(model_name, compile=False)
                model_type = "keras"
                break
        
        # Try to load .tflite model
        if model is None:
            files = [f for f in os.listdir(".") if f.endswith(".tflite") and os.path.isfile(f)]
            if files:
                model_name = files[0]
                model = tf.lite.Interpreter(model_path=model_name)
                model.allocate_tensors()
                model_type = "tflite"
    except Exception as e:
        st.sidebar.warning(f"⚠️ Model loading failed: {e}")
    
    return model, model_name, model_type

def predict_parasite(model, model_type: str, img: Image.Image, 
                     seed: Optional[int] = None) -> Dict:
    """Predict parasite from image"""
    result = {
        "label": "Negative",
        "confidence": 0,
        "predictions": {},
        "is_reliable": False,
        "is_demo": False,
        "risk": "none"
    }
    
    risk_map = {
        "Plasmodium": "critical",
        "Amoeba (E. histolytica)": "high",
        "Leishmania": "high",
        "Trypanosoma": "high",
        "Giardia": "medium",
        "Schistosoma": "medium",
        "Negative": "none"
    }
    
    # Demo mode (no model)
    if model is None:
        result["is_demo"] = True
        if seed is None:
            seed = random.randint(0, 999999)
        
        rng = random.Random(seed)
        label = rng.choice(CLASS_NAMES)
        confidence = rng.randint(55, 98)
        
        # Generate predictions
        all_preds = {}
        remaining = 100.0 - confidence
        for cls in CLASS_NAMES:
            if cls == label:
                all_preds[cls] = float(confidence)
            else:
                all_preds[cls] = round(rng.uniform(0, remaining / max(1, len(CLASS_NAMES) - 1)), 1)
        
        result.update({
            "label": label,
            "confidence": confidence,
            "predictions": all_preds,
            "is_reliable": confidence >= CONFIDENCE_THRESHOLD,
            "risk": risk_map.get(label, "none")
        })
        
        return result
    
    # Real AI prediction
    try:
        import tensorflow as tf
        
        # Preprocess image
        img_resized = ImageOps.fit(img.convert("RGB"), MODEL_INPUT_SIZE, Image.LANCZOS)
        img_array = np.expand_dims(np.asarray(img_resized).astype(np.float32) / 127.5 - 1.0, 0)
        
        # Predict
        if model_type == "tflite":
            input_details = model.get_input_details()
            output_details = model.get_output_details()
            model.set_tensor(input_details[0]['index'], img_array)
            model.invoke()
            predictions = model.get_tensor(output_details[0]['index'])[0]
        else:
            predictions = model.predict(img_array, verbose=0)[0]
        
        # Process results
        pred_index = int(np.argmax(predictions))
        confidence = int(predictions[pred_index] * 100)
        label = CLASS_NAMES[pred_index] if pred_index < len(CLASS_NAMES) else "Negative"
        
        all_preds = {
            CLASS_NAMES[i]: round(float(predictions[i]) * 100, 1)
            for i in range(min(len(predictions), len(CLASS_NAMES)))
        }
        
        result.update({
            "label": label,
            "confidence": confidence,
            "predictions": all_preds,
            "is_reliable": confidence >= CONFIDENCE_THRESHOLD,
            "risk": risk_map.get(label, "none")
        })
        
    except Exception as e:
        st.error(f"Prediction error: {e}")
    
    return result

# ============================================
#  PDF GENERATION
# ============================================
def sanitize_text(text: str) -> str:
    """Sanitize text for PDF"""
    if not text:
        return ""
    
    # Replace special characters
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
        'Ô': 'O',
        'Î': 'I',
        'Ç': 'C',
        '→': '->',
        '°': 'o',
        'µ': 'u',
        '×': 'x',
        '±': '+/-',
        '≥': '>=',
        '≤': '<=',
    }
    
    result = str(text)
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    # Remove any remaining non-ASCII
    result = ''.join(c if ord(c) < 128 else '?' for c in result)
    
    return result

class PDFReport(FPDF):
    """Custom PDF class"""
    
    def header(self):
        # Top gradient bar
        self.set_fill_color(0, 20, 60)
        self.rect(0, 0, 210, 4, 'F')
        self.set_fill_color(0, 180, 255)
        self.rect(0, 4, 210, 1, 'F')
        self.ln(8)
        
        # Title
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 60, 150)
        self.cell(0, 8, f"DM SMART LAB AI v{APP_VERSION}", 0, 0, "L")
        self.set_font("Arial", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 0, 1, "R")
        
        # Subtitle
        self.set_font("Arial", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, sanitize_text("Systeme de Diagnostic Parasitologique par IA"), 0, 1, "L")
        self.cell(0, 4, "INFSPM - Ouargla, Algerie", 0, 1, "L")
        
        # Line
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
        self.cell(0, 4, sanitize_text("AVERTISSEMENT: Validation par professionnel de sante requise"), 0, 1, "C")
        self.set_font("Arial", "", 6)
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}} | DM Smart Lab AI | INFSPM Ouargla", 0, 0, "C")

def generate_pdf_report(patient_data: Dict, lab_data: Dict, 
                        result: Dict, parasite_label: str) -> bytes:
    """Generate PDF report"""
    if not HAS_FPDF:
        return b""
    
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(True, 25)
    
    # Report ID
    report_id = hashlib.md5(
        f"{patient_data.get('Nom', '')}{datetime.now().isoformat()}".encode()
    ).hexdigest()[:10].upper()
    
    # Title
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 40, 100)
    pdf.cell(0, 12, sanitize_text("RAPPORT D'ANALYSE PARASITOLOGIQUE"), 0, 1, "C")
    
    # Reference
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Reference: DM-{report_id} | {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "R")
    pdf.ln(3)
    
    # Patient section
    pdf.set_fill_color(0, 60, 150)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "  INFORMATIONS PATIENT", 0, 1, "L", True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    
    for key, value in patient_data.items():
        if value:
            pdf.set_font("Arial", "B", 9)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(55, 6, sanitize_text(f"{key}:"), 0, 0)
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, sanitize_text(str(value)), 0, 1)
    
    pdf.ln(2)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Lab section
    pdf.set_fill_color(0, 100, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "  INFORMATIONS LABORATOIRE", 0, 1, "L", True)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)
    
    for key, value in lab_data.items():
        if value:
            pdf.set_font("Arial", "B", 9)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(55, 6, sanitize_text(f"{key}:"), 0, 0)
            pdf.set_font("Arial", "", 9)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 6, sanitize_text(str(value)), 0, 1)
    
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    
    # Result section
    confidence = result.get("confidence", 0)
    is_negative = parasite_label == "Negative"
    
    if is_negative:
        pdf.set_fill_color(180, 0, 0)
    else:
        pdf.set_fill_color(220, 255, 220)
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "  RESULTAT DE L'ANALYSE IA", 0, 1, "L", True)
    pdf.ln(2)
    
    # Result box
    if is_negative:
        pdf.set_fill_color(220, 255, 220)
        pdf.set_text_color(0, 100, 0)
    else:
        pdf.set_fill_color(255, 220, 220)
        pdf.set_text_color(180, 0, 0)
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 12, sanitize_text(f"  {parasite_label} - Confiance: {confidence}%"), 1, 1, "C", True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)
    
    # Parasite details
    info = PARASITE_DB.get(parasite_label, PARASITE_DB["Negative"])
    
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Nom Scientifique:", 0, 0)
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, f"  {sanitize_text(info.get('sci', 'N/A'))}", 0, 1)
    
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Morphologie:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, sanitize_text(info['morph'].get('fr', '')))
    
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Description:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.multi_cell(0, 5, sanitize_text(info['desc'].get('fr', '')))
    
    pdf.ln(2)
    pdf.set_font("Arial", "B", 9)
    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 6, "Conseil Medical:", 0, 1)
    pdf.set_font("Arial", "", 8)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, sanitize_text(info['advice'].get('fr', '')))
    
    # Tests
    if info.get("tests"):
        pdf.ln(2)
        pdf.set_font("Arial", "B", 9)
        pdf.cell(0, 6, "Examens Complementaires:", 0, 1)
        pdf.set_font("Arial", "", 8)
        for test in info["tests"]:
            pdf.cell(10, 5, "", 0, 0)
            pdf.cell(0, 5, f"- {sanitize_text(test)}", 0, 1)
    
    # QR Code
    if HAS_QRCODE:
        try:
            qr = qrcode.QRCode(box_size=3, border=1)
            qr.add_data(f"DM-{report_id}|{parasite_label}|{confidence}%|{datetime.now().isoformat()}")
            qr.make(fit=True)
            qr_path = f"_qr_{report_id}.png"
            qr.make_image().save(qr_path)
            pdf.image(qr_path, x=170, y=pdf.get_y() - 30, w=28)
            try:
                os.remove(qr_path)
            except:
                pass
        except:
            pass
    
    # Signatures
    pdf.ln(8)
    pdf.set_fill_color(80, 80, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(0, 8, "  SIGNATURES ET VALIDATION", 0, 1, "L", True)
    pdf.ln(5)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "", 9)
    pdf.cell(95, 5, "Technicien 1: ___________________", 0, 0)
    pdf.cell(95, 5, "Technicien 2: ___________________", 0, 1)
    pdf.ln(8)
    pdf.cell(95, 5, "Date: ___/___/______", 0, 0)
    pdf.cell(95, 5, "Cachet du Laboratoire:", 0, 1)
    pdf.ln(10)
    pdf.cell(0, 5, "Validation Biologiste: ___________________", 0, 1)
    
    return bytes(pdf.output())

# ============================================
#  EXCEL EXPORT
# ============================================
def generate_excel_export(data: List[Dict], title: str = "Export") -> bytes:
    """Generate Excel export"""
    if not HAS_EXCEL:
        return b""
    
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df = pd.DataFrame(data)
        df.to_excel(writer, sheet_name='Data', index=False)
        
        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets['Data']
        
        # Style header
        header_fill = PatternFill(start_color='0066FF', end_color='0066FF', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=12)
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output.read()

# ============================================
#  VOICE SYSTEM
# ============================================
def render_voice_player():
    """Render voice player using Web Speech API"""
    if st.session_state.get("voice_text"):
        text = st.session_state.voice_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
        lang_code = {
            "fr": "fr-FR",
            "ar": "ar-SA",
            "en": "en-US"
        }.get(st.session_state.get("voice_lang", st.session_state.lang), "fr-FR")
        
        html_code = f"""
        <div style="display:none;">
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
    """Queue text for speech"""
    st.session_state.voice_text = text
    st.session_state.voice_lang = lang or st.session_state.lang

def stop_speech():
    """Stop speech"""
    st.session_state.voice_text = None
    st.components.v1.html("<script>try{window.speechSynthesis.cancel()}catch(e){}</script>", height=0)

# ============================================
#  CSS STYLING
# ============================================
def apply_custom_css():
    """Apply custom CSS"""
    rtl = st.session_state.lang == "ar"
    direction = "rtl" if rtl else "ltr"
    
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Orbitron:wght@400;600;700;800;900&family=JetBrains+Mono:wght@400;600&family=Tajawal:wght@400;500;700;800&display=swap');
    
    html {{ direction: {direction}; }}
    
    /* Background */
    .stApp {{
        background: #030614 !important;
        color: #e0e8ff !important;
        background-image: 
            radial-gradient(2px 2px at 20px 30px, rgba(0,245,255,0.3), transparent),
            radial-gradient(2px 2px at 60px 70px, rgba(255,0,255,0.2), transparent),
            radial-gradient(1px 1px at 90px 40px, rgba(0,255,136,0.3), transparent);
        background-size: 250px 150px;
        animation: sparkle 8s linear infinite;
    }}
    
    @keyframes sparkle {{
        0% {{ background-position: 0 0; }}
        100% {{ background-position: 250px 150px; }}
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #020410 0%, rgba(5,10,30,0.98) 100%) !important;
        border-right: 1px solid rgba(0,245,255,0.1) !important;
    }}
    
    /* Cards */
    .dm-card {{
        background: rgba(10,15,46,0.85);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0,245,255,0.15);
        border-radius: 20px;
        padding: 24px;
        margin: 12px 0;
        transition: all 0.4s ease;
        color: #e0e8ff !important;
    }}
    
    .dm-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,245,255,0.1);
        border-color: rgba(0,245,255,0.3);
    }}
    
    .dm-card-cyan {{ border-left: 3px solid #00f5ff; }}
    .dm-card-green {{ border-left: 3px solid #00ff88; }}
    .dm-card-red {{ border-left: 3px solid #ff0040; }}
    .dm-card-purple {{ border-left: 3px solid #9933ff; }}
    
    /* Metric Cards */
    .dm-m {{
        background: rgba(10,15,46,0.85);
        border: 1px solid rgba(0,245,255,0.15);
        border-radius: 18px;
        padding: 20px 12px;
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .dm-m:hover {{
        border-color: #00f5ff;
        box-shadow: 0 0 20px rgba(0,245,255,0.1);
    }}
    
    .dm-m-i {{ font-size: 1.6rem; }}
    .dm-m-v {{
        font-size: 1.8rem;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace !important;
        background: linear-gradient(135deg, #00f5ff, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}
    .dm-m-l {{
        font-size: 0.7rem;
        font-weight: 600;
        color: #6b7fa0 !important;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 6px;
    }}
    
    /* Buttons */
    div.stButton > button {{
        background: linear-gradient(135deg, #00f5ff, #0066ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 28px !important;
        font-weight: 700 !important;
        transition: all 0.4s ease !important;
    }}
    
    div.stButton > button:hover {{
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(0,245,255,0.3) !important;
    }}
    
    /* Neon Title */
    .dm-nt {{
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        background: linear-gradient(135deg, #00f5ff, #ff00ff, #00ff88);
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
    
    /* Inputs */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        background: rgba(10,15,46,0.6) !important;
        color: #e0e8ff !important;
        border: 1px solid rgba(0,245,255,0.15) !important;
        border-radius: 12px !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #00f5ff !important;
        box-shadow: 0 0 15px rgba(0,245,255,0.2) !important;
    }}
    
    /* Progress */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, #00f5ff, #ff00ff, #00ff88) !important;
        border-radius: 10px !important;
    }}
    
    /* Scrollbar */
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: #030614; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, #00f5ff, #ff00ff);
        border-radius: 10px;
    }}
    
    /* Text colors */
    .stApp p, .stApp span, .stApp label, .stApp div {{ color: #e0e8ff !important; }}
    .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{ color: #e0e8ff !important; }}
    
    /* RTL Support */
    {"body, p, span, div, label { font-family: 'Tajawal', sans-serif !important; }" if rtl else ""}
    
    /* Badge */
    .dm-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }}
    
    .dm-badge-success {{
        background: rgba(0, 255, 136, 0.2);
        color: #00ff88;
        border: 1px solid rgba(0, 255, 136, 0.3);
    }}
    
    .dm-badge-warning {{
        background: rgba(255, 149, 0, 0.2);
        color: #ff9500;
        border: 1px solid rgba(255, 149, 0, 0.3);
    }}
    
    .dm-badge-danger {{
        background: rgba(255, 0, 64, 0.2);
        color: #ff0040;
        border: 1px solid rgba(255, 0, 64, 0.3);
    }}
    
    /* Logo */
    .dm-logo {{
        text-align: center;
        padding: 16px;
        background: linear-gradient(135deg, rgba(0,245,255,0.05), rgba(255,0,255,0.05));
        border-radius: 24px;
        border: 1px solid rgba(0,245,255,0.15);
        margin-bottom: 12px;
    }}
    
    /* Notification badge */
    .notif-badge {{
        background: #ff0040;
        color: white;
        border-radius: 10px;
        padding: 2px 6px;
        font-size: 0.7rem;
        font-weight: 700;
        margin-left: 6px;
    }}
    
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

# ============================================
#  ANIMATED LOGO
# ============================================
def render_logo():
    """Render animated logo"""
    st.markdown("""
    <div class="dm-logo">
        <svg width="75" height="75" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#00f5ff">
                        <animate attributeName="stop-color" values="#00f5ff;#ff00ff;#00ff88;#00f5ff" dur="4s" repeatCount="indefinite"/>
                    </stop>
                    <stop offset="50%" style="stop-color:#ff00ff">
                        <animate attributeName="stop-color" values="#ff00ff;#00ff88;#00f5ff;#ff00ff" dur="4s" repeatCount="indefinite"/>
                    </stop>
                    <stop offset="100%" style="stop-color:#00ff88">
                        <animate attributeName="stop-color" values="#00ff88;#00f5ff;#ff00ff;#00ff88" dur="4s" repeatCount="indefinite"/>
                    </stop>
                </linearGradient>
            </defs>
            <circle cx="50" cy="50" r="45" fill="none" stroke="url(#g1)" stroke-width="2.5" opacity=".8">
                <animateTransform attributeName="transform" type="rotate" values="0 50 50;360 50 50" dur="20s" repeatCount="indefinite"/>
            </circle>
            <circle cx="50" cy="50" r="38" fill="none" stroke="url(#g1)" stroke-width="1" opacity=".3">
                <animateTransform attributeName="transform" type="rotate" values="360 50 50;0 50 50" dur="15s" repeatCount="indefinite"/>
            </circle>
            <text x="50" y="42" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="14" font-weight="900" fill="url(#g1)">DM</text>
            <text x="50" y="58" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="8" font-weight="600" fill="url(#g1)">SMART LAB</text>
            <text x="50" y="68" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="7" font-weight="400" fill="#00f5ff" opacity=".6">AI</text>
        </svg>
        <h3 style="font-family:Orbitron,sans-serif;margin:6px 0;background:linear-gradient(135deg,#00f5ff,#ff00ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.1rem;">DM SMART LAB AI</h3>
        <p style="font-size:.55rem;opacity:.35;letter-spacing:.35em;text-transform:uppercase;margin:0;">v8.0 Ultimate Edition</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
#  MAIN APPLICATION
# ============================================
def main():
    """Main application"""
    
    # Apply CSS
    apply_custom_css()
    
    # Render voice player
    render_voice_player()
    
    # Sidebar logo
    with st.sidebar:
        render_logo()
    
    # ============================================
    #  LOGIN PAGE
    # ============================================
    if not st.session_state.logged_in:
        lc1, lc2, lc3 = st.columns([1, 2, 1])
        with lc2:
            # Language selector
            lang_options = ["FR Français", "AR العربية", "EN English"]
            current_index = ["fr", "ar", "en"].index(st.session_state.lang)
            lang_choice = st.selectbox("Language", lang_options, index=current_index, label_visibility="collapsed")
            st.session_state.lang = {"FR Français": "fr", "AR العربية": "ar", "EN English": "en"}[lang_choice]
            
            # Logo
            render_logo()
            
            # Login card
            st.markdown(f"""
            <div class='dm-card dm-card-cyan' style='text-align:center;'>
                <div style='font-size:3.5rem;margin-bottom:10px;'>
                    <span style='animation: pulse 2s ease-in-out infinite;display:inline-block;'>🔐</span>
                </div>
                <h2 class='dm-nt'>{t('login')}</h2>
                <p style='opacity:.4;font-size:.85rem;'>Professional Authentication System</p>
            </div>
            <style>
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
            }}
            </style>
            """, unsafe_allow_html=True)
            
            with st.form("login_form"):
                username = st.text_input(t("username"), placeholder="admin / dhia / demo")
                password = st.text_input(t("password"), type="password")
                submit = st.form_submit_button(t("connect"), use_container_width=True)
                
                if submit:
                    if username.strip():
                        result = db_login(username.strip(), password)
                        
                        if result is None:
                            st.error("❌ User not found")
                        elif isinstance(result, dict) and "error" in result:
                            if result["error"] == "locked":
                                st.error(f"🔒 Account locked. Try again later.")
                            else:
                                st.error(f"❌ Wrong password. {result.get('attempts_left', 0)} attempts left")
                        else:
                            # Success
                            st.session_state.logged_in = True
                            st.session_state.user_id = result["id"]
                            st.session_state.user_name = result["username"]
                            st.session_state.user_role = result["role"]
                            st.session_state.user_full_name = result["full_name"]
                            st.session_state.user_email = result.get("email", "")
                            st.session_state.lang = result.get("language", "fr")
                            
                            db_log_activity(result["id"], result["username"], "Login")
                            st.rerun()
            
            st.markdown("""
            <div style='text-align:center;opacity:.3;font-size:.72rem;margin-top:16px;'>
                admin/admin2026 | dhia/dhia2026 | demo/demo123
            </div>
            """, unsafe_allow_html=True)
        
        st.stop()
    
    # ============================================
    #  SIDEBAR NAVIGATION
    # ============================================
    with st.sidebar:
        # User info
        role_info = ROLES.get(st.session_state.user_role, ROLES["viewer"])
        st.markdown(f"### {role_info['icon']} {st.session_state.user_full_name}")
        st.caption(f"@{st.session_state.user_name} | {tl(role_info['label'])}")
        
        # Daily tip
        tips = DAILY_TIPS.get(st.session_state.lang, DAILY_TIPS["fr"])
        tip_index = datetime.now().timetuple().tm_yday % len(tips)
        st.info(f"**💡 {t('daily_tip')}:**\n\n{tips[tip_index]}")
        
        st.markdown("---")
        
        # Language selector
        st.markdown(f"#### {t('language')}")
        lang_options = ["FR Français", "AR العربية", "EN English"]
        current_index = ["fr", "ar", "en"].index(st.session_state.lang)
        lang_choice = st.radio("lang_radio", lang_options, index=current_index, label_visibility="collapsed")
        new_lang = {"FR Français": "fr", "AR العربية": "ar", "EN English": "en"}[lang_choice]
        
        if new_lang != st.session_state.lang:
            st.session_state.lang = new_lang
            st.rerun()
        
        st.markdown("---")
        
        # Navigation menu
        menu_items = [
            f"🏠 {t('home')}",
            f"🔬 {t('scan')}",
            f"📦 {t('batch')}",
            f"👥 {t('patients')}",
            f"📘 {t('encyclopedia')}",
            f"📊 {t('dashboard')}",
            f"🧠 {t('quiz')}",
            f"💬 {t('chatbot')}",
            f"🔄 {t('compare')}",
            f"🎓 {t('training')}",
        ]
        
        menu_keys = ["home", "scan", "batch", "patients", "enc", "dash", "quiz", "chat", "cmp", "training"]
        
        if get_role_level() >= 5:
            menu_items.append(f"⚙️ {t('admin')}")
            menu_keys.append("admin")
        
        menu_items.append(f"ℹ️ {t('about')}")
        menu_keys.append("about")
        
        selected_menu = st.radio("Navigation", menu_items, label_visibility="collapsed")
        page = dict(zip(menu_items, menu_keys)).get(selected_menu, "home")
        
        st.markdown("---")
        
        # Logout button
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            db_log_activity(st.session_state.user_id, st.session_state.user_name, "Logout")
            for key in DEFAULTS:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()
    
    # ============================================
    #  PAGE ROUTING
    # ============================================
    
    if page == "home":
        render_home_page()
    elif page == "scan":
        render_scan_page()
    elif page == "batch":
        render_batch_page()
    elif page == "patients":
        render_patients_page()
    elif page == "enc":
        render_encyclopedia_page()
    elif page == "dash":
        render_dashboard_page()
    elif page == "quiz":
        render_quiz_page()
    elif page == "chat":
        render_chatbot_page()
    elif page == "cmp":
        render_compare_page()
    elif page == "training":
        render_training_page()
    elif page == "admin":
        render_admin_page()
    elif page == "about":
        render_about_page()

# ============================================
#  PAGE RENDERERS
# ============================================

def render_home_page():
    """Render home page"""
    st.markdown(f"""
    <h1 class='dm-nt'>
        👋 {get_greeting()}, {st.session_state.user_full_name}!
    </h1>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='dm-card dm-card-cyan'>
        <h2 class='dm-nt'>DM SMART LAB AI v{APP_VERSION}</h2>
        <h4 style='opacity:.6;'>Where Science Meets Intelligence</h4>
        <p style='opacity:.4;font-size:.85rem;'>Advanced Parasitological Diagnosis System</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick stats
    stats = db_get_statistics(st.session_state.user_id)
    
    st.markdown("### 📊 Quick Overview")
    cols = st.columns(4)
    metrics = [
        ("🔬", stats["total"], "Total Analyses"),
        ("✅", stats["reliable"], "Reliable"),
        ("⚠️", stats["to_verify"], "To Verify"),
        ("🦠", stats["top_parasite"], "Most Frequent")
    ]
    
    for col, (icon, value, label) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class='dm-m'>
                <span class='dm-m-i'>{icon}</span>
                <div class='dm-m-v'>{value}</div>
                <div class='dm-m-l'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    ac1, ac2, ac3, ac4 = st.columns(4)
    
    with ac1:
        if st.button("🔬 New Analysis", use_container_width=True, type="primary"):
            st.session_state._nav_override = "scan"
            st.rerun()
    
    with ac2:
        if st.button("📦 Batch Analysis", use_container_width=True):
            st.session_state._nav_override = "batch"
            st.rerun()
    
    with ac3:
        if st.button("👥 Manage Patients", use_container_width=True):
            st.session_state._nav_override = "patients"
            st.rerun()
    
    with ac4:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.session_state._nav_override = "dash"
            st.rerun()

def render_scan_page():
    """Render scan & analysis page"""
    st.title("🔬 Scan & Analysis")
    
    # Load AI model
    model, model_name, model_type = load_ai_model()
    
    if model_name:
        st.sidebar.success(f"🧠 Model: {model_name}")
    else:
        st.sidebar.info("🧠 Demo Mode (No AI model loaded)")
    
    # Patient info
    st.markdown("### 📋 1. Patient Information")
    
    with st.expander("Patient Details", expanded=True):
        pc1, pc2 = st.columns(2)
        patient_name = pc1.text_input("Patient Name *")
        patient_firstname = pc2.text_input("First Name")
        
        pc3, pc4, pc5, pc6 = st.columns(4)
        patient_age = pc3.number_input("Age", 0, 120, 30)
        patient_sex = pc4.selectbox("Sex", ["Male", "Female"])
        patient_weight = pc5.number_input("Weight (kg)", 0, 300, 70)
        sample_type = pc6.selectbox("Sample Type", SAMPLE_TYPES.get(st.session_state.lang, SAMPLE_TYPES["fr"]))
    
    # Lab info
    st.markdown("### 🔬 2. Laboratory Information")
    
    with st.expander("Lab Details", expanded=True):
        lc1, lc2, lc3 = st.columns(3)
        tech1 = lc1.text_input("Technician 1", value=st.session_state.user_full_name)
        tech2 = lc2.text_input("Technician 2")
        microscope = lc3.selectbox("Microscope", MICROSCOPE_TYPES)
        
        lc4, lc5 = st.columns(2)
        magnification = lc4.selectbox("Magnification", MAGNIFICATIONS, index=3)
        preparation = lc5.selectbox("Preparation", PREPARATION_TYPES)
        
        notes = st.text_area("Clinical Notes", height=80)
    
    # Image capture
    st.markdown("### 📸 3. Image Capture")
    
    capture_method = st.radio("Capture Method", 
                              ["📸 Camera", "📁 Upload File"], 
                              horizontal=True, 
                              label_visibility="collapsed")
    
    img = None
    img_hash = None
    
    if "📸" in capture_method:
        st.info("📷 Position microscope eyepiece in front of camera")
        camera_photo = st.camera_input("camera")
        if camera_photo:
            img = Image.open(camera_photo).convert("RGB")
            img_hash = hashlib.md5(camera_photo.getvalue()).hexdigest()
    else:
        upload_file = st.file_uploader("Upload Image", type=ALLOWED_EXTENSIONS)
        if upload_file:
            img = Image.open(upload_file).convert("RGB")
            img_hash = hashlib.md5(upload_file.getvalue()).hexdigest()
    
    if img:
        if not patient_name.strip():
            st.error("❌ Patient name is required!")
            st.stop()
        
        # Generate new seeds if image changed
        if st.session_state.get("_current_hash") != img_hash:
            st.session_state._current_hash = img_hash
            st.session_state.demo_seed = random.randint(0, 999999)
            st.session_state.heatmap_seed = random.randint(0, 999999)
        
        # Image processing and results
        ic1, ic2 = st.columns([1, 1])
        
        with ic1:
            st.markdown("#### 🎛️ Image Processing")
            
            with st.expander("Adjustments", expanded=False):
                zoom = st.slider("Zoom", 1.0, 5.0, 1.0, 0.25)
                brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
                contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
                saturation = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)
            
            processed_img = process_image(img, brightness, contrast, saturation)
            if zoom > 1.0:
                processed_img = zoom_image(processed_img, zoom)
            
            tabs = st.tabs(["Original", "Thermal", "Edges", "Enhanced", "Negative", "Emboss", "Heatmap"])
            
            with tabs[0]:
                st.image(processed_img, use_container_width=True)
            with tabs[1]:
                st.image(apply_filter_thermal(processed_img), use_container_width=True)
            with tabs[2]:
                st.image(apply_filter_edges(processed_img), use_container_width=True)
            with tabs[3]:
                st.image(apply_filter_enhanced(processed_img), use_container_width=True)
            with tabs[4]:
                st.image(apply_filter_negative(processed_img), use_container_width=True)
            with tabs[5]:
                st.image(apply_filter_emboss(processed_img), use_container_width=True)
            with tabs[6]:
                st.image(generate_heatmap(img, st.session_state.heatmap_seed), use_container_width=True)
        
        with ic2:
            st.markdown("#### 🧠 AI Analysis Result")
            
            # Run prediction
            with st.spinner("🔬 Analyzing..."):
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.003)
                    progress_bar.progress(i + 1)
                
                result = predict_parasite(model, model_type, img, st.session_state.demo_seed)
            
            parasite_label = result["label"]
            confidence = result["confidence"]
            risk = result["risk"]
            risk_clr = risk_color(risk)
            
            parasite_info = PARASITE_DB.get(parasite_label, PARASITE_DB["Negative"])
            
            # Warnings
            if not result["is_reliable"]:
                st.warning("⚠️ Low confidence. Manual verification recommended!")
            
            if result["is_demo"]:
                st.info("ℹ️ Demo Mode Active (Simulated Results)")
            
            # Result card
            st.markdown(f"""
            <div class='dm-card' style='border-left:4px solid {risk_clr};'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
                    <div>
                        <h2 style='color:{risk_clr}!important;-webkit-text-fill-color:{risk_clr}!important;margin:0;font-family:Orbitron;'>
                            {parasite_label}
                        </h2>
                        <p style='opacity:.4;font-style:italic;'>{parasite_info['sci']}</p>
                    </div>
                    <div style='text-align:center;'>
                        <div style='font-size:2.8rem;font-weight:900;font-family:JetBrains Mono;color:{risk_clr}!important;-webkit-text-fill-color:{risk_clr}!important;'>
                            {confidence}%
                        </div>
                        <div style='font-size:.7rem;opacity:.4;'>Confidence</div>
                    </div>
                </div>
                <hr style='opacity:.1;margin:14px 0;'>
                <p><b>🔬 Morphology:</b><br>{tl(parasite_info['morph'])}</p>
                <p><b>⚠️ Risk:</b> <span style='color:{risk_clr}!important;-webkit-text-fill-color:{risk_clr}!important;font-weight:700;'>
                    {tl(parasite_info['risk_d'])}
                </span></p>
                <div style='background:rgba(0,255,136,.06);padding:14px;border-radius:12px;margin:10px 0;border:1px solid rgba(0,255,136,.1);'>
                    <b>💡 Medical Advice:</b><br>{tl(parasite_info['advice'])}
                </div>
                <div style='background:rgba(0,100,255,.06);padding:14px;border-radius:12px;font-style:italic;border:1px solid rgba(0,100,255,.1);'>
                    🤖 {tl(parasite_info['funny'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Voice controls
            vc1, vc2 = st.columns(2)
            with vc1:
                if st.button("🔊 Listen", use_container_width=True):
                    speak(f"{parasite_label}. {tl(parasite_info['funny'])}")
                    st.rerun()
            with vc2:
                if st.button("🔇 Stop", key="stop_voice", use_container_width=True):
                    stop_speech()
            
            # Additional info
            if parasite_info.get("tests"):
                with st.expander("🩺 Suggested Tests"):
                    for test in parasite_info["tests"]:
                        st.markdown(f"- {test}")
            
            keys_text = tl(parasite_info.get("keys", {}))
            if keys_text and keys_text not in ["N/A", "غير متوفر"]:
                with st.expander("🔑 Diagnostic Keys"):
                    st.markdown(keys_text)
            
            cycle_text = tl(parasite_info.get("cycle", {}))
            if cycle_text and cycle_text not in ["N/A", "غير متوفر"]:
                with st.expander("🔄 Life Cycle"):
                    st.markdown(f"**{cycle_text}**")
            
            if result["predictions"] and HAS_PLOTLY:
                with st.expander("📊 All Predictions"):
                    sorted_preds = dict(sorted(result["predictions"].items(), 
                                              key=lambda x: x[1], reverse=True))
                    fig = px.bar(x=list(sorted_preds.values()), 
                               y=list(sorted_preds.keys()), 
                               orientation='h',
                               color=list(sorted_preds.values()),
                               color_continuous_scale='RdYlGn_r')
                    fig.update_layout(height=220, template='plotly_dark',
                                    margin=dict(l=20, r=20, t=10, b=20),
                                    showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
        
        # Action buttons
        st.markdown("---")
        st.markdown("### ⚙️ Actions")
        
        ac1, ac2, ac3 = st.columns(3)
        
        with ac1:
            if HAS_FPDF:
                patient_data = {
                    "Nom": patient_name,
                    "Prenom": patient_firstname,
                    "Age": str(patient_age),
                    "Sexe": patient_sex,
                    "Poids": str(patient_weight),
                    "Echantillon": sample_type
                }
                
                lab_data = {
                    "Microscope": microscope,
                    "Grossissement": magnification,
                    "Preparation": preparation,
                    "Technicien 1": tech1,
                    "Technicien 2": tech2,
                    "Notes": notes
                }
                
                pdf_bytes = generate_pdf_report(patient_data, lab_data, result, parasite_label)
                
                st.download_button(
                    "📥 Download PDF Report",
                    pdf_bytes,
                    f"Report_{patient_name}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    "application/pdf",
                    use_container_width=True
                )
        
        with ac2:
            if has_permission("save"):
                if st.button("💾 Save to Database", use_container_width=True):
                    analysis_id = db_create_analysis(st.session_state.user_id, {
                        "patient_id": None,
                        "sample_type": sample_type,
                        "microscope_type": microscope,
                        "magnification": magnification,
                        "preparation_type": preparation,
                        "technician1": tech1,
                        "technician2": tech2,
                        "parasite_detected": parasite_label,
                        "confidence": confidence,
                        "risk_level": risk,
                        "is_reliable": result["is_reliable"],
                        "all_predictions": result["predictions"],
                        "image_hash": img_hash,
                        "is_demo": result["is_demo"],
                        "clinical_notes": notes
                    })
                    
                    db_log_activity(st.session_state.user_id, st.session_state.user_name, 
                                  "Analysis Created", f"ID: {analysis_id}")
                    
                    st.success(f"✅ Analysis saved! ID: {analysis_id}")
        
        with ac3:
            if st.button("🔄 New Analysis", use_container_width=True):
                st.session_state.demo_seed = None
                st.session_state._current_hash = None
                st.rerun()

def render_batch_page():
    """Render batch analysis page"""
    st.title("📦 Batch Analysis")
    st.info("💡 Upload multiple images for batch processing")
    
    uploaded_files = st.file_uploader(
        "Upload Images (Max 50)",
        type=ALLOWED_EXTENSIONS,
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if len(uploaded_files) > MAX_BATCH_UPLOAD:
            st.error(f"❌ Maximum {MAX_BATCH_UPLOAD} files allowed!")
            st.stop()
        
        st.success(f"✅ {len(uploaded_files)} images uploaded")
        
        # Load model
        model, model_name, model_type = load_ai_model()
        
        if st.button("🚀 Start Batch Analysis", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            results = []
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {i+1}/{len(uploaded_files)}: {file.name}")
                
                img = Image.open(file).convert("RGB")
                result = predict_parasite(model, model_type, img)
                
                results.append({
                    "filename": file.name,
                    "parasite": result["label"],
                    "confidence": result["confidence"],
                    "risk": result["risk"],
                    "reliable": "✅" if result["is_reliable"] else "⚠️"
                })
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.text("✅ Batch analysis complete!")
            
            # Display results
            st.markdown("---")
            st.markdown("### 📊 Results Summary")
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            cols = st.columns(4)
            with cols[0]:
                st.metric("Total", len(results))
            with cols[1]:
                reliable_count = len([r for r in results if r["reliable"] == "✅"])
                st.metric("Reliable", reliable_count)
            with cols[2]:
                negative_count = len([r for r in results if r["parasite"] == "Negative"])
                st.metric("Negative", negative_count)
            with cols[3]:
                avg_conf = sum([r["confidence"] for r in results]) / len(results)
                st.metric("Avg Confidence", f"{avg_conf:.1f}%")
            
            # Export
            if HAS_EXCEL:
                excel_bytes = generate_excel_export(results, "Batch Analysis")
                st.download_button(
                    "📊 Export to Excel",
                    excel_bytes,
                    f"Batch_Analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

def render_patients_page():
    """Render patient management page"""
    st.title("👥 Patient Management")
    
    tab1, tab2 = st.tabs(["📋 Patient List", "➕ Add Patient"])
    
    with tab1:
        search_query = st.text_input("🔍 Search patients", placeholder="Name or ID...")
        
        if search_query:
            patients = db_search_patients(search_query)
            
            if patients:
                for patient in patients:
                    with st.expander(f"{patient['patient_id']} - {patient['first_name']} {patient['last_name']}"):
                        pc1, pc2, pc3 = st.columns(3)
                        with pc1:
                            st.write(f"**Age:** {patient.get('age', 'N/A')}")
                            st.write(f"**Sex:** {patient.get('sex', 'N/A')}")
                        with pc2:
                            st.write(f"**Phone:** {patient.get('phone', 'N/A')}")
                            st.write(f"**Email:** {patient.get('email', 'N/A')}")
                        with pc3:
                            st.write(f"**Status:** {patient.get('status', 'active')}")
                            st.write(f"**Last Visit:** {patient.get('last_visit', 'N/A')}")
            else:
                st.info("No patients found")
    
    with tab2:
        with st.form("add_patient_form"):
            st.markdown("### Patient Information")
            
            pc1, pc2 = st.columns(2)
            first_name = pc1.text_input("First Name *")
            last_name = pc2.text_input("Last Name *")
            
            pc3, pc4, pc5 = st.columns(3)
            age = pc3.number_input("Age", 0, 120, 30)
            sex = pc4.selectbox("Sex", ["Male", "Female", "Other"])
            phone = pc5.text_input("Phone")
            
            email = st.text_input("Email")
            address = st.text_area("Address")
            
            submit = st.form_submit_button("➕ Add Patient", use_container_width=True)
            
            if submit:
                if first_name and last_name:
                    patient_id = db_create_patient(
                        first_name, last_name,
                        age=age, sex=sex, phone=phone,
                        email=email, address=address
                    )
                    st.success(f"✅ Patient added! ID: {patient_id}")
                else:
                    st.error("❌ First name and last name are required!")

def render_encyclopedia_page():
    """Render encyclopedia page"""
    st.title("📘 Parasite Encyclopedia")
    
    search = st.text_input("🔍 Search parasites...", placeholder="Amoeba, Giardia, etc.")
    
    st.markdown("---")
    
    found = False
    for parasite_name, parasite_data in PARASITE_DB.items():
        if parasite_name == "Negative":
            continue
        
        if search.strip() and search.lower() not in (parasite_name + " " + parasite_data["sci"]).lower():
            continue
        
        found = True
        risk_clr = risk_color(parasite_data["risk"])
        
        with st.expander(
            f"{parasite_data['icon']} {parasite_name} — *{parasite_data['sci']}* | {tl(parasite_data['risk_d'])}",
            expanded=not search.strip()
        ):
            pc1, pc2 = st.columns([2.5, 1])
            
            with pc1:
                st.markdown(f"""
                <div class='dm-card' style='border-left:3px solid {risk_clr};'>
                    <h4 style='color:{risk_clr}!important;-webkit-text-fill-color:{risk_clr}!important;'>
                        {parasite_data['sci']}
                    </h4>
                    <p><b>🔬 Morphology:</b><br>{tl(parasite_data['morph'])}</p>
                    <p><b>📖 Description:</b><br>{tl(parasite_data['desc'])}</p>
                    <p><b>⚠️ Risk:</b> <span style='color:{risk_clr}!important;-webkit-text-fill-color:{risk_clr}!important;font-weight:700;'>
                        {tl(parasite_data['risk_d'])}
                    </span></p>
                    <div style='background:rgba(0,255,136,.06);padding:12px;border-radius:10px;margin:8px 0;'>
                        <b>💡:</b> {tl(parasite_data['advice'])}
                    </div>
                    <div style='background:rgba(0,100,255,.06);padding:12px;border-radius:10px;font-style:italic;'>
                        🤖 {tl(parasite_data['funny'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                cycle_text = tl(parasite_data.get("cycle", {}))
                if cycle_text and cycle_text not in ["N/A", "غير متوفر"]:
                    st.markdown(f"**🔄 Life Cycle:** {cycle_text}")
                
                keys_text = tl(parasite_data.get("keys", {}))
                if keys_text:
                    st.markdown(f"**🔑 Diagnostic Keys:**\n{keys_text}")
                
                if parasite_data.get("tests"):
                    st.markdown(f"**🩺 Suggested Tests:** {', '.join(parasite_data['tests'])}")
            
            with pc2:
                st.markdown(f'<div style="text-align:center;font-size:4rem;">{parasite_data["icon"]}</div>', 
                          unsafe_allow_html=True)
                
                if st.button(f"🔊 Listen", key=f"listen_{parasite_name}"):
                    speak(f"{parasite_name}. {tl(parasite_data['desc'])}")
                    st.rerun()
    
    if search.strip() and not found:
        st.warning("No parasites found matching your search")

def render_dashboard_page():
    """Render dashboard page"""
    st.title("📊 Dashboard & Analytics")
    
    # Get statistics
    if get_role_level() >= 4:
        stats = db_get_statistics()
        analyses = db_get_analyses(limit=1000)
    else:
        stats = db_get_statistics(st.session_state.user_id)
        analyses = db_get_analyses(st.session_state.user_id, limit=1000)
    
    # Metrics
    metrics = [
        ("🔬", stats["total"], "Total Analyses"),
        ("✅", stats["reliable"], "Reliable"),
        ("⚠️", stats["to_verify"], "To Verify"),
        ("🦠", stats["top_parasite"], "Most Frequent"),
        ("📈", f"{stats['avg_confidence']}%", "Avg Confidence")
    ]
    
    cols = st.columns(5)
    for col, (icon, value, label) in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class='dm-m'>
                <span class='dm-m-i'>{icon}</span>
                <div class='dm-m-v'>{value}</div>
                <div class='dm-m-l'>{label}</div>
            </div>
            """, unsafe_allow_html=True)
    
    if stats["total"] > 0 and analyses and HAS_PLOTLY:
        df = pd.DataFrame(analyses)
        
        st.markdown("---")
        
        # Charts
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("#### Parasite Distribution")
            if "parasite_detected" in df.columns:
                counts = df["parasite_detected"].value_counts()
                fig = px.pie(values=counts.values, names=counts.index, hole=0.4)
                fig.update_layout(height=350, template='plotly_dark', 
                                margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.markdown("#### Confidence Levels")
            if "confidence" in df.columns:
                fig = px.histogram(df, x="confidence", nbins=20, 
                                 color_discrete_sequence=["#00f5ff"])
                fig.update_layout(height=350, template='plotly_dark',
                                margin=dict(l=20, r=20, t=20, b=20))
                st.plotly_chart(fig, use_container_width=True)
        
        # Trends
        trends = db_get_trends(30)
        if trends:
            st.markdown("#### 30-Day Trends")
            trend_df = pd.DataFrame(trends)
            fig = px.line(trend_df, x="date", y="count", 
                         color="parasite", markers=True)
            fig.update_layout(height=300, template='plotly_dark',
                            margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        
        # History table
        st.markdown("### 📋 Analysis History")
        display_cols = [c for c in ["id", "analysis_date", "patient_id", "parasite_detected", 
                                    "confidence", "risk_level", "validated", "status"] 
                       if c in df.columns]
        st.dataframe(df[display_cols] if display_cols else df, use_container_width=True)
    else:
        st.info("No data available yet. Start analyzing to see statistics!")

def render_quiz_page():
    """Render quiz page"""
    st.title("🧠 Medical Quiz")
    
    # Note: Quiz questions would need to be defined
    # This is a placeholder implementation
    
    st.info("💡 Quiz feature - Test your parasitology knowledge!")
    st.markdown("Coming soon in the next update...")

def render_chatbot_page():
    """Render chatbot page"""
    st.title("💬 DM Bot - Medical Assistant")
    
    st.info("💡 Ask me anything about parasites, techniques, or treatments!")
    st.markdown("Chat functionality - Coming soon...")

def render_compare_page():
    """Render image comparison page"""
    st.title("🔄 Image Comparison")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("### 📷 Image 1")
        file1 = st.file_uploader("Upload first image", type=ALLOWED_EXTENSIONS, key="cmp1")
    
    with c2:
        st.markdown("### 📷 Image 2")
        file2 = st.file_uploader("Upload second image", type=ALLOWED_EXTENSIONS, key="cmp2")
    
    if file1 and file2:
        img1 = Image.open(file1).convert("RGB")
        img2 = Image.open(file2).convert("RGB")
        
        c1, c2 = st.columns(2)
        with c1:
            st.image(img1, caption="Image 1", use_container_width=True)
        with c2:
            st.image(img2, caption="Image 2", use_container_width=True)
        
        if st.button("🔍 Compare Images", type="primary"):
            metrics = compare_images(img1, img2)
            
            st.markdown("---")
            st.markdown("### 📊 Comparison Results")
            
            mc = st.columns(3)
            with mc[0]:
                st.metric("Similarity", f"{metrics['similarity']}%")
            with mc[1]:
                st.metric("SSIM", f"{metrics['ssim']}")
            with mc[2]:
                st.metric("MSE", f"{metrics['mse']}")
            
            # Pixel difference
            st.markdown("### 🔍 Pixel Difference")
            diff_img = pixel_difference(img1, img2)
            st.image(diff_img, caption="Difference", use_container_width=True)

def render_training_page():
    """Render training mode page"""
    st.title("🎓 Training Mode")
    
    st.info("💡 Practice identifying parasites with real microscope images")
    st.markdown("Training module - Coming soon...")

def render_admin_page():
    """Render admin page"""
    if get_role_level() < 5:
        st.error("🔒 Admin access required")
        st.stop()
    
    st.title("⚙️ Administration")
    
    tab1, tab2, tab3 = st.tabs(["👥 Users", "📜 Activity Log", "🖥️ System"])
    
    with tab1:
        users = db_get_users()
        if users:
            st.dataframe(pd.DataFrame(users), use_container_width=True)
            
            st.markdown("---")
            st.markdown("### User Management")
            
            uc1, uc2, uc3 = st.columns(3)
            user_id = uc1.number_input("User ID", min_value=1, step=1)
            status = uc2.selectbox("Status", ["Active", "Disabled"])
            
            if uc3.button("Apply", use_container_width=True):
                db_toggle_user(user_id, status == "Active")
                st.success(f"User #{user_id} updated!")
                st.rerun()
    
    with tab2:
        logs = db_get_activity_logs(500)
        if logs:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
    
    with tab3:
        sc1, sc2 = st.columns(2)
        
        with sc1:
            st.markdown(f"""
            <div class='dm-card dm-card-green'>
                <h4>🟢 System Status</h4>
                <p><b>Version:</b> {APP_VERSION}</p>
                <p><b>Database:</b> SQLite</p>
                <p><b>Bcrypt:</b> {'✅' if HAS_BCRYPT else '❌'}</p>
                <p><b>Plotly:</b> {'✅' if HAS_PLOTLY else '❌'}</p>
                <p><b>FPDF:</b> {'✅' if HAS_FPDF else '❌'}</p>
                <p><b>Excel:</b> {'✅' if HAS_EXCEL else '❌'}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with sc2:
            stats = db_get_statistics()
            st.markdown(f"""
            <div class='dm-card dm-card-cyan'>
                <h4>📊 Database Stats</h4>
                <p><b>Users:</b> {len(db_get_users())}</p>
                <p><b>Analyses:</b> {stats['total']}</p>
                <p><b>Reliable:</b> {stats['reliable']}</p>
                <p><b>Languages:</b> FR / AR / EN</p>
            </div>
            """, unsafe_allow_html=True)

def render_about_page():
    """Render about page"""
    st.title("ℹ️ About DM Smart Lab AI")
    
    st.markdown(f"""
    <div class='dm-card dm-card-cyan' style='text-align:center;'>
        <h1 class='dm-nt'>🧬 DM SMART LAB AI</h1>
        <p style='font-size:1.1rem;font-family:Orbitron,sans-serif;'><b>v{APP_VERSION} — Ultimate Edition</b></p>
        <p style='opacity:.4;'>Advanced Parasitological Diagnosis System with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("""
        <div class='dm-card dm-card-cyan'>
            <h3>👨‍🔬 Development Team</h3><br>
            <p><b>🧑‍💻 Sebbag Mohamed Dhia Eddine</b><br>
            <span style='opacity:.5;'>AI & System Architecture Expert</span></p><br>
            <p><b>🔬 Ben Sghir Mohamed</b><br>
            <span style='opacity:.5;'>Laboratory & Data Science Expert</span></p><br>
            <p><b>Level:</b> 3rd Year</p>
            <p><b>Specialty:</b> Public Health Laboratory</p>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown("""
        <div class='dm-card'>
            <h3>🏫 Institution</h3><br>
            <p><b>INFSPM</b></p>
            <p>Institut National de Formation Supérieure Paramédicale</p>
            <p>📍 Ouargla, Algeria 🇩🇿</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 🛠️ Technologies Used")
    
    tech_cols = st.columns(8)
    techs = [
        ("🐍", "Python"), ("🧠", "TensorFlow"), ("🎨", "Streamlit"), ("📊", "Plotly"),
        ("🗄️", "SQLite"), ("🔒", "Bcrypt"), ("📄", "FPDF"), ("📱", "QR")
    ]
    
    for col, (icon, name) in zip(tech_cols, techs):
        with col:
            st.markdown(f"""
            <div class='dm-m'>
                <span class='dm-m-i'>{icon}</span>
                <div class='dm-m-v' style='font-size:.85rem;'>{name}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption(f"Made with ❤️ in Ouargla — 2026 🇩🇿 | © DM Smart Lab AI v{APP_VERSION}")

# ============================================
#  RUN APPLICATION
# ============================================
if __name__ == "__main__":
    main()
