import unittest

from OpenApiDriver import OpenApiDriver


class TestInit(unittest.TestCase):
    def test_load_from_invalid_source(self):
        self.assertRaises(
            Exception, OpenApiDriver, source="http://localhost:8000/openapi.doc"
        )


if __name__ == "__main__":
    unittest.main()
