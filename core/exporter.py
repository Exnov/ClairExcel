
from io import BytesIO

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


class ExcelExportError(Exception):
    """Erreur rencontrée lors de l'export Excel."""


def export_consolidation_to_excel(
    consolidated: pd.DataFrame,
    duplicates: pd.DataFrame,
    anomalies: pd.DataFrame,
) -> BytesIO:
    """
    Génère un classeur Excel avec les données consolidées,
    les doublons, les anomalies et les statistiques.
    """

    buffer = BytesIO()

    # Répartition des anomalies par catégorie
    if "niveau" in anomalies.columns:
        levels = anomalies["niveau"].fillna("nettoyage")
    else:
        levels = pd.Series(
            ["nettoyage"] * len(anomalies),
            index=anomalies.index,
        )

    error_count = int((levels == "erreur").sum())
    warning_count = int((levels == "avertissement").sum())
    cleaning_count = int((levels == "nettoyage").sum())

    # Nombre de fichiers sources, en tenant compte
    # des données conservées et des doublons.
    source_names = []

    for dataframe in [consolidated, duplicates]:
        if "source_file" in dataframe.columns:
            source_names.extend(
                dataframe["source_file"].dropna().tolist()
            )

    source_count = len(set(source_names))

    # Tableau des statistiques
    stats = pd.DataFrame({
        "Indicateur": [
            "Nombre de lignes consolidées",
            "Nombre de doublons détectés",
            "Nombre total d'anomalies",
            "Nombre de fichiers sources",
            "Nombre d'erreurs",
            "Nombre d'avertissements",
            "Nombre d'anomalies de nettoyage",
        ],
        "Valeur": [
            len(consolidated),
            len(duplicates),
            len(anomalies),
            source_count,
            error_count,
            warning_count,
            cleaning_count,
        ],
    })

    sheets = {
        "Données consolidées": consolidated,
        "Doublons détectés": duplicates,
        "Anomalies": anomalies,
        "Statistiques": stats,
    }

    try:
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

            for sheet_name, dataframe in sheets.items():
                dataframe.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                )

            workbook = writer.book

            for worksheet in workbook.worksheets:

                # Figer la première ligne
                worksheet.freeze_panes = "A2"

                # Mise en forme de l'en-tête
                for cell in worksheet[1]:
                    cell.font = Font(
                        bold=True,
                        color="FFFFFF",
                    )
                    cell.fill = PatternFill(
                        fill_type="solid",
                        fgColor="1F4E78",
                    )
                    cell.alignment = Alignment(
                        horizontal="center"
                    )

                # Ajouter les filtres
                if worksheet.max_row >= 1 and worksheet.max_column >= 1:
                    worksheet.auto_filter.ref = worksheet.dimensions

                # Ajuster la largeur des colonnes
                for column_cells in worksheet.columns:
                    max_length = 0

                    column_letter = get_column_letter(
                        column_cells[0].column
                    )

                    for cell in column_cells:
                        if cell.value is not None:
                            max_length = max(
                                max_length,
                                len(str(cell.value)),
                            )

                    worksheet.column_dimensions[
                        column_letter
                    ].width = min(max_length + 2, 40)

        buffer.seek(0)
        return buffer

    except Exception as error:
        raise ExcelExportError(
            f"Impossible de générer le fichier Excel : {error}"
        ) from error
