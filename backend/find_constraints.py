import prompts
import json
import boto3


def generate_constraints(n_constraints, initial_prompt, db_json, MODEL_ID, bedrock,
                         valid_constraints, invalid_constraints):

    if not initial_prompt : # initial prompt
        db_string = json.dumps(db_json)
        initial_prompt = prompts.INTRO_CONSTRAINTS + "\n" + db_string + "\n" + prompts.TASK_CONSTRAINTS
        message_list = [{
            "role": "user",
            "content": [{"text": initial_prompt}],
        }]

    else:

        few_shot_message = get_few_shot_prompt(valid_constraints, invalid_constraints)
        
        prompt = initial_prompt + "\n" + few_shot_message

        message_list = [{
            "role": "user",
            "content": [{"text": prompt}],
        }]


    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=message_list,
        system=[{"text": prompts.get_format_constraints(n_constraints)}],
        inferenceConfig={}, # temperature
    )

    output = response["output"]["message"]["content"][0]["text"]

    if output.startswith("```json"):
        output = output.split("\n", 1)[1]
    if output.endswith("```"):
        output = output.rsplit("\n", 1)[0]

    output = json.loads(output)

    return output, initial_prompt

def get_few_shot_prompt(valid_constraints, invalid_constraints):
    prompt = ""
    for constraint in valid_constraints:
        prompt += prompts.VALID_CONSTRAINTS + "\n" + json.dumps(constraint) + "\n"
    for constraint in invalid_constraints:
        prompt += prompts.INVALID_CONSTRAINTS + "\n" + json.dumps(constraint) + "\n"
    prompt += "Do not reproduce the valid or invalid constraints from above, you have to generate NEW constraints." # Sinon le modèle se contente de reproduire les contraintes considérées comme bonnes
    return prompt


if __name__ == "__main__":
    n_constraints = 4
    message_list = []
    db_json = {
        "tables": [
            {
                "name": "table1",
                "columns": [
                    {
                        "name": "column1",
                        "type": "int",
                        "description": "This is the first column"
                    }
                ]
            }
        ]
    }
    MODEL_ID = "mistral.mistral-large-2407-v1:0"
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name="us-west-2",
        aws_access_key_id="AKIAUMYCIUHUBUQMWTUS",
        aws_secret_access_key="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",
        # aws_session_token="VOTRE_TOKEN_DE_SESSION" # facultatif si vous utilisez des credentials temporaires
    )
    output, message_list = generate_constraints(n_constraints, message_list, db_json, MODEL_ID, bedrock,
                                                valid_constraints=[], invalid_constraints=[])
    print(output)
    print(message_list)

    output, message_list = generate_constraints(n_constraints, message_list, db_json, MODEL_ID, bedrock,
                                                valid_constraints=json.loads(output)["constraints"], invalid_constraints=[])

    
    print(output)
    print(message_list)