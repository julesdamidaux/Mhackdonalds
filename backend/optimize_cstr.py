from find_constraints import generate_constraints
import json

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