"""Tests for parsers."""

import unittest
from xml.dom import minidom  # noqa

from babelon.babelon_io import to_babelon_linkml_document, to_json, to_owl_graph
from babelon.utils import BabelonDataFrame
from tests.constants import _create_empty_example_for_testing, _create_simple_example_for_testing


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
        self.assertEqual(5, len(doc))
        self.assertTrue("translations" in doc)

    def test_convert_owl(self):
        """Test conver an Xliff XML."""
        df_babelon = _create_simple_example_for_testing()
        bdf = BabelonDataFrame(df=df_babelon)

        graph = to_owl_graph(bdf)

        self.assertEqual(25, len(graph))

        # t = graph.serialize(format="ttl", encoding="utf-8")
        # test_file_path = f"{test_out_dir}/simple-test.babelon.tsv"
        # with open(test_file_path, "w", encoding="utf-8") as file:
        #    print(t.decode(), file=file)

    def test_convert_empty_owl(self):
        """Test Convert an empty file."""
        df_babelon = _create_empty_example_for_testing()
        bdf = BabelonDataFrame(df=df_babelon)

        graph = to_owl_graph(bdf)

        self.assertEqual(1, len(graph))

        # t = graph.serialize(format="ttl", encoding="utf-8")
        # test_file_path = f"{test_out_dir}/simple-test.babelon.tsv"
        # with open(test_file_path, "w", encoding="utf-8") as file:
        #    print(t.decode(), file=file)

    def test_convert_json(self):
        """Test conver an Xliff XML."""
        df_babelon = _create_simple_example_for_testing()
        bdf = BabelonDataFrame(df=df_babelon)

        data = to_json(bdf)

        self.assertTrue("translations" in data)
        self.assertEqual(2, len(data["translations"]))

        # test_file_path = f"{test_out_dir}/simple-test.babelon.json"
        # with open(test_file_path, "w", encoding="utf-8") as file:
        #    json.dump(data, file, indent=2)
