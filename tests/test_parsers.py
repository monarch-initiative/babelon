"""Tests for parsers."""

import unittest
from xml.dom import minidom  # noqa

from babelon.parsers.xliff import xliff_path_to_babelon
from tests.test_data import data_dir as test_data_dir


class TestParse(unittest.TestCase):
    """A test case for parser functionality."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.xliff_file = f"{test_data_dir}/hpo_dutch.xliff"
        self.xliff_file_xml = minidom.parse(self.xliff_file)  # noqa

    def test_parse_xliff(self):
        """Test parsing an Xliff XML."""
        df_babelon, df_synonyms = xliff_path_to_babelon(input_file_path=self.xliff_file)

        # out_path_babelon = os.path.join(test_out_dir, "test_parse_xliff.babelon.tsv")
        # out_path_synonyms = os.path.join(test_out_dir, "test_parse_xliff.synonyms.tsv")
        # df_babelon.to_csv(out_path_babelon, sep="\t")
        # df_synonyms.to_csv(out_path_synonyms, sep="\t")

        self.assertEqual(
            len(df_babelon),
            25133,
            f"{self.xliff_file} has the wrong number of translations.",
        )

        self.assertEqual(
            len(df_synonyms),
            16755,
            f"{self.xliff_file} has the wrong number of translations.",
        )
