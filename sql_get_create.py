import sqlite3
import json

def extract_table_definitions(db_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # Récupérer les définitions des tables
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = {}
    
    for row in cursor.fetchall():
        table_name, create_sql = row
        if create_sql:
            # Récupérer les trois premières lignes de la table
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            column_names = [desc[0] for desc in cursor.description]  # Obtenir les noms de colonnes
            rows = cursor.fetchall()
            
            tables[table_name] = {
                "create_statement": create_sql,
                "columns" : {
                    "column_names" : column_names,
                    "column_meta_data" : ""
                },
                "first_3_rows": rows
            }
    
    conn.close()
    return tables

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"tables": data}, f, indent=4, ensure_ascii=False)

def save_to_txt(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        for table_name, table_info in data.items():
        
            f.write(f"\n{table_info['create_statement']}\n")
            f.write("\n3 premières lignes:\n")
            f.write("\t".join(table_info["columns"]["column_names"]) + "\n")
            for row in table_info["first_3_rows"]:
                f.write("\t".join(map(str, row)) + "\n")
            f.write("\n")

def main():
    input_db_file = "veolia_data.db"  # Remplace par le nom de ton fichier .db
    output_json_file = "tables.json"
    output_txt_file = "tables.txt"

    tables_data = extract_table_definitions(input_db_file)
    save_to_json(tables_data, output_json_file)
    save_to_txt(tables_data, output_txt_file)

    print(f"JSON généré avec succès : {output_json_file}")
    print(f"TXT généré avec succès : {output_txt_file}")
    for table_name, table_info in tables_data.items():
        print(f"\nCREATE TABLE pour {table_name}:")
        print(table_info["create_statement"])
        print("\n3 premières lignes:")
        print(table_info["columns"]["column_names"])
        for row in table_info["first_3_rows"]:
            print(row)

main()