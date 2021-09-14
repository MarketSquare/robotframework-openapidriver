from abc import ABC
from dataclasses import dataclass
from typing import Any, List, Optional


class ResourceRelation(ABC):
    property_name: str
    error_code: int


class Constraint(ResourceRelation):
    pass


class Dependency(ResourceRelation):
    pass


@dataclass
class Dto:
    @staticmethod
    def get_dependencies() -> List[Dependency]:
        return []

    @staticmethod
    def get_constraints() -> List[Constraint]:
        return []

    def get_relation_for_error_code(self, error_code: int) -> List[ResourceRelation]:
        relations: List[ResourceRelation] = [
            d for d in self.get_dependencies() if d.error_code == error_code
        ] + [
            c for c in self.get_constraints() if c.error_code == error_code
        ]
        return relations


@dataclass
class PropertyValueConstraint(Constraint):
    """The allowed values for property_name."""
    property_name: str
    values: List[Any]
    error_code: int = 422


@dataclass
class IdDependency(Dependency):
    """The path where a valid id for the propery_name can be gotten (using GET)"""
    property_name: str
    get_path: str
    operation_id: Optional[str] = None
    error_code: int = 422


@dataclass
class IdReference(Dependency):
    """The path where a resource that needs this resource's id can be created (using POST)"""
    property_name: str
    post_path: str
    error_code: int = 422


@dataclass
class UniquePropertyValueConstraint(Constraint):
    """The value of the property must be unique within the resource scope."""
    property_name: str
    value: Any
    error_code: int = 422
