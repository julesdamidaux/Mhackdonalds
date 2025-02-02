"""
This module provides functions to generate constraints for a given prompt using a language model.
Functions:
    generate_constraints(n_constraints, initial_prompt, db_json, MODEL_ID, bedrock, valid_constraints, invalid_constraints):
        Generates a specified number of constraints based on an initial prompt and database JSON.
    get_few_shot_prompt(valid_constraints, invalid_constraints):
        Creates a few-shot learning prompt using valid and invalid constraints.
Args:
    n_constraints (int): The number of constraints to generate.
    initial_prompt (str): The initial prompt to start the constraint generation.
    db_json (dict): The database JSON to be included in the prompt.
    MODEL_ID (str): The ID of the language model to use.
    bedrock (object): The language model interface object.
    valid_constraints (list): A list of valid constraints for few-shot learning.
    invalid_constraints (list): A list of invalid constraints for few-shot learning.
Returns:
    tuple: A tuple containing the generated constraints and the initial prompt.
"""

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
