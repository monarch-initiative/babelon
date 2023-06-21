"""babelon.io."""
from babelon.parsers.xliff import XliffParser


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
        parser = XliffParser(input_file_path=input_path, output_file_path=output_path)
        parser.xml_to_tsv()
        parser.synonym_split()
    else:
        raise ValueError(f"File type: {file_extension} not supported.")
