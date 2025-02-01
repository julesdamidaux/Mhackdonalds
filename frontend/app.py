import streamlit as st
import json
import os
import sqlite3
import sys
import boto3

# Ajouter le chemin vers le dossier backend
dossier_source = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(dossier_source)

from find_constraints import generate_constraints
from create_database_json_from_database import get_database_json_from_database

MODEL_ID = "mistral.mistral-large-2407-v1:0" 

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-west-2",
    aws_access_key_id="AKIAUMYCIUHUBUQMWTUS",
    aws_secret_access_key="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",
)

# Configuration de la page
st.set_page_config(page_title="Pipeline SQL - Téléversement & Contraintes", layout="centered")

# Initialisation des variables de session
if "generation_phase" not in st.session_state:
    st.session_state["generation_phase"] = False
if "constraints" not in st.session_state:
    st.session_state["constraints"] = []  # Liste des contraintes actuellement affichées (liste de dict)
if "validated_constraints" not in st.session_state:
    st.session_state["validated_constraints"] = []  # Contraintes acceptées
if "rejected_constraints" not in st.session_state:
    st.session_state["rejected_constraints"] = []  # Contraintes rejetées
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""  # Historique des prompts envoyés au modèle (message_list)
if "selected_constraints" not in st.session_state:
    st.session_state["selected_constraints"] = []  # Liste de booléens pour la sélection

# On stocke également les chemins des fichiers uploadés
if "input_json_path" not in st.session_state:
    st.session_state["input_json_path"] = ""
if "db_file" not in st.session_state:
    st.session_state["db_file"] = ""
if "txt_path" not in st.session_state:
    st.session_state["txt_path"] = ""

# Vérifier et créer le dossier `data/`
DATA_FOLDER = "data"
os.makedirs(DATA_FOLDER, exist_ok=True)

# Chemin vers la base de données SQLite (localement, après upload)
DB_PATH = os.path.join(DATA_FOLDER, "database.db")

def save_uploaded_file(uploaded_file, folder):
    """Sauvegarde un fichier téléchargé dans le dossier spécifié."""
    if uploaded_file is not None:
        file_path = os.path.join(folder, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None

def display_upload_section():
    """Affiche la section de téléchargement des fichiers et enregistre leurs chemins."""
    st.title("📂 Téléversement de fichiers vers `data/`")
    st.subheader("Déposez vos fichiers ici 👇")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 📜 Fichier JSON")
        json_file = st.file_uploader("Glissez-déposez un fichier JSON", type=["json"], key="json")
        if json_file:
            json_path_local = save_uploaded_file(json_file, DATA_FOLDER)
            st.success(f"✅ Fichier JSON enregistré : `{json_path_local}`")
            try:
                with open(json_path_local, "r", encoding="utf-8") as f:
                    json_content = json.load(f)
            except json.JSONDecodeError:
                st.error("❌ Erreur : le fichier JSON semble invalide.")
            st.session_state["input_json_path"] = json_path_local

    with col2:
        st.markdown("### 🗃️ Base de données SQLite")
        db_file = st.file_uploader("Glissez-déposez un fichier SQLite (.db)", type=["db"], key="db")
        if db_file:
            db_path_local = save_uploaded_file(db_file, DATA_FOLDER)
            st.success(f"✅ Base de données SQLite enregistrée : `{db_path_local}`")
            st.session_state["db_file"] = db_path_local

    with col3:
        st.markdown("### 📄 Fichier Texte")
        txt_file = st.file_uploader("Glissez-déposez un fichier texte", type=["txt"], key="txt")
        if txt_file:
            txt_path_local = save_uploaded_file(txt_file, DATA_FOLDER)
            st.success(f"✅ Fichier texte enregistré : `{txt_path_local}`")
            with open(txt_path_local, "r", encoding="utf-8") as f:
                txt_content = f.read()
            st.text_area("📖 Contenu du fichier texte :", txt_content, height=200)
            st.session_state["txt_path"] = txt_path_local

    # Bouton pour passer à la génération de contraintes
    if st.button("Générer contraintes"):
        # Vérifier que les chemins ont été enregistrés
        if st.session_state["db_file"] and st.session_state["input_json_path"] and st.session_state["txt_path"]:
            # Lire le contexte depuis le fichier texte
            with open(st.session_state["txt_path"], "r", encoding="utf-8") as f:
                contexte = f.read()
            # Appeler la fonction pour créer le JSON de la base depuis la base SQLite et le fichier JSON d'input
            st.session_state['db_json'] = get_database_json_from_database(
                st.session_state["db_file"],
                contexte,
                st.session_state["input_json_path"],
                save_json=False
            )
        else:
            st.error("Veuillez téléverser le fichier JSON, la base de données SQLite et le fichier texte.")
            return

        st.session_state["generation_phase"] = True
        # Appel de generate_constraints qui renvoie un JSON et un prompt
        constraints_json, st.session_state["prompt"] = generate_constraints(
            5,  # Nombre de contraintes à générer
            st.session_state["prompt"],
            st.session_state['db_json'],
            MODEL_ID,
            bedrock,
            st.session_state["validated_constraints"],
            st.session_state["rejected_constraints"]
        )
        # On stocke uniquement la liste des contraintes depuis le JSON
        st.session_state["constraints"] = constraints_json.get("constraints", [])
        st.session_state["selected_constraints"] = [False] * len(st.session_state["constraints"])

def execute_validated_constraints():
    """Exécute les contraintes validées sur la base SQLite."""
    if not os.path.exists(DB_PATH):
        st.error(f"❌ La base de données `{DB_PATH}` n'existe pas. Vérifiez votre téléversement.")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for constraint in st.session_state["validated_constraints"]:
            cursor.execute(constraint)
        conn.commit()
        conn.close()
        st.success("✅ Toutes les contraintes validées ont été exécutées avec succès.")
    except Exception as e:
        st.error(f"❌ Erreur lors de l'exécution des contraintes : {e}")

def display_constraints_generation_section():
    """Affiche la section de génération et validation des contraintes."""
    st.title("🔍 Sélectionnez les contraintes à valider")

    if st.session_state["constraints"]:
        new_selected = []
        st.write("Veuillez sélectionner les contraintes qui vous conviennent (description) :")
        # Affichage des contraintes générées
        for i, constraint in enumerate(st.session_state["constraints"]):
            label = constraint.get("description", "Pas de description")
            selected = st.checkbox(label, value=st.session_state["selected_constraints"][i], key=f"constraint_{i}")
            new_selected.append(selected)
        st.session_state["selected_constraints"] = new_selected

        if st.button("✅ Valider la sélection et générer de nouvelles contraintes"):
            for i, selected in enumerate(st.session_state["selected_constraints"]):
                if selected:
                    st.session_state["validated_constraints"].append(st.session_state["constraints"][i]["description"])
                else:
                    st.session_state["rejected_constraints"].append(st.session_state["constraints"][i]["description"])
            # Générer de nouvelles contraintes avec l'historique des prompts
            constraints_json, st.session_state["prompt"] = generate_constraints(
                5,
                st.session_state["prompt"],
                st.session_state['db_json'],  # On réutilise le JSON généré lors de l'upload
                MODEL_ID,
                bedrock,
                st.session_state["validated_constraints"],
                st.session_state["rejected_constraints"]
            )
            st.session_state["constraints"] = constraints_json.get("constraints", [])
            st.session_state["selected_constraints"] = [False] * len(st.session_state["constraints"])
    else:
        st.success("✅ Toutes les contraintes ont été évaluées.")

    if st.session_state["validated_constraints"]:
        st.subheader("✅ Contraintes validées :")
        for c in st.session_state["validated_constraints"]:
            st.code(c, language="sql")
    if st.session_state["rejected_constraints"]:
        st.subheader("❌ Contraintes rejetées :")
        for c in st.session_state["rejected_constraints"]:
            st.code(c, language="sql")

    if st.button("🚀 Exécuter les contraintes validées"):
        execute_validated_constraints()

    if st.button("Retour au téléversement des fichiers"):
        st.session_state["generation_phase"] = False

# Affichage de la section appropriée selon l'état de session
if not st.session_state["generation_phase"]:
    display_upload_section()
else:
    display_constraints_generation_section()
