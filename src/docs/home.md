# BABELON - A simple standard for managing ontology translations and language profiles

BABELON is simple standard for managing ontology translations and language profiles. Profiles are managed a simple TSV files (for examples go to the [GitHub repo](https://github.com/matentzn/babelon)).
The goal of BABELON is to capture the minimum data required to enable the following use cases:

- Translate a profile into RDF to enable seamless integration of alternative language alongside the primary ones.
- Support all properties for translation, including labels, synonyms and definitions.
- Capture important metadata such as confidence and precision of translation.
- Enable cross-language editing. For example:
  - Notify language profile maintainers of new terms or changed labels
  - Notify the core ontology teams of changes to translations, with a potential to suggest updating ones own annotations or adding new synonyms.
