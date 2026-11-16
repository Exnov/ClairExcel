
import pandas as pd


def clean_dataframe(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Nettoie un DataFrame et identifie les anomalies.

    Retourne :
        - Le DataFrame nettoyé
        - Un DataFrame contenant les anomalies
    """

    # Copie pour préserver les données originales
    cleaned = dataframe.copy()

    anomalies = []

    # 1. Suppression des lignes totalement vides
    empty_rows = cleaned.isna().all(axis=1)
    removed_empty_rows = int(empty_rows.sum())

    cleaned = cleaned.loc[~empty_rows].copy()

    # 2. Nettoyage des cellules textuelles
    for column in cleaned.select_dtypes(include=["object", "string"]).columns:
        cleaned[column] = cleaned[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    # 3. Conversion des chaînes vides en valeurs manquantes
    cleaned = cleaned.replace(r"^\s*$", pd.NA, regex=True)

    # 4. Identification des lignes sans client
    if "client" in cleaned.columns:
        missing_clients = cleaned["client"].isna()

        for index in cleaned.index[missing_clients]:
            anomalies.append({
                "index_ligne": index,
                "type_anomalie": "Client manquant",
                "description": "La ligne ne contient pas de nom de client.",
            })

    # 5. Identification des dates manquantes
    if "date" in cleaned.columns:
        missing_dates = cleaned["date"].isna()

        for index in cleaned.index[missing_dates]:
            anomalies.append({
                "index_ligne": index,
                "type_anomalie": "Date manquante",
                "description": "La ligne ne contient pas de date.",
            })

    # 6. Identification des montants manquants
    if "montant_ht" in cleaned.columns:
        missing_amounts = cleaned["montant_ht"].isna()

        for index in cleaned.index[missing_amounts]:
            anomalies.append({
                "index_ligne": index,
                "type_anomalie": "Montant manquant",
                "description": "La ligne ne contient pas de montant HT.",
            })

    # 7. Construction du rapport d'anomalies
    anomalies_df = pd.DataFrame(
        anomalies,
        columns=[
            "index_ligne",
            "type_anomalie",
            "description",
        ],
    )

    # Ajout d'une information sur les lignes vides supprimées
    if removed_empty_rows > 0:
        anomalies_df.loc[len(anomalies_df)] = {
            "index_ligne": None,
            "type_anomalie": "Lignes vides supprimées",
            "description": (
                f"{removed_empty_rows} ligne(s) totalement vide(s) supprimée(s)."
            ),
        }

    return cleaned, anomalies_df
