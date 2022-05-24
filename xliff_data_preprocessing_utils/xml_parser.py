import xmltodict
import csv

with open('tests/data/hpo_notes.xliff') as fd:
    doc = xmltodict.parse(fd.read())

csvfile = open("tests/data/parsed_data.csv", 'w', encoding='utf-8')
csvfile_writer = csv.writer(csvfile)

# ADD HEADER
csvfile_writer.writerow(
    ['source_language', 'translation_language', 'subject_id', 'predicate_id', 'source_value', 'translation_value'])
for trans_unit in doc['xliff']['file']['body']['trans-unit']:
    source_language = trans_unit['source']['@xml:lang']
    translation_language = trans_unit['target']['@xml:lang']
    # get subject_id and and format
    split_string_id_column = trans_unit['@id']
    get_subject_id = split_string_id_column[0: 10]
    subject_id = get_subject_id.replace("_", ":")
    # get predicate_id and format
    get_predicate_id = split_string_id_column[11: 21]
    if get_predicate_id == 'label':
        predicate_id = get_predicate_id.replace('label', 'rdfs:label')
    elif get_predicate_id == 'definition':
        predicate_id = get_predicate_id.replace('definition', 'IAO:0000115')
    elif get_predicate_id == 'synonyms':
        predicate_id = get_predicate_id.replace('synonyms', 'oboInOwl:exactSynonym')
    source_value = trans_unit['source']['#text']
    translational_value = trans_unit['target']['#text']
    csv_line = [source_language, translation_language, subject_id, predicate_id, source_value, translational_value]
    csvfile_writer.writerow(csv_line)


