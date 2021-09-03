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

If you already have Python >= 3.7 with pip installed, you can simply
run:

``pip install --upgrade robotframework-openapidriver``


Table of contents
-----------------

-  `What DataDriver Does`_
-  `How DataDriver Works`_
-  `Usage`_


What DataDriver Does
--------------------

DataDriver is an alternative approach to create Data-Driven Tests with
Robot Framework®. DataDriver creates multiple test cases based on a test
template and data content of a csv or Excel file. All created tests
share the same test sequence (keywords) and differ in the test data.
Because these tests are created on runtime only the template has to be
specified within the robot test specification and the used data are
specified in an external data file.


How DataDriver Works
--------------------

When the DataDriver is used in a test suite it will be activated before
the test suite starts. It uses the Listener Interface Version 3 of Robot
Framework® to read and modify the test specification objects. After
activation it searches for the ``Test Template`` -Keyword to analyze the
``[Arguments]`` it has. As a second step, it loads the data from the
specified data source. Based on the ``Test Template`` -Keyword, DataDriver
creates as much test cases as data sets are in the data source.

In the case that data source is csv (Default)
As values for the arguments of the ``Test Template`` -Keyword, DataDriver
reads values from the column of the CSV file with the matching name of the
``[Arguments]``.
For each line of the CSV data table, one test case will be created. It
is also possible to specify test case names, tags and documentation for
each test case in the specific test suite related CSV file.


Usage
-----

Data Driver is a "Library Listener" but does not provide keywords.
Because Data Driver is a listener and a library at the same time it
sets itself as a listener when this library is imported into a test suite.

To use it, just use it as Library in your suite. You may use the first
argument (option) which may set the file name or path to the data file.

Without any options set, it loads a .csv file which has the same name
and path like the test suite .robot .



**Example:**

.. code :: robotframework

    *** Settings ***
    Library    DataDriver
    Test Template    Invalid Logins

    *** Keywords ***
    Invalid Logins
        ...


Structure of Test Suite
-----------------------


Requirements
~~~~~~~~~~~~

In the Moment there are some requirements how a test
suite must be structured so that the DataDriver can get all the
information it needs.

 - only the first test case will be used as a template. All other test
   cases will be deleted.
 - Test cases have to be defined with a
   ``Test Template`` in Settings secion. Reason for this is,
   that the DataDriver needs to know the names of the test case arguments.
   Test cases do not have named arguments. Keywords do.
 - The keyword which is used as
   ``Test Template`` must be defined within the test suite (in the same
   \*.robot file). If the keyword which is used as ``Test Template`` is
   defined in a ``Resource`` the DataDriver has no access to its
   arguments names.


Example Test Suite
~~~~~~~~~~~~~~~~~~

.. code :: robotframework

    ***Settings***
    Library           DataDriver
    Resource          login_resources.robot
    Suite Setup       Open my Browser
    Suite Teardown    Close Browsers
    Test Setup        Open Login Page
    Test Template     Invalid Login

    *** Test Case ***
    Login with user ${username} and password ${password}    Default    UserData

    ***** *Keywords* *****
    Invalid login
        [Arguments]    ${username}    ${password}
        Input username    ${username}
        Input pwd    ${password}
        click login button
        Error page should be visible

In this example, the DataDriver is activated by using it as a Library.
It is used with default settings.
As ``Test Template`` the keyword ``Invalid Login`` is used. This
keyword has two arguments. Argument names are ``${username}`` and
``${password}``. These names have to be in the CSV file as column
header. The test case has two variable names included in its name,
which does not have any functionality in Robot Framework®. However, the
Data Driver will use the test case name as a template name and
replaces the variables with the specific value of the single generated
test case.
This template test will only be used as a template. The specified data
``Default`` and ``UserData`` would only be used if no CSV file has
been found.


OpenAPI (aka Swagger)
~~~~~~~~~~~~~~~~~~~~~

The OpenAPI Specification (OAS) defines a standard, language-agnostic interface to RESTful APIs.
https://swagger.io/specification/

The openapi module implements a reader class that generates a test case for each
endpoint, method and response that is defined in an OpenAPI document, typically
an openapi.json or openapi.yaml file.


How it works
^^^^^^^^^^^^

If the openapi_reader is used and the file has the .json or .yaml extension, it will be
loaded by the prance module and the test cases will be generated.

.. code :: robotframework

    *** Settings ***
    Library            DataDriver    reader_class=openapi_reader
    ...                    file=openapi.json
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
    Library            DataDriver    reader_class=openapi_reader
    ...                    url=http://127.0.0.1:8000/openapi.json


Since the OpenAPI document is essentially a contract that specifies what operations are
supported and what data needs to be send and will be returned, it is possible to
automatically validate the API against this contract. For this purpose, the openapi
module also implements a number of keywords.


Validate OpenAPI Document
^^^^^^^^^^^^^^^^^^^^^^^^^

The Validate OpenAPI Document is intended to be used in the Suite Setup and will validate
the OpenAPI document against the OpenAPI v3 specification. All errors encountered will
be logged and the keyword fails if any errors are found. This keyword can be used in
Test Setup to Skip test execution for the generated Test Cases if the document is
invalid to prevent a great number of failed test cases.


Test Endpoint
^^^^^^^^^^^^^

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
