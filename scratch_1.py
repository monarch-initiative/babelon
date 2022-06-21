from xliff_data_preprocessing_utils.xmlParser import XMLParser
import os


parser = XMLParser(input_file_path=os.getcwd() + r'/tests/data/hpo_notes.xliff', output_file_path=os.getcwd() + r'/tests/data/output_data.tsv')
parser.xml_to_tsv()
parser.synonym_split()
