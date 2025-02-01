# Ajouter le chemin vers le dossier backend
import os
import sys
dossier_source = os.path.join(os.path.dirname(__file__), "..", "code")
sys.path.append(dossier_source)

from find_constraints_deepseek import generate_constraints
import boto3
import json

if __name__ == "__main__":

    n_constraints = 4
    initial_prompt = False
    db_path = "backend/test_create_database_json/database_json.json"
    with open(db_path, "r", encoding="utf-8") as f:
        db_json = json.load(f)
    MODEL_ID = "mistral.mistral-large-2407-v1:0"
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name="us-west-2",
        aws_access_key_id="AKIAUMYCIUHUBUQMWTUS",
        aws_secret_access_key="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",
        # aws_session_token="VOTRE_TOKEN_DE_SESSION" # facultatif si vous utilisez des credentials temporaires
    )
    valid_constraints = None
    invalid_constraints = None
    output = generate_constraints(n_constraints, initial_prompt, db_json, MODEL_ID, bedrock,
                         valid_constraints, invalid_constraints)
    

    with open("backend/test_create_database_json/testing_creativity_deepseek.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

        print(f"Le fichier testing_creativity_deepseek.json a été généré avec succès.")