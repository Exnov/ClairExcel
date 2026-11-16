
from pathlib import Path

import pandas as pd


def generate_excel_samples():
    # Dossier de destination
    output_folder = Path(__file__).parent / "data" / "samples"
    output_folder.mkdir(parents=True, exist_ok=True)

    # FICHIER 1 : interventions de janvier
    data_1 = {
        "Nom client": [
            "Dupont",
            "Martin",
            " Durand ",
            "Bernard",
            "Leroy",
        ],
        "Date intervention": [
            "15/01/2026",
            "16/01/2026",
            "18/01/2026",
            "20/01/2026",
            "22/01/2026",
        ],
        "Montant HT": [
            120,
            250,
            180,
            95,
            310,
        ],
        "Adresse client": [
            "Saint-Brieuc",
            "Pordic",
            "Plérin",
            "Trégueux",
            "Langueux",
        ],
    }

    # FICHIER 2 : autres interventions
    # Les noms de colonnes sont volontairement différents.
    data_2 = {
        "Nom du client": [
            "Dupont",       # Doublon du fichier 1
            "Le Goff",
            "Le Gall",
            "Petit",
            "Moreau",
            "Thomas",
        ],
        "Date": [
            "15/01/2026",   # Doublon du fichier 1
            "25/01/2026",
            "35/15/2026",   # Date invalide
            "28/01/2026",
            "30/01/2026",
            "31/01/2026",
        ],
        "Prix": [
            120,            # Doublon du fichier 1
            450,
            160,
            "ABC",          # Montant non numérique
            -50,            # Montant négatif
            220,
        ],
        "Adresse": [
            "Saint-Brieuc",
            "Ploufragan",
            "Pordic",
            "Plérin",
            "Saint-Brieuc",
            "Trégueux",
        ],
    }

    # Création des DataFrames
    dataframe_1 = pd.DataFrame(data_1)
    dataframe_2 = pd.DataFrame(data_2)

    # Ajout d'une ligne vide dans le premier fichier
    dataframe_1.loc[len(dataframe_1)] = [None, None, None, None]

    # Génération des fichiers Excel
    file_1 = output_folder / "interventions_janvier.xlsx"
    file_2 = output_folder / "interventions_fevrier.xlsx"

    dataframe_1.to_excel(file_1, index=False, engine="openpyxl")
    dataframe_2.to_excel(file_2, index=False, engine="openpyxl")

    print("Fichiers Excel générés avec succès !")
    print(f"Fichier 1 : {file_1}")
    print(f"Fichier 2 : {file_2}")


if __name__ == "__main__":
    generate_excel_samples()
