"""
Module holding the (base) classes that can be used by the user of the OpenApiDriver
to implement custom mappings for dependencies between resources in the API under
test and constraints / restrictions on properties of the resources.
"""
from abc import ABC
from dataclasses import dataclass
from logging import getLogger
from random import shuffle
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from OpenApiDriver import value_utils

logger = getLogger(__name__)


class ResourceRelation(ABC):
    """ABC for all resource relations or restrictions within the API."""

    property_name: str
    error_code: int


@dataclass
class PathPropertiesConstraint(ResourceRelation):
    """The resolved path for the endpoint."""

    path: str
    property_name: str = "id"
    error_code: int = 404


@dataclass
class PropertyValueConstraint(ResourceRelation):
    """The allowed values for property_name."""

    property_name: str
    values: List[Any]
    error_code: int = 422


@dataclass
class IdDependency(ResourceRelation):
    """The path where a valid id for the propery_name can be gotten (using GET)."""

    property_name: str
    get_path: str
    operation_id: Optional[str] = None
    error_code: int = 422


@dataclass
class IdReference(ResourceRelation):
    """The path where a resource that needs this resource's id can be created (using POST)."""

    property_name: str
    post_path: str
    error_code: int = 422


@dataclass
class UniquePropertyValueConstraint(ResourceRelation):
    """The value of the property must be unique within the resource scope."""

    property_name: str
    value: Any
    error_code: int = 422


Relation = Union[
    IdDependency,
    IdReference,
    PathPropertiesConstraint,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
]


class DtoBase(ABC):
    """Base class for the Dto class."""

    @staticmethod
    def get_parameter_relations() -> List[Relation]:
        """Return the list of Relations for the header and query parameters."""
        return []

    def get_parameter_relations_for_error_code(self, error_code: int) -> List[Relation]:
        """Return the list of Relations associated with the given error_code."""
        relations: List[Relation] = [
            r for r in self.get_parameter_relations() if r.error_code == error_code
        ]
        return relations

    @staticmethod
    def get_relations() -> List[Relation]:
        """Return the list of Relations for the (json) body."""
        return []

    def get_relations_for_error_code(self, error_code: int) -> List[Relation]:
        """Return the list of Relations associated with the given error_code."""
        relations: List[Relation] = [
            r for r in self.get_relations() if r.error_code == error_code
        ]
        return relations

    def get_invalidated_data(
        self,
        schema: Dict[str, Any],
        status_code: int,
        invalid_property_default_code: int,
    ) -> Dict[str, Any]:
        """Return a data set with one of the properties set to an invalid value or type."""
        properties: Dict[str, Any] = self.__dict__

        relations = [r for r in self.get_relations() if r.error_code == status_code]
        if status_code == invalid_property_default_code:
            property_names = list(properties.keys())
        else:
            property_names = [r.property_name for r in relations]
        # shuffle the propery_names so different properties on the Dto are invalidated
        # when rerunning the test
        shuffle(property_names)
        for property_name in property_names:
            # if possible, invalidate a constraint but send otherwise valid data
            id_dependencies = [
                r
                for r in relations
                if isinstance(r, IdDependency) and r.property_name == property_name
            ]
            if id_dependencies:
                invalid_value = uuid4().hex
                logger.debug(
                    f"Breaking IdDependency for status_code {status_code}: replacing "
                    f"{properties[property_name]} with {invalid_value}"
                )
                properties[property_name] = invalid_value
                return properties

            value_schema = schema["properties"][property_name]
            current_value = properties[property_name]
            values_from_constraint = [
                r.values
                for r in relations
                if isinstance(r, PropertyValueConstraint)
                and r.property_name == property_name
            ]

            properties[property_name] = value_utils.get_invalid_value(
                value_schema=value_schema,
                current_value=current_value,
                values_from_constraint=values_from_constraint,
            )
            return properties
        return properties  # pragma: no cover


@dataclass
class DataClassMixin:
    """Mixin to add dataclass functionality to an ABC."""


class Dto(DataClassMixin, DtoBase):
    """Abstract base class to support custom mappings of resource dependencies."""
