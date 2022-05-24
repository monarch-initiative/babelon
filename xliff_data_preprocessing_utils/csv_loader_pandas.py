from linkml_runtime.dumpers import json_dumper
from xliff_data_preprocessing_utils.babelon import Translation, Profile
import pandas as pd
import numpy as np
import json

parsed_data = pd.read_csv('../tests/data/parsed_data.csv')
hpo = []
for row in parsed_data.itertuples():
    data = Translation(subject_id=row.subject_id, predicate_id=row.predicate_id,
                       translation_value=row.translation_value, source_language=row.source_language,
                       translation_language=row.translation_language, source_value=row.source_value)
    hpo.append(data)

profile = Profile(hpo)
with open('../tests/data/parsed_data.json', 'w') as f:
    f.write(json_dumper.dumps(profile))
