import unittest
from sys import float_info

EPSILON = float_info.epsilon

from OpenApiDriver import IGNORE, value_utils


class TestRandomInteger(unittest.TestCase):
    def test_default_min_max(self):
        schema = {"maximum": -2147483648}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, -2147483648)

        schema = {"minimum": 2147483647}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, 2147483647)

    def test_exclusive_min_max(self):
        schema = {"maximum": -2147483647, "exclusiveMaximum": True}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, -2147483648)

        schema = {"minimum": 2147483646, "exclusiveMinimum": True}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, 2147483647)

    def test_min_max(self):
        schema = {"minimum": 42, "maximum": 42}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, 42)

        schema = {"minimum": -42, "maximum": -42}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, -42)

        schema = {
            "minimum": 41,
            "maximum": 43,
            "exclusiveMinimum": True,
            "exclusiveMaximum": True,
        }
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, 42)

        schema = {
            "minimum": -43,
            "maximum": -41,
            "exclusiveMinimum": True,
            "exclusiveMaximum": True,
        }
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, -42)

    def test_int64(self):
        schema = {"maximum": -9223372036854775808, "format": "int64"}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, -9223372036854775808)

        schema = {"minimum": 9223372036854775807, "format": "int64"}
        value = value_utils.get_random_int(schema)
        self.assertEqual(value, 9223372036854775807)


class TestRandomFloat(unittest.TestCase):
    def test_default_min_max(self):
        schema = {}
        value = value_utils.get_random_float(schema)
        self.assertGreaterEqual(value, -1.0)
        self.assertLessEqual(value, 1.0)

        schema = {"minimum": -2.0}
        value = value_utils.get_random_float(schema)
        self.assertGreaterEqual(value, -2.0)
        self.assertLessEqual(value, -1.0)

        schema = {"maximum": -2.0}
        value = value_utils.get_random_float(schema)
        self.assertGreaterEqual(value, -3.0)
        self.assertLessEqual(value, -2.0)

    def test_exclusive_min_max(self):
        schema = {
            "minimum": 1.0 - EPSILON,
            "maximum": 1.0 + EPSILON,
            "exclusiveMinimum": True,
        }
        value = value_utils.get_random_float(schema)
        self.assertAlmostEqual(value, 1.0)

        schema = {
            "minimum": -1.0 - EPSILON,
            "maximum": -1.0 + EPSILON,
            "exclusiveMaximum": True,
        }
        value = value_utils.get_random_float(schema)
        self.assertAlmostEqual(value, -1.0)

    def test_raises(self):
        schema = {"minimum": 1.0 + EPSILON, "maximum": 1.0}
        self.assertRaises(ValueError, value_utils.get_random_float, schema)

        schema = {"minimum": -1.0, "maximum": -1.0 - EPSILON}
        self.assertRaises(ValueError, value_utils.get_random_float, schema)

        schema = {"minimum": 1.0, "maximum": 1.0, "exclusiveMinimum": True}
        self.assertRaises(ValueError, value_utils.get_random_float, schema)

        schema = {"minimum": 1.0, "maximum": 1.0, "exclusiveMaximum": True}
        self.assertRaises(ValueError, value_utils.get_random_float, schema)

    def test_min_max(self):
        schema = {"minimum": 1.1, "maximum": 1.1}
        value = value_utils.get_random_float(schema)
        self.assertEqual(value, 1.1)

        schema = {"minimum": -1.1, "maximum": -1.1}
        value = value_utils.get_random_float(schema)
        self.assertEqual(value, -1.1)

        schema = {"minimum": 2.1, "maximum": 2.2, "exclusiveMinimum": True}
        value = value_utils.get_random_float(schema)
        self.assertGreater(value, 2.1)
        self.assertLess(value, 2.2)

        schema = {"minimum": -0.2, "maximum": -0.1, "exclusiveMaximum": True}
        value = value_utils.get_random_float(schema)
        self.assertGreater(value, -0.2)
        self.assertLess(value, -0.1)


class TestRandomString(unittest.TestCase):
    def test_default_min_max(self):
        schema = {"maxLength": 0}
        value = value_utils.get_random_string(schema)
        self.assertEqual(value, "")

        schema = {"minLength": 36}
        value = value_utils.get_random_string(schema)
        self.assertEqual(len(value), 36)

    def test_min_max(self):
        schema = {"minLength": 42, "maxLength": 42}
        value = value_utils.get_random_string(schema)
        self.assertEqual(len(value), 42)

        schema = {"minLength": 42}
        value = value_utils.get_random_string(schema)
        self.assertEqual(len(value), 42)


class TestGetValidValue(unittest.TestCase):
    def test_enum(self):
        schema = {"enum": ["foo", "bar"]}
        value = value_utils.get_valid_value(schema)
        self.assertIn(value, ["foo", "bar"])

    def test_bool(self):
        schema = {"type": "boolean"}
        value = value_utils.get_valid_value(schema)
        self.assertIsInstance(value, bool)

    def test_integer(self):
        schema = {"type": "integer"}
        value = value_utils.get_valid_value(schema)
        self.assertIsInstance(value, int)

    def test_number(self):
        schema = {"type": "number"}
        value = value_utils.get_valid_value(schema)
        self.assertIsInstance(value, float)

    def test_string(self):
        schema = {"type": "string"}
        value = value_utils.get_valid_value(schema)
        self.assertIsInstance(value, str)

    def test_raises(self):
        schema = {"type": "array"}
        self.assertRaises(NotImplementedError, value_utils.get_valid_value, schema)


class TestInvalidValueFromConstraint(unittest.TestCase):
    def test_ignore(self):
        values = [42, IGNORE]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="irrelevant",
        )
        self.assertEqual(value, IGNORE)

    def test_unsupported(self):
        values = [{"red": 255, "green": 255, "blue": 255}]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="object",
        )
        self.assertEqual(value, None)

    def test_bool(self):
        values = [True]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="boolean",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, bool)

        values = [False]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="boolean",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, bool)

        values = [True, False]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="boolean",
        )
        self.assertEqual(value, None)

    def test_string(self):
        values = ["foo"]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="string",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, str)

        values = ["foo", "bar", "baz"]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="string",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, str)

        values = [""]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="string",
        )
        self.assertEqual(value, None)

    def test_integer(self):
        values = [0]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="integer",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, int)

        values = [-3, 0, 3]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="integer",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, int)

    def test_number(self):
        values = [0.0]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="number",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, float)

        values = [-0.1, 0.0, 0.1]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="number",
        )
        self.assertNotIn(value, values)
        self.assertIsInstance(value, float)

    def test_array(self):
        values = [[42]]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="array",
        )
        self.assertNotIn(value, values)

        values = [["spam"], ["ham", "eggs"]]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="array",
        )
        self.assertNotIn(value, values)

        values = []
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="array",
        )
        self.assertEqual(value, None)

        values = [[], []]
        value = value_utils.get_invalid_value_from_constraint(
            values_from_constraint=values,
            value_type="array",
        )
        self.assertEqual(value, None)


class TestInvalidValueFromEnum(unittest.TestCase):
    def test_string(self):
        value_list = ["foo", "bar"]
        result = value_utils.get_invalid_value_from_enum(
            values=value_list,
            value_type="string",
        )
        self.assertNotIn(result, value_list)

    def test_integer(self):
        value_list = [-1, 0, 1]
        result = value_utils.get_invalid_value_from_enum(
            values=value_list,
            value_type="integer",
        )
        self.assertNotIn(result, value_list)

    def test_float(self):
        value_list = [-0.1, 0, 0.1]
        result = value_utils.get_invalid_value_from_enum(
            values=value_list,
            value_type="integer",
        )
        self.assertNotIn(result, value_list)

    def test_array(self):
        value_list = [["foo", "bar", "baz"], ["spam", "ham", "eggs"]]
        result = value_utils.get_invalid_value_from_enum(
            values=value_list,
            value_type="array",
        )
        self.assertNotIn(result, value_list)

    def test_object(self):
        value_list = [
            {
                "red": 255,
                "blue": 0,
                "green": 0,
            },
            {
                "red": 0,
                "blue": 255,
                "green": 0,
            },
            {
                "red": 0,
                "blue": 0,
                "green": 255,
            },
        ]
        result = value_utils.get_invalid_value_from_enum(
            values=value_list,
            value_type="object",
        )
        self.assertNotIn(result, value_list)

    def test_unsupported(self):
        value_list = [True, False]
        result = value_utils.get_invalid_value_from_enum(
            values=value_list,
            value_type="bool",
        )
        self.assertEqual(result, None)


class TestValueOutOfBounds(unittest.TestCase):
    def test_minimum_integer(self):
        minimum = -42
        value_schema = {"type": "integer", "minimum": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertLess(value, minimum)
        self.assertIsInstance(value, int)

        minimum = 3
        value_schema = {"type": "integer", "minimum": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertLess(value, minimum)
        self.assertIsInstance(value, int)

    def test_minimum_number(self):
        minimum = -0.6
        value_schema = {"type": "integer", "minimum": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertLess(value, minimum)
        self.assertIsInstance(value, float)

        minimum = 3.14159
        value_schema = {"type": "integer", "minimum": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertLess(value, minimum)
        self.assertIsInstance(value, float)

    def test_maximum_integer(self):
        maximum = -42
        value_schema = {"type": "integer", "maximum": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertGreater(value, maximum)
        self.assertIsInstance(value, int)

        maximum = 3
        value_schema = {"type": "integer", "maximum": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertGreater(value, maximum)
        self.assertIsInstance(value, int)

    def test_maximum_number(self):
        maximum = -0.6
        value_schema = {"type": "integer", "maximum": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertGreater(value, maximum)
        self.assertIsInstance(value, float)

        maximum = 3.14159
        value_schema = {"type": "integer", "maximum": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertGreater(value, maximum)
        self.assertIsInstance(value, float)

    def test_exclusive_minimum_integer(self):
        minimum = -42
        value_schema = {"type": "integer", "exclusiveMinimum": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, minimum)
        self.assertIsInstance(value, int)

    def test_exclusive_minimum_number(self):
        minimum = 3.14159
        value_schema = {"type": "integer", "exclusiveMinimum": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, minimum)
        self.assertIsInstance(value, float)

    def test_exclusive_maximum_integer(self):
        maximum = -42
        value_schema = {"type": "integer", "exclusiveMaximum": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, maximum)
        self.assertIsInstance(value, int)

    def test_exclusive_maximum_number(self):
        maximum = -273.15
        value_schema = {"type": "integer", "exclusiveMinimum": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, maximum)
        self.assertIsInstance(value, float)

    def test_minimum_length(self):
        minimum = 1
        value_schema = {"type": "string", "minLength": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertLess(len(value), minimum)
        self.assertIsInstance(value, str)

    def test_maximum_length(self):
        maximum = 7
        value_schema = {"type": "string", "maxLength": maximum}
        current_value = "valid"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertGreater(len(value), maximum)
        self.assertIsInstance(value, str)

        maximum = 7
        value_schema = {"type": "string", "maxLength": maximum}
        current_value = ""
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertGreater(len(value), maximum)
        self.assertIsInstance(value, str)

    def test_minimum_zero(self):
        minimum = 0
        value_schema = {"type": "string", "minLength": minimum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, None)

    def test_maximum_zero(self):
        maximum = 0
        value_schema = {"type": "string", "maxLength": maximum}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, None)

    def test_unbound(self):
        value_schema = {"type": "integer"}
        current_value = "irrelvant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, None)

        value_schema = {"type": "number"}
        current_value = "irrelvant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, None)

        value_schema = {"type": "string"}
        current_value = "irrelvant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, None)

    def test_unsupported(self):
        value_schema = {"type": "boolean"}
        current_value = "irrelevant"
        value = value_utils.get_value_out_of_bounds(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertEqual(value, None)


class TestGetInvalidValue(unittest.TestCase):
    def test_invalid_from_constraint(self):
        current_value = "irrelevant"
        values_from_constraints = [42]

        value_schema = {"type": "integer"}
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
            values_from_constraint=values_from_constraints,
        )
        self.assertNotIn(value, values_from_constraints)
        self.assertIsInstance(value, int)

        value_schema = {"type": None}
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
            values_from_constraint=values_from_constraints,
        )
        self.assertIsInstance(value, str)

    def test_invalid_from_enum(self):
        enum_values = [0.1, 0.3]
        current_value = "irrelevant"

        value_schema = {"type": "number", "enum": enum_values}
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertNotIn(value, enum_values)
        self.assertIsInstance(value, float)

        value_schema = {"type": None, "enum": enum_values}
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertIsInstance(value, str)

    def test_invalid_from_bounds(self):
        min_length = 7
        current_value = "long enough"
        value_schema = {"type": "string", "minLength": min_length}
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertLess(len(value), min_length)
        self.assertIsInstance(value, str)

        value_schema = {"type": "bytes", "minLength": min_length}
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertIsInstance(value, str)

    def test_invalid_string(self):
        value_schema = {"type": "string"}
        current_value = "irrelevant"
        value = value_utils.get_invalid_value(
            value_schema=value_schema,
            current_value=current_value,
        )
        self.assertNotIsInstance(value, str)


if __name__ == "__main__":
    unittest.main()
