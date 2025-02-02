"""
This module provides functions to discriminate constraints for data quality enforcement.

Functions:
    task_discriminate(n: int) -> str:
        Generates a prompt asking the user to classify constraints as valid or invalid.

    get_format_discriminate(n: int) -> str:
        Generates a JSON format prompt for classifying constraints.

    discriminate_constraints(n_constraints: int, initial_prompt: str, db_json: dict, MODEL_ID: str, bedrock: boto3.client, constraints: list) -> tuple:
        Discriminates constraints into valid and invalid categories using a conversational AI model.

        Parameters:
            n_constraints (int): Number of constraints suggested.
            initial_prompt (str): Initial prompt for the AI model.
            db_json (dict): Database schema in JSON format.
            MODEL_ID (str): Model ID for the AI model.
            bedrock (boto3.client): Boto3 client for interacting with the AI model.
            constraints (list): List of constraints to be classified.

        Returns:
            tuple: A tuple containing two lists - valid_constraints and invalid_constraints.
"""

import prompts as prompts
import json
import boto3

def task_discriminate(n):

    return f"""You suggested {n} constraints to enforce data quality. Choose the constraints that are the most relevant and should be enforced.
    The remaining constraints will not be enforced. Do not change the constraints, simply classify them between valid and invalid constraints."""

def get_format_discriminate(n):

    return """Generate a JSON object containing the valid and invalid constraints following this structure: \n
    {
        "valid_constraints": [
            {
                "tables": ["table_name_used_1","table_name_used_2",...],
                "columns": ["column_name_used_1","column_name_used_2",...],
                "description": "Clear constraint explanation"
            }
        ],
        "invalid_constraints": [
            {
                "tables": ["table_name_used_1","table_name_used_2",...],
                "columns": ["column_name_used_1","column_name_used_2",...],
                "description": "Clear constraint explanation"
            }
        ]
    }\n
    Do not output anything else than this JSON object.""" 


def discriminate_constraints(n_constraints, initial_prompt, db_json, MODEL_ID, bedrock,
                             constraints):

    constraints_string = json.dumps(constraints)

    message_list = [{
        "role": "user",
        "content": [{"text": initial_prompt}],
    },
    {
        "role": "assistant",
        "content": [{"text": constraints_string}],
    },
    {
        "role": "user",
        "content": [{"text": task_discriminate(n_constraints)}],
    }]

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=message_list,
        system=[{"text": get_format_discriminate(n_constraints)}],
        inferenceConfig={}, # temperature
    )

    output = response["output"]["message"]["content"][0]["text"]

    if output.startswith("```json"):
        output = output.split("\n", 1)[1]
    if output.endswith("```"):
        output = output.rsplit("\n", 1)[0]

    output = json.loads(output)

    valid_constraints = output["valid_constraints"]
    invalid_constraints = output["invalid_constraints"]

    return valid_constraints, invalid_constraints
