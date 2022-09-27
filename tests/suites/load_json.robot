*** Settings ***
Library             OpenApiDriver
...                     source=${ROOT}/tests/files/petstore_openapi.json
...                     ignored_responses=${ignored_responses}
...                     ignored_testcases=${ignored_tests}

Test Template       Do Nothing


*** Variables ***
@{ignored_responses}=       200    404    400
@{ignore_post_pet}=         /pet    POST    405
@{ignore_post_pet_id}=      /pet/{petId}    post    405
@{ignore_post_order}=       /store/order    post    405
@{ignored_tests}=           ${ignore_post_pet}    ${ignore_post_pet_id}    ${ignore_post_order}


*** Test Cases ***
openapi.json test for ${method} on ${endpoint} where ${status_code} is expected


*** Keywords ***
Do Nothing
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    No Operation
