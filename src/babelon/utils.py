"""Utility methods for babelon processing."""

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from string import punctuation
from typing import TextIO, Union

import pandas as pd
import validators
from curies import Converter
from sssom.util import get_converter as get_sssom_converter


def parse_babelon(input_path):
    """Parse a babelon TSV file into a BabelonDataFrame."""
    df = pd.read_csv(input_path, sep="\t")
    return BabelonDataFrame(df=df)


def raise_for_bad_path(file_path: Union[str, Path]) -> None:
    """
    Throw exception if file path is invalid.

    Args:
        file_path: The file path or URL to be validated.

    Raises:
        FileNotFoundError: If the provided file path is not a valid file or URL.

    """
    if isinstance(file_path, Path):
        if not file_path.is_file():
            raise FileNotFoundError(f"{file_path} is not a valid file path or url.")
    elif not isinstance(file_path, str):
        logging.info("Path provided to raise_for_bad_path() is neither a Path nor str-like object.")
    elif not validators.url(file_path) and not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} is not a valid file path or url.")


@lru_cache(1)
def get_converter():
    """Get default SSSOM converter."""
    return get_sssom_converter()


@dataclass
class BabelonDataFrame:
    """A collection of mappings represented as a DataFrame, together with additional metadata."""

    df: pd.DataFrame
    converter: Converter = field(default_factory=get_converter)

    @property
    def prefix_map(self):
        """Get a simple, bijective prefix map."""
        return self.converter.bimap

    @classmethod
    def with_converter(
        cls,
        converter: Converter,
        df: pd.DataFrame,
    ) -> "BabelonDataFrame":
        """Instantiate with a converter instead of a vanilla prefix map."""
        # TODO replace with regular instantiation
        return cls(
            df=df,
            converter=converter,
        )


def _get_file_extension(file: Union[str, Path, TextIO]) -> str:
    """Get file extension.

    :param file: File path
    :return: format of the file passed, default tsv
    """
    if isinstance(file, Path):
        if file.suffix:
            return file.suffix.strip(punctuation)
        else:
            logging.warning(
                f"Cannot guess format from {file}, despite appearing to be a Path-like object."
            )
    elif isinstance(file, str):
        filename = file
        parts = filename.split(".")
        if len(parts) > 0:
            f_format = parts[-1]
            return f_format.strip(punctuation)
        else:
            logging.warning(f"Cannot guess format from {filename}")
    logging.info("Cannot guess format extension for this file, assuming TSV.")
    return "tsv"
