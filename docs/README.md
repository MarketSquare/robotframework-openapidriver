---
---

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

``pip install --upgrade robotframework-openapidriver``

---
## OpenAPI (aka Swagger)

The OpenAPI Specification (OAS) defines a standard, language-agnostic interface
to RESTful APIs, see https://swagger.io/specification/

The OpenApiDriver module implements a reader class that generates a test case for
each endpoint, method and response that is defined in an OpenAPI document, typically
an openapi.json or openapi.yaml file.

---
## How it works

If the source file has the .json or .yaml extension, it will be loaded by the
library (using the prance library under the hood) and the test cases will be generated.

``` robotframework
*** Settings ***
Library            OpenApiDriver
...                    source=openapi.json
Test Template      Do Nothing


*** Test Cases ***
Some OpenAPI test for ${method} on ${endpoint} where ${status_code} is expected

*** Keywords *** ***
Do Nothing
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    No Operation
```

It is also possible to load the openapi.json / openapi.yaml directly from the
server by using the url instead of a local file:

``` robotframework
*** Settings ***
Library            OpenApiDriver
...                    source=http://127.0.0.1:8000/openapi.json
```

Since the OpenAPI document is essentially a contract that specifies what operations are
supported and what data needs to be send and will be returned, it is possible to
automatically validate the API against this contract. For this purpose, the openapi
module also implements a number of keywords.

Details about the Keywords can be found
[here](https://marketsquare.github.io/robotframework-openapidriver/openapidriver.html).

The OpenApiDriver also support handling of relations between resources within the scope
of the API being validated as well as handling dependencies on resources outside the
scope of the API. In addition there is support for handling restrictions on the values
of parameters and properties.
Details about the `mappings_path` variable usage can be found
[here](https://marketsquare.github.io/robotframework-openapidriver/advanced_use.md).

---
## Limitations

There are currently a number of limitations to supported API structures, supported
data types and properties. The following list details the most important ones:
- Only JSON request and response bodies are currently supported.
- The unique identifier for a resource as used in the ``paths`` section of the
    openapi document is expected to be the ``id`` property on a resource of that type.
- Limited support for query strings.
- No support for headers at this time.
- Limited support for authentication
    - ``username`` and ``password`` can be passed as parameters to use Basic Authentication
    - A [requests AuthBase instance](https://docs.python-requests.org/en/latest/api/#authentication)
        can be passed and it will be used as provided.
    - No support for per-endpoint authorization levels (just simple 401 validation).
- ``exclusiveMinimum`` and ``exclusiveMaximum`` not supported yet.
- byte, binary, date, date-time string formats not supported yet.

