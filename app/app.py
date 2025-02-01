import streamlit as st
import json
import os

# Chemin vers le fichier JSON des contraintes
JSON_FILE = "../data/constraints.json"

def load_constraints():
    """Charge les contraintes depuis le fichier JSON"""
    if not os.path.exists(JSON_FILE):
        st.error(f"Le fichier {JSON_FILE} n'existe pas.")
        return []
    
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return data.get("constraints", [])

def save_constraints(selected_constraints):
    """Enregistre les contraintes sélectionnées dans le fichier JSON"""
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump({"constraints": selected_constraints}, f, indent=4, ensure_ascii=False)

# Interface Streamlit
st.title("Gestion des Contraintes SQL")

# Charger les contraintes
constraints = load_constraints()

if not constraints:
    st.warning("Aucune contrainte trouvée.")
else:
    # Stocker les choix de l'utilisateur
    st.subheader("Sélectionnez les contraintes à conserver :")
    
    selected_constraints = []
    
    for i, constraint in enumerate(constraints):
        description = constraint["description"]
        is_selected = st.checkbox(description, value=True, key=f"constraint_{i}")
        
        if is_selected:
            selected_constraints.append(constraint)

    # Bouton pour sauvegarder les contraintes sélectionnées
    if st.button("Sauvegarder les contraintes sélectionnées"):
        save_constraints(selected_constraints)
        st.success("Le fichier JSON a été mis à jour avec les contraintes sélectionnées.")

    # Afficher les contraintes sélectionnées
    st.subheader("Contraintes sélectionnées :")
    for constraint in selected_constraints:
        st.write(f"- **{constraint['description']}**")

