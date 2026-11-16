
import pandas as pd


class DuplicateDetectionError(Exception):
    """Erreur lors de la détection des doublons."""


def detect_duplicates(
    dataframe: pd.DataFrame,
    subset: list[str] | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Détecte les doublons selon les colonnes choisies.

    Args:
        dataframe: Tableau de données à analyser.
        subset: Colonnes utilisées pour identifier un doublon.
                Par défaut : client, date et montant_ht.

    Returns:
        Un tuple contenant :
        - Le DataFrame sans doublons détectés.
        - Le DataFrame des lignes identifiées comme doublons.

    Les lignes ayant une valeur manquante dans une colonne clé
    sont conservées et ne sont pas considérées comme des doublons.
    """

    if subset is None:
        subset = ["client", "date", "montant_ht"]

    if not subset:
        raise DuplicateDetectionError(
            "Vous devez sélectionner au moins une colonne."
        )

    # Vérification de l'existence des colonnes
    missing_columns = [
        column for column in subset
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise DuplicateDetectionError(
            "Colonnes introuvables : "
            + ", ".join(missing_columns)
        )

    # Les lignes dont une clé est incomplète sont conservées.
    complete_key = dataframe[subset].notna().all(axis=1)

    # Détection des doublons uniquement parmi les clés complètes
    duplicate_mask = pd.Series(
        False,
        index=dataframe.index,
        dtype=bool,
    )

    duplicate_mask.loc[complete_key] = (
        dataframe.loc[complete_key]
        .duplicated(subset=subset, keep="first")
    )

    # Séparation des lignes conservées et des doublons
    duplicates = dataframe.loc[duplicate_mask].copy()
    unique_rows = dataframe.loc[~duplicate_mask].copy()

    return unique_rows, duplicates
