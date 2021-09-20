import unittest

from DataDriver.ReaderConfig import ReaderConfig
from OpenApiDriver.openapi_reader import OpenApiReader, Test


class TestInit(unittest.TestCase):
    def test_get_data_from_invalid_source(self):
        reader = OpenApiReader(reader_config=ReaderConfig(source=None))
        self.assertRaises(
            AssertionError,
            reader.get_data_from_source,
        )

    def test_test_class_not_equal(self):
        test = Test("/", "GET", 200)
        self.assertFalse(test == ("/", "GET", 200))


if __name__ == "__main__":
    unittest.main()
