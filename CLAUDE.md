# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Babelon is a TSV-based standard (and reference Python implementation) for managing ontology translations and language profiles. The schema is authored in LinkML; the Python data classes, JSON Schema, OWL, ShEx, GraphQL, and Markdown docs are all generated artifacts.

## Common commands

Install / setup:
```
pip install poetry
poetry install
```

Run a single CLI command:
```
poetry run babelon <subcommand> ...
```
Top-level CLI subcommands (see `src/babelon/cli.py`): `parse`, `convert`, `translate`, `prepare-translation`, `prepare-ontology-for-crowdin`, `statistics`, `merge`, `example`.

Tests (pytest via tox):
```
poetry run tox -e py            # full suite
poetry run pytest tests/test_translate.py::test_name   # single test
```

Lint / format (matches CI in `.github/workflows/qc.yml`):
```
poetry run tox -e lint          # black --check + ruff check
poetry run tox -e lint-fix      # black + ruff --fix
poetry run tox -e flake8
poetry run tox -e mypy
```

Regenerate schema-derived artifacts after editing `src/babelon/schema/babelon.yaml`:
```
make gen                        # writes target/, then `stage` copies to top-level dirs
```
Output directories `csv/`, `graphql/`, `jsonschema/`, `owl/`, `shex/`, `python/`, `docs/` are generated from the LinkML schema — do not hand-edit.

End-to-end CLI smoke test:
```
make cli_test
```

## Architecture

The schema is the source of truth. `src/babelon/schema/babelon.yaml` (LinkML) defines `TranslationProfile` / `Translation` and the controlled-vocabulary enums (`translation_type`, `translation_status`, `translation_precision`, `translator_expertise`). From it the Makefile generates `src/babelon/dataclasses.py` (excluded from black/ruff/flake8/mypy — never lint or hand-edit it) and the artifacts under `target/`, `csv/`, `owl/`, `jsonschema/`, etc.

Core Python modules under `src/babelon/`:

- `cli.py` — Click entry point (`babelon = "babelon.cli:babelon"` in `pyproject.toml`). Each subcommand is thin glue over the modules below.
- `babelon_io.py` — Parse/convert pipeline. Uses `linkml_runtime` (`TSVLoader`, `JSONDumper`, `rdflib_dumper`) and dispatches to format-specific parsers; the loaded profile can be serialized back to TSV, JSON, or OWL/RDF.
- `parsers/xliff.py` — XLIFF → Babelon TSV ingestion.
- `translate.py` — `Translator` base class with concrete backends: `OpenAITranslator` (via the `llm` library), `DeepLTranslator`, and `AnthropicTranslator` (Claude, via the `anthropic` SDK). The base class exposes `translate` (one text) and `translate_batch` (many at once, defaulting to a loop over `translate`); backends that can translate many texts per request override `translate_batch` and `batch_size`, which is how the Anthropic backend keeps a whole-ontology run to hundreds of requests rather than tens of thousands. `translate_profile` and `prepare_translation_for_ontology` orchestrate batch translation and pre-population of rows from an ontology.
- `translation_profile.py` — Pandas-based statistics (`tabulate`-printed grouped counts).
- `utils.py` — `BabelonDataFrame`, sort/dedup helpers, XLIFF assembly, column policing (drop unknown columns vs. schema slots), file-extension dispatch.
- `constants.py` — Path to the bundled `babelon.yaml` schema (loaded via `importlib.resources`).

`prepare-translation` uses OAK (`oaklib.get_adapter`) to read an ontology and seed missing translation rows; `translate` then fills `translation_value` via an LLM/DeepL backend. The TSV round-trips through the LinkML schema, so adding a new column generally means editing the schema and regenerating `dataclasses.py`.

## Conventions specific to this repo

- Python 3.11 only (set in `pyproject.toml` and CI matrix).
- Black line length 100; ruff and flake8 configured in `tox.ini` (max line 120, with `T201`/`S408`/`S405`/`S314`/`S318` etc. ignored — `print` is allowed).
- `src/babelon/dataclasses.py` is generated; all lint/type-check configs explicitly exclude it. Regenerate via `make gen-python` rather than editing.
- User-facing CLI output uses `print`, not `logging.warning` (see commit `17fbb3d`).
- The bundled schema is read with `importlib.resources` (see commit `38d8169`); do not switch to `importlib_resources` or filesystem paths.
