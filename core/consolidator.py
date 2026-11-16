
import pandas as pd

from core.normalizer import normalize_dataframe_columns
from core.cleaner import clean_dataframe
from core.duplicates import detect_duplicates


class ConsolidationError(Exception):
    """Erreur rencontrée pendant la consolidation."""


def consolidate_dataframes(
    files: list[tuple[str, pd.DataFrame]],
    duplicate_subset: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Consolide plusieurs DataFrames Excel.

    Args:
        files:
            Liste de tuples (nom_du_fichier, DataFrame).
        duplicate_subset:
            Colonnes utilisées pour identifier les doublons.
            Par défaut : client, date et montant_ht.

    Returns:
        Trois DataFrames :
        - Les données consolidées sans doublons.
        - Les lignes identifiées comme doublons.
        - Le rapport des anomalies.

    Chaque ligne conserve son nom de fichier source.
    """

    if not files:
        raise ConsolidationError(
            "Aucun fichier n'a été fourni pour la consolidation."
        )

    if duplicate_subset is None:
        duplicate_subset = ["client", "date", "montant_ht"]

    processed_dataframes = []
    anomaly_reports = []

    # Traitement de chaque fichier
    for filename, dataframe in files:

        if not isinstance(dataframe, pd.DataFrame):
            raise ConsolidationError(
                f"Le contenu de « {filename} » n'est pas un DataFrame."
            )

        # 1. Normalisation des colonnes
        normalized = normalize_dataframe_columns(dataframe)

        # La colonne source est réservée au programme
        if "source_file" in normalized.columns:
            raise ConsolidationError(
                f"Le fichier « {filename} » contient une colonne "
                "'source_file' réservée au programme."
            )

        # 2. Nettoyage des données
        cleaned, anomalies = clean_dataframe(normalized)

        # 3. Conservation de la provenance
        cleaned["source_file"] = filename
        processed_dataframes.append(cleaned)

        if not anomalies.empty:
            anomalies["source_file"] = filename
            anomaly_reports.append(anomalies)

    # 4. Regroupement de tous les fichiers
    consolidated = pd.concat(
        processed_dataframes,
        ignore_index=True,
        sort=False,
    )

    # 5. Détection des doublons entre tous les fichiers
    try:
        unique_rows, duplicates = detect_duplicates(
            consolidated,
            subset=duplicate_subset,
        )
    except Exception as error:
        raise ConsolidationError(
            f"Impossible de détecter les doublons : {error}"
        ) from error

    # 6. Regroupement des rapports d'anomalies
    if anomaly_reports:
        all_anomalies = pd.concat(
            anomaly_reports,
            ignore_index=True,
        )
    else:
        all_anomalies = pd.DataFrame(
            columns=[
                "index_ligne",
                "type_anomalie",
                "description",
                "source_file",
            ]
        )

    return unique_rows, duplicates, all_anomalies
