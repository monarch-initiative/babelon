"""Command line interface for Babelon."""

import logging
import os
import sys
from pathlib import Path

import click

from babelon.babelon_io import parse_file
from babelon.translation_profile import statistics_translation_profile, update_translation_profile

info_log = logging.getLogger("info")
# Click input options common across commands
input_argument = click.argument("input_path", required=True, type=click.Path())

input_format_option = click.option(
    "--input-format",
    "-f",
    help="Input format",
)
output_option = click.option(
    "--output",
    "-o",
    help="Path of output file.",
    type=Path,
    default=sys.stdout,
)
output_format_option = click.option(
    "--output-format",
    "-t",
    help="Output format",
)
output_directory_option = click.option(
    "-d",
    "--output-directory",
    type=click.Path(),
    help="Path to output file",
    default=os.getcwd(),
)


@click.group()
@click.option("-v", "--verbose", count=True)
@click.option("-q", "--quiet")
def main(verbose=1, quiet=False) -> None:
    """Command Line Interface for the main method for SSSOM.

    Args:
        verbose (int, optional): Verbose flag.
        quiet (bool, optional): Queit Flag.
    """
    if verbose >= 2:
        info_log.setLevel(level=logging.DEBUG)
    elif verbose == 1:
        info_log.setLevel(level=logging.INFO)
    else:
        info_log.setLevel(level=logging.WARNING)
    if quiet:
        info_log.setLevel(level=logging.ERROR)


@click.group()
def babelon():
    """babelon."""


# Input and metadata would be files (file paths). Check if exists.
# @main.command()
@click.command()
@input_argument
# @input_format_option
@output_option
def parse(input_path, output):
    """Parse a file in one of the supported formats (such as obographs) into an SSSOM TSV file."""
    parse_file(input_path=input_path, output_path=output)


if __name__ == "__main__":
    try:
        parse(sys.argv[1:])
    except Exception as e:
        print(e)


@click.command("statistics")
@click.option(
    "--translation-profile",
    "-t",
    metavar="PATH",
    required=True,
    help="Path to translation profile.",
    type=Path,
)
def statistics_translation_profile_command(
    translation_profile: Path,
):
    """Takes as an input a babelon profile (TSV) and returns some basic stats:
        number of translations by source_language, target_language
        number of translations by source_language, target_language, predicate_id
        number of translations by source_language, target_language, translation_status
    Args:
        translation_profile (Path): translation profile
    """
    statistics_translation_profile(translation_profile)


@click.command("update-translation-profile")
@click.option(
    "--translation-profile",
    "-t",
    metavar="PATH",
    required=True,
    help="Path to translation profile.",
    type=Path,
)
@click.option(
    "--ontology-file",
    "-o",
    metavar="PATH",
    required=True,
    help="Path to ontology file.",
    type=Path,
)
@click.option(
    "--output",
    "-o",
    metavar="PATH",
    required=True,
    help="Path where updated profile will be written.",
    type=Path,
)
def update_translation_profile_command(
    translation_profile: Path,
    ontology_file: Path,
    output: Path,
):
    """Write update_translation_profile to TSV file.

    Args:
        translation_profile (Path): Path to the translation profile
        ontology_file (Path): Path to the ontology file
        output (Path): Path to the output TSV file
    """
    update_translation_profile(translation_profile, ontology_file, output)


babelon.add_command(parse)
babelon.add_command(update_translation_profile_command)
babelon.add_command(statistics_translation_profile_command)
