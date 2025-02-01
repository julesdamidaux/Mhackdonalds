# %% 
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

if __name__ == "__main__":
    # read demo/db_json_empty.json
    bedrock = boto3.client(
        "bedrock-runtime",
        region_name="us-west-2",
        aws_access_key_id="AKIAUMYCIUHUI2TD5FWW",
        aws_secret_access_key="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",
    )

    # MODEL_ID = "mistral.mistral-large-2407-v1:0" 
    MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    with open("demo/db_json_empty.json", "r", encoding="utf-8") as f:
        db_json = json.load(f)
    print(db_json)
    print("\n\n\n")
    db_json_new = fill_metadatas(db_json, bedrock, MODEL_ID)

    print(db_json_new)

# %%
