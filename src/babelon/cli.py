"""Command line interface for Babelon."""

import logging
import os
import sys
from pathlib import Path
from typing import TextIO

import click
import pandas as pd
from oaklib import get_adapter

from babelon.babelon_io import convert_file, parse_file
from babelon.translate import prepare_translation_for_ontology, translate_profile
from babelon.translation_profile import statistics_translation_profile

info_log = logging.getLogger("info")
# Click input options common across commands
input_argument = click.argument("input", required=False, type=click.Path())

input_format_option = click.option(
    "--input-format",
    "-f",
    help="Input format",
)
output_option = click.option(
    "--output",
    "-o",
    help="Path of output file.",
    type=click.File(mode="w"),
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
    """Command Line Interface for the main method for Babelon.

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
@click.command("parse")
@input_argument
# @input_format_option
@output_option
def parse(input, output):
    """Parse a file in one of the supported formats (such as obographs) into an Babelon TSV file."""
    parse_file(input_path=input, output_path=output)


@click.command("convert")
@input_argument
@output_option
@output_format_option
def convert(input: str, output: TextIO, output_format: str):
    """Convert a Babelon file into a different format.

    Example:
        babelon convert my.babelon.tsv --output-format owl --output my.babelon.owl
    """  # noqa: DAR101
    convert_file(input_path=input, output=output, output_format=output_format)


@click.command("translate")
@input_argument
@click.option(
    "--model",
    type=str,
    help="The model used to run the translation. "
    "Currently allowed: gpt-4, gpt-3.5 or any official model from OpenAI "
    "(https://platform.openai.com/docs/models).",
    default="gpt-4",
)
@click.option("--language-code", type=str, help="ISO code for the target translation language.")
@click.option(
    "--update-existing",
    type=bool,
    default=False,
    help="If true, all values will be translated, including the once already translated.",
)
@output_option
def translate(input, model, language_code, update_existing, output):
    """Process a table to translate values."""
    df = pd.read_csv(input, sep="\t")
    translated_df = translate_profile(
        babelon_df=df, language_code=language_code, update_existing=update_existing, model=model
    )
    translated_df.to_csv(output, sep="\t", index=False)


@click.command()
@input_argument
@click.option("--oak-adapter", type=str, help="Oak handle string.")
@click.option("--language-code", type=str, help="ISO code for the target translation language.")
@click.option(
    "--term-list",
    type=click.Path(exists=True),
    help="Path to file containing term ids to be translated.",
)
@click.option("--field", multiple=True, type=str, help="Fields to be translated.")
@output_option
def prepare_translation(input, oak_adapter, language_code, term_list, field, output):
    """Translate ontology fields based on the specified language code."""
    ontology = get_adapter(oak_adapter)
    if input:
        df_babelon = pd.read_csv(input, sep="\t")
    else:
        df_babelon = None

    terms = None
    if term_list:
        with open(term_list, "r") as file:
            lines = file.readlines()
        terms = [line.strip() for line in lines]

    output_profile = prepare_translation_for_ontology(
        ontology=ontology,
        language_code=language_code,
        df_babelon=df_babelon,
        terms=terms,
        fields=field,
    )
    output_profile.to_csv(output, sep="\t", index=False)


@click.command("statistics")
@input_argument
def statistics_translation_profile_command(
    input: Path,
):
    """Take as an input a babelon profile (TSV) and returns some basic stats.

        number of translations by source_language, target_language
        number of translations by source_language, target_language, predicate_id
        number of translations by source_language, target_language, translation_status
    Args:
        input (Path): translation profile
    """
    statistics_translation_profile(input)


@click.command("example")
@input_argument
def example(input):
    """Generate an example babelon file for user."""
    data = [
        {
            "source_language": "en",
            "source_value": "Fever",
            "subject_id": "HP:0001945",
            "predicate_id": "rdfs:label",
            "translation_language": "de",
            "translation_value": "",
            "translation_status": "NOT_TRANSLATED",
        },
        {
            "source_language": "en",
            "source_value": "Stroke",
            "subject_id": "HP:0001297",
            "predicate_id": "rdfs:label",
            "translation_language": "de",
            "translation_value": "",
            "translation_status": "NOT_TRANSLATED",
        },
    ]
    df = pd.DataFrame(data)

    if input:
        df.to_csv(input, sep="\t", index=False)
    else:
        click.echo(df.to_string(index=False))


babelon.add_command(example)
babelon.add_command(parse)
babelon.add_command(prepare_translation)
babelon.add_command(translate)
babelon.add_command(convert)
babelon.add_command(statistics_translation_profile_command)
