"""babelon.io."""

import json
import logging
import tempfile
from typing import Callable, Dict, Optional, TextIO, Tuple

from jsonasobj2 import JsonObj
from linkml_runtime.dumpers import JSONDumper, rdflib_dumper
from linkml_runtime.linkml_model.meta import SlotDefinitionName
from linkml_runtime.loaders.tsv_loader import TSVLoader
from linkml_runtime.utils.schemaview import SchemaView
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF

from babelon.constants import SCHEMA_YAML
from babelon.parsers.xliff import xliff_path_to_babelon
from babelon.utils import BabelonDataFrame, _get_file_extension, parse_babelon, raise_for_bad_path


def parse_file(input_path: str, output_path: TextIO) -> None:
    """Parse a Babelon metadata file and write to a table.

    Args:
        input_path (str): The path to the input file in one of the legal formats, eg obographs, aligmentapi-xml
        output_path (TextIO): The path to the output file.

    Raises:
        ValueError: [description]
    """
    file_extension = input_path.split(".")[-1]
    if file_extension == "xliff":
        df_babelon, df_synonym = xliff_path_to_babelon(input_file_path=input_path)
        output_path_synonym = str(output_path.name).replace(".babelon.", ".synonyms.")
        df_babelon.to_csv(output_path, sep="\t", index=False)
        df_synonym.to_csv(output_path_synonym, sep="\t", index=False)
    else:
        raise ValueError(f"File type: {file_extension} not supported.")


def convert_file(
    input_path: str,
    output: TextIO,
    drop_unknown_columns: bool = True,
    output_format: Optional[str] = None,
) -> None:
    """Convert a file from one format to another.

    :param input_path: The path to the input babelon tsv file
    :param output: The path to the output file. If none is given, will default to using stdout.
    :param drop_unknown_columns: If true, columns unknown to Babelon format are dropped prior to processing.
    :param output_format: The format to which the SSSOM TSV should be converted.
    """
    raise_for_bad_path(input_path)
    babelon_df: BabelonDataFrame = parse_babelon(
        input_path, drop_unknown_columns=drop_unknown_columns
    )
    write_func, fileformat = _get_writer_function(output_format=output_format, output=output)

    # We need to silence logging for the LinkML parts as it is way too verbose
    original_level = logging.getLogger().getEffectiveLevel()
    logging.getLogger().setLevel(logging.CRITICAL)

    write_func(babelon_df, output, serialisation=fileformat)  # type:ignore

    # Restore the original logging level
    logging.getLogger().setLevel(original_level)


DFWriter = Callable[[BabelonDataFrame, TextIO], None]

RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
BABELON_URI_PREFIX = "https://w3id.org/babelon/"
URI_BABELON_TRANSLATIONS = f"{BABELON_URI_PREFIX}translations"


def to_owl_graph(bdf: BabelonDataFrame) -> Graph:
    """Convert a mapping set dataframe to OWL in an RDF graph."""
    graph = to_rdf_graph(bdf=bdf)

    for _s, _p, o in graph.triples((None, URIRef(URI_BABELON_TRANSLATIONS), None)):
        graph.add((o, URIRef(RDF_TYPE), OWL.Axiom))

    for axiom in graph.subjects(RDF.type, OWL.Axiom):
        for p in graph.objects(subject=axiom, predicate=OWL.annotatedProperty):
            for s in graph.objects(subject=axiom, predicate=OWL.annotatedSource):
                for o in graph.objects(subject=axiom, predicate=OWL.annotatedTarget):
                    graph.add((s, p, o))

    sparql_prefixes = """
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX IAO: <http://purl.obolibrary.org/obo/IAO_>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX babelon: <https://w3id.org/babelon/>

"""
    queries = []

    queries.append(
        sparql_prefixes
        + """
        DELETE {
          ?o rdf:type babelon:Profile .
        }
        INSERT {
          ?o rdf:type owl:Ontology .
        }
        WHERE {
         ?o rdf:type babelon:Profile .
        }
        """
    )

    queries.append(
        sparql_prefixes
        + """
    DELETE {
      ?o babelon:translations ?translations .
    }
    WHERE {
     ?o babelon:translations ?translations .
    }
    """
    )

    # Add annotation assertions to known properties
    queries.append(
        sparql_prefixes
        + """
        INSERT {
            ?property rdf:type owl:AnnotationProperty .
        }
        WHERE {
            VALUES ?property { <http://purl.obolibrary.org/obo/IAO_0000115> oboInOwl:hasExactSynonym }
            ?ax a owl:Axiom ;
            owl:annotatedProperty ?property .
        }
        """
    )

    queries.append(
        sparql_prefixes
        + """
            INSERT {
                ?p rdf:type owl:AnnotationProperty .
            }
            WHERE {
                ?o a owl:Axiom ;
                ?p ?v .
                FILTER(?p!=rdf:type && ?p!=owl:annotatedProperty && ?p!=owl:annotatedTarget && ?p!=owl:annotatedSource)
            }
        """
    )

    queries.append(
        sparql_prefixes
        + """
            # Turn language in annotation to LANG(string), i.e abc@fr

            DELETE {
              ?ax owl:annotatedTarget ?translation .
              ?term ?property ?translation .
            }

            INSERT {
              ?term ?property ?translation_lang .
              ?ax owl:annotatedTarget ?translation_lang .
            }

            WHERE {

              ?ax a owl:Axiom ;
                owl:annotatedProperty ?property ;
                owl:annotatedSource ?term ;
                owl:annotatedTarget ?translation ;
                babelon:source_language ?source_language ;
                babelon:source_value ?source_value ;
                babelon:translation_language ?language_tag .

              OPTIONAL {
                ?ax babelon:translation_status ?translation_status .
              }

              OPTIONAL {
                ?term ?property ?translation .
              }

              BIND(STRLANG(STR(?translation),STR(?language_tag)) as ?translation_lang)
            }
                """
    )

    for query in queries:
        graph.update(query)

    return graph


def to_babelon_linkml_document(bdf: BabelonDataFrame):
    """Load a LinkML YAML representation from a BabelonDataFrame."""
    df = bdf.df

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
        df.to_csv(
            temp_file, sep="\t", index=False
        )  # You can use index=False to exclude the index from the CSV
        temp_file_path = temp_file.name

    sv = SchemaView(SCHEMA_YAML)
    from babelon.dataclasses import Profile

    if df.empty:
        return Profile()
    else:
        babelon_translation = TSVLoader().loads(
            input=temp_file_path,
            target_class=Profile,
            index_slot=SlotDefinitionName("translations"),
            schemaview=sv,
        )
    return babelon_translation


def to_rdf_graph(bdf: BabelonDataFrame) -> Graph:
    """Convert a mapping set dataframe to an RDF graph."""
    doc = to_babelon_linkml_document(bdf)
    graph = rdflib_dumper.as_rdf_graph(
        element=doc,
        schemaview=SchemaView(SCHEMA_YAML),
        prefix_map=bdf.converter.bimap,
    )
    return graph


def to_json(bdf: BabelonDataFrame) -> JsonObj:
    """Convert a mapping set dataframe to a JSON object."""
    doc = to_babelon_linkml_document(bdf)
    data = JSONDumper().dumps(doc, inject_type=False)
    json_obj = json.loads(data)
    return json_obj


def write_json(bdf: BabelonDataFrame, output: TextIO, serialisation="json") -> None:
    """Write a mapping set dataframe to the file as JSON.

    Args:
        bdf (BabelonDataFrame): The path to the input file in one of the legal formats, eg obographs, aligmentapi-xml
        output (TextIO): The path or stream of the output.
        serialisation (str): the target serialisation (must be 'json')

    Raises:
        ValueError: [description]
    """
    if serialisation == "json":
        data = to_json(bdf)
        json.dump(data, output, indent=2)
    else:
        raise ValueError(f"Unknown json format: {serialisation}, currently only json supported")


def write_owl(bdf: BabelonDataFrame, output: TextIO, serialisation="owl") -> None:
    """Write a mapping set dataframe to the file as OWL.

    Args:
        bdf (BabelonDataFrame): The path to the input file in one of the legal formats, eg obographs, aligmentapi-xml
        output (TextIO): The path or stream of the output.
        serialisation (str): the target serialisation (must be 'json')

    Raises:
        ValueError: [description]
    """
    if serialisation == "owl":
        graph = to_owl_graph(bdf)
        t = graph.serialize(format="ttl", encoding="utf-8")
        print(t.decode(), file=output)
    else:
        raise ValueError(f"Unknown json format: {serialisation}, currently only OWL supported")


def _get_writer_function(
    *, output_format: Optional[str] = None, output: TextIO
) -> Tuple[DFWriter, str]:
    """
    Get appropriate writer function based on file format.

    Args:
        output_format: The format of the file to be written
        output: The handle of the file to be written (TextIO)

    Raises:
        ValueError: If the provided file path is not a valid file or URL.

    """
    func: DFWriter
    tag: str

    if output_format is None:
        output_format = _get_file_extension(output)
    if output_format not in WRITER_FUNCTIONS:
        raise ValueError(f"Unknown output format: {output_format}")

    func, tag = WRITER_FUNCTIONS[output_format]
    return func, tag or output_format


# Adjust WRITER_FUNCTIONS to map to tuples of (function, tag)
WRITER_FUNCTIONS: Dict[str, Tuple[Callable, str]] = {
    "owl": (write_owl, "owl"),
    "json": (write_json, "json"),
}
