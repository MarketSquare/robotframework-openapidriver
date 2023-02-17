"""Module holding the OpenApiReader reader_class implementation."""
from typing import Any, List, Union

from DataDriver.AbstractReaderClass import AbstractReaderClass
from DataDriver.ReaderConfig import TestCaseData


# pylint: disable=too-few-public-methods
class Test:
    """Helper class to support ignoring endpoints when generating the test cases."""

    def __init__(self, endpoint: str, method: str, response: Union[str, int]):
        self.endpoint = endpoint
        self.method = method.lower()
        self.response = str(response)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, type(self)):
            return False
        return (
            self.endpoint == other.endpoint
            and self.method == other.method
            and self.response == other.response
        )


class OpenApiReader(AbstractReaderClass):
    """Implementation of the reader_class used by DataDriver."""

    def get_data_from_source(self) -> List[TestCaseData]:
        test_data: List[TestCaseData] = []

        endpoints = getattr(self, "endpoints")
        if ignored_endpoints := getattr(self, "ignored_endpoints", None):
            for endpoint in ignored_endpoints:
                endpoints.pop(endpoint)
        if ignored_responses := getattr(self, "ignored_responses", None):
            ignore_list: List[str] = [str(response) for response in ignored_responses]
        else:
            ignore_list = []
        if ignored_testcases := getattr(self, "ignored_testcases", None):
            ignored_tests = [Test(*test) for test in ignored_testcases]
        else:
            ignored_tests = []
        for path, path_item in endpoints.items():
            for item_name, item_data in reversed(path_item.items()):
                if item_name not in ["get", "put", "post", "delete", "patch"]:
                    continue
                method, method_data = item_name, item_data
                tags_from_spec = method_data.get("tags", [])
                for response in method_data.get("responses"):
                    # default applies to all status codes that are not specified, in
                    # which case we don't know what to expect and thus can't verify
                    if (
                        response == "default"
                        or response in ignore_list
                        or Test(path, method, response) in ignored_tests
                    ):
                        continue
                    tag_list = _get_tag_list(
                        tags=tags_from_spec, method=method, response=response
                    )
                    test_data.append(
                        TestCaseData(
                            arguments={
                                "${endpoint}": path,
                                "${method}": method.upper(),
                                "${status_code}": response,
                            },
                            tags=tag_list,
                        ),
                    )
        return test_data


def _get_tag_list(tags: List[str], method: str, response: str) -> List[str]:
    return [*tags, f"Method: {method.upper()}", f"Response: {response}"]
