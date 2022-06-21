"""Command line interface for Babelon.

"""

import logging
import os
import re
import sys
from pathlib import Path
from typing import ChainMap, Dict, List, Optional, TextIO, Tuple

import click
import pandas as pd
import yaml

from . import __version__

# Click input options common across commands
input_argument = click.argument("input", required=True, type=click.Path())

input_format_option = click.option(
    "-I",
    "--input-format",
    help=f'The string denoting the input format, e.g. {",".join(SSSOM_READ_FORMATS)}',
)
output_option = click.option(
    "-o",
    "--output",
    help="Path of SSSOM output file.",
    type=click.File(mode="w"),
    default=sys.stdout,
)
output_format_option = click.option(
    "-O",
    "--output-format",
    help=f'Desired output format, e.g. {",".join(SSSOM_EXPORT_FORMATS)}',
)
output_directory_option = click.option(
    "-d",
    "--output-directory",
    type=click.Path(),
    help="Output directory path.",
    default=os.getcwd(),
)

@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
@click.version_option(__version__)
def main(verbose: int, quiet: bool):
    """Run the SSSOM CLI."""
    if verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)
    if quiet:
        logging.basicConfig(level=logging.ERROR)


# Input and metadata would be files (file paths). Check if exists.
@main.command()
@input_argument
@input_format_option
@output_option
def parse(
    input: str,
    input_format: str,
    output: TextIO,
):
    """Parse a file in one of the supported formats (such as obographs) into an SSSOM TSV file."""
    parse_file(
        input_path=input,
        output=output,
        input_format=input_format,
    )


if __name__ == "__main__":
    main()
