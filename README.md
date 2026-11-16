# ClairExcel

**Vos fichiers Excel réunis, vos données vérifiées, votre temps préservé.**

ClairExcel est un outil de traitement et de consolidation de fichiers Excel, conçu pour simplifier la gestion des données des artisans, TPE, associations et petites structures.

## Fonctionnalités

- Import de plusieurs fichiers Excel (`.xlsx`).
- Normalisation des intitulés de colonnes.
- Nettoyage des données.
- Consolidation des fichiers.
- Détection des doublons.
- Identification des anomalies.
- Export d'un rapport Excel avec plusieurs feuilles de résultats.

## Technologies utilisées

- Python
- Streamlit
- Pandas
- Openpyxl

## Installation en local

Cloner le dépôt :

```bash
git clone URL_DU_DEPOT
cd automatisation_excel
```

Créer un environnement virtuel :

```bash
python -m venv .venv
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Lancer l'application :

```bash
streamlit run app.py
```

## Utilisation

L'application propose un mode de démonstration avec des fichiers d'exemple ainsi qu'un mode permettant d'importer ses propres fichiers Excel.

Pour que l'import fonctionne, les fichiers doivent utiliser des intitulés de colonnes reconnus par l'application.

## Statut du projet

Projet en développement – version de démonstration.