import subprocess
import sql_get_create

subprocess.run(["python", "generate_veolia_cb.py.py"], capture_output=True, text=True)

sql_get_create.main()

subprocess.run(["python", "fill_metadatas.py"], capture_output=True, text=True)

subprocess.run(["python", "generate_constraints.py"], capture_output=True, text=True)