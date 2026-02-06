import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import requests
from streamlit_lottie import st_lottie

# --- Configuration de la Page ---
st.set_page_config(
    page_title="Microscope IA | DHIA & MOUHAMED",
    page_icon="🔬",
    layout="centered"
)

# --- Fonction pour charger les animations Lottie ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Animation d'un microscope (Visuel pour le labo)
lottie_micro = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_ym8w5lcs.json")

# --- Barre Latérale (Sidebar) ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🎓 Projet de Fin d'Études</h2>", unsafe_allow_html=True)
    st.write("---")
    st.write("👨‍🔬 **Réalisé par :**")
    st.info("**DHIA**")
    st.info("**MOUHAMED**")
    st.write("---")
    st.write("**Spécialité :** Parasitologie & IA")
    st.success("Système automatisé d'identification des parasites.")

# --- En-tête Principal ---
if lottie_micro:
    st_lottie(lottie_micro, height=200, key="microscope")

st.markdown("""
    <h1 style='text-align: center; color: #2E86C1;'>🔬 Laboratoire Intelligent de Parasitologie</h1>
    <h3 style='text-align: center; color: #566573;'>Bienvenue dans l'application de DHIA et MOUHAMED</h3>
    <p style='text-align: center;'>Analyse morphologique assistée par Intelligence Artificielle</p>
    <hr>
""", unsafe_allow_html=True)

# --- Base de Données Morphologique (Structure détaillée) ---
# Note : Les clés doivent correspondre aux noms dans votre fichier labels.txt
morphology_db = {
    "Amoeba": {
        "title": "Entamoeba histolytica",
        "structure": "Forme irrégulière avec présence de pseudopodes.",
        "details": "Noyau sphérique avec un petit endosome central (caryosome). Cytoplasme granulaire.",
        "note": "Cherchez des hématies phagocytées pour confirmer le caractère pathogène."
    },
    "Giardia": {
        "title": "Giardia lamblia",
        "structure": "Forme de poire (pyriforme), symétrie bilatérale.",
        "details": "Deux noyaux (aspect de lunettes), quatre paires de flagelles et un axostyle central.",
        "note": "Se présente sous forme de trophozoïte (mobile) ou de kyste (ovale)."
    },
    "Leishmania": {
        "title": "Leishmania (Amastigote)",
        "structure": "Forme ovoïde ou arrondie très petite (2-5 µm).",
        "details": "Présence d'un noyau et d'un kinétoplaste en forme de bâtonnet.",
        "note": "S'observe principalement à l'intérieur des cellules mononucléées."
    },
    "Plasmodium": {
        "title": "Plasmodium (Paludisme)",
        "structure": "Forme en anneau (Ring form) à l'intérieur des globules rouges.",
        "details": "Petit point de chromatine rouge relié à un anneau de cytoplasme bleu.",
        "note": "Le diagnostic dépend de la densité parasitaire observée sur frottis."
    },
    "Trypanosoma": {
        "title": "Trypanosoma spp.",
        "structure": "Forme allongée, fusiforme avec un flagelle libre.",
        "details": "Membrane ondulante visible et noyau central volumineux.",
        "note": "Parasite extracellulaire visible dans le plasma sanguin."
    },
    "Schistosoma": {
        "title": "Schistosoma (Œuf)",
        "structure": "Œuf de grande taille avec une coque transparente.",
        "details": "Présence d'un éperon (épine) latéral ou terminal caractéristique.",
        "note": "L'identification de l'épine permet de différencier les espèces (Mansoni vs Haematobium)."
    },
    "Negative": {
        "title": "Échantillon Négatif",
        "structure": "Absence de parasites.",
        "details": "Présence d'éléments cellulaires normaux, débris ou artefacts de coloration.",
        "note": "Vérifiez plusieurs champs microscopiques avant de conclure."
    }
}

# --- Fonction de Chargement du Modèle ---
@st.cache_resource
def load_ai_model():
    m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
    l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f.lower()), None)
    
    if m_path and l_path:
        model = tf.keras.models.load_model(m_path, compile=False)
        with open(l_path, "r", encoding="utf-8") as f:
            classes = [line.strip().split(" ", 1)[-1] for line in f.readlines()]
        return model, classes
    return None, None

model, class_names = load_ai_model()

# --- Section d'Analyse ---
if model:
    st.write("### 📸 Examen de l'Échantillon")
    img_file = st.camera_input("Capturez l'image via le microscope")
    
    if img_file:
        image = Image.open(img_file).convert("RGB")
        st.image(image, caption="Image capturée", use_container_width=True)
        
        # Prétraitement de l'image (224x224 pour Keras)
        size = (224, 224)
        image_resized = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
        img_array = np.asarray(image_resized).astype(np.float32) / 127.5 - 1
        data = np.expand_dims(img_array, axis=0)
        
        # Prédiction de l'IA
        with st.spinner('Analyse des structures en cours...'):
            prediction = model.predict(data, verbose=0)
            index = np.argmax(prediction)
            label = class_names[index]
            confidence = prediction[0][index]
        
        st.divider()
        
        # Affichage des Résultats
        if confidence > 0.65:
            st.markdown(f"## 🧬 Diagnostic : <span style='color:#2E86C1'>{label}</span>", unsafe_allow_html=True)
            st.metric(label="Indice de Confiance", value=f"{confidence*100:.1f}%")
            st.progress(float(confidence))
            
            # Récupération des détails morphologiques
            info = morphology_db.get(label, {"title": label, "structure": "N/A", "details": "N/A", "note": "Vérification manuelle conseillée."})
            
            with st.expander("📚 Guide de Validation Morphologique"):
                st.subheader(info['title'])
                st.write(f"**Structure :** {info['structure']}")
                st.write(f"**Détails Clés :** {info['details']}")
                st.info(f"**Note du Laboratoire :** {info['note']}")
        else:
            st.warning("⚠️ Signal faible. Veuillez améliorer la netteté de l'image ou changer de champ.")
else:
    st.error("Erreur : Les fichiers 'keras_model.h5' et 'labels.txt' sont introuvables sur GitHub.")