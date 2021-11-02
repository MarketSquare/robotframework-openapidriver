import unittest
from sys import float_info

EPSILON = float_info.epsilon

from OpenApiDriver import value_utils


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


if __name__ == "__main__":
    unittest.main()
