from importlib.metadata import version

from OpenApiDriver.dto_base import (
    Dto,
    IdDependency,
    IdReference,
    PropertyValueConstraint,
    Relation,
    UniquePropertyValueConstraint,
)
from OpenApiDriver.openapidriver import OpenApiDriver

try:
    __version__ = version("robotframework-openapidriver")
except:  # pragma: no cover
    pass
