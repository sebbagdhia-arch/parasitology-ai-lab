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
#  UTILITY FUNCTIONS - ENHANCED WITH STREAMLIT FIXES
# ============================================
def has_role(lvl):
    """Check user role level - Fixed for session state"""
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
    """Get client IP address - Fixed for Streamlit Cloud"""
    try:
        # Works in Streamlit Cloud
        return st.experimental_connection_info().client.ip
    except:
        try:
            # Fallback for local development
            import socket
            return socket.gethostbyname(socket.gethostname())
        except:
            return "unknown"

# ============================================
#  IMAGE PROCESSING - FIXED FOR STREAMLIT
# ============================================
def safe_image_open(img_data):
    """Safely open image from various sources - Fixed for Streamlit uploads"""
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
            # File-like object (Streamlit upload)
            return Image.open(img_data)
        elif isinstance(img_data, bytes):
            # Raw bytes
            return Image.open(io.BytesIO(img_data))
        else:
            # PIL Image
            return img_data
    except Exception as e:
        st.error(f"❌ Erreur de chargement de l'image: {e}")
        return None

def resize_image(img, max_size=(1200, 1200)):
    """Resize image while maintaining aspect ratio - Fixed for large images"""
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
        st.error(f"❌ Erreur de redimensionnement: {e}")
        return None

def gen_heatmap(img, seed=None):
    """Generate AI heatmap overlay - Fixed for Streamlit display"""
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
        st.error(f"❌ Erreur de génération de heatmap: {e}")
        return img

# ✅ NEW: Fallback functions for unsupported features
def thermal_filter_fallback(img):
    """Fallback thermal filter using simple color manipulation"""
    if img is None:
        return None
    try:
        # Simple red color overlay for fallback
        overlay = Image.new('RGB', img.size, (255, 0, 0, 128))
        return Image.blend(img.convert('RGB'), overlay, 0.3)
    except:
        return img

def edges_filter_fallback(img):
    """Fallback edge detection using simple sobel"""
    if img is None:
        return None
    try:
        # Simple sobel edge detection
        img = img.convert('L')
        arr = np.array(img)
        gx = cv2.Sobel(arr, cv2.CV_64F, 1, 0, ksize=3)
        gy = cv2.Sobel(arr, cv2.CV_64F, 0, 1, ksize=3)
        edges = np.sqrt(gx**2 + gy**2)
        edges = (edges / edges.max() * 255).astype(np.uint8)
        return Image.fromarray(edges)
    except:
        return img.convert('L')

# ============================================
#  VOICE SYSTEM - COMPLETELY REWRITTEN FOR STREAMLIT
# ============================================
def render_voice_player():
    """Render voice player using HTML5 Audio as fallback"""
    if not st.session_state.get("voice_text"):
        return

    text = st.session_state.voice_text.replace("'", "\\'").replace('"', '\\"')
    lang_code = {"fr": "fr-FR", "ar": "ar-SA", "en": "en-US"}.get(
        st.session_state.get("voice_lang", st.session_state.get("lang", "fr")), "fr-FR")

    # ✅ NEW: HTML5 Audio fallback for browsers without Web Speech API
    html_code = f"""
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999;">
        <audio id="voiceAudio" style="display: none;" controls>
            <source src="data:audio/mpeg;base64,{base64.b64encode(b'').decode()}" type="audio/mpeg">
        </audio>

        <div style="display: flex; gap: 8px;">
            <button id="playBtn" onclick="playVoice()" style="
                background: linear-gradient(135deg, #00f5ff, #0066ff);
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 20px;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,245,255,0.3);
            ">🔊</button>

            <button id="stopBtn" onclick="stopVoice()" style="
                background: #ff0040;
                color: white;
                border: none;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                font-size: 20px;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(255,0,64,0.3);
                display: none;
            ">🛑</button>
        </div>
    </div>

    <script>
        // Text-to-speech using Web Speech API
        function playVoice() {{
            document.getElementById('playBtn').style.display = 'none';
            document.getElementById('stopBtn').style.display = 'block';

            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();

                const utterance = new SpeechSynthesisUtterance(`{text}`);
                utterance.lang = '{lang_code}';
                utterance.rate = 0.9;
                utterance.pitch = 1.0;

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
                // Fallback: Show message if not supported
                alert('La synthèse vocale n\'est pas supportée par votre navigateur. Utilisez Chrome/Edge pour une meilleure expérience.');
                document.getElementById('playBtn').style.display = 'block';
                document.getElementById('stopBtn').style.display = 'none';
            }}
        }}

        function stopVoice() {{
            document.getElementById('playBtn').style.display = 'block';
            document.getElementById('stopBtn').style.display = 'none';

            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
            }}
        }}
    </script>
    """

    components.html(html_code, height=0)
    st.session_state.voice_text = None
    st.session_state.voice_lang = None

def speak(text, lang=None):
    """Queue text for speaking - Fixed for Streamlit rerun"""
    st.session_state.voice_text = text
    st.session_state.voice_lang = lang or st.session_state.get("lang", "fr")
    st.rerun()

def stop_speech():
    """Stop speech - Fixed for Streamlit"""
    st.session_state.voice_text = None
    st.session_state.voice_lang = None
    st.rerun()

# ============================================
#  AI ENGINE - ENHANCED WITH FALLBACKS
# ============================================
@st.cache_resource(show_spinner=False)
def load_model():
    """Load AI model with enhanced error handling and fallbacks"""
    m, mn, mt = None, None, None
    try:
        import tensorflow as tf
        from tensorflow.keras.models import load_model

        # Check for different model formats
        model_dirs = ["models", "."]  # Look in models/ directory first
        for dir in model_dirs:
            if os.path.exists(dir):
                for ext in [".keras", ".h5"]:
                    files = [f for f in os.listdir(dir) if f.endswith(ext)]
                    if files:
                        mn = os.path.join(dir, files[0])
                        m = load_model(mn, compile=False)
                        mt = "keras"
                        break
                if m is not None:
                    break

        if m is None:
            for dir in model_dirs:
                if os.path.exists(dir):
                    files = [f for f in os.listdir(dir) if f.endswith(".tflite")]
                    if files:
                        mn = os.path.join(dir,
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
