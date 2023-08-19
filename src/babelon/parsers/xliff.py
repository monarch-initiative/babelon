"""xliff.py."""
import csv
import os
from os.path import exists

import pandas as pd
import xmltodict


class XliffParser:
    """parser = XliffParser(/tests/data/)."""

    def __init__(self, input_file_path, output_file_path):
        self.input_file = input_file_path
        self.output_file = output_file_path

    def xml_to_tsv(self):
        """xlm_to_tsv.

        Raises:
            FileNotFoundError: FileNotFoundError

        Returns:
            [type]: [description]
        """
        if exists(self.input_file):
            with open(self.input_file) as fd:
                doc = xmltodict.parse(fd.read())
        else:
            raise FileNotFoundError(f"Input file:{self.input_file} not found.")

        csvfile = open(self.output_file, "w", encoding="utf-8")
        csvfile_writer = csv.writer(csvfile, delimiter="\t")

        csvfile_synonyms = open(
            str(self.output_file).replace(".babelon.", ".synonyms."), "w", encoding="utf-8"
        )
        csvfile_writer_synonyms = csv.writer(csvfile_synonyms, delimiter="\t")

        # ADD HEADER
        csvfile_writer.writerow(
            [
                "source_language",
                "translation_language",
                "subject_id",
                "predicate_id",
                "source_value",
                "translation_value",
                "translation_status",
            ]
        )
        csvfile_writer_synonyms.writerow(["subject_id", "translation_value", "comment"])

        lang = "unknown"

        if doc["xliff"]["file"]["body"]["trans-unit"]:
            lang = doc["xliff"]["file"]["body"]["trans-unit"][0]["target"]["@xml:lang"]

        csvfile_writer_synonyms.writerow(["ID", f"AL oboInOwl:hasExactSynonym@{lang}", ""])

        for trans_unit in doc["xliff"]["file"]["body"]["trans-unit"]:
            source_language = trans_unit["source"]["@xml:lang"]
            translation_language = trans_unit["target"]["@xml:lang"]
            translation_status = self.get_translation_status(trans_unit["target"]["@state"])
            # get subject_id and and format
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

            csv_line = []

            if predicate_id == "oboInOwl:exactSynonym":
                all_synonyms = self.synonym_split_value(translational_value)
                subject_id = self._remove_redundant_whitespace(subject_id)
                translation_status = self._remove_redundant_whitespace(translation_status)

                for syn in all_synonyms:
                    csv_line = [subject_id, syn, translation_status]
                    csvfile_writer_synonyms.writerow(csv_line)
            else:
                for line in [
                    source_language,
                    translation_language,
                    subject_id,
                    predicate_id,
                    source_value,
                    translational_value,
                    translation_status,
                ]:
                    csv_line.append(self._remove_redundant_whitespace(line))
                csvfile_writer.writerow(csv_line)

        return self.output_file

    def _remove_redundant_whitespace(self, v: str):
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

    def get_translation_status(self, translation_status_raw):
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

    def synonym_split_value(self, raw_synonym):
        """synonym_split_value."""
        word_list = raw_synonym.split("#")
        stripped = [self._remove_redundant_whitespace(s) for s in word_list if s]
        return stripped

    def synonym_split(self):
        """synonym_split."""
        df = pd.read_csv(self.output_file, sep="\t")

        output_df = df[0:0]

        for _, row in df.iterrows():
            if row.predicate_id == "oboInOwl:exactSynonym":
                word_list = row["source_value"].split("#")
                word_list.remove("")
                temp_row = row.copy()
                if len(word_list) > 1:
                    for each_word in word_list:
                        temp_row.source_value = each_word
                        temp_row.translation_value = each_word
                        output_df = pd.concat(
                            [output_df, pd.DataFrame([temp_row.to_dict()])], ignore_index=True
                        )

                else:
                    temp_row.source_value = word_list[0]
                    temp_row.translation_value = temp_row.translation_value.replace("#", "")
                    output_df = pd.concat(
                        [output_df, pd.DataFrame([temp_row.to_dict()])], ignore_index=True
                    )

            else:
                output_df = pd.concat([output_df, pd.DataFrame([row.to_dict()])], ignore_index=True)
        output_df.to_csv(self.output_file, sep="\t", index=False)
        return self.output_file
