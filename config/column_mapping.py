
"""
Correspondances entre les différents intitulés Excel
et les noms de colonnes standardisés du projet.
"""

COLUMN_MAPPING = {
    # Client
    "nom client": "client",
    "nom du client": "client",
    "client": "client",

    # Date
    "date intervention": "date",
    "date de l'intervention": "date",
    "date": "date",

    # Montant
    "montant ht": "montant_ht",
    "prix": "montant_ht",
    "montant": "montant_ht",

    # Adresse
    "adresse client": "adresse",
    "adresse du client": "adresse",
    "adresse": "adresse",
}
