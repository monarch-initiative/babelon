"""Translate Babelon profiles."""

import json
import logging
import os
import re
import string
import time
from typing import ClassVar, Dict, List, Optional

import anthropic
import deepl
import llm
import pandas as pd

# DeepL rate-limit / transient-error retry config.
# The DeepL Free tier in particular throttles aggressively; without retries
# any batch larger than a few dozen rows tends to fail mid-run.
_DEEPL_MAX_ATTEMPTS = 8
_DEEPL_INITIAL_BACKOFF_SECONDS = 5
_DEEPL_MAX_BACKOFF_SECONDS = 120

# Anthropic (Claude) defaults. Terms are sent in batches rather than one request
# per row: a batch amortises the instruction prompt over many terms, which is
# both markedly cheaper and orders of magnitude faster over a whole ontology.
_ANTHROPIC_DEFAULT_MODEL = "claude-sonnet-5"
_ANTHROPIC_DEFAULT_BATCH_SIZE = 40
_ANTHROPIC_MAX_ATTEMPTS = 5
_ANTHROPIC_INITIAL_BACKOFF_SECONDS = 2
_ANTHROPIC_MAX_BACKOFF_SECONDS = 60

# The default identifier recorded in the `translator` column. Kept as-is for the
# existing backends so their output does not change.
_DEFAULT_TRANSLATOR_ID = "wikidata:Q116709136"


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

    def translate_batch(self, texts: List[str], target_language: str) -> List[str]:
        """Translate several texts at once, returning one result per input.

        The default implementation simply calls :meth:`translate` for each text,
        so backends that have no batch endpoint keep working unchanged. Backends
        that can translate many texts in a single request (LLMs in particular)
        should override this: it amortises the instruction prompt across the
        batch and cuts the number of round trips by orders of magnitude.

        Args:
            texts (List[str]): The texts to be translated.
            target_language (str): The language to translate the texts into.

        Returns:
            List[str]: Translations, aligned by position with ``texts``.
        """
        return [self.translate(text, target_language) for text in texts]

    def batch_size(self) -> int:
        """Return how many texts to pass to :meth:`translate_batch` at a time."""
        return 1

    def translator_id(self) -> str:
        """Return the identifier recorded in the ``translator`` column."""
        return _DEFAULT_TRANSLATOR_ID


class OpenAITranslator(Translator):
    """A specific translator class that uses GPT-4 for translation."""

    def __init__(self, model="gpt-4o"):
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


class DeepLTranslator(Translator):
    """A specific translator class that uses DeepL API for translation."""

    def __init__(self):
        """Instantiate DeepL translator with an API key."""
        self.api_key = os.environ["DEEPL_API_KEY"]
        self.translator = deepl.Translator(self.api_key)

    def model_name(self):
        """Return the unique name of the translation model."""
        return "DeepL"

    def translate(self, text_to_translate, language_code):
        """
        Translate text using DeepL API with exponential-backoff retry.

        Args:
        text_to_translate (str): The text to be translated.
        language_code (str): The target language code (e.g., 'DE' for German).

        Returns:
        str: The translated text, or an empty string if translation fails.
        """
        target_lang = language_code.upper()
        backoff = _DEEPL_INITIAL_BACKOFF_SECONDS
        last_error: Optional[Exception] = None
        for attempt in range(1, _DEEPL_MAX_ATTEMPTS + 1):
            try:
                result = self.translator.translate_text(text_to_translate, target_lang=target_lang)
                translation = result.text
                if translation:
                    print(f"Translation: {translation}")
                    return translation
                return ""
            except (
                deepl.exceptions.TooManyRequestsException,
                deepl.exceptions.ConnectionException,
            ) as e:
                last_error = e
                if attempt == _DEEPL_MAX_ATTEMPTS:
                    break
                print(
                    f"DeepL transient error ({type(e).__name__}); "
                    f"retrying in {backoff}s (attempt {attempt}/{_DEEPL_MAX_ATTEMPTS})"
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, _DEEPL_MAX_BACKOFF_SECONDS)
        # Quota / auth errors propagate immediately (not caught above). For exhausted
        # retries on transient errors we surface the last exception so callers can decide.
        raise last_error  # type: ignore[misc]


class AnthropicTranslator(Translator):
    """A translator class that uses Anthropic's Claude models.

    Unlike the other backends this one translates in batches: a single request
    carries many terms, which amortises the instruction prompt and removes the
    per-row round trip. Responses are constrained with a JSON schema so results
    map back by index instead of being scraped out of free text.
    """

    def __init__(self, model: str = _ANTHROPIC_DEFAULT_MODEL, batch_size: Optional[int] = None):
        """Instantiate a Claude translator.

        Args:
            model (str): The Claude model id, e.g. ``claude-sonnet-5``.
            batch_size (int): How many terms to send per request.
        """
        # The SDK resolves credentials itself (ANTHROPIC_API_KEY, or a configured
        # profile), so no key is read or held here.
        self.client = anthropic.Anthropic()
        self.model = model
        self._batch_size = batch_size or _ANTHROPIC_DEFAULT_BATCH_SIZE

    def model_name(self):
        """Return the unique name of the translation model."""
        return self.model

    def batch_size(self) -> int:
        """Return the configured batch size."""
        return self._batch_size

    def translator_id(self) -> str:
        """Return the identifier recorded in the ``translator`` column."""
        return f"anthropic:{self.model}"

    _SYSTEM_PROMPT = (
        "You translate terms from an ontology into another language. The terms are "
        "controlled-vocabulary entries used by domain experts, not prose.\n\n"
        "Rules:\n"
        "- Translate into the established technical register of the target language. "
        "Use the term a specialist in the field would write, not a lay paraphrase.\n"
        "- Where the target language has a standard technical or Latin/Greek-derived "
        "term, prefer it over a descriptive circumlocution.\n"
        "- Preserve the grammatical shape of the source. Ontology labels are noun "
        "phrases naming a class, not sentences. Do not add articles, final "
        "punctuation, commentary or explanations.\n"
        "- Keep qualifiers exact. Words such as absent, decreased, increased, "
        "bilateral, unilateral, mild and severe carry meaning that must survive "
        "translation, as must any negation.\n"
        "- Do not transliterate an English term when a real term exists in the "
        "target language.\n"
        "- If a term genuinely has no translation, return it unchanged.\n"
        "- Return exactly one translation for every numbered input, keeping the "
        "numbering. Never merge, skip or reorder entries."
    )

    _RESPONSE_SCHEMA: ClassVar[Dict] = {
        "type": "object",
        "properties": {
            "translations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "n": {
                            "type": "integer",
                            "description": "The number of the input term.",
                        },
                        "translation": {"type": "string"},
                    },
                    "required": ["n", "translation"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["translations"],
        "additionalProperties": False,
    }

    def translate(self, text_to_translate, language_code):
        """Translate a single text. Prefer :meth:`translate_batch`.

        Args:
            text_to_translate (str): The text to be translated.
            language_code (str): The target language code, e.g. ``de``.

        Returns:
            str: The translated text, or an empty string if translation fails.
        """
        return self.translate_batch([text_to_translate], language_code)[0]

    def translate_batch(self, texts: List[str], target_language: str) -> List[str]:
        """Translate a batch of texts in a single request.

        Args:
            texts (List[str]): The texts to be translated.
            target_language (str): The target language code, e.g. ``de``.

        Returns:
            List[str]: Translations aligned by position with ``texts``. An entry
            is an empty string if the model returned nothing for it, which
            leaves the row untranslated for a later run to pick up.

        Raises:
            Exception: The last transient API error, if all retries are exhausted.
        """
        if not texts:
            return []

        numbered = "\n".join(f"{i}. {text}" for i, text in enumerate(texts))
        prompt = (
            f"Translate these {len(texts)} ontology terms into the language with "
            f"ISO code '{target_language}'.\n\n{numbered}"
        )

        backoff = _ANTHROPIC_INITIAL_BACKOFF_SECONDS
        last_error: Optional[Exception] = None
        for attempt in range(1, _ANTHROPIC_MAX_ATTEMPTS + 1):
            try:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=16000,
                    system=[
                        {
                            "type": "text",
                            "text": self._SYSTEM_PROMPT,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    messages=[{"role": "user", "content": prompt}],
                    output_config={
                        "format": {"type": "json_schema", "schema": self._RESPONSE_SCHEMA}
                    },
                )
                if response.stop_reason == "refusal":
                    print(f"Claude declined to translate a batch: {response.stop_details}")
                    return [""] * len(texts)
                return self._parse_response(response, len(texts))
            except (
                anthropic.RateLimitError,
                anthropic.APIConnectionError,
                anthropic.InternalServerError,
            ) as e:
                last_error = e
                if attempt == _ANTHROPIC_MAX_ATTEMPTS:
                    break
                print(
                    f"Anthropic transient error ({type(e).__name__}); "
                    f"retrying in {backoff}s (attempt {attempt}/{_ANTHROPIC_MAX_ATTEMPTS})"
                )
                time.sleep(backoff)
                backoff = min(backoff * 2, _ANTHROPIC_MAX_BACKOFF_SECONDS)
        raise last_error  # type: ignore[misc]

    @staticmethod
    def _parse_response(response, expected: int) -> List[str]:
        """Map a structured response back onto the batch by index."""
        text = next((block.text for block in response.content if block.type == "text"), "")
        try:
            entries = json.loads(text)["translations"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logging.warning(f"Could not read translation response: {e}")
            return [""] * expected
        by_index = {
            entry["n"]: entry["translation"]
            for entry in entries
            if isinstance(entry, dict) and "n" in entry and "translation" in entry
        }
        missing = expected - sum(1 for i in range(expected) if by_index.get(i))
        if missing:
            logging.warning(f"{missing} of {expected} terms came back without a translation.")
        return [by_index.get(i, "") or "" for i in range(expected)]


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
        return OpenAITranslator("gpt-4o")
    elif model == "gpt-3.5":
        return OpenAITranslator("gpt-3.5-turbo")
    elif model == "deepl":
        return DeepLTranslator()
    elif model in ("claude", "anthropic"):
        return AnthropicTranslator()
    elif model.startswith("claude-"):
        # Any current or future Claude model id is passed straight through.
        return AnthropicTranslator(model)
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
