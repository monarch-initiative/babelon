[![DOI](https://zenodo.org/badge/369423393.svg)](https://zenodo.org/badge/latestdoi/369423393)

# Babelon - A simple standard for managing ontology translations and language profiles

Editors:
- @matentzn
- @LLTommy
- @mellybelly
- @drseb
- Anyone that wants to be on here.

[Provisional documentation here.](https://monarch-initiative.github.io/babelon/)

Babelon is simple standard for managing ontology translations and language profiles. Profiles are managed a simple TSV files, for example:

| source                                | source_version                                               | source_language | translation_language | subject_id | predicate_id     | source_value       | translation_value   | translator                            | translation_date | translation_confidence | translation_precision | translation_type |
|---------------------------------------|--------------------------------------------------------------|-----------------|----------------------|------------|------------------|--------------------|---------------------|---------------------------------------|------------------|------------------------|-----------------------|------------------|
| http://purl.obolibrary.org/obo/hp.owl | http://purl.obolibrary.org/obo/hp/releases/2021-04-13/hp.owl | en              | de                   | HP:0001945 | rdfs:label       | Fever              | Fieber              | https://orcid.org/0000-0002-1373-XXXX |       2021-05-21 |                   0.95 | exact                 | HumanCurated     |
| http://purl.obolibrary.org/obo/hp.owl | http://purl.obolibrary.org/obo/hp/releases/2021-04-13/hp.owl | en              | de                   | HP:0002615 | oio:exactSynonym | Low blood pressure | Niedriger Blutdruck | https://orcid.org/0000-0002-1373-XXXX |       2021-05-21 |                    0.9 | exact                 | HumanCurated     |

The goal of Babelon is to capture the minimum data required to enable the following use cases:

- Translate a profile into RDF to enable seamless integration of alternative language alongside the primary ones.
- Support all properties for translation, including labels, synonyms and definitions.
- Capture important metadata such as confidence and precision of translation.
- Enable cross-language editing. For example:
  - Notify language profile maintainers of new terms or changed labels
  - Notify the core ontology teams of changes to translations, with a potential to suggest updating ones own annotations or adding new synonyms.


As a first use case for the format, we see to capture the French language translations of the Human Phenotype Ontology by the Orphanet team and use them to provide versioned language profiles of HPO.

### Editors

```
# in new environment
pip install poetry
poetry install
make translations
```
# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [monarch-project-template](https://github.com/monarch-initiative/monarch-project-template) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).
