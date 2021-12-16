# region: docstring
"""
# OpenApiDriver for Robot Framework®

OpenApiDriver is an extension of the Robot Framework® DataDriver library that allows
for generation and execution of test cases based on the information in an OpenAPI
document (also known as Swagger document).
This document explains how to use the OpenApiDriver library.

For more information about Robot Framework®, see http://robotframework.org.

For more information about the DataDriver library, see
https://github.com/Snooz82/robotframework-datadriver.

---

> Note: OpenApiDriver is currently in early development so there are currently
restrictions / limitations that you may encounter when using this library to run
tests against an API. See [Limitations](#limitations) for details.

---

## Installation

If you already have Python >= 3.8 with pip installed, you can simply run:

`pip install --upgrade robotframework-openapidriver`

---

## OpenAPI (aka Swagger)

The OpenAPI Specification (OAS) defines a standard, language-agnostic interface
to RESTful APIs, see https://swagger.io/specification/

The OpenApiDriver module implements a reader class that generates a test case for
each endpoint, method and response that is defined in an OpenAPI document, typically
an openapi.json or openapi.yaml file.

> Note: OpenApiDriver is designed for APIs based on the OAS v3
The library has not been tested for APIs based on the OAS v2.

---

## Getting started

Before trying to use OpenApiDriver to run automatic validations on the target API
it's recommended to first ensure that the openapi document for the API is valid
under the OpenAPI Specification.

This can be done using the command line interface of a package that is installed as
a prerequisite for OpenApiDriver.
Both a local openapi.json or openapi.yaml file or one hosted by the API server
can be checked using the `prance validate <reference_to_file>` shell command:

```shell
prance validate http://localhost:8000/openapi.json
Processing "http://localhost:8000/openapi.json"...
 -> Resolving external references.
Validates OK as OpenAPI 3.0.2!

prance validate /tests/files/petstore_openapi.yaml
Processing "/tests/files/petstore_openapi.yaml"...
 -> Resolving external references.
Validates OK as OpenAPI 3.0.2!
```

You'll have to change the url or file reference to the location of the openapi
document for your API.

If the openapi document passes this validation, the next step is trying to do a test
run with a minimal test suite.
The example below can be used, with `source` and `origin` altered to fit your situation.

``` robotframework
*** Settings ***
Library            OpenApiDriver
...                    source=http://localhost:8000/openapi.json
...                    origin=http://localhost:8000
Test Template      Validate Using Test Endpoint Keyword

*** Test Cases ***
Test Endpoint for ${method} on ${endpoint} where ${status_code} is expected

*** Keywords ***
Validate Using Test Endpoint Keyword
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    Test Endpoint
    ...    endpoint=${endpoint}    method=${method}    status_code=${status_code}

```

Running the above suite for the first time is likely to result in some
errors / failed testes.
You should look at the Robot Framework `log.html` to determine the reasons
for the failing tests.
Depending on the reasons for the failures, different solutions are possible.

Details about the OpenApiDriver library parameters that you may need can be found
[here](https://marketsquare.github.io/robotframework-openapidriver/openapidriver.html).

The OpenApiDriver also support handling of relations between resources within the scope
of the API being validated as well as handling dependencies on resources outside the
scope of the API. In addition there is support for handling restrictions on the values
of parameters and properties.

Details about the `mappings_path` variable usage can be found
[here](https://marketsquare.github.io/robotframework-openapi-libcore/advanced_use.html).

---

## Limitations

There are currently a number of limitations to supported API structures, supported
data types and properties. The following list details the most important ones:
- Only JSON request and response bodies are currently supported.
- The unique identifier for a resource as used in the `paths` section of the
    openapi document is expected to be the `id` property on a resource of that type.
- Limited support for query strings and headers.
- Limited support for authentication
    - `username` and `password` can be passed as parameters to use Basic Authentication
    - A [requests AuthBase instance](https://docs.python-requests.org/en/latest/api/#authentication)
        can be passed and it will be used as provided.
    - No support for per-endpoint authorization levels (just simple 401 validation).
- byte, binary, date, date-time string formats not supported yet.

"""
# region
from importlib.metadata import version
from pathlib import Path
from typing import List, Optional, Union

from DataDriver import DataDriver
from DataDriver.AbstractReaderClass import AbstractReaderClass
from requests.auth import AuthBase
from robot.api.deco import library

from OpenApiDriver.openapi_executors import OpenApiExecutors, ValidationLevel
from OpenApiDriver.openapi_reader import OpenApiReader

try:
    __version__ = version("robotframework-openapidriver")
except:  # pragma: no cover
    __version__ = "unknown"


@library(scope="TEST SUITE", version=__version__, doc_format="ROBOT")
class OpenApiDriver(OpenApiExecutors, DataDriver):
    """
    Visit the [https://github.com/MarketSquare/robotframework-openapidriver | library page]
    for an introduction and examples.
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-locals
        self,
        source: str,
        ignored_endpoints: Optional[List[str]] = None,
        ignored_responses: Optional[List[int]] = None,
        ignored_testcases: Optional[List[List[str]]] = None,
        ignore_fastapi_default_422: bool = False,
        origin: str = "",
        base_path: str = "",
        mappings_path: Union[str, Path] = "",
        username: str = "",
        password: str = "",
        security_token: str = "",
        auth: Optional[AuthBase] = None,
        response_validation: ValidationLevel = ValidationLevel.WARN,
        disable_server_validation: bool = True,
        require_body_for_invalid_url: bool = False,
        invalid_property_default_response: int = 422,
    ):
        # region: docstring
        """
        === source ===
        An absolute path to an openapi.json or openapi.yaml file or an url to such a file.

        === ignored_endpoints ===
        A list of endpoints that will be ignored when generating the test cases.

        === ignored_responses ===
        A list of responses that will be ignored when generating the test cases.

        === ignored_testcases ===
        A list of specific test cases that, if it would be generated, will be ignored.
        Specific test cases to ignore must be specified as a ``List`` of ``endpoint``,
        ``method`` and ``response``.

        === ignore_fastapi_default_422 ===
        The FastAPI framework generates an openapi.json that, by default, has a 422 response
        for almost every endpoint. In some cases, this response can only be triggered by
        request header invalidation, which is currently not supported. When testing a FastApi
        webserver, you can set this argument to ``True``

        === origin ===
        The server (and port) of the target server. E.g. ``https://localhost:7000``

        === base_path ===
        The routing between ``origin`` and the endpoints as found in the ``paths`` in the
        openapi document. E.g. ``/petshop/v2``.

        === mappings_path ===
        See [https://marketsquare.github.io/robotframework-openapi-libcore/advanced_use.html | here].

        === username ===
        The username to be used for Basic Authentication.

        === password ===
        The password to be used for Basic Authentication.

        === security_token ===
        The token to be used for token based security using the ``Authorization`` header.

        === auth ===
        A [https://docs.python-requests.org/en/latest/api/#authentication | requests AuthBase instance]
        to be used for authentication instead of the ``username`` and ``password``.

        === response_validation ===
        By default, a ``WARN`` is logged when the Response received after a Request does not
        comply with the schema as defined in the openapi document for the given operation. The
        following values are supported:

        - ``DISABLED``: All Response validation errors will be ignored
        - ``INFO``: Any Response validation erros will be logged at ``INFO`` level
        - ``WARN``: Any Response validation erros will be logged at ``WARN`` level
        - ``STRICT``: The Test Case will fail on any Response validation errors

        === disable_server_validation ===
        If enabled by setting this parameter to ``True``, the Response validation will also
        include possible errors for Requests made to a server address that is not defined in
        the list of servers in the openapi document. This generally means that if there is a
        mismatch, every Test Case will raise this error. Note that ``localhost`` and
        ``127.0.0.1`` are not considered the same by Response validation.

        === require_body_for_invalid_url ===
        When a request is made against an invalid url, this usually is because of a "404" request;
        a request for a resource that does not exist. Depending on API implementation, when a
        request with a missing or invalid request body is made on a non-existent resource,
        either a 404 or a 422 or 400 Response is normally returned. If the API being tested
        processes the request body before checking if the requested resource exists, set
        this parameter to True.

        === invalid_property_default_response ===
        The default response code for requests with a JSON body that does not comply with
        the schema. Example: a value outside the specified range or a string value for a
        property defined as integer in the schema.
        """
        # endregion
        ignored_endpoints = ignored_endpoints if ignored_endpoints else []
        ignored_responses = ignored_responses if ignored_responses else []
        ignored_testcases = ignored_testcases if ignored_testcases else []

        mappings_path = Path(mappings_path).as_posix()
        OpenApiExecutors.__init__(
            self,
            source=source,
            origin=origin,
            base_path=base_path,
            mappings_path=mappings_path,
            username=username,
            password=password,
            security_token=security_token,
            auth=auth,
            response_validation=response_validation,
            disable_server_validation=disable_server_validation,
            require_body_for_invalid_url=require_body_for_invalid_url,
            invalid_property_default_response=invalid_property_default_response,
        )

        endpoints = self.openapi_spec["paths"]
        DataDriver.__init__(
            self,
            # FIXME: Enable when DataDriver accepts AbstractReaderClass subclasses
            # reader_class=OpenApiReader
            reader_class="openapi_reader",
            endpoints=endpoints,
            ignored_endpoints=ignored_endpoints,
            ignored_responses=ignored_responses,
            ignored_testcases=ignored_testcases,
            ignore_fastapi_default_422=ignore_fastapi_default_422,
        )

    # FIXME: Hack to allow directly loading the OpenApiReader - remove when DataDriver
    # accepts an AbstractReaderClass subclass as reader_class argument
    def _data_reader(self) -> AbstractReaderClass:
        return OpenApiReader(self.reader_config)

    @staticmethod
    def get_keyword_names():
        """Curated keywords for libdoc and libspec."""
        return ["test_unauthorized", "test_invalid_url", "test_endpoint"]
