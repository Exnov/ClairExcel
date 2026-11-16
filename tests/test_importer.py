
from io import BytesIO

import pandas as pd
import pytest

from core.importer import import_excel_file, ExcelImportError


def create_excel_file() -> BytesIO:
    """Crée un fichier Excel temporaire en mémoire."""

    dataframe = pd.DataFrame({
        "Client": ["Dupont", "Martin"],
        "Montant": [120, 250],
    })

    buffer = BytesIO()
    buffer.name = "test.xlsx"

    dataframe.to_excel(
        buffer,
        index=False,
        engine="openpyxl",
    )

    buffer.seek(0)
    return buffer


def test_import_excel_file():
    """Vérifie l'import d'un fichier Excel valide."""

    file = create_excel_file()

    result = import_excel_file(file)

    assert len(result) == 2
    assert "Client" in result.columns
    assert "Montant" in result.columns
    assert result.iloc[0]["Client"] == "Dupont"


def test_import_rejects_wrong_extension():
    """Vérifie le refus d'un fichier qui n'est pas un .xlsx."""

    file = BytesIO(b"contenu fictif")
    file.name = "document.csv"

    with pytest.raises(ExcelImportError):
        import_excel_file(file)


def test_import_rejects_invalid_excel():
    """Vérifie la gestion d'un fichier Excel illisible."""

    file = BytesIO(b"ceci n'est pas un fichier Excel")
    file.name = "fichier_invalide.xlsx"

    with pytest.raises(ExcelImportError):
        import_excel_file(file)
