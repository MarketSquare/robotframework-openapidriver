from pathlib import Path
from typing import List, Optional, Union

from OpenApiDriver.openapi_reader import OpenApiReader
from OpenApiDriver.openapi_executors import OpenapiExecutors, ValidationLevel

from DataDriver import DataDriver
from DataDriver.AbstractReaderClass import AbstractReaderClass
from requests.auth import AuthBase
from robotlibcore import DynamicCore

class OpenApiDriver(DataDriver, DynamicCore):
# region: docstring
    """
===================================================
OpenApiDriver for Robot Framework®
===================================================

OpenDriver is an extension of the Robot Framework® DataDriver library that allows for
generation and execution of test cases based on the information in an OpenAPI document
(also known as Swagger document).
This document explains how to use the OpenApiDriver library.

For more information about Robot Framework®, see http://robotframework.org.
For more information about the DataDriver library, see
https://github.com/Snooz82/robotframework-datadriver.


Installation
------------

If you already have Python >= 3.8 with pip installed, you can simply run:

``pip install --upgrade robotframework-openapidriver``

OpenAPI (aka Swagger)
~~~~~~~~~~~~~~~~~~~~~

The OpenAPI Specification (OAS) defines a standard, language-agnostic interface to RESTful APIs.
https://swagger.io/specification/

The openapi module implements a reader class that generates a test case for each
endpoint, method and response that is defined in an OpenAPI document, typically
an openapi.json or openapi.yaml file.


How it works
^^^^^^^^^^^^

If the source file has the .json or .yaml extension, it will be
loaded by the prance module and the test cases will be generated.

.. code :: robotframework

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

It is also possible to load the openapi.json / openapi.yaml directly from the server
by using the url instead of a local file:

.. code :: robotframework

    *** Settings ***
    Library            OpenApiDriver
    ...                    source=http://127.0.0.1:8000/openapi.json


Since the OpenAPI document is essentially a contract that specifies what operations are
supported and what data needs to be send and will be returned, it is possible to
automatically validate the API against this contract. For this purpose, the openapi
module also implements a number of keywords.

"""
# endregion
    def __init__(
            self,
            source: str,
            ignored_endpoints: Optional[List[str]] = None,
            ignored_responses: Optional[List[int]] = None,
            ignored_testcases: Optional[List[List[str]]] = None,
            ignore_fastapi_default_422: Optional[bool] = None,
            origin: str = "",
            base_path: str = "",
            mappings_path: Union[str, Path] = "",
            username: str = "",
            password: str = "",
            auth: Optional[AuthBase] = None,
            response_validation: ValidationLevel = ValidationLevel.WARN,
        ):
        DataDriver.__init__(self,
            #FIXME: Enable when DataDriver accepts AbstractReaderClass subclasses
            # reader_class=OpenApiReader
            reader_class="openapi_reader",
            source=source,
            ignored_endpoints = ignored_endpoints,
            ignored_responses = ignored_responses,
            ignored_testcases = ignored_testcases,
            ignore_fastapi_default_422 = ignore_fastapi_default_422,
        )

        mappings_path = Path(mappings_path).as_posix()
        openapi_executors = OpenapiExecutors(
            source=source,
            origin=origin,
            base_path=base_path,
            mappings_path=mappings_path,
            username=username,
            password=password,
            auth=auth,
            response_validation=response_validation
        )
        DynamicCore.__init__(self, [openapi_executors])

    #FIXME: Hack to allow directly loading the OpenApiReader - remove when DataDriver
    # accepts an AbstractReaderClass subclass as reader_class argument
    def _data_reader(self) -> AbstractReaderClass:
        return OpenApiReader(self.reader_config)

# Support Robot Framework import mechanism
openapidriver = OpenApiDriver    # pylint: disable=invalid-name
