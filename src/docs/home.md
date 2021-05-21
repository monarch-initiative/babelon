# OBABEL - A simple standard for managing ontology translations and language profiles

OBABEL is simple standard for managing ontology translations and language profiles. Profiles are managed a simple TSV files, for example:

| source                                | source_version                                               | source_language | translation_language | subject_id | predicate_id     | source_value       | translation_value   | translator                            | translation_date | translation_confidence | translation_precision | translation_type |
|---------------------------------------|--------------------------------------------------------------|-----------------|----------------------|------------|------------------|--------------------|---------------------|---------------------------------------|------------------|------------------------|-----------------------|------------------|
| http://purl.obolibrary.org/obo/hp.owl | http://purl.obolibrary.org/obo/hp/releases/2021-04-13/hp.owl | en              | de                   | HP:0001945 | rdfs:label       | Fever              | Fieber              | https://orcid.org/0000-0002-1373-XXXX |       2021-05-21 |                   0.95 | exact                 | HumanCurated     |
| http://purl.obolibrary.org/obo/hp.owl | http://purl.obolibrary.org/obo/hp/releases/2021-04-13/hp.owl | en              | de                   | HP:0002615 | oio:exactSynonym | Low blood pressure | Niedriger Blutdruck | https://orcid.org/0000-0002-1373-XXXX |       2021-05-21 |                    0.9 | exact                 | HumanCurated     |

The goal of OBABEL is to capture the minimum data required to enable the following use cases:

- Translate a profile into RDF to enable seamless integration of alternative language alongside the primary ones.
- Support all properties for translation, including labels, synonyms and definitions.
- Capture important metadata such as confidence and precision of translation.
- Enable cross-language editing. For example:
  - Notify language profile maintainers of new terms or changed labels
  - Notify the core ontology teams of changes to translations, with a potential to suggest updating ones own annotations or adding new synonyms.

