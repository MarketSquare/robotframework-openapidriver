# pylint: disable=invalid-name
from typing import Any, Dict, List, Tuple

from OpenApiDriver import (
    IGNORE,
    Dto,
    IdDependency,
    IdReference,
    PathPropertiesConstraint,
    PropertyValueConstraint,
    Relation,
    UniquePropertyValueConstraint,
)


class WagegroupDto(Dto):
    @staticmethod
    def get_relations() -> List[Relation]:
        relations: List[Relation] = [
            UniquePropertyValueConstraint(
                property_name="id",
                value="Teapot",
                error_code=418,
            ),
            IdReference(
                property_name="wagegroup_id",
                post_path="/employees",
                error_code=406,
            ),
        ]
        return relations


class EmployeeDto(Dto):
    @staticmethod
    def get_relations() -> List[Relation]:
        relations: List[Relation] = [
            IdDependency(
                property_name="wagegroup_id",
                get_path="/wagegroups",
                error_code=451,
            ),
        ]
        return relations


class EnergyLabelDto(Dto):
    @staticmethod
    def get_relations() -> List[Relation]:
        relations: List[Relation] = [
            PathPropertiesConstraint(path="/energy_label/1111AA/10"),
        ]
        return relations


class MessageDto(Dto):
    @staticmethod
    def get_parameter_relations() -> List[Relation]:
        relations: List[Relation] = [
            PropertyValueConstraint(
                property_name="secret-code",  # note: property name converted by FastAPI
                values=[42],
                error_code=401,
            ),
            PropertyValueConstraint(
                property_name="seal",
                values=[IGNORE],
                error_code=403,
            ),
        ]
        return relations


DTO_MAPPING: Dict[Tuple[Any, Any], Any] = {
    ("/wagegroups", "post"): WagegroupDto,
    ("/wagegroups/{wagegroup_id}", "delete"): WagegroupDto,
    ("/employees", "post"): EmployeeDto,
    ("/energy_label/{zipcode}/{home_number}", "get"): EnergyLabelDto,
    ("/message", "get"): MessageDto,
}
