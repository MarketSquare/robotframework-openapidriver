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

> Note: OpenApiDriver is still under development so there are currently
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
each path, method and response (i.e. every response for each endpoint) that is defined
in an OpenAPI document, typically an openapi.json or openapi.yaml file.

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
prance validate --backend=openapi-spec-validator http://localhost:8000/openapi.json
Processing "http://localhost:8000/openapi.json"...
 -> Resolving external references.
Validates OK as OpenAPI 3.0.2!

prance validate --backend=openapi-spec-validator /tests/files/petstore_openapi.yaml
Processing "/tests/files/petstore_openapi.yaml"...
 -> Resolving external references.
Validates OK as OpenAPI 3.0.2!
```

You'll have to change the url or file reference to the location of the openapi
document for your API.

> Note: Although recursion is technically allowed under the OAS, tool support is limited
and changing the OAS to not use recursion is recommended.
OpenApiDriver has limited support for parsing OpenAPI documents with
recursion in them. See the `recursion_limit` and `recursion_default` parameters.

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
Test Endpoint for ${method} on ${path} where ${status_code} is expected

*** Keywords ***
Validate Using Test Endpoint Keyword
    [Arguments]    ${path}    ${method}    ${status_code}
    Test Endpoint
    ...    path=${path}    method=${method}    status_code=${status_code}

```

Running the above suite for the first time is likely to result in some
errors / failed tests.
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
- Only JSON request and response bodies are supported.
- No support for per-path authorization levels (only simple 401 / 403 validation).

"""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

from DataDriver import DataDriver
from requests.auth import AuthBase
from requests.cookies import RequestsCookieJar as CookieJar
from robot.api.deco import library

from OpenApiDriver.openapi_executors import OpenApiExecutors, ValidationLevel
from OpenApiDriver.openapi_reader import OpenApiReader


@library(scope="TEST SUITE", doc_format="ROBOT")
class OpenApiDriver(OpenApiExecutors, DataDriver):
    """
    Visit the [https://github.com/MarketSquare/robotframework-openapidriver | library page]
    for an introduction and examples.
    """

    def __init__(  # pylint: disable=too-many-arguments, too-many-locals, dangerous-default-value
        self,
        source: str,
        origin: str = "",
        base_path: str = "",
        included_paths: Optional[Iterable[str]] = None,
        ignored_paths: Optional[Iterable[str]] = None,
        ignored_responses: Optional[Iterable[int]] = None,
        ignored_testcases: Optional[Iterable[Tuple[str, str, int]]] = None,
        response_validation: ValidationLevel = ValidationLevel.WARN,
        disable_server_validation: bool = True,
        mappings_path: Union[str, Path] = "",
        invalid_property_default_response: int = 422,
        default_id_property_name: str = "id",
        faker_locale: Optional[Union[str, List[str]]] = None,
        require_body_for_invalid_url: bool = False,
        recursion_limit: int = 1,
        recursion_default: Any = {},
        username: str = "",
        password: str = "",
        security_token: str = "",
        auth: Optional[AuthBase] = None,
        cert: Optional[Union[str, Tuple[str, str]]] = None,
        verify_tls: Optional[Union[bool, str]] = True,
        extra_headers: Optional[Dict[str, str]] = None,
        cookies: Optional[Union[Dict[str, str], CookieJar]] = None,
        proxies: Optional[Dict[str, str]] = None,
    ):
        """
         == Base parameters ==

         === source ===
         An absolute path to an openapi.json or openapi.yaml file or an url to such a file.

         === origin ===
         The server (and port) of the target server. E.g. ``https://localhost:8000``

        === base_path ===
         The routing between ``origin`` and the endpoints as found in the ``paths``
         section in the openapi document.
         E.g. ``/petshop/v2``.

         == Test case generation and execution ==

         === included_paths ===
         A list of paths that will be included when generating the test cases.
         The ``*`` character can be used at the end of a partial path to include all paths
         starting with the partial path (wildcard include).

         === ignored_paths ===
         A list of paths that will be ignored when generating the test cases.
         The ``*`` character can be used at the end of a partial path to ignore all paths
         starting with the partial path (wildcard ignore).

         === ignored_responses ===
         A list of responses that will be ignored when generating the test cases.

         === ignored_testcases ===
         A list of specific test cases that, if it would be generated, will be ignored.
         Specific test cases to ignore must be specified as a ``Tuple`` or ``List``
         of ``path``, ``method`` and ``response``.

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

         == API-specific configurations ==

         === mappings_path ===
         See [https://marketsquare.github.io/robotframework-openapi-libcore/advanced_use.html | this page]
         for an in-depth explanation.

         === invalid_property_default_response ===
         The default response code for requests with a JSON body that does not comply
         with the schema.
         Example: a value outside the specified range or a string value
         for a property defined as integer in the schema.

         === default_id_property_name ===
         The default name for the property that identifies a resource (i.e. a unique
         entity) within the API.
         The default value for this property name is ``id``.
         If the target API uses a different name for all the resources within the API,
         you can configure it globally using this property.

         If different property names are used for the unique identifier for different
         types of resources, an ``ID_MAPPING`` can be implemented using the ``mappings_path``.

         === faker_locale ===
         A locale string or list of locale strings to pass to the Faker library to be
         used in generation of string data for supported format types.

         === require_body_for_invalid_url ===
         When a request is made against an invalid url, this usually is because of a "404" request;
         a request for a resource that does not exist. Depending on API implementation, when a
         request with a missing or invalid request body is made on a non-existent resource,
         either a 404 or a 422 or 400 Response is normally returned. If the API being tested
         processes the request body before checking if the requested resource exists, set
         this parameter to True.

         == Parsing parameters ==

         === recursion_limit ===
         The recursion depth to which to fully parse recursive references before the
         `recursion_default` is used to end the recursion.

         === recursion_default ===
         The value that is used instead of the referenced schema when the
         `recursion_limit` has been reached.
         The default `{}` represents an empty object in JSON.
         Depending on schema definitions, this may cause schema validation errors.
         If this is the case, 'None' (``${NONE}`` in Robot Framework) or an empty list
         can be tried as an alternative.

         == Security-related parameters ==
         _Note: these parameters are equivalent to those in the ``requests`` library._

         === username ===
         The username to be used for Basic Authentication.

         === password ===
         The password to be used for Basic Authentication.

         === security_token ===
         The token to be used for token based security using the ``Authorization`` header.

         === auth ===
         A [https://requests.readthedocs.io/en/latest/api/#authentication | requests ``AuthBase`` instance]
         to be used for authentication instead of the ``username`` and ``password``.

         === cert ===
         The SSL certificate to use with all requests.
         If string: the path to ssl client cert file (.pem).
         If tuple: the ('cert', 'key') pair.

         === verify_tls ===
         Whether or not to verify the TLS / SSL certificate of the server.
         If boolean: whether or not to verify the server TLS certificate.
         If string: path to a CA bundle to use for verification.

         === extra_headers ===
         A dictionary with extra / custom headers that will be send with every request.
         This parameter can be used to send headers that are not documented in the
         openapi document or to provide an API-key.

         === cookies ===
         A dictionary or [https://docs.python.org/3/library/http.cookiejar.html#http.cookiejar.CookieJar | CookieJar object]
         to send with all requests.

         === proxies ===
         A dictionary of 'protocol': 'proxy url' to use for all requests.
        """
        included_paths = included_paths if included_paths else ()
        ignored_paths = ignored_paths if ignored_paths else ()
        ignored_responses = ignored_responses if ignored_responses else ()
        ignored_testcases = ignored_testcases if ignored_testcases else ()

        mappings_path = Path(mappings_path).as_posix()
        OpenApiExecutors.__init__(
            self,
            source=source,
            origin=origin,
            base_path=base_path,
            response_validation=response_validation,
            disable_server_validation=disable_server_validation,
            mappings_path=mappings_path,
            invalid_property_default_response=invalid_property_default_response,
            default_id_property_name=default_id_property_name,
            faker_locale=faker_locale,
            require_body_for_invalid_url=require_body_for_invalid_url,
            recursion_limit=recursion_limit,
            recursion_default=recursion_default,
            username=username,
            password=password,
            security_token=security_token,
            auth=auth,
            cert=cert,
            verify_tls=verify_tls,
            extra_headers=extra_headers,
            cookies=cookies,
            proxies=proxies,
        )

        paths = self.openapi_spec["paths"]
        DataDriver.__init__(
            self,
            reader_class=OpenApiReader,
            paths=paths,
            included_paths=included_paths,
            ignored_paths=ignored_paths,
            ignored_responses=ignored_responses,
            ignored_testcases=ignored_testcases,
        )


class DocumentationGenerator(OpenApiDriver):
    __doc__ = OpenApiDriver.__doc__

    @staticmethod
    def get_keyword_names() -> List[str]:
        """Curated keywords for libdoc and libspec."""
        return [
            "test_unauthorized",
            "test_invalid_url",
            "test_endpoint",
        ]  # pragma: no cover
