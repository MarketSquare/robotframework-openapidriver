import unittest

from OpenApiDriver.openapi_reader import Test


class TestInit(unittest.TestCase):
    def test_test_class_not_equal(self):
        test = Test("/", "GET", 200)
        self.assertFalse(test == ("/", "GET", 200))


if __name__ == "__main__":
    unittest.main()
