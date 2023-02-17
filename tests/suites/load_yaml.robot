*** Settings ***
Library             OpenApiDriver
...                     source=${ROOT}/tests/files/petstore_openapi.yaml
...                     ignored_endpoints=${ignored_endpoints}

Test Template       Do Nothing


*** Variables ***
@{ignored_endpoints}=
...                         /pet    /pet/findByStatus    /pet/findByTags    /pet/{petId}
...                         /store/inventory    /store/order    /store/order/{orderId}
...                         /user/createWithList    /user/login    /user/{username}


*** Test Cases ***
openapi.yaml test for ${method} on ${endpoint} where ${status_code} is expected


*** Keywords ***
Do Nothing
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    No Operation
