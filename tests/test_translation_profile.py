"""Tests for translation profile."""
import unittest

from babelon.translation_profile import update_translation_status


class TestTranslationProfile(unittest.TestCase):
    """A test case for translation profile functionality."""

    def setUp(self) -> None:
        """Set up the test case."""

    def test_update_translation_profile(self):
        """Test update_translation_profile"""
        res = update_translation_status(
            "tests/data/translations/hp-tr.babelon.tsv", "tests/data/hp.obo"
        )
        assert any(res[res["translation_status"].isin(["CANDIDATE"])]) == True
