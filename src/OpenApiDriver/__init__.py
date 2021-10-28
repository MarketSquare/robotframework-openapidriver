from importlib.metadata import version

from OpenApiDriver.dto_base import (
    IGNORE,
    Dto,
    IdDependency,
    IdReference,
    PathPropertiesConstraint,
    PropertyValueConstraint,
    Relation,
    UniquePropertyValueConstraint,
)
from OpenApiDriver.openapidriver import OpenApiDriver

try:
    __version__ = version("robotframework-openapidriver")
except:  # pragma: no cover
    pass
