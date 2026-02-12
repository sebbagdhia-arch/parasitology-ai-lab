import streamlit as st
import tensorflow as tf
from PIL import Image, ImageOps
import numpy as np
import os
import requests
from streamlit_lottie import st_lottie
from gtts import gTTS
import base64
import time

# --- Configuration de la Page ---
st.set_page_config(
    page_title="PFE IA Parasitologie | Dhia & Mouhamed",
    page_icon="🔬",
    layout="centered"
)

# --- Gestion des Étapes (Session State) ---
if 'step' not in st.session_state:
    st.session_state.step = 0

# --- Fonction Audio ---
def speak_audio(text, lang='fr'):
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        filename = "audio_temp.mp3"
        tts.save(filename)
        with open(filename, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
        md = f"""
            <audio autoplay="true" style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
        """
        st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- Design CSS (Arrière-plan Parasites Animés + Caméra Circulaire) ---
st.markdown("""
    <style>
    /* Arrière-plan avec Parasites Animés Colorés */
    .stApp {
        background-color: #f0f4f8;
        /* Remplacer par une URL valide d'une image de parasites colorés */
        background-image: url("https://www.transparenttextures.com/patterns/microbes.png");
        background-attachment: fixed;
    }

    /* Animation de flottement des parasites */
    @keyframes move-background {
        from { background-position: 0 0; }
        to { background-position: 1000px 1000px; }
    }
    .stApp {
        animation: move-background 50s linear infinite;
    }

    /* Caméra Circulaire (Lentille de Microscope) */
    div[data-testid="stCameraInput"] video {
        border-radius: 50% !important;
        border: 12px solid #2C3E50;
        box-shadow: 0 0 25px rgba(0,0,0,0.4);
        width: 300px !important;
        height: 300px !important;
        object-fit: cover;
    }

    /* Boutons Modernes */
    .stButton button {
        width: 100%;
        background-color: #2E86C1;
        color: white;
        border-radius: 20px;
        font-weight: bold;
        padding: 15px;
        border: none;
        transition: 0.3s;
    }
    .stButton button:hover {
        background-color: #1B4F72;
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- Chargement de l'image du microscope fourni ---
# Assurez-vous que 'image_0.png' est dans le même dossier ou utilisez le bon chemin
microscope_image_path = "image_0.png" # Remplacez par le chemin correct si nécessaire

# --- Contenu du Script ---
funny_script = "Salam alikoum la famille ! C'est moi, le microscope intelligent de Dhia et Mouhamed. On a trop galéré pour me créer, on est fatigués ! S'il vous plaît, donnez-nous une super note, genre 19 sur 20, ma t'cassrouch rasskoum ! Allez, on commence ?"
full_title = "Exploration du potentiel de l'intelligence artificielle pour la lecture automatique de l'examen parasitologique à l'état frais."

# --- Interface Principale ---
st.markdown(f"<h1 style='text-align: center; color: #1B4F72;'>{full_title}</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center; color: #1B4F72;'>🧪 Laboratoire IA : Dhia & Mouhamed</h3>", unsafe_allow_html=True)

# --- Base de Données Morphologique (Structure détaillée et drôle) ---
morphology_db = {
    "Amoeba": {
        "title": "Entamoeba histolytica",
        "desc": "Forme irrégulière avec présence de pseudopodes (faux pieds).",
        "funny": "Ayaaa ! C'est une Amibe ! Elle bouge comme un ninja avec ses faux pieds. Attention à la dysenterie sahbi !"},
    "Giardia": {
        "title": "Giardia lamblia",
        "desc": "Forme de poire (pyriforme), symétrie bilatérale, deux noyaux.",
        "funny": "Regarde sa tête ! On dirait un petit fantôme avec des lunettes (ses noyaux). C'est Giardia !"},
    "Leishmania": {
        "title": "Leishmania (Amastigote)",
        "desc": "Petite forme ovoïde ou arrondie (2 à 5 µm), kinétoplaste.",
        "funny": "Oulala, Leishmania ! C'est tout petit mais c'est méchant avec son kinétoplaste. Faut traiter ça vite fait !"},
    "Plasmodium": {
        "title": "Plasmodium (Malaria)",
        "desc": "Forme en anneau (Ring form) à l'intérieur des globules rouges.",
        "funny": "Aïe aïe aïe ! Paludisme détecté ! Il se cache en forme de bague dans tes globules. Les moustiques ont fait des dégâts mon frère."},
    "Trypanosoma": {
        "title": "Trypanosoma spp.",
        "desc": "Forme allongée, fusiforme avec un flagelle libre à l'extrémité.",
        "funny": "Wesh ! C'est Trypanosoma ! Avec son flagelle libre, il court dans le sang comme Usain Bolt."},
    "Schistosoma": {
        "title": "Schistosoma (Oeuf)",
        "desc": "Oeuf volumineux avec une coque transparente et un éperon (épine).",
        "funny": "Gros œuf en vue ! Regarde l'épine sur le côté, c'est Schistosoma. Pas bon du tout !"},
    "Negative": {
        "title": "Échantillon Négatif",
        "desc": "Structure cellulaire normale.",
        "funny": "Hamdoullah ! Y'a rien du tout. Le patient est propre, c'est clean !"}
}

# --- Système de Navigation par Étapes ---
if st.session_state.step == 0:
    st.markdown("<h4 style='text-align: center;'>Cliquez sur le microscope pour écouter son message</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎤 Écouter le Message Spécial"):
            speak_audio(funny_script)
            st.session_state.step = 1
            st.rerun()
    st.image(microscope_image_path, use_container_width=True)

elif st.session_state.step == 1:
    st.markdown("<h4 style='text-align: center;'>Cliquez pour écouter le titre officiel du projet</h4>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📜 Lire le Titre du Projet"):
            speak_audio(full_title)
            st.session_state.step = 2
            st.rerun()
    st.image(microscope_image_path, use_container_width=True)

elif st.session_state.step == 2:
    st.markdown("<h3 style='text-align: center; color: #E74C3C;'>📸 Analyse en Temps Réel</h3>", unsafe_allow_html=True)
    
    # Chargement du modèle
    @st.cache_resource
    def load_model_ia():
        m_path = next((f for f in os.listdir() if f.endswith(".h5")), None)
        l_path = next((f for f in os.listdir() if f.endswith(".txt") and "req" not in f.lower()), None)
        if m_path and l_path:
            model = tf.keras.models.load_model(m_path, compile=False)
            with open(l_path, "r", encoding="utf-8") as f:
                classes = [line.strip().split(" ", 1)[-1] for line in f.readlines()]
            return model, classes
        return None, None

    model, class_names = load_model_ia()

    if model:
        # Caméra circulaire
        img_file = st.camera_input("Scanner la lame")
        
        if img_file:
            image = Image.open(img_file).convert("RGB")
            size = (224, 224)
            image_res = ImageOps.fit(image, size, Image.Resampling.LANCZOS)
            img_array = np.asarray(image_res).astype(np.float32) / 127.5 - 1
            data = np.expand_dims(img_array, axis=0)
            
            with st.spinner('Analyse morphologique...'):
                prediction = model.predict(data, verbose=0)
                idx = np.argmax(prediction)
                label = class_names[idx]
                conf = int(prediction[0][idx] * 100)
            
            # Affichage Résultat
            info = morphology_db.get(label, {"desc": "Inconnu", "funny": f"C'est {label} !"})
            st.markdown(f"""
                <div style="background: white; padding: 20px; border-radius: 20px; text-align: center; border-left: 10px solid #2E86C1;">
                    <h2 style="color: #2E86C1;">Résultat : {label}</h2>
                    <h3>Confiance : {conf}%</h3>
                    <p>{info['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Voix du résultat (Marrante)
            res_voice = f"J'ai trouvé {label} à {conf} pourcent ! {info['funny']}"
            speak_audio(res_voice)

    if st.button("🔄 Recommencer la présentation"):
        st.session_state.step = 0
        st.rerun()
