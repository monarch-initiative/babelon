"""Translate Babelon profiles."""

import logging
import os
import re
import string
from typing import Dict, List

import llm
import pandas as pd


class Translator:
    """A generic translator class."""

    def model_name(self):
        """Return the unique name of the model.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass
        """
        raise NotImplementedError("This method should be implemented by subclasses.")

    def translate(self, text, target_language):
        """
        Translate the provided text into the target language.

        Args:
            text (str): The text to be translated.
            target_language (str): The language to translate the text into.

        Raises:
            NotImplementedError: If the method is not implemented in the subclass.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")


class OpenAITranslator(Translator):
    """A specific translator class that uses GPT-4 for translation."""

    def __init__(self, model="gpt-4-turbo-preview"):
        """Instantiate GPT4 translator."""
        self.model = llm.get_model(model)
        self.model.key = os.environ["OPENAI_API_KEY"]

    def model_name(self):
        """Return the unique name of the model."""
        return self.model.model_id

    def translate(self, text_to_translate, language_code):
        """
        Translate text using OpenAI's GPT-4 API (hypothetical).

        Args:
        text_to_translate (str): The text to be translated.
        language_code (str): The target language code (e.g., 'de' for German).

        Returns:
        str: The translated text.
        """
        # Set up your OpenAI API key

        prompt = f"""Translate the following text into the specified language.
The language code provided is in ISO format.

- Language Code (ISO format): {language_code}
- Text to Translate: {text_to_translate}

Please provide the translation.
If no translation can be found for whatever reason, including that the translation
language is the same as the language of the text to translate, return an empty string.
Give no comments, no explanations. Just the translation or an empty string."""

        logging.getLogger().setLevel(logging.CRITICAL)

        try:
            response = self.model.prompt(prompt)
            translated_value = response.text()
            return translated_value
        except Exception as e:
            logging.getLogger().warning(f"An error occurred: {e}")
            return ""


def _get_translation_language(translation_language_df, default_language="en"):
    if translation_language_df:
        return translation_language_df
    else:
        return default_language


def _is_legal_string(value):
    if isinstance(value, str):
        return value != "" and value.lower() != "nan"
    return False


def get_translator_model(model="gpt-4"):
    """
    Instantiate translator model based on string.

    Args:
        model (str): The model to be instatiated.

    Raises:
        ValueError: If the model does not exist.
    """
    if model == "gpt-4":
        return OpenAITranslator("gpt-4-turbo-preview")
    elif model == "gpt-3.5":
        return OpenAITranslator("gpt-3.5-turbo")
    else:
        try:
            translator = OpenAITranslator(model)
            return translator
        except Exception:
            raise ValueError(f"{model} is not a valid translation model!")


def translate_profile(
    babelon_df: pd.DataFrame, language_code="en", update_existing=False, model="gpt-4"
):
    """Iterate through DataFrame rows and translate values."""
    from datetime import datetime

    translator = get_translator_model(model)

    # Get today's date
    today = datetime.now()

    # Format the date as YYYY-MM-DD
    formatted_date = today.strftime("%Y-%m-%d")
    translated_df = babelon_df.copy()
    translated_df = translated_df.astype(str)
    for index, row in translated_df.iterrows():
        translation_language = _get_translation_language(row["translation_language"], language_code)
        source_value = row["source_value"]
        if source_value:
            existing_translation_value = (
                row["translation_value"] if "translation_value" in row else None
            )
            if update_existing or not _is_legal_string(existing_translation_value):
                translated_value = translator.translate(source_value, translation_language)
                translated_df.at[index, "translation_value"] = translated_value
                translated_df.at[index, "translator"] = "wikidata:Q116709136"
                translated_df.at[index, "translator_expertise"] = "ALGORITHM"
                translated_df.at[index, "comment"] = translator.model_name()
                translated_df.at[index, "translation_date"] = formatted_date
                translated_df.at[index, "translation_status"] = "CANDIDATE"
            else:
                logging.warning(f"Existing translation {existing_translation_value}, skipping..")
        else:
            logging.warning(f"No source_value at index {index}, row: {row}")
    return translated_df


def _create_default_dataframe():
    default_columns = [
        "source_language",
        "source_value",
        "subject_id",
        "predicate_id",
        "translation_language",
        "translation_value",
        "translation_status",
    ]
    return pd.DataFrame(columns=default_columns)


def prepare_translation_for_ontology(
    ontology,
    language_code,
    df_babelon: pd.DataFrame,
    terms: List[str],
    fields: List[str],
    include_not_translated: bool = False,
    update_translation_status: bool = True,
):
    """Prepare a babelon translation table for an ontology."""
    if df_babelon is None:
        df_augmented = _create_default_dataframe()
    else:
        df_augmented = df_babelon.copy()

    output_source_changed_data = []
    output_not_translated_data = []

    if terms is None:
        terms = []
        for entity in ontology.entities():
            terms.append(entity)

    # First, we update the existing records
    # If a value has changed in the ontology, we flip the translation status to
    # CANDIDATE

    processed: Dict[str, List[str]] = {}
    mark_index_for_removal = []

    for index, row in df_augmented.iterrows():
        subject_id = row["subject_id"]
        if subject_id not in processed:
            processed[subject_id] = []
        predicate_id = row["predicate_id"]
        if predicate_id not in processed[subject_id]:
            processed[subject_id].append(predicate_id)
        source_value = row["source_value"]
        translation_status = row["translation_status"]
        term_metadata = _get_metadata_for_term(ontology, subject_id)
        if translation_status == "NOT_TRANSLATED":
            if not include_not_translated:
                mark_index_for_removal.append(index)
            if predicate_id in term_metadata:
                output_not_translated_data.append(row.to_dict())
            else:
                logging.warning(
                    f"{predicate_id} value for {subject_id} is marked as NOT_TRANSLATED,"
                    f"but does not exist at all in the ontology. Omitting row."
                )
        if predicate_id in term_metadata:
            ontology_value = term_metadata[predicate_id][0]
            if len(term_metadata[predicate_id]) > 1:
                logging.warning(
                    f"{predicate_id} value for {subject_id} is ambiguous,"
                    f"picking first one ({term_metadata[predicate_id]})."
                )
            if not _is_equivalent_string(ontology_value, source_value):
                # If the translated string and the ontology literal are not equivalent, change status:
                translation_value = row["translation_value"]
                # Set the ontology value as the source value, so that the translation profiles are consistent
                # With what is in the ontology
                df_augmented.at[index, "source_value"] = ontology_value
                new_translation_status = (
                    "CANDIDATE" if translation_value != "NOT_TRANSLATED" else "NOT_TRANSLATED"
                )
                if update_translation_status:
                    df_augmented.at[index, "translation_status"] = new_translation_status
                logging.warning(
                    f"{predicate_id} value for {subject_id} is {source_value} in the translation table, "
                    f"but {ontology_value} in the ontology."
                )
                output_source_changed_data.append(row)
            else:
                # Because `_is_equivalent_string` is a bit forgiving, we still want to replace the source value,
                # so that the translation profiles are consistent
                df_augmented.at[index, "source_value"] = ontology_value
        else:
            logging.warning(
                f"{predicate_id} value for {subject_id} does not exist in ontology. "
                f"Keeping value in the translation profile: {source_value}"
            )

    df_augmented.drop(mark_index_for_removal, inplace=True)

    added_rows = []
    for term in terms:
        term_metadata = _get_metadata_for_term(ontology, term)
        for field in fields:
            if term in processed:
                if field in processed[term]:
                    continue
            if field not in term_metadata:
                logging.info(f"{field} does not exist for {term}.")
                continue
            for source_value in term_metadata[field]:
                subject_id = term
                data_row = {
                    "source_language": "en",
                    "source_value": source_value,
                    "subject_id": subject_id,
                    "predicate_id": field,
                    "translation_language": language_code,
                    "translation_value": "",
                    "translation_status": "NOT_TRANSLATED",
                }

                added_rows.append(data_row)
                output_not_translated_data.append(data_row)

    if added_rows and include_not_translated:
        df_added = pd.DataFrame(added_rows)
        df_augmented = pd.concat([df_augmented, df_added], ignore_index=True)

    if output_not_translated_data:
        df_output_not_translated = pd.DataFrame(output_not_translated_data)
    else:
        df_output_not_translated = _create_default_dataframe()

    if output_source_changed_data:
        df_output_source_changed = pd.DataFrame(output_source_changed_data)
    else:
        df_output_source_changed = _create_default_dataframe()

    return df_augmented, df_output_source_changed, df_output_not_translated


def _is_equivalent_string(string1, string2):
    """Compare two strings after they are whitespace, punctuation and case normalised."""

    def _normalize(s):
        # Remove punctuation
        s = s.translate(str.maketrans("", "", string.punctuation))
        # Normalize whitespace and convert to lowercase
        return re.sub(r"\s+", " ", s).strip().lower()

    normalized_string1 = _normalize(string1)
    normalized_string2 = _normalize(string2)

    # Compare the normalized strings
    return normalized_string1 == normalized_string2


def _get_metadata_for_term(ontology, term):
    term_metadata = ontology.entity_metadata_map(term)
    term_label = ontology.label(term)
    if term_label:
        term_metadata["rdfs:label"] = [term_label]
    term_definition = ontology.definition(term)
    if term_definition:
        term_metadata["IAO:0000115"] = [term_definition]
    return term_metadata
