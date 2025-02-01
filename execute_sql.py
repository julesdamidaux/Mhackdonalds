import json
import boto3
import sqlite3


# Chemin vers le fichier JSON contenant les queries traduites
file_path = 'translated_queries.json'

#lien de la database
db_path='veolia_data_duplicate.db'

# Lire le contenu du fichier JSON
with open(file_path, 'r') as file:
    data = json.load(file)


executed_queries = []  #liste des requêtes de translated_queries avec le statue, si la requête a été exécutée avec succès ou sinon l'erreur
results_queries=[] #liste des résultats des requêtes exécutées

# Itérer sur les éléments du dictionnaire
for request in data:
    description = request['description']
    sql_request = request['sql']
    status=True
    new_sql_request = sql_request.replace('veolia-data-', '')  #supprimer le préfixe veolia-data- car table enregistrée sans préfixe
    
    # Se connecter à la base de données SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
    
        # Récupérer les résultats
        results = cursor.fetchall()
        # Exécuter la requête SQL
        cursor.execute(new_sql_request)

        # Récupérer les résultats
        results = cursor.fetchall()

        results_queries.append({
            'description': description,
            'results': results
        })
        # Afficher les résultats
        print('executé avec succès')

    except sqlite3.Error as e:
        # Afficher un message d'erreur
        status=str(e)
        print(f"Erreur lors de l'exécution de la requête : {e}")

    finally:

        executed_queries.append({
        'description': description,
        'sql': sql_request,
        'executed': status
    })
        # Fermer la connexion
        conn.close()


with open('executed_queries.json', 'w') as file:
    json.dump(executed_queries, file, indent=4)

with open('results_queries.json', 'w') as file:
    json.dump(results_queries, file, indent=4)