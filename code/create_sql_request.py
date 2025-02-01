import json
import boto3
from credentials import region_name, aws_access_key_id, aws_secret_access_key

# Initialiser le client Bedrock
bedrock = boto3.client(
    "bedrock-runtime",
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    # aws_session_token="VOTRE_TOKEN_DE_SESSION"  # facultatif si vous utilisez des credentials temporaires
)
# Identifiant du modèle Mistral
MODEL_ID = "mistral.mistral-large-2407-v1:0"

# Lire le fichier JSON d'entrée
with open('../data/constraints.json', 'r') as file:
    input_data = json.load(file)

# Identifiant du modèle Mistral
MODEL_ID = "mistral.mistral-large-2407-v1:0"


debut_prompt=''' J'ai une liste de contraintes pour faire des requêtes SQL : \n
    Nom tables : table_name \n
    Nom colonnes : column_name \n
    description requete SQL: description \n
'''
fin_prompt='''\n  SELECT
'''

def prompt(constraint):
    description = constraint['description']
    columns = constraint['columns']
    tables = constraint['tables']
    res=f''' J'ai liste contraintes pour faire requête SQL : \n
    Nom tables : {tables} \n
    Nom colonnes : {columns} \n
    description requete SQL: {description} \n\n

    
    "description
    "request":
    '''
    return res

system_prompt='''return only a json type object with the following columns: \n

    -description: description of the constraint \n
    -request: SQL query \n

'''


# Traduire les requêtes
translated_queries = []
for constraint in input_data['constraints']:
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
    json_response_message=json.loads(response_message['text'][7:-3].strip())
    # print(response_message)
    # print(json.dumps(response_message, indent=4))
    
    description=json_response_message['description']
    translated_text=json_response_message['request']

    # Ajouter la requête traduite à la liste
    translated_queries.append({
        'desription': description,
        'sql': translated_text
    })

# Enregistrer les résultats dans un nouveau fichier JSON
with open('../data/constraints_sql.json', 'w') as file:
    json.dump(translated_queries, file, indent=4)

print("Traduction terminée. Les requêtes SQL ont été enregistrées dans 'constraints_sql.json'.")
