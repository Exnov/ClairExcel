
import pandas as pd


class DataValidationError(Exception):
    """Erreur rencontrée pendant la validation des données."""


def validate_dataframe(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Vérifie la cohérence des données et retourne un rapport.

    Colonnes attendues :
        - client
        - date
        - montant_ht

    Les données originales ne sont jamais modifiées.

    Le rapport contient :
        - index_ligne
        - colonne
        - valeur
        - type_anomalie
        - niveau
        - description
    """

    required_columns = ["client", "date", "montant_ht"]

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise DataValidationError(
            "Colonnes obligatoires absentes : "
            + ", ".join(missing_columns)
        )

    anomalies = []

    # Vérification des clients
    for index, value in dataframe["client"].items():
        if pd.isna(value):
            anomalies.append({
                "index_ligne": index,
                "colonne": "client",
                "valeur": value,
                "type_anomalie": "Client manquant",
                "niveau": "erreur",
                "description": "Le nom du client est absent.",
            })

    # Vérification des dates
    parsed_dates = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
        dayfirst=True,
        format="mixed",
    )

    for index, value in dataframe["date"].items():
        if pd.isna(value):
            continue

        if pd.isna(parsed_dates.loc[index]):
            anomalies.append({
                "index_ligne": index,
                "colonne": "date",
                "valeur": value,
                "type_anomalie": "Date invalide",
                "niveau": "erreur",
                "description": "La valeur ne correspond pas à une date valide.",
            })

    # Vérification des montants
    numeric_amounts = pd.to_numeric(
        dataframe["montant_ht"],
        errors="coerce",
    )

    for index, value in dataframe["montant_ht"].items():
        if pd.isna(value):
            continue

        if pd.isna(numeric_amounts.loc[index]):
            anomalies.append({
                "index_ligne": index,
                "colonne": "montant_ht",
                "valeur": value,
                "type_anomalie": "Montant invalide",
                "niveau": "erreur",
                "description": "Le montant n'est pas une valeur numérique.",
            })

        elif numeric_amounts.loc[index] < 0:
            anomalies.append({
                "index_ligne": index,
                "colonne": "montant_ht",
                "valeur": value,
                "type_anomalie": "Montant négatif",
                "niveau": "avertissement",
                "description": (
                    "Le montant est négatif. "
                    "Une vérification est recommandée."
                ),
            })

    return pd.DataFrame(
        anomalies,
        columns=[
            "index_ligne",
            "colonne",
            "valeur",
            "type_anomalie",
            "niveau",
            "description",
        ],
    )
