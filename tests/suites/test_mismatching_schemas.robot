*** Settings ***
Variables           ${ROOT}/tests/variables.py
Library             OpenApiDriver
...                     source=${ROOT}/tests/files/mismatched_openapi.json
...                     origin=http://localhost:8000
...                     base_path=${EMPTY}
...                     mappings_path=${ROOT}/tests/user_implemented/custom_user_mappings.py
...                     response_validation=INFO
...                     require_body_for_invalid_url=${TRUE}
...                     extra_headers=${API_KEY}
...                     faker_locale=nl_NL
...                     default_id_property_name=identification

Test Template       Validate Test Endpoint Keyword


*** Variables ***
@{expected_failures}
...                     GET /reactions/ 200
...                     POST /employees 201
...                     GET /employees 200
...                     PATCH /employees/{employee_id} 200
...                     GET /employees/{employee_id} 200
...                     GET /available_employees 200


*** Test Cases ***
Test Endpoint for ${method} on ${endpoint} where ${status_code} is expected


*** Keywords ***
Validate Test Endpoint Keyword
    [Arguments]    ${endpoint}    ${method}    ${status_code}
    IF    ${status_code} == 404
        Test Invalid Url    endpoint=${endpoint}    method=${method}
    ELSE
        ${operation}=    Set Variable    ${method}${SPACE}${endpoint}${SPACE}${status_code}
        IF    $operation in $expected_failures
            Run Keyword And Expect Error    *    Test Endpoint
            ...    endpoint=${endpoint}    method=${method}    status_code=${status_code}
        ELSE
            Test Endpoint
            ...    endpoint=${endpoint}    method=${method}    status_code=${status_code}
        END
    END
