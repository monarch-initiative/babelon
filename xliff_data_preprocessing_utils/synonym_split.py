import pandas as pd

df = pd.read_csv("../tests/data/parsed_data.tsv", sep='\t')

output_df = df[0:0]

for index, row in df.iterrows():
    if row.predicate_id == 'oboInOwl:exactSynonym':
        word_list = row['source_value'].split('#')
        word_list.remove('')
        temp_row = row.copy()
        if len(word_list) > 1:
            for each_word in word_list:
                temp_row.source_value = each_word
                temp_row.translation_value = each_word
                output_df = output_df.append(temp_row.to_dict(), ignore_index=True)

        else:
            temp_row.source_value = word_list[0]
            temp_row.translation_value = temp_row.translation_value.replace('#', '')
            output_df = output_df.append(temp_row.to_dict(), ignore_index=True)

    else:
        output_df = output_df.append(row.to_dict(), ignore_index=True)

output_df.to_csv("../tests/data/parsed_data.tsv", sep="\t", index=False)
