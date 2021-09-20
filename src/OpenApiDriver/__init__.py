from importlib.metadata import version

from OpenApiDriver.openapidriver import OpenApiDriver
from OpenApiDriver.dto_base import (
    Relation,
    Dto,
    IdDependency,
    IdReference,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
)

try:
    __version__ = version("robotframework-openapidriver")
except:  # pragma: no cover
    pass
