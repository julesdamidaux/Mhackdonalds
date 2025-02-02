"""
Fills metadata for a given database JSON using a conversational AI model.
Args:
    db_json (dict): The database JSON object to be processed.
    bedrock (object): The conversational AI model interface.
    MODEL_ID (str): The identifier for the AI model to be used.
Returns:
    dict: The processed metadata as a JSON object.
"""

import json
import boto3
import prompts


def fill_metadatas(db_json, bedrock, MODEL_ID):
    
    db_string = json.dumps(db_json)

    prompt = prompts.INTRO_METADATA + "\n" + db_string + "\n" + prompts.TASK_METADATA

    message_list = [{
        "role": "user",
        "content": [{"text": prompt}],
    }]

    print("1")
    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=message_list,
        system=[{"text": prompts.FORMAT_METADATA}],
        inferenceConfig={}, # max tokens, temperature
    )
    print("2")

    output = response["output"]["message"]["content"][0]["text"]

    if output.startswith("```json"):
        output = output.split("\n", 1)[1]
    if output.endswith("```"):
        output = output.rsplit("\n", 1)[0]

    output = json.loads(output)

    return output
# %%
