"""
This module provides functionality to execute SQL queries from a request on a Redshift database.
Functions:
    execute_sql_from_request(db_name, data):
        Executes SQL queries from the provided data on the specified database.
        Args:
            db_name (str): The name of the database.
            data (list): A list of dictionaries containing SQL queries and their descriptions.
        Returns:
            tuple: A tuple containing two lists:
                - executed_queries: A list of dictionaries with the status of each executed query.
                - results_queries: A list of dictionaries with the results of each executed query.
Example usage:
        db_name = 'dev'
        executed_queries, results_queries = execute_sql_from_request(db_name, data)
"""

import json
import boto3
import sqlite3
import redshift_connector

def execute_sql_from_request(db_name, data):

    executed_queries = []  #liste des requêtes de translated_queries avec le statue, si la requête a été exécutée avec succès ou sinon l'erreur
    results_queries=[] #liste des résultats des requêtes exécutées
    
    # Itérer sur les éléments du dictionnaire
    for request in data:
        description = request['description']
        sql_request = request['sql']
        status=True
        new_sql_request = sql_request.replace('veolia-data-', '')  #supprimer le préfixe veolia-data- car table enregistrée sans préfixe
        #print("SQL REQUEST")
        #print(new_sql_request)
        # Se connecter à la base de données SQLite
        with open("credentials.json", "r", encoding="utf-8") as f:
            config = json.load(f)
    
        ACCESS_KEY = config.get("aws_access_key_id")
        SECRET_KEY = config.get("aws_secret_access_key")
        region_name = config.get("region_name")
        host = config.get("host")
        port = config.get("port")

        session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=region_name
        )

        client = session.client('redshift-serverless')

        response = client.get_credentials(
            workgroupName="hackathon",
        )

        conn = redshift_connector.connect(
            host=host,
            database=db_name,
            port=port,
            user=response["dbUser"],
            password=response['dbPassword'],
        )

        cursor = conn.cursor()

        try:
        
            #print("try")
            # Exécuter la requête SQL
            cursor.execute(new_sql_request)

            # Récupérer les résultats
            results = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]


            results_queries.append({
                'description': description,
                'columns_names': column_names,
                'results': results
            })
            # Afficher les résultats
            # print('executé avec succès')

        except Exception as e:
            # Afficher un message d'erreur
            status=str(e)
            # print(f"Erreur lors de l'exécution de la requête : {e}")

        finally:

            executed_queries.append({
            'description': description,
            'sql': sql_request,
            'executed': status
        })
            # Fermer la connexion
            conn.close()

    return executed_queries, results_queries


# Exemple d'utilisation
if __name__ == "__main__":
    db_name='dev'
    file_path = 'translated_queries.json'
    with open(file_path, 'r') as file:
         data = json.load(file)
    executed_queries,results_queries=execute_sql_from_request(db_name,data)
    with open('executed_queries.json', 'w') as file:
        json.dump(executed_queries, file, indent=4)

    with open('results_queries.json', 'w') as file:
        json.dump(results_queries, file, indent=4)
