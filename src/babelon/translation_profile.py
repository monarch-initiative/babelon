"""Translation Profile."""

import logging
from pathlib import Path

import pandas as pd
from oaklib import BasicOntologyInterface, get_adapter
from tabulate import tabulate

logging.basicConfig(format="%(message)s", level=logging.DEBUG)


def update_translation_profile(
    translation_profile: Path, ontology_file: Path, output_file: Path
) -> None:
    """Write update_translation_profile to TSV file.

    Args:
        translation_profile (Path): Path to the translation profile
        ontology_file (Path): Path to the ontology file
        output_file (Path): Path to the output TSV file
    """
    updated_profile = update_translation_status(translation_profile, ontology_file)
    updated_profile.to_csv(output_file, sep="\t", index=False)


def table_print(title: str, data: pd.DataFrame):
    """Print grouped translation data.

    Args:
        title (str): Table title
        data (pd.DataFrame): Translation groupped data
    """
    logging.info("--------------------------------------------------------------------------------")
    logging.info(title)
    logging.info("--------------------------------------------------------------------------------")
    logging.info(
        tabulate(
            data.reset_index().rename(columns={"level_0": "", "level_1": ""}),
            tablefmt="fancy_grid",
            headers="keys",
            showindex=False,
        )
    )


def statistics_translation_profile(translation_profile: Path) -> None:
    """Take as an input a babelon profile (TSV) and returns some basic stats.

        number of translations by source_language, target_language
        number of translations by source_language, target_language, predicate_id
        number of translations by source_language, target_language, translation_status
    Args:
        translation_profile (Path): translation profile
    """
    profile = pd.read_csv(translation_profile, sep="\t")
    # source_language	translation_language	subject_id	predicate_id	source_value	translation_value	translation_status
    source_target = (
        profile.groupby(["source_language", "translation_language"]).size().to_frame("count")
    )
    source_target_pred = (
        profile.groupby(["source_language", "translation_language", "predicate_id"])
        .size()
        .to_frame("count")
    )
    source_target_status = (
        profile.groupby(["source_language", "translation_language", "translation_status"])
        .size()
        .to_frame("count")
    )

    table_print("Number of translations by: Source Language; Target Language", source_target)
    table_print(
        "Number of translations by: Source Language; Target Language; Predicate ID",
        source_target_pred,
    )
    table_print(
        "Number of translations by: Source Language; Target Language; Translation Status",
        source_target_status,
    )


def update_translation_status(translation_profile: Path, ontology_file: Path) -> pd.DataFrame:
    """Update all translation_status in translation_profile.

    From "OFFICIAL"  to "CANDIDATE"  if the original ontology label has changed.


    Args:
        translation_profile (Path): Path to the translation profile
        ontology_file (Path): Path to the ontology file

    Returns:
        pd.DataFrame: updated translation status
    """
    profile = pd.read_csv(translation_profile, sep="\t")
    adapter = get_adapter(f"pronto:{ontology_file}")
    profile["translation_status"] = profile.apply(
        lambda row: _translate_profile_iterator(row, adapter), axis=1
    )

    rows = []
    for ent in set(adapter.entities()).difference(set(profile["subject_id"])):
        if ":" in ent:
            new_row = pd.DataFrame(
                {
                    "subject_id": ent,
                    "source_language": "en",
                    "translation_language": profile["translation_language"][0],
                    "predicate_id": "rdfs:label",
                    "source_value": adapter.label(ent),
                    "translation_status": "CANDIDATE",
                    "translation_value": None,
                },
                index=[ent],
            )
            rows.append(new_row)
    new_rows = pd.concat(rows)
    return pd.concat([profile, new_rows])


def _translate_profile_iterator(row: pd.Series, adapter: BasicOntologyInterface) -> str:
    """
    Iterate through profile rows and returns OFFICIAL if the profile label is equal to the ontology label.

    Returns CANDIDATE if it's different than OFFICIAL.

    Args:
        row (pd.Series): translation profile row
        adapter (BasicOntologyInterface): ontology

    Returns:
        str: new translation status label
    """
    profile_label = row["source_value"]
    onto_label = adapter.label(row["subject_id"])
    return "OFFICIAL" if profile_label == onto_label else "CANDIDATE"
