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

logger = getLogger(__name__)


IGNORE = object()


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
        return []

    @staticmethod
    def get_relations() -> List[Relation]:
        return []

    def get_relations_for_error_code(self, error_code: int) -> List[Relation]:
        relations: List[Relation] = [
            r for r in self.get_relations() if r.error_code == error_code
        ]
        return relations

    def get_parameter_relations_for_error_code(self, error_code: int) -> List[Relation]:
        relations: List[Relation] = [
            r for r in self.get_parameter_relations() if r.error_code == error_code
        ]
        return relations

    def get_invalidated_data(
        self, schema: Dict[str, Any], status_code: int
    ) -> Dict[str, Any]:
        def get_invalid_value_from_enum(values: List[Any], value_type: str):
            if value_type == "string":
                invalid_value: Any = ""
            elif value_type in ["integer", "number"]:
                invalid_value = 0
            elif value_type == "array":
                invalid_value = []
            elif value_type == "object":
                invalid_value = {}
            else:
                logger.warning(f"Cannot invalidate enum value with type {value_type}")
                return None
            for value in values:
                if value_type in ["string", "integer", "number"]:
                    invalid_value += value
                # TODO: can the values to choose from in an enum be array/object in JSON?
                if value_type == "array":
                    invalid_value.extend(value)
                if value_type == "object":
                    invalid_value.update(value)
            return invalid_value

        properties: Dict[str, Any] = self.__dict__

        relations = self.get_relations()
        shuffle(relations)
        for relation in relations:
            if (
                isinstance(relation, IdDependency)
                and status_code == relation.error_code
            ):
                invalid_value = uuid4().hex
                logger.debug(
                    f"Breaking IdDependency for status_code {status_code}: replacing "
                    f"{properties[relation.property_name]} with {invalid_value}"
                )
                properties[relation.property_name] = invalid_value
                return properties

        constrained_property_names: List[str] = [
            r.property_name for r in relations if isinstance(r, PropertyValueConstraint)
        ]
        property_names = list(properties.keys())
        # shuffle the propery_names so different properties on the Dto are invalidated
        # when rerunning the test
        shuffle(property_names)
        for property_name in property_names:
            # if possible, invalidate a constraint but send otherwise valid data
            property_data = schema["properties"][property_name]
            property_type = property_data["type"]
            current_value = properties[property_name]
            if enum_values := property_data.get("enum"):
                invalidated_value = get_invalid_value_from_enum(
                    values=enum_values, value_type=property_type
                )
                if invalidated_value is not None:
                    properties[property_name] = invalidated_value
                    return properties
            if (
                property_type == "boolean"
                and property_name in constrained_property_names
            ):
                properties[property_name] = not current_value
                return properties
            if property_type == "integer":
                if minimum := property_data.get("minimum"):
                    properties[property_name] = minimum - 1
                    return properties
                if maximum := property_data.get("maximum"):
                    properties[property_name] = maximum + 1
                    return properties
                if property_name in constrained_property_names:
                    # TODO: figure out a good generic approach, also consider multiple
                    # constraints on the same property
                    # HACK: this int is way out of the json supported int range
                    properties[property_name] = uuid4().int
                    return properties
            if property_type == "number":
                if minimum := property_data.get("minimum"):
                    properties[property_name] = minimum - 1
                    return properties
                if maximum := property_data.get("maximum"):
                    properties[property_name] = maximum + 1
                    return properties
                if property_name in constrained_property_names:
                    # TODO: figure out a good generic approach, also consider multiple
                    # constraints on the same property
                    # HACK: this float is way out of the json supported float range
                    properties[property_name] = uuid4().int / 3.14
                    return properties
            if property_type == "string":
                if minimum := property_data.get("minLength"):
                    if minimum > 0:
                        # if there is a minimum length, send 1 character less
                        properties[property_name] = current_value[0 : minimum - 1]
                        return properties
                if maximum := property_data.get("maxLength"):
                    properties[property_name] = current_value + uuid4().hex
                    return properties
        # if there are no constraints to violate, send invalid data types
        schema_properties = schema["properties"]
        for property_name, property_values in schema_properties.items():
            property_type = property_values.get("type")
            if property_type != "string":
                logger.debug(
                    f"property {property_name} set to str instead of {property_type}"
                )
                properties[property_name] = uuid4().hex
            else:
                # Since int / float / bool can always be cast to sting,
                # change the string to a nested object
                properties[property_name] = [{"invalid": [None]}]
        return properties


@dataclass
class DataClassMixin:
    """Mixin to add dataclass functionality to an ABC."""


class Dto(DataClassMixin, DtoBase):
    """Abstract base class to support custom mappings of resource dependencies."""
