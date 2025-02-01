import json
import boto3
from credentials import region_name, aws_access_key_id, aws_secret_access_key


def create_sql_request(MODEL_ID,bedrock,input_data):
    
    def prompt(constraint):
        description = constraint['description']
        columns = constraint['columns']
        tables = constraint['tables']
        res=f""" J'ai liste contraintes pour faire requête SQL : \n
        Nom tables : {tables} \n
        Nom colonnes : {columns} \n
        description requete SQL: {description} \n\n

        ```json
        "description
        "request":
        """
        return res

    system_prompt='''return only a json type object with the following columns: \n

        -description: description of the constraint \n
        -request: SQL query \n

    '''


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
    print(translated_queries)

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