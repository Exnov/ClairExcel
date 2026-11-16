
from pathlib import Path
from typing import Any

import pandas as pd


class ExcelImportError(Exception):
    """Erreur rencontrée lors de l'import d'un fichier Excel."""


def import_excel_file(
    file: Any,
    sheet_name: str | int = 0,
) -> pd.DataFrame:
    """
    Importe une feuille d'un fichier Excel et retourne un DataFrame.

    Args:
        file: Chemin du fichier ou objet fichier (ex. Streamlit UploadedFile).
        sheet_name: Nom ou numéro de la feuille à importer.

    Returns:
        Un DataFrame contenant les données de la feuille.

    Raises:
        ExcelImportError: Si le fichier est invalide ou illisible.
    """

    # Récupération du nom du fichier
    filename = getattr(file, "name", str(file))
    extension = Path(filename).suffix.lower()

    # Vérification de l'extension
    if extension != ".xlsx":
        raise ExcelImportError(
            f"Format non pris en charge : {extension}. "
            "Veuillez fournir un fichier .xlsx."
        )

    try:
        # Certains objets fichier doivent être replacés au début
        if hasattr(file, "seek"):
            file.seek(0)

        # Lecture du fichier Excel
        dataframe = pd.read_excel(
            file,
            sheet_name=sheet_name,
            engine="openpyxl",
        )

        return dataframe

    except Exception as error:
        raise ExcelImportError(
            f"Impossible de lire le fichier « {filename} ». "
            f"Détail : {error}"
        ) from error
