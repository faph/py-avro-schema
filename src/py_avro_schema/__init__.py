"""
Generate Avro schemas for any Python (nested) dataclass or Pydantic model.

First, define a Python data structure like this::

   >>> from typing import List
   >>> import dataclasses

   >>> @dataclasses.dataclass
   ... class Person:
   ...     name: str = ""
   ...
   >>> @dataclasses.dataclass
   ... class Ship:
   ...     name: str = ""
   ...     crew: List[Person] = dataclasses.field(default_factory=list)
   ...

Pydantic models can also be used instead of dataclasses. "Normal" Python classes cannot be used to construct Avro record
schemas because there is no way to determine the attributes and their types from the class definition.

Then, generate the corresponding Avro schema like this::

   >>> import py_avro_schema as pas
   >>> pas.generate(Ship, namespace="my_package")
   b'{"type":"record","name":"Ship","fields":[{"name":"name","type":"string","default":""},...'

The ``options`` argument supports the following :class:`Option` enum-values:

===================== ==================================================================================================
Option                Description
===================== ==================================================================================================
INT_32                Use "int" schemas instead of "long" schemas
FLOAT_32              Use "float" schemas instead of "double" schemas
MILLISECONDS          Use milliseconds instead of microseconds precision for (date)time schemas
DEFAULTS_MANDATORY    Mandate default values to be specified for all dataclass fields. This option may be used to
                      enforce default values on Avro record fields to support schema evoluation/resolution.
LOGICAL_JSON_STRING   Model Dict[str, Any] fields as string schemas instead of byte schemas (with logical type "json",
                      to support JSON serialization inside Avro).
NO_AUTO_NAMESPACE     Do not populate namespaces automatically based on the package a Python class is defined in.
AUTO_NAMESPACE_MODULE Automatically populate namespaces using full (dotted) module names instead of top-level package
                      names.
JSON_INDENT_2         Format JSON data using 2 spaces indentation
JSON_SORT_KEYS        Sort keys in JSON data
JSON_APPEND_NEWLINE   Append a newline character at the end of the JSON data
===================== ==================================================================================================

"""

import functools
from typing import Optional, Type

import orjson

from py_avro_schema._schemas import JSON_OPTIONS, Option, schema
from py_avro_schema._typing import DecimalType

__all__ = [
    "generate",
    "DecimalType",
    "Option",
]


@functools.lru_cache(maxsize=None)
def generate(
    py_type: Type,
    *,
    namespace: Optional[str] = None,
    options: Option = Option(0),
) -> bytes:
    """
    Return an Avro schema as a JSON-formatted bytestring for a given Python class or instance

    This function is cached and can be called repeatedly with the same arguments without any performance penalty.

    :param py_type:    The Python class to generate a schema for
    :param namespace:  The Avro namespace to add to schemas
    :param options:    Option flags, specify multiple values like this: ``Option.INT_32 | Option.FLOAT_32``
    """
    schema_dict = schema(py_type, namespace=namespace, options=options)
    json_options = 0
    for opt in JSON_OPTIONS:
        if opt in options:
            json_options |= opt.value
    schema_json = orjson.dumps(schema_dict, option=json_options)
    return schema_json
