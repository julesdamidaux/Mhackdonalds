"""
Crée les fichiers JSON qui décrit la database, les tables et le contexte.


Le contexte est décrit par un string

La structrue du JSON input est la suivante:
{
    "tables": {
        column1: {
                    column_names: "col1",
                    column_description: "",
                    type: "type of the column"},
        ...
    }
}


La structure du JSON output est la suivante:
{
    "tables": {
        "table_name1": {
            "create_statement": "CREATE TABLE statement",
            "example": [
                ["col1", "col2", ...],
                ["val1", "val2", ...],
                ...
            ],
            "column1": {
                "column_names": "col1",
                "column_description": "description of the columns",
                "type": "type of the column"
            },
            "column2: {
                "column_names": "col2",
                "column_description": "description of the columns",
                "type": "type of the column"
            },
            ...

    "contexte": "description du contexte"
    }
}
"""

import sqlite3
import json



def get_database_json_from_database(db_path, contexte, input_json,save_json=False):
    

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Dictionnaire final qui sera exporté au format JSON
    output = {
        "tables": {},
        "contexte": contexte
    }

    # Récupération de toutes les tables de l'utilisateur (exclut les tables système)
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = cursor.fetchall()

    for table in tables:
        table_name, create_statement = table
        
        # Création de la structure pour cette table
        table_dict = {
            "create_statement": create_statement,
            "example": []  # On va remplir la liste avec le header (noms des colonnes) et quelques exemples de lignes
        }
        
        # Récupération des informations sur les colonnes via la commande PRAGMA
        cursor.execute(f"PRAGMA table_info('{table_name}');")
        columns_info = cursor.fetchall()  
        # Chaque ligne de columns_info correspond à : (cid, name, type, notnull, default_value, pk)
        
        # Construction de la liste des noms de colonnes
        column_names = [col[1] for col in columns_info]
        # La première ligne de "example" est la liste des noms de colonnes
        table_dict["example"].append(column_names)
        
        # Récupération de quelques lignes d'exemple (ici, 3 lignes)
        cursor.execute(f"SELECT * FROM '{table_name}' LIMIT 3;")
        rows = cursor.fetchall()
        for row in rows:
            # On transforme le tuple en liste pour JSON
            table_dict["example"].append(list(row))
        
        # Pour chaque colonne, on ajoute un objet décrivant la colonne
        for col in columns_info:
            col_name = col[1]
            col_type = col[2]
            table_dict[col_name] = {
                "column_names": col_name,
                "column_description": "",  # Description laissée vide pour le moment
                "type": col_type
            }
        
        # Ajout de la table dans le dictionnaire final
        output["tables"][table_name] = table_dict

    #Chargement du JSON input
    with open(input_json, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    # Mise à jour du JSON output avec les informations de l'input
    # Parcours des tables
    for table_name, table_data in output["tables"].items():
        if table_name in input_data:
            for column_name, column_info in table_data.items():
                if isinstance(column_info, dict) and "column_names" in column_info:
                    if column_name in input_data[table_name]:
                        # Mettre à jour la description si elle existe dans input
                        column_info["column_description"] = input_data[table_name][column_name].get("column_description", "")

    if save_json:
        # Sauvegarde du JSON mis à jour
        with open("backend/test_create_database_json/database_json.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"Le fichier '{"database_json.json"}' a été généré avec succès.")

    # Fermeture de la connexion à la base
    conn.close()

    return output

# Exemple d'utilisation
if __name__ == "__main__":
    db_path = "data/veolia_data.db"
    contexte = "test réussi"
    input_json = "data/input.json"
    get_database_json_from_database(db_path, contexte, input_json, save_json=True)