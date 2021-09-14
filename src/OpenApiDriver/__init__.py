from importlib.metadata import version

from OpenApiDriver.openapidriver import OpenApiDriver
from OpenApiDriver.dto_base import  (
    ResourceRelation,
    Constraint,
    Dependency,
    Dto,
    IdDependency,
    IdReference,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
)

try:
    __version__ = version("robotframework-openapidriver")
except:     # pragma: no cover
    pass
