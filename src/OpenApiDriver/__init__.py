from importlib.metadata import version

from OpenApiDriver.openapidriver import OpenApiDriver
from OpenApiDriver.dto_base import  (
    Constraint,
    Dependency,
    Dto,
    IdDependency,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
)

try:
    __version__ = version("robotframework-openapidriver")
except:
    pass
