"""Tests for translation profile."""

import unittest

import pandas as pd
from dotenv import load_dotenv
from oaklib.implementations.pronto.pronto_implementation import ProntoImplementation
from oaklib.resource import OntologyResource

from babelon.translate import GPT4Translator, prepare_translation_for_ontology, translate_profile


def _create_simple_example():
    data = [
        {
            "source_language": "en",
            "source_value": "Fever",
            "subject_id": "HP:0001945",
            "predicate_id": "rdfs:label",
            "translation_language": "de",
            "translation_value": "",
            "translation_status": "NOT_TRANSLATED",
        },
        {
            "source_language": "en",
            "source_value": "Stroke",
            "subject_id": "HP:0001297",
            "predicate_id": "rdfs:label",
            "translation_language": "de",
            "translation_value": "",
            "translation_status": "NOT_TRANSLATED",
        },
    ]
    return pd.DataFrame(data)


class TestTranslationProfile(unittest.TestCase):
    """A test case for translation profile functionality."""

    def setUp(self) -> None:
        """Set up the test case."""

    def test_translate(self):
        """Test update_translation_profile."""
        load_dotenv()
        translator = GPT4Translator()
        translated_value = translator.translate("fever", "de")
        self.assertEqual("Fieber", translated_value)

    def test_translate_profile(self):
        """Test to see if a small babelon profile can be translated."""
        load_dotenv()
        df_babelon = _create_simple_example()
        df_translated = translate_profile(df_babelon)
        translations = df_translated["translation_value"].tolist()
        expected_translations = ["Fieber", "Schlaganfall"]
        self.assertEqual(translations, expected_translations)

    def test_prepare_translation_for_ontology(self):
        """Test the update method for babelon profiles."""
        resource = OntologyResource(slug="data/hp-testsubset.obo", local=True)
        ontology = ProntoImplementation(resource)
        terms = ["HP:0001707"]
        fields = ["rdfs:label"]
        df_babelon = _create_simple_example()
        df_augmented = prepare_translation_for_ontology(ontology, "de", df_babelon, terms, fields)
        subject_ids = df_augmented["subject_id"].tolist()
        expected_subject_ids = ["HP:0001945", "HP:0001297"]
        self.assertEquals(expected_subject_ids, subject_ids)
