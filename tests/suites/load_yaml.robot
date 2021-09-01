*** Settings ***
Library            OpenApiDriver
...                    source=${root}/tests/files/petstore_openapi.yaml
Suite Setup        Validate OpenAPI specification
Test Template      Do Nothing


*** Test Cases ***
Some OpenAPI test for ${method} on ${endpoint} where ${status_code} is expected

*** Keywords *** ***
Do Nothing
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    No Operation

Validate OpenAPI specification
    [Documentation]
    ...    Validate the retrieved document against the OpenApi 3.0 specification
    Validate OpenAPI Document
