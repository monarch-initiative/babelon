"""Tests for translation profile."""

import unittest

from babelon.utils import drop_unknown_columns_babelon
from tests.constants import _create_simple_example_for_testing


class TestUtils(unittest.TestCase):
    """A test case for translation profile functionality."""

    def setUp(self) -> None:
        """Set up the test case."""
        pass

    def test_drop_unknown_columns_babelon(self):
        """Test update_translation_profile."""
        df_babelon = _create_simple_example_for_testing()
        df_babelon_original = df_babelon.copy()
        df_babelon["irrelevant_column"] = "irrelevant value"

        self.assertNotEqual(list(df_babelon.columns), list(df_babelon_original.columns))
        df_babelon = drop_unknown_columns_babelon(df_babelon)

        self.assertEqual(list(df_babelon.columns), list(df_babelon_original.columns))
        self.assertEqual(df_babelon.shape, df_babelon_original.shape)
        self.assertEqual(list(df_babelon.index), list(df_babelon_original.index))
        self.assertEqual(list(df_babelon.dtypes), list(df_babelon_original.dtypes))
