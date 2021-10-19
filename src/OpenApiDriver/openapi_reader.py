from typing import Any, Dict, List, Union

from DataDriver.AbstractReaderClass import AbstractReaderClass
from DataDriver.ReaderConfig import TestCaseData
from prance import ResolvingParser
from prance.util.url import ResolutionError
from robot.libraries.BuiltIn import BuiltIn


class Test:
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
    def get_data_from_source(self) -> List[TestCaseData]:
        test_data: List[TestCaseData] = []

        try:
            parser = ResolvingParser(
                getattr(self, "source", None), backend="openapi-spec-validator"
            )
        except (ResolutionError, AssertionError) as exception:
            BuiltIn().fatal_error(
                f"Exception while trying to load openapi spec from source: {exception}"
            )
        endpoints: Dict[str, Any] = parser.specification["paths"]
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
        ignore_fastapi_default_422: bool = getattr(
            self, "ignore_fastapi_default_422", False
        )
        for endpoint, methods in endpoints.items():
            for method, method_data in reversed(methods.items()):
                for response in method_data.get("responses"):
                    # FastAPI also adds a 422 response to endpoints that do not take
                    # parameters that can be invalidated. Since header-invalidation is
                    # currently not supported, these endpoints can be filtered by a
                    # generic flag
                    if (
                        response == "422"
                        and method in ["get", "delete"]
                        and ignore_fastapi_default_422
                    ):
                        continue
                    # default applies to all status codes that are not specified, in
                    # which case we don't know what to expect and thus can't verify
                    if (
                        response == "default"
                        or response in ignore_list
                        or Test(endpoint, method, response) in ignored_tests
                    ):
                        continue
                    tag_list: List[str] = []
                    if tags := method_data.get("tags", None):
                        tag_list.extend(tags)
                    tag_list.append(f"Method: {method.upper()}")
                    tag_list.append(f"Response: {response}")
                    test_data.append(
                        TestCaseData(
                            arguments={
                                "${endpoint}": endpoint,
                                "${method}": method.upper(),
                                "${status_code}": response,
                            },
                            tags=tag_list,
                        )
                    )
        return test_data
