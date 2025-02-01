import sqlite3
import pandas as pd

# Fonction pour charger les données CSV dans une table SQLite
def load_csv_to_sqlite(csv_file, table_name, conn):
    df = pd.read_csv(csv_file)
    df.to_sql(table_name, conn, if_exists='replace', index=False)

# Connexion à la base SQLite (création si n'existe pas)
conn = sqlite3.connect("veolia_data.db")
cursor = conn.cursor()

# Activer les clés étrangères dans SQLite
cursor.execute("PRAGMA foreign_keys = ON;")

# Création des tables avec les clés primaires et étrangères
cursor.execute("""
    CREATE TABLE IF NOT EXISTS abonnements (
        abonnement_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_nom TEXT NOT NULL,
        client_prenom TEXT NOT NULL,
        adresse TEXT NOT NULL,
        date_abonnement TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS consos (
        conso_id INTEGER PRIMARY KEY AUTOINCREMENT,
        abonnement_id INTEGER,
        mois TEXT NOT NULL,
        consommation REAL NOT NULL,
        FOREIGN KEY (abonnement_id) REFERENCES abonnements(abonnement_id)
    );
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS factures (
        facture_id INTEGER PRIMARY KEY AUTOINCREMENT,
        abonnement_id INTEGER,
        date_facture TEXT NOT NULL,
        montant REAL NOT NULL,
        statut TEXT NOT NULL,
        FOREIGN KEY (abonnement_id) REFERENCES abonnements(abonnement_id)
    );
""")

# Charger les données des CSV dans les tables correspondantes
load_csv_to_sqlite("veolia-data-abonnements.csv", "abonnements", conn)
load_csv_to_sqlite("veolia-data-consos.csv", "consos", conn)
load_csv_to_sqlite("veolia-data-factures.csv", "factures", conn)

# Sauvegarder les changements et fermer la connexion
conn.commit()
conn.close()

print("Base de données SQLite créée avec succès !")
