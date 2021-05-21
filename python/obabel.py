# Auto generated from obabel.yaml by pythongen.py version: 0.9.0
# Generation date: 2021-05-21 10:26
# Schema: obabel
#
# id: https://w3id.org/obabel
# description: A schema for describing translations and language profiles for ontologies
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml.utils.slot import Slot
from linkml.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml.utils.formatutils import camelcase, underscore, sfx
from linkml.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml.utils.curienamespace import CurieNamespace
from linkml_model.types import Double, String

metamodel_version = "1.7.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
OBABEL = CurieNamespace('obabel', 'https://w3id.org/obabel/')
DEFAULT_ = OBABEL


# Types

# Class references



@dataclass
class Translation(YAMLRoot):
    """
    Represents and individual translation
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OBABEL.Translation
    class_class_curie: ClassVar[str] = "obabel:Translation"
    class_name: ClassVar[str] = "translation"
    class_model_uri: ClassVar[URIRef] = OBABEL.Translation

    predicate_id: Optional[str] = None
    translation_value: Optional[str] = None
    source_value: Optional[str] = None
    source_language: Optional[str] = None
    translation_language: Optional[str] = None
    source_version: Optional[str] = None
    translator: Optional[str] = None
    translation_date: Optional[str] = None
    translation_confidence: Optional[float] = None
    translation_precision: Optional[str] = None
    translation_type: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.predicate_id is not None and not isinstance(self.predicate_id, str):
            self.predicate_id = str(self.predicate_id)

        if self.translation_value is not None and not isinstance(self.translation_value, str):
            self.translation_value = str(self.translation_value)

        if self.source_value is not None and not isinstance(self.source_value, str):
            self.source_value = str(self.source_value)

        if self.source_language is not None and not isinstance(self.source_language, str):
            self.source_language = str(self.source_language)

        if self.translation_language is not None and not isinstance(self.translation_language, str):
            self.translation_language = str(self.translation_language)

        if self.source_version is not None and not isinstance(self.source_version, str):
            self.source_version = str(self.source_version)

        if self.translator is not None and not isinstance(self.translator, str):
            self.translator = str(self.translator)

        if self.translation_date is not None and not isinstance(self.translation_date, str):
            self.translation_date = str(self.translation_date)

        if self.translation_confidence is not None and not isinstance(self.translation_confidence, float):
            self.translation_confidence = float(self.translation_confidence)

        if self.translation_precision is not None and not isinstance(self.translation_precision, str):
            self.translation_precision = str(self.translation_precision)

        if self.translation_type is not None and not isinstance(self.translation_type, str):
            self.translation_type = str(self.translation_type)

        if self.source is not None and not isinstance(self.source, str):
            self.source = str(self.source)

        super().__post_init__(**kwargs)


@dataclass
class Profile(YAMLRoot):
    """
    Represents a set of translation that together compose a language profile.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = OBABEL.Profile
    class_class_curie: ClassVar[str] = "obabel:Profile"
    class_name: ClassVar[str] = "profile"
    class_model_uri: ClassVar[URIRef] = OBABEL.Profile

    translation_provider: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.translation_provider is not None and not isinstance(self.translation_provider, str):
            self.translation_provider = str(self.translation_provider)

        super().__post_init__(**kwargs)


# Enumerations


# Slots
class slots:
    pass

slots.predicate_id = Slot(uri=OBABEL.predicate_id, name="predicate_id", curie=OBABEL.curie('predicate_id'),
                   model_uri=OBABEL.predicate_id, domain=None, range=Optional[str])

slots.translation_value = Slot(uri=OBABEL.translation_value, name="translation_value", curie=OBABEL.curie('translation_value'),
                   model_uri=OBABEL.translation_value, domain=None, range=Optional[str])

slots.source_value = Slot(uri=OBABEL.source_value, name="source_value", curie=OBABEL.curie('source_value'),
                   model_uri=OBABEL.source_value, domain=None, range=Optional[str])

slots.source_language = Slot(uri=OBABEL.source_language, name="source_language", curie=OBABEL.curie('source_language'),
                   model_uri=OBABEL.source_language, domain=None, range=Optional[str])

slots.translation_language = Slot(uri=OBABEL.translation_language, name="translation_language", curie=OBABEL.curie('translation_language'),
                   model_uri=OBABEL.translation_language, domain=None, range=Optional[str])

slots.source = Slot(uri=OBABEL.source, name="source", curie=OBABEL.curie('source'),
                   model_uri=OBABEL.source, domain=None, range=Optional[str])

slots.source_version = Slot(uri=OBABEL.source_version, name="source_version", curie=OBABEL.curie('source_version'),
                   model_uri=OBABEL.source_version, domain=None, range=Optional[str])

slots.translator = Slot(uri=OBABEL.translator, name="translator", curie=OBABEL.curie('translator'),
                   model_uri=OBABEL.translator, domain=None, range=Optional[str])

slots.translation_type = Slot(uri=OBABEL.translation_type, name="translation_type", curie=OBABEL.curie('translation_type'),
                   model_uri=OBABEL.translation_type, domain=None, range=Optional[str])

slots.translation_date = Slot(uri=OBABEL.translation_date, name="translation_date", curie=OBABEL.curie('translation_date'),
                   model_uri=OBABEL.translation_date, domain=None, range=Optional[str])

slots.translation_confidence = Slot(uri=OBABEL.translation_confidence, name="translation_confidence", curie=OBABEL.curie('translation_confidence'),
                   model_uri=OBABEL.translation_confidence, domain=None, range=Optional[float])

slots.translation_precision = Slot(uri=OBABEL.translation_precision, name="translation_precision", curie=OBABEL.curie('translation_precision'),
                   model_uri=OBABEL.translation_precision, domain=None, range=Optional[str])

slots.translation_provider = Slot(uri=OBABEL.translation_provider, name="translation_provider", curie=OBABEL.curie('translation_provider'),
                   model_uri=OBABEL.translation_provider, domain=None, range=Optional[str])
