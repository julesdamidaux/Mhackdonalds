# %%

import prompts
import json
import boto3

task_CoT = """
    Your task is to identify relationships, constraints, and rules necessary to ensure data consistency, accuracy, and reliability across related tables and fields.

    **Instructions:**  
    1. **Analyze Relationships:** For each pair of related tables, determine how their columns are connected.  
    2. **Define Constraints:** Specify rules that must be verified to maintain data integrity.
    3. **Step-by-Step Reasoning:** For each constraint, explain your thought process:  
    - Why is this relationship important?  
    - What potential issues could arise without this constraint?  
    - How does this constraint improve data consistency?  

    **Example:**  
    If *Column 1* in *Table A* and *Column 2* in *Table B* are related in any way, output a constraint that describes this relationship.  

"""


def format_CoT(n_constraints):
    return f"""
        For exactly {2 * n_constraints} constraints, follow these instructions carefully:

        1. **Identify the Constraint:** Clearly state the relation or constraint.  
        2. **Specify Involved Tables and Columns:** List all tables and columns relevant to the constraint.  
        3. **Step-by-Step Reasoning:** Explain how the constraint applies, breaking down the logic step by step. Focus on why this constraint is important and how it relates to the data structure.  

        **Output Format:**  
        - **Constraint 1:**  
        - **Tables:** [list of tables]  
        - **Columns:** [list of columns]  
        - **Reasoning:** [detailed, step-by-step explanation]  

        - **Constraint 2:**  
        - **Tables:** [list of tables]  
        - **Columns:** [list of columns]  
        - **Reasoning:** [detailed, step-by-step explanation]  

        ...continue until you have exactly {n_constraints} constraints.  

        **Important Notes:**  
        - List constraints from the most relevant to the least relevant.  
        - Do NOT include any additional text or explanations outside the specified format.  
        - Ensure there are exactly {n_constraints} constraints in total.  

    """

def task_discriminator(n_constraints):
    return f"""
    Your task is to identify relationships, constraints, and rules necessary to ensure data consistency, accuracy, and reliability across related tables and fields.
    Use your previous answer to answer. You have to choose {n_constraints} constraints among the {2 * n_constraints} you proposed. Output a json containing exactly {n_constraints} constraints.
"""

def format_discriminator(n_constraints):
    return f"Answer by providing a json describing exactly {n_constraints} " + """constraints with the following structure: \n
    {
    "constraints": [
    {
    "tables": [],
    "columns": [],
    "description": ""
    }
    ]
    }
    For each constraint, specify the tables and columns involved, and provide a description of the constraint. Do not give me anything more than this json containing n constraints.\n
    """


def generate_constraints(n_constraints, initial_prompt, db_json, MODEL_ID, bedrock,
                         valid_constraints, invalid_constraints, return_cot=False):

    if not initial_prompt : # initial prompt
        db_string = json.dumps(db_json)
        initial_prompt = prompts.INTRO_CONSTRAINTS + "\n" + db_string + "\n" + task_CoT
        message_list = [{
            "role": "user",
            "content": [{"text": initial_prompt}],
        }]
        prompt = initial_prompt

    else:

        few_shot_message = get_few_shot_prompt(valid_constraints, invalid_constraints)
        
        prompt = initial_prompt + "\n" + few_shot_message

        message_list = [{
            "role": "user",
            "content": [{"text": prompt}],
        }]


    response_cot = bedrock.converse(
        modelId=MODEL_ID,
        messages=message_list,
        system=[{"text": prompts.get_format_constraints(n_constraints)}],
        inferenceConfig={"temperature":1}, # temperature
    )

    output_cot = response_cot["output"]["message"]["content"][0]["text"]

    ###### run through discriminator

    message_list = [{
        "role": "user",
        "content": [{"text": prompt}],
    },
    {
        "role": "assistant",
        "content": [{"text": output_cot}]
    },
    {
        "role": "user",
        "content": [{"text": task_discriminator(n_constraints)}]
    }]

    response = bedrock.converse(
        modelId=MODEL_ID,
        messages=message_list,
        system=[{"text": format_discriminator(n_constraints)}],
        inferenceConfig={"temperature": 0.1}, # temperature
    )

    output = response["output"]["message"]["content"][0]["text"]

    if output.startswith("```json"):
        output = output.split("\n", 1)[1]
    if output.endswith("```"):
        output = output.rsplit("\n", 1)[0]

    output = json.loads(output)

    if return_cot:
        return output, initial_prompt, output_cot

    return output, initial_prompt

def get_few_shot_prompt(valid_constraints, invalid_constraints):
    prompt = "Here are some examples of relevant and irrelevant constraints:\n"
    for constraint in valid_constraints:
        prompt += prompts.VALID_CONSTRAINTS + "\n" + json.dumps(constraint) + "\n"
    for constraint in invalid_constraints:
        prompt += prompts.INVALID_CONSTRAINTS + "\n" + json.dumps(constraint) + "\n"
    return prompt

    

# %%
