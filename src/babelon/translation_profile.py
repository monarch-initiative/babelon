"""Translation Profile."""

from pathlib import Path

import pandas as pd
from oaklib import BasicOntologyInterface, get_adapter


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
