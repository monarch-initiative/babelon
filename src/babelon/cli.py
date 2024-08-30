"""Command line interface for Babelon."""

import logging
import os
import sys
from pathlib import Path
from typing import TextIO

import click
import pandas as pd
from oaklib import get_adapter
from oaklib.datamodels.vocabulary import IS_A

from babelon.babelon_io import convert_file, parse_file
from babelon.translate import prepare_translation_for_ontology, translate_profile
from babelon.translation_profile import statistics_translation_profile
from babelon.utils import (
    drop_unknown_columns_babelon,
    sort_babelon,
    generate_translation_units,
    assemble_xliff_file,
)

info_log = logging.getLogger()
# Click input options common across commands
input_argument = click.argument("input", required=False, type=click.Path())

multiple_inputs_argument = click.argument("inputs", nargs=-1, required=False, type=click.Path())

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
sort_table_option = click.option(
    "--sort-tables",
    type=bool,
    default=True,
    help="If true, all output tables are sorted before written.",
)
drop_unknown_column_option = click.option(
    "--drop-unknown-columns",
    type=bool,
    default=False,
    help="If true, columns that are not specified as part of the babelon format are dropped.",
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
@click.option("-q", "--quiet", type=bool, is_flag=True, default=False)
def babelon(verbose=1, quiet=False) -> None:
    """Command Line Interface for the main method for Babelon.

    Args:
        verbose (int, optional): Verbose flag.
        quiet (bool, optional): Queit Flag.
    """
    if verbose > 2:
        info_log.setLevel(level=logging.INFO)
    elif verbose == 2:
        info_log.setLevel(level=logging.WARNING)
    elif verbose == 1:
        info_log.setLevel(level=logging.DEBUG)
    else:
        info_log.setLevel(level=logging.WARNING)

    if quiet:
        info_log.setLevel(level=logging.ERROR)


# Input and metadata would be files (file paths). Check if exists.
# @main.command()
@click.command("parse")
@input_argument
# @input_format_option
@output_option
def parse(input, output):
    """Parse a file in one of the supported formats (such as obographs) into a Babelon TSV file."""
    parse_file(input_path=input, output_path=output)


@click.command("convert")
@input_argument
@click.option(
    "--drop-unknown-columns",
    type=bool,
    default=True,
    help="If true, columns that are not specified as part of the babelon format are dropped.",
)
@output_option
@output_format_option
def convert(input: str, drop_unknown_columns: bool, output: TextIO, output_format: str):
    """Convert a Babelon file into a different format.

    Example:
        babelon convert my.babelon.tsv --output-format owl --output my.babelon.owl --drop-unknown-columns true
    """  # noqa: DAR101
    convert_file(
        input_path=input,
        output=output,
        drop_unknown_columns=drop_unknown_columns,
        output_format=output_format,
    )


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
    """Translate a babelon TSV file.

    Example:
        export OPENAI_API_KEY="sk-FILLINBEFORERUN"
            babelon translate my.babelon.tsv -o my.babelon-translated.tsv
    """  # noqa: DAR101
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
@click.option(
    "--output-source-changed",
    type=click.Path(),
    help="Path to file where you want to write records where the source has change the value.",
)
@click.option(
    "--output-not-translated",
    type=click.Path(),
    help="Path to file where you want to write records where a value is not yet translated.",
)
@click.option(
    "--include-not-translated",
    type=bool,
    default=False,
    help="If true, values that are not translated are included in the output.",
)
@click.option(
    "--update-translation-status",
    type=bool,
    default=True,
    help="If true, the translation status is changed to CANDIDATE if a source value has changed.",
)
@drop_unknown_column_option
@sort_table_option
@output_option
def prepare_translation(
    input,
    oak_adapter,
    language_code,
    term_list,
    field,
    output_source_changed,
    output_not_translated,
    include_not_translated,
    update_translation_status,
    drop_unknown_columns,
    sort_tables,
    output,
):
    """Prepare a babelon TSV file based on an ontology.

    Example:
        babelon prepare-translation my.babelon.tsv \
        --oak-adapter pronto:myont.obo \
        --language-code de \
        --field rdfs:label --field IAO:0000115 \
        --output-source-changed tests/tmp/example-source-changed.babelon.tsv \
        --output-not-translated tests/tmp/example-not-translated.babelon.tsv \
        --include-not-translated false \
        --update-translation-status true \
        -o my.babelon-preprocessed.tsv
    """  # noqa: DAR101
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

    df_output_profile, df_output_source_changed, df_output_not_translated = (
        prepare_translation_for_ontology(
            ontology=ontology,
            language_code=language_code,
            df_babelon=df_babelon,
            terms=terms,
            fields=field,
            include_not_translated=include_not_translated,
            update_translation_status=update_translation_status,
        )
    )
    _sort_drop_write_df(df_output_profile, drop_unknown_columns, sort_tables, output)
    _sort_drop_write_df(
        df_output_source_changed, drop_unknown_columns, sort_tables, output_source_changed
    )
    _sort_drop_write_df(
        df_output_not_translated, drop_unknown_columns, sort_tables, output_not_translated
    )


def _sort_drop_write_df(
    df: pd.DataFrame, drop_unknown_cols: bool, sort_tables: bool, output_path: str
):
    if output_path:
        df_out = df.copy()
        if sort_tables:
            df_out = sort_babelon(df_out)
        if drop_unknown_cols:
            df_out = drop_unknown_columns_babelon(df_out)
        df_out.to_csv(output_path, sep="\t", index=False)


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


@click.command("merge")
@multiple_inputs_argument
@drop_unknown_column_option
@sort_table_option
@output_option
def merge(inputs, sort_tables, drop_unknown_columns, output):
    """Merge multiple babelon TSV files into one.

    Example:
        babelon merge my1.babelon.tsv my2.babelon.tsv -o my.babelon-merged.tsv \
          --drop-unknown-columns true --sort-tables true
    """  # noqa: DAR101
    df = pd.read_csv(inputs[0], sep="\t")

    # Loop through the rest of the input files and concatenate each DataFrame
    for input_file in inputs[1:]:
        df_temp = pd.read_csv(input_file, sep="\t")
        df = pd.concat([df, df_temp], axis=0, ignore_index=True)

    if sort_tables:
        df = sort_babelon(df)

    if drop_unknown_columns:
        df = drop_unknown_columns_babelon(df)

    if output:
        df.to_csv(output, sep="\t", index=False)
    else:
        click.echo(df.to_string(index=False))


@click.command("prepare-ontology-for-crowdin")
@click.option("--oak-adapter", type=str, help="Oak handle string.")
@click.option(
    "--top-level-term",
    multiple=True,
    type=str,
    help="Top level term in ontology of which to translate all descendants.",
)
@output_option
def prepare_ontology_for_crowdin(oak_adapter, top_level_term, output):
    """Merge multiple babelon TSV files into one.

    Example:
        babelon prepare-ontology-for-crowdin --oak-adapter simpleobo:hp-base.obo --top-level-term HP:0000001 -o hp-translation.xliff
    """  # noqa: DAR101
    adapter = get_adapter(oak_adapter)
    translation_units = list()

    for top_level_term in top_level_term:
        for term in adapter.descendants(top_level_term, predicates=[IS_A]):
            label = adapter.label(term)
            definition = adapter.definition(term)
            alias_map = adapter.entity_alias_map(term)
            synonyms = [v for p, vl in alias_map.items() if "oio:hasExactSynonym" == p for v in vl]
            xml = generate_translation_units(term, label, definition, synonyms)
            translation_units.extend(xml)

    xliff = assemble_xliff_file(translation_units)
    output.write(xliff)


@click.command("example")
@input_argument
def example(input):
    """Generate an example babelon file for the user.

    Example:
        babelon example my-example.babelon.tsv
    """  # noqa: DAR101
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
babelon.add_command(merge)
babelon.add_command(parse)
babelon.add_command(prepare_ontology_for_crowdin)
babelon.add_command(prepare_translation)
babelon.add_command(translate)
babelon.add_command(convert)
babelon.add_command(statistics_translation_profile_command)
