
from pathlib import Path

import pandas as pd
import streamlit as st

from core.importer import import_excel_file
from core.consolidator import consolidate_dataframes
from core.validator import validate_dataframe
from core.exporter import export_consolidation_to_excel


# Limites du démonstrateur pour les fichiers importés
MAX_FILES = 5
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# --------------------------------------------------
# FONCTIONS D'AFFICHAGE
# --------------------------------------------------

def prepare_anomaly_view(dataframe):
    """Prépare un tableau d'anomalies facile à lire."""

    result = dataframe.copy()

    # Fusionner les deux éventuelles colonnes de fichier source
    if "source_file" in result.columns and "fichier_source" in result.columns:

        result["source_file"] = result["source_file"].fillna(
            result["fichier_source"]
        )

        result = result.drop(columns=["fichier_source"])

    elif "fichier_source" in result.columns:

        result = result.rename(
            columns={"fichier_source": "source_file"}
        )

    column_labels = {
        "source_file": "Fichier source",
        "index_ligne": "Ligne concernée",
        "colonne": "Colonne concernée",
        "valeur": "Valeur détectée",
        "type_anomalie": "Type de problème",
        "niveau": "Catégorie",
        "description": "Explication",
    }

    preferred_columns = [
        "source_file",
        "index_ligne",
        "colonne",
        "valeur",
        "type_anomalie",
        "niveau",
        "description",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in result.columns
    ]

    if not available_columns:
        return result

    result = result[available_columns].copy()
    result = result.rename(columns=column_labels)

    return result



def prepare_duplicate_view(dataframe):
    """Prépare un tableau de doublons lisible."""

    result = dataframe.copy()

    column_labels = {
        "client": "Client",
        "date": "Date",
        "montant_ht": "Montant HT",
        "adresse": "Adresse",
        "source_file": "Fichier source",
    }

    result = result.rename(columns=column_labels)

    return result


# --------------------------------------------------
# CONFIGURATION DE LA PAGE
# --------------------------------------------------

st.set_page_config(
    page_title="ClairExcel",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main {
        background-color: #f7f9fc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# EN-TÊTE CLAIREXCEL
# --------------------------------------------------

st.markdown(
    """
    <div style="
        padding: 25px;
        border-radius: 12px;
        background: linear-gradient(120deg, #17365D, #2878C8);
        color: white;
        margin-bottom: 25px;
    ">
        <h1 style="margin: 0;">📊 ClairExcel</h1>
        <p style="font-size: 18px; margin-bottom: 0;">
            Vos fichiers Excel réunis, vos données vérifiées,
            votre temps préservé.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# ONGLETS PRINCIPAUX
# --------------------------------------------------

tab_traitement, tab_presentation = st.tabs(
    [
        "📊 Traitement des fichiers",
        "ℹ️ Présentation de ClairExcel",
    ]
)


# ==================================================
# ONGLET 1 : TRAITEMENT DES FICHIERS
# ==================================================

with tab_traitement:

    st.subheader("Bienvenue dans votre espace de traitement")

    # --------------------------------------------------
    # PRÉSENTATION DE L'ACCUEIL
    # --------------------------------------------------

    st.markdown(
        """
        <div style="
            background-color: white;
            padding: 22px;
            border-radius: 12px;
            border: 1px solid #e5eaf0;
            margin-bottom: 20px;
        ">
            <h2 style="color: #17365D; margin-top: 0;">
                Bienvenue sur ClairExcel
            </h2>
            <p style="font-size: 17px; color: #44546A;">
                Simplifiez le traitement de vos fichiers Excel.
            </p>
            <p style="color: #667085;">
                Regroupez vos données, détectez les doublons,
                identifiez les anomalies et gagnez du temps.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Comment souhaitez-vous commencer ?")

    # --------------------------------------------------
    # CHOIX DU MODE DE DÉMONSTRATION
    # --------------------------------------------------

    st.subheader("1. Choisissez votre mode de test")

    demo_mode = st.radio(
        "Choisissez votre expérience :",
        [
            "Découvrir ClairExcel",
            "Tester mes propres fichiers",
        ],
        captions=[
            "Découvrir l'outil avec deux fichiers d'exemple, sans importation.",
            "Importer vos propres fichiers Excel pour les analyser.",
        ],
        horizontal=True,
    )

    if demo_mode == "Tester mes propres fichiers":
        st.warning(
            """
            **Protection de vos données**

            Ce démonstrateur sert à tester le fonctionnement de ClairExcel.
            N'importez pas de fichiers contenant des données sensibles,
            des coordonnées bancaires, des données personnelles confidentielles
            ou des informations commerciales stratégiques.

            Les fichiers et les résultats sont traités dans la session
            de l'application. N'utilisez pas ce démonstrateur public comme
            espace de stockage ou comme outil de traitement de données sensibles.
            """
        )

    uploaded_files = None
    uploader_key = (
        f"clair_excel_uploader_{st.session_state.get('uploader_version', 0)}"
    )

    sample_directory = (
        Path(__file__).parent / "data" / "samples"
    )

    sample_files = [
        sample_directory / "interventions_janvier.xlsx",
        sample_directory / "interventions_fevrier.xlsx",
    ]

    # --------------------------------------------------
    # MODE DÉMONSTRATION
    # --------------------------------------------------

    if demo_mode == "Découvrir ClairExcel":

        st.info(
            "Deux fichiers Excel d'exemple sont disponibles. "
            "Découvrez leur contenu avant de lancer le traitement."
        )

        if all(path.exists() for path in sample_files):

            st.success(
                "Les deux fichiers de démonstration sont disponibles."
            )

            st.subheader("Découvrir les fichiers de démonstration")

            st.write(
                "Voici les colonnes et un aperçu des cinq premières "
                "lignes de chaque fichier."
            )

            for sample_file in sample_files:

                with st.expander(
                    f"📄 {sample_file.name}",
                    expanded=False,
                ):

                    try:
                        apercu = pd.read_excel(
                            sample_file,
                            engine="openpyxl",
                        )

                        st.caption(
                            f"{len(apercu)} ligne(s) de données "
                            f"et {len(apercu.columns)} colonne(s)"
                        )

                        st.markdown("**Colonnes présentes :**")

                        st.write(
                            ", ".join(str(colonne) for colonne in apercu.columns)
                        )

                        st.markdown("**Aperçu des 5 premières lignes :**")

                        st.dataframe(
                            apercu.head(5),
                            use_container_width=True,
                        )

                    except Exception:
                        st.warning(
                            "Impossible d'afficher l'aperçu de ce fichier."
                        )

            st.info(
                "💡 Les fichiers contiennent volontairement des cas "
                "de test permettant de découvrir les contrôles de "
                "ClairExcel : doublons, dates et montants à vérifier."
            )

            files_available = True

        else:

            st.error(
                "Les fichiers de démonstration sont introuvables. "
                "Vérifiez le dossier data/samples."
            )

            files_available = False


    # --------------------------------------------------
    # MODE FICHIERS PERSONNELS
    # --------------------------------------------------

    else:

        st.write(
            "Sélectionnez les fichiers Excel que vous souhaitez traiter."
        )

        st.info(
            """
            **Avant d'importer vos fichiers**

            Pour que ClairExcel fonctionne correctement avec vos propres fichiers Excel, les intitulés de colonnes doivent correspondre aux formats actuellement reconnus :

            - **Client** : `Nom client`, `Nom du client` ou `Client`
            - **Date** : `Date intervention`, `Date de l'intervention` ou `Date`
            - **Montant HT** : `Montant HT`, `Prix` ou `Montant`
            - **Adresse** : `Adresse client`, `Adresse du client` ou `Adresse` (facultatif)

            Les intitulés peuvent varier d'un fichier à l'autre, à condition de correspondre à l'un des intitulés reconnus ci-dessus.

            Les fichiers doivent être au format `.xlsx`.

            Si vos fichiers utilisent d'autres intitulés, ils devront être adaptés avant leur importation.
            """
        )

        uploaded_files = st.file_uploader(
            "Sélectionnez vos fichiers Excel (.xlsx)",
            type=["xlsx"],
            accept_multiple_files=True,
            help=(
                f"{MAX_FILES} fichiers maximum, "
                f"{MAX_FILE_SIZE_MB} Mo maximum par fichier."
            ),
            max_upload_size=MAX_FILE_SIZE_MB,
            key=uploader_key,
        )

        files_available = False

        if uploaded_files:

            if len(uploaded_files) > MAX_FILES:

                st.error(
                    f"Vous avez sélectionné {len(uploaded_files)} fichiers. "
                    f"La limite est de {MAX_FILES} fichiers par traitement."
                )

            elif any(
                uploaded_file.size > MAX_FILE_SIZE_BYTES
                for uploaded_file in uploaded_files
            ):

                st.error(
                    f"Au moins un fichier dépasse la taille maximale "
                    f"autorisée de {MAX_FILE_SIZE_MB} Mo."
                )

            else:

                st.success(
                    f"{len(uploaded_files)} fichier(s) sélectionné(s)."
                )

                with st.expander("Voir les fichiers sélectionnés"):

                    for uploaded_file in uploaded_files:
                        taille_mo = uploaded_file.size / (1024 * 1024)

                        st.write(
                            f"📄 {uploaded_file.name} — {taille_mo:.2f} Mo"
                        )

                files_available = True

    # --------------------------------------------------
    # LANCEMENT DU TRAITEMENT
    # --------------------------------------------------

    if st.button(
        "🚀 Lancer la consolidation",
        type="primary",
        disabled=not files_available,
        use_container_width=True,
    ):

        progress_bar = st.progress(
            0,
            text="Préparation du traitement...",
        )

        step_message = st.empty()

        try:

            # --------------------------------------------------
            # ÉTAPE 1 : IMPORTATION
            # --------------------------------------------------

            step_message.info(
                "📂 Étape 1/5 — Importation des fichiers\n\n"
                "ClairExcel ouvre les fichiers Excel sélectionnés "
                "et récupère leurs données."
            )

            progress_bar.progress(
                10,
                text="Importation des fichiers Excel...",
            )

            files_to_process = []
            processed_file_names = []

            if demo_mode == "Découvrir ClairExcel":

                for sample_path in sample_files:

                    with open(sample_path, "rb") as sample_file:

                        dataframe = import_excel_file(sample_file)

                    files_to_process.append(
                        (sample_path.name, dataframe)
                    )

                    processed_file_names.append(sample_path.name)

            else:

                if not uploaded_files:
                    raise ValueError("Aucun fichier n'a été sélectionné.")

                if len(uploaded_files) > MAX_FILES:
                    raise ValueError(
                        f"La limite est de {MAX_FILES} fichiers par traitement."
                    )

                for uploaded_file in uploaded_files:

                    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
                        raise ValueError(
                            f"Le fichier {uploaded_file.name} dépasse "
                            f"{MAX_FILE_SIZE_MB} Mo."
                        )

                    uploaded_file.seek(0)

                    dataframe = import_excel_file(uploaded_file)

                    files_to_process.append(
                        (uploaded_file.name, dataframe)
                    )

                    processed_file_names.append(uploaded_file.name)

            if not files_to_process:

                raise ValueError(
                    "Aucun fichier Excel n'a été chargé."
                )

            progress_bar.progress(
                25,
                text="Importation terminée...",
            )

            # --------------------------------------------------
            # ÉTAPE 2 : NETTOYAGE ET CONSOLIDATION
            # --------------------------------------------------

            step_message.info(
                "🧹 Étape 2/5 — Nettoyage et consolidation\n\n"
                "ClairExcel harmonise les colonnes, nettoie les données "
                "et rassemble les fichiers dans un tableau unique."
            )

            progress_bar.progress(
                40,
                text="Nettoyage et consolidation des données...",
            )

            consolidated, duplicates, cleaning_anomalies = (
                consolidate_dataframes(files_to_process)
            )

            # Nombre de lignes examinées après nettoyage,
            # mais avant le retrait des doublons
            examined_rows = len(consolidated) + len(duplicates)

            consolidated = consolidated.reset_index(drop=True)

            progress_bar.progress(
                55,
                text="Consolidation terminée...",
            )

            # --------------------------------------------------
            # ÉTAPE 3 : VALIDATION DES DONNÉES
            # --------------------------------------------------

            step_message.info(
                "🔍 Étape 3/5 — Vérification des données\n\n"
                "ClairExcel contrôle les informations importantes : "
                "noms des clients, dates et montants."
            )

            progress_bar.progress(
                65,
                text="Vérification de la qualité des données...",
            )

            validation_anomalies = validate_dataframe(consolidated)

            # Ajout du fichier source aux anomalies de validation
            if (
                "index_ligne" in validation_anomalies.columns
                and "source_file" in consolidated.columns
            ):

                source_by_index = consolidated["source_file"].to_dict()

                validation_anomalies["source_file"] = (
                    validation_anomalies["index_ligne"].map(source_by_index)
                )

            # --------------------------------------------------
            # ÉTAPE 4 : REGROUPEMENT DES ANOMALIES
            # --------------------------------------------------

            step_message.info(
                "⚠️ Étape 4/5 — Analyse des anomalies\n\n"
                "Les doublons, les erreurs et les avertissements "
                "sont regroupés pour faciliter leur consultation."
            )

            all_anomalies = pd.concat(
                [
                    cleaning_anomalies,
                    validation_anomalies,
                ],
                ignore_index=True,
                sort=False,
            )

            if "niveau" in all_anomalies.columns:

                all_anomalies["niveau"] = (
                    all_anomalies["niveau"].fillna("nettoyage")
                )

            progress_bar.progress(
                75,
                text="Analyse des anomalies terminée...",
            )

            # --------------------------------------------------
            # ÉTAPE 5 : GÉNÉRATION DU RAPPORT EXCEL
            # --------------------------------------------------

            step_message.info(
                "📊 Étape 5/5 — Création du rapport Excel\n\n"
                "ClairExcel prépare votre classeur avec les données "
                "consolidées, les doublons, les anomalies "
                "et les statistiques."
            )

            progress_bar.progress(
                85,
                text="Génération du fichier Excel...",
            )

            excel_file = export_consolidation_to_excel(
                consolidated,
                duplicates,
                all_anomalies,
            )

            # --------------------------------------------------
            # SAUVEGARDE DES RÉSULTATS
            # --------------------------------------------------

            st.session_state["consolidated"] = consolidated
            st.session_state["duplicates"] = duplicates
            st.session_state["anomalies"] = all_anomalies
            st.session_state["excel_bytes"] = excel_file.getvalue()
            st.session_state["processed_files"] = processed_file_names
            st.session_state["examined_rows"] = examined_rows

            progress_bar.progress(
                100,
                text="Traitement terminé !",
            )

            step_message.success(
                "✅ Votre démonstration est terminée ! "
                "Vous pouvez maintenant consulter les résultats ci-dessous."
            )

            st.success(
                "La consolidation est terminée avec succès."
            )

        except Exception as error:

            progress_bar.empty()

            step_message.error(
                "Le traitement n'a pas pu être terminé."
            )

            st.error(
                "Le traitement n'a pas pu aboutir. "
                "Vérifiez que vos fichiers sont des classeurs Excel .xlsx "
                "valides et réessayez. Si le problème persiste, "
                "contactez l'administrateur de ClairExcel."
            )

    # --------------------------------------------------
    # EFFACEMENT DES RÉSULTATS
    # --------------------------------------------------

    result_keys = [
        "consolidated",
        "duplicates",
        "anomalies",
        "excel_bytes",
        "processed_files",
        "examined_rows",
    ]

    if "consolidated" in st.session_state:

        if st.button(
            "🗑️ Effacer les résultats précédents",
            help="Supprime les résultats affichés dans cette session.",
        ):

            for key in result_keys:
                st.session_state.pop(key, None)

            # Change la clé du composant pour réinitialiser aussi
            # la sélection des fichiers importés.
            st.session_state["uploader_version"] = (
                st.session_state.get("uploader_version", 0) + 1
            )

            st.rerun()

    # --------------------------------------------------
    # AFFICHAGE DU TABLEAU DE BORD
    # --------------------------------------------------

    if "consolidated" in st.session_state:

        consolidated = st.session_state["consolidated"]
        duplicates = st.session_state["duplicates"]
        anomalies = st.session_state["anomalies"]

        st.divider()

        st.subheader("2. Tableau de bord")

        # --------------------------------------------------
        # EXPLICATION DES ÉTAPES
        # --------------------------------------------------

        with st.expander(
            "💡 Comprendre les 5 étapes réalisées par ClairExcel"
        ):

            st.markdown(
                """
                **1. Importation des fichiers**

                Les données de vos différents fichiers Excel ont été récupérées.

                **2. Nettoyage et consolidation**

                Les colonnes ont été harmonisées et les données regroupées
                dans un tableau unique.

                **3. Vérification des données**

                Les informations importantes ont été contrôlées :
                noms des clients, dates et montants.

                **4. Détection des problèmes**

                Les doublons, les erreurs et les avertissements ont été identifiés.

                **5. Génération du rapport**

                Un classeur Excel a été créé avec les résultats et les statistiques.
                """
            )

        # --------------------------------------------------
        # CALCUL DES INDICATEURS
        # --------------------------------------------------

        error_count = 0
        warning_count = 0
        cleaning_count = 0

        if "niveau" in anomalies.columns:

            error_count = int(
                (anomalies["niveau"] == "erreur").sum()
            )

            warning_count = int(
                (anomalies["niveau"] == "avertissement").sum()
            )

            cleaning_count = int(
                (anomalies["niveau"] == "nettoyage").sum()
            )

        # --------------------------------------------------
        # INDICATEURS PRINCIPAUX
        # --------------------------------------------------

        st.markdown("#### Résumé du traitement")

        metric1, metric2, metric3, metric4 = st.columns(4)

        metric1.metric(
            "Lignes conservées",
            len(consolidated),
            help="Nombre de lignes présentes dans le tableau consolidé.",
        )

        metric2.metric(
            "Doublons détectés",
            len(duplicates),
            help="Lignes écartées du tableau consolidé car elles étaient en double.",
        )

        metric3.metric(
            "Erreurs",
            error_count,
            help="Données qui nécessitent une correction ou une vérification.",
        )

        metric4.metric(
            "Avertissements",
            warning_count,
            help="Valeurs inhabituelles qui méritent votre attention.",
        )

        # --------------------------------------------------
        # INDICATEURS DE NETTOYAGE
        # --------------------------------------------------

        metric5, metric6 = st.columns(2)

        metric5.metric(
            "Anomalies de nettoyage",
            cleaning_count,
            help="Éléments repérés pendant le nettoyage, comme les lignes entièrement vides.",
        )

        metric6.metric(
            "Fichiers traités",
            len(st.session_state["processed_files"]),
        )

        st.caption(
            "Les anomalies de nettoyage sont présentées séparément "
            "des erreurs et des avertissements de validation."
        )


        # --------------------------------------------------
        # COMPARAISON AVANT / APRÈS
        # --------------------------------------------------

        st.divider()

        st.subheader("Avant / après : le résultat de ClairExcel")

        examined_rows = st.session_state.get(
            "examined_rows",
            len(consolidated) + len(duplicates),
        )

        retained_rows = len(consolidated)
        removed_duplicates = len(duplicates)

        duplicate_percentage = (
            removed_duplicates / examined_rows * 100
            if examined_rows > 0
            else 0
        )

        st.write(
            "Visualisez l'effet du traitement sur vos fichiers Excel."
        )

        before_col, after_col, duplicate_col = st.columns(3)

        with before_col:

            st.markdown("#### 📥 Avant dédoublonnage")

            st.metric(
                "Lignes examinées",
                examined_rows,
            )

            st.caption(
                "Après le nettoyage des lignes entièrement vides."
            )

        with after_col:

            st.markdown("#### 📊 Après dédoublonnage")

            st.metric(
                "Lignes conservées",
                retained_rows,
            )

            st.caption(
                "Données uniques regroupées dans le tableau final."
            )

        with duplicate_col:

            st.markdown("#### 🔁 Doublons écartés")

            st.metric(
                "Doublons détectés",
                removed_duplicates,
            )

            st.caption(
                f"{duplicate_percentage:.1f} % des lignes examinées."
            )

        st.success(
            f"ClairExcel a regroupé {examined_rows} lignes examinées "
            f"en {retained_rows} lignes uniques et identifié "
            f"{removed_duplicates} doublon(s)."
        )

        # --------------------------------------------------
        # ONGLETS DE CONSULTATION
        # --------------------------------------------------

        st.divider()

        tab_data, tab_duplicates, tab_anomalies = st.tabs(
            [
                "📋 Données consolidées",
                "🔁 Doublons",
                "⚠️ Anomalies",
            ]
        )

        # --------------------------------------------------
        # DONNÉES CONSOLIDÉES
        # --------------------------------------------------

        with tab_data:

            st.subheader("Données consolidées")

            st.write(
                "Voici les données conservées après nettoyage "
                "et traitement des doublons."
            )

            st.info(
                "Les lignes présentes dans ce tableau sont celles "
                "qui ont été conservées dans le résultat final. "
                "Les doublons sont consultables dans l'onglet dédié."
            )

            st.dataframe(
                consolidated,
                use_container_width=True,
                hide_index=True,
            )

        # --------------------------------------------------
        # DOUBLONS
        # --------------------------------------------------

        with tab_duplicates:

            st.subheader("Doublons détectés")

            if duplicates.empty:

                st.success(
                    "Aucun doublon détecté. "
                    "Toutes les lignes examinées sont uniques."
                )

            else:

                st.warning(
                    f"{len(duplicates)} doublon(s) détecté(s)."
                )

                st.markdown(
                    """
                    **Pourquoi ces lignes apparaissent-elles ici ?**

                    ClairExcel repère les enregistrements qui possèdent
                    les mêmes informations de client, de date et de montant.

                    Lorsqu'un doublon est identifié, une seule occurrence
                    est conservée dans les données consolidées.
                    Les occurrences supplémentaires sont affichées ici
                    afin que vous puissiez les contrôler.
                    """
                )

                st.dataframe(
                    prepare_duplicate_view(duplicates),
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    "Important : les doublons ne sont pas perdus. "
                    "Ils restent disponibles dans ce rapport pour vérification."
                )

        # --------------------------------------------------
        # ANOMALIES
        # --------------------------------------------------

        with tab_anomalies:

            st.subheader("Comprendre les anomalies")

            st.write(
                "ClairExcel classe les problèmes détectés en trois catégories."
            )

            # Présentation pédagogique des catégories

            explanation_col1, explanation_col2, explanation_col3 = (
                st.columns(3)
            )

            with explanation_col1:

                st.markdown("🔴 **Erreurs**")

                st.write(
                    "Informations qui nécessitent une correction "
                    "ou une vérification, par exemple une date invalide "
                    "ou un montant non numérique."
                )

            with explanation_col2:

                st.markdown("🟠 **Avertissements**")

                st.write(
                    "Valeurs inhabituelles qui méritent votre attention, "
                    "comme un montant négatif."
                )

            with explanation_col3:

                st.markdown("🧹 **Nettoyage**")

                st.write(
                    "Éléments repérés pendant le nettoyage, "
                    "comme les lignes entièrement vides."
                )

            st.divider()

            if anomalies.empty:

                st.success(
                    "Aucune anomalie détectée. "
                    "Les contrôles réalisés n'ont révélé aucun problème."
                )

            else:

                if "niveau" in anomalies.columns:

                    error_tab, warning_tab, cleaning_tab = st.tabs(
                        [
                            f"🔴 Erreurs ({error_count})",
                            f"🟠 Avertissements ({warning_count})",
                            f"🧹 Nettoyage ({cleaning_count})",
                        ]
                    )

                    # ------------------------------------------
                    # ERREURS
                    # ------------------------------------------

                    with error_tab:

                        errors = anomalies[
                            anomalies["niveau"] == "erreur"
                        ]

                        if errors.empty:

                            st.success("Aucune erreur détectée.")

                        else:

                            st.error(
                                f"{len(errors)} erreur(s) à examiner."
                            )

                            st.write(
                                "Ces données présentent un problème "
                                "qui peut empêcher leur exploitation correcte."
                            )

                            st.dataframe(
                                prepare_anomaly_view(errors),
                                use_container_width=True,
                                hide_index=True,
                            )

                            st.info(
                                "Conseil : vérifiez les valeurs indiquées "
                                "dans le tableau, corrigez-les dans votre "
                                "fichier source, puis relancez le traitement."
                            )

                    # ------------------------------------------
                    # AVERTISSEMENTS
                    # ------------------------------------------

                    with warning_tab:

                        warnings = anomalies[
                            anomalies["niveau"] == "avertissement"
                        ]

                        if warnings.empty:

                            st.success(
                                "Aucun avertissement détecté."
                            )

                        else:

                            st.warning(
                                f"{len(warnings)} avertissement(s) à vérifier."
                            )

                            st.write(
                                "Ces valeurs ne sont pas nécessairement "
                                "incorrectes, mais elles méritent votre attention."
                            )

                            st.dataframe(
                                prepare_anomaly_view(warnings),
                                use_container_width=True,
                                hide_index=True,
                            )

                            st.info(
                                "Conseil : vérifiez que les valeurs signalées "
                                "correspondent bien à votre activité."
                            )

                    # ------------------------------------------
                    # NETTOYAGE
                    # ------------------------------------------

                    with cleaning_tab:

                        cleaning = anomalies[
                            anomalies["niveau"] == "nettoyage"
                        ]

                        if cleaning.empty:

                            st.success(
                                "Aucune anomalie de nettoyage enregistrée."
                            )

                        else:

                            st.info(
                                f"{len(cleaning)} élément(s) repéré(s) "
                                "pendant le nettoyage."
                            )

                            st.write(
                                "Ces éléments correspondent aux opérations "
                                "de nettoyage réalisées avant la consolidation."
                            )

                            st.dataframe(
                                prepare_anomaly_view(cleaning),
                                use_container_width=True,
                                hide_index=True,
                            )

                else:

                    st.dataframe(
                        prepare_anomaly_view(anomalies),
                        use_container_width=True,
                        hide_index=True,
                    )

            st.divider()

            st.caption(
                "ClairExcel identifie les problèmes, mais ne corrige pas "
                "automatiquement les valeurs signalées. "
                "Vous gardez le contrôle des modifications à effectuer."
            )

        # --------------------------------------------------
        # TÉLÉCHARGEMENTS
        # --------------------------------------------------

        st.divider()

        st.subheader("3. Télécharger les résultats")

        st.write(
            "Récupérez votre classeur complet ou téléchargez "
            "uniquement le rapport des anomalies."
        )

        download_col1, download_col2 = st.columns(2)

        with download_col1:

            st.download_button(
                label="📥 Télécharger le classeur Excel complet",
                data=st.session_state["excel_bytes"],
                file_name="resultat_consolidation.xlsx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
                use_container_width=True,
                type="primary",
            )

        with download_col2:

            anomaly_csv = anomalies.to_csv(
                index=False,
                sep=";",
                encoding="utf-8-sig",
            )

            st.download_button(
                label="📄 Télécharger le rapport des anomalies",
                data=anomaly_csv,
                file_name="rapport_anomalies.csv",
                mime="text/csv",
                use_container_width=True,
            )

    else:

        st.info(
            "Commencez par sélectionner vos fichiers Excel, "
            "puis lancez la consolidation pour afficher les résultats."
        )


# ==================================================
# ONGLET 2 : PRÉSENTATION DE CLAIREXCEL
# ==================================================

with tab_presentation:

    st.title("Découvrez ClairExcel")

    st.subheader(
        "Vos fichiers Excel réunis, vos données vérifiées, "
        "votre temps préservé."
    )

    st.markdown(
        """
        ### Pourquoi utiliser ClairExcel ?

        Vous recevez régulièrement plusieurs fichiers Excel
        contenant des informations similaires ?

        Vous perdez du temps à les ouvrir, les comparer,
        faire des copier-coller et vérifier les données ?

        **ClairExcel automatise ces opérations pour vous.**

        ---

        ### Les fonctionnalités

        #### 📂 Regroupement automatique
        Rassemble plusieurs fichiers Excel dans un tableau unique.

        #### 🔄 Harmonisation des colonnes
        Reconnaît différentes appellations pour une même information.

        #### 🧹 Nettoyage des données
        Repère les lignes vides et les informations manquantes.

        #### 🔁 Détection des doublons
        Identifie les enregistrements présents plusieurs fois.

        #### ⚠️ Contrôle des anomalies
        Signale notamment les dates invalides, les montants
        non numériques et les montants négatifs.

        #### 📊 Rapport Excel
        Génère un classeur structuré avec les données consolidées,
        les doublons, les anomalies et les statistiques.

        ---

        ### À qui s'adresse ClairExcel ?

        ClairExcel peut répondre aux besoins :

        - Des artisans et petites entreprises.
        - Des associations.
        - Des TPE.
        - Des organismes de formation.

        ---

        ### Un exemple concret

        Vous disposez de deux fichiers Excel contenant
        des interventions clients.

        ClairExcel :

        1. Importe les deux fichiers.
        2. Regroupe leurs données.
        3. Identifie les doublons.
        4. Signale les informations à vérifier.
        5. Produit un rapport Excel exploitable.

        **Résultat de notre démonstration :**

        - 10 lignes uniques.
        - 1 doublon détecté.
        - 3 anomalies signalées.
        - 2 fichiers sources traités.

        ---

        ### Une solution adaptée à votre organisation

        Chaque activité possède ses propres fichiers et habitudes
        de travail.

        Je peux étudier votre fonctionnement et adapter
        l'automatisation à vos besoins : formats Excel,
        colonnes, règles de contrôle et présentation des résultats.

        ---

        ### Envie de gagner du temps ?

        Je vous propose une démonstration de ClairExcel
        à partir d'un exemple concret de votre activité.

        **ClairExcel — L'automatisation Excel au service de votre activité.**
        """
    )

    st.info(
        "Pour découvrir le fonctionnement de l'outil, "
        "rendez-vous dans l'onglet « Traitement des fichiers »."
    )


    # --------------------------------------------------
    # CONTACT - COORDONNÉES DE DÉMONSTRATION
    # --------------------------------------------------

    st.divider()

    st.subheader("Une question ? Parlons de votre projet")

    st.markdown(
        """
        Vous souhaitez savoir comment ClairExcel pourrait
        s'adapter à votre activité ?

        Contactez-nous pour poser vos questions ou demander
        une démonstration personnalisée.
        """
    )

    col_contact, col_action = st.columns([2, 1])

    with col_contact:
        st.markdown("**E-mail de démonstration**")
        st.markdown(
            "[contact@clairexcel.fr](mailto:contact@clairexcel.fr)"
        )

    with col_action:
        st.link_button(
            "Nous contacter",
            "mailto:contact@clairexcel.fr?subject=Demande%20de%20renseignements%20-%20ClairExcel",
            use_container_width=True,
        )

    st.caption(
        "Adresse fictive utilisée uniquement pour cette démonstration. "
        "Elle devra être remplacée par une adresse réelle avant publication."
    )



# --------------------------------------------------
# PIED DE PAGE
# --------------------------------------------------

st.divider()

st.caption(
    "ClairExcel — Démonstrateur de traitement "
    "et de contrôle de données Excel."
)
