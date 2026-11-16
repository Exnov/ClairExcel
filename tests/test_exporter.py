
import pandas as pd

from core.exporter import export_consolidation_to_excel


def create_test_data():
    consolidated = pd.DataFrame({
        "client": ["Dupont", "Martin"],
        "date": ["15/01/2026", "16/01/2026"],
        "montant_ht": [120, 250],
        "source_file": ["fichier1.xlsx", "fichier2.xlsx"],
    })

    duplicates = pd.DataFrame({
        "client": ["Dupont"],
        "date": ["15/01/2026"],
        "montant_ht": [120],
    })

    anomalies = pd.DataFrame({
        "index_ligne": [2],
        "type_anomalie": ["Date invalide"],
        "description": ["La date est incorrecte."],
    })

    return consolidated, duplicates, anomalies


def test_export_creates_excel_file():
    consolidated, duplicates, anomalies = create_test_data()

    result = export_consolidation_to_excel(
        consolidated,
        duplicates,
        anomalies,
    )

    assert result.getvalue()


def test_export_contains_all_sheets():
    consolidated, duplicates, anomalies = create_test_data()

    result = export_consolidation_to_excel(
        consolidated,
        duplicates,
        anomalies,
    )

    workbook = pd.ExcelFile(result)

    assert "Données consolidées" in workbook.sheet_names
    assert "Doublons détectés" in workbook.sheet_names
    assert "Anomalies" in workbook.sheet_names
    assert "Statistiques" in workbook.sheet_names


def test_export_statistics_are_correct():
    consolidated, duplicates, anomalies = create_test_data()

    result = export_consolidation_to_excel(
        consolidated,
        duplicates,
        anomalies,
    )

    stats = pd.read_excel(result, sheet_name="Statistiques")

    assert stats.loc[0, "Valeur"] == 2
    assert stats.loc[1, "Valeur"] == 1
    assert stats.loc[2, "Valeur"] == 1
    assert stats.loc[3, "Valeur"] == 2


def test_export_statistics_separate_anomaly_levels():
    consolidated, duplicates, anomalies = create_test_data()

    anomalies = pd.DataFrame({
        "type_anomalie": [
            "Date invalide",
            "Montant négatif",
            "Ligne vide supprimée",
        ],
        "niveau": [
            "erreur",
            "avertissement",
            "nettoyage",
        ],
    })

    result = export_consolidation_to_excel(
        consolidated,
        duplicates,
        anomalies,
    )

    stats = pd.read_excel(
        result,
        sheet_name="Statistiques",
    )

    values = dict(
        zip(stats["Indicateur"], stats["Valeur"])
    )

    assert values["Nombre total d'anomalies"] == 3
    assert values["Nombre d'erreurs"] == 1
    assert values["Nombre d'avertissements"] == 1
    assert values["Nombre d'anomalies de nettoyage"] == 1
