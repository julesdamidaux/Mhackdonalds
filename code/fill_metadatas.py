import json
import boto3

bedrock = boto3.client(
    "bedrock-runtime",
    region_name="us-west-2",
    aws_access_key_id="AKIAUMYCIUHUBUQMWTUS",
    aws_secret_access_key="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",
    # aws_session_token="VOTRE_TOKEN_DE_SESSION" # facultatif si vous utilisez des credentials temporaires
)

MODEL_ID = "mistral.mistral-large-2407-v1:0"  # À vérifier

fichier = "../data/tables.json"

with open(fichier, "r", encoding="utf-8") as f:
    db_json = json.load(f)

db_string = json.dumps(db_json)


#########################################################################################################
############################################ ANALYZE DB #################################################
#########################################################################################################


intro_analyse = "Here is the description of a database in json format: \n"
task_analyse = "Fill in the missing colums descriptions in the database description. Use the names of tables and fields. Use the examples of rows provided.\n"
format_analyse = "Answer by providing the same json as in input, but with the missing information filled in. Do not give me anything more than this json.\n"

final_prompt_analyse = (
    intro_analyse + db_string + task_analyse
)


message_list = []

initial_message = {
    "role": "user",
    "content": [{"text": final_prompt_analyse}],
}

message_list.append(initial_message)


response = bedrock.converse(
    modelId=MODEL_ID,
    messages=message_list,
    system=[{"text": format_analyse}],
    inferenceConfig={"maxTokens": 4000, "temperature": 0.7},
)


output = response["output"]["message"]["content"][0]["text"]

# Retirer les marqueurs Markdown
if output.startswith("```json"):
    # Retire la première ligne contenant "```json"
    output = output.split("\n", 1)[1]
if output.endswith("```"):
    # Retire la dernière ligne contenant "```"
    output = output.rsplit("\n", 1)[0]

# Maintenant, output doit contenir uniquement le JSON
try:
    data = json.loads(output)
except json.JSONDecodeError as e:
    print("Erreur de décodage JSON :", e)
    exit(1)

# Enregistrer l'objet JSON dans un fichier avec une mise en forme indentée
with open('../data/tables_filled.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Fichier JSON enregistré avec succès.")
