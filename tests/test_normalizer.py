
import pandas as pd
import pytest

from core.normalizer import (
    normalize_column_name,
    normalize_dataframe_columns,
    ColumnNormalizationError,
)


def test_normalize_column_name():
    assert normalize_column_name("Nom Client") == "nom_client"
    assert normalize_column_name("Montant HT") == "montant_ht"
    assert normalize_column_name("Date d'intervention") == "date_d_intervention"
    assert normalize_column_name("  Adresse Client  ") == "adresse_client"


def test_normalize_dataframe_columns():
    dataframe = pd.DataFrame({
        "Nom Client": ["Dupont"],
        "Date intervention": ["2026-01-15"],
        "Montant HT": [120],
        "Adresse client": ["Saint-Brieuc"],
    })

    result = normalize_dataframe_columns(dataframe)

    assert list(result.columns) == [
        "client",
        "date",
        "montant_ht",
        "adresse",
    ]


def test_normalize_unknown_column():
    dataframe = pd.DataFrame({
        "Téléphone professionnel": ["0600000000"],
    })

    result = normalize_dataframe_columns(dataframe)

    assert list(result.columns) == ["telephone_professionnel"]


def test_detect_duplicate_columns():
    dataframe = pd.DataFrame({
        "Nom Client": ["Dupont"],
        "Client": ["Martin"],
    })

    with pytest.raises(ColumnNormalizationError):
        normalize_dataframe_columns(dataframe)
