"""Constants for test cases."""

import pathlib

import pandas as pd

cwd = pathlib.Path(__file__).parent.resolve()
data_dir = cwd / "data"

test_out_dir = cwd / "tmp"
test_out_dir.mkdir(parents=True, exist_ok=True)


def _create_simple_example_for_testing():
    data = [
        {
            "source_language": "en",
            "source_value": "Fever",
            "subject_id": "HP:0001945",
            "predicate_id": "rdfs:label",
            "translation_language": "de",
            "translation_value": "Fieber",
            "translation_status": "NOT_TRANSLATED",
        },
        {
            "source_language": "en",
            "source_value": "Sudden impairment of blood flow to a part of the "
            "brain due to occlusion or rupture of an artery to the brain.",
            "subject_id": "HP:0001297",
            "predicate_id": "IAO:0000115",
            "translation_language": "de",
            "translation_value": "",
            "translation_status": "NOT_TRANSLATED",
        },
    ]
    return pd.DataFrame(data)


def _create_empty_example_for_testing():
    df = _create_simple_example_for_testing()
    return df.iloc[0:0]
