INTRO_CONSTRAINTS = "Here is the description of a database: \n"

TASK_CONSTRAINTS = "Find the relationships, constraints and rules that should be verified to ensure data consistency, accuracy, and reliability across related tables and fields. \n"

VALID_CONSTRAINTS = "This is a valid and interesting constraint: \n"

INVALID_CONSTRAINTS = "This is a an invalid or uninteresting constraint, that you should avoid to output: \n"


def get_format_constraints(n):

    return f"Answer by providing a json describing exactly {n} " + """constraints with the following structure: \n
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