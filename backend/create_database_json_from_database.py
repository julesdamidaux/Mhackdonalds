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
import boto3
import redshift_connector
from datetime import date


def serialize_date(obj):
    if isinstance(obj, date):
        return obj.isoformat()  # Convertit en format 'YYYY-MM-DD'
    return obj

def get_database_json_from_database(db_name, contexte, input_json, save_json=False):
    
    with open("credentials_redshift.json", "r", encoding="utf-8") as f:
        config = json.load(f)

    ACCESS_KEY = config.get("ACCESS_KEY")
    SECRET_KEY = config.get("SECRET_KEY")

    session = boto3.Session(
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    region_name='us-west-2'
)

    client = session.client('redshift-serverless')

    response = client.get_credentials(
        workgroupName="hackathon",
    )

    conn = redshift_connector.connect(
        host='hackathon.302263083496.us-west-2.redshift-serverless.amazonaws.com',
        database=db_name,
        port=5439,
        user=response["dbUser"],
        password=response['dbPassword'],
    )

    cursor = conn.cursor()

    # Dictionnaire final qui sera exporté au format JSON
    output = {
        "tables": {},
        "contexte": contexte
    }

    # Récupération de toutes les tables utilisateur (exclut les tables système)
    cursor.execute("""
        SELECT tablename
        FROM pg_table_def
        WHERE schemaname = 'public';
    """)
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        
        # Récupération de la structure de la table
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}';
        """)
        columns_info = cursor.fetchall()

        # Création de la structure pour cette table
        table_dict = {
            "create_statement": f"Table {table_name} (définition non disponible via Redshift directement)",
            "example": []
        }

        # Liste des noms de colonnes
        column_names = [col[0] for col in columns_info]
        table_dict["example"].append(column_names)

        # Récupération de quelques lignes d'exemple
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        rows = cursor.fetchall()
        for row in rows:
            table_dict["example"].append([serialize_date(value) for value in row])

        # Ajout des détails des colonnes
        for col in columns_info:
            col_name, col_type = col
            table_dict[col_name] = {
                "column_names": col_name,
                "column_description": "",
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

        print(f"Le fichier database_json.json a été généré avec succès.")

    # Fermeture de la connexion à la base
    conn.close()

    return output

# Exemple d'utilisation
if __name__ == "__main__":
    db_name = "dev"
    contexte = "test réussi"
    input_json = "data/input.json"
    get_database_json_from_database(db_name, contexte, input_json, save_json=True)