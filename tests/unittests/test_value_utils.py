import unittest
from sys import float_info

EPSILON = float_info.epsilon

from OpenApiDriver import IGNORE, value_utils


class TestValidInteger(unittest.TestCase):
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


class TestValidFloat(unittest.TestCase):
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


class TestValidString(unittest.TestCase):
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


class TestInvalidEnum(unittest.TestCase):
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


# class TestGetInvalidValue(unittest.TestCase):


if __name__ == "__main__":
    unittest.main()
