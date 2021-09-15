# pylint: disable=invalid-name
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from OpenApiDriver import (
    Constraint,
    Dependency,
    Dto,
    IdDependency,
    IdReference,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
)


@dataclass
class WagegroupDto(Dto):
    @staticmethod
    def get_constraints() -> List[Constraint]:
        constraints = [
            UniquePropertyValueConstraint(
                property_name="id",
                value="Teapot",
                error_code=418,
            ),
            IdReference(
                property_name="wagegroup_id",
                post_path="/employees",
                error_code=406,
            )
        ]
        return constraints


@dataclass
class EmployeeDto(Dto):
    @staticmethod
    def get_dependencies() -> List[Dependency]:
        dependencies = [
            IdDependency(
                property_name="wagegroup_id",
                get_path="/wagegroups",
                error_code=451,
            ),
        ]
        return dependencies


DTO_MAPPING: Dict[Tuple[Any, Any], Any] = {
    (r"/wagegroups", "post"): WagegroupDto,
    (r"/wagegroups/{wagegroup_id}", "delete"): WagegroupDto,
    (r"/employees", "post"): EmployeeDto,
}
