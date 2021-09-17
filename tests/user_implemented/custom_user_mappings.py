# pylint: disable=invalid-name
from typing import Any, Dict, List, Tuple

from OpenApiDriver import (
    Dto,
    Relation,
    IdDependency,
    IdReference,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
)


class WagegroupDto(Dto):
    @staticmethod
    def get_relations() -> List[Relation]:
        relations = [
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
        return relations


class EmployeeDto(Dto):
    @staticmethod
    def get_relations() -> List[Relation]:
        relations = [
            IdDependency(
                property_name="wagegroup_id",
                get_path="/wagegroups",
                error_code=451,
            ),
        ]
        return relations


DTO_MAPPING: Dict[Tuple[Any, Any], Any] = {
    (r"/wagegroups", "post"): WagegroupDto,
    (r"/wagegroups/{wagegroup_id}", "delete"): WagegroupDto,
    (r"/employees", "post"): EmployeeDto,
}
