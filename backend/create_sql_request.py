import json
import boto3
from credentials import region_name, aws_access_key_id, aws_secret_access_key


def create_sql_request(MODEL_ID,bedrock,input_data):
    
    def prompt(constraint):
        description = constraint['description']
        columns = constraint['columns']
        tables = constraint['tables']
        
        res = f"""I need to create a read-only SQL validation query for this constraint:
        
        Related Tables: {tables}
        Involved Columns: {columns}
        Constraint Description: {description}

        The query must:
        1. Check referential integrity between tables
        2. Use SELECT with READ-only permissions
        3. Return problematic records if any
        4. Use explicit table aliases
        5. Include relevant columns for analysis

        Expected output format:
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
        - Ensure the JSON is valid and can be parsed directly
        """

        return res

    system_prompt = """Generate exclusively a JSON object with:
    - description: A clear and concise reformulation of the constraint
    - request: A SELECT validation query that checks referential integrity

    The query must:
    - Use explicit joins (e.g., LEFT JOIN, INNER JOIN)
    - Check column consistency between tables
    - Identify potential mismatches or orphaned records
    - Be executable as read-only
    - Be formatted as a single-line string with escaped newlines (\\n) and escaped double quotes (\\")

    Example of valid output:
    ```json
    {
        "description": "Validates that all cle_abonnement values in factures table exist in abonnements table, identifying orphaned records that violate referential integrity",
        "request": "SELECT f.cle_abonnement as facture_cle, f.id as facture_id, a.cle_abonnement as abonnement_existant FROM factures f LEFT JOIN abonnements a ON f.cle_abonnement = a.cle_abonnement WHERE a.cle_abonnement IS NULL"
    }"""


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