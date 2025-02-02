"""
This module provides functionality to retry and correct SQL queries using the Bedrock API.
Functions:
    retry_prompt(MODEL_ID, bedroxck, request):
        Generates a prompt for retrying a SQL query based on the provided request details.
    retry_execute_sql_from_request(data):
        Processes a list of SQL query requests, retries the execution of failed queries, and returns the corrected queries.
Usage Example:
        # Initialize the Bedrock client
        # Read the input JSON file
        datapath = 'executed_queries.json'
"""

import json
import boto3

with open("credentials.json", "r", encoding="utf-8") as f:
    config = json.load(f)

    aws_access_key_id = config.get("aws_access_key_id")
    aws_secret_access_key = config.get("aws_secret_access_key")
    region_name = config.get("region_name")





def retry_prompt(MODEL_ID,bedroxck,request):
    description = request['description']
    old_request = request['sql']
    error = request['executed']
    res=f''' J'ai liste requètes SQL défectueuses qui doivent être corrigées : \n
    description de la requête : {description} \n
    requête SQL : {old_request} \n
    nom de l'erreur: {error} \n\n

    
    "description":
    "request":
    '''
    return res

system_prompt='''return only a json type object with the following columns: \n

    -description: description of the constraint \n
    -request: SQL query \n

'''


def retry_execute_sql_from_request(data):

    retry_translated_queries=[]

    # Itérer sur les éléments du dictionnaire
    for request in data:
        if request['executed']==True:
            continue

        # Préparer le payload pour l'API Bedrock

        # Configuration du système
        

        message_list = []
    
        initial_message = {
            "role": "user",
            "content": [
                { "text": retry_prompt(request) } 
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
        
        description=json_response_message['description']
        translated_text=json_response_message['request']

        # Ajouter la requête traduite à la liste
        retry_translated_queries.append({
            'description': description,
            'sql': translated_text
        })
            
    return retry_translated_queries




# Exemple d'utilisation
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

    datapath='executed_queries.json'
    with open(datapath, 'r') as file:
         data = json.load(file)
    retry_execute_sql_from_request(data)
   
    
