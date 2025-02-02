import json
import boto3

import os
import sys

with open("credentials.json", "r", encoding="utf-8") as f:
    config = json.load(f)

    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    region_name = config.get("region_name")

def create_sql_request(MODEL_ID,bedrock,input_data,db_json):
    
    def prompt(constraint):
        description = constraint['description']
        columns = constraint['columns']
        tables = constraint['tables']
        
        res = f"""I need to create a read-only SQL validation query for this constraint:
        
        Involved Tables to use in the SQL query: {tables}
        Involved Columns in the SQL query : {columns}
        Constraint Description: {description}

        The query must:
        1. Code the constraint in SQL (MOST IMPORTANT)
        2. Use SELECT with READ-only permissions
        3. Use only columns and tables that you can infer from above

        Never try to use table or column names that are not present in the Database Schema.
        Database Schema:
        """
        res += "\n" + json.dumps(db_json) + "\n"
        return res

    system_prompt = """Generate exclusively a JSON object with:
    - description: A clear and concise reformulation of the constraint
    - request: A SELECT validation query that checks referential integrity
     
    - Expected output format:
        ```json
        {{
            "description": "Concise constraint description",
            "request": "Your validation SQL query here, with escaped newlines (\\n) and no unescaped double quotes"
        }}
        ```

        Rules for the SQL query:
        - Replace all newlines with \\n
        - Escape all double quotes (") inside the SQL query with a backslash (\\")
        - Ensure the SQL query is a single-line string inside the JSON
        - Do not include any markdown syntax (e.g., ```json or ```)
        - Ensure the JSON is valid and can be parsed directly"""


    # Traduire les requêtes
    translated_queries = []
    for constraint in input_data:
        input_text = constraint['description']
        
        # Préparer le payload pour l'API Bedrock

        # Configuration du système
        system=[
            { "text": system_prompt}
        ],
        inferenceConfig={
            "maxTokens": 2000,
            "temperature": 0.7
        },

        message_list = []
        
        initial_message = {
            "role": "user",
            "content": [
                { "text": prompt(constraint) } 
            ],
        }

        message_list.append(initial_message)

        response = bedrock.converse(
            modelId=MODEL_ID,
            messages = message_list,
            system=[
                { "text": system_prompt}
            ],
            inferenceConfig={
                "maxTokens": 2000,
                "temperature": 0.7
            },
        )

        # Lire la réponse du modèle
        response_message = response['output']['message']['content'][0]
        json_response_message=json.loads(response_message['text'])
        # print(response_message)
        # print(json.dumps(response_message, indent=4))
        
        description=json_response_message['description']
        translated_text=json_response_message['request']

        # Ajouter la requête traduite à la liste
        translated_queries.append({
            'description': description,
            'sql': translated_text
        })

    return translated_queries



if __name__ == "__main__":

    # Initialiser le client Bedrock
    bedrock = boto3.client(
    "bedrock-runtime",
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    # aws_session_token="VOTRE_TOKEN_DE_SESSION"  # facultatif si vous utilisez des credentials temporaires
    )
    MODEL_ID = "mistral.mistral-large-2407-v1:0"

    # Lire le fichier JSON d'entrée
    with open('C:/Users/Adrien/Documents/Perso/Mhackdonalds/Mhackdonalds/input_queries.json', 'r') as file:
        input_data = json.load(file)
   
    translated_queries=create_sql_request(MODEL_ID,bedrock,input_data)

    # Enregistrer les résultats dans un nouveau fichier JSON
    with open('data/translated_sql.json', 'w') as file:
        json.dump(translated_queries, file, indent=4)

    print("Traduction terminée. Les requêtes SQL ont été enregistrées dans 'constraints_sql.json'.")
