"""Utility module with functions to handle OpenAPI value types and restrictions."""
from logging import getLogger
from random import choice, getrandbits, randint, uniform
from typing import Any, Dict, List, Optional
from uuid import uuid4

IGNORE = object()

logger = getLogger(__name__)


def get_valid_value(value_schema: Dict[str, Any]) -> Any:
    """Return a random value that is valid under the provided value_schema."""
    if from_enum := value_schema.get("enum", None):
        return choice(from_enum)

    value_type = value_schema["type"]

    if value_type == "boolean":
        return bool(getrandbits(1))
    # Use int32 integers if "format" does not specify int64
    if value_type == "integer":
        return get_random_int(value_schema=value_schema)
    if value_type == "number":
        return get_random_float(value_schema=value_schema)
    # TODO: byte, binary, date, date-time based on "format"
    if value_type == "string":
        return get_random_string(value_schema=value_schema)
    raise NotImplementedError(f"Type '{value_type}' is currently not supported")


def get_invalid_value(
    value_schema: Dict[str, Any],
    current_value: Any,
    values_from_constraint: Optional[List[Any]] = None,
) -> Any:
    """Return a random value that violates the provided value_schema."""

    # if IGNORE is in the values_from_constraints, the parameter needs to be
    # ignored for an OK response so leaving the value at it's original value
    # should result in the specified error response
    if values_from_constraint:
        if IGNORE in values_from_constraint:
            return IGNORE
        # if the value is forced True or False, return the opposite to invalidate
        if len(values_from_constraint) == 1 and isinstance(
            values_from_constraint[0], bool
        ):
            return not values_from_constraint[0]
        invalid_values = 2 * values_from_constraint
        invalid_value = invalid_values.pop()
        for value in invalid_values:
            invalid_value = invalid_value + value
        return invalid_value
    # if an enum is possible, combine the values from the enum to invalidate the value
    value_type = value_schema["type"]
    if enum_values := value_schema.get("enum"):
        invalid_value = get_invalid_value_from_enum(
            values=enum_values, value_type=value_type
        )
        if invalid_value is not None:
            return invalid_value
    # violate min / max values if possible
    if value_type == "integer":
        if minimum := value_schema.get("minimum"):
            return minimum - 1
        if maximum := value_schema.get("maximum"):
            return maximum + 1
    if value_type == "number":
        if minimum := value_schema.get("minimum"):
            return minimum - 1
        if maximum := value_schema.get("maximum"):
            return maximum + 1
    if value_type == "string":
        # if there is a minimum length, send 1 character less
        if minimum := value_schema.get("minLength", 0) > 0:
            return current_value[0 : minimum - 1]
        # if there is a maximum length, send 1 character more
        if maximum := value_schema.get("maxLength"):
            invalid_value = current_value
            # add random characters from the current value to prevent adding new characters
            while len(invalid_value) <= maximum:
                invalid_value += choice(current_value)
            return invalid_value
    # no value constraints or min / max ranges to violate, so change the data type
    if value_type == "string":
        # since int / float / bool can always be cast to sting, change
        # the string to a nested object
        return [{"invalid": [None]}]
    logger.debug(f"property set to str instead of {value_type}")
    return uuid4().hex


def get_random_int(value_schema: Dict[str, Any]) -> int:
    """Generate a random int within the min/max range of the schema, is specified."""
    # Use int32 integers if "format" does not specify int64
    property_format = value_schema.get("format", "int32")
    if property_format == "int64":
        min_int = -9223372036854775808
        max_int = 9223372036854775807
    else:
        min_int = -2147483648
        max_int = 2147483647
    minimum = value_schema.get("minimum", min_int)
    maximum = value_schema.get("maximum", max_int)
    if value_schema.get("exclusiveMinimum", False):
        minimum += 1
    if value_schema.get("exclusiveMaximum", False):
        maximum -= 1
    return randint(minimum, maximum)


def get_random_float(value_schema: Dict[str, Any]) -> float:
    """Generate a random float within the min/max range of the schema, is specified."""
    # Python floats are already double precision, so no check for "format"
    minimum = value_schema.get("minimum")
    maximum = value_schema.get("maximum")
    if minimum is None:
        if maximum is None:
            minimum = -1.0
            maximum = 1.0
        else:
            minimum = maximum - 1.0
    else:
        if maximum is None:
            maximum = minimum + 1.0
        if maximum < minimum:
            raise ValueError(f"maximum of {maximum} is less than minimum of {minimum}")
    # for simplicity's sake, exclude both boundaries if one boundary is exclusive
    while value_schema.get("exclusiveMinimum", False) or value_schema.get(
        "exclusiveMaximum", False
    ):
        if minimum == maximum:
            raise ValueError(
                f"maximum of {maximum} is equal to minimum of {minimum} and "
                f"exclusiveMinimum or exclusiveMaximum is True"
            )
        result = uniform(minimum, maximum)
        if minimum < result < maximum:
            return result
    return uniform(minimum, maximum)


def get_random_string(value_schema: Dict[str, Any]) -> str:
    """Generate a random string within the min/max length in the schema, is specified."""
    minimum = value_schema.get("minLength", 0)
    maximum = value_schema.get("maxLength", 36)
    if minimum > maximum:
        maximum = minimum
    value = uuid4().hex
    while len(value) < minimum:
        value = value + uuid4().hex
    if len(value) > maximum:
        value = value[:maximum]
    return value


def get_invalid_value_from_enum(values: List[Any], value_type: str):
    """Return a value not in the enum by combining the enum values."""
    if value_type == "string":
        invalid_value: Any = ""
    elif value_type in ["integer", "number"]:
        invalid_value = 0
    elif value_type == "array":
        invalid_value = []
    elif value_type == "object":
        # force creation of a new object since we will be modifing it
        invalid_value = {**values[0]}
    else:
        logger.warning(f"Cannot invalidate enum value with type {value_type}")
        return None
    for value in values:
        if value_type in ["integer", "number"]:
            invalid_value += abs(value)
        if value_type == "string":
            invalid_value += value
        if value_type == "array":
            invalid_value.extend(value)
        # objects are a special case, since they must be of the same type / class
        # invalid_value.update(value) will end up with the last value in the list,
        # which is a valid value, so another approach is needed
        if value_type == "object":
            for key in invalid_value.keys():
                invalid_value[key] = value.get(key)
                if invalid_value not in values:
                    return invalid_value
    return invalid_value
