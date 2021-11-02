from importlib.metadata import version

from OpenApiDriver.dto_base import (
    Dto,
    IdDependency,
    IdReference,
    PathPropertiesConstraint,
    PropertyValueConstraint,
    Relation,
    UniquePropertyValueConstraint,
)
from OpenApiDriver.openapidriver import OpenApiDriver
from OpenApiDriver.value_utils import IGNORE

try:
    __version__ = version("robotframework-openapidriver")
except:  # pragma: no cover
    pass
