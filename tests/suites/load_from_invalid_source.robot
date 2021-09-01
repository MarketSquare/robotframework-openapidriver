*** Settings ***
Library            OpenApiDriver
...                    source=http://127.0.0.1:8000/openapi.doc
...                    origin=http://127.0.0.1:8000
...                    base_path=${EMPTY}
Test Template      Validate Test Endpoint Keyword


*** Test Cases ***
Test Endpoint for ${method} on ${endpoint} where ${status_code} is expected


*** Keywords *** ***
Validate Test Endpoint Keyword
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    No Operation
