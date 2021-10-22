from importlib import import_module
from logging import getLogger
from typing import Any, Dict, List, Tuple, Type

from OpenApiDriver.dto_base import Dto, Relation

logger = getLogger(__name__)


class DefaultDto(Dto):
    @staticmethod
    def get_relations() -> List[Relation]:
        return []


class get_dto_class:
    def __init__(self, mappings_module_name: str) -> None:
        try:
            mappings_module = import_module(mappings_module_name)
            self.dto_mapping: Dict[Tuple[str, str], Any] = mappings_module.DTO_MAPPING
        except (ImportError, AttributeError, ValueError) as exception:
            logger.debug(f"DTO_MAPPING was not imported: {exception}")
            self.dto_mapping = {}

    def __call__(self, endpoint: str, method: str) -> Type[Dto]:
        try:
            return self.dto_mapping[(endpoint, method.lower())]
        except KeyError:
            logger.debug(f"No Dto mapping for {endpoint} {method}.")
            return DefaultDto
