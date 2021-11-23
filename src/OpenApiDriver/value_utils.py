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
    if value_type == "integer":
        return get_random_int(value_schema=value_schema)
    if value_type == "number":
        return get_random_float(value_schema=value_schema)
    if value_type == "string":
        return get_random_string(value_schema=value_schema)
    raise NotImplementedError(f"Type '{value_type}' is currently not supported")


def get_invalid_value(
    value_schema: Dict[str, Any],
    current_value: Any,
    values_from_constraint: Optional[List[Any]] = None,
) -> Any:
    """Return a random value that violates the provided value_schema."""

    invalid_value: Any = None
    value_type = value_schema["type"]

    if values_from_constraint:
        if (
            invalid_value := get_invalid_value_from_constraint(
                values_from_constraint=values_from_constraint,
                value_type=value_type,
            )
        ) is not None:
            return invalid_value
    # if an enum is possible, combine the values from the enum to invalidate the value
    if enum_values := value_schema.get("enum"):
        if (
            invalid_value := get_invalid_value_from_enum(
                values=enum_values, value_type=value_type
            )
        ) is not None:
            return invalid_value
    # violate min / max values or length if possible
    if (
        invalid_value := get_value_out_of_bounds(
            value_schema=value_schema, current_value=current_value
        )
    ) is not None:
        return invalid_value
    # no value constraints or min / max ranges to violate, so change the data type
    if value_type == "string":
        # since int / float / bool can always be cast to sting, change
        # the string to a nested object
        return [{"invalid": [None]}]
    logger.debug(f"property type changed from {value_type} to random string")
    return uuid4().hex


def get_random_int(value_schema: Dict[str, Any]) -> int:
    """Generate a random int within the min/max range of the schema, if specified."""
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
    """Generate a random float within the min/max range of the schema, if specified."""
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
    exclusive = value_schema.get("exclusiveMinimum", False) or value_schema.get(
        "exclusiveMaximum", False
    )
    if exclusive:
        if minimum == maximum:
            raise ValueError(
                f"maximum of {maximum} is equal to minimum of {minimum} and "
                f"exclusiveMinimum or exclusiveMaximum is True"
            )
    while exclusive:
        result = uniform(minimum, maximum)
        if minimum < result < maximum:  # pragma: no cover
            return result
    return uniform(minimum, maximum)


def get_random_string(value_schema: Dict[str, Any]) -> str:
    """Generate a random string within the min/max length in the schema, if specified."""
    # TODO: byte, binary, date, date-time based on "format"
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


def get_invalid_value_from_constraint(
    values_from_constraint: List[Any], value_type: str
) -> Any:
    """
    Return a value of the same type as the values in the values_from_constraints that
    is not in the values_from_constraints, if possible. Otherwise returns None.
    """
    # if IGNORE is in the values_from_constraints, the parameter needs to be
    # ignored for an OK response so leaving the value at it's original value
    # should result in the specified error response
    if IGNORE in values_from_constraint:
        return IGNORE
    # if the value is forced True or False, return the opposite to invalidate
    if len(values_from_constraint) == 1 and value_type == "boolean":
        return not values_from_constraint[0]
    if (
        value_type not in ["string", "integer", "number", "array"]
        or not values_from_constraint
    ):
        return None
    invalid_values = 2 * values_from_constraint
    # None for empty array
    if not invalid_values:
        return None
    invalid_value = invalid_values.pop()
    if value_type in ["integer", "number"]:
        for value in invalid_values:
            invalid_value = abs(invalid_value) + abs(value)
        if not invalid_value:
            invalid_value += 1
        return invalid_value
    for value in invalid_values:
        invalid_value = invalid_value + value
    # None for empty string
    return invalid_value if invalid_value else None


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


def get_value_out_of_bounds(value_schema: Dict[str, Any], current_value: Any) -> Any:
    """
    Return a value just outside the value or length range if specified in the
    provided schema, otherwise None is returned.
    """
    value_type = value_schema["type"]

    if value_type in ["integer", "number"]:
        if minimum := value_schema.get("minimum"):
            return minimum - 1
        if maximum := value_schema.get("maximum"):
            return maximum + 1
        if exclusive_minimum := value_schema.get("exclusiveMinimum"):
            return exclusive_minimum
        if exclusive_maximum := value_schema.get("exclusiveMaximum"):
            return exclusive_maximum
    if value_type == "string":
        # if there is a minimum length, send 1 character less
        if minimum := value_schema.get("minLength", 0):
            return current_value[0 : minimum - 1]
        # if there is a maximum length, send 1 character more
        if maximum := value_schema.get("maxLength"):
            invalid_value = current_value if current_value else "x"
            # add random characters from the current value to prevent adding new characters
            while len(invalid_value) <= maximum:
                invalid_value += choice(invalid_value)
            return invalid_value
    return None
