"""Tests for translation profile."""

import os
import unittest

from dotenv import load_dotenv
from oaklib.implementations.pronto.pronto_implementation import ProntoImplementation
from oaklib.resource import OntologyResource

from babelon.translate import OpenAITranslator, prepare_translation_for_ontology, translate_profile
from tests.constants import _create_simple_example_for_testing
from tests.test_data import data_dir as test_data_dir
from tests.test_data import env_file


class TestTranslationProfile(unittest.TestCase):
    """A test case for translation profile functionality."""

    def setUp(self) -> None:
        """Set up the test case."""

    @unittest.skipIf(not os.path.exists(env_file), "Skipping test as .env file does not exist")
    def test_translate(self):
        """Test update_translation_profile."""
        load_dotenv()
        translator = OpenAITranslator()
        translated_value = translator.translate("fever", "de")
        self.assertEqual("Fieber", translated_value)

    @unittest.skipIf(not os.path.exists(env_file), "Skipping test as .env file does not exist")
    def test_translate_profile(self):
        """Test to see if a small babelon profile can be translated."""
        load_dotenv()
        df_babelon = _create_simple_example_for_testing()
        df_translated = translate_profile(df_babelon)
        translations = df_translated["translation_value"].tolist()
        expected_translations = ["Fieber", "Schlaganfall"]
        self.assertEqual(translations[0], expected_translations[0])

    def test_prepare_translation_for_ontology(self):
        """Test the update method for babelon profiles."""
        test_file = f"{test_data_dir}/hp-testsubset.obo"
        resource = OntologyResource(slug=test_file, local=True)
        ontology = ProntoImplementation(resource)
        terms = ["HP:0001707"]
        fields = ["rdfs:label"]
        df_babelon = _create_simple_example_for_testing()
        df_augmented = prepare_translation_for_ontology(ontology, "de", df_babelon, terms, fields)
        subject_ids = df_augmented["subject_id"].tolist()
        expected_subject_ids = ["HP:0001945", "HP:0001297", "HP:0001707"]
        self.assertEqual(expected_subject_ids, subject_ids)
