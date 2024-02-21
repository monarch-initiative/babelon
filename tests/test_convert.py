"""Tests for parsers."""

import logging
import unittest
from xml.dom import minidom  # noqa

from babelon.babelon_io import to_babelon_linkml_document, write_json, write_owl
from babelon.utils import BabelonDataFrame
from tests.constants import _create_simple_example_for_testing, test_out_dir


class TestConvert(unittest.TestCase):
    """A test case for parser functionality."""

    def setUp(self) -> None:
        """Set up the test case."""
        pass

    def test_convert_linkml(self):
        """Test conver an Xliff XML."""
        df_babelon = _create_simple_example_for_testing()
        bdf = BabelonDataFrame(df=df_babelon)
        doc = to_babelon_linkml_document(bdf)
        self.assertEquals(1, len(doc))
        self.assertTrue("translations" in doc)

    def test_convert_owl(self):
        """Test conver an Xliff XML."""
        df_babelon = _create_simple_example_for_testing()
        bdf = BabelonDataFrame(df=df_babelon)
        test_file_path = f"{test_out_dir}/simple-test.babelon.tsv"
        with open(test_file_path, "w", encoding="utf-8") as file:
            write_owl(bdf, file)

    def test_convert_json(self):
        """Test conver an Xliff XML."""
        df_babelon = _create_simple_example_for_testing()
        bdf = BabelonDataFrame(df=df_babelon)
        test_file_path = f"{test_out_dir}/simple-test.babelon.json"
        with open(test_file_path, "w", encoding="utf-8") as file:
            write_json(bdf, file)
