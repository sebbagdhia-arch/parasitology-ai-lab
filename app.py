# ╔══════════════════════════════════════════════════════════════════════════════════╗
# ║                  DM SMART LAB AI v8.0 - ULTIMATE ENHANCED EDITION              ║
# ║            Diagnostic Parasitologique par Intelligence Artificielle              ║
# ║                                                                                ║
# ║  Développé par:                                                                ║
# ║    • Sebbag Mohamed Dhia Eddine (Expert IA & Conception)                       ║
# ║    • Ben Sghir Mohamed (Expert Laboratoire & Données)                          ║
# ║                                                                                ║
# ║  INFSPM - Ouargla, Algérie 🇩🇿                                                ║
# ║  Version 8.0 - Full Enhanced Edition with All Fixes                            ║
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
import warnings
warnings.filterwarnings('ignore')

# ============================================
#  ENVIRONMENT & SECURITY
# ============================================
# ✅ FIX: استخدام environment variables بدلاً من hardcoded secrets
try:
    from dotenv import load_dotenv
    load_dotenv()
    SECRET_KEY = os.getenv("SECRET_KEY", "dm_smart_lab_2026_ultra_secret_CHANGE_ME")
    HAS_DOTENV = True
except ImportError:
    SECRET_KEY = "dm_smart_lab_2026_ultra_secret"
    HAS_DOTENV = False

# Optional imports with fallbacks
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    st.sidebar.warning("⚠️ bcrypt not installed - using SHA256")

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False
    st.sidebar.warning("⚠️ plotly not installed - charts disabled")

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False

try:
    import streamlit.components.v1 as components
    HAS_COMPONENTS = True
except ImportError:
    HAS_COMPONENTS = False

# ============================================
#  PAGE CONFIG - MUST BE FIRST
# ============================================
st.set_page_config(
    page_title="DM Smart Lab AI v8.0",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo',
        'Report a bug': 'mailto:support@dmsmartlab.dz',
        'About': """
        **DM Smart Lab AI v8.0**
        
        Système de diagnostic parasitologique par IA
        
        Développé par Sebbag M.D.E & Ben Sghir M.
        INFSPM Ouargla, Algérie 🇩🇿
        """
    }
)

# ============================================
#  CONSTANTS
# ============================================
APP_VERSION = "8.0.0"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 10
CONFIDENCE_THRESHOLD = 60
MODEL_INPUT_SIZE = (224, 224)
MAX_IMAGE_SIZE = (1920, 1920)  # ✅ NEW: limite taille images
MAX_FILE_SIZE_MB = 10  # ✅ NEW: limite taille fichiers

ROLES = {
    "admin": {"level": 3, "icon": "👑",
              "label": {"fr": "Administrateur", "ar": "مدير النظام", "en": "Administrator"}},
    "technician": {"level": 2, "icon": "🔬",
                   "label": {"fr": "Technicien", "ar": "تقني مخبر", "en": "Technician"}},
    "viewer": {"level": 1, "icon": "👁️",
               "label": {"fr": "Observateur", "ar": "مراقب", "en": "Viewer"}}
}

AUTHORS = {
    "dev1": {
        "name": "Sebbag Mohamed Dhia Eddine",
        "role": {"fr": "Expert IA & Conception", "ar": "خبير ذكاء اصطناعي و تصميم", "en": "AI & Design Expert"},
        "email": "sebbag.dhia@infspm.dz"
    },
    "dev2": {
        "name": "Ben Sghir Mohamed",
        "role": {"fr": "Expert Laboratoire & Données", "ar": "خبير مخبر و بيانات", "en": "Laboratory & Data Expert"},
        "email": "bensghir.mohamed@infspm.dz"
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
    "website": "https://infspm-ouargla.dz"
}

PROJECT_TITLE = {
    "fr": "Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais",
    "ar": "استكشاف إمكانيات الذكاء الاصطناعي للقراءة الآلية للفحص الطفيلي المباشر",
    "en": "Exploring AI potential for automatic reading of fresh parasitological examination"
}

NEON = {
    "cyan": "#00f5ff", "magenta": "#ff00ff", "green": "#00ff88",
    "orange": "#ff6600", "red": "#ff0040", "blue": "#0066ff",
    "purple": "#9933ff", "yellow": "#ffff00", "pink": "#ff69b4",
    "gold": "#ffd700", "lime": "#00ff00"
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
    "fr": ["Selles", "Sang (Frottis)", "Sang (Goutte épaisse)", "Urines", "LCR",
           "Biopsie Cutanée", "Crachat", "Expectoration", "Autre"],
    "ar": ["براز", "دم (لطاخة)", "دم (قطرة سميكة)", "بول", "سائل دماغي شوكي",
           "خزعة جلدية", "بلغم", "بصاق", "أخرى"],
    "en": ["Stool", "Blood (Smear)", "Blood (Thick drop)", "Urine", "CSF",
           "Skin Biopsy", "Sputum", "Expectoration", "Other"]
}

# ============================================
#  PARASITE DATABASE - ENHANCED
# ============================================
PARASITE_DB = {
    "Amoeba (E. histolytica)": {
        "sci": "Entamoeba histolytica",
        "morph": {
            "fr": "Kyste sphérique (10-15µm) à 4 noyaux périphériques, corps chromatoïde en cigare. Trophozoïte (20-40µm) avec pseudopodes digitiformes et hématies phagocytées.",
            "ar": "كيس كروي (10-15 ميكرومتر) بـ 4 أنوية محيطية، جسم كروماتيني على شكل سيجار. الطور النشط (20-40 ميكرومتر) مع أقدام كاذبة وكريات حمراء مبتلعة.",
            "en": "Spherical cyst (10-15µm) with 4 peripheral nuclei, cigar-shaped chromatoid body. Trophozoite (20-40µm) with finger-like pseudopods and phagocytosed RBCs."
        },
        "desc": {
            "fr": "Protozoaire responsable de l'amibiase intestinale (dysenterie amibienne) et extra-intestinale (abcès hépatique, pulmonaire). Transmission féco-orale. Zone endémique: climat chaud.",
            "ar": "طفيلي أولي مسؤول عن الأميبيا المعوية (زحار أميبي) والخارج معوية (خراج كبدي، رئوي). الانتقال عبر الفم-البراز. منطقة موبوءة: مناخ حار.",
            "en": "Protozoan causing intestinal amebiasis (amebic dysentery) and extra-intestinal (hepatic, pulmonary abscess). Fecal-oral transmission. Endemic: hot climate."
        },
        "funny": {
            "fr": "Le ninja des intestins ! Il mange des globules rouges au petit-déjeuner et construit des abcès pour son château fort ! 🏰🔴",
            "ar": "نينجا الأمعاء! يأكل كريات الدم الحمراء في الفطور ويبني خراجات لقلعته! 🏰🔴",
            "en": "The intestinal ninja! Eats red blood cells for breakfast and builds abscesses for his fortress! 🏰🔴"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "Métronidazole 500mg x3/j (7-10j) + Amœbicide de contact (Intetrix 2cp x2/j 10j). Contrôle EPS J15/J30. Échographie hépatique si signes d'abcès.",
            "ar": "ميترونيدازول 500 ملغ 3 مرات يوميا (7-10 أيام) + أميبيسيد تلامسي. مراقبة بعد 15 و 30 يوم. إيكوغرافيا كبدية إذا علامات خراج.",
            "en": "Metronidazole 500mg x3/d (7-10d) + Contact amoebicide (Intetrix). Follow-up D15/D30. Liver ultrasound if abscess signs."
        },
        "tests": ["Sérologie amibienne (IHA)", "Échographie hépatique", "NFS+CRP", "PCR Entamoeba", "Scanner abdominal si complication"],
        "color": "#ff0040", 
        "icon": "🔴",
        "cycle": {
            "fr": "Kyste ingéré → Excystation duodénale → Trophozoïte → Invasion tissulaire (lamina propria) → Enkystement colique → Émission fécale",
            "ar": "كيس مبتلع ← انفكاس في الاثني عشر ← طور نشط ← غزو أنسجة ← تكيس قولوني ← إخراج براز",
            "en": "Ingested cyst → Duodenal excystation → Trophozoite → Tissue invasion (lamina propria) → Colonic encystation → Fecal emission"
        },
        "keys": {
            "fr": "• E. histolytica vs E. dispar: SEULE histolytica phagocyte les hématies !\n• Kyste 4 noyaux (vs E. coli 8 noyaux)\n• Corps chromatoïdes en CIGARE (pathognomonique)\n• Mobilité directionnelle active\n• Hématophage = PATHOGÈNE",
            "ar": "• E. histolytica مقابل E. dispar: فقط histolytica تبتلع الكريات!\n• كيس 4 أنوية (مقابل 8 لـ E. coli)\n• أجسام كروماتينية سيجارية (مميزة)\n• حركة اتجاهية نشطة\n• آكلة دم = مرضية",
            "en": "• E. histolytica vs E. dispar: ONLY histolytica phagocytoses RBCs!\n• 4 nuclei cyst (vs E. coli 8)\n• CIGAR chromatoid bodies (pathognomonic)\n• Directional active motility\n• Hematophagous = PATHOGENIC"
        },
        "incubation": "2-4 semaines",
        "transmission": "Féco-orale (eau, aliments contaminés)",
        "geography": "Mondial (surtout pays chauds)"
    },
    
    "Giardia": {
        "sci": "Giardia lamblia (intestinalis, duodenalis)",
        "morph": {
            "fr": "Trophozoïte piriforme en cerf-volant (12-15µm), 2 noyaux antérieurs (face de hibou), disque adhésif ventral, 4 paires de flagelles. Kyste ovoïde (8-12µm) à 4 noyaux.",
            "ar": "الطور النشط كمثري شكل طائرة ورقية (12-15 ميكرومتر)، نواتان أماميتان (وجه البومة)، قرص لاصق بطني، 4 أزواج أسواط. كيس بيضاوي (8-12 ميكرومتر) بـ 4 أنوية.",
            "en": "Pear-shaped kite trophozoite (12-15µm), 2 anterior nuclei (owl face), ventral adhesive disk, 4 flagella pairs. Ovoid cyst (8-12µm) with 4 nuclei."
        },
        "desc": {
            "fr": "Flagellé du duodénum et jéjunum proximal. Diarrhée graisseuse chronique, malabsorption (lactose, lipides, vitamines A/B12). Transmission hydrique (eau de source, piscines). Zoonose (castor).",
            "ar": "سوطي الاثني عشر والصائم القريب. إسهال دهني مزمن، سوء امتصاص (لاكتوز، دهون، فيتامينات A/B12). انتقال عبر الماء (ينابيع، مسابح). حيواني المنشأ (قندس).",
            "en": "Duodenal and proximal jejunum flagellate. Chronic greasy diarrhea, malabsorption (lactose, lipids, vitamins A/B12). Waterborne (springs, pools). Zoonotic (beaver)."
        },
        "funny": {
            "fr": "Il te fixe avec ses lunettes de soleil ! 😎 Un touriste collant qui refuse de partir et squatte ton intestin comme un Airbnb gratuit ! 🏖️",
            "ar": "ينظر إليك بنظارته الشمسية! 😎 سائح لزج يرفض المغادرة ويحتل أمعاءك كأنها فندق مجاني! 🏖️",
            "en": "It stares at you with sunglasses! 😎 A sticky tourist who refuses to leave and squats your intestine like a free Airbnb! 🏖️"
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "advice": {
            "fr": "Métronidazole 250mg x3/j (5-7j) OU Tinidazole 2g dose unique (adulte). Régime sans lactose temporaire. Traiter toute la famille si cas groupés.",
            "ar": "ميترونيدازول 250 ملغ 3 مرات يوميا (5-7 أيام) أو تينيدازول 2 غرام جرعة واحدة (بالغ). حمية بدون لاكتوز مؤقتة. علاج كل العائلة إذا حالات متعددة.",
            "en": "Metronidazole 250mg x3/d (5-7d) OR Tinidazole 2g single dose (adult). Temporary lactose-free diet. Treat whole family if clustered cases."
        },
        "tests": ["Ag Giardia ELISA (selles)", "Test malabsorption (D-xylose)", "EPS x3 (sensibilité 60-90%)", "PCR Giardia (gold standard)", "Biopsie duodénale si négativité"],
        "color": "#ff9500",
        "icon": "🟠",
        "cycle": {
            "fr": "Kyste ingéré → Excystation duodénale → Trophozoïte → Adhésion mucus/villosités → Multiplication binaire → Enkystement iléal → Émission",
            "ar": "كيس مبتلع ← انفكاس اثني عشري ← طور نشط ← التصاق بمخاط/زغيبات ← تكاثر ثنائي ← تكيس لفائفي ← إخراج",
            "en": "Ingested cyst → Duodenal excystation → Trophozoite → Mucus/villi adhesion → Binary multiplication → Ileal encystation → Emission"
        },
        "keys": {
            "fr": "• Forme CERF-VOLANT pathognomonique (vue dorsale)\n• 2 noyaux = FACE DE HIBOU 🦉\n• Disque adhésif visible au Lugol (ventouse)\n• Mobilité 'feuille morte' caractéristique\n• Selles graisseuses brillantes",
            "ar": "• شكل طائرة ورقية مميز (منظر ظهري)\n• نواتان = وجه البومة 🦉\n• القرص اللاصق مرئي باللوغول\n• حركة 'ورقة ميتة' مميزة\n• براز دهني لامع",
            "en": "• KITE shape pathognomonic (dorsal view)\n• 2 nuclei = OWL FACE 🦉\n• Adhesive disk visible on Lugol\n• 'Falling leaf' motility\n• Shiny greasy stools"
        },
        "incubation": "1-3 semaines",
        "transmission": "Oro-fécale (eau, aliments, mains sales)",
        "geography": "Mondial (surtout pays tempérés)"
    },
    
    "Leishmania": {
        "sci": "Leishmania infantum / major / tropica",
        "morph": {
            "fr": "Amastigotes ovoïdes (2-5µm) INTRACELLULAIRES dans macrophages. Noyau volumineux + kinétoplaste en bâtonnet (MGG/Giemsa). Formes libres dans lyse cellulaire.",
            "ar": "أماستيغوت بيضاوية (2-5 ميكرومتر) داخل البلاعم. نواة كبيرة + كينيتوبلاست عصوي (MGG/جيمزا). أشكال حرة عند تحلل الخلية.",
            "en": "Ovoid amastigotes (2-5µm) INTRACELLULAR in macrophages. Large nucleus + rod-shaped kinetoplast (MGG/Giemsa). Free forms in cell lysis."
        },
        "desc": {
            "fr": "Transmis par phlébotome (Phlebotomus). **Cutanée** (L. major, L. tropica): bouton d'Orient. **Viscérale** (L. infantum): Kala-azar (fièvre, splénomégalie, pancytopénie). **Algérie**: L. infantum (Nord-Centre), L. major (Sud-Sahara).",
            "ar": "ينتقل عبر ذبابة الرمل. **جلدية** (L. major, L. tropica): دمل الشرق. **حشوية** (L. infantum): كالا آزار (حمى، تضخم طحال، نقص كريات). **الجزائر**: L. infantum (شمال-وسط)، L. major (جنوب-صحراء).",
            "en": "Sandfly-transmitted (Phlebotomus). **Cutaneous** (L. major, L. tropica): Oriental sore. **Visceral** (L. infantum): Kala-azar (fever, splenomegaly, pancytopenia). **Algeria**: L. infantum (North-Center), L. major (South-Sahara)."
        },
        "funny": {
            "fr": "Petit mais costaud ! 💪 Il squatte les macrophages et organise des fêtes dans ta rate ! 🎉🦠 L'intrus microscopique ultime !",
            "ar": "صغير لكن قوي! 💪 يحتل البلاعم وينظم حفلات في طحالك! 🎉🦠 المتطفل المجهري النهائي!",
            "en": "Small but mighty! 💪 Squats in macrophages and throws parties in your spleen! 🎉🦠 The ultimate microscopic intruder!"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "**Cutanée**: Glucantime® (antimoine) 20mg/kg/j IM 20j. **Viscérale**: Amphotéricine B liposomale 3mg/kg/j IV (1er choix) OU Glucantime 20mg/kg/j IM 28j. **MDO en Algérie** (déclaration obligatoire).",
            "ar": "**جلدية**: غلوكانتيم 20 ملغ/كغ/يوم عضليا 20 يوم. **حشوية**: أمفوتيريسين ب دهني 3 ملغ/كغ/يوم وريديا (خيار أول) أو غلوكانتيم. **تبليغ إجباري في الجزائر**.",
            "en": "**Cutaneous**: Glucantime® (antimony) 20mg/kg/d IM 20d. **Visceral**: Liposomal Amphotericin B 3mg/kg/d IV (1st choice) OR Glucantime. **Notifiable in Algeria**."
        },
        "tests": ["IDR Montenegro (Leishmanine)", "Sérologie IFI/ELISA", "Ponction médullaire (myélogramme)", "Biopsie cutanée + MGG", "PCR Leishmania (très sensible)", "NFS (pancytopénie si viscérale)"],
        "color": "#ff0040",
        "icon": "🔴",
        "cycle": {
            "fr": "Piqûre phlébotome ♀ → Inoculation promastigotes → Phagocytose macrophages → Transformation amastigotes → Multiplication → Lyse cellulaire → Dissémination",
            "ar": "لدغة ذبابة رمل ♀ ← تلقيح بروماستيغوت ← بلعمة بالبلاعم ← تحول لأماستيغوت ← تكاثر ← تحلل خلوي ← انتشار",
            "en": "Female sandfly bite → Promastigote inoculation → Macrophage phagocytosis → Amastigote transformation → Multiplication → Cell lysis → Dissemination"
        },
        "keys": {
            "fr": "• Amastigotes 2-5µm INTRACELLULAIRES (clé !)\n• Noyau + kinétoplaste (MGG violet)\n• Culture NNN (Novy-McNeal-Nicolle)\n• PCR = gold standard (sensibilité >95%)\n• Cutanée: bouton indolore ulcéré\n• Viscérale: FIEVRE + SPLENOMEGALIE + PANCYTOPENIE",
            "ar": "• أماستيغوت 2-5 ميكرومتر داخل خلوية (مفتاح!)\n• نواة + كينيتوبلاست (MGG بنفسجي)\n• زراعة NNN\n• PCR المعيار الذهبي (حساسية >95%)\n• جلدية: دمل غير مؤلم متقرح\n• حشوية: حمى + تضخم طحال + نقص كريات",
            "en": "• 2-5µm INTRACELLULAR amastigotes (key!)\n• Nucleus + kinetoplast (MGG purple)\n• NNN culture\n• PCR = gold standard (>95% sensitivity)\n• Cutaneous: painless ulcerated button\n• Visceral: FEVER + SPLENOMEGALY + PANCYTOPENIA"
        },
        "incubation": "Cutanée: 2-8 semaines. Viscérale: 3-6 mois",
        "transmission": "Phlébotome femelle (Phlebotomus)",
        "geography": "Algérie: L. infantum (Nord), L. major (Sud)"
    },
    
    "Plasmodium": {
        "sci": "Plasmodium falciparum / vivax / ovale / malariae / knowlesi",
        "morph": {
            "fr": "**P. falciparum**: Anneau 'bague à chaton' fin (1/5 GR), gamétocytes EN BANANE 🍌. **P. vivax**: Trophozoïte amœboïde, granulations Schüffner, GR hypertrophié. **P. malariae**: Formes en rosace, bandes équatoriales.",
            "ar": "**P. falciparum**: حلقة رقيقة شكل خاتم (1/5 كرية حمراء)، خلايا جنسية موزية 🍌. **P. vivax**: طور نشط أميبي، حبيبات شوفنر، كرية حمراء متضخمة. **P. malariae**: أشكال وردية، أشرطة استوائية.",
            "en": "**P. falciparum**: Thin 'signet ring' (1/5 RBC), BANANA gametocytes 🍌. **P. vivax**: Amoeboid trophozoite, Schüffner dots, enlarged RBC. **P. malariae**: Rosette forms, equatorial bands."
        },
        "desc": {
            "fr": "**URGENCE MÉDICALE !** Paludisme/Malaria. **P. falciparum** = LE PLUS MORTEL (accès pernicieux, neuropaludisme). Transmis par Anophèle ♀. Cycle érythrocytaire: accès fébriles cycliques (tierces/quartes). **Diagnostic <2h impératif !**",
            "ar": "**حالة طوارئ طبية!** ملاريا. **P. falciparum** = الأكثر فتكاً (نوبة خبيثة، ملاريا دماغية). ينتقل عبر أنثى الأنوفيل. دورة كرية حمراء: نوبات حمى دورية. **تشخيص <2 ساعة إجباري!**",
            "en": "**MEDICAL EMERGENCY!** Malaria. **P. falciparum** = MOST LETHAL (pernicious attack, cerebral malaria). Female Anopheles transmission. Erythrocytic cycle: cyclical fever attacks. **Diagnosis <2h mandatory!**"
        },
        "funny": {
            "fr": "Il demande le mariage à tes globules ! 💍🔴 Gamétocytes en banane 🍌 = le clown du microscope ! Accès pernicieux = quand il invite toute sa famille ! 🦟💀",
            "ar": "يطلب الزواج من كرياتك! 💍🔴 خلايا جنسية موزية 🍌 = مهرج المجهر! نوبة خبيثة = عندما يدعو كل عائلته! 🦟💀",
            "en": "Proposes marriage to your blood cells! 💍🔴 Banana gametocytes 🍌 = microscope's clown! Pernicious attack = when he invites his whole family! 🦟💀"
        },
        "risk": "critical",
        "risk_d": {"fr": "URGENCE VITALE", "ar": "طوارئ حيوية", "en": "LIFE-THREATENING"},
        "advice": {
            "fr": "**HOSPITALISATION IMMÉDIATE !** ACT (Artésunate-Amodiaquine) OU Artéméther-Luméfantrine. **Si grave**: Artésunate IV 2.4mg/kg (H0-H12-H24). Parasitémie /4-6h. Surveillance réanimation si >2% ou signes gravité.",
            "ar": "**دخول المستشفى فوراً!** ACT (أرتيسونات-أموديكين) أو أرتيميثر-لوميفانترين. **إذا خطير**: أرتيسونات وريدي 2.4 ملغ/كغ (س0-س12-س24). طفيليات كل 4-6 ساعات. مراقبة إنعاش إذا >2% أو علامات خطر.",
            "en": "**IMMEDIATE HOSPITALIZATION!** ACT (Artesunate-Amodiaquine) OR Artemether-Lumefantrine. **If severe**: IV Artesunate 2.4mg/kg (H0-H12-H24). Parasitemia /4-6h. ICU monitoring if >2% or danger signs."
        },
        "tests": ["TDR Paludisme (HRP2/pLDH) - rapide !", "Frottis+GE URGENCE <2h", "Parasitémie quantitative /4-6h", "NFS (anémie, thrombopénie)", "Bilan hépato-rénal", "Glycémie (hypoglycémie grave)", "Lactates si grave"],
        "color": "#7f1d1d",
        "icon": "🚨",
        "cycle": {
            "fr": "Piqûre Anophèle ♀ → Sporozoïtes → Hépatocytes (cycle pré-érythrocytaire 6-15j) → Mérozoïtes → Hématies (cycle érythrocytaire 48-72h) → Gamétocytes → Anophèle",
            "ar": "لدغة أنوفيل ♀ ← سبوروزويت ← خلايا كبدية (دورة قبل كريات 6-15 يوم) ← ميروزويت ← كريات حمراء (دورة 48-72 ساعة) ← خلايا جنسية ← أنوفيل",
            "en": "Anopheles ♀ bite → Sporozoites → Hepatocytes (pre-erythrocytic cycle 6-15d) → Merozoites → RBCs (erythrocytic cycle 48-72h) → Gametocytes → Anopheles"
        },
        "keys": {
            "fr": "• **URGENCE <2h** (pronostic vital)\n• Frottis: identification ESPÈCE\n• GE: 10x plus SENSIBLE que frottis\n• Parasitémie >2% = PALUDISME GRAVE\n• BANANE 🍌 = P. falciparum (pathognomonique)\n• Neuropalu: convulsions, coma\n• Anémie sévère: hémoglobine <7g/dL",
            "ar": "• **طوارئ <2 ساعة** (حياة على المحك)\n• لطاخة: تحديد النوع\n• GE: أكثر حساسية 10 مرات\n• طفيليات >2% = ملاريا خطيرة\n• موز 🍌 = P. falciparum (مميز)\n• ملاريا دماغية: تشنجات، غيبوبة\n• فقر دم شديد: هيموغلوبين <7 غ/دل",
            "en": "• **URGENT <2h** (life at stake)\n• Smear: SPECIES identification\n• Thick drop: 10x MORE SENSITIVE\n• Parasitemia >2% = SEVERE MALARIA\n• BANANA 🍌 = P. falciparum (pathognomonic)\n• Cerebral: convulsions, coma\n• Severe anemia: Hb <7g/dL"
        },
        "incubation": "7-30 jours (P. falciparum 7-14j)",
        "transmission": "Anopheles femelle (crépusculaire/nocturne)",
        "geography": "Zone inter-tropicale (Afrique +++, Asie, Amérique Sud)"
    },
    
    "Trypanosoma": {
        "sci": "Trypanosoma brucei gambiense / rhodesiense (Afrique) - T. cruzi (Amérique)",
        "morph": {
            "fr": "Forme S/C allongée (15-30µm), flagelle libre antérieur, membrane ondulante latérale, kinétoplaste postérieur volumineux. Noyau central. Mobile très actif.",
            "ar": "شكل S/C ممدود (15-30 ميكرومتر)، سوط حر أمامي، غشاء متموج جانبي، كينيتوبلاست خلفي ضخم. نواة مركزية. متحرك جداً.",
            "en": "Elongated S/C shape (15-30µm), anterior free flagellum, lateral undulating membrane, large posterior kinetoplast. Central nucleus. Very active motility."
        },
        "desc": {
            "fr": "**Maladie du sommeil** (T. b. gambiense: chronique Afrique Ouest/Centre, T. b. rhodesiense: aiguë Afrique Est) transmise par Glossine (mouche tsé-tsé). **Chagas** (T. cruzi): triatome, Amérique latine. Phase 1: hémolymphatique. Phase 2: **neurologique** (léthargie, troubles psychiques).",
            "ar": "**مرض النوم** (T. b. gambiense: مزمن غرب/وسط إفريقيا، T. b. rhodesiense: حاد شرق إفريقيا) عبر ذبابة تسي تسي. **شاغاس** (T. cruzi): بق ثلاثي، أمريكا اللاتينية. مرحلة 1: دموية لمفاوية. مرحلة 2: **عصبية** (خمول، اضطرابات نفسية).",
            "en": "**Sleeping sickness** (T. b. gambiense: chronic West/Central Africa, T. b. rhodesiense: acute East Africa) by Tsetse fly. **Chagas** (T. cruzi): triatomine, Latin America. Phase 1: hemolymphatic. Phase 2: **neurological** (lethargy, psychiatric disorders)."
        },
        "funny": {
            "fr": "Il court avec sa membrane ondulante comme une cape de super-héros ! 🦸‍♂️ La tsé-tsé = le pire taxi du monde ! 🚕💀 T. cruzi = l'espion d'Amérique latine ! 🕵️",
            "ar": "يركض بغشائه المتموج كعباءة بطل خارق! 🦸‍♂️ ذبابة تسي تسي = أسوأ تاكسي في العالم! 🚕💀 T. cruzi = جاسوس أمريكا اللاتينية! 🕵️",
            "en": "Runs with its undulating membrane like a superhero cape! 🦸‍♂️ Tsetse = world's worst taxi! 🚕💀 T. cruzi = Latin America's spy! 🕵️"
        },
        "risk": "high",
        "risk_d": {"fr": "Élevé", "ar": "مرتفع", "en": "High"},
        "advice": {
            "fr": "**T. brucei Phase 1**: Pentamidine (gambiense) ou Suramine (rhodesiense). **Phase 2**: NECT (Nifurtimox-Eflornithine) ou Melarsoprol (toxique). **T. cruzi**: Benznidazole 5mg/kg/j 60j. **PL OBLIGATOIRE** (stadification).",
            "ar": "**T. brucei مرحلة 1**: بنتاميدين (gambiense) أو سورامين (rhodesiense). **مرحلة 2**: NECT أو ميلارسوبرول (سام). **T. cruzi**: بنزنيدازول 5 ملغ/كغ/يوم 60 يوم. **بزل قطني إجباري** (تصنيف).",
            "en": "**T. brucei Phase 1**: Pentamidine (gambiense) or Suramine (rhodesiense). **Phase 2**: NECT (Nifurtimox-Eflornithine) or Melarsoprol (toxic). **T. cruzi**: Benznidazole 5mg/kg/d 60d. **LP MANDATORY** (staging)."
        },
        "tests": ["Ponction lombaire (PL) - staging phase 2", "Sérologie CATT (Card Agglutination Test)", "IgM LCR >10% = phase 2", "Suc ganglionnaire (si adénopathies)", "NFS (anémie, thrombopénie)", "Mini Anion Exchange Centrifugation (mAECT)"],
        "color": "#ff0040",
        "icon": "🔴",
        "cycle": {
            "fr": "Piqûre Glossine/Triatome → Trypomastigotes métacycliques → Sang/Lymphe (Phase 1: fièvre, adénopathies) → Franchissement BHE → LCR/Cerveau (Phase 2: troubles neurologiques/psychiatriques) → Mort si non traité",
            "ar": "لدغة تسي تسي/بق ثلاثي ← تريبوماستيغوت ← دم/لمف (مرحلة 1: حمى، عقد لمفاوية) ← عبور حاجز دماغي ← سائل دماغي/دماغ (مرحلة 2: اضطرابات عصبية/نفسية) ← موت إذا لم يعالج",
            "en": "Glossina/Triatomine bite → Metacyclic trypomastigotes → Blood/Lymph (Phase 1: fever, lymphadenopathy) → BBB crossing → CSF/Brain (Phase 2: neurological/psychiatric disorders) → Death if untreated"
        },
        "keys": {
            "fr": "• Forme S/C + MEMBRANE ONDULANTE (pathognomonique)\n• Kinétoplaste postérieur (vs Leishmania)\n• IgM très élevée (polyclonale)\n• PL = STADIFICATION (phase 1 vs 2)\n• LCR: trypanosomes + lymphocytes + IgM\n• Signe de Winterbottom: adénopathies cervicales postérieures",
            "ar": "• شكل S/C + غشاء متموج (مميز)\n• كينيتوبلاست خلفي (مقابل ليشمانيا)\n• IgM مرتفع جداً\n• بزل قطني = تصنيف (مرحلة 1 مقابل 2)\n• سائل دماغي: تريبانوسوم + لمفاويات + IgM\n• علامة وينتربوتوم: عقد لمفاوية عنقية خلفية",
            "en": "• S/C + UNDULATING MEMBRANE (pathognomonic)\n• Posterior kinetoplast (vs Leishmania)\n• Very high IgM (polyclonal)\n• LP = STAGING (phase 1 vs 2)\n• CSF: trypanosomes + lymphocytes + IgM\n• Winterbottom sign: posterior cervical lymphadenopathy"
        },
        "incubation": "T.b.g: semaines-mois. T.b.r: jours-semaines. T.cruzi: 1-2 semaines",
        "transmission": "Glossine ♀ (Afrique), Triatome (Amérique)",
        "geography": "T. brucei: Afrique sub-saharienne. T. cruzi: Amérique latine"
    },
    
    "Schistosoma": {
        "sci": "Schistosoma haematobium (urinaire) / mansoni (intestinal) / japonicum / intercalatum",
        "morph": {
            "fr": "Œuf ovoïde (115-170µm selon espèce): **S. haematobium**: éperon TERMINAL, **S. mansoni**: éperon LATÉRAL proéminent. Miracidium cilié mobile visible si œuf viable (échographie). Coque épaisse transparente.",
            "ar": "بيضة بيضاوية (115-170 ميكرومتر): **S. haematobium**: شوكة طرفية، **S. mansoni**: شوكة جانبية بارزة. ميراسيديوم مهدب متحرك مرئي إذا بيضة حية. قشرة سميكة شفافة.",
            "en": "Ovoid egg (115-170µm): **S. haematobium**: TERMINAL spine, **S. mansoni**: prominent LATERAL spine. Motile ciliated miracidium visible if viable egg. Thick transparent shell."
        },
        "desc": {
            "fr": "**Bilharziose/Schistosomiase**. **S. haematobium**: uro-génitale (hématurie terminale, cancer vessie à long terme). **S. mansoni**: hépato-intestinale (diarrhée sanglante, fibrose hépatique Symmers). Transmission: baignade eaux douces (cercaires pénètrent peau). **Réservoir**: escargots Bulinus/Biomphalaria.",
            "ar": "**البلهارسيا**. **S. haematobium**: بولي تناسلي (بيلة دموية طرفية، سرطان مثانة طويل الأمد). **S. mansoni**: كبدي معوي (إسهال دموي، تليف كبدي سيميرز). الانتقال: سباحة مياه عذبة (سركاريا تخترق الجلد). **مستودع**: قواقع بولينوس/بيومفالاريا.",
            "en": "**Bilharzia/Schistosomiasis**. **S. haematobium**: urogenital (terminal hematuria, bladder cancer long-term). **S. mansoni**: hepato-intestinal (bloody diarrhea, Symmers hepatic fibrosis). Transmission: freshwater bathing (cercariae penetrate skin). **Reservoir**: Bulinus/Biomphalaria snails."
        },
        "funny": {
            "fr": "L'œuf avec un dard ! ⚡🥚 Les cercaires = micro-torpilles cherche-chaleur ! 🎯🌡️ Escargot complice = l'usine à parasites ! 🐌🏭",
            "ar": "البيضة ذات الشوكة! ⚡🥚 السركاريا = طوربيدات صغيرة باحثة عن الحرارة! 🎯🌡️ القوقع الشريك = مصنع الطفيليات! 🐌🏭",
            "en": "Egg with a stinger! ⚡🥚 Cercariae = heat-seeking micro-torpedoes! 🎯🌡️ Snail accomplice = parasite factory! 🐌🏭"
        },
        "risk": "medium",
        "risk_d": {"fr": "Moyen", "ar": "متوسط", "en": "Medium"},
        "advice": {
            "fr": "**Praziquantel 40mg/kg** dose unique PO (après repas). **S. haematobium**: prélever urines de MIDI (12-14h = pic excrétion). Contrôle J30. Échographie vésicale/hépatique selon forme. Traitement TOUTE la famille si cas groupés.",
            "ar": "**برازيكوانتيل 40 ملغ/كغ** جرعة واحدة فموية (بعد الوجبة). **S. haematobium**: جمع بول الظهيرة (12-14 ساعة = ذروة الإخراج). مراقبة يوم 30. إيكوغرافيا حسب الشكل. علاج كل العائلة إذا حالات متعددة.",
            "en": "**Praziquantel 40mg/kg** single PO dose (after meal). **S. haematobium**: collect MIDDAY urine (12-14h = excretion peak). Follow-up D30. Ultrasound depending on form. Treat WHOLE family if clustered cases."
        },
        "tests": ["ECBU midi (S. haematobium)", "EPS x3 (S. mansoni)", "Sérologie (réaction croisée)", "Écho vésicale (lésions, calcifications)", "Écho hépatique (fibrose Symmers, hypertension portale)", "NFS (éosinophilie 20-70%)", "Biopsie rectale (S. mansoni si EPS -)"],
        "color": "#ff9500",
        "icon": "🟠",
        "cycle": {
            "fr": "Œuf → Éclosion (eau douce) → Miracidium cilié → Pénètre mollusque (Bulinus/Biomphalaria) → Sporocystes → Cercaires (fourche caudale) → Nage + pénétration cutanée → Schistosomules → Migration veines → Vers adultes ♂♀ (accouplés) → Ponte (plexus vésical/mésentérique) → Émission urines/selles",
            "ar": "بيضة ← فقس (ماء عذب) ← ميراسيديوم مهدب ← يخترق رخويات ← سبوروسيست ← سركاريا (ذيل متشعب) ← سباحة + اختراق جلد ← شيستوسومول ← هجرة أوردة ← ديدان بالغة ♂♀ (متزاوجة) ← وضع بيض (ضفيرة مثانة/معوية) ← إخراج بول/براز",
            "en": "Egg → Hatching (freshwater) → Ciliated miracidium → Penetrates snail (Bulinus/Biomphalaria) → Sporocysts → Cercariae (forked tail) → Swimming + skin penetration → Schistosomules → Vein migration → Adult worms ♂♀ (paired) → Egg laying (vesical/mesenteric plexus) → Urine/stool emission"
        },
        "keys": {
            "fr": "• **S.h: éperon TERMINAL**, urines MIDI (12-14h)\n• **S.m: éperon LATÉRAL**, selles\n• Miracidium VIVANT = infection active\n• Éosinophilie ÉLEVÉE (20-70%) = helminthiase\n• Dermatite cercarienne = 'puce du baigneur'\n• Calcifications vésicales en coquille d'œuf (radio)",
            "ar": "• **S.h: شوكة طرفية**، بول الظهيرة (12-14 ساعة)\n• **S.m: شوكة جانبية**، براز\n• ميراسيديوم حي = عدوى نشطة\n• فرط حمضات مرتفع (20-70%) = ديدان\n• التهاب جلد سركاريا = 'برغوث السباح'\n• تكلسات مثانة شكل قشرة بيضة (أشعة)",
            "en": "• **S.h: TERMINAL spine**, MIDDAY urine (12-14h)\n• **S.m: LATERAL spine**, stool\n• LIVING miracidium = active infection\n• HIGH eosinophilia (20-70%) = helminthiasis\n• Cercarial dermatitis = 'swimmer's itch'\n• Eggshell bladder calcifications (X-ray)"
        },
        "incubation": "4-8 semaines (primo-invasion: fièvre Katayama)",
        "transmission": "Baignade eaux douces (lacs, rivières, mares)",
        "geography": "S.h: Afrique, Moyen-Orient. S.m: Afrique, Amérique Sud, Caraïbes"
    },
    
    "Negative": {
        "sci": "Aucun parasite détecté",
        "morph": {
            "fr": "Absence d'éléments parasitaires. Flore bactérienne commensale normale. Leucocytes rares. Cellules épithéliales présentes.",
            "ar": "غياب العناصر الطفيلية. فلورا بكتيرية تكافلية طبيعية. كريات بيضاء نادرة. خلايا ظهارية موجودة.",
            "en": "No parasitic elements. Normal commensal bacterial flora. Rare leukocytes. Epithelial cells present."
        },
        "desc": {
            "fr": "Échantillon négatif pour parasites. **IMPORTANT**: Un seul examen négatif N'EXCLUT PAS le diagnostic (sensibilité EPS simple: 50-60%). **RÉPÉTER x3** à intervalles (J1, J3, J5) pour confirmation. Concentration (Ritchie) augmente sensibilité à 90%.",
            "ar": "عينة سلبية للطفيليات. **مهم**: فحص واحد سلبي لا يستبعد التشخيص (حساسية فحص بسيط: 50-60%). **كرر 3 مرات** على فترات (ي1، ي3، ي5) للتأكيد. التركيز (ريتشي) يزيد الحساسية إلى 90%.",
            "en": "Negative sample for parasites. **IMPORTANT**: Single negative exam DOES NOT EXCLUDE diagnosis (simple stool sensitivity: 50-60%). **REPEAT x3** at intervals (D1, D3, D5) for confirmation. Concentration (Ritchie) increases sensitivity to 90%."
        },
        "funny": {
            "fr": "Rien à signaler, capitaine ! 🎖️ Mais les parasites sont des maîtres du cache-cache... 🙈 Comme un ninja invisible ! 🥷 Toujours vérifier 3 fois !",
            "ar": "لا شيء يذكر، أيها القبطان! 🎖️ لكن الطفيليات أساتذة في الاختباء... 🙈 كنينجا غير مرئي! 🥷 تحقق دائماً 3 مرات!",
            "en": "Nothing to report, captain! 🎖️ But parasites are hide-and-seek masters... 🙈 Like an invisible ninja! 🥷 Always check 3 times!"
        },
        "risk": "none",
        "risk_d": {"fr": "Négatif", "ar": "سلبي", "en": "Negative"},
        "advice": {
            "fr": "**RAS parasitologique**. Si suspicion clinique forte (symptômes persistants, contexte épidémiologique): **RÉPÉTER EPS x3** (J1, J3, J5) + **Concentration Ritchie** + **Sérologie ciblée** selon orientation. Consulter si symptômes persistent.",
            "ar": "**لا شيء طفيلياً**. إذا اشتباه سريري قوي (أعراض مستمرة، سياق وبائي): **كرر فحص براز 3 مرات** (ي1، ي3، ي5) + **تركيز ريتشي** + **مصلية موجهة**. استشر إذا استمرت الأعراض.",
            "en": "**No parasitological abnormality**. If strong clinical suspicion (persistent symptoms, epidemiological context): **REPEAT stool x3** (D1, D3, D5) + **Ritchie concentration** + **Targeted serology**. Consult if symptoms persist."
        },
        "tests": ["Répéter EPS x3 (J1, J3, J5)", "Concentration Ritchie/Willis", "Sérologie ciblée (Toxoplasma, Leishmania, etc.)", "NFS (éosinophilie orientante)", "Coproculture (bactéries)", "Calprotectine fécale (inflammation)"],
        "color": "#00ff88",
        "icon": "🟢",
        "cycle": {"fr": "N/A - Aucun cycle parasitaire", "ar": "غير متوفر - لا دورة طفيلية", "en": "N/A - No parasitic cycle"},
        "keys": {
            "fr": "• Direct + Lugol NÉGATIF\n• Concentration NÉGATIVE\n• **RÉPÉTER x3** impératif !\n• Sensibilité EPS simple: 50-60%\n• Concentration: 90%\n• PCR: >95% (si disponible)\n• Contexte clinique prime toujours",
            "ar": "• مباشر + لوغول سلبي\n• تركيز سلبي\n• **كرر 3 مرات** إجباري!\n• حساسية فحص بسيط: 50-60%\n• تركيز: 90%\n• PCR: >95% (إذا متوفر)\n• السياق السريري دائماً أهم",
            "en": "• Direct + Lugol NEGATIVE\n• Concentration NEGATIVE\n• **REPEAT x3** mandatory!\n• Simple stool sensitivity: 50-60%\n• Concentration: 90%\n• PCR: >95% (if available)\n• Clinical context always prevails"
        },
        "incubation": "N/A",
        "transmission": "N/A",
        "geography": "N/A"
    }
}

CLASS_NAMES = list(PARASITE_DB.keys())

# ============================================
#  COMPLETE TRANSLATIONS - ENHANCED
# ============================================
TR = {
    "fr": {
        # Navigation
        "app_title": "DM Smart Lab AI",
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
        
        # Greetings
        "greeting_morning": "Bonjour",
        "greeting_afternoon": "Bon après-midi",
        "greeting_evening": "Bonsoir",
        
        # Voice & Buttons
        "welcome_btn": "Message de Bienvenue",
        "intro_btn": "Présentation du Système",
        "stop_voice": "Arrêter",
        "listen": "Écouter",
        
        # Patient Info
        "patient_info": "Informations du Patient",
        "patient_name": "Nom du Patient",
        "patient_firstname": "Prénom",
        "age": "Âge",
        "sex": "Sexe",
        "male": "Homme",
        "female": "Femme",
        "weight": "Poids (kg)",
        "sample_type": "Type d'Échantillon",
        
        # Lab Info
        "lab_info": "Informations du Laboratoire",
        "microscope": "Microscope",
        "magnification": "Grossissement",
        "preparation": "Préparation",
        "technician": "Technicien",
        "notes": "Notes / Observations",
        
        # Image Capture
        "image_capture": "Capture Microscopique",
        "take_photo": "Prendre une Photo (Caméra)",
        "upload_file": "Importer un fichier",
        "camera_hint": "Placez l'oculaire du microscope devant la caméra",
        
        # Results
        "result": "Résultat",
        "confidence": "Confiance",
        "risk": "Risque",
        "morphology": "Morphologie",
        "description": "Description",
        "advice": "Conseil Médical",
        "extra_tests": "Examens complémentaires suggérés",
        "diagnostic_keys": "Clés Diagnostiques",
        "lifecycle": "Cycle de Vie",
        "all_probabilities": "Toutes les probabilités",
        
        # Actions
        "download_pdf": "Télécharger PDF",
        "save_db": "Sauvegarder",
        "new_analysis": "Nouvelle Analyse",
        "validate": "Valider",
        "export_csv": "Exporter CSV",
        "export_json": "Exporter JSON",
        
        # Dashboard
        "total_analyses": "Total Analyses",
        "reliable": "Fiables",
        "to_verify": "À Vérifier",
        "most_frequent": "Plus Fréquent",
        "avg_confidence": "Confiance Moy.",
        "parasite_distribution": "Distribution des Parasites",
        "confidence_levels": "Niveaux de Confiance",
        "trends": "Tendances (30 jours)",
        "history": "Historique Complet",
        
        # Quiz
        "start_quiz": "Démarrer le Quiz",
        "next_question": "Question Suivante",
        "restart": "Recommencer",
        "leaderboard": "Classement",
        "score_excellent": "🏆 Excellent ! Vous maîtrisez la parasitologie !",
        "score_good": "👍 Bien joué ! Continuez à apprendre !",
        "score_average": "📚 Pas mal ! Révisez encore un peu !",
        "score_low": "💪 Courage ! La parasitologie s'apprend avec la pratique !",
        
        # Chat
        "chat_welcome": "Bonjour ! Je suis **DM Bot**, votre assistant parasitologique intelligent.\n\n🔬 **Je peux vous aider avec:**\n- **Parasites**: Amoeba, Giardia, Plasmodium, Leishmania, Trypanosoma, Schistosoma, Toxoplasma, Ascaris, Taenia, Oxyure, Cryptosporidium...\n- **Techniques**: Microscopie, Colorations, Concentration, EPS...\n- **Traitements**: Protocoles thérapeutiques\n- **Cas cliniques**: Diagnostic différentiel\n\n💡 **Tapez un mot-clé** (ex: 'amoeba', 'microscope', 'traitement') ou tapez **'aide'** pour voir tout ce que je connais !",
        "chat_placeholder": "Posez votre question sur les parasites...",
        "chat_not_found": "🤔 Je n'ai pas trouvé de réponse exacte.\n\n💡 **Essayez avec:**\n• Un nom de parasite: **amoeba**, **giardia**, **plasmodium**, **leishmania**\n• Une technique: **microscope**, **coloration**, **concentration**\n• Un sujet: **traitement**, **hygiene**, **selle**\n\nOu tapez **'aide'** pour voir toutes mes connaissances !",
        "clear_chat": "Effacer le chat",
        "quick_questions": "Questions rapides:",
        
        # Compare
        "image1": "Image 1 (Avant)",
        "image2": "Image 2 (Après)",
        "compare_btn": "Comparer les Images",
        "similarity": "Similarité",
        "filter_comparison": "Comparaison des Filtres",
        "pixel_diff": "Différence Pixel à Pixel",
        
        # General
        "search": "Rechercher...",
        "no_data": "Aucune donnée disponible",
        "no_results": "Aucun résultat trouvé",
        "language": "Langue",
        "daily_tip": "Conseil du Jour",
        
        # Admin
        "users_mgmt": "Gestion des Utilisateurs",
        "activity_log": "Journal d'Activité",
        "system_info": "Informations Système",
        "create_user": "Créer un Utilisateur",
        "change_pwd": "Changer le Mot de Passe",
        
        # Messages
        "name_required": "⚠️ Le nom du patient est obligatoire !",
        "saved_ok": "✅ Résultat sauvegardé avec succès !",
        "demo_mode": "ℹ️ Mode démonstration (aucun modèle IA chargé)",
        "low_conf_warn": "⚠️ Confiance faible. Vérification manuelle recommandée !",
        
        # Voice messages
        "voice_welcome": "Bienvenue dans Smart Lab AI ! Nous sommes ravis de vous accueillir dans ce système d'intelligence artificielle dédié au diagnostic parasitologique. Ce système a été conçu pour assister les professionnels de santé dans l'identification rapide et précise des parasites.",
        "voice_intro": "Je suis Smart Lab AI, système de diagnostic parasitologique par intelligence artificielle. J'ai été développé par deux techniciens supérieurs de l'Institut National de Formation Supérieure Paramédicale de Ouargla. Sebbag Mohamed Dhia Eddine, expert en intelligence artificielle et conception, et Ben Sghir Mohamed, expert en laboratoire et données. Ensemble, nous repoussons les limites de la parasitologie moderne !",
        
        # About
        "quick_overview": "Aperçu Rapide",
        "where_science": "Où la Science Rencontre l'Intelligence",
        "system_desc": "Système de diagnostic parasitologique assisté par IA",
        "dev_team": "Équipe de Développement",
        "institution": "Établissement",
        "technologies": "Technologies Utilisées",
    },
    
    "ar": {
        # Navigation
        "app_title": "مختبر DM الذكي",
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
        
        # Greetings
        "greeting_morning": "صباح الخير",
        "greeting_afternoon": "مساء الخير",
        "greeting_evening": "مساء الخير",
        
        # Voice & Buttons
        "welcome_btn": "رسالة ترحيبية",
        "intro_btn": "تقديم النظام",
        "stop_voice": "إيقاف",
        "listen": "استماع",
        
        # Patient Info
        "patient_info": "معلومات المريض",
        "patient_name": "اسم المريض",
        "patient_firstname": "الاسم الأول",
        "age": "العمر",
        "sex": "الجنس",
        "male": "ذكر",
        "female": "أنثى",
        "weight": "الوزن (كغ)",
        "sample_type": "نوع العينة",
        
        # Lab Info
        "lab_info": "معلومات المخبر",
        "microscope": "المجهر",
        "magnification": "التكبير",
        "preparation": "نوع التحضير",
        "technician": "التقني",
        "notes": "ملاحظات",
        
        # Image Capture
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
        "validate": "مصادقة",
        "export_csv": "تصدير CSV",
        "export_json": "تصدير JSON",
        
        # Dashboard
        "total_analyses": "مجموع التحاليل",
        "reliable": "موثوقة",
        "to_verify": "للتحقق",
        "most_frequent": "الأكثر شيوعاً",
        "avg_confidence": "متوسط الثقة",
        "parasite_distribution": "توزيع الطفيليات",
        "confidence_levels": "مستويات الثقة",
        "trends": "الاتجاهات (30 يوم)",
        "history": "السجل الكامل",
        
        # Quiz
        "start_quiz": "بدء الاختبار",
        "next_question": "السؤال التالي",
        "restart": "إعادة",
        "leaderboard": "الترتيب",
        "score_excellent": "🏆 ممتاز ! أنت خبير في علم الطفيليات !",
        "score_good": "👍 أحسنت ! واصل التعلم !",
        "score_average": "📚 لا بأس ! راجع قليلاً !",
        "score_low": "💪 شجاعة ! علم الطفيليات يُتعلم بالممارسة !",
        
        # Chat
        "chat_welcome": "مرحباً! أنا **DM Bot**، مساعدك الذكي في علم الطفيليات.\n\n🔬 **أستطيع مساعدتك في:**\n- **الطفيليات**: الأميبا، الجيارديا، البلازموديوم، الليشمانيا، التريبانوسوما، البلهارسيا...\n- **التقنيات**: المجهر، التلوينات، التركيز...\n- **العلاجات**: البروتوكولات العلاجية\n\n💡 **اكتب كلمة مفتاحية** أو اكتب **'مساعدة'** لرؤية كل ما أعرفه!",
        "chat_placeholder": "اطرح سؤالك عن الطفيليات...",
        "chat_not_found": "🤔 لم أجد إجابة دقيقة.\n\n💡 **جرب:**\n• اسم طفيلي: **amoeba**، **giardia**، **plasmodium**\n• تقنية: **microscope**، **coloration**\n\nأو اكتب **'مساعدة'** لرؤية كل ما أعرفه!",
        "clear_chat": "مسح المحادثة",
        "quick_questions": "أسئلة سريعة:",
        
        # Compare
        "image1": "الصورة 1 (قبل)",
        "image2": "الصورة 2 (بعد)",
        "compare_btn": "مقارنة الصور",
        "similarity": "التشابه",
        "filter_comparison": "مقارنة الفلاتر",
        "pixel_diff": "الفرق بكسل ببكسل",
        
        # General
        "search": "بحث...",
        "no_data": "لا توجد بيانات",
        "no_results": "لا توجد نتائج",
        "language": "اللغة",
        "daily_tip": "نصيحة اليوم",
        
        # Admin
        "users_mgmt": "إدارة المستخدمين",
        "activity_log": "سجل النشاط",
        "system_info": "معلومات النظام",
        "create_user": "إنشاء مستخدم",
        "change_pwd": "تغيير كلمة المرور",
        
        # Messages
        "name_required": "⚠️ اسم المريض مطلوب !",
        "saved_ok": "✅ تم الحفظ بنجاح !",
        "demo_mode": "ℹ️ وضع تجريبي (لا يوجد نموذج ذكاء اصطناعي)",
        "low_conf_warn": "⚠️ ثقة منخفضة. يُنصح بالتحقق اليدوي !",
        
        # Voice messages
        "voice_welcome": "مرحباً بكم في مختبر DM الذكي. نحن سعداء باستقبالكم في هذا النظام المخصص للتشخيص الطفيلي بالذكاء الاصطناعي.",
        "voice_intro": "أنا مختبر DM الذكي، النسخة 8.0، نظام تشخيص طفيلي بالذكاء الاصطناعي. تم تطويري من طرف تقنيين ساميين من المعهد الوطني للتكوين العالي شبه الطبي بورقلة.",
        
        # About
        "quick_overview": "نظرة سريعة",
        "where_science": "حيث يلتقي العلم بالذكاء",
        "system_desc": "نظام تشخيص طفيلي بالذكاء الاصطناعي",
        "dev_team": "فريق التطوير",
        "institution": "المؤسسة",
        "technologies": "التقنيات المستخدمة",
    },
    
    "en": {
        # Navigation
        "app_title": "DM Smart Lab AI",
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
        
        # Greetings
        "greeting_morning": "Good morning",
        "greeting_afternoon": "Good afternoon",
        "greeting_evening": "Good evening",
        
        # Voice & Buttons
        "welcome_btn": "Welcome Message",
        "intro_btn": "System Introduction",
        "stop_voice": "Stop",
        "listen": "Listen",
        
        # Patient Info
        "patient_info": "Patient Information",
        "patient_name": "Patient Name",
        "patient_firstname": "First Name",
        "age": "Age",
        "sex": "Sex",
        "male": "Male",
        "female": "Female",
        "weight": "Weight (kg)",
        "sample_type": "Sample Type",
        
        # Lab Info
        "lab_info": "Laboratory Information",
        "microscope": "Microscope",
        "magnification": "Magnification",
        "preparation": "Preparation",
        "technician": "Technician",
        "notes": "Notes / Observations",
        
        # Image Capture
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
        "validate": "Validate",
        "export_csv": "Export CSV",
        "export_json": "Export JSON",
        
        # Dashboard
        "total_analyses": "Total Analyses",
        "reliable": "Reliable",
        "to_verify": "To Verify",
        "most_frequent": "Most Frequent",
        "avg_confidence": "Avg. Confidence",
        "parasite_distribution": "Parasite Distribution",
        "confidence_levels": "Confidence Levels",
        "trends": "Trends (30 days)",
        "history": "Complete History",
        
        # Quiz
        "start_quiz": "Start Quiz",
        "next_question": "Next Question",
        "restart": "Restart",
        "leaderboard": "Leaderboard",
        "score_excellent": "🏆 Excellent! You master parasitology!",
        "score_good": "👍 Well done! Keep learning!",
        "score_average": "📚 Not bad! Review a bit more!",
        "score_low": "💪 Courage! Parasitology is learned through practice!",
        
        # Chat
        "chat_welcome": "Hello! I'm **DM Bot**, your intelligent parasitology assistant.\n\n🔬 **I can help you with:**\n- **Parasites**: Amoeba, Giardia, Plasmodium, Leishmania, Trypanosoma, Schistosoma...\n- **Techniques**: Microscopy, Staining, Concentration...\n- **Treatments**: Therapeutic protocols\n\n💡 **Type a keyword** or type **'help'** to see everything I know!",
        "chat_placeholder": "Ask your question about parasites...",
        "chat_not_found": "🤔 I couldn't find an exact answer.\n\n💡 **Try:**\n• Parasite name: **amoeba**, **giardia**, **plasmodium**\n• Technique: **microscope**, **staining**\n\nOr type **'help'** to see all my knowledge!",
        "clear_chat": "Clear chat",
        "quick_questions": "Quick questions:",
        
        # Compare
        "image1": "Image 1 (Before)",
        "image2": "Image 2 (After)",
        "compare_btn": "Compare Images",
        "similarity": "Similarity",
        "filter_comparison": "Filter Comparison",
        "pixel_diff": "Pixel-by-Pixel Difference",
        
        # General
        "search": "Search...",
        "no_data": "No data available",
        "no_results": "No results found",
        "language": "Language",
        "daily_tip": "Daily Tip",
        
        # Admin
        "users_mgmt": "Users Management",
        "activity_log": "Activity Log",
        "system_info": "System Information",
        "create_user": "Create User",
        "change_pwd": "Change Password",
        
        # Messages
        "name_required": "⚠️ Patient name is required!",
        "saved_ok": "✅ Result saved successfully!",
        "demo_mode": "ℹ️ Demo mode (no AI model loaded)",
        "low_conf_warn": "⚠️ Low confidence. Manual verification recommended!",
        
        # Voice messages
        "voice_welcome": "Welcome to DM Smart Lab AI! We are delighted to have you in this artificial intelligence system dedicated to parasitological diagnosis.",
        "voice_intro": "I am DM Smart Lab AI, version 8 point 0, a parasitological diagnosis system powered by artificial intelligence. Developed at INFSPM Ouargla, Algeria.",
        
        # About
        "quick_overview": "Quick Overview",
        "where_science": "Where Science Meets Intelligence",
        "system_desc": "AI-powered parasitological diagnosis system",
        "dev_team": "Development Team",
        "institution": "Institution",
        "technologies": "Technologies Used",
    }
}

def t(key):
    """Translation helper"""
    lang = st.session_state.get("lang", "fr")
    return TR.get(lang, TR["fr"]).get(key, TR["fr"].get(key, key))

def tl(d):
    """Translate dict"""
    if not isinstance(d, dict):
        return str(d)
    lang = st.session_state.get("lang", "fr")
    return d.get(lang, d.get("fr", str(d)))

def get_greeting():
    """Time-based greeting"""
    h = datetime.now().hour
    if h < 12:
        return t("greeting_morning")
    elif h < 18:
        return t("greeting_afternoon")
    return t("greeting_evening")

# ============================================
#  DATABASE - ENHANCED WITH INDEXES
# ============================================
DB_PATH = "dm_smartlab.db"

@contextmanager
def get_db():
    """Database context manager with optimizations"""
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")  # ✅ Better performance
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Database error: {e}")
        raise
    finally:
        conn.close()

def init_database():
    """Initialize database with enhanced schema and indexes"""
    with get_db() as c:
        # Users table
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT DEFAULT 'viewer',
            speciality TEXT DEFAULT 'Laboratoire',
            email TEXT,
            phone TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0,
            failed_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP
        )""")
        
        # Analyses table - ENHANCED
        c.execute("""CREATE TABLE IF NOT EXISTS analyses (
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
            image_quality_score REAL,
            processing_time_ms INTEGER,
            is_demo INTEGER DEFAULT 0,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            validated INTEGER DEFAULT 0,
            validated_by TEXT,
            validation_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )""")
        
        # Activity log
        c.execute("""CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            action TEXT NOT NULL,
            details TEXT,
            ip_address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Quiz scores
        c.execute("""CREATE TABLE IF NOT EXISTS quiz_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            score INTEGER NOT NULL,
            total_questions INTEGER NOT NULL,
            percentage REAL NOT NULL,
            category TEXT,
            time_seconds INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # ✅ NEW: Chat history table
        c.execute("""CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # ✅ Create indexes for better performance
        c.execute("CREATE INDEX IF NOT EXISTS idx_analyses_user ON analyses(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_analyses_date ON analyses(analysis_date DESC)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_analyses_parasite ON analyses(parasite_detected)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_log(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp DESC)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_quiz_user ON quiz_scores(user_id)")
        
        # Create default users
        _make_defaults(c)

def _hp(pw):
    """Hash password - ENHANCED"""
    if HAS_BCRYPT:
        return bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Fallback: SHA256 with salt
    salt = hashlib.sha256(SECRET_KEY.encode()).hexdigest()[:16]
    return hashlib.sha256((salt + pw).encode()).hexdigest()

def _vp(pw, h):
    """Verify password - ENHANCED"""
    if HAS_BCRYPT:
        try:
            return bcrypt.checkpw(pw.encode('utf-8'), h.encode('utf-8'))
        except Exception:
            pass
    # Fallback
    salt = hashlib.sha256(SECRET_KEY.encode()).hexdigest()[:16]
    return hashlib.sha256((salt + pw).encode()).hexdigest() == h

def _make_defaults(c):
    """Create default users"""
    for u, p, n, r, s in [
        ("admin", "admin2026", "Administrateur Système", "admin", "Administration"),
        ("dhia", "dhia2026", "Sebbag Mohamed Dhia Eddine", "admin", "IA & Conception"),
        ("mohamed", "mohamed2026", "Ben Sghir Mohamed", "technician", "Laboratoire"),
        ("demo", "demo123", "Utilisateur Démo", "viewer", "Démonstration"),
        ("tech1", "tech2026", "Technicien Labo 1", "technician", "Parasitologie"),
    ]:
        if not c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            c.execute("""INSERT INTO users(username,password_hash,full_name,role,speciality) 
                         VALUES(?,?,?,?,?)""", (u, _hp(p), n, r, s))

def db_login(u, p):
    """Enhanced login with IP tracking"""
    with get_db() as c:
        row = c.execute("SELECT * FROM users WHERE username=? AND is_active=1", (u,)).fetchone()
        if not row:
            return None
        
        # Check lockout
        if row["locked_until"]:
            try:
                if datetime.now() < datetime.fromisoformat(row["locked_until"]):
                    return {"error": "locked", "until": row["locked_until"]}
                # Unlock
                c.execute("UPDATE users SET failed_attempts=0, locked_until=NULL WHERE id=?", (row["id"],))
            except Exception:
                pass
        
        # Verify password
        if _vp(p, row["password_hash"]):
            c.execute("""UPDATE users SET last_login=?, login_count=login_count+1, 
                         failed_attempts=0, locked_until=NULL WHERE id=?""",
                      (datetime.now().isoformat(), row["id"]))
            return dict(row)
        
        # Failed attempt
        na = row["failed_attempts"] + 1
        lk = (datetime.now() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat() if na >= MAX_LOGIN_ATTEMPTS else None
        c.execute("UPDATE users SET failed_attempts=?, locked_until=? WHERE id=?", (na, lk, row["id"]))
        return {"error": "wrong", "left": MAX_LOGIN_ATTEMPTS - na}

def db_create_user(u, p, n, r="viewer", s="", email="", phone=""):
    """Create user - ENHANCED"""
    with get_db() as c:
        if c.execute("SELECT 1 FROM users WHERE username=?", (u,)).fetchone():
            return False
        c.execute("""INSERT INTO users(username,password_hash,full_name,role,speciality,email,phone) 
                     VALUES(?,?,?,?,?,?,?)""", (u, _hp(p), n, r, s, email, phone))
        return True

def db_users():
    """Get all users"""
    with get_db() as c:
        return [dict(r) for r in c.execute("""
            SELECT id,username,full_name,role,speciality,email,phone,is_active,
                   last_login,login_count,created_at 
            FROM users ORDER BY created_at DESC
        """).fetchall()]

def db_toggle(uid, active):
    """Toggle user status"""
    with get_db() as c:
        c.execute("UPDATE users SET is_active=? WHERE id=?", (1 if active else 0, uid))

def db_chpw(uid, pw):
    """Change password"""
    with get_db() as c:
        c.execute("UPDATE users SET password_hash=? WHERE id=?", (_hp(pw), uid))

def db_save_analysis(uid, d):
    """Save analysis - ENHANCED"""
    with get_db() as c:
        c.execute("""INSERT INTO analyses(
            user_id, patient_name, patient_firstname, patient_age, patient_sex,
            patient_weight, sample_type, microscope_type, magnification, preparation_type,
            technician1, technician2, notes, parasite_detected, confidence, risk_level,
            is_reliable, all_predictions, image_hash, image_quality_score, 
            processing_time_ms, is_demo
        ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (uid, d.get("pn", ""), d.get("pf", ""), d.get("pa", 0), d.get("ps", ""),
                   d.get("pw", 0), d.get("st", ""), d.get("mt", ""), d.get("mg", ""),
                   d.get("pt", ""), d.get("t1", ""), d.get("t2", ""), d.get("nt", ""),
                   d.get("label", "Negative"), d.get("conf", 0), d.get("risk", "none"),
                   d.get("rel", 0), json.dumps(d.get("preds", {})), d.get("hash", ""),
                   d.get("quality", 0), d.get("proc_time", 0), d.get("demo", 0)))
        return c.execute("SELECT last_insert_rowid()").fetchone()[0]

def db_analyses(uid=None, lim=500):
    """Get analyses with optional filtering"""
    with get_db() as c:
        if uid:
            q = """SELECT a.*, u.full_name as analyst FROM analyses a 
                   JOIN users u ON a.user_id=u.id 
                   WHERE a.user_id=? ORDER BY a.analysis_date DESC LIMIT ?"""
            rows = c.execute(q, (uid, lim)).fetchall()
        else:
            q = """SELECT a.*, u.full_name as analyst FROM analyses a 
                   JOIN users u ON a.user_id=u.id 
                   ORDER BY a.analysis_date DESC LIMIT ?"""
            rows = c.execute(q, (lim,)).fetchall()
        return [dict(r) for r in rows]

def db_stats(uid=None):
    """Get statistics - ENHANCED"""
    with get_db() as c:
        w = "WHERE user_id=?" if uid else ""
        p = (uid,) if uid else ()
        
        tot = c.execute(f"SELECT COUNT(*) FROM analyses {w}", p).fetchone()[0]
        
        if uid:
            rel = c.execute("SELECT COUNT(*) FROM analyses WHERE user_id=? AND is_reliable=1", (uid,)).fetchone()[0]
        else:
            rel = c.execute("SELECT COUNT(*) FROM analyses WHERE is_reliable=1").fetchone()[0]
        
        para = c.execute(f"""SELECT parasite_detected, COUNT(*) as n 
                            FROM analyses {w} 
                            GROUP BY parasite_detected ORDER BY n DESC""", p).fetchall()
        
        avg = c.execute(f"SELECT AVG(confidence) FROM analyses {w}", p).fetchone()[0] or 0
        
        # ✅ NEW: Average processing time
        avg_time = c.execute(f"SELECT AVG(processing_time_ms) FROM analyses {w}", p).fetchone()[0] or 0
        
        return {
            "total": tot,
            "reliable": rel,
            "verify": tot - rel,
            "parasites": [dict(x) for x in para],
            "avg": round(avg, 1),
            "avg_time_ms": round(avg_time, 0),
            "top": para[0]["parasite_detected"] if para else "N/A"
        }

def db_trends(days=30):
    """Get analysis trends"""
    with get_db() as c:
        return [dict(r) for r in c.execute("""
            SELECT DATE(analysis_date) as day, parasite_detected, 
                   COUNT(*) as count, AVG(confidence) as avg_conf
            FROM analyses 
            WHERE analysis_date >= date('now', ?) 
            GROUP BY day, parasite_detected 
            ORDER BY day
        """, (f"-{days} days",)).fetchall()]

def db_log(uid, uname, action, details="", ip=""):
    """Activity logging - ENHANCED"""
    try:
        with get_db() as c:
            c.execute("""INSERT INTO activity_log(user_id, username, action, details, ip_address) 
                         VALUES(?,?,?,?,?)""", (uid, uname, action, details, ip))
    except Exception:
        pass

def db_logs(lim=300):
    """Get activity logs"""
    with get_db() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (lim,)
        ).fetchall()]

def db_quiz_save(uid, un, sc, tot, pct, cat="general", time_sec=0):
    """Save quiz score - ENHANCED"""
    with get_db() as c:
        c.execute("""INSERT INTO quiz_scores(user_id, username, score, total_questions, 
                     percentage, category, time_seconds) VALUES(?,?,?,?,?,?,?)""",
                  (uid, un, sc, tot, pct, cat, time_sec))

def db_leaderboard(lim=20):
    """Get quiz leaderboard"""
    with get_db() as c:
        return [dict(r) for r in c.execute("""
            SELECT username, score, total_questions, percentage, category, time_seconds, timestamp 
            FROM quiz_scores 
            ORDER BY percentage DESC, time_seconds ASC, timestamp ASC 
            LIMIT ?
        """, (lim,)).fetchall()]

def db_validate(aid, who):
    """Validate analysis"""
    with get_db() as c:
        c.execute("""UPDATE analyses SET validated=1, validated_by=?, validation_date=? 
                     WHERE id=?""", (who, datetime.now().isoformat(), aid))

def db_chat_save(uid, un, msg, resp):
    """Save chat interaction - NEW"""
    try:
        with get_db() as c:
            c.execute("""INSERT INTO chat_history(user_id, username, message, response) 
                         VALUES(?,?,?,?)""", (uid, un, msg, resp))
    except Exception:
        pass

# Initialize database
init_database()
# ============================================
#  UTILITY FUNCTIONS - ENHANCED
# ============================================
def has_role(lvl):
    """Check user role level"""
    return ROLES.get(st.session_state.get("user_role", "viewer"), {}).get("level", 0) >= lvl

def risk_color(lv):
    """Get color for risk level"""
    return {
        "critical": "#ff0040", "high": "#ff3366",
        "medium": "#ff9500", "low": "#00e676",
        "none": "#00ff88"
    }.get(lv, "#888")

def risk_pct(lv):
    """Get percentage for risk level"""
    return {
        "critical": 100, "high": 80,
        "medium": 50, "low": 25,
        "none": 0
    }.get(lv, 0)

def get_client_ip():
    """Get client IP address"""
    try:
        return st.experimental_connection_info().client.ip
    except:
        return "unknown"

# ============================================
#  IMAGE PROCESSING - ENHANCED
# ============================================
def safe_image_open(img_data):
    """Safely open image from various sources"""
    try:
        if isinstance(img_data, str):
            # Base64 or file path
            if img_data.startswith('data:image'):
                # Base64 data URL
                header, encoded = img_data.split(",", 1)
                binary = base64.b64decode(encoded)
                return Image.open(io.BytesIO(binary))
            else:
                # File path
                return Image.open(img_data)
        elif hasattr(img_data, 'read'):
            # File-like object
            return Image.open(img_data)
        elif isinstance(img_data, bytes):
            # Raw bytes
            return Image.open(io.BytesIO(img_data))
        else:
            # PIL Image
            return img_data
    except Exception as e:
        st.error(f"Error opening image: {e}")
        return None

def resize_image(img, max_size=(1200, 1200)):
    """Resize image while maintaining aspect ratio"""
    if img is None:
        return None

    try:
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if too large
        if max(img.size) > max(max_size):
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return img
    except Exception as e:
        st.error(f"Error resizing image: {e}")
        return None

def gen_heatmap(img, seed=None):
    """Generate AI heatmap overlay - ENHANCED"""
    if img is None:
        return None

    try:
        im = img.copy().convert("RGB")
        w, h = im.size

        # Generate seed if none
        if seed is None:
            seed = hash(im.tobytes()[:1000]) % 1000000

        rng = random.Random(seed)

        # Edge detection
        ea = np.array(ImageOps.grayscale(im).filter(ImageFilter.FIND_EDGES))

        # Find most interesting region
        bs, mx, bx, by = 32, 0, w // 2, h // 2
        for y in range(0, h - bs, bs // 2):
            for x in range(0, w - bs, bs // 2):
                s = np.mean(ea[y:y + bs, x:x + bs])
                if s > mx:
                    mx, bx, by = s, x + bs // 2, y + bs // 2

        # Add some randomness
        bx = max(50, min(w - 50, bx + rng.randint(-w // 10, w // 10)))
        by = max(50, min(h - 50, by + rng.randint(-h // 10, h // 10)))

        # Create heatmap overlay
        hm = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(hm)
        mr = min(w, h) // 3

        # Draw concentric circles with gradient
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

    except Exception as e:
        st.error(f"Error generating heatmap: {e}")
        return img

def thermal_filter(img):
    """Thermal camera effect"""
    if img is None:
        return None

    try:
        return ImageOps.colorize(
            ImageOps.grayscale(ImageEnhance.Contrast(img).enhance(1.5)).filter(ImageFilter.GaussianBlur(1)),
            black="navy", white="yellow", mid="red")
    except Exception as e:
        st.error(f"Error applying thermal filter: {e}")
        return img

def edges_filter(img):
    """Edge detection filter"""
    if img is None:
        return None

    try:
        return ImageOps.grayscale(img).filter(ImageFilter.FIND_EDGES)
    except Exception as e:
        st.error(f"Error applying edges filter: {e}")
        return img

def enhanced_filter(img):
    """Enhanced contrast and sharpness"""
    if img is None:
        return None

    try:
        return ImageEnhance.Contrast(ImageEnhance.Sharpness(img).enhance(2.0)).enhance(2.0)
    except Exception as e:
        st.error(f"Error applying enhanced filter: {e}")
        return img

def negative_filter(img):
    """Negative/Invert filter"""
    if img is None:
        return None

    try:
        return ImageOps.invert(img.convert("RGB"))
    except Exception as e:
        st.error(f"Error applying negative filter: {e}")
        return img

def emboss_filter(img):
    """Emboss filter"""
    if img is None:
        return None

    try:
        return img.filter(ImageFilter.EMBOSS)
    except Exception as e:
        st.error(f"Error applying emboss filter: {e}")
        return img

def adjust_image(img, br=1.0, co=1.0, sa=1.0):
    """Adjust brightness, contrast, saturation"""
    if img is None:
        return None

    try:
        r = img.copy()
        if br != 1.0:
            r = ImageEnhance.Brightness(r).enhance(br)
        if co != 1.0:
            r = ImageEnhance.Contrast(r).enhance(co)
        if sa != 1.0:
            r = ImageEnhance.Color(r).enhance(sa)
        return r
    except Exception as e:
        st.error(f"Error adjusting image: {e}")
        return img

def zoom_img(img, lv):
    """Zoom image with center crop"""
    if img is None or lv <= 1.0:
        return img

    try:
        w, h = img.size
        nw, nh = int(w / lv), int(h / lv)
        l, tp = (w - nw) // 2, (h - nh) // 2
        return img.crop((l, tp, l + nw, tp + nh)).resize((w, h), Image.Resampling.LANCZOS)
    except Exception as e:
        st.error(f"Error zooming image: {e}")
        return img

def compare_imgs(i1, i2):
    """Compare two images with multiple metrics"""
    if i1 is None or i2 is None:
        return {"mse": 0, "ssim": 0, "sim": 0}

    try:
        # Resize to same dimensions
        i1 = i1.resize((256, 256))
        i2 = i2.resize((256, 256))

        a1 = np.array(i1.convert("RGB")).astype(float)
        a2 = np.array(i2.convert("RGB")).astype(float)

        # Mean Squared Error
        mse = np.mean((a1 - a2) ** 2)

        # Structural Similarity Index
        m1, m2 = np.mean(a1), np.mean(a2)
        s1, s2 = np.std(a1), np.std(a2)
        s12 = np.mean((a1 - m1) * (a2 - m2))
        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
        ssim = ((2 * m1 * m2 + c1) * (2 * s12 + c2)) / ((m1 ** 2 + m2 ** 2 + c1) * (s1 ** 2 + s2 ** 2 + c2))

        return {
            "mse": round(mse, 2),
            "ssim": round(float(ssim), 4),
            "sim": round(float(ssim) * 100, 1)
        }
    except Exception as e:
        st.error(f"Error comparing images: {e}")
        return {"mse": 0, "ssim": 0, "sim": 0}

def pixel_diff(i1, i2):
    """Generate pixel difference image"""
    if i1 is None or i2 is None:
        return None

    try:
        a1 = np.array(i1.convert("RGB").resize((256, 256))).astype(float)
        a2 = np.array(i2.convert("RGB").resize((256, 256))).astype(float)
        diff = np.abs(a1 - a2).astype(np.uint8)
        diff = np.clip(diff * 3, 0, 255).astype(np.uint8)
        return Image.fromarray(diff)
    except Exception as e:
        st.error(f"Error generating pixel difference: {e}")
        return None

def histogram(img):
    """Generate image histogram data"""
    if img is None:
        return {"red": [], "green": [], "blue": []}

    try:
        r, g, b = img.convert("RGB").split()
        return {
            "red": list(r.histogram()),
            "green": list(g.histogram()),
            "blue": list(b.histogram())
        }
    except Exception as e:
        st.error(f"Error generating histogram: {e}")
        return {"red": [], "green": [], "blue": []}

# ============================================
#  VOICE SYSTEM - FIXED FOR STREAMLIT
# ============================================
def render_voice_player():
    """Render voice player using HTML5 Audio"""
    if not st.session_state.get("voice_text"):
        return

    text = st.session_state.voice_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ').replace('\r', ' ')
    lang_code = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(
        st.session_state.get("voice_lang", st.session_state.get("lang", "fr")), "fr-FR")

    # ✅ NEW: Use HTML5 Audio with Web Speech API fallback
    html_code = f"""
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
        <audio id="voiceAudio" style="display: none;"></audio>
        <button id="playBtn" onclick="playVoice()" style="
            background: linear-gradient(135deg, #00f5ff, #0066ff);
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,245,255,0.3);
            transition: all 0.3s ease;
        ">🔊</button>
        <button id="stopBtn" onclick="stopVoice()" style="
            background: #ff0040;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(255,0,64,0.3);
            transition: all 0.3s ease;
            display: none;
        ">🛑</button>
    </div>

    <script>
        let utterance = null;
        let audio = document.getElementById('voiceAudio');

        function playVoice() {{
            document.getElementById('playBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'block';

            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();

                utterance = new SpeechSynthesisUtterance(`{text}`);
                utterance.lang = '{lang_code}';
                utterance.rate = 0.9;
                utterance.pitch = 1.0;
                utterance.volume = 1.0;

                // Set voice if available
                const voices = window.speechSynthesis.getVoices();
                if (voices.length > 0) {{
                    const voice = voices.find(v => v.lang.startsWith('{lang_code.split("-")[0]}'));
                    if (voice) utterance.voice = voice;
                }}

                utterance.onend = function() {{
                    document.getElementById('playBtn').style.display = 'block';
                    document.getElementById('stopBtn').style.display = 'none';
                }};

                window.speechSynthesis.speak(utterance);
            }} else {{
                // Fallback to HTML5 Audio (for mobile)
                try {{
                    const blob = new Blob([new TextEncoder().encode(`{text}`)], {{type: 'audio/mpeg'}});
                    const url = URL.createObjectURL(blob);
                    audio.src = url;
                    audio.play();
                    audio.onended = function() {{
                        document.getElementById('playBtn').style.display = 'block';
                        document.getElementById('stopBtn').style.display = 'none';
                    }};
                }} catch(e) {{
                    alert('Voice not supported on this device');
                    document.getElementById('playBtn').style.display = 'block';
                    document.getElementById('stopBtn').style.display = 'none';
                }}
            }}
        }}

        function stopVoice() {{
            document.getElementById('playBtn').style.display = 'block';
            document.getElementById('stopBtn').style.display = 'none';

            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
            }} else {{
                audio.pause();
                audio.currentTime = 0;
            }}
        }}
    </script>
    """

    components.html(html_code, height=0)
    st.session_state.voice_text = None
    st.session_state.voice_lang = None

def speak(text, lang=None):
    """Queue text for speaking"""
    st.session_state.voice_text = text
    st.session_state.voice_lang = lang or st.session_state.get("lang", "fr")
    st.rerun()

def stop_speech():
    """Stop speech"""
    st.session_state.voice_text = None
    st.session_state.voice_lang = None
    st.rerun()

# ============================================
#  AI ENGINE - ENHANCED
# ============================================
@st.cache_resource(show_spinner=False)
def load_model():
    """Load AI model with enhanced error handling"""
    m, mn, mt = None, None, None
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model

        # Check for different model formats
        for ext in [".keras", ".h5"]:
            ff = [f for f in os.listdir(".") if f.endswith(ext) and os.path.isfile(f)]
            if ff:
                mn = ff[0]
                m = load_model(mn, compile=False)
                mt = "keras"
                break

        if m is None:
            ff = [f for f in os.listdir(".") if f.endswith(".tflite") and os.path.isfile(f)]
            if ff:
                mn = ff[0]
                from tensorflow.lite.python.interpreter import Interpreter
                m = Interpreter(model_path=mn)
                m.allocate_tensors()
                mt = "tflite"

        # Test model with dummy input
        if m and mt == "keras":
            test_input = np.zeros((1, *MODEL_INPUT_SIZE, 3), dtype=np.float32)
            m.predict(test_input, verbose=0)

    except Exception as e:
        st.warning(f"⚠️ Model loading error: {e}")

    return m, mn, mt

def predict(model, mt, img, seed=None):
    """Run prediction with enhanced error handling"""
    res = {
        "label": "Negative",
        "conf": 0,
        "preds": {},
        "rel": False,
        "demo": False,
        "risk": "none",
        "proc_time": 0
    }

    rm = {
        "Plasmodium": "critical", "Amoeba (E. histolytica)": "high",
        "Leishmania": "high", "Trypanosoma": "high",
        "Giardia": "medium", "Schistosoma": "medium",
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
            ap[c] = float(cf) if c == lb else round(rng.uniform(0, rem / max(1, len(CLASS_NAMES) - 1)), 1)
        res.update({
            "label": lb,
            "conf": cf,
            "preds": ap,
            "rel": cf >= CONFIDENCE_THRESHOLD,
            "risk": rm.get(lb, "none"),
            "proc_time": rng.randint(500, 2000)
        })
        return res

    try:
        import tensorflow as tf
        start_time = time.time()

        # Preprocess image
        im = ImageOps.fit(img.convert("RGB"), MODEL_INPUT_SIZE, Image.Resampling.LANCZOS)
        arr = np.expand_dims(np.asarray(im).astype(np.float32) / 127.5 - 1.0, 0)

        # Run prediction
        if mt == "tflite":
            inp, out = model.get_input_details(), model.get_output_details()
            model.set_tensor(inp[0]['index'], arr)
            model.invoke()
            pr = model.get_tensor(out[0]['index'])[0]
        else:
            pr = model.predict(arr, verbose=0)[0]

        # Process results
        ix = int(np.argmax(pr))
        cf = int(pr[ix] * 100)
        lb = CLASS_NAMES[ix] if ix < len(CLASS_NAMES) else "Negative"
        ap = {CLASS_NAMES[i]: round(float(pr[i]) * 100, 1) for i in range(min(len(pr), len(CLASS_NAMES)))}

        res.update({
            "label": lb,
            "conf": cf,
            "preds": ap,
            "rel": cf >= CONFIDENCE_THRESHOLD,
            "risk": rm.get(lb, "none"),
            "proc_time": int((time.time() - start_time) * 1000)
        })

    except Exception as e:
        st.error(f"Prediction error: {e}")
        res["demo"] = True

    return res

# ============================================
#  PDF GENERATION - ENHANCED
# ============================================
class PDF(FPDF):
    """Enhanced PDF with Arabic support"""
    def __init__(self, lang="fr"):
        super().__init__()
        self.lang = lang
        self.set_auto_page_break(True, 25)
        self.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
        self.add_font('DejaVu', 'B', 'fonts/DejaVuSansCondensed-Bold.ttf', uni=True)
        self.add_font('Amiri', '', 'fonts/Amiri-Regular.ttf', uni=True)
        self.add_font('Amiri', 'B', 'fonts/Amiri-Bold.ttf', uni=True)

    def header(self):
        """Enhanced header with gradient"""
        # Gradient background
        self.set_fill_color(0, 20, 60)
        self.rect(0, 0, 210, 4, 'F')
        self.set_fill_color(0, 180, 255)
        self.rect(0, 4, 210, 1, 'F')
        self.set_fill_color(0, 255, 136)
        self.rect(0, 5, 210, 0.5, 'F')
        self.ln(8)

        # Logo and title
        self.set_font("DejaVu", "B", 14)
        self.set_text_color(0, 60, 150)
        self.cell(0, 8, f"DM SMART LAB AI v{APP_VERSION}", 0, 0, "L")

        self.set_font("DejaVu", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, datetime.now().strftime("%d/%m/%Y %H:%M:%S"), 0, 1, "R")

        # Subtitle
        self.set_font("DejaVu", "I", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 4, "Système de Diagnostic Parasitologique par Intelligence Artificielle", 0, 1, "L")
        self.cell(0, 4, "INFSPM - Ouargla, Algérie", 0, 1, "L")

        # Line separator
        self.set_draw_color(0, 180, 255)
        self.set_line_width(0.5)
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(6)

    def footer(self):
        """Enhanced footer with warnings"""
        self.set_y(-20)
        self.set_fill_color(0, 20, 60)
        self.rect(0, 282, 210, 15, 'F')
        self.set_y(-15)
        self.set_font("DejaVu", "I", 7)
        self.set_text_color(200, 200, 200)

        # Arabic/English warning based on language
        if self.lang == "ar":
            warning = "تحذير: هذا التقرير تم إنشاؤه بواسطة ذكاء اصطناعي - يجب التحقق من قبل متخصص"
        else:
            warning = "AVERTISSEMENT: Ce rapport est généré par IA - Validation par un professionnel de santé requise"

        self.cell(0, 4, warning, 0, 1, "C")
        self.set_font("DejaVu", "", 6)
        self.cell(0, 4, f"Page {self.page_no()}/{{nb}} | DM Smart Lab AI | INFSPM Ouargla", 0, 0, "C")

    def section(self, title, color=(0, 60, 150)):
        """Enhanced section header"""
        self.set_fill_color(*color)
        self.set_text_color(255, 255, 255)

        # Use appropriate font based on language
        if self.lang == "ar":
            self.set_font("Amiri", "B", 10)
        else:
            self.set_font("DejaVu", "B", 10)

        self.cell(0, 8, f"  {title}", 0, 1, "L", True)
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def field(self, label, val):
        """Enhanced field display"""
        if self.lang == "ar":
            self.set_font("Amiri", "B", 9)
        else:
            self.set_font("DejaVu", "B", 9)

        self.set_text_color(60, 60, 60)
        self.cell(55, 6, label, 0, 0)

        if self.lang == "ar":
            self.set_font("Amiri", "", 9)
        else:
            self.set_font("DejaVu", "", 9)

        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f"  {val}", 0, 1)

    def add_separator(self):
        """Add separator line"""
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

def make_pdf(pat, lab, result, lbl, lang="fr"):
    """Generate enhanced PDF report"""
    pdf = PDF(lang)
    pdf.alias_nb_pages()
    pdf.add_page()

    # Title
    if lang == "ar":
        pdf.set_font("Amiri", "B", 18)
    else:
        pdf.set_font("DejaVu", "B", 18)

    pdf.set_text_color(0, 40, 100)
    pdf.cell(0, 12, {
        "fr": "RAPPORT D'ANALYSE PARASITOLOGIQUE",
        "ar": "تقرير تحليل طفيلي",
        "en": "PARASITOLOGICAL ANALYSIS REPORT"
    }[lang], 0, 1, "C")

    # Reference ID
    rid = hashlib.md5(f"{pat.get('Nom', '')}{datetime.now().isoformat()}".encode()).hexdigest()[:10].upper()
    pdf.set_font("DejaVu", "", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, f"Reference: DM-{rid} | Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "R")
    pdf.ln(3)

    # Patient section
    pdf.section({
        "fr": "INFORMATIONS DU PATIENT",
        "ar": "معلومات المريض",
        "en": "PATIENT INFORMATION"
    }[lang])

    for k, v in pat.items():
        if v:
            pdf.field(f"{k}:", v)
    pdf.add_separator()

    # Lab section
    pdf.section({
        "fr": "INFORMATIONS LABORATOIRE",
        "ar": "معلومات المخبر",
        "en": "LABORATORY INFORMATION"
    }[lang], (0, 100, 80))

    for k, v in lab.items():
        if v:
            pdf.field(f"{k}:", v)
    pdf.add_separator()

    # Result section
    cf = result.get("conf", 0)
    if lbl == "Negative":
        pdf.section({
            "fr": "RÉSULTAT DE L'ANALYSE IA",
            "ar": "نتيجة التحليل بالذكاء الاصطناعي",
            "en": "AI ANALYSIS RESULT"
        }[lang], (0, 150, 80))
    else:
        pdf.section({
            "fr": "RÉSULTAT DE L'ANALYSE IA",
            "ar": "نتيجة التحليل بالذكاء الاصطناعي",
            "en": "AI ANALYSIS RESULT"
        }[lang], (180, 0, 0))

    pdf.ln(2)

    # Result box
    if lbl == "Negative":
        pdf.set_fill_color(220, 255, 220)
        pdf.set_text_color(0, 100, 0)
    else:
        pdf.set_fill_color(255, 220, 220)
        pdf.set_text_color(180, 0, 0)

    if lang == "ar":
        pdf.set_font("Amiri", "B", 16)
    else:
        pdf.set_font("DejaVu", "B", 16)

    pdf.cell(0, 12, f"  {lbl} - {cf}%", 1, 1, "C", True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # Parasite details
    info = PARASITE_DB.get(lbl, PARASITE_DB["Negative"])

    if lang == "ar":
        pdf.set_font("Amiri", "B", 9)
    else:
        pdf.set_font("DejaVu", "B", 9)

    pdf.cell(0, 6, {
        "fr": "Nom Scientifique:",
        "ar": "الاسم العلمي:",
        "en": "Scientific Name:"
    }[lang], 0, 0)

    if lang == "ar":
        pdf.set_font("Amiri", "I", 9)
    else:
        pdf.set_font("DejaVu", "I", 9)

    pdf.cell(0, 6, f"  {info.get('sci', 'N/A')}", 0, 1)

    pdf.ln(2)

    if lang == "ar":
        pdf.set_font("Amiri", "B", 9)
    else:
        pdf.set_font("DejaVu", "B", 9)

    pdf.cell(0, 6, {
        "fr": "Morphologie:",
        "ar": "المورفولوجيا:",
        "en": "Morphology:"
    }[lang], 0, 1)

    if lang == "ar":
        pdf.set_font("Amiri", "", 8)
    else:
        pdf.set_font("DejaVu", "", 8)

    pdf.multi_cell(0, 5, info['morph'].get(lang, info['morph'].get('fr', '')))

    pdf.ln(2)

    if lang == "ar":
        pdf.set_font("Amiri", "B", 9)
    else:
        pdf.set_font("DejaVu", "B", 9)

    pdf.cell(0, 6, {
        "fr": "Description:",
        "ar": "الوصف:",
        "en": "Description:"
    }[lang], 0, 1)

    if lang == "ar":
        pdf.set_font("Amiri", "", 8)
    else:
        pdf.set_font("DejaVu", "", 8)

    pdf.multi_cell(0, 5, info['desc'].get(lang, info['desc'].get('fr', '')))

    pdf.ln(2)

    if lang == "ar":
        pdf.set_font("Amiri", "B", 9)
    else:
        pdf.set_font("DejaVu", "B", 9)

    pdf.set_text_color(0, 100, 0)
    pdf.cell(0, 6, {
        "fr": "Conseil Médical:",
        "ar": "النصيحة الطبية:",
        "en": "Medical Advice:"
    }[lang], 0, 1)

    if lang == "ar":
        pdf.set_font("Amiri", "", 8)
    else:
        pdf.set_font("DejaVu", "", 8)

    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 5, info['advice'].get(lang, info['advice'].get('fr', '')))

    # Tests
    if info.get("tests"):
        pdf.ln(2)
        if lang == "ar":
            pdf.set_font("Amiri", "B", 9)
        else:
            pdf.set_font("DejaVu", "B", 9)

        pdf.cell(0, 6, {
            "fr": "Examens Complementaires Suggérés:",
            "ar": "الفحوصات الإضافية المقترحة:",
            "en": "Suggested Additional Tests:"
        }[lang], 0, 1)

        if lang == "ar":
            pdf.set_font("Amiri", "", 8)
        else:
            pdf.set_font("DejaVu", "", 8)

        for test in info["tests"]:
            pdf.cell(10, 5, "", 0, 0)
            pdf.cell(0, 5, f"- {test}", 0, 1)

    # Reliability indicator
    pdf.ln(3)
    pdf.add_separator()

    rel_text = {
        "fr": "FIABLE" if result.get("rel", False) else "À VÉRIFIER",
        "ar": "موثوق" if result.get("rel", False) else "للتحقق",
        "en": "RELIABLE" if result.get("rel", False) else "TO VERIFY"
    }[lang]

    rel_color = (0, 150, 0) if result.get("rel", False) else (200, 100, 0)

    if lang == "ar":
        pdf.set_font("Amiri", "B", 10)
    else:
        pdf.set_font("DejaVu", "B", 10)

    pdf.set_text_color(*rel_color)
pdf.cell(
    0, 8,
    {
        'fr': 'Fiabilité: {0} ({1}%)',
        'ar': 'موثوقية: {0} ({1}%)',
        'en': 'Reliability: {0} ({1}%)'
    }[lang].format(rel_text, cf),
    0, 1, "C"
)

pdf.set_text_color(0, 0, 0)
    # QR Code
    if HAS_QRCODE:
        try:
            qr = qrcode.QRCode(box_size=3, border=1)
            qr.add_data(f"DM-SmartLab|{lbl}|{cf}%|{rid}|{datetime.now().isoformat()}")
            qr.make(fit=True)
            qp = f"_qr_{rid}.png"
            qr.make_image().save(qp)
            pdf.image(qp, x=170, y=pdf.get_y() - 30, w=28)
            try:
                os.remove(qp)
            except:
                pass
        except:
            pass

    # Signatures section
    pdf.ln(8)
    pdf.section({
        "fr": "SIGNATURES ET VALIDATION",
        "ar": "التوقيعات والمصادقة",
        "en": "SIGNATURES & VALIDATION"
    }[lang], (80, 80, 80))

    pdf.ln(5)
    if lang == "ar":
        pdf.set_font("Amiri", "", 9)
    else:
        pdf.set_font("DejaVu", "", 9)

    pdf.cell(95, 5, {
        "fr": "Technicien 1: ___________________",
        "ar": "التقني 1: ___________________",
        "en": "Technician 1: ___________________"
    }[lang], 0, 0)

    pdf.cell(95, 5, {
        "fr": "Technicien 2: ___________________",
        "ar": "التقني 2: ___________________",
        "en": "Technician 2: ___________________"
    }[lang], 0, 1)

    pdf.ln(8)
    pdf.cell(95, 5, {
        "fr": "Date: ___/___/______",
        "ar": "التاريخ: ___/___/______",
        "en": "Date: ___/___/______"
    }[lang], 0, 0)

    pdf.cell(95, 5, {
        "fr": "Cachet du Laboratoire:",
        "ar": "ختم المخبر:",
        "en": "Lab Seal:"
    }[lang], 0, 1)

    pdf.ln(10)
    pdf.cell(0, 5, {
        "fr": "Validation Biologiste: ___________________",
        "ar": "مصادقة أخصائي: ___________________",
        "en": "Biologist Validation: ___________________"
    }[lang], 0, 1)

    return bytes(pdf.output())

# ============================================
#  CSS - ENHANCED SPACE THEME
# ============================================
def apply_css():
    """Apply enhanced CSS theme"""
    rtl = st.session_state.get("lang") == "ar"
    d = "rtl" if rtl else "ltr"

    # Space dark theme
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

    # ✅ NEW: Enhanced CSS with better RTL support
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
            radial-gradient(1px 1px at 200px 60px, rgba(0,255,136,0.2), transparent),
            radial-gradient(2px 2px at 60px 100px, rgba(0,102,255,0.2), transparent),
            radial-gradient(1px 1px at 180px 120px, rgba(255,105,180,0.15), transparent);
        background-size: 250px 150px;
        animation: sparkle 8s linear infinite;
    }}

    @keyframes sparkle {{
        0% {{ background-position: 0 0; }}
        100% {{ background-position: 250px 150px; }}
    }}

    /* ====== FLOATING PARTICLES OVERLAY ====== */
    .stApp::before {{
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
        background:
            radial-gradient(circle at 15% 25%, rgba(0,245,255,0.03) 0%, transparent 50%),
            radial-gradient(circle at 85% 75%, rgba(255,0,255,0.03) 0%, transparent 50%),
            radial-gradient(circle at 50% 50%, rgba(0,255,136,0.02) 0%, transparent 50%);
        animation: nebula 20s ease-in-out infinite;
    }}

    @keyframes nebula {{
        0%, 100% {{ opacity: 0.5; }}
        50% {{ opacity: 1; }}
    }}

    /* ====== SIDEBAR ====== */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {sbg} 0%, rgba(5,10,30,0.98) 100%) !important;
        border-right: 1px solid rgba(0,245,255,0.1) !important;
        width: 320px !important;
    }}

    section[data-testid="stSidebar"] * {{ color: {tx} !important; }}

    /* ====== TEXT COLORS ====== */
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
        padding: 12px !important;
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
        padding: 8px !important;
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

    .dm-card-cyan {{ border-left: 3px solid {pr}; }}
    .dm-card-green {{ border-left: 3px solid {ac2}; }}
    .dm-card-red {{ border-left: 3px solid #ff0040; }}
    .dm-card-purple {{ border-left: 3px solid #9933ff; }}

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
        height: 48px !important;
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

    div.stButton > button * {{ color: white !important; }}

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

    /* ====== CHAT BUBBLES ====== */
    .dm-ch {{
        padding: 14px 18px;
        border-radius: 18px;
        margin: 8px 0;
        max-width: 85%;
        font-size: .9rem;
        line-height: 1.6;
        animation: fadeInUp 0.3s ease;
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .dm-cu {{
        background: linear-gradient(135deg, #0066ff, #0044cc) !important;
        color: white !important;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }}

    .dm-cu * {{ color: white !important; -webkit-text-fill-color: white !important; }}

    .dm-cb {{
        background: {cbg};
        border: 1px solid {brd};
        border-bottom-left-radius: 4px;
    }}

    /* ====== HEADINGS ====== */
    h1 {{ font-family: 'Orbitron', sans-serif !important; }}

    /* ====== RTL Support ====== */
    {"body, p, span, div, label { font-family: 'Tajawal', sans-serif !important; }" if rtl else ""}

    /* ====== LOGO CONTAINER ====== */
    .dm-logo {{
        text-align: center;
        padding: 16px;
        background: linear-gradient(135deg, rgba(0,245,255,0.05), rgba(255,0,255,0.05));
        border-radius: 24px;
        border: 1px solid {brd};
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }}

    .dm-logo::after {{
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(from 0deg, transparent, rgba(0,245,255,0.05), transparent, rgba(255,0,255,0.05), transparent);
        animation: logo-rotate 10s linear infinite;
    }}

    @keyframes logo-rotate {{
        100% {{ transform: rotate(360deg); }}
    }}

    /* ====== EXPANDER ====== */
    .streamlit-expanderHeader {{
        background: rgba(10,15,46,0.5) !important;
        border-radius: 12px !important;
        border: 1px solid {brd} !important;
        padding: 12px !important;
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
        padding: 10px 16px !important;
        font-weight: 600 !important;
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(0,245,255,0.2), rgba(0,102,255,0.2)) !important;
    }}

    /* ====== PROGRESS BAR ====== */
    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, {pr}, {ac}, {ac2}) !important;
        border-radius: 10px !important;
        animation: progress-glow 2s ease infinite;
    }}

    @keyframes progress-glow {{
        0%, 100% {{ box-shadow: 0 0 5px rgba(0,245,255,0.3); }}
        50% {{ box-shadow: 0 0 15px rgba(0,245,255,0.5); }}
    }}

    /* ====== DATAFRAME ====== */
    .stDataFrame {{
        border-radius: 14px !important;
        overflow: hidden !important;
        background: {cbg} !important;
        border: 1px solid {brd} !important;
    }}

    /* ====== RADIO ====== */
    .stRadio > div {{
        gap: 4px;
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

    /* ====== FILE UPLOADER ====== */
    .stFileUploader > div > div > div > div {{
        background: {ibg} !important;
        border: 1px solid {brd} !important;
        border-radius: 12px !important;
    }}

    /* ====== CAMERA INPUT ====== */
    .stCameraInput > div > div > div > div {{
        background: {ibg} !important;
        border: 1px solid {brd} !important;
        border-radius: 12px !important;
    }}

    /* ====== DOWNLOAD BUTTON ====== */
    .stDownloadButton > button {{
        background: linear-gradient(135deg, #00f5ff, #0066ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
    }}

    /* ====== FORM SUBMIT BUTTON ====== */
    .stForm > form > div > button {{
        background: linear-gradient(135deg, #00f5ff, #0066ff) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        height: 48px !important;
    }}

    /* ====== ALERT BOXES ====== */
    .stAlert {{
        border-radius: 12px !important;
        padding: 16px !important;
    }}

    /* ====== CODE BLOCKS ====== */
    .stCodeBlock {{
        background: {cbg} !important;
        border: 1px solid {brd} !important;
        border-radius: 12px !important;
    }}

    /* ====== MARKDOWN ====== */
    .stMarkdown {{
        line-height: 1.7 !important;
    }}

    /* ====== CAPTION ====== */
    .stCaption {{
        color: {mu} !important;
        font-size: 0.8rem !important;
    }}

    /* ====== DIVIDER ====== */
    hr {{
        border: none !important;
        border-top: 1px solid {brd} !important;
        margin: 20px 0 !important;
    }}

    /* ====== EMPTY CONTAINER ====== */
    .empty {{
        display: none !important;
    }}

    /* ====== HIDDEN ELEMENTS ====== */
    .stHidden {{
        display: none !important;
    }}

    /* ====== FULL WIDTH ELEMENTS ====== */
    .stFullWidth {{
        width: 100% !important;
    }}

    </style>""", unsafe_allow_html=True)

    # ✅ NEW: Return plotly template name
    return "plotly_dark" if HAS_PLOTLY else "default"

# ============================================
#  ANIMATED LOGO - ENHANCED
# ============================================
def render_logo():
    """Render enhanced animated logo"""
    st.markdown("""<div class="dm-logo">
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
        <filter id="gl">
            <feGaussianBlur stdDeviation="2" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
        </filter>
        <filter id="gl2">
            <feGaussianBlur stdDeviation="1" result="b"/>
            <feComposite in="SourceGraphic" in2="b" operator="over"/>
        </filter>
    </defs>

    <!-- Outer circle with animation -->
    <circle cx="50" cy="50" r="45" fill="none" stroke="url(#g1)" stroke-width="2.5" filter="url(#gl)" opacity=".8">
        <animateTransform attributeName="transform" type="rotate" values="0 50 50;360 50 50" dur="20s" repeatCount="indefinite"/>
    </circle>

    <!-- Inner circle -->
    <circle cx="50" cy="50" r="38" fill="none" stroke="url(#g1)" stroke-width="1" opacity=".3">
        <animateTransform attributeName="transform" type="rotate" values="360 50 50;0 50 50" dur="15s" repeatCount="indefinite"/>
    </circle>

    <!-- Static circle -->
    <circle cx="50" cy="50" r="30" fill="none" stroke="url(#g1)" stroke-width="0.5" opacity=".2"/>

    <!-- Text -->
    <text x="50" y="42" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="14" font-weight="900" fill="url(#g1)" filter="url(#gl2)">DM</text>
    <text x="50" y="58" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="8" font-weight="600" fill="url(#g1)">SMART LAB</text>
    <text x="50" y="68" text-anchor="middle" font-family="Orbitron,sans-serif" font-size="7" font-weight="400" fill="#00f5ff" opacity=".6">AI</text>

    <!-- DNA helix dots with animation -->
    <circle cx="25" cy="35" r="2" fill="#00f5ff" opacity=".4">
        <animate attributeName="cy" values="35;65;35" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="75" cy="65" r="2" fill="#ff00ff" opacity=".4">
        <animate attributeName="cy" values="65;35;65" dur="3s" repeatCount="indefinite"/>
    </circle>
    <circle cx="30" cy="50" r="1.5" fill="#00ff88" opacity=".3">
        <animate attributeName="cx" values="30;70;30" dur="4s" repeatCount="indefinite"/>
    </circle>

    <!-- Additional particles -->
    <circle cx="40" cy="20" r="1" fill="#ff9500" opacity=".2">
        <animate attributeName="cx" values="40;60;40" dur="5s" repeatCount="indefinite"/>
        <animate attributeName="cy" values="20;40;20" dur="7s" repeatCount="indefinite"/>
    </circle>
    <circle cx="60" cy="80" r="1" fill="#9933ff" opacity=".2">
        <animate attributeName="cx" values="60;40;60" dur="6s" repeatCount="indefinite"/>
        <animate attributeName="cy" values="80;60;80" dur="4s" repeatCount="indefinite"/>
    </circle>
    </svg>

    <h3 style="font-family:Orbitron,sans-serif;margin:6px 0;background:linear-gradient(135deg,#00f5ff,#ff00ff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:1.1rem;position:relative;z-index:1;">
        DM SMART LAB AI
    </h3>
    <p style="font-size:.55rem;opacity:.35;letter-spacing:.35em;text-transform:uppercase;margin:0;position:relative;z-index:1;">
        v{APP_VERSION} - Space Enhanced Edition
    </p>
    </div>""", unsafe_allow_html=True)

# ============================================
#  SIDEBAR - ENHANCED
# ============================================
def render_sidebar():
    """Render enhanced sidebar with user info and navigation"""
    with st.sidebar:
        # Logo
        render_logo()

        # User info
        if st.session_state.logged_in:
            ri = ROLES.get(st.session_state.user_role, ROLES["viewer"])
            st.markdown(f"""
            <div class='dm-card dm-card-cyan' style='text-align:center;'>
                <h4 style='margin:0;color:{NEON["cyan"]}!important;'>
                    {ri['icon']} {st.session_state.user_full_name}
                </h4>
                <p style='margin:0;opacity:.6;font-size:.8rem;'>
                    @{st.session_state.user_name} | {tl(ri['label'])}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Daily tip
            tips = TIPS.get(st.session_state.lang, TIPS["fr"])
            st.markdown(f"""
            <div class='dm-card' style='background:rgba(0,255,136,.06);'>
                <p style='margin:0;opacity:.8;'>
                    <b>💡 {t('daily_tip')}:</b><br>
                    {tips[datetime.now().timetuple().tm_yday % len(tips)]}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")

            # Language selector
            st.markdown(f"<p style='margin:0;opacity:.6;'>{t('language')}</p>", unsafe_allow_html=True)
            lc = st.radio("lang_select", ["FR Francais", "AR العربية", "EN English"],
                         label_visibility="collapsed",
                         index=["fr", "ar", "en"].index(st.session_state.lang),
                         horizontal=True)

            nl = "fr" if "FR" in lc else ("ar" if "AR" in lc else "en")
            if nl != st.session_state.lang:
                st.session_state.lang = nl
                st.rerun()

            st.markdown("---")

            # Navigation
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

            menu = st.radio("Navigation", navs, label_visibility="collapsed")

            st.markdown("---")

            # Logout button
            if st.button(f"🚪 {t('logout')}", use_container_width=True):
                db_log(st.session_state.user_id, st.session_state.user_name, "Logout")
                for k in DEFAULTS:
                    st.session_state[k] = DEFAULTS[k]
                st.rerun()

            return keys[navs.index(menu)]

        else:
            # Login form will be rendered in main page
            return "login"

# ============================================
#  LOGIN PAGE - ENHANCED
# ============================================
def render_login():
    """Render enhanced login page"""
    lc1, lc2, lc3 = st.columns([1, 2, 1])

    with lc2:
        # Language selector
        ll = st.selectbox("Language", ["FR Francais", "AR العربية", "EN English"],
                         label_visibility="collapsed")
        st.session_state.lang = "fr" if "FR" in ll else ("ar" if "AR" in ll else "en")

        # Logo
        render_logo()

        # Login card with animated border
        st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
        <div style='font-size:3.5rem;margin-bottom:10px;'>
            <span style='animation: pulse 2s ease-in-out infinite;display:inline-block;'>🔐</span>
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

        with st.form("login"):
            u = st.text_input(f"{t('username')}", placeholder="admin / dhia / demo")
            p = st.text_input(f"{t('password')}", type="password")
            if st.form_submit_button(f"{t('connect')}", use_container_width=True):
                if u.strip():
                    r = db_login(u.strip(), p)
                    if r is None:
                        st.error("❌ Utilisateur non trouvé")
                    elif isinstance(r, dict) and "error" in r:
                        if r["error"] == "locked":
                            until = datetime.fromisoformat(r["until"])
                            st.error(f"⏳ Compte verrouillé jusqu'à {until.strftime('%H:%M:%S')}")
                        else:
                            st.error(f"❌ Mot de passe incorrect. {r.get('left', 0)} tentatives restantes")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.user_id = r["id"]
                        st.session_state.user_name = r["username"]
                        st.session_state.user_role = r["role"]
                        st.session_state.user_full_name = r["full_name"]

                        # Log login with IP
                        ip = get_client_ip()
                        db_log(r["id"], r["username"], "Login", f"IP: {ip}")

                        st.rerun()

        st.markdown("""<div style='text-align:center;opacity:.3;font-size:.72rem;margin-top:16px;'>
        admin/admin2026 | dhia/dhia2026 | demo/demo123
        </div>""", unsafe_allow_html=True)

    st.stop()

# ============================================
#  MAIN APP STRUCTURE
# ============================================
def main():
    """Main application entry point"""
    # Initialize session state
    DEFAULTS = {
        "logged_in": False, "user_id": None, "user_name": "", "user_role": "viewer",
        "user_full_name": "", "lang": "fr",
        "demo_seed": None, "heatmap_seed": None,
        "quiz_state": {
            "current": 0, "score": 0, "answered": [], "active": False,
            "order": [], "wrong": [], "total_q": 0, "finished": False,
            "selected_answer": None, "show_result": False
        },
        "chat_history": [],
        "voice_text": None, "voice_lang": None,
        "current_page": "home"
    }

    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Apply CSS
    plot_template = apply_css()

    # Render voice player at top of page
    render_voice_player()

    # Check login status
    if not st.session_state.logged_in:
        render_login()

    # Get current page from sidebar
    pg = render_sidebar()

    # ============================================
    #  PAGE: HOME - ENHANCED
    # ============================================
    if pg == "home":
        st.markdown(f"""<h1 style='font-family:Orbitron,sans-serif;'>
        <span class='dm-nt'>👋 {get_greeting()}, {st.session_state.user_full_name}!</span>
        </h1>""", unsafe_allow_html=True)

        st.markdown(f"""<div class='dm-card dm-card-cyan'>
        <h2 class='dm-nt'>DM SMART LAB AI v{APP_VERSION}</h2>
        <h4 style='opacity:.6;'>{t('where_science')}</h4>
        <p style='opacity:.4;font-size:.85rem;'>{t('system_desc')}</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("---")

        w1, w2, w3 = st.columns([2, 2, 1])
        with w1:
            if st.button(f"🎙️ {t('welcome_btn')}", use_container_width=True, type="primary"):
                speak(t("voice_welcome"))
                st.rerun()
        with w2:
            if st.button(f"🤖 {t('intro_btn')}", use_container_width=True, type="primary"):
                speak(t("voice_intro"))
                st.rerun()
        with w3:
            if st.button(f"🔇 {t('stop_voice')}", use_container_width=True):
                stop_speech()

        st.markdown("---")

        # ✅ NEW: System status cards
        st.markdown(f"### 📊 {t('quick_overview')}")

        # Get system stats
        s = db_stats(st.session_state.user_id)
        users = len(db_users())
        logs = len(db_logs(1))

        metrics = [
            ("🔬", s["total"], t("total_analyses")),
            ("✅", s["reliable"], t("reliable")),
            ("⚠️", s["verify"], t("to_verify")),
            ("🦠", s["top"], t("most_frequent")),
            ("👥", users, "Utilisateurs"),
            ("📜", logs, "Activités"),
            ("⏱️", f"{s['avg_time_ms']}ms", "Temps moyen"),
        ]

        cols = st.columns(4)
        for i, (ic, v, lb) in enumerate(metrics):
            with cols[i % 4]:
                st.markdown(f"""<div class='dm-m'>
                <span class='dm-m-i'>{ic}</span>
                <div class='dm-m-v'>{v}</div>
                <div class='dm-m-l'>{lb}</div>
                </div>""", unsafe_allow_html=True)

        # ✅ NEW: Recent activity
        st.markdown("---")
        st.markdown(f"### 📜 Activité récente")

        recent_logs = db_logs(5)
        if recent_logs:
            for log in recent_logs[:5]:
                st.markdown(f"""
                <div class='dm-card' style='padding:12px;margin:4px 0;'>
                    <p style='margin:0;opacity:.8;'>
                        <b>{log['username']}</b> {log['action']} • {log['timestamp']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune activité récente")

        # ✅ NEW: Quick access buttons
        st.markdown("---")
        st.markdown(f"### ⚡ Accès rapide")

        qa_cols = st.columns(4)
        with qa_cols[0]:
            if st.button("🔬 Nouvelle Analyse", use_container_width=True):
                st.session_state.current_page = "scan"
                st.rerun()
        with qa_cols[1]:
            if st.button("📊 Tableau de Bord", use_container_width=True):
                st.session_state.current_page = "dash"
                st.rerun()
        with qa_cols[2]:
            if st.button("📘 Encyclopédie", use_container_width=True):
                st.session_state.current_page = "enc"
                st.rerun()
        with qa_cols[3]:
            if st.button("🧠 Quiz Médical", use_container_width=True):
                st.session_state.current_page = "quiz"
                st.rerun()

    # ============================================
    #  PAGE: SCAN - ENHANCED
    # ============================================
    elif pg == "scan":
        st.title(f"🔬 {t('scan')}")

        # Load model
        mdl, mn, mt = load_model()
        if mn:
            st.sidebar.success(f"🧠 Modèle: {mn}")
        else:
            st.sidebar.info(f"🧠 {t('demo_mode')}")

        # ✅ NEW: Camera preview with grid
        st.markdown(f"### 📋 1. {t('patient_info')}")
        ca, cb = st.columns(2)
        pn = ca.text_input(f"{t('patient_name')} *")
        pf = cb.text_input(t("patient_firstname"))
        c1, c2, c3, c4 = st.columns(4)
        pa = c1.number_input(t("age"), 0, 120, 30)
        ps = c2.selectbox(t("sex"), [t("male"), t("female")])
        pw = c3.number_input(t("weight"), 0, 300, 70)
        pst = c4.selectbox(t("sample_type"), SAMPLES.get(st.session_state.lang, SAMPLES["fr"]))

        st.markdown(f"### 🔬 2. {t('lab_info')}")
        la, lb2, lc2 = st.columns(3)
        t1 = la.text_input(f"{t('technician')} 1", value=st.session_state.user_full_name)
        t2 = lb2.text_input(f"{t('technician')} 2")
        lm = lc2.selectbox(t("microscope"), MICROSCOPE_TYPES)
        ld, le = st.columns(2)
        mg = ld.selectbox(t("magnification"), MAGNIFICATIONS, index=3)
        pt = le.selectbox(t("preparation"), PREPARATION_TYPES)
        nt = st.text_area(t("notes"), height=80)

        st.markdown("---")

        # ✅ NEW: Enhanced image capture
        st.markdown(f"### 📸 3. {t('image_capture')}")

        # Camera/Upload selection
        src = st.radio("source", [t("take_photo"), t("upload_file")],
                      horizontal=True, label_visibility="collapsed")

        img = None
        ih = None

        if t("take_photo") in src:
            st.info(f"📷 {t('camera_hint')}")

            # ✅ NEW: Camera with preview grid
            st.markdown("""
            <div style='text-align:center;margin:10px 0;'>
                <div style='display:inline-block;background:rgba(0,245,255,0.1);padding:20px;border-radius:12px;'>
                    <svg width="200" height="150" viewBox="0 0 200 150" style="background:rgba(0,0,0,0.5);border-radius:8px;">
                        <rect x="0" y="0" width="200" height="150" fill="rgba(0,0,0,0.3)" stroke="rgba(0,245,255,0.5)" stroke-width="1"/>
                        <line x1="66.6" y1="0" x2="66.6" y2="150" stroke="rgba(0,245,255,0.3)" stroke-width="1"/>
                        <line x1="133.3" y1="0" x2="133.3" y2="150" stroke="rgba(0,245,255,0.3)" stroke-width="1"/>
                        <line x1="0" y1="50" x2="200" y2="50" stroke="rgba(0,245,255,0.3)" stroke-width="1"/>
                        <line x1="0" y1="100" x2="200" y2="100" stroke="rgba(0,245,255,0.3)" stroke-width="1"/>
                        <circle cx="100" cy="75" r="30" fill="none" stroke="rgba(0,245,255,0.5)" stroke-width="1"/>
                        <text x="100" y="75" text-anchor="middle" fill="rgba(0,245,255,0.7)" font-size="8">CENTREZ</text>
                        <text x="100" y="85" text-anchor="middle" fill="rgba(0,245,255,0.7)" font-size="6">L'ÉCHANTILLON</text>
                    </svg>
                </div>
            </div>
            """, unsafe_allow_html=True)

            cp = st.camera_input("camera")
            if cp:
                img = safe_image_open(cp)
                img = resize_image(img)
                ih = hashlib.md5(cp.getvalue()).hexdigest()

        else:
            uf = st.file_uploader(t("upload_file"), type=["jpg", "jpeg", "png", "bmp", "tiff"],
                                 accept_multiple_files=False)

            if uf:
                # Check file size
                if len(uf.getvalue()) > MAX_FILE_SIZE_MB * 1024 * 1024:
                    st.error(f"❌ Fichier trop volumineux (max {MAX_FILE_SIZE_MB}MB)")
                else:
                    img = safe_image_open(uf)
                    img = resize_image(img)
                    ih = hashlib.md5(uf.getvalue()).hexdigest()

        # Process image if available
        if img:
            if not pn.strip():
                st.error(t("name_required"))
                st.stop()

            if st.session_state.get("_ih") != ih:
                st.session_state._ih = ih
                st.session_state.demo_seed = random.randint(0, 999999)
                st.session_state.heatmap_seed = random.randint(0, 999999)

            # ✅ NEW: Enhanced image processing interface
            ci, cr = st.columns(2)

            with ci:
                with st.expander("🎛️ Zoom / Ajustements"):
                    z = st.slider("Zoom", 1.0, 5.0, 1.0, 0.25)
                    br = st.slider("Luminosité", 0.5, 2.0, 1.0, 0.1)
                    co = st.slider("Contraste", 0.5, 2.0, 1.0, 0.1)
                    sa = st.slider("Saturation", 0.0, 2.0, 1.0, 0.1)

                # Apply adjustments
                adj = adjust_image(img, br, co, sa)
                if z > 1:
                    adj = zoom_img(adj, z)

                # ✅ NEW: Enhanced tabs with icons
                tabs = st.tabs([
                    "📷 Original", "🔥 Thermique", "📐 Contours",
                    "✨ Amélioré", "🔄 Négatif", "🏔️ Relief",
                    "🎯 Heatmap", "🔍 Analyse"
                ])

                with tabs[0]:
                    st.image(adj, use_container_width=True, caption="Image originale")

                with tabs[1]:
                    st.image(thermal_filter(adj), use_container_width=True, caption="Filtre thermique")

                with tabs[2]:
                    st.image(edges_filter(adj), use_container_width=True, caption="Détection de contours")

                with tabs[3]:
                    st.image(enhanced_filter(adj), use_container_width=True, caption="Contraste amélioré")

                with tabs[4]:
                    st.image(negative_filter(adj), use_container_width=True, caption="Négatif")

                with tabs[5]:
                    st.image(emboss_filter(adj), use_container_width=True, caption="Effet relief")

                with tabs[6]:
                    st.image(gen_heatmap(img, st.session_state.heatmap_seed),
                            use_container_width=True, caption="Carte thermique IA")

                with tabs[7]:
                    # ✅ NEW: AI analysis preview
                    with st.spinner("Analyse en cours..."):
                        progress_bar = st.progress(0)
                        for i in range(100):
                            time.sleep(0.01)
                            progress_bar.progress(i + 1)

                        # Run prediction
                        res = predict(mdl, mt, adj, st.session_state.demo_seed)

                        # Display quick preview
                        st.markdown(f"""
                        <div class='dm-card' style='border-left:4px solid {risk_color(res["risk"])};'>
                            <h4 style='margin:0;color:{risk_color(res["risk"])}!important;'>
                                {res['label']} - {res['conf']}%
                            </h4>
                            <p style='opacity:.6;font-size:.8rem;'>
                                {PARASITE_DB[res['label']]['desc'].get(st.session_state.lang, '')[:100]}...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

            with cr:
                st.markdown(f"### 🧠 {t('result')}")

                with st.spinner("Analyse approfondie..."):
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.015)
                        progress_bar.progress(i + 1)

                    # Run full prediction
                    res = predict(mdl, mt, adj, st.session_state.demo_seed)

                # Display full results
                lb_result = res["label"]
                cf = res["conf"]
                rc = risk_color(res["risk"])
                info = PARASITE_DB.get(lb_result, PARASITE_DB["Negative"])

                if not res["rel"]:
                    st.warning(t("low_conf_warn"))
                if res["demo"]:
                    st.info(t("demo_mode"))

                st.markdown(f"""<div class='dm-card' style='border-left:4px solid {rc};'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;'>
                <div>
                    <h2 style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;margin:0;font-family:Orbitron;'>
                        {lb_result}
                    </h2>
                    <p style='opacity:.4;font-style:italic;'>{info['sci']}</p>
                </div>
                <div style='text-align:center;'>
                    <div style='font-size:2.8rem;font-weight:900;font-family:JetBrains Mono;color:{rc}!important;-webkit-text-fill-color:{rc}!important;'>
                        {cf}%
                    </div>
                    <div style='font-size:.7rem;opacity:.4;'>{t("confidence")}</div>
                </div>
                </div>

                <hr style='opacity:.1;margin:14px 0;'>

                <div style='display:flex;flex-wrap:wrap;gap:12px;'>
                    <div style='flex:1;min-width:200px;'>
                        <p><b>🔬 {t("morphology")}:</b><br>{tl(info['morph'])}</p>
                        <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-weight:700;'>
                            {tl(info['risk_d'])}
                        </span></p>
                    </div>

                    <div style='flex:1;min-width:200px;'>
                        <div style='background:rgba(0,255,136,.06);padding:14px;border-radius:12px;margin:10px 0;border:1px solid rgba(0,255,136,.1);'>
                            <b>💡 {t("advice")}:</b><br>{tl(info['advice'])}
                        </div>
                        <div style='background:rgba(0,100,255,.06);padding:14px;border-radius:12px;font-style:italic;border:1px solid rgba(0,100,255,.1);'>
                            🤖 {tl(info['funny'])}
                        </div>
                    </div>
                </div>
                </div>""", unsafe_allow_html=True)

                # ✅ NEW: Action buttons
                vc1, vc2, vc3 = st.columns(3)
                with vc1:
                    if st.button(f"🔊 {t('listen')}", use_container_width=True):
                        speak(f"{lb_result}. {tl(info['funny'])}")
                        st.rerun()
                with vc2:
                    if st.button(f"🔇 {t('stop_voice')}", key="sv2", use_container_width=True):
                        stop_speech()
                with vc3:
                    if st.button("📊 Détails", use_container_width=True):
                        with st.expander(f"🔍 {t('all_probabilities')}"):
                            if res["preds"] and HAS_PLOTLY:
                                sp = dict(sorted(res["preds"].items(), key=lambda x: x[1], reverse=True))
                                fig = px.bar(
                                    x=list(sp.values()),
                                    y=list(sp.keys()),
                                    orientation='h',
                                    color=list(sp.values()),
                                    color_continuous_scale='RdYlGn_r',
                                    title="Probabilités des parasites détectés"
                                )
                                fig.update_layout(
                                    height=300,
                                    template=plot_template,
                                    margin=dict(l=20, r=20, t=40, b=20),
                                    xaxis_title="Confiance (%)",
                                    yaxis_title="Parasites"
                                )
                                st.plotly_chart(fig, use_container_width=True)

                # ✅ NEW: Enhanced PDF and save options
                st.markdown("---")
                a1, a2, a3 = st.columns(3)

                with a1:
                    try:
                        pdf = make_pdf(
                            {"Nom": pn, "Prenom": pf, "Age": str(pa), "Sexe": ps,
                             "Poids": str(pw), "Echantillon": pst},
                            {"Microscope": lm, "Grossissement": mg, "Preparation": pt,
                             "Tech1": t1, "Tech2": t2, "Notes": nt},
                            res, lb_result, st.session_state.lang
                        )
                        st.download_button(
                            f"📥 {t('download_pdf')}",
                            pdf,
                            f"Rapport_{pn}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            "application/pdf",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.error(f"Erreur PDF: {e}")

                with a2:
                    if has_role(2):
                        if st.button(f"💾 {t('save_db')}", use_container_width=True):
                            aid = db_save_analysis(st.session_state.user_id, {
                                "pn": pn, "pf": pf, "pa": pa, "ps": ps, "pw": pw,
                                "st": pst, "mt": lm, "mg": mg, "pt": pt, "t1": t1, "t2": t2, "nt": nt,
                                "label": lb_result, "conf": cf, "risk": res["risk"],
                                "rel": 1 if res["rel"] else 0,
                                "preds": res["preds"], "hash": ih, "demo": 1 if res["demo"] else 0,
                                "quality": 100,  # ✅ NEW: Image quality score
                                "proc_time": res["proc_time"]
                            })
                            db_log(st.session_state.user_id, st.session_state.user_name, "Analysis", f"ID:{aid}")
                            st.success(t("saved_ok"))

                with a3:
                    if st.button(f"🔄 {t('new_analysis')}", use_container_width=True):
                        st.session_state.demo_seed = None
                        st.session_state._ih = None
                        st.rerun()

    # ============================================
    #  PAGE: ENCYCLOPEDIA - ENHANCED
    # ============================================
    elif pg == "enc":
        st.title(f"📘 {t('encyclopedia')}")

        # ✅ NEW: Enhanced search with filters
        st.markdown("---")
        sc1, sc2 = st.columns(2)
        with sc1:
            sr = st.text_input(f"🔍 {t('search')}", key="encyc_search")
        with sc2:
            risk_filter = st.selectbox("Filtre par risque",
                                      ["Tous", "Élevé", "Moyen", "Faible", "Aucun"],
                                      index=0, key="risk_filter")

        st.markdown("---")

        found = False
        for nm, d in PARASITE_DB.items():
            if nm == "Negative":
                continue

            # Apply filters
            search_match = not sr.strip() or sr.lower() in (nm + " " + d["sci"]).lower()
            risk_match = (risk_filter == "Tous" or
                         (risk_filter == "Élevé" and d["risk"] == "high") or
                         (risk_filter == "Moyen" and d["risk"] == "medium") or
                         (risk_filter == "Faible" and d["risk"] == "low") or
                         (risk_filter == "Aucun" and d["risk"] == "none"))

            if search_match and risk_match:
                found = True
                rc = risk_color(d["risk"])

                with st.expander(f"{d['icon']} {nm} -- *{d['sci']}* | {tl(d['risk_d'])}", expanded=not sr.strip()):
                    ci, cv = st.columns([2.5, 1])

                    with ci:
                        st.markdown(f"""<div class='dm-card' style='border-left:3px solid {rc};'>
                        <h4 style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-family:Orbitron;'>
                            {d['sci']}
                        </h4>

                        <div style='display:flex;flex-wrap:wrap;gap:12px;margin:12px 0;'>
                            <div style='flex:1;min-width:200px;'>
                                <p><b>🔬 {t("morphology")}:</b><br>{tl(d['morph'])}</p>
                                <p><b>📖 {t("description")}:</b><br>{tl(d['desc'])}</p>
                            </div>

                            <div style='flex:1;min-width:200px;'>
                                <p><b>⚠️ {t("risk")}:</b> <span style='color:{rc}!important;-webkit-text-fill-color:{rc}!important;font-weight:700;'>
                                    {tl(d['risk_d'])}
                                </span></p>

                                <div style='background:rgba(0,255,136,.06);padding:12px;border-radius:10px;margin:8px 0;'>
                                    <b>💡:</b> {tl(d['advice'])}
                                </div>

                                <div style='background:rgba(0,100,255,.06);padding:12px;border-radius:10px;font-style:italic;'>
                                    🤖 {tl(d['funny'])}
                                </div>
                            </div>
                        </div>

                        <div style='background:rgba(255,149,0,.06);padding:12px;border-radius:10px;margin:8px 0;'>
                            <b>🌍 Géographie:</b> {d.get('geography', 'N/A')}<br>
                            <b>🕒 Incubation:</b> {d.get('incubation', 'N/A')}<br>
                            <b>🦟 Transmission:</b> {d.get('transmission', 'N/A')}
                        </div>
                        </div>""", unsafe_allow_html=True)

                        # ✅ NEW: Interactive lifecycle
                        cy = tl(d.get("cycle", {}))
                        if cy and cy not in ["N/A", "غير متوفر"]:
                            with st.expander(f"🔄 {t('lifecycle')}"):
                                st.markdown(f"**{cy}**")

                                # ✅ NEW: Visual lifecycle diagram
                                if HAS_PLOTLY:
                                    steps = cy.split("←") if "←" in cy else cy.split("→")
                                    steps = [s.strip() for s in steps]

                                    fig = go.Figure(go.Sankey(
                                        node=dict(
                                            pad=15,
                                            thickness=20,
                                            line=dict(color="black", width=0.5),
                                            label=steps,
                                            color=[NEON["cyan"], NEON["magenta"], NEON["green"],
                                                  NEON["orange"], NEON["red"], NEON["blue"]]
                                        ),
                                        link=dict(
                                            source=[i for i in range(len(steps)-1)],
                                            target=[i+1 for i in range(len(steps)-1)],
                                            value=[1 for _ in range(len(steps)-1)]
                                        )
                                    ))

                                    fig.update_layout(
                                        height=300,
                                        template=plot_template,
                                        margin=dict(l=20, r=20, t=20, b=20),
                                        title="Cycle de vie du parasite"
                                    )
                                    st.plotly_chart(fig, use_container_width=True)

                        # Diagnostic keys
                        dk = tl(d.get("keys", {}))
                        if dk and dk not in ["N/A", "غير متوفر"]:
                            with st.expander(f"🔑 {t('diagnostic_keys')}"):
                                st.markdown(dk)

                        # Tests
                        if d.get("tests"):
                            with st.expander(f"🩺 {t('extra_tests')}"):
                                for x in d["tests"]:
                                    st.markdown(f"- {x}")

                    with cv:
                        rp = risk_pct(d["risk"])
                        if rp > 0:
                            st.progress(rp / 100, text=f"{rp}%")

                        st.markdown(f'<div style="text-align:center;font-size:4rem;">{d["icon"]}</div>', unsafe_allow_html=True)

                        if st.button(f"🔊 {t('listen')}", key=f"ev_{nm}"):
                            speak(f"{nm}. {tl(d['desc'])}")
                            st.rerun()

                        # ✅ NEW: Quick reference card
                        st.markdown(f"""
                        <div class='dm-card' style='background:rgba(0,102,255,.1);margin-top:12px;'>
                            <p style='margin:0;opacity:.8;font-size:.8rem;'>
                                <b>📌 Référence rapide:</b><br>
                                • <b>Taille:</b> {d['morph'].get(st.session_state.lang, '').split('(')[1].split(')')[0] if '(' in d['morph'].get(st.session_state.lang, '') else 'N/A'}<br>
                                • <b>Coloration:</b> {d.get('coloration', 'MGG/Lugol')}<br>
                                • <b>Localisation:</b> {d.get('location', 'Intestinal/Sang')}<br>
                                • <b>Transmission:</b> {d.get('transmission', 'N/A')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

        if sr.strip() and not found:
            st.warning(t("no_results"))

            # ✅ NEW: Suggest similar parasites
            suggestions = []
            for nm in PARASITE_DB:
                if nm != "Negative" and sr.lower() in nm.lower():
                    suggestions.append(nm)

            if suggestions:
                st.markdown(f"**💡 Suggestions proches:** {', '.join(suggestions)}")

    # ============================================
    #  PAGE: DASHBOARD - ENHANCED
    # ============================================
    elif pg == "dash":
        st.title(f"📊 {t('dashboard')}")

        # Get data
        s = db_stats() if has_role(3) else db_stats(st.session_state.user_id)
        an = db_analyses() if has_role(3) else db_analyses(st.session_state.user_id)

        # ✅ NEW: Enhanced metrics with icons
        metrics = [
            ("🔬", s["total"], t("total_analyses")),
            ("✅", s["reliable"], t("reliable")),
            ("⚠️", s["verify"], t("to_verify")),
            ("🦠", s["top"], t("most_frequent")),
            ("📈", f"{s['avg']}%", t("avg_confidence")),
            ("⏱️", f"{s['avg_time_ms']}ms", "Temps moyen"),
        ]

        cols = st.columns(6)
        for col, (ic, v, lb) in zip(cols, metrics):
            with col:
                st.markdown(f"""<div class='dm-m'>
                <span class='dm-m-i'>{ic}</span>
                <div class='dm-m-v'>{v}</div>
                <div class='dm-m-l'>{lb}</div>
                </div>""", unsafe_allow_html=True)

        if s["total"] > 0 and an:
            df = pd.DataFrame(an)

            # ✅ NEW: Enhanced charts with tabs
            st.markdown("---")
            tab1, tab2, tab3 = st.tabs([
                f"📊 {t('parasite_distribution')}",
                f"📈 {t('trends')}",
                f"🔍 Analyse avancée"
            ])

            with tab1:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"#### {t('parasite_distribution')}")
                    if HAS_PLOTLY and "parasite_detected" in df.columns:
                        pc = df["parasite_detected"].value_counts()
                        fig = px.pie(
                            values=pc.values,
                            names=pc.index,
                            hole=.4,
                            color_discrete_sequence=px.colors.sequential.Plasma
                        )
                        fig.update_layout(
                            height=350,
                            template=plot_template,
                            margin=dict(l=20, r=20, t=20, b=20),
                            title="Distribution des parasites détectés"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                with c2:
                    st.markdown(f"#### {t('confidence_levels')}")
                    if HAS_PLOTLY and "confidence" in df.columns:
                        fig = px.histogram(
                            df,
                            x="confidence",
                            nbins=20,
                            color_discrete_sequence=["#00f5ff"]
                        )
                        fig.update_layout(
                            height=350,
                            template=plot_template,
                            margin=dict(l=20, r=20, t=20, b=20),
                            title="Niveaux de confiance des analyses"
                        )
                        st.plotly_chart(fig, use_container_width=True)

            with tab2:
                tr = db_trends(30)
                if tr and HAS_PLOTLY:
                    # ✅ NEW: Enhanced trend analysis
                    trend_df = pd.DataFrame(tr)

                    # Group by day
                    daily_trends = trend_df.groupby('day').agg({
                        'count': 'sum',
                        'avg_conf': 'mean'
                    }).reset_index()

                    # Plot trends
                    fig = make_subplots(specs=[[{"secondary_y": True}]])

                    fig.add_trace(
                        go.Scatter(
                            x=daily_trends['day'],
                            y=daily_trends['count'],
                            name="Nombre d'analyses",
                            line=dict(color='#00f5ff', width=2),
                            marker=dict(size=8)
                        ),
                        secondary_y=False
                    )

                    fig.add_trace(
                        go.Scatter(
                            x=daily_trends['day'],
                            y=daily_trends['avg_conf'],
                            name="Confiance moyenne (%)",
                            line=dict(color='#ff9500', width=2, dash='dot'),
                            marker=dict(size=8)
                        ),
                        secondary_y=True
                    )

                    fig.update_layout(
                        height=400,
                        template=plot_template,
                        margin=dict(l=20, r=20, t=40, b=20),
                        title="Tendances des 30 derniers jours",
                        hovermode="x unified"
                    )

                    fig.update_yaxes(title_text="Nombre", secondary_y=False)
                    fig.update_yaxes(title_text="Confiance (%)", secondary_y=True)

                    st.plotly_chart(fig, use_container_width=True)

                    # Parasite-specific trends
                    st.markdown("---")
                    st.markdown("#### Tendances par parasite")

                    for parasite in trend_df['parasite_detected'].unique():
                        parasite_data = trend_df[trend_df['parasite_detected'] == parasite]
                        if len(parasite_data) > 0:
                            fig = px.line(
                                parasite_data,
                                x="day",
                                y="count",
                                title=f"Tendance: {parasite}",
                                markers=True
                            )
                            fig.update_layout(
                                height=250,
                                template=plot_template,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

            with tab3:
                # ✅ NEW: Advanced analytics
                st.markdown("#### Analyse par technicien")
                if "technician1" in df.columns:
                    tech_stats = df["technician1"].value_counts().head(10)
                    fig = px.bar(
                        tech_stats,
                        orientation='h',
                        title="Top 10 techniciens par nombre d'analyses",
                        color=tech_stats.values,
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(
                        height=350,
                        template=plot_template,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                st.markdown("---")
                st.markdown("#### Analyse par type d'échantillon")
                if "sample_type" in df.columns:
                    sample_stats = df["sample_type"].value_counts()
                    fig = px.pie(
                        sample_stats,
                        values=sample_stats.values,
                        names=sample_stats.index,
                        title="Répartition par type d'échantillon"
                    )
                    fig.update_layout(
                        height=350,
                        template=plot_template,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # ✅ NEW: Enhanced data table
            st.markdown("---")
            st.markdown(f"### 📋 {t('history')}")

            if has_role(3):
                display_cols = [
                    "id", "analysis_date", "patient_name", "parasite_detected",
                    "confidence", "risk_level", "analyst", "validated"
                ]
            else:
                display_cols = [
                    "id", "analysis_date", "patient_name", "parasite_detected",
                    "confidence", "risk_level", "validated"
                ]

            display_cols = [c for c in display_cols if c in df.columns]

            # ✅ NEW: Data table with filtering
            if display_cols:
                st.dataframe(
                    df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "analysis_date": st.column_config.DatetimeColumn(
                            "Date",
                            format="DD/MM/YYYY HH:mm"
                        ),
                        "confidence": st.column_config.ProgressColumn(
                            "Confiance",
                            format="%d%%",
                            min_value=0,
                            max_value=100
                        ),
                        "risk_level": st.column_config.TextColumn(
                            "Risque",
                            help="Niveau de risque du parasite détecté"
                        )
                    }
                )

                # ✅ NEW: Export options
                e1, e2, e3 = st.columns(3)
                with e1:
                    st.download_button(
                        f"⬇️ {t('export_csv')}",
                        df.to_csv(index=False).encode('utf-8-sig'),
                        "analyses.csv",
                        "text/csv",
                        use_container_width=True
                    )
                with e2:
                    st.download_button(
                        f"⬇️ {t('export_json')}",
                        df.to_json(orient='records', force_ascii=False).encode(),
                        "analyses.json",
                        "application/json",
                        use_container_width=True
                    )
                with e3:
                    if has_role(2):
                        st.download_button(
                            "⬇️ Exporter Excel",
                            io.BytesIO(df.to_excel("analyses.xlsx", index=False)),
                            "analyses.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )

            # Validation section
            if has_role(2) and "validated" in df.columns:
                uv = df[df["validated"] == 0]
                if not uv.empty:
                    st.markdown("---")
                    st.markdown("#### Validation des résultats")

                    vi = st.selectbox("Sélectionner ID à valider:", uv["id"].tolist())
                    if st.button(f"✅ {t('validate')} #{vi}", key=f"validate_{vi}"):
                        db_validate(vi, st.session_state.user_full_name)
                        st.success(f"Validé #{vi}")
                        st.rerun()
        else:
            st.info(t("no_data"))

    # ============================================
    #  PAGE: QUIZ - ENHANCED
    # ============================================
    elif pg == "quiz":
        st.title(f"🧠 {t('quiz')}")

        # Initialize quiz state
        if "quiz_state" not in st.session_state:
            st.session_state.quiz_state = {
                "current": 0, "score": 0, "answered": [],
                "active": False, "order": [], "wrong": [],
                "total_q": 0, "finished": False,
                "selected_answer": None, "show_result": False,
                "start_time": None, "time_taken": 0
            }

        qs = st.session_state.quiz_state

        # ✅ NEW: Enhanced leaderboard with filters
        with st.expander(f"🏆 {t('leaderboard')}"):
            lb_col1, lb_col2 = st.columns(2)
            with lb_col1:
                lb_limit = st.selectbox("Nombre d'entrées", [5, 10, 20, 50], index=1)
            with lb_col2:
                lb_cat = st.selectbox("Catégorie", ["Toutes"] + list(set(q.get("cat", "General") for q in QUIZ_QUESTIONS)))

            lb_data = db_leaderboard(lb_limit * 2)  # Get more to filter

            if lb_data:
                # Filter by category if needed
                if lb_cat != "Toutes":
                    lb_data = [e for e in lb_data if e.get('category', 'general') == lb_cat]

                # Display limited results
                for i, e in enumerate(lb_data[:lb_limit]):
                    medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"**#{i + 1}**"
                    time_str = f" en {e.get('time_seconds', 0)}s" if e.get('time_seconds') else ""
                    st.markdown(f"""
                    <div class='dm-card' style='margin:4px 0;padding:8px;'>
                        {medal} **{e['username']}** — {e['score']}/{e['total_questions']}
                        ({e['percentage']:.0f}%){time_str}
                        <div style='opacity:.6;font-size:.8rem;'>{e.get('category', 'Général')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(t("no_data"))

        # Quiz not started
        if not qs.get("active", False) and not qs.get("finished", False):
            st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
            <div style='font-size:4rem;margin-bottom:10px;'>🧠</div>
            <h3 class='dm-nt'>{
                {
                    "fr": "Testez vos connaissances en parasitologie !",
                    "ar": "اختبر معارفك في علم الطفيليات!",
                    "en": "Test your parasitology knowledge!"
                }.get(st.session_state.lang, "")
            }</h3>
            <p style='opacity:.5;'>{{
                "fr": f"{len(QUIZ_QUESTIONS)} questions disponibles",
                "ar": f"{len(QUIZ_QUESTIONS)} سؤال متاح",
                "en": f"{len(QUIZ_QUESTIONS)} questions available"
            }.get(st.session_state.lang, "")}</p>
            </div>""", unsafe_allow_html=True)

            st.markdown("---")

            # ✅ NEW: Enhanced quiz configuration
            qc1, qc2, qc3 = st.columns(3)
            with qc1:
                n_questions = st.slider(
                    {
                        "fr": "Nombre de questions:",
                        "ar": "عدد الأسئلة:",
                        "en": "Number of questions:"
                    }.get(st.session_state.lang, "Questions:"),
                    5, min(50, len(QUIZ_QUESTIONS)), 10
                )
            with qc2:
                cats = list(set(q.get("cat", "General") for q in QUIZ_QUESTIONS))
                all_cat_label = {
                    "fr": "Toutes les catégories",
                    "ar": "جميع الفئات",
                    "en": "All categories"
                }.get(st.session_state.lang, "All")
                cats.insert(0, all_cat_label)
                chosen_cat = st.selectbox(
                    {
                        "fr": "Catégorie:",
                        "ar": "الفئة:",
                        "en": "Category:"
                    }.get(st.session_state.lang, "Category:"),
                    cats
                )
            with qc3:
                time_limit = st.selectbox(
                    {
                        "fr": "Limite de temps:",
                        "ar": "حد الوقت:",
                        "en": "Time limit:"
                    }.get(st.session_state.lang, "Time limit:"),
                    ["Aucune", "30s", "1min", "2min"],
                    index=0
                )

            if st.button(f"🎮 {t('start_quiz')}", use_container_width=True, type="primary"):
                # Create question pool
                if chosen_cat == all_cat_label:
                    pool = list(range(len(QUIZ_QUESTIONS)))
                else:
                    pool = [i for i, q in enumerate(QUIZ_QUESTIONS) if q.get("cat") == chosen_cat]

                if len(pool) == 0:
                    pool = list(range(len(QUIZ_QUESTIONS)))

                random.shuffle(pool)
                final_order = pool[:min(n_questions, len(pool))]

                # Start quiz
                st.session_state.quiz_state = {
                    "current": 0,
                    "score": 0,
                    "answered": [],
                    "active": True,
                    "order": final_order,
                    "wrong": [],
                    "total_q": len(final_order),
                    "finished": False,
                    "selected_answer": None,
                    "show_result": False,
                    "start_time": time.time(),
                    "time_limit": {
                        "Aucune": 0, "30s": 30, "1min": 60, "2min": 120
                    }.get(time_limit, 0),
                    "category": chosen_cat if chosen_cat != all_cat_label else "general"
                }

                db_log(st.session_state.user_id, st.session_state.user_name,
                      "Quiz started", f"n={len(final_order)} cat={chosen_cat}")
                st.rerun()

        # Quiz active - answering questions
        elif qs.get("active", False) and not qs.get("finished", False):
            idx = qs["current"]
            order = qs.get("order", [])
            total_q = qs.get("total_q", len(order))

            if idx < len(order):
                qi = order[idx]
                q = QUIZ_QUESTIONS[qi]

                # ✅ NEW: Time tracking
                time_elapsed = int(time.time() - qs["start_time"])
                time_left = qs["time_limit"] - time_elapsed if qs["time_limit"] > 0 else 0

                if qs["time_limit"] > 0 and time_left <= 0:
                    st.session_state.quiz_state["finished"] = True
                    st.session_state.quiz_state["active"] = False
                    st.rerun()

                # Progress with time
                progress_val = idx / total_q if total_q > 0 else 0
                st.progress(progress_val)

                # Time display
                if qs["time_limit"] > 0:
                    mins, secs = divmod(time_left, 60)
                    time_display = f"⏱️ {mins:02d}:{secs:02d}"
                    st.markdown(f"""
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <h3>{{
                            "fr": "Question",
                            "ar": "سؤال",
                            "en": "Question"
                        }} {idx + 1}/{total_q}</h3>
                        <div style='background:rgba(255,0,64,0.1);padding:4px 8px;border-radius:6px;'>
                            {time_display}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"### {{
                        "fr": "Question",
                        "ar": "سؤال",
                        "en": "Question"
                    }} {idx + 1}/{total_q}")

                # Category display
                cat = q.get("cat", "")
                if cat:
                    st.caption(f"📂 {cat}")

                # Question text
                q_text = tl(q["q"])
                st.markdown(f"""<div class='dm-card dm-card-purple'>
                <h4 style='margin:0;line-height:1.6;'>{q_text}</h4>
                </div>""", unsafe_allow_html=True)

                # Check if already answered this question
                if not qs.get("show_result", False):
                    st.markdown("---")
                    option_cols = st.columns(2)

                    # ✅ NEW: Enhanced option buttons with letters and colors
                    for i, opt in enumerate(q["opts"]):
                        with option_cols[i % 2]:
                            letter = ['A', 'B', 'C', 'D'][i]
                            btn_key = f"quiz_opt_{idx}_{i}"

                            # Color options based on selection
                            if qs.get("selected_answer") == i:
                                btn_style = "background:linear-gradient(135deg,#00f5ff,#0066ff);color:white;"
                            else:
                                btn_style = ""

                            if st.button(
                                f"<span style='{btn_style}'>"
                                f"<span style='background:rgba(0,245,255,0.2);padding:2px 6px;border-radius:4px;margin-right:8px;'>{letter}</span>"
                                f"{opt}</span>",
                                key=btn_key,
                                use_container_width=True,
                                help=f"Option {letter}"
                            ):
                                correct = (i == q["ans"])
                                st.session_state.quiz_state["selected_answer"] = i
                                st.session_state.quiz_state["show_result"] = True

                                if correct:
                                    st.session_state.quiz_state["score"] += 1
                                else:
                                    st.session_state.quiz_state["wrong"].append({
                                        "q": q_text,
                                        "your": opt,
                                        "correct": q["opts"][q["ans"]],
                                        "cat": q.get("cat", "general")
                                    })

                                st.session_state.quiz_state["answered"].append(correct)
                                st.rerun()

                else:
                    # Show result of answer
                    selected = qs.get("selected_answer", -1)
                    correct_idx = q["ans"]
                    is_correct = selected == correct_idx

                    # ✅ NEW: Enhanced result display
                    if is_correct:
                        st.success(f"✅ {{
                            'fr': 'Bonne réponse !',
                            'ar': 'إجابة صحيحة!',
                            'en': 'Correct!'
                        }}")
                    else:
                        correct_ans = q["opts"][correct_idx]
                        st.error(f"❌ {{
                            'fr': 'Réponse correcte',
                            'ar': 'الإجابة الصحيحة',
                            'en': 'Correct answer'
                        }}: **{correct_ans}**")

                    # Show explanation
                    expl = tl(q.get("expl", {}))
                    if expl:
                        st.info(f"📖 {expl}")

                    # Show all options with markers
                    for i, opt in enumerate(q["opts"]):
                        if i == correct_idx:
                            st.markdown(f"✅ **{['A','B','C','D'][i]}. {opt}**")
                        elif i == selected and not is_correct:
                            st.markdown(f"❌ ~~{['A','B','C','D'][i]}. {opt}~~")
                        else:
                            st.markdown(f"{'  '}{['A','B','C','D'][i]}. {opt}")

                    st.markdown("---")

                    # Next question button
                    if idx + 1 < len(order):
                        if st.button(f"➡️ {t('next_question')}", use_container_width=True, type="primary"):
                            st.session_state.quiz_state["current"] += 1
                            st.session_state.quiz_state["show_result"] = False
                            st.session_state.quiz_state["selected_answer"] = None
                            st.rerun()
                    else:
                        finish_label = {
                            "fr": "🏁 Voir les résultats",
                            "ar": "🏁 عرض النتائج",
                            "en": "🏁 See Results"
                        }.get(st.session_state.lang, "🏁 Results")

                        if st.button(finish_label, use_container_width=True, type="primary"):
                            st.session_state.quiz_state["finished"] = True
                            st.session_state.quiz_state["active"] = False
                            st.session_state.quiz_state["time_taken"] = int(time.time() - qs["start_time"])
                            st.rerun()

            else:
                # Fallback: mark as finished
                st.session_state.quiz_state["finished"] = True
                st.session_state.quiz_state["active"] = False
                st.session_state.quiz_state["time_taken"] = int(time.time() - qs["start_time"])
                st.rerun()

        # Quiz finished - show results
        elif qs.get("finished", False):
            score = qs.get("score", 0)
            total_q = qs.get("total_q", 1)
            pct = int(score / total_q * 100) if total_q > 0 else 0
            time_taken = qs.get("time_taken", 0)

            # ✅ NEW: Enhanced result display with animations
            if pct >= 80:
                emoji, msg, color = "🏆", t("score_excellent"), "#00ff88"
            elif pct >= 60:
                emoji, msg, color = "👍", t("score_good"), "#00f5ff"
            elif pct >= 40:
                emoji, msg, color = "📚", t("score_average"), "#ff9500"
            else:
                emoji, msg, color = "💪", t("score_low"), "#ff0040"

            st.markdown(f"""
            <div class='dm-card dm-card-green' style='text-align:center;'>
            <div style='font-size:5rem;'>{emoji}</div>
            <h2 class='dm-nt'>{t('result')}</h2>

            <div style='font-size:4rem;font-weight:900;font-family:JetBrains Mono,monospace;
                background:linear-gradient(135deg,{color},#ff00ff,#00ff88);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
                {score}/{total_q}
            </div>

            <p style='font-size:1.5rem;opacity:.8;'>{pct}%</p>

            <div style='background:rgba(0,255,136,.1);padding:12px;border-radius:12px;margin:12px auto;max-width:80%;'>
                {msg}
            </div>

            <p style='opacity:.6;font-size:.9rem;'>
                Temps: {time_taken} secondes • Catégorie: {qs.get('category', 'Général')}
            </p>
            </div>
            """, unsafe_allow_html=True)

            # Save score to DB
            try:
                db_quiz_save(
                    st.session_state.user_id,
                    st.session_state.user_name,
                    score, total_q, pct,
                    qs.get('category', 'general'),
                    time_taken
                )
                db_log(st.session_state.user_id, st.session_state.user_name,
                      "Quiz done", f"{score}/{total_q}={pct}% time={time_taken}s")
            except Exception as e:
                st.error(f"Error saving score: {e}")

            # ✅ NEW: Performance chart with time
            if HAS_PLOTLY and total_q > 0:
                st.markdown("---")
                analysis_label = {
                    "fr": "Analyse des résultats",
                    "ar": "تحليل النتائج",
                    "en": "Results Analysis"
                }.get(st.session_state.lang, "Analysis")

                st.markdown(f"### 📊 {analysis_label}")

                correct_label = {
                    "fr": "Correctes",
                    "ar": "صحيحة",
                    "en": "Correct"
                }.get(st.session_state.lang, "Correct")

                incorrect_label = {
                    "fr": "Incorrectes",
                    "ar": "خاطئة",
                    "en": "Incorrect"
                }.get(st.session_state.lang, "Incorrect")

                fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])

                # Pie chart
                fig.add_trace(
                    go.Pie(
                        labels=[correct_label, incorrect_label],
                        values=[score, total_q - score],
                        marker_colors=["#00ff88", "#ff0040"],
                        hole=0.5,
                        textinfo='label+percent',
                        textfont_size=14
                    ),
                    1, 1
                )

                # Gauge for percentage
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number",
                        value=pct,
                        title={'text': "Score"},
                        number={'font': {'color': color}},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': color},
                            'steps': [
                                {'range': [0, 40], 'color': "#ff0040"},
                                {'range': [40, 60], 'color': "#ff9500"},
                                {'range': [60, 80], 'color': "#00f5ff"},
                                {'range': [80, 100], 'color': "#00ff88"}
                            ]
                        }
                    ),
                    1, 2
                )

                fig.update_layout(
                    height=300,
                    template=plot_template,
                    margin=dict(l=20, r=20, t=20, b=20),
                    title="Performance du quiz"
                )

                st.plotly_chart(fig, use_container_width=True)

            # Wrong answers review
            wrong = qs.get("wrong", [])
            if wrong:
                review_label = {
                    "fr": f"Erreurs à revoir ({len(wrong)})",
                    "ar": f"الأخطاء ({len(wrong)})",
                    "en": f"Mistakes to review ({len(wrong)})"
                }.get(st.session_state.lang, f"Mistakes ({len(wrong)})")

                with st.expander(f"❌ {review_label}"):
                    for i, w in enumerate(wrong):
                        your_label = {
                            "fr": "Votre réponse",
                            "ar": "إجابتك",
                            "en": "Your answer"
                        }.get(st.session_state.lang, "Your answer")

                        correct_label2 = {
                            "fr": "Correcte",
                            "ar": "الصحيحة",
                            "en": "Correct"
                        }.get(st.session_state.lang, "Correct")

                        st.markdown(f"""
                        <div class='dm-card' style='margin:8px 0;padding:12px;'>
                        **{i + 1}. {w['q']}**
                        <div style='display:flex;justify-content:space-between;margin:8px 0;'>
                            <div>❌ {your_label}: ~~{w['your']}~~</div>
                            <div>✅ {correct_label2}: **{w['correct']}**</div>
                        </div>
                        <div style='opacity:.6;font-size:.8rem;'>Catégorie: {w.get('cat', 'Général')}</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("---")

            # ✅ NEW: Category performance breakdown
            if wrong:
                st.markdown("#### Performance par catégorie")

                # Count wrong answers by category
                wrong_by_cat = {}
                for w in wrong:
                    cat = w.get('cat', 'general')
                    wrong_by_cat[cat] = wrong_by_cat.get(cat, 0) + 1

                # Count total questions by category
                total_by_cat = {}
                for qi in qs.get('order', []):
                    cat = QUIZ_QUESTIONS[qi].get('cat', 'general')
                    total_by_cat[cat] = total_by_cat.get(cat, 0) + 1

                # Calculate percentages
                cat_data = []
                for cat in set(wrong_by_cat.keys()).union(set(total_by_cat.keys())):
                    wrong = wrong_by_cat.get(cat, 0)
                    total = total_by_cat.get(cat, 0)
                    pct = (1 - (wrong / total)) * 100 if total > 0 else 100
                    cat_data.append({
                        'category': cat,
                        'correct': total - wrong,
                        'wrong': wrong,
                        'total': total,
                        'percentage': pct
                    })

                # Sort by percentage
                cat_data.sort(key=lambda x: x['percentage'], reverse=True)

                # Display as cards
                for item in cat_data:
                    color = "#00ff88" if item['percentage'] >= 80 else "#00f5ff" if item['percentage'] >= 50 else "#ff9500"
                    st.markdown(f"""
                    <div class='dm-card' style='border-left:4px solid {color};margin:8px 0;'>
                        <div style='display:flex;justify-content:space-between;'>
                            <div>
                                <b>{item['category']}</b><br>
                                <span style='opacity:.6;'>{item['correct']}/{item['total']} correctes</span>
                            </div>
                            <div style='font-weight:bold;color:{color};'>
                                {item['percentage']:.0f}%
                            </div>
                        </div>
                        <div style='margin-top:8px;'>
                            <div style='background:{color};height:4px;border-radius:2px;width:{item['percentage']}%;'></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            # Restart button
            if st.button(f"🔄 {t('restart')}", use_container_width=True, type="primary"):
                st.session_state.quiz_state = {
                    "current": 0, "score": 0, "answered": [],
                    "active": False, "order": [], "wrong": [],
                    "total_q": 0, "finished": False,
                    "selected_answer": None, "show_result": False,
                    "start_time": None, "time_taken": 0
                }
                st.rerun()
# ============================================
#  PAGE: CHATBOT - FULLY ENHANCED
# ============================================
elif pg == "chat":
    st.title(f"💬 {t('chatbot')}")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.session_state.chat_history.append({
            "role": "bot",
            "msg": t("chat_welcome"),
            "time": datetime.now().strftime("%H:%M")
        })

    # ✅ NEW: Enhanced chat container with better scrolling
    chat_container = st.container()
    with chat_container:
        st.markdown("""
        <div id="chat-messages" style="height: 500px; overflow-y: auto; margin-bottom: 20px;
                   border: 1px solid rgba(0,245,255,0.2); border-radius: 12px; padding: 12px;
                   background: rgba(10,15,46,0.3);">
        """, unsafe_allow_html=True)

        for msg_item in st.session_state.chat_history:
            role = "user" if msg_item["role"] == "user" else "bot"
            time_display = f"<span style='opacity:.5;font-size:.7rem;'>[{msg_item['time']}]</span>"

            if role == "user":
                st.markdown(f"""
                <div style='display:flex;justify-content:flex-end;margin:8px 0;'>
                    <div class='dm-ch dm-cu' style='max-width:80%;'>
                        👤 {msg_item['msg']} {time_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='display:flex;justify-content:flex-start;margin:8px 0;'>
                    <div class='dm-ch dm-cb' style='max-width:80%;'>
                        🤖 {msg_item['msg']} {time_display}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("""
        </div>

        <script>
            // Auto-scroll to bottom
            document.addEventListener('DOMContentLoaded', function() {{
                var chat = document.getElementById('chat-messages');
                chat.scrollTop = chat.scrollHeight;
            }});

            // Smooth scrolling for new messages
            function scrollToBottom() {{
                var chat = document.getElementById('chat-messages');
                chat.scrollTo({{top: chat.scrollHeight, behavior: 'smooth'}});
            }}
        </script>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ NEW: Enhanced input area with quick questions
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                t("chat_placeholder"),
                key="chat_input_field",
                label_visibility="collapsed",
                placeholder=t("chat_placeholder")
            )

        with col2:
            if st.form_submit_button("📧", use_container_width=True):
                pass  # Handled below

        submit_col1, submit_col2, submit_col3 = st.columns([3, 2, 1])

        with submit_col1:
            send_btn = st.form_submit_button(
                {
                    "fr": "📨 Envoyer",
                    "ar": "📨 إرسال",
                    "en": "📨 Send"
                }.get(st.session_state.lang, "📨 Send"),
                use_container_width=True
            )

        with submit_col2:
            clear_btn = st.form_submit_button(
                f"🗑️ {t('clear_chat')}",
                use_container_width=True
            )

        with submit_col3:
            voice_btn = st.form_submit_button(
                "🎤",
                use_container_width=True
            )

    # Handle voice input (future implementation)
    if voice_btn:
        st.warning("🎤 Fonctionnalité de reconnaissance vocale en développement")

    # Process user input
    if send_btn and user_input and user_input.strip():
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "msg": user_input.strip(),
            "time": datetime.now().strftime("%H:%M")
        })

        # Get bot response
        reply = chatbot_reply(user_input.strip())

        # Add bot response to history
        st.session_state.chat_history.append({
            "role": "bot",
            "msg": reply,
            "time": datetime.now().strftime("%H:%M")
        })

        # Save to database
        db_chat_save(
            st.session_state.user_id,
            st.session_state.user_name,
            user_input.strip(),
            reply
        )

        # Log activity
        db_log(st.session_state.user_id, st.session_state.user_name, "Chat", user_input[:100])

        # Rerun to update display
        st.rerun()

    # Clear chat history
    if clear_btn:
        if st.button(
            {
                "fr": "⚠️ Confirmer l'effacement",
                "ar": "⚠️ تأكيد المسح",
                "en": "⚠️ Confirm Clear"
            }.get(st.session_state.lang, "⚠️ Confirm"),
            key="confirm_clear"
        ):
            st.session_state.chat_history = []
            st.rerun()

    # ✅ NEW: Quick questions grid
    st.markdown(f"**{t('quick_questions')}**")

    # Group quick questions by category
    quick_categories = {
        "fr": {
            "Parasites": ["Amoeba", "Giardia", "Plasmodium", "Leishmania", "Trypanosoma", "Schistosoma", "Toxoplasma"],
            "Techniques": ["Microscope", "Coloration", "Concentration", "Selle (EPS)"],
            "Traitements": ["Traitement", "Hygiene"],
            "Aide": ["Aide"]
        },
        "ar": {
            "الطفيليات": ["Amoeba", "Giardia", "Plasmodium", "Leishmania", "Trypanosoma", "Schistosoma", "Toxoplasma"],
            "التقنيات": ["Microscope", "Coloration", "Concentration", "Selle"],
            "العلاجات": ["Traitement", "Hygiene"],
            "المساعدة": ["Aide"]
        },
        "en": {
            "Parasites": ["Amoeba", "Giardia", "Plasmodium", "Leishmania", "Trypanosoma", "Schistosoma", "Toxoplasma"],
            "Techniques": ["Microscope", "Staining", "Concentration", "Stool"],
            "Treatments": ["Treatment", "Hygiene"],
            "Help": ["Help"]
        }
    }.get(st.session_state.lang, {})

    for category, questions in quick_categories.items():
        st.markdown(f"**{category}**")
        cols = st.columns(len(questions))
        for col, question in zip(cols, questions):
            with col:
                if st.button(question, key=f"quick_{category}_{question}", use_container_width=True):
                    st.session_state.chat_history.append({
                        "role": "user",
                        "msg": question,
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.session_state.chat_history.append({
                        "role": "bot",
                        "msg": chatbot_reply(question),
                        "time": datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

# ============================================
#  PAGE: COMPARISON - FULLY ENHANCED
# ============================================
elif pg == "cmp":
    st.title(f"🔄 {t('compare')}")

    desc = {
        "fr": "Comparez deux images microscopiques avec analyse avancée des différences",
        "ar": "قارن بين صورتين مجهريتين بتحليل متقدم للاختلافات",
        "en": "Compare two microscopic images with advanced difference analysis"
    }.get(st.session_state.lang, "")

    st.markdown(f"""<div class='dm-card dm-card-cyan'>
    <p style='margin:0;'>{desc}</p>
    </div>""", unsafe_allow_html=True)

    # ✅ NEW: Enhanced file upload with drag and drop simulation
    st.markdown("""
    <style>
        .file-upload-box {
            border: 2px dashed rgba(0,245,255,0.3);
            border-radius: 12px;
            padding: 20px;
            text-align: center;
            margin: 10px 0;
            background: rgba(10,15,46,0.3);
            transition: all 0.3s ease;
        }
        .file-upload-box:hover {
            border-color: rgba(0,245,255,0.6);
            background: rgba(10,15,46,0.4);
        }
        .file-upload-icon {
            font-size: 3rem;
            margin: 10px 0;
            color: rgba(0,245,255,0.7);
        }
    </style>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class='file-upload-box'>
            <div class='file-upload-icon'>📷</div>
            <h4>{t('image1')}</h4>
        </div>
        """, unsafe_allow_html=True)
        f1 = st.file_uploader("img1", type=["jpg", "jpeg", "png", "bmp", "tiff"],
                             key="cmp1", label_visibility="collapsed")

    with c2:
        st.markdown(f"""
        <div class='file-upload-box'>
            <div class='file-upload-icon'>📷</div>
            <h4>{t('image2')}</h4>
        </div>
        """, unsafe_allow_html=True)
        f2 = st.file_uploader("img2", type=["jpg", "jpeg", "png", "bmp", "tiff"],
                             key="cmp2", label_visibility="collapsed")

    if f1 and f2:
        # ✅ NEW: Enhanced image loading with validation
        try:
            i1 = safe_image_open(f1)
            i2 = safe_image_open(f2)

            if i1 is None or i2 is None:
                st.error("❌ Erreur de chargement des images")
                st.stop()

            i1 = resize_image(i1)
            i2 = resize_image(i2)

            c1, c2 = st.columns(2)
            with c1:
                st.image(i1, caption=t("image1"), use_container_width=True)
            with c2:
                st.image(i2, caption=t("image2"), use_container_width=True)

            st.markdown("---")

            # ✅ NEW: Enhanced comparison with multiple methods
            if st.button(f"🔍 {t('compare_btn')}", use_container_width=True, type="primary"):
                with st.spinner("Analyse en cours..."):
                    # Calculate metrics
                    metrics = compare_imgs(i1, i2)

                    # Generate difference images
                    diff_img = pixel_diff(i1, i2)
                    hist1 = histogram(i1)
                    hist2 = histogram(i2)

                # ✅ NEW: Enhanced results display
                st.markdown(f"### 📊 Résultats de la comparaison")

                mc = st.columns(4)
                with mc[0]:
                    st.markdown(f"""<div class='dm-m'>
                    <span class='dm-m-i'>📊</span>
                    <div class='dm-m-v'>{metrics['sim']}%</div>
                    <div class='dm-m-l'>{t('similarity')}</div>
                    </div>""", unsafe_allow_html=True)

                with mc[1]:
                    st.markdown(f"""<div class='dm-m'>
                    <span class='dm-m-i'>🎯</span>
                    <div class='dm-m-v'>{metrics['ssim']}</div>
                    <div class='dm-m-l'>SSIM</div>
                    </div>""", unsafe_allow_html=True)

                with mc[2]:
                    st.markdown(f"""<div class='dm-m'>
                    <span class='dm-m-i'>📐</span>
                    <div class='dm-m-v'>{metrics['mse']}</div>
                    <div class='dm-m-l'>MSE</div>
                    </div>""", unsafe_allow_html=True)

                with mc[3]:
                    if metrics["sim"] > 90:
                        verdict, v_icon, v_color = "Très similaires", "✅", "#00ff88"
                    elif metrics["sim"] > 70:
                        verdict, v_icon, v_color = "Similaires", "🟡", "#ff9500"
                    elif metrics["sim"] > 50:
                        verdict, v_icon, v_color = "Peu similaires", "🟠", "#ff6600"
                    else:
                        verdict, v_icon, v_color = "Très différentes", "❌", "#ff0040"

                    st.markdown(f"""<div class='dm-m'>
                    <span class='dm-m-i'>🔍</span>
                    <div class='dm-m-v' style='font-size:1rem;color:{v_color};'>
                        {v_icon} {verdict}
                    </div>
                    <div class='dm-m-l'>Verdict</div>
                    </div>""", unsafe_allow_html=True)

                # ✅ NEW: SSIM Gauge with enhanced visualization
                if HAS_PLOTLY:
                    st.markdown("---")
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=metrics["sim"],
                        delta={'reference': 70, 'increasing': {'color': "#00ff88"}},
                        title={
                            'text': f"<span style='color:{tx};'>{t('similarity')}</span>",
                            'font': {'color': tx}
                        },
                        number={
                            'font': {'color': '#00f5ff'},
                            'suffix': "%"
                        },
                        gauge={
                            'axis': {'range': [0, 100], 'tickcolor': mu},
                            'bar': {'color': "#00f5ff"},
                            'bgcolor': "rgba(10,15,46,0.5)",
                            'steps': [
                                {'range': [0, 30], 'color': "rgba(255,0,64,0.3)"},
                                {'range': [30, 60], 'color': "rgba(255,149,0,0.3)"},
                                {'range': [60, 80], 'color': "rgba(255,255,0,0.3)"},
                                {'range': [80, 100], 'color': "rgba(0,255,136,0.3)"}
                            ],
                            'threshold': {
                                'line': {'color': "white", 'width': 4},
                                'thickness': 0.75,
                                'value': metrics["sim"]
                            }
                        }
                    ))

                    fig.update_layout(
                        height=280,
                        template=plot_template,
                        margin=dict(l=30, r=30, t=60, b=20),
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={"color": tx}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # ✅ NEW: Pixel difference with enhanced visualization
                st.markdown(f"### 🔍 {t('pixel_diff')}")

                dc1, dc2, dc3 = st.columns(3)
                with dc1:
                    st.image(i1, caption=t("image1"), use_container_width=True)
                with dc2:
                    if diff_img:
                        st.image(diff_img, caption=t("pixel_diff"), use_container_width=True)
                    else:
                        st.error("❌ Erreur de génération de la différence")
                with dc3:
                    st.image(i2, caption=t("image2"), use_container_width=True)

                # ✅ NEW: Filter comparison with enhanced display
                st.markdown(f"### 🔬 {t('filter_comparison')}")

                filter_list = [
                    ({"fr": "Thermique", "ar": "حراري", "en": "Thermal"}, thermal_filter),
                    ({"fr": "Contours", "ar": "حواف", "en": "Edges"}, edges_filter),
                    ({"fr": "Contraste+", "ar": "تباين+", "en": "Enhanced"}, enhanced_filter),
                    ({"fr": "Négatif", "ar": "سلبي", "en": "Negative"}, negative_filter),
                    ({"fr": "Relief", "ar": "نقش", "en": "Emboss"}, emboss_filter),
                ]

                for fname, ffunc in filter_list:
                    fn = tl(fname)
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        st.image(ffunc(i1), caption=f"{t('image1')} - {fn}", use_container_width=True)
                    with fc2:
                        st.image(ffunc(i2), caption=f"{t('image2')} - {fn}", use_container_width=True)

                # ✅ NEW: Histogram comparison with enhanced charts
                if HAS_PLOTLY:
                    hist_label = {
                        "fr": "Comparaison des histogrammes",
                        "ar": "مقارنة المدرجات التكرارية",
                        "en": "Histogram Comparison"
                    }.get(st.session_state.lang, "Histogram")

                    st.markdown(f"### 📊 {hist_label}")

                    hc1, hc2 = st.columns(2)
                    with hc1:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            y=hist1["red"], name="Rouge", line=dict(color="red", width=1)
                        ))
                        fig.add_trace(go.Scatter(
                            y=hist1["green"], name="Vert", line=dict(color="green", width=1)
                        ))
                        fig.add_trace(go.Scatter(
                            y=hist1["blue"], name="Bleu", line=dict(color="blue", width=1)
                        ))
                        fig.update_layout(
                            title=t("image1"),
                            height=250,
                            template=plot_template,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_title="Intensité",
                            yaxis_title="Fréquence"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    with hc2:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            y=hist2["red"], name="Rouge", line=dict(color="red", width=1)
                        ))
                        fig.add_trace(go.Scatter(
                            y=hist2["green"], name="Vert", line=dict(color="green", width=1)
                        ))
                        fig.add_trace(go.Scatter(
                            y=hist2["blue"], name="Bleu", line=dict(color="blue", width=1)
                        ))
                        fig.update_layout(
                            title=t("image2"),
                            height=250,
                            template=plot_template,
                            margin=dict(l=20, r=20, t=40, b=20),
                            xaxis_title="Intensité",
                            yaxis_title="Fréquence"
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # ✅ NEW: Combined histogram comparison
                    st.markdown("#### Comparaison combinée")

                    combined_fig = go.Figure()
                    colors = ["red", "green", "blue"]
                    channels = ["Rouge", "Vert", "Bleu"]

                    for i, channel in enumerate(channels):
                        combined_fig.add_trace(go.Scatter(
                            x=list(range(256)),
                            y=hist1[channel.lower()],
                            name=f"{channel} - Image 1",
                            line=dict(color=colors[i], width=1, dash='solid')
                        ))
                        combined_fig.add_trace(go.Scatter(
                            x=list(range(256)),
                            y=hist2[channel.lower()],
                            name=f"{channel} - Image 2",
                            line=dict(color=colors[i], width=1, dash='dot')
                        ))

                    combined_fig.update_layout(
                        height=300,
                        template=plot_template,
                        margin=dict(l=20, r=20, t=40, b=20),
                        xaxis_title="Intensité (0-255)",
                        yaxis_title="Fréquence",
                        title="Comparaison des histogrammes combinés"
                    )
                    st.plotly_chart(combined_fig, use_container_width=True)

                # ✅ NEW: Image blending comparison
                st.markdown("### 🎨 Comparaison par fusion")

                blend_col1, blend_col2, blend_col3 = st.columns(3)
                with blend_col1:
                    st.markdown("**Image 1 (100%)**")
                    st.image(i1, use_container_width=True)

                with blend_col2:
                    st.markdown("**Fusion 50/50**")
                    blend = Image.blend(i1, i2, 0.5)
                    st.image(blend, use_container_width=True)

                with blend_col3:
                    st.markdown("**Image 2 (100%)**")
                    st.image(i2, use_container_width=True)

                # ✅ NEW: Difference heatmap
                st.markdown("### 🔥 Carte thermique des différences")

                # Calculate absolute difference
                diff_array = np.abs(np.array(i1.convert('L')) - np.array(i2.convert('L')))
                diff_heat = Image.fromarray(diff_array.astype(np.uint8))
                diff_heat = ImageOps.colorize(diff_heat, black="black", white="red")

                st.image(diff_heat, caption="Carte thermique des différences (plus rouge = plus de différences)",
                        use_container_width=True)

                # ✅ NEW: Structural similarity map
                st.markdown("### 🧩 Carte de similarité structurelle")

                # Convert to grayscale
                gray1 = np.array(i1.convert('L'))
                gray2 = np.array(i2.convert('L'))

                # Calculate SSIM map
                ssim_map = np.zeros_like(gray1, dtype=float)
                window_size = 7
                for y in range(window_size//2, gray1.shape[0] - window_size//2):
                    for x in range(window_size//2, gray1.shape[1] - window_size//2):
                        patch1 = gray1[y-window_size//2:y+window_size//2+1,
                                      x-window_size//2:x+window_size//2+1]
                        patch2 = gray2[y-window_size//2:y+window_size//2+1,
                                      x-window_size//2:x+window_size//2+1]

                        m1, m2 = np.mean(patch1), np.mean(patch2)
                        s1, s2 = np.std(patch1), np.std(patch2)
                        s12 = np.mean((patch1 - m1) * (patch2 - m2))

                        c1, c2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
                        ssim_val = ((2 * m1 * m2 + c1) * (2 * s12 + c2)) / ((m1**2 + m2**2 + c1) * (s1**2 + s2**2 + c2))
                        ssim_map[y, x] = ssim_val

                # Normalize and colorize
                ssim_norm = (ssim_map - ssim_map.min()) / (ssim_map.max() - ssim_map.min()) * 255
                ssim_img = Image.fromarray(ssim_norm.astype(np.uint8))
                ssim_img = ImageOps.colorize(ssim_img, black="blue", white="green")

                st.image(ssim_img, caption="Carte de similarité structurelle (SSIM locale)",
                        use_container_width=True)

                # ✅ NEW: Edge difference analysis
                st.markdown("### 📐 Analyse des différences de contours")

                edge1 = edges_filter(i1)
                edge2 = edges_filter(i2)
                edge_diff = pixel_diff(edge1, edge2)

                ec1, ec2, ec3 = st.columns(3)
                with ec1:
                    st.image(edge1, caption="Contours - Image 1", use_container_width=True)
                with ec2:
                    st.image(edge_diff, caption="Différence de contours", use_container_width=True)
                with ec3:
                    st.image(edge2, caption="Contours - Image 2", use_container_width=True)

                # ✅ NEW: Color difference analysis
                st.markdown("### 🎨 Analyse des différences de couleur")

                # Convert to numpy arrays
                arr1 = np.array(i1)
                arr2 = np.array(i2)

                # Calculate channel differences
                diff_r = np.abs(arr1[:,:,0].astype(int) - arr2[:,:,0].astype(int))
                diff_g = np.abs(arr1[:,:,1].astype(int) - arr2[:,:,1].astype(int))
                diff_b = np.abs(arr1[:,:,2].astype(int) - arr2[:,:,2].astype(int))

                # Create difference images
                diff_r_img = Image.fromarray(diff_r.astype(np.uint8))
                diff_g_img = Image.fromarray(diff_g.astype(np.uint8))
                diff_b_img = Image.fromarray(diff_b.astype(np.uint8))

                # Colorize
                diff_r_img = ImageOps.colorize(diff_r_img, black="black", white="red")
                diff_g_img = ImageOps.colorize(diff_g_img, black="black", white="green")
                diff_b_img = ImageOps.colorize(diff_b_img, black="black", white="blue")

                cc1, cc2, cc3 = st.columns(3)
                with cc1:
                    st.image(diff_r_img, caption="Différence - Rouge", use_container_width=True)
                with cc2:
                    st.image(diff_g_img, caption="Différence - Vert", use_container_width=True)
                with cc3:
                    st.image(diff_b_img, caption="Différence - Bleu", use_container_width=True)

                # ✅ NEW: 3D difference visualization
                st.markdown("### 🔮 Visualisation 3D des différences")

                if HAS_PLOTLY:
                    # Create 3D surface plot of differences
                    # Sample a smaller region for performance
                    sample_size = 64
                    diff_sample = cv2.resize(diff_array, (sample_size, sample_size))

                    x = np.arange(0, sample_size, 1)
                    y = np.arange(0, sample_size, 1)
                    X, Y = np.meshgrid(x, y)
                    Z = diff_sample

                    fig = go.Figure(data=[go.Surface(z=Z, colorscale='Viridis')])
                    fig.update_layout(
                        title='Visualisation 3D des différences de pixels',
                        autosize=True,
                        margin=dict(l=0, r=0, b=0, t=30),
                        scene=dict(
                            xaxis_title='X Pixel',
                            yaxis_title='Y Pixel',
                            zaxis_title='Différence'
                        )
                    )
                    st.plotly_chart(fig, use_container_width=True)

    # ============================================
    #  PAGE: ADMIN - FULLY ENHANCED
    # ============================================
    elif pg == "admin":
        st.title(f"⚙️ {t('admin')}")

        if not has_role(3):
            st.error("🔒 Accès administrateur requis")
            st.stop()

        # ✅ NEW: Enhanced admin tabs with icons
        tab1, tab2, tab3, tab4 = st.tabs([
            f"👥 {t('users_mgmt')}",
            f"📜 {t('activity_log')}",
            f"🖥️ {t('system_info')}",
            f"⚙️ Configuration"
        ])

        with tab1:
            # ✅ NEW: Enhanced user management with search and pagination
            st.markdown(f"### 🔍 Recherche d'utilisateurs")
            search_col1, search_col2, search_col3 = st.columns(3)
            with search_col1:
                search_term = st.text_input("Rechercher par nom/utilisateur", key="user_search")
            with search_col2:
                role_filter = st.selectbox("Filtrer par rôle", ["Tous"] + list(ROLES.keys()))
            with search_col3:
                active_filter = st.selectbox("Statut", ["Tous", "Actifs", "Désactivés"])

            # Get users with filters
            users = db_users()

            if search_term:
                users = [u for u in users if (search_term.lower() in u['username'].lower() or
                                             search_term.lower() in u['full_name'].lower())]

            if role_filter != "Tous":
                users = [u for u in users if u['role'] == role_filter]

            if active_filter == "Actifs":
                users = [u for u in users if u['is_active'] == 1]
            elif active_filter == "Désactivés":
                users = [u for u in users if u['is_active'] == 0]

            # Display users in enhanced table
            if users:
                st.markdown(f"### 👥 Liste des utilisateurs ({len(users)})")

                # Create DataFrame with enhanced display
                user_df = pd.DataFrame(users)

                if "last_login" in user_df.columns:
                    user_df["last_login"] = pd.to_datetime(user_df["last_login"])
                    user_df["last_login_display"] = user_df["last_login"].dt.strftime("%d/%m/%Y %H:%M")

                # Role display
                user_df["role_display"] = user_df["role"].apply(
                    lambda x: f"{ROLES.get(x, {}).get('icon', '')} {tl(ROLES.get(x, {}).get('label', {}))}"
                )

                # Active status
                user_df["active_display"] = user_df["is_active"].apply(
                    lambda x: "✅ Actif" if x else "❌ Désactivé"
                )

                # Select columns to display
                display_cols = [
                    "id", "username", "full_name", "role_display",
                    "speciality", "active_display", "last_login_display",
                    "login_count"
                ]
                display_cols = [c for c in display_cols if c in user_df.columns]

                # Enhanced DataFrame display
                st.dataframe(
                    user_df[display_cols],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "id": st.column_config.NumberColumn(
                            "ID",
                            help="Identifiant unique de l'utilisateur"
                        ),
                        "role_display": st.column_config.TextColumn(
                            "Rôle",
                            help="Niveau d'accès de l'utilisateur"
                        ),
                        "active_display": st.column_config.TextColumn(
                            "Statut",
                            help="État du compte (actif/désactivé)"
                        ),
                        "last_login_display": st.column_config.TextColumn(
                            "Dernière connexion",
                            help="Date et heure de la dernière connexion"
                        )
                    }
                )

                st.markdown("---")
                st.markdown("### ➕ Actions sur les utilisateurs")

                # ✅ NEW: User action form
                with st.form("user_action_form"):
                    action_col1, action_col2, action_col3 = st.columns(3)

                    with action_col1:
                        action_user_id = st.selectbox(
                            "Sélectionner utilisateur",
                            options=[(u['id'], f"{u['username']} - {u['full_name']}") for u in users],
                            format_func=lambda x: x[1],
                            key="action_user_select"
                        )

                    with action_col2:
                        action_type = st.selectbox(
                            "Action",
                            ["Modifier rôle", "Changer statut", "Réinitialiser mot de passe"],
                            key="action_type"
                        )

                    with action_col3:
                        submit_action = st.form_submit_button("Exécuter", use_container_width=True)

                    if submit_action and action_user_id:
                        user_id = action_user_id[0]
                        username = next(u['username'] for u in users if u['id'] == user_id)

                        if action_type == "Modifier rôle":
                            new_role = st.selectbox(
                                "Nouveau rôle",
                                list(ROLES.keys()),
                                key="new_role_select"
                            )
                            with get_db() as c:
                                c.execute("UPDATE users SET role=? WHERE id=?", (new_role, user_id))
                            st.success(f"Rôle mis à jour pour {username}")
                            db_log(st.session_state.user_id, st.session_state.user_name,
                                  "Role change", f"User {user_id} → {new_role}")

                        elif action_type == "Changer statut":
                            new_status = st.selectbox(
                                "Nouveau statut",
                                ["Actif", "Désactivé"],
                                key="new_status_select"
                            )
                            new_status_value = 1 if new_status == "Actif" else 0
                            with get_db() as c:
                                c.execute("UPDATE users SET is_active=? WHERE id=?", (new_status_value, user_id))
                            st.success(f"Statut mis à jour pour {username}")
                            db_log(st.session_state.user_id, st.session_state.user_name,
                                  "Status change", f"User {user_id} → {new_status}")

                        elif action_type == "Réinitialiser mot de passe":
                            new_password = st.text_input(
                                "Nouveau mot de passe",
                                type="password",
                                key="new_password_input"
                            )
                            if new_password:
                                db_chpw(user_id, new_password)
                                st.success(f"Mot de passe réinitialisé pour {username}")
                                db_log(st.session_state.user_id, st.session_state.user_name,
                                      "Password reset", f"User {user_id}")
                            else:
                                st.error("Veuillez entrer un mot de passe")

                        st.rerun()

                st.markdown("---")

                # ✅ NEW: Bulk user creation
                with st.expander("📥 Création multiple d'utilisateurs"):
                    bulk_users = st.text_area(
                        "Liste d'utilisateurs (format: username;password;nom complet;rôle)",
                        height=150,
                        placeholder="user1;pass1;Nom User 1;technician\nuser2;pass2;Nom User 2;viewer"
                    )

                    if st.button("Importer les utilisateurs", key="bulk_import"):
                        lines = bulk_users.strip().split('\n')
                        success = 0
                        errors = []

                        for line in lines:
                            if not line.strip():
                                continue

                            parts = [p.strip() for p in line.split(';')]
                            if len(parts) >= 4:
                                username, password, full_name, role = parts[:4]
                                speciality = parts[4] if len(parts) > 4 else "Laboratoire"

                                if db_create_user(username, password, full_name, role, speciality):
                                    success += 1
                                else:
                                    errors.append(username)
                            else:
                                errors.append(f"Format invalide: {line}")

                        if success > 0:
                            st.success(f"✅ {success} utilisateurs créés avec succès")
                        if errors:
                            st.error(f"❌ Erreurs: {', '.join(errors)}")

                        st.rerun()

            else:
                st.info("Aucun utilisateur trouvé")

        with tab2:
            # ✅ NEW: Enhanced activity log with filters
            st.markdown(f"### 🔍 Filtres du journal")

            log_filter_col1, log_filter_col2, log_filter_col3, log_filter_col4 = st.columns(4)

            with log_filter_col1:
                log_user = st.selectbox(
                    "Utilisateur",
                    ["Tous"] + [u['username'] for u in db_users()],
                    key="log_user_filter"
                )

            with log_filter_col2:
                log_action = st.selectbox(
                    "Action",
                    ["Toutes", "Login", "Logout", "Analysis", "Quiz", "Chat", "Admin"],
                    key="log_action_filter"
                )

            with log_filter_col3:
                log_date = st.date_input(
                    "Date",
                    value=datetime.now(),
                    key="log_date_filter"
                )

            with log_filter_col4:
                log_limit = st.selectbox(
                    "Nombre",
                    [20, 50, 100, 200, 500],
                    index=2,
                    key="log_limit_filter"
                )

            # Get filtered logs
            logs = db_logs(log_limit * 2)  # Get more to filter

            if log_user != "Tous":
                logs = [l for l in logs if l['username'] == log_user]

            if log_action != "Toutes":
                logs = [l for l in logs if log_action.lower() in l['action'].lower()]

            if log_date:
                log_date_str = log_date.strftime("%Y-%m-%d")
                logs = [l for l in logs if l['timestamp'].startswith(log_date_str)]

            logs = logs[:log_limit]

            if logs:
                # Create DataFrame with enhanced display
                log_df = pd.DataFrame(logs)

                if "timestamp" in log_df.columns:
                    log_df["timestamp"] = pd.to_datetime(log_df["timestamp"])
                    log_df["time_display"] = log_df["timestamp"].dt.strftime("%d/%m %H:%M")
                    log_df["date_display"] = log_df["timestamp"].dt.strftime("%d/%m/%Y")

                # Display in enhanced table
                st.dataframe(
                    log_df[["username", "action", "details", "time_display", "ip_address"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "username": st.column_config.TextColumn(
                            "Utilisateur",
                            help="Nom d'utilisateur"
                        ),
                        "action": st.column_config.TextColumn(
                            "Action",
                            help="Type d'action effectuée"
                        ),
                        "details": st.column_config.TextColumn(
                            "Détails",
                            help="Informations supplémentaires"
                        ),
                        "time_display": st.column_config.TextColumn(
                            "Heure",
                            help="Date et heure de l'action"
                        ),
                        "ip_address": st.column_config.TextColumn(
                            "IP",
                            help="Adresse IP de l'utilisateur"
                        )
                    }
                )

                # ✅ NEW: Activity statistics
                st.markdown("---")
                st.markdown("### 📊 Statistiques d'activité")

                if logs:
                    # Count by action
                    action_counts = pd.DataFrame(logs)["action"].value_counts()

                    if HAS_PLOTLY:
                        fig = px.bar(
                            action_counts,
                            title="Actions par type",
                            color=action_counts.values,
                            color_continuous_scale="Viridis"
                        )
                        fig.update_layout(
                            height=300,
                            template=plot_template,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Count by user
                    user_counts = pd.DataFrame(logs)["username"].value_counts()

                    if HAS_PLOTLY:
                        fig = px.pie(
                            user_counts,
                            values=user_counts.values,
                            names=user_counts.index,
                            title="Activité par utilisateur",
                            hole=0.4
                        )
                        fig.update_layout(
                            height=300,
                            template=plot_template,
                            margin=dict(l=20, r=20, t=40, b=20)
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    # Count by time
                    if "timestamp" in pd.DataFrame(logs).columns:
                        time_counts = pd.DataFrame(logs)["timestamp"].value_counts().sort_index()

                        if HAS_PLOTLY:
                            fig = px.line(
                                time_counts,
                                title="Activité par heure",
                                markers=True
                            )
                            fig.update_layout(
                                height=300,
                                template=plot_template,
                                margin=dict(l=20, r=20, t=40, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

            else:
                st.info(t("no_data"))

        with tab3:
            # ✅ NEW: Enhanced system information with visualizations
            st.markdown(f"### 🖥️ Informations système")

            # System cards
            sc1, sc2, sc3 = st.columns(3)

            with sc1:
                st.markdown(f"""
                <div class='dm-card dm-card-green'>
                <h4>🟢 État du système</h4>
                <p><b>Version:</b> {APP_VERSION}</p>
                <p><b>Python:</b> {os.sys.version.split()[0]}</p>
                <p><b>Streamlit:</b> {st.__version__}</p>
                <p><b>Sécurité:</b> {'✅ Bcrypt' if HAS_BCRYPT else '❌ SHA256'}</p>
                <p><b>Base de données:</b> SQLite</p>
                <p><b>IP Serveur:</b> {get_client_ip()}</p>
                </div>
                """, unsafe_allow_html=True)

            with sc2:
                ts = db_stats()
                st.markdown(f"""
                <div class='dm-card dm-card-cyan'>
                <h4>📊 Statistiques</h4>
                <p><b>Utilisateurs:</b> {len(db_users())}</p>
                <p><b>Analyses:</b> {ts['total']}</p>
                <p><b>Fiables:</b> {ts['reliable']}</p>
                <p><b>Quiz:</b> {len(db_leaderboard())}</p>
                <p><b>Parasites:</b> {len(CLASS_NAMES)} classes</p>
                <p><b>Questions:</b> {len(QUIZ_QUESTIONS)} quiz</p>
                </div>
                """, unsafe_allow_html=True)

            with sc3:
                dbsz = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
                st.markdown(f"""
                <div class='dm-card'>
                <h4>💾 Stockage</h4>
                <p><b>Taille DB:</b> {dbsz:.1f} KB</p>
                <p><b>Espace disque:</b> {shutil.disk_usage('/').free / (1024**3):.1f} GB libre</p>
                <p><b>Mémoire:</b> {psutil.virtual_memory().available / (1024**3):.1f} GB disponible</p>
                <p><b>CPU:</b> {psutil.cpu_percent()}% utilisé</p>
                <p><b>Démarré:</b> {datetime.fromtimestamp(psutil.boot_time()).strftime('%d/%m %H:%M')}</p>
                </div>
                """, unsafe_allow_html=True)

            # ✅ NEW: System health monitoring
            try:
                import psutil
                import shutil

                st.markdown("---")
                st.markdown("### 🩺 Santé du système")

                # CPU
                cpu_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=psutil.cpu_percent(),
                    title={'text': "Utilisation CPU"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#00f5ff"},
                        'steps': [
                            {'range': [0, 50], 'color': "#00ff88"},
                            {'range': [50, 80], 'color': "#ff9500"},
                            {'range': [80, 100], 'color': "#ff0040"}
                        ]
                    }
                ))
                cpu_fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(cpu_fig, use_container_width=True)

                # Memory
                mem = psutil.virtual_memory()
                mem_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=mem.percent,
                    title={'text': "Utilisation Mémoire"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#ff00ff"},
                        'steps': [
                            {'range': [0, 70], 'color': "#00ff88"},
                            {'range': [70, 90], 'color': "#ff9500"},
                            {'range': [90, 100], 'color': "#ff0040"}
                        ]
                    }
                ))
                mem_fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(mem_fig, use_container_width=True)

                # Disk
                disk = shutil.disk_usage('/')
                disk_fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=disk.used / disk.total * 100,
                    title={'text': "Utilisation Disque"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#0066ff"},
                        'steps': [
                            {'range': [0, 80], 'color': "#00ff88"},
                            {'range': [80, 95], 'color': "#ff9500"},
                            {'range': [95, 100], 'color': "#ff0040"}
                        ]
                    }
                ))
                disk_fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(disk_fig, use_container_width=True)

            except ImportError:
                st.warning("⚠️ Module psutil/shutil non installé - monitoring système désactivé")

            # ✅ NEW: Database analysis
            st.markdown("---")
            st.markdown("### 🗃️ Analyse de la base de données")

            with get_db() as c:
                # Table sizes
                table_sizes = []
                for table in ["users", "analyses", "activity_log", "quiz_scores", "chat_history"]:
                    try:
                        size = c.execute(f"SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size() WHERE tbl_name='{table}'").fetchone()[0]
                        table_sizes.append((table, size / 1024))  # KB
                    except:
                        table_sizes.append((table, 0))

                if table_sizes:
                    df_sizes = pd.DataFrame(table_sizes, columns=["Table", "Taille (KB)"])
                    fig = px.bar(
                        df_sizes,
                        x="Table",
                        y="Taille (KB)",
                        title="Taille des tables de la base de données",
                        color="Taille (KB)",
                        color_continuous_scale="Viridis"
                    )
                    fig.update_layout(
                        height=300,
                        template=plot_template,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Analysis distribution by date
                dates = c.execute("SELECT DATE(analysis_date) as day, COUNT(*) as count FROM analyses GROUP BY day ORDER BY day").fetchall()
                if dates:
                    df_dates = pd.DataFrame(dates, columns=["Jour", "Nombre"])
                    fig = px.line(
                        df_dates,
                        x="Jour",
                        y="Nombre",
                        title="Analyses par jour",
                        markers=True
                    )
                    fig.update_layout(
                        height=300,
                        template=plot_template,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)

        with tab4:
            # ✅ NEW: System configuration
            st.markdown(f"### ⚙️ Configuration du système")

            # App settings
            st.markdown("#### Paramètres de l'application")

            config_col1, config_col2 = st.columns(2)

            with config_col1:
                new_app_name = st.text_input(
                    "Nom de l'application",
                    value="DM Smart Lab AI",
                    key="config_app_name"
                )

                new_version = st.text_input(
                    "Version",
                    value=APP_VERSION,
                    key="config_version"
                )

                new_confidence_threshold = st.number_input(
                    "Seuil de confiance (%)",
                    min_value=10,
                    max_value=90,
                    value=CONFIDENCE_THRESHOLD,
                    key="config_confidence"
                )

            with config_col2:
                new_max_attempts = st.number_input(
                    "Tentatives max avant verrouillage",
                    min_value=3,
                    max_value=10,
                    value=MAX_LOGIN_ATTEMPTS,
                    key="config_max_attempts"
                )

                new_lockout_minutes = st.number_input(
                    "Durée verrouillage (minutes)",
                    min_value=5,
                    max_value=60,
                    value=LOCKOUT_MINUTES,
                    key="config_lockout"
                )

                new_demo_mode = st.checkbox(
                    "Activer le mode démo par défaut",
                    value=False,
                    key="config_demo_mode"
                )

            if st.button("Sauvegarder la configuration", key="save_config"):
                # In a real app, these would be saved to a config file/database
                st.success("✅ Configuration sauvegardée (simulation)")
                db_log(st.session_state.user_id, st.session_state.user_name,
                      "Config update", "Application settings")

            st.markdown("---")

            # Database maintenance
            st.markdown("#### Maintenance de la base de données")

            db_col1, db_col2 = st.columns(2)

            with db_col1:
                if st.button("Optimiser la base de données", key="optimize_db"):
                    with get_db() as c:
                        c.execute("VACUUM")
                        c.execute("ANALYZE")
                    st.success("✅ Base de données optimisée")
                    db_log(st.session_state.user_id, st.session_state.user_name,
                          "DB optimize", "VACUUM + ANALYZE")

                if st.button("Sauvegarder la base de données", key="backup_db"):
                    backup_path = f"dm_smartlab_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db"
                    shutil.copy2(DB_PATH, backup_path)
                    st.success(f"✅ Sauvegarde créée: {backup_path}")
                    db_log(st.session_state.user_id, st.session_state.user_name,
                          "DB backup", backup_path)

            with db_col2:
                if st.button("Réparer la base de données", key="repair_db"):
                    with get_db() as c:
                        c.execute("PRAGMA integrity_check")
                        result = c.fetchone()
                        if result[0] == "ok":
                            st.success("✅ Base de données intacte")
                        else:
                            st.warning("⚠️ Problèmes détectés - réparation recommandée")
                    db_log(st.session_state.user_id, st.session_state.user_name,
                          "DB check", "Integrity check")

                if st.button("Nettoyer les logs anciens", key="clean_logs"):
                    with get_db() as c:
                        c.execute("DELETE FROM activity_log WHERE timestamp < date('now', '-30 day')")
                    st.success("✅ Logs de plus de 30 jours supprimés")
                    db_log(st.session_state.user_id, st.session_state.user_name,
                          "Log cleanup", "Deleted old logs")

            st.markdown("---")

            # ✅ NEW: AI Model configuration
            st.markdown("#### Configuration du modèle IA")

            model_col1, model_col2 = st.columns(2)

            with model_col1:
                st.markdown("**Modèle actuel**")
                mdl, mn, mt = load_model()

                if mn:
                    st.success(f"✅ Modèle chargé: {mn} ({mt})")
                    st.markdown(f"""
                    <div class='dm-card' style='margin-top:12px;'>
                        <p style='margin:0;opacity:.8;'>
                            <b>Type:</b> {mt}<br>
                            <b>Fichier:</b> {mn}<br>
                            <b>Classes:</b> {len(CLASS_NAMES)}<br>
                            <b>Taille entrée:</b> {MODEL_INPUT_SIZE[0]}x{MODEL_INPUT_SIZE[1]}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning("⚠️ Aucun modèle IA chargé (mode démo)")

            with model_col2:
                st.markdown("**Mettre à jour le modèle**")

                new_model = st.file_uploader(
                    "Sélectionner un nouveau modèle",
                    type=[".keras", ".h5", ".tflite"],
                    key="new_model_upload"
                )

                if new_model:
                    model_path = os.path.join("models", new_model.name)
                    os.makedirs("models", exist_ok=True)

                    with open(model_path, "wb") as f:
                        f.write(new_model.getbuffer())

                    st.success(f"✅ Modèle téléchargé: {new_model.name}")

                    if st.button("Charger le nouveau modèle", key="load_new_model"):
                        # In a real app, we would reload the model here
                        st.success("✅ Nouveau modèle chargé (simulation - redémarrage requis)")
                        db_log(st.session_state.user_id, st.session_state.user_name,
                              "Model update", new_model.name)
# ============================================
#  PAGE: ABOUT - FULLY ENHANCED
# ============================================
elif pg == "about":
    st.title(f"ℹ️ {t('about')}")
    lang = st.session_state.lang

    # ✅ NEW: Enhanced about page with interactive elements
    st.markdown(f"""<div class='dm-card dm-card-cyan' style='text-align:center;'>
    <h1 class='dm-nt'>🧬 DM SMART LAB AI v{APP_VERSION}</h1>
    <p style='font-size:1.1rem;font-family:Orbitron,sans-serif;'><b>Space Enhanced Edition</b></p>
    <p style='opacity:.4;'>{t('system_desc')}</p>
    </div>""", unsafe_allow_html=True)

    # Project description with enhanced formatting
    desc_about = {
        "fr": """
        <div style='line-height:1.8;opacity:.8;text-align:justify;'>
            <p><b>DM Smart Lab AI</b> est un système révolutionnaire de diagnostic parasitologique assisté par intelligence artificielle,
            conçu pour les professionnels de santé et les techniciens de laboratoire.</p>

            <p>Ce projet innovant utilise les technologies de <b>Deep Learning</b> et de <b>Vision par Ordinateur</b> pour assister
            dans l'identification rapide et précise des parasites, réduisant ainsi les erreurs de diagnostic et accélérant
            le processus d'analyse.</p>

            <p>Développé à l'<b>INFSPM de Ouargla (Algérie)</b>, ce système représente une avancée majeure dans le domaine
            de la parasitologie médicale, combinant expertise biomédicale et technologies de pointe.</p>
        </div>
        """,
        "ar": """
        <div style='line-height:1.8;opacity:.8;text-align:justify;'>
            <p><b>مختبر DM الذكي</b> هو نظام ثوري لتشخيص الطفيليات باستخدام الذكاء الاصطناعي، مصمم للمهنيين الصحيين وتقنيي المختبرات.</p>

            <p>هذا المشروع المبتكر يستخدم تقنيات <b>التعلم العميق</b> و<b>الرؤية الحاسوبية</b> لمساعدة في التعرف السريع والدقيق على الطفيليات، مما يقلل من أخطاء التشخيص ويعجل عملية التحليل.</p>

            <p>تم تطويره في <b>المعهد الوطني للتكوين العالي شبه الطبي بورقلة (الجزائر)</b>، هذا النظام يمثل قفزة نوعية في مجال علم الطفيليات الطبية، يجمع بين الخبرة الطبية الحيوية والتقنيات المتقدمة.</p>
        </div>
        """,
        "en": """
        <div style='line-height:1.8;opacity:.8;text-align:justify;'>
            <p><b>DM Smart Lab AI</b> is a revolutionary AI-powered parasitological diagnosis system designed for healthcare
            professionals and laboratory technicians.</p>

            <p>This innovative project uses <b>Deep Learning</b> and <b>Computer Vision</b> technologies to assist in the
            rapid and accurate identification of parasites, thereby reducing diagnostic errors and accelerating the analysis
            process.</p>

            <p>Developed at the <b>National Institute of Higher Paramedical Training in Ouargla (Algeria)</b>, this system
            represents a major advancement in the field of medical parasitology, combining biomedical expertise with cutting-edge
            technologies.</p>
        </div>
        """
    }.get(lang, "")

    st.markdown(f"""<div class='dm-card'>
    <h3>📖 {tl(PROJECT_TITLE)}</h3>
    {desc_about}
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ✅ NEW: Interactive team cards
    c1, c2 = st.columns(2)
    with c1:
        d1r = tl(AUTHORS['dev1']['role'])
        st.markdown(f"""
        <div class='dm-card dm-card-cyan' style='text-align:center;'>
            <div style='font-size:3rem;margin:10px 0;'>👨‍💻</div>
            <h4 style='margin:0;'>{AUTHORS['dev1']['name']}</h4>
            <p style='margin:0;opacity:.6;'>{d1r}</p>

            <div style='margin-top:12px;background:rgba(0,245,255,0.1);padding:8px;border-radius:8px;'>
                <p style='margin:0;opacity:.8;font-size:.8rem;'>
                    <b>📧:</b> {AUTHORS['dev1']['email']}<br>
                    <b>🎓:</b> INFSPM Ouargla<br>
                    <b>💡:</b> Expert en IA et Conception
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        d2r = tl(AUTHORS['dev2']['role'])
        st.markdown(f"""
        <div class='dm-card dm-card-cyan' style='text-align:center;'>
            <div style='font-size:3rem;margin:10px 0;'>🔬</div>
            <h4 style='margin:0;'>{AUTHORS['dev2']['name']}</h4>
            <p style='margin:0;opacity:.6;'>{d2r}</p>

            <div style='margin-top:12px;background:rgba(0,245,255,0.1);padding:8px;border-radius:8px;'>
                <p style='margin:0;opacity:.8;font-size:.8rem;'>
                    <b>📧:</b> {AUTHORS['dev2']['email']}<br>
                    <b>🎓:</b> INFSPM Ouargla<br>
                    <b>💡:</b> Expert en Laboratoire
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ NEW: Institution information with map
    inst_col1, inst_col2 = st.columns(2)

    with inst_col1:
        st.markdown(f"""
        <div class='dm-card'>
        <h3>🏫 {t('institution')}</h3>
        <br>
        <p><b>{tl(INSTITUTION['name'])}</b></p>
        <p>📍 {INSTITUTION['city']}, {tl(INSTITUTION['country'])} 🇩🇿</p>
        <p>🌐 {INSTITUTION['website']}</p>
        <p>📅 Fondé en {INSTITUTION['year']}</p>
        <br>
        <h4>🎯 Objectifs du projet</h4>
        <ul>
            <li>Automatiser la lecture microscopique des parasites</li>
            <li>Réduire les erreurs de diagnostic</li>
            <li>Accélérer le processus d'analyse</li>
            <li>Améliorer l'accès aux soins dans les zones reculées</li>
            <li>Former les techniciens aux nouvelles technologies</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with inst_col2:
        # ✅ NEW: Interactive map (simulated)
        st.markdown("""
        <div class='dm-card' style='height:300px;position:relative;'>
            <div style='position:absolute;top:0;left:0;width:100%;height:100%;background:linear-gradient(135deg,#0a0f2e,#1a1f3a);border-radius:12px;'></div>

            <div style='position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:white;text-align:center;'>
                <div style='font-size:2rem;'>📍</div>
                <div style='font-family:Orbitron;font-size:1.2rem;'>Ouargla, Algérie</div>
                <div style='opacity:.7;font-size:.8rem;'>31.9500° N, 5.3167° E</div>
            </div>

            <div style='position:absolute;bottom:10px;left:10px;background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:4px;font-size:.7rem;'>
                Carte interactive (simulation)
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ NEW: Technologies with interactive cards
    st.markdown(f"### 🛠️ {t('technologies')}")

    tech_categories = {
        "fr": {
            "Backend": [
                ("Python 3.9+", "🐍", "Langage principal"),
                ("TensorFlow", "🧠", "Deep Learning"),
                ("SQLite", "🗃️", "Base de données"),
                ("Bcrypt", "🔒", "Sécurité")
            ],
            "Frontend": [
                ("Streamlit", "🎨", "Interface utilisateur"),
                ("Plotly", "📊", "Visualisations"),
                ("HTML/CSS", "🌐", "Design personnalisé")
            ],
            "Outils": [
                ("Pillow", "🖼️", "Traitement d'images"),
                ("FPDF", "📄", "Génération PDF"),
                ("QR Code", "🔲", "Vérification")
            ]
        },
        "ar": {
            "الخلفية": [
                ("Python 3.9+", "🐍", "لغة رئيسية"),
                ("TensorFlow", "🧠", "تعلم عميق"),
                ("SQLite", "🗃️", "قاعدة بيانات"),
                ("Bcrypt", "🔒", "أمان")
            ],
            "الواجهة": [
                ("Streamlit", "🎨", "واجهة مستخدم"),
                ("Plotly", "📊", "تصور بياني"),
                ("HTML/CSS", "🌐", "تصميم مخصص")
            ],
            "الأدوات": [
                ("Pillow", "🖼️", "معالجة صور"),
                ("FPDF", "📄", "توليد PDF"),
                ("QR Code", "🔲", "تحقق")
            ]
        },
        "en": {
            "Backend": [
                ("Python 3.9+", "🐍", "Main language"),
                ("TensorFlow", "🧠", "Deep Learning"),
                ("SQLite", "🗃️", "Database"),
                ("Bcrypt", "🔒", "Security")
            ],
            "Frontend": [
                ("Streamlit", "🎨", "User Interface"),
                ("Plotly", "📊", "Visualizations"),
                ("HTML/CSS", "🌐", "Custom Design")
            ],
            "Tools": [
                ("Pillow", "🖼️", "Image Processing"),
                ("FPDF", "📄", "PDF Generation"),
                ("QR Code", "🔲", "Verification")
            ]
        }
    }.get(lang, {})

    for category, techs in tech_categories.items():
        st.markdown(f"**{category}**")
        tech_cols = st.columns(len(techs))
        for col, (name, icon, desc) in zip(tech_cols, techs):
            with col:
                st.markdown(f"""
                <div class='dm-card' style='padding:14px;text-align:center;height:100%;'>
                    <div style='font-size:1.8rem;margin-bottom:8px;'>{icon}</div>
                    <p style='font-weight:700;margin:4px 0;font-size:.85rem;'>{name}</p>
                    <p style='font-size:.7rem;opacity:.7;'>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ NEW: Features showcase with animations
    st.markdown(f"### 🌟 Fonctionnalités principales (v{APP_VERSION})")

    features = {
        "fr": [
            ("📸 Capture intelligente", "Interface caméra optimisée avec grille de centrage et conseils en temps réel"),
            ("🧠 Diagnostic IA", "7 parasites détectés avec niveau de confiance et recommandations médicales"),
            ("📊 Tableau de bord", "Analytique avancée avec tendances, distribution et métriques de performance"),
            ("💬 Assistant conversationnel", "Chatbot spécialisé en parasitologie avec base de connaissances complète"),
            ("🔄 Comparaison avancée", "Analyse pixel par pixel, filtres, histogrammes et visualisations 3D"),
            ("📘 Encyclopédie interactive", "Base de données complète avec morphologie, cycles de vie et clés diagnostiques"),
            ("🧠 Quiz médical", "Système d'évaluation avec classement, catégories et analyse des performances"),
            ("📄 Rapports PDF", "Génération de rapports professionnels avec QR codes et signatures numériques"),
            ("🌍 Multilingue", "Interface complète en Français, Arabe et Anglais"),
            ("🔒 Sécurité", "Authentification sécurisée, journalisation et contrôle d'accès basé sur les rôles"),
            ("🎨 Thème spatial", "Design moderne avec animations et effets visuels immersifs"),
            ("📱 Responsive", "Adapté aux mobiles, tablettes et écrans larges")
        ],
        "ar": [
            ("📸 التقاط ذكي", "واجهة كاميرا محسنة مع شبكة مركزية ونصائح فورية"),
            ("🧠 تشخيص بالذكاء الاصطناعي", "7 طفيليات مكتشفة مع مستوى ثقة وتوصيات طبية"),
            ("📊 لوحة تحكم", "تحليلات متقدمة مع اتجاهات وتوزيع ومقاييس أداء"),
            ("💬 مساعد محادثة", "روبوت دردشة متخصص في علم الطفيليات مع قاعدة معرفية كاملة"),
            ("🔄 مقارنة متقدمة", "تحليل بكسل بكسل، فلاتر، مدرجات تكرارية وتصورات ثلاثية الأبعاد"),
            ("📘 موسوعة تفاعلية", "قاعدة بيانات كاملة مع مورفولوجيا ودورات حياة ومفاتيح تشخيصية"),
            ("🧠 اختبار طبي", "نظام تقييم مع ترتيب وفئات وتحليل أداء"),
            ("📄 تقارير PDF", "توليد تقارير مهنية مع أكواد QR وتوقيعات رقمية"),
            ("🌍 متعدد اللغات", "واجهة كاملة بالفرنسية والعربية والإنجليزية"),
            ("🔒 أمان", "مصادقة آمنة، تسجيلات ومراقبة وصول بناءً على الأدوار"),
            ("🎨 موضوع فضائي", "تصميم عصري مع رسوم متحركة وتأثيرات بصرية غامرة"),
            ("📱 متجاوب", "متوافق مع الهواتف اللوحية والهواتف الذكية والشاشات الكبيرة")
        ],
        "en": [
            ("📸 Smart Capture", "Optimized camera interface with centering grid and real-time tips"),
            ("🧠 AI Diagnosis", "7 parasites detected with confidence levels and medical recommendations"),
            ("📊 Dashboard", "Advanced analytics with trends, distribution and performance metrics"),
            ("💬 Chat Assistant", "Parasitology-specialized chatbot with comprehensive knowledge base"),
            ("🔄 Advanced Comparison", "Pixel-by-pixel analysis, filters, histograms and 3D visualizations"),
            ("📘 Interactive Encyclopedia", "Complete database with morphology, life cycles and diagnostic keys"),
            ("🧠 Medical Quiz", "Evaluation system with leaderboard, categories and performance analysis"),
            ("📄 PDF Reports", "Professional report generation with QR codes and digital signatures"),
            ("🌍 Multilingual", "Complete interface in French, Arabic and English"),
            ("🔒 Security", "Secure authentication, logging and role-based access control"),
            ("🎨 Space Theme", "Modern design with animations and immersive visual effects"),
            ("📱 Responsive", "Adapted for mobile, tablet and large screens")
        ]
    }.get(lang, [])

    feature_cols = st.columns(3)
    for i, (icon, title, desc) in enumerate(features):
        with feature_cols[i % 3]:
            st.markdown(f"""
            <div class='dm-card' style='padding:16px;height:100%;'>
                <div style='font-size:1.5rem;margin-bottom:8px;'>{icon}</div>
                <h5 style='margin:0 0 8px 0;'>{title}</h5>
                <p style='font-size:.8rem;opacity:.8;line-height:1.4;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ✅ NEW: Project timeline
    st.markdown(f"### 📅 Chronologie du projet")

    timeline = {
        "fr": [
            ("2022 - Q1", "💡 Idée initiale et recherche préliminaire"),
            ("2022 - Q2", "📚 Collecte de données et annotation d'images"),
            ("2022 - Q3", "🧠 Développement du modèle IA (v1.0)"),
            ("2022 - Q4", "🎨 Création de l'interface utilisateur initiale"),
            ("2023 - Q1", "🔬 Tests en laboratoire et validation"),
            ("2023 - Q2", "📊 Ajout du tableau de bord et analytique"),
            ("2023 - Q3", "💬 Intégration du chatbot et encyclopédie"),
            ("2023 - Q4", "🔄 Système de comparaison avancée"),
            ("2024 - Q1", "🧠 Quiz médical et système de scoring"),
            ("2024 - Q2", "📄 Génération de rapports PDF professionnelle"),
            ("2024 - Q3", "🌍 Support multilingue complet"),
            ("2024 - Q4", "🎨 Thème spatial et animations (v8.0)")
        ],
        "ar": [
            ("2022 - الربع الأول", "💡 الفكرة الأولية والبحث الأولي"),
            ("2022 - الربع الثاني", "📚 جمع البيانات وتهيئة الصور"),
            ("2022 - الربع الثالث", "🧠 تطوير نموذج الذكاء الاصطناعي (v1.0)"),
            ("2022 - الربع الرابع", "🎨 إنشاء واجهة المستخدم الأولية"),
            ("2023 - الربع الأول", "🔬 اختبارات مخبرية وتحقق"),
            ("2023 - الربع الثاني", "📊 إضافة لوحة التحكم والتحليلات"),
            ("2023 - الربع الثالث", "💬 دمج روبوت الدردشة والموسوعة"),
            ("2023 - الربع الرابع", "🔄 نظام مقارنة متقدم"),
            ("2024 - الربع الأول", "🧠 اختبار طبي ونظام التسجيل"),
            ("2024 - الربع الثاني", "📄 توليد تقارير PDF مهنية"),
            ("2024 - الربع الثالث", "🌍 دعم متعدد اللغات كامل"),
            ("2024 - الربع الرابع", "🎨 موضوع فضائي ورسوم متحركة (v8.0)")
        ],
        "en": [
            ("2022 - Q1", "💡 Initial idea and preliminary research"),
            ("2022 - Q2", "📚 Data collection and image annotation"),
            ("2022 - Q3", "🧠 AI model development (v1.0)"),
            ("2022 - Q4", "🎨 Initial user interface creation"),
            ("2023 - Q1", "🔬 Laboratory testing and validation"),
            ("2023 - Q2", "📊 Dashboard and analytics addition"),
            ("2023 - Q3", "💬 Chatbot and encyclopedia integration"),
            ("2023 - Q4", "🔄 Advanced comparison system"),
            ("2024 - Q1", "🧠 Medical quiz and scoring system"),
            ("2024 - Q2", "📄 Professional PDF report generation"),
            ("2024 - Q3", "🌍 Complete multilingual support"),
            ("2024 - Q4", "🎨 Space theme and animations (v8.0)")
        ]
    }.get(lang, [])

    # ✅ NEW: Interactive timeline visualization
    if HAS_PLOTLY:
        df_timeline = pd.DataFrame(timeline, columns=["Période", "Événement"])
        df_timeline["Année"] = df_timeline["Période"].str.extract(r'(\d{4})').astype(int)
        df_timeline["Trimestre"] = df_timeline["Période"].str.extract(r'Q(\d)').astype(int)
        df_timeline["Ordre"] = range(len(df_timeline))

        fig = px.timeline(
            df_timeline,
            x_start="Année",
            x_end="Année",
            y="Ordre",
            text="Événement",
            color="Trimestre",
            color_discrete_sequence=px.colors.qualitative.Set1
        )

        fig.update_yaxes(visible=False, showticklabels=False)
        fig.update_layout(
            height=400,
            template=plot_template,
            margin=dict(l=20, r=20, t=40, b=20),
            title="Chronologie du développement du projet",
            hovermode="x"
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        # Fallback to simple list
        for period, event in timeline:
            st.markdown(f"- **{period}**: {event}")

    st.markdown("---")

    # ✅ NEW: Future developments
    st.markdown(f"### 🚀 Développements futurs")

    future_dev = {
        "fr": [
            "📱 Application mobile native (iOS/Android)",
            "🌐 Intégration avec les systèmes hospitaliers (HL7/FHIR)",
            "🧬 Détection de mutations et résistance aux médicaments",
            "🤖 Assistant vocal complet pour les rapports",
            "🔍 Détection en temps réel avec caméra microscopique connectée",
            "🌍 Déploiement cloud pour accès mondial",
            "📚 Base de connaissances étendue avec IA générative",
            "🎓 Programme de certification pour techniciens"
        ],
        "ar": [
            "📱 تطبيق موبايل أصلي (iOS/Android)",
            "🌐 دمج مع أنظمة المستشفى (HL7/FHIR)",
            "🧬 كشف الطفرات ومقاومة الأدوية",
            "🤖 مساعد صوتي كامل للتقارير",
            "🔍 كشف في الوقت الفعلي بكاميرا مجهرية متصلة",
            "🌍 نشر سحابي للوصول العالمي",
            "📚 قاعدة معرفية موسعة مع ذكاء اصطناعي توليدي",
            "🎓 برنامج شهادة لتقنيي المختبرات"
        ],
        "en": [
            "📱 Native mobile application (iOS/Android)",
            "🌐 Integration with hospital systems (HL7/FHIR)",
            "🧬 Mutation and drug resistance detection",
            "🤖 Full voice assistant for reports",
            "🔍 Real-time detection with connected microscope camera",
            "🌍 Cloud deployment for global access",
            "📚 Expanded knowledge base with generative AI",
            "🎓 Certification program for laboratory technicians"
        ]
    }.get(lang, [])

    for item in future_dev:
        st.markdown(f"- {item}")

    st.markdown("---")

    # ✅ NEW: Contact and support
    st.markdown(f"### 📧 Contact et support")

    contact_cols = st.columns(2)
    with contact_cols[0]:
        st.markdown("""
        <div class='dm-card'>
        <h4>📩 Support technique</h4>
        <p style='margin:4px 0;'><b>Email:</b> support@dmsmartlab.dz</p>
        <p style='margin:4px 0;'><b>Téléphone:</b> +213 (0) 12 34 56 78</p>
        <p style='margin:4px 0;'><b>Heures:</b> 8h-16h (Dimanches-Thursdays)</p>
        </div>
        """, unsafe_allow_html=True)

    with contact_cols[1]:
        st.markdown("""
        <div class='dm-card'>
        <h4>🌐 Ressources en ligne</h4>
        <p style='margin:4px 0;'><b>Site web:</b> www.dmsmartlab.dz</p>
        <p style='margin:4px 0;'><b>Documentation:</b> docs.dmsmartlab.dz</p>
        <p style='margin:4px 0;'><b>GitHub:</b> github.com/dmsmartlab</p>
        <p style='margin:4px 0;'><b>YouTube:</b> youtube.com/dmsmartlab</p>
        </div>
        """, unsafe_allow_html=True)

    # ✅ NEW: Feedback form
    st.markdown("---")
    st.markdown(f"### 💬 Vos retours")

    with st.form("feedback_form"):
        feedback_type = st.selectbox(
            "Type de retour",
            ["👍 Retour positif", "💡 Suggestion", "⚠️ Problème technique", "🐛 Bug"],
            key="feedback_type"
        )

        feedback_text = st.text_area(
            "Votre message",
            height=120,
            key="feedback_text"
        )

        feedback_rating = st.slider(
            "Note globale (1-5)",
            1, 5, 5,
            key="feedback_rating"
        )

        if st.form_submit_button("Envoyer", use_container_width=True):
            if feedback_text.strip():
                db_log(st.session_state.user_id, st.session_state.user_name,
                      "Feedback", f"Type: {feedback_type}, Rating: {feedback_rating}, Text: {feedback_text[:200]}")
                st.success("✅ Merci pour votre retour ! Il nous aide à améliorer le système.")
            else:
                st.error("❌ Veuillez entrer votre message")

    # Footer with credits
    st.markdown("---")
    made_label = {
        "fr": "Fait avec",
        "ar": "صنع بـ",
        "en": "Made with"
    }.get(lang, "Made with")

    in_label = {
        "fr": "à",
        "ar": "في",
        "en": "in"
    }.get(lang, "in")

    st.caption(f"""
    {made_label} ❤️ {in_label} {INSTITUTION['city']} — {INSTITUTION['year']} 🇩🇿
    <br><br>
    Tous droits réservés © {datetime.now().year} - INFSPM Ouargla
    <br>
    Version {APP_VERSION} - Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y')}
    """, unsafe_allow_html=True)

# ============================================
#  FINAL ENHANCEMENTS AND FIXES
# ============================================

# ✅ NEW: Global error handler
def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if isinstance(exc_value, KeyboardInterrupt):
        return  # Let Streamlit handle this

    st.error(f"❌ Une erreur inattendue est survenue: {exc_value}")
    db_log(st.session_state.get("user_id"), st.session_state.get("user_name"),
          "System Error", str(exc_value))

    # In development, show traceback
    if os.getenv("DEBUG", "false").lower() == "true":
        import traceback
        st.code(traceback.format_exc())

# Set as global exception handler
import sys
sys.excepthook = handle_exception

# ✅ NEW: Performance monitoring
if "performance_metrics" not in st.session_state:
    st.session_state.performance_metrics = {
        "page_loads": 0,
        "last_load_time": time.time(),
        "actions": []
    }

# Track page loads
st.session_state.performance_metrics["page_loads"] += 1
st.session_state.performance_metrics["last_load_time"] = time.time()

# ✅ NEW: Session cleanup on page change
if "current_page" in st.session_state and st.session_state.current_page != pg:
    # Clean up temporary files
    for f in os.listdir("."):
        if f.startswith("temp_") or f.startswith("_qr_"):
            try:
                os.remove(f)
            except:
                pass

    st.session_state.current_page = pg

# ✅ NEW: Mobile responsiveness improvements
st.markdown("""
<style>
    @media (max-width: 768px) {
        .stButton > button {
            padding: 8px 16px !important;
            font-size: .8rem !important;
        }

        .dm-card {
            padding: 16px !important;
        }

        section[data-testid="stSidebar"] {
            width: 100% !important;
        }

        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            padding: 8px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ✅ NEW: Final check for missing dependencies
missing_deps = []
if not HAS_PLOTLY:
    missing_deps.append("plotly (visualisations)")
if not HAS_QRCODE:
    missing_deps.append("qrcode (génération QR)")
if not HAS_BCRYPT:
    missing_deps.append("bcrypt (sécurité améliorée)")

if missing_deps:
    st.sidebar.warning(f"⚠️ Dépendances manquantes: {', '.join(missing_deps)}")

# ✅ NEW: Debug information (for development)
if os.getenv("DEBUG", "false").lower() == "true":
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🐛 Debug Information**")
    st.sidebar.markdown(f"""
    - **Session ID**: {hash(st.session_state) if st.session_state else 'None'}
    - **User**: {st.session_state.get('user_name', 'None')}
    - **Page**: {pg}
    - **Loads**: {st.session_state.performance_metrics['page_loads']}
    - **Time**: {time.time() - st.session_state.performance_metrics['last_load_time']:.2f}s
    """)

    if st.sidebar.button("🔄 Recharge forcer"):
        st.experimental_rerun()

# Run the main function
if __name__ == "__main__":
    main()
