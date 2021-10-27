from dataclasses import dataclass
from importlib import import_module
from logging import getLogger
from typing import Any, Dict, Tuple, Type

from OpenApiDriver.dto_base import Dto

logger = getLogger(__name__)


@dataclass
class DefaultDto(Dto):
    """A default Dto that can be instantiated."""


# pylint: disable=invalid-name, too-few-public-methods
class get_dto_class:
    """Callable class to return Dtos from user-implemented mappings file."""

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
