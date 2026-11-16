
import pandas as pd
import pytest

from core.validator import (
    validate_dataframe,
    DataValidationError,
)


def create_valid_dataframe():
    return pd.DataFrame({
        "client": ["Dupont", "Martin"],
        "date": ["15/01/2026", "16/01/2026"],
        "montant_ht": [120, 250],
    })


def test_valid_dataframe_has_no_anomalies():
    dataframe = create_valid_dataframe()

    report = validate_dataframe(dataframe)

    assert report.empty


def test_detect_invalid_date():
    dataframe = create_valid_dataframe()
    dataframe.loc[0, "date"] = "35/15/2026"

    report = validate_dataframe(dataframe)

    assert "Date invalide" in report["type_anomalie"].values


def test_detect_invalid_amount():
    dataframe = create_valid_dataframe()

    # On convertit la colonne en texte pour accepter "ABC"
    dataframe["montant_ht"] = dataframe["montant_ht"].astype("object")
    dataframe.loc[0, "montant_ht"] = "ABC"

    report = validate_dataframe(dataframe)

    assert "Montant invalide" in report["type_anomalie"].values


def test_detect_negative_amount():
    dataframe = create_valid_dataframe()
    dataframe.loc[0, "montant_ht"] = -50

    report = validate_dataframe(dataframe)

    anomaly = report[
        report["type_anomalie"] == "Montant négatif"
    ]

    assert len(anomaly) == 1
    assert anomaly.iloc[0]["niveau"] == "avertissement"


def test_detect_missing_client():
    dataframe = create_valid_dataframe()
    dataframe.loc[0, "client"] = None

    report = validate_dataframe(dataframe)

    assert "Client manquant" in report["type_anomalie"].values


def test_missing_required_column_raises_error():
    dataframe = pd.DataFrame({
        "client": ["Dupont"],
        "date": ["15/01/2026"],
    })

    with pytest.raises(DataValidationError):
        validate_dataframe(dataframe)


def test_validation_does_not_modify_original():
    dataframe = create_valid_dataframe()
    original = dataframe.copy(deep=True)

    validate_dataframe(dataframe)

    pd.testing.assert_frame_equal(dataframe, original)
