from abc import ABC
from dataclasses import dataclass
from typing import Any, List, Optional


class Constraint(ABC):
    pass


class Dependency(ABC):
    pass


@dataclass
class Dto:
    @staticmethod
    def get_dependencies() -> List[Dependency]:
        return []

    @staticmethod
    def get_constraints() -> List[Constraint]:
        return []


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
class UniquePropertyValueConstraint(Constraint):
    """The value of the property must be unique within the resource scope."""
    property_name: str
    value: Any
    error_code: int = 422
