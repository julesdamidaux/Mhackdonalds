import prompts as prompts
import json
import boto3

def task_discriminate(n):

    return f"""You suggested {n} constraints to enforce data quality. Choose the {n//2} constraints that are the most important and should be enforced.
    The {n//2} remaining constraints will not be enforced. Do not change the constraints, simply classify them between valid and invalid constraints."""

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
    Do not output anything else than this JSON object.""" + f"There should be exactly {n//2} valid constraints and {n//2} invalid constraints."


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