# Veolia Project - Data Base Error Analyser

Une brève description de ton projet.

## Table des Matières

- [Installation](#installation)
- [Utilisation](#utilisation)
- [Structure du Projet](#structure-du-projet)
- [Contribuer](#contribuer)

## Installation

Instructions pour installer et configurer le projet localement.

```bash
# Clone le dépôt
git clone https://github.com/julesdamidaux/Mhackdonalds.git

#Créer un venv dans Mhackdonalds

#Activer votre venv
source activate

# pip
pip install -r requirements.txt

# Démarrer le frontend
streamlite run frontend/app.py
```

## Utilisation

1.

Une fois le front-end lancé vous pouvez 
- Remplissez le nom de votre Database sur Redshift
- Ajouter un descriptif JSON de la Database de la forme suivante :
```json
{
    "tables": {
        "table_name1": {
            "create_statement": "CREATE TABLE statement",
            "example": [
                ["col1", "col2", ...],
                ["val1", "val2", ...],
                ...
            ],
            "column1": {
                "column_names": "col1",
                "column_description": "description of the columns",
                "type": "type of the column"
            },
            "column2: {
                "column_names": "col2",
                "column_description": "description of the columns",
                "type": "type of the column"
            },
            ...

    "contexte": "description du contexte"
    }
}
```
- Ajouter un fichier contexte.txt qui décrit le contexte d'utilisation de votre Base de Donnée

Les informations manquantes seront complétées par un block LLM.

2.

Des suggestions de requetes SQL vous seront proposé, vous pouvez choisir les meilleurs et avec un system de feedback et de few-shot prompt a partir de vos préférences le LLM vous repropose des nouvelles idées.

Pour finir un block se charge de la convertion en SQL des idées et les éxécutes via un lien Redshift sur la Database

## Structure du Projet

![Alt text](hackaton_diagrammev2.drawio.png)

## Contribuer

- Jules D.
- Rodrigue R.
- Adrien G.
- Maxence A.
