"""Tests for translation profile."""

import os
import unittest

from dotenv import load_dotenv
from oaklib import get_adapter

from babelon.translate import (
    OpenAITranslator,
    _is_equivalent_string,
    prepare_translation_for_ontology,
    translate_profile,
)
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
        ontology = get_adapter(f"pronto:{test_file}")
        terms = ["HP:0001707"]
        fields = ["rdfs:label"]
        df_babelon = _create_simple_example_for_testing()
        df_augmented, df_output_source_changed, df_output_not_translated = (
            prepare_translation_for_ontology(
                ontology, "de", df_babelon, terms, fields, include_not_translated=True
            )
        )

        self.assertEqual(
            ["HP:0001945", "HP:0001297", "HP:0001707"], df_augmented["subject_id"].tolist()
        )
        self.assertEqual([], df_output_source_changed["subject_id"].tolist())
        self.assertEqual(
            ["HP:0001945", "HP:0001297", "HP:0001707"],
            df_output_not_translated["subject_id"].tolist(),
        )

    def test_equivalent_string(self):
        """Test if _is_equivalent_string() catches important cases."""
        string1 = "Hello, my."
        string2 = "hello  my"

        self.assertTrue(_is_equivalent_string(string1, string2))
