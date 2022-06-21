

def parse_file(
    input_path: str,
    output: TextIO,
    input_format: Optional[str] = None,
) -> None:
    """Parse a Babelon metadata file and write to a table.

    :param input_path: The path to the input file in one of the legal formats, eg obographs, aligmentapi-xml
    :param output: The path to the output file.
    :param input_format: The string denoting the input format.
    """
    
    if input_format=="xliff":
        parser = XliffParser()...
    
    parser.write()
