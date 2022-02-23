import click


@click.command()
@click.option("--input", "-i", "in_file", required=True,
              help="Path to csv file to be processed.",
              type=click.Path(exists=True, dir_okay=False, readable=True))
@click.option("--output-file", "-o", default="./output.xlsx",
              help="Path to excel file to store the result.",
              type=click.Path(dir_okay=False))
def process(in_file, out_file):
    """ Processes the input file IN and stores the result to
    output file OUT.
    """
    input = read_csv(in_file)
    output = process_csv(input)
    write_excel(output, out_file)


if __name__ == "__main__":
    process()
