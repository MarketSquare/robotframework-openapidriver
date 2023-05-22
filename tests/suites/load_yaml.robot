*** Settings ***
Library             OpenApiDriver
...                     source=${ROOT}/tests/files/petstore_openapi.yaml
...                     included_paths=${INCLUDED_PATHS}
...                     ignored_paths=${IGNORED_PATHS}

Test Template       Do Nothing


*** Variables ***
@{INCLUDED_PATHS}=
...                     /pet/{petId}/uploadImage
...                     /user*
@{IGNORED_PATHS}=
...                     /user/createWithList    /user/l*


*** Test Cases ***
OpenApiYaml test for ${method} on ${path} where ${status_code} is expected


*** Keywords ***
Do Nothing
    [Arguments]    ${path}    ${method}    ${status_code}
    No Operation
