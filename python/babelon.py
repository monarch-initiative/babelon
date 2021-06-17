# Auto generated from babelon.yaml by pythongen.py version: 0.9.0
# Generation date: 2021-06-17 11:44
# Schema: babelon
#
# id: https://w3id.org/babelon
# description: A schema for describing translations and language profiles for ontologies
# license: https://creativecommons.org/publicdomain/zero/1.0/

import dataclasses
import sys
import re
from jsonasobj2 import JsonObj
from typing import Optional, List, Union, Dict, ClassVar, Any
from dataclasses import dataclass
from linkml_runtime.linkml_model.meta import EnumDefinition, PermissibleValue, PvFormulaOptions

from linkml_runtime.utils.slot import Slot
from linkml_runtime.utils.metamodelcore import empty_list, empty_dict, bnode
from linkml_runtime.utils.yamlutils import YAMLRoot, extended_str, extended_float, extended_int
from linkml_runtime.utils.dataclass_extensions_376 import dataclasses_init_fn_with_kwargs
from linkml_runtime.utils.formatutils import camelcase, underscore, sfx
from linkml_runtime.utils.enumerations import EnumDefinitionImpl
from rdflib import Namespace, URIRef
from linkml_runtime.utils.curienamespace import CurieNamespace
from linkml_runtime.linkml_model.types import Double, String

metamodel_version = "1.7.0"

# Overwrite dataclasses _init_fn to add **kwargs in __init__
dataclasses._init_fn = dataclasses_init_fn_with_kwargs

# Namespaces
BABELON = CurieNamespace('babelon', 'https://w3id.org/babelon/')
LINKML = CurieNamespace('linkml', 'https://w3id.org/linkml/')
DEFAULT_ = BABELON


# Types

# Class references



@dataclass
class Translation(YAMLRoot):
    """
    Represents and individual translation
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = BABELON.Translation
    class_class_curie: ClassVar[str] = "babelon:Translation"
    class_name: ClassVar[str] = "translation"
    class_model_uri: ClassVar[URIRef] = BABELON.Translation

    subject_id: str = None
    predicate_id: str = None
    translation_value: str = None
    source_language: str = None
    translation_language: str = None
    translator: str = None
    translator_expertise: Union[str, "TranslatorExpertiseEnum"] = None
    source_value: Optional[str] = None
    source_version: Optional[str] = None
    translation_type: Optional[Union[str, "TranslationTypeEnum"]] = None
    translation_date: Optional[str] = None
    translation_confidence: Optional[float] = None
    translation_precision: Optional[Union[str, "TranslationPrecisionEnum"]] = None
    translation_status: Optional[Union[str, "TranslationStatusEnum"]] = None
    source: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self._is_empty(self.subject_id):
            self.MissingRequiredField("subject_id")
        if not isinstance(self.subject_id, str):
            self.subject_id = str(self.subject_id)

        if self._is_empty(self.predicate_id):
            self.MissingRequiredField("predicate_id")
        if not isinstance(self.predicate_id, str):
            self.predicate_id = str(self.predicate_id)

        if self._is_empty(self.translation_value):
            self.MissingRequiredField("translation_value")
        if not isinstance(self.translation_value, str):
            self.translation_value = str(self.translation_value)

        if self._is_empty(self.source_language):
            self.MissingRequiredField("source_language")
        if not isinstance(self.source_language, str):
            self.source_language = str(self.source_language)

        if self._is_empty(self.translation_language):
            self.MissingRequiredField("translation_language")
        if not isinstance(self.translation_language, str):
            self.translation_language = str(self.translation_language)

        if self._is_empty(self.translator):
            self.MissingRequiredField("translator")
        if not isinstance(self.translator, str):
            self.translator = str(self.translator)

        if self._is_empty(self.translator_expertise):
            self.MissingRequiredField("translator_expertise")
        if not isinstance(self.translator_expertise, TranslatorExpertiseEnum):
            self.translator_expertise = TranslatorExpertiseEnum(self.translator_expertise)

        if self.source_value is not None and not isinstance(self.source_value, str):
            self.source_value = str(self.source_value)

        if self.source_version is not None and not isinstance(self.source_version, str):
            self.source_version = str(self.source_version)

        if self.translation_type is not None and not isinstance(self.translation_type, TranslationTypeEnum):
            self.translation_type = TranslationTypeEnum(self.translation_type)

        if self.translation_date is not None and not isinstance(self.translation_date, str):
            self.translation_date = str(self.translation_date)

        if self.translation_confidence is not None and not isinstance(self.translation_confidence, float):
            self.translation_confidence = float(self.translation_confidence)

        if self.translation_precision is not None and not isinstance(self.translation_precision, TranslationPrecisionEnum):
            self.translation_precision = TranslationPrecisionEnum(self.translation_precision)

        if self.translation_status is not None and not isinstance(self.translation_status, TranslationStatusEnum):
            self.translation_status = TranslationStatusEnum(self.translation_status)

        if self.source is not None and not isinstance(self.source, str):
            self.source = str(self.source)

        super().__post_init__(**kwargs)


@dataclass
class Profile(YAMLRoot):
    """
    Represents a set of translation that together compose a language profile.
    """
    _inherited_slots: ClassVar[List[str]] = []

    class_class_uri: ClassVar[URIRef] = BABELON.Profile
    class_class_curie: ClassVar[str] = "babelon:Profile"
    class_name: ClassVar[str] = "profile"
    class_model_uri: ClassVar[URIRef] = BABELON.Profile

    translation_provider: Optional[str] = None

    def __post_init__(self, *_: List[str], **kwargs: Dict[str, Any]):
        if self.translation_provider is not None and not isinstance(self.translation_provider, str):
            self.translation_provider = str(self.translation_provider)

        super().__post_init__(**kwargs)


# Enumerations
class TranslatorExpertiseEnum(EnumDefinitionImpl):

    DOMAIN_EXPERT = PermissibleValue(text="DOMAIN_EXPERT",
                                                 description="The translator is an expert of the domain of the ontology, for example an expert in anatomy when translating terms from an anatomy ontology such as Uberon.")
    LAYPERSON = PermissibleValue(text="LAYPERSON",
                                         description="The translator is an interested lay person with no specific knowledge of the domain.")
    DOMAIN_STUDENT = PermissibleValue(text="DOMAIN_STUDENT",
                                                   description="The translator is a student of the domain of the ontology, for example a student of anatomy, when translating terms from an anatomy ontology such as Uberon.")
    PROFESSIONAL_TRANSLATOR = PermissibleValue(text="PROFESSIONAL_TRANSLATOR",
                                                                     description="The translator is a professional translator by trade.")
    ALGORITHM = PermissibleValue(text="ALGORITHM",
                                         description="The translator is a machine, not a person.")

    _defn = EnumDefinition(
        name="TranslatorExpertiseEnum",
    )

class TranslationStatusEnum(EnumDefinitionImpl):

    CANDIDATE = PermissibleValue(text="CANDIDATE",
                                         description="The translation has been suggested from an entity (algorithm, person) outside the core team managing the translation.")
    UNDER_REVIEW = PermissibleValue(text="UNDER_REVIEW",
                                               description="The translation has been suggested from an entity (algorithm, person) inside the core team managing the translation, but not yet officially ratified.")
    OFFICIAL = PermissibleValue(text="OFFICIAL",
                                       description="The translation has been accepted by the core team managing the language profile.")

    _defn = EnumDefinition(
        name="TranslationStatusEnum",
    )

class TranslationTypeEnum(EnumDefinitionImpl):

    TRANSLATION = PermissibleValue(text="TRANSLATION",
                                             description="The record corresponds to an actual translation of a source value into a translation value.")
    AUGMENTATION = PermissibleValue(text="AUGMENTATION",
                                               description="The record corresponds to an additional language specific terminological element without a corresponding element in the source language.")
    CORRECTION = PermissibleValue(text="CORRECTION",
                                           description="The record corresponds to a translation of a source value into a translation value, but rather than being an exact translation, it suggests a change to the original source value.")

    _defn = EnumDefinition(
        name="TranslationTypeEnum",
    )

class TranslationPrecisionEnum(EnumDefinitionImpl):

    EXACT = PermissibleValue(text="EXACT",
                                 description="The translation is exact.")
    BROADER = PermissibleValue(text="BROADER",
                                     description="The translation value has a somewhat broader meaning than the source value.")
    NARROWER = PermissibleValue(text="NARROWER",
                                       description="The translation value has a somewhat narrower meaning than the source value.")
    CLOSE = PermissibleValue(text="CLOSE",
                                 description="The translation value is close in meaning to the source value, but not exact.")

    _defn = EnumDefinition(
        name="TranslationPrecisionEnum",
    )

# Slots
class slots:
    pass

slots.predicate_id = Slot(uri=BABELON.predicate_id, name="predicate_id", curie=BABELON.curie('predicate_id'),
                   model_uri=BABELON.predicate_id, domain=None, range=Optional[str])

slots.translation_value = Slot(uri=BABELON.translation_value, name="translation_value", curie=BABELON.curie('translation_value'),
                   model_uri=BABELON.translation_value, domain=None, range=Optional[str])

slots.source_value = Slot(uri=BABELON.source_value, name="source_value", curie=BABELON.curie('source_value'),
                   model_uri=BABELON.source_value, domain=None, range=Optional[str])

slots.subject_id = Slot(uri=BABELON.subject_id, name="subject_id", curie=BABELON.curie('subject_id'),
                   model_uri=BABELON.subject_id, domain=None, range=Optional[str])

slots.source_language = Slot(uri=BABELON.source_language, name="source_language", curie=BABELON.curie('source_language'),
                   model_uri=BABELON.source_language, domain=None, range=Optional[str])

slots.translation_type = Slot(uri=BABELON.translation_type, name="translation_type", curie=BABELON.curie('translation_type'),
                   model_uri=BABELON.translation_type, domain=None, range=Optional[Union[str, "TranslationTypeEnum"]])

slots.translation_language = Slot(uri=BABELON.translation_language, name="translation_language", curie=BABELON.curie('translation_language'),
                   model_uri=BABELON.translation_language, domain=None, range=Optional[str])

slots.source = Slot(uri=BABELON.source, name="source", curie=BABELON.curie('source'),
                   model_uri=BABELON.source, domain=None, range=Optional[str])

slots.source_version = Slot(uri=BABELON.source_version, name="source_version", curie=BABELON.curie('source_version'),
                   model_uri=BABELON.source_version, domain=None, range=Optional[str])

slots.translator = Slot(uri=BABELON.translator, name="translator", curie=BABELON.curie('translator'),
                   model_uri=BABELON.translator, domain=None, range=Optional[str])

slots.translator_expertise = Slot(uri=BABELON.translator_expertise, name="translator_expertise", curie=BABELON.curie('translator_expertise'),
                   model_uri=BABELON.translator_expertise, domain=None, range=Optional[Union[str, "TranslatorExpertiseEnum"]])

slots.translation_date = Slot(uri=BABELON.translation_date, name="translation_date", curie=BABELON.curie('translation_date'),
                   model_uri=BABELON.translation_date, domain=None, range=Optional[str])

slots.translation_confidence = Slot(uri=BABELON.translation_confidence, name="translation_confidence", curie=BABELON.curie('translation_confidence'),
                   model_uri=BABELON.translation_confidence, domain=None, range=Optional[float])

slots.translation_precision = Slot(uri=BABELON.translation_precision, name="translation_precision", curie=BABELON.curie('translation_precision'),
                   model_uri=BABELON.translation_precision, domain=None, range=Optional[Union[str, "TranslationPrecisionEnum"]])

slots.translation_provider = Slot(uri=BABELON.translation_provider, name="translation_provider", curie=BABELON.curie('translation_provider'),
                   model_uri=BABELON.translation_provider, domain=None, range=Optional[str])

slots.translation_status = Slot(uri=BABELON.translation_status, name="translation_status", curie=BABELON.curie('translation_status'),
                   model_uri=BABELON.translation_status, domain=None, range=Optional[Union[str, "TranslationStatusEnum"]])

slots.translation_subject_id = Slot(uri=BABELON.subject_id, name="translation_subject_id", curie=BABELON.curie('subject_id'),
                   model_uri=BABELON.translation_subject_id, domain=Translation, range=str)

slots.translation_predicate_id = Slot(uri=BABELON.predicate_id, name="translation_predicate_id", curie=BABELON.curie('predicate_id'),
                   model_uri=BABELON.translation_predicate_id, domain=Translation, range=str)

slots.translation_source_language = Slot(uri=BABELON.source_language, name="translation_source_language", curie=BABELON.curie('source_language'),
                   model_uri=BABELON.translation_source_language, domain=Translation, range=str)

slots.translation_translation_language = Slot(uri=BABELON.translation_language, name="translation_translation_language", curie=BABELON.curie('translation_language'),
                   model_uri=BABELON.translation_translation_language, domain=Translation, range=str)

slots.translation_translation_value = Slot(uri=BABELON.translation_value, name="translation_translation_value", curie=BABELON.curie('translation_value'),
                   model_uri=BABELON.translation_translation_value, domain=Translation, range=str)

slots.translation_translator = Slot(uri=BABELON.translator, name="translation_translator", curie=BABELON.curie('translator'),
                   model_uri=BABELON.translation_translator, domain=Translation, range=str)

slots.translation_translator_expertise = Slot(uri=BABELON.translator_expertise, name="translation_translator_expertise", curie=BABELON.curie('translator_expertise'),
                   model_uri=BABELON.translation_translator_expertise, domain=Translation, range=Union[str, "TranslatorExpertiseEnum"])
