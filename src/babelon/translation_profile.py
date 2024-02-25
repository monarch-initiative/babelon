"""Translation Profile."""

import logging
from pathlib import Path

import pandas as pd
from tabulate import tabulate

logging.basicConfig(format="%(message)s", level=logging.DEBUG)


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
