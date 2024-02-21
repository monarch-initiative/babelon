"""babelon.io."""

from babelon.parsers.xliff import xliff_path_to_babelon


def parse_file(input_path: str, output_path: str) -> None:
    """Parse a Babelon metadata file and write to a table.

    Args:
        input_path (str): The path to the input file in one of the legal formats, eg obographs, aligmentapi-xml
        output_path (str): The path to the output file.

    Raises:
        ValueError: [description]
    """
    file_extension = input_path.split(".")[-1]
    if file_extension == "xliff":
        df_babelon, df_synonym = xliff_path_to_babelon(input_file_path=input_path)
        output_path_synonym = str(output_path).replace(".babelon.", ".synonyms.")
        df_babelon.to_csv(output_path, sep="\t", index=False)
        df_synonym.to_csv(output_path_synonym, sep="\t", index=False)
    else:
        raise ValueError(f"File type: {file_extension} not supported.")
