from create_database_json_from_database import get_database_json_from_database

db_path = "data/veolia_data.db"
contexte = "test réussi"
input_json = "data/input.json"

if __name__ == "__main__":

    database_json = get_database_json_from_database(db_path, contexte, input_json, save_json=False)


"""

subprocess.run(["python", "generate_constraints.py"], capture_output=True, text=True)"""