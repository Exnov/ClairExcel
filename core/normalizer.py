
import re
import unicodedata

import pandas as pd

from config.column_mapping import COLUMN_MAPPING


class ColumnNormalizationError(Exception):
    """Erreur lors de la normalisation des colonnes."""


def normalize_column_name(column_name: str) -> str:
    """
    Transforme un intitulé de colonne en nom standardisé.

    Exemple :
        'Nom Client' -> 'nom_client'
        'Montant HT' -> 'montant_ht'
    """

    # Conversion en minuscules
    name = str(column_name).strip().lower()

    # Suppression des accents
    name = unicodedata.normalize("NFKD", name)
    name = "".join(
        character
        for character in name
        if not unicodedata.combining(character)
    )

    # Remplacement des caractères non alphanumériques
    # par des underscores
    name = re.sub(r"[^a-z0-9]+", "_", name)

    # Suppression des underscores au début et à la fin
    name = name.strip("_")

    return name


def normalize_dataframe_columns(
    dataframe: pd.DataFrame,
    mapping: dict | None = None,
) -> pd.DataFrame:
    """
    Standardise les noms des colonnes d'un DataFrame.

    Les synonymes sont convertis selon le dictionnaire
    de correspondance fourni.
    """

    if mapping is None:
        mapping = COLUMN_MAPPING

    # Normalisation préalable des clés du dictionnaire
    normalized_mapping = {
        normalize_column_name(alias): standard_name
        for alias, standard_name in mapping.items()
    }

    new_columns = []

    for column in dataframe.columns:
        normalized_name = normalize_column_name(column)

        # Recherche d'une correspondance
        standard_name = normalized_mapping.get(
            normalized_name,
            normalized_name,
        )

        new_columns.append(standard_name)

    # Détection des doublons de noms de colonnes
    if len(new_columns) != len(set(new_columns)):
        duplicates = [
            name
            for name in set(new_columns)
            if new_columns.count(name) > 1
        ]

        raise ColumnNormalizationError(
            "Plusieurs colonnes aboutissent au même nom : "
            + ", ".join(sorted(duplicates))
        )

    # Copie du DataFrame pour ne pas modifier l'original
    result = dataframe.copy()
    result.columns = new_columns

    return result
