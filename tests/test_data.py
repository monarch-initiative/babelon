"""Tests for loading and processing data."""

import os
from typing import Any, List, Mapping

import yaml

from tests.constants import cwd, data_dir, test_out_dir

test_validate_dir = os.path.join(cwd, "validate_data")
schema_dir = os.path.join(cwd, os.pardir, "schema")

def get_test_file(filename: str) -> str:
    """Get a test file path inside the test data directory."""
    return os.path.join(data_dir, filename)

