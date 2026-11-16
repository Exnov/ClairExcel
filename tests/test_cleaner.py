
import pandas as pd

from core.cleaner import clean_dataframe


def test_remove_completely_empty_rows():
    dataframe = pd.DataFrame({
        "client": ["Dupont", None, None],
        "montant_ht": [120, None, None],
    })

    cleaned, anomalies = clean_dataframe(dataframe)

    assert len(cleaned) == 1
    assert len(anomalies) == 1
    assert anomalies.iloc[0]["type_anomalie"] == "Lignes vides supprimées"


def test_clean_text_spaces():
    dataframe = pd.DataFrame({
        "client": ["  Dupont  ", " Martin "],
    })

    cleaned, _ = clean_dataframe(dataframe)

    assert cleaned.iloc[0]["client"] == "Dupont"
    assert cleaned.iloc[1]["client"] == "Martin"


def test_detect_missing_client():
    dataframe = pd.DataFrame({
        "client": ["Dupont", None],
        "date": ["2026-01-15", "2026-01-16"],
        "montant_ht": [120, 250],
    })

    cleaned, anomalies = clean_dataframe(dataframe)

    assert len(cleaned) == 2
    assert "Client manquant" in anomalies["type_anomalie"].values


def test_detect_multiple_missing_values():
    dataframe = pd.DataFrame({
        "client": ["Dupont"],
        "date": [None],
        "montant_ht": [None],
    })

    _, anomalies = clean_dataframe(dataframe)

    assert "Date manquante" in anomalies["type_anomalie"].values
    assert "Montant manquant" in anomalies["type_anomalie"].values


def test_cleaner_does_not_modify_original():
    dataframe = pd.DataFrame({
        "client": ["  Dupont  "],
    })

    clean_dataframe(dataframe)

    assert dataframe.iloc[0]["client"] == "  Dupont  "
