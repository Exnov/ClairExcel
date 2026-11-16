
import pandas as pd
import pytest

from core.consolidator import (
    consolidate_dataframes,
    ConsolidationError,
)


def create_file_a():
    return pd.DataFrame({
        "Nom Client": ["Dupont", "Martin"],
        "Date intervention": ["2026-01-15", "2026-01-16"],
        "Montant HT": [120, 250],
    })


def create_file_b():
    return pd.DataFrame({
        "Client": ["Dupont", "Durand"],
        "Date": ["2026-01-15", "2026-01-20"],
        "Prix": [120, 180],
    })


def test_consolidate_multiple_files():
    files = [
        ("janvier.xlsx", create_file_a()),
        ("fevrier.xlsx", create_file_b()),
    ]

    unique_rows, duplicates, anomalies = consolidate_dataframes(files)

    assert len(unique_rows) == 3
    assert len(duplicates) == 1
    assert anomalies.empty


def test_preserve_source_filename():
    files = [
        ("janvier.xlsx", create_file_a()),
        ("fevrier.xlsx", create_file_b()),
    ]

    unique_rows, duplicates, _ = consolidate_dataframes(files)

    assert "source_file" in unique_rows.columns
    assert "janvier.xlsx" in unique_rows["source_file"].values
    assert duplicates.iloc[0]["source_file"] == "fevrier.xlsx"


def test_anomalies_keep_source_filename():
    dataframe = pd.DataFrame({
        "Nom Client": ["Dupont", None],
        "Date intervention": ["2026-01-15", "2026-01-16"],
        "Montant HT": [120, 250],
    })

    _, _, anomalies = consolidate_dataframes([
        ("janvier.xlsx", dataframe),
    ])

    assert len(anomalies) == 1
    assert anomalies.iloc[0]["source_file"] == "janvier.xlsx"
    assert anomalies.iloc[0]["type_anomalie"] == "Client manquant"


def test_custom_duplicate_subset():
    dataframe_a = pd.DataFrame({
        "Client": ["Dupont"],
        "Date": ["2026-01-15"],
        "Prix": [120],
    })

    dataframe_b = pd.DataFrame({
        "Client": ["Dupont"],
        "Date": ["2026-01-15"],
        "Prix": [180],
    })

    unique_rows, duplicates, _ = consolidate_dataframes(
        [
            ("a.xlsx", dataframe_a),
            ("b.xlsx", dataframe_b),
        ],
        duplicate_subset=["client", "date"],
    )

    assert len(unique_rows) == 1
    assert len(duplicates) == 1


def test_empty_file_list_raises_error():
    with pytest.raises(ConsolidationError):
        consolidate_dataframes([])


def test_reserved_source_column_raises_error():
    dataframe = pd.DataFrame({
        "Client": ["Dupont"],
        "Date": ["2026-01-15"],
        "Prix": [120],
        "Source File": ["origine.xlsx"],
    })

    with pytest.raises(ConsolidationError):
        consolidate_dataframes([
            ("fichier.xlsx", dataframe),
        ])
