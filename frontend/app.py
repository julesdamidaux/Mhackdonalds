import streamlit as st
import json
import os
import sqlite3
import sys
import boto3
import csv

# Ajouter le chemin vers le dossier backend
dossier_source = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.append(dossier_source)

from find_constraints import generate_constraints
from create_database_json_from_database import get_database_json_from_database
from create_sql_request import create_sql_request  # Fonction qui calcule les requêtes SQL à partir des contraintes validées
from fill_metadatas import fill_metadatas
from execute_sql import execute_sql_from_request

MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0" 

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
if "execution_phase" not in st.session_state:
    st.session_state["execution_phase"] = False
if "constraints" not in st.session_state:
    st.session_state["constraints"] = []  # Liste des contraintes actuellement affichées (liste de dict)
if "validated_constraints" not in st.session_state:
    st.session_state["validated_constraints"] = []  # Contraintes acceptées
if "rejected_constraints" not in st.session_state:
    st.session_state["rejected_constraints"] = []  # Contraintes rejetées
if "prompt" not in st.session_state:
    st.session_state["prompt"] = ""  # Historique des prompts envoyés au modèle
if "selected_constraints" not in st.session_state:
    st.session_state["selected_constraints"] = []  # Liste de booléens pour la sélection

# On stocke également les chemins des fichiers uploadés
if "input_json_path" not in st.session_state:
    st.session_state["input_json_path"] = ""
if "db_file" not in st.session_state:
    st.session_state["db_file"] = ""
if "txt_path" not in st.session_state:
    st.session_state["txt_path"] = ""
if "db_name" not in st.session_state:
    st.session_state["db_name"] = ""

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
        st.markdown("### Entrée de texte")
        # Ici, l'utilisateur saisit le nom de la database (par exemple Redshift ou autre)
        user_text = st.text_input("Nom de la database :", key="user_text")
        if user_text:
            st.session_state["db_name"] = user_text
            st.success("✅ Nom de la database enregistré.")

    with col2:
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

    with col3:
        st.markdown("### 📄 Fichier Texte")
        txt_file = st.file_uploader("Glissez-déposez un fichier texte", type=["txt"], key="txt")
        if txt_file:
            txt_path_local = save_uploaded_file(txt_file, DATA_FOLDER)
            st.success(f"✅ Fichier texte enregistré : `{txt_path_local}`")
            with open(txt_path_local, "r", encoding="utf-8") as f:
                txt_content = f.read()
            st.session_state["txt_path"] = txt_path_local

    # Case à cocher pour améliorer les métadonnées
    enhance_metadata = st.checkbox("Améliorer les métadonnées", key="enhance_meta")

    # Bouton pour passer à la génération de contraintes
    if st.button("Générer contraintes"):
        if st.session_state["db_name"] and st.session_state["input_json_path"] and st.session_state["txt_path"]:
            with open(st.session_state["txt_path"], "r", encoding="utf-8") as f:
                contexte = f.read()
            # Création du JSON de la base à partir de la base et du fichier JSON d'input
            st.session_state["db_json"] = get_database_json_from_database(
                st.session_state["db_name"],
                contexte,
                st.session_state["input_json_path"],
                save_json=False
            )
            # Si la case est cochée, améliorer les métadonnées
            if enhance_metadata:
                st.session_state["db_json"] = fill_metadatas(st.session_state["db_json"], bedrock, MODEL_ID)
        else:
            st.error("Veuillez renseigner le nom de la database et téléverser le fichier JSON et le fichier texte.")
            return

        st.session_state["generation_phase"] = True
        constraints_json, st.session_state["prompt"] = generate_constraints(
            5,  # Nombre de contraintes à générer
            st.session_state["prompt"],
            st.session_state["db_json"],
            MODEL_ID,
            bedrock,
            st.session_state["validated_constraints"],
            st.session_state["rejected_constraints"]
        )
        st.session_state["constraints"] = constraints_json.get("constraints", [])
        st.session_state["selected_constraints"] = [False] * len(st.session_state["constraints"])


def display_constraints_generation_section():
    """Affiche la section de génération et validation des contraintes."""
    st.title("🔍 Sélectionnez les contraintes à valider")

    if st.session_state["constraints"]:
        new_selected = []
        st.write("Veuillez sélectionner les contraintes qui vous conviennent (description) :")
        for i, constraint in enumerate(st.session_state["constraints"]):
            label = constraint.get("description", "Pas de description")
            selected = st.checkbox(label, value=st.session_state["selected_constraints"][i], key=f"constraint_{i}")
            new_selected.append(selected)
        st.session_state["selected_constraints"] = new_selected

        if st.button("✅ Valider la sélection et générer de nouvelles contraintes"):
            for i, selected in enumerate(st.session_state["selected_constraints"]):
                if selected:
                    st.session_state["validated_constraints"].append(st.session_state["constraints"][i])
                else:
                    st.session_state["rejected_constraints"].append(st.session_state["constraints"][i])
            constraints_json, st.session_state["prompt"] = generate_constraints(
                5,
                st.session_state["prompt"],
                st.session_state["db_json"],
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
            st.markdown(c.get("description", "Pas de description"))
    if st.session_state["rejected_constraints"]:
        st.subheader("❌ Contraintes rejetées :")
        for c in st.session_state["rejected_constraints"]:
            st.markdown(c.get("description", "Pas de description"))

    if st.button("🚀 Créer les requêtes SQL"):
        # Plutôt que d'exécuter directement dans la DB, on passe à une nouvelle "fenêtre" d'exécution
        st.session_state["execution_phase"] = True

    if st.button("Retour au téléversement des fichiers"):
        st.session_state["generation_phase"] = False

def display_execution_section():
    """Affiche la nouvelle fenêtre avec les requêtes SQL calculées par create_sql_request()."""
    st.title("💻 Requêtes SQL générées")
    # On suppose que create_sql_request() prend les contraintes validées et renvoie une liste de dictionnaires,
    # chaque dictionnaire contenant les clés 'description' et 'sql'
    sql_queries = create_sql_request(MODEL_ID, bedrock, st.session_state["validated_constraints"])
    st.markdown("### Voici les requêtes SQL générées :")
    for query in sql_queries:
        st.markdown(f"- **Description** : {query['description']}\n\n```sql\n{query['sql']}\n```")

    if st.button("Exécuter les requêtes"):
        # Exécute les requêtes SQL proposées grâce à la fonction execute_sql_from_request
        executed_queries, results_queries = execute_sql_from_request(st.session_state['db_name'], sql_queries)
        st.success("✅ Requêtes exécutées avec succès !")
        results_folder = "results"
        os.makedirs(results_folder, exist_ok=True)

        # Conversion de executed_queries en CSV
        executed_csv_file = os.path.join(results_folder, "executed_queries.csv")
        with open(executed_csv_file, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["description", "sql", "executed"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in executed_queries:
                writer.writerow(row)

        print(f"Le fichier '{executed_csv_file}' a été généré avec succès.")

        # Conversion de results_queries en CSV
        results_csv_file = os.path.join(results_folder, "results_queries.csv")
        with open(results_csv_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            # Pour chaque contrainte, écrire d'abord sa description puis les résultats
            for query in results_queries:
                description = query.get("description", "Pas de description")
                writer.writerow([f"Description: {description}"])
                for row in query.get("results", []):
                    writer.writerow(row)
                writer.writerow([])  # Ligne vide pour séparer les contraintes

        print(f"Le fichier '{results_csv_file}' a été généré avec succès.")

    if st.button("Retour à la validation des contraintes"):
        st.session_state["execution_phase"] = False

# Affichage de la section appropriée selon l'état de session
if "execution_phase" not in st.session_state or not st.session_state.get("execution_phase"):
    if not st.session_state["generation_phase"]:
        display_upload_section()
    else:
        display_constraints_generation_section()
else:
    display_execution_section()
