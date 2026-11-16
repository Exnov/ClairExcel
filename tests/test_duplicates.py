
import pandas as pd
import pytest

from core.duplicates import (
    detect_duplicates,
    DuplicateDetectionError,
)


def create_dataframe():
    return pd.DataFrame({
        "client": ["Dupont", "Martin", "Dupont", "Dupont"],
        "date": [
            "2026-01-15",
            "2026-01-16",
            "2026-01-15",
            "2026-01-20",
        ],
        "montant_ht": [120, 250, 120, 180],
    })


def test_detect_duplicates():
    dataframe = create_dataframe()

    unique_rows, duplicates = detect_duplicates(dataframe)

    assert len(unique_rows) == 3
    assert len(duplicates) == 1
    assert duplicates.iloc[0]["client"] == "Dupont"


def test_custom_duplicate_columns():
    dataframe = pd.DataFrame({
        "client": ["Dupont", "Dupont", "Martin"],
        "date": ["2026-01-15", "2026-01-15", "2026-01-16"],
        "montant_ht": [120, 180, 250],
    })

    unique_rows, duplicates = detect_duplicates(
        dataframe,
        subset=["client", "date"],
    )

    assert len(unique_rows) == 2
    assert len(duplicates) == 1


def test_missing_key_values_are_preserved():
    dataframe = pd.DataFrame({
        "client": ["Dupont", "Dupont", None, None],
        "date": [
            "2026-01-15",
            "2026-01-15",
            "2026-01-15",
            "2026-01-15",
        ],
        "montant_ht": [120, 120, 120, 120],
    })

    unique_rows, duplicates = detect_duplicates(dataframe)

    assert len(unique_rows) == 3
    assert len(duplicates) == 1
    assert unique_rows["client"].isna().sum() == 2


def test_missing_column_raises_error():
    dataframe = pd.DataFrame({
        "client": ["Dupont"],
    })

    with pytest.raises(DuplicateDetectionError):
        detect_duplicates(dataframe)


def test_empty_subset_raises_error():
    dataframe = create_dataframe()

    with pytest.raises(DuplicateDetectionError):
        detect_duplicates(dataframe, subset=[])
