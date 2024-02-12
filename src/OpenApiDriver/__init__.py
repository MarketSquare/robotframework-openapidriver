"""
The OpenApiDriver package is intended to be used as a Robot Framework library.
The following classes and constants are exposed to be used by the library user:
- OpenApiDriver: The class to be used as a Library in the *** Settings *** section
- IdDependency, IdReference, PathPropertiesConstraint, PropertyValueConstraint,
    UniquePropertyValueConstraint: Classes to be subclassed by the library user
    when implementing a custom mapping module (advanced use).
- Dto, Relation: Base classes that can be used for type annotations.
- IGNORE: A special constant that can be used as a value in the PropertyValueConstraint.
"""

from importlib.metadata import version

from OpenApiLibCore.dto_base import (
    Dto,
    IdDependency,
    IdReference,
    PathPropertiesConstraint,
    PropertyValueConstraint,
    Relation,
    UniquePropertyValueConstraint,
)
from OpenApiLibCore.value_utils import IGNORE

from OpenApiDriver.openapidriver import OpenApiDriver

try:
    __version__ = version("robotframework-openapidriver")
except Exception:  # pragma: no cover
    pass

__all__ = [
    "Dto",
    "IdDependency",
    "IdReference",
    "PathPropertiesConstraint",
    "PropertyValueConstraint",
    "Relation",
    "UniquePropertyValueConstraint",
    "IGNORE",
    "OpenApiDriver",
]
