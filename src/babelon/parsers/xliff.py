"""xliff.py."""

from os.path import exists
from typing import Dict, Tuple

import pandas as pd
import xmltodict


def _get_translation_status(translation_status_raw):
    """get_translation_status."""
    if translation_status_raw:
        if translation_status_raw == "needs-translation":
            return "NOT_TRANSLATED"
        elif translation_status_raw == "final":
            return "OFFICIAL"
        elif translation_status_raw == "translated":
            return "CANDIDATE"
        else:
            return translation_status_raw
    return ""


def _synonym_split_value(raw_synonym):
    """synonym_split_value."""
    word_list = raw_synonym.split("#")
    stripped = [_remove_redundant_whitespace(s) for s in word_list if s]
    return stripped


def _remove_redundant_whitespace(v: str):
    if not v:
        return ""
    return (
        v.replace("\n", " ")
        .replace("\t", " ")
        .replace("\r", "")
        .replace("  ", " ")
        .replace("  ", " ")
        .strip()
    )


def xliff_path_to_babelon(input_file_path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate a babelon dataframe for translations and a ROBOT template for synonyms from XLIFF file."""
    doc = _load_xliff_as_xmldoc(input_file_path)
    return xliff_to_babelon(doc)


def xliff_to_babelon(doc: Dict) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Translate the loaded XLIFF document to Babelon TSV in pandas.

    Returns:
       Tuple (pd.DataFrame, pd.DataFrame) : a babelon and a synonym dataframe
    """
    babelon_data = []
    synonym_data = []

    if doc["xliff"]["file"]["body"]["trans-unit"]:
        lang = doc["xliff"]["file"]["body"]["trans-unit"][0]["target"]["@xml:lang"]
    else:
        lang = "unknown"

    synonym_data.append(
        {
            "subject_id": "ID",
            "translation_value": f"AL oboInOwl:hasExactSynonym@{lang}",
            "comment": "",
        }
    )

    for trans_unit in doc["xliff"]["file"]["body"]["trans-unit"]:
        source_language = trans_unit["source"]["@xml:lang"]
        translation_language = trans_unit["target"]["@xml:lang"]
        translation_status = _get_translation_status(trans_unit["target"]["@state"])
        # get subject_id and format
        split_string_id_column = trans_unit["@id"]
        get_subject_id = split_string_id_column[0:10]
        subject_id = get_subject_id.replace("_", ":")
        # get predicate_id and format
        get_predicate_id = split_string_id_column[11:21]
        if get_predicate_id == "label":
            predicate_id = get_predicate_id.replace("label", "rdfs:label")
        elif get_predicate_id == "definition":
            predicate_id = get_predicate_id.replace("definition", "IAO:0000115")
        else:
            # elif get_predicate_id == 'synonyms':
            predicate_id = get_predicate_id.replace("synonyms", "oboInOwl:exactSynonym")
        source_value = trans_unit["source"]["#text"]
        translational_value = trans_unit["target"]["#text"]

        if predicate_id == "oboInOwl:exactSynonym":
            all_synonyms = _synonym_split_value(translational_value)
            subject_id = _remove_redundant_whitespace(subject_id)
            translation_status = _remove_redundant_whitespace(translation_status)

            for syn in all_synonyms:
                synonym_data.append(
                    {
                        "subject_id": subject_id,
                        "translation_value": syn,
                        "comment": translation_status,
                    }
                )
        else:
            babelon_data.append(
                {
                    "source_language": _remove_redundant_whitespace(source_language),
                    "translation_language": _remove_redundant_whitespace(translation_language),
                    "subject_id": _remove_redundant_whitespace(subject_id),
                    "predicate_id": _remove_redundant_whitespace(predicate_id),
                    "source_value": _remove_redundant_whitespace(source_value),
                    "translational_value": _remove_redundant_whitespace(translational_value),
                    "translation_status": _remove_redundant_whitespace(translation_status),
                }
            )

    df_synonyms = pd.DataFrame(synonym_data)
    df_babelon = pd.DataFrame(babelon_data)

    return df_babelon, df_synonyms


def _load_xliff_as_xmldoc(input_file_path):
    if exists(input_file_path):
        with open(input_file_path) as fd:
            doc = xmltodict.parse(fd.read())
    else:
        raise FileNotFoundError(f"Input file:{input_file_path} not found.")
    return doc


#
# # TODO this method seems not necessary
# def synonym_split(df_synonym: pd.DataFrame):
#     """synonym_split."""
#
#     output_df = df_synonym[0:0]
#
#     for _, row in df_synonym.iterrows():
#         if row.predicate_id == "oboInOwl:exactSynonym":
#             word_list = row["source_value"].split("#")
#             word_list.remove("")
#             temp_row = row.copy()
#             if len(word_list) > 1:
#                 for each_word in word_list:
#                     temp_row.source_value = each_word
#                     temp_row.translation_value = each_word
#                     output_df = pd.concat(
#                         [output_df, pd.DataFrame([temp_row.to_dict()])], ignore_index=True
#                     )
#
#             else:
#                 temp_row.source_value = word_list[0]
#                 temp_row.translation_value = temp_row.translation_value.replace("#", "")
#                 output_df = pd.concat(
#                     [output_df, pd.DataFrame([temp_row.to_dict()])], ignore_index=True
#                 )
#
#         else:
#             output_df = pd.concat([output_df, pd.DataFrame([row.to_dict()])], ignore_index=True)
#     return output_df
