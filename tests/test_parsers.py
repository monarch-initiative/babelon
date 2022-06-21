"""Tests for parsers."""

import json
import math
import os
import unittest
from xml.dom import minidom

import numpy as np
import pandas as pd
import yaml

from tests.test_data import data_dir as test_data_dir
from tests.test_data import test_out_dir

class TestParse(unittest.TestCase):
    """A test case for parser functionality."""

    def setUp(self) -> None:
        """Set up the test case."""
        self.xliff_file = f"{test_data_dir}/hpo_dutch.xliff"
        self.xliff_file_xml = minidom.parse(self.xliff_file)

    def test_parse_xliff(self):
        """Test parsing an Xliff XML."""
        
        out_path = os.path.join(test_out_dir, "test_parse_alignment_minidom.tsv")
        parser = XliffParser(input_file_path=self.xliff_file, output_file_path=out_path)
        
        df = parser.xml_to_tsv()
        df.to_csv(out_path, sep="\t")
        
        self.assertEqual(
            len(df),
            646,
            f"{self.xliff_file} has the wrong number of translations.",
        )