#################################### PROMPTS FOR METADATA TASK #######################################


INTRO_METADATA = """## Database Schema Context ##
You will be provided with a JSON database schema containing:
1. Table structures with CREATE statements
2. Example data rows
3. Existing column_description (some may be incomplete)
4. Business context documentation

Schema Overview:
"""

TASK_METADATA = """## Task Instructions ##
1. Analyze the business context and existing schema
2. Complete MISSING column descriptions using:
   - Table/column naming patterns
   - Data type implications
   - Example row values analysis
   - Contextual business domain knowledge
3. Maintain technical accuracy and consistency with existing descriptions
4. Never invent information beyond what can be reasonably inferred

Required Action: Fill ONLY empty "column_description" fields in the JSON structure."""

FORMAT_METADATA = """## Strict Response Requirements ##
1. Return EXACTLY the original JSON structure
2. Add/change ONLY missing "column_description" values
3. JSON must remain parseable with:
   - Identical table/column names
   - Original data types preserved
   - Example rows unchanged
4. No additional text or formatting outside the JSON

Response must begin with: {"""

#################################### PROMPTS FOR CONSTRAINTS TASK ####################################

INTRO_CONSTRAINTS = """Analyze the following database schema to identify data quality constraints. Consider these aspects:
1. Domain Integrity Constraints
2. Temporal Consistency Rules
3. Business Logic Validation
4. Cross-Table Dependency Rules

Never try to use table or column names that are not present in the Database Schema.
Database Schema:"""

TASK_CONSTRAINTS = """"Generate a comprehensive list of data validation constraints that should be enforced to ensure:
- Data integrity
- Temporal coherence in date fields
- Valid value ranges for numerical columns
- Consistent categorical values
- Domain-specific business rules

Include for each constraint:
1. Constraint type and Description of the rule
2. Affected columns/tables

Never try to use table or column names that are not present in the Database Schema."""

VALID_CONSTRAINTS = """# Valid Data Quality Constraint Example"""

INVALID_CONSTRAINTS = """# Invalid Constraint Example ❌"""


def get_format_constraints(n):
    return f"Generate a JSON object containing exactly {n}" + """ constraints following this structure:
{
    "constraints": [
        {
            "tables": ["table_name_used_1","table_name_used_2",...],
            "columns": ["column_name_used_1","column_name_used_2",...],
            "description": "Clear constraint explanation"
        }
    ]
}
- For each constraint:
  - Populate 'tables' and 'columns' arrays with relevant names
  - Write specific descriptions explaining each constraint
- Return ONLY the JSON object without additional text
- Maintain strict adherence to the specified structure
"""


