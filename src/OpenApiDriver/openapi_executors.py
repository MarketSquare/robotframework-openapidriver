"""Module containing the classes to perform automatic OpenAPI contract validation."""

import json as _json
from dataclasses import asdict
from enum import Enum
from logging import getLogger
from pathlib import Path
from random import choice
from typing import Any, Dict, List, Optional, Union

from openapi_core.contrib.requests import (
    RequestsOpenAPIRequest,
    RequestsOpenAPIResponse,
)
from openapi_core.templating.paths.exceptions import ServerNotFound
from OpenApiLibCore import OpenApiLibCore, RequestData, RequestValues, resolve_schema
from requests import Response
from requests.auth import AuthBase
from robot.api import SkipExecution
from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

run_keyword = BuiltIn().run_keyword


logger = getLogger(__name__)


class ValidationLevel(str, Enum):
    """The available levels for the response_validation parameter."""

    DISABLED = "DISABLED"
    INFO = "INFO"
    WARN = "WARN"
    STRICT = "STRICT"


@library(scope="TEST SUITE", doc_format="ROBOT")
class OpenApiExecutors(OpenApiLibCore):  # pylint: disable=too-many-instance-attributes
    """Main class providing the keywords and core logic to perform endpoint validations."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        source: str,
        origin: str = "",
        base_path: str = "",
        mappings_path: Union[str, Path] = "",
        username: str = "",
        password: str = "",
        security_token: str = "",
        auth: Optional[AuthBase] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        response_validation: ValidationLevel = ValidationLevel.WARN,
        disable_server_validation: bool = True,
        require_body_for_invalid_url: bool = False,
        invalid_property_default_response: int = 422,
    ) -> None:
        super().__init__(
            source=source,
            origin=origin,
            base_path=base_path,
            mappings_path=mappings_path,
            username=username,
            password=password,
            security_token=security_token,
            auth=auth,
            extra_headers=extra_headers,
        )
        self.response_validation = response_validation
        self.disable_server_validation = disable_server_validation
        self.require_body_for_invalid_url = require_body_for_invalid_url
        self.invalid_property_default_response = invalid_property_default_response

    @keyword
    def test_unauthorized(self, endpoint: str, method: str) -> None:
        """
        Perform a request for `method` on the `endpoint`, with no authorization.

        This keyword only passes if the response code is 401: Unauthorized.

        Any authorization parameters used to initialize the library are
        ignored for this request.
        > Note: No headers or (json) body are send with the request. For security
        reasons, the authorization validation should be checked first.
        """
        url: str = run_keyword("get_valid_url", endpoint, method)
        response = self.session.request(
            method=method,
            url=url,
            verify=False,
        )
        assert response.status_code == 401

    @keyword
    def test_invalid_url(
        self, endpoint: str, method: str, expected_status_code: int = 404
    ) -> None:
        """
        Perform a request for the provided 'endpoint' and 'method' where the url for
        the `endpoint` is invalidated.

        This keyword will be `SKIPPED` if the endpoint contains no parts that
        can be invalidated.

        The optional `expected_status_code` parameter (default: 404) can be set to the
        expected status code for APIs that do not return a 404 on invalid urls.

        > Note: Depending on API design, the url may be validated before or after
        validation of headers, query parameters and / or (json) body. By default, no
        parameters are send with the request. The `require_body_for_invalid_url`
        parameter can be set to `True` if needed.
        """
        valid_url: str = run_keyword("get_valid_url", endpoint, method)

        if not (url := run_keyword("get_invalidated_url", valid_url)):
            raise SkipExecution(
                f"Endpoint {endpoint} does not contain resource references that "
                f"can be invalidated."
            )

        params, headers, json_data = None, None, None
        if self.require_body_for_invalid_url:
            request_data = self.get_request_data(method=method, endpoint=endpoint)
            params = request_data.params
            headers = request_data.headers
            dto = request_data.dto
            json_data = asdict(dto)
        response: Response = run_keyword(
            "authorized_request", url, method, params, headers, json_data
        )
        if response.status_code != expected_status_code:
            raise AssertionError(
                f"Response {response.status_code} was not {expected_status_code}"
            )

    @keyword
    def test_endpoint(self, endpoint: str, method: str, status_code: int) -> None:
        """
        Validate that performing the `method` operation on `endpoint` results in a
        `status_code` response.

        This is the main keyword to be used in the `Test Template` keyword when using
        the OpenApiDriver.

        The keyword calls other keywords to generate the neccesary data to perform
        the desired operation and validate the response against the openapi document.
        """
        json_data: Optional[Dict[str, Any]] = None
        original_data = None

        url: str = run_keyword("get_valid_url", endpoint, method)
        request_data: RequestData = self.get_request_data(
            method=method, endpoint=endpoint
        )
        params = request_data.params
        headers = request_data.headers
        json_data = asdict(request_data.dto)
        # when patching, get the original data to check only patched data has changed
        if method == "PATCH":
            original_data = self.get_original_data(url=url)
        # in case of a status code indicating an error, ensure the error occurs
        if status_code >= 400:
            invalidation_keyword_data = {
                "get_invalid_json_data": [
                    "get_invalid_json_data",
                    url,
                    method,
                    status_code,
                    request_data,
                ],
                "get_invalidated_parameters": [
                    "get_invalidated_parameters",
                    status_code,
                    request_data,
                ],
            }
            invalidation_keywords = []

            if request_data.dto.get_relations_for_error_code(status_code):
                invalidation_keywords.append("get_invalid_json_data")
            if request_data.dto.get_parameter_relations_for_error_code(status_code):
                invalidation_keywords.append("get_invalidated_parameters")
            if invalidation_keywords:
                if (
                    invalidation_keyword := choice(invalidation_keywords)
                ) == "get_invalid_json_data":
                    json_data = run_keyword(
                        *invalidation_keyword_data[invalidation_keyword]
                    )
                else:
                    params, headers = run_keyword(
                        *invalidation_keyword_data[invalidation_keyword]
                    )
            # if there are no relations to invalide and the status_code is the default
            # response_code for invalid properties, invalidate properties instead
            elif status_code == self.invalid_property_default_response:
                if (
                    params
                    or request_data.has_optional_params
                    or request_data.headers_that_can_be_invalidated
                ):
                    params, headers = run_keyword(
                        *invalidation_keyword_data["get_invalidated_parameters"]
                    )
                    if request_data.dto_schema:
                        json_data = run_keyword(
                            *invalidation_keyword_data["get_invalid_json_data"]
                        )
                elif request_data.dto_schema:
                    json_data = run_keyword(
                        *invalidation_keyword_data["get_invalid_json_data"]
                    )
                else:
                    raise SkipExecution(
                        "No properties or parameters can be invalidated."
                    )
            else:
                logger.error(
                    f"No Dto mapping found to cause status_code {status_code}."
                )
        run_keyword(
            "perform_validated_request",
            endpoint,
            status_code,
            RequestValues(
                url=url,
                method=method,
                params=params,
                headers=headers,
                json_data=json_data,
            ),
            original_data,
        )
        if status_code < 300 and (
            request_data.has_optional_properties
            or request_data.has_optional_params
            or request_data.has_optional_headers
        ):
            logger.info("Performing request without optional properties and parameters")
            url = run_keyword("get_valid_url", endpoint, method)
            request_data = self.get_request_data(method=method, endpoint=endpoint)
            params = request_data.get_required_params()
            headers = request_data.get_required_headers()
            json_data = request_data.get_required_properties_dict()
            original_data = None
            if method == "PATCH":
                original_data = self.get_original_data(url=url)
            run_keyword(
                "perform_validated_request",
                endpoint,
                status_code,
                RequestValues(
                    url=url,
                    method=method,
                    params=params,
                    headers=headers,
                    json_data=json_data,
                ),
                original_data,
            )

    def get_original_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to GET the current data for the given url and return it.

        If the GET request fails, None is returned.
        """
        original_data = None
        endpoint = self.get_parameterized_endpoint_from_url(url)
        get_request_data = self.get_request_data(endpoint=endpoint, method="GET")
        get_params = get_request_data.params
        get_headers = get_request_data.headers
        response: Response = run_keyword(
            "authorized_request", url, "GET", get_params, get_headers
        )
        if response.ok:
            original_data = response.json()
        return original_data

    @keyword
    def perform_validated_request(
        self,
        endpoint: str,
        status_code: int,
        request_values: RequestValues,
        original_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        This keyword first calls the Authorized Request keyword, then the Validate
        Response keyword and finally validates is, for `DELETE` operations, whether
        the target resource was indeed deleted (OK response) or not (error responses).
        """
        response = run_keyword(
            "authorized_request",
            request_values.url,
            request_values.method,
            request_values.params,
            request_values.headers,
            request_values.json_data,
        )
        if response.status_code != status_code:
            if not response.ok:
                if description := response.json().get("detail"):
                    pass
                else:
                    description = response.json().get("message")
                logger.error(f"{response.reason}: {description}")
            try:
                response_json = response.json()
            except Exception as exception:  # pylint: disable=broad-except
                logger.error(f"Failed to get json body from response: {exception}")
                response_json = {}
            logger.info(
                f"\nSend: {_json.dumps(request_values.json_data, indent=4, sort_keys=True)}"
                f"\nGot: {_json.dumps(response_json, indent=4, sort_keys=True)}"
            )
            raise AssertionError(
                f"Response status_code {response.status_code} was not {status_code}"
            )
        run_keyword("validate_response", endpoint, response, original_data)
        if request_values.method == "DELETE":
            get_request_data = self.get_request_data(endpoint=endpoint, method="GET")
            get_params = get_request_data.params
            get_headers = get_request_data.headers
            get_response = run_keyword(
                "authorized_request", request_values.url, "GET", get_params, get_headers
            )
            if response.ok:
                if get_response.ok:
                    raise AssertionError(
                        f"Resource still exists after deletion. Url was {request_values.url}"
                    )
                # if the endpoint supports GET, 404 is expected, if not 405 is expected
                if get_response.status_code not in [404, 405]:
                    logger.warning(
                        f"Unexpected response after deleting resource: Status_code "
                        f"{get_response.status_code} was received after trying to get {request_values.url} "
                        f"after sucessfully deleting it."
                    )
            else:
                if not get_response.ok:
                    raise AssertionError(
                        f"Resource could not be retrieved after failed deletion. "
                        f"Url was {request_values.url}, status_code was {get_response.status_code}"
                    )

    @keyword
    def validate_response(
        self,
        endpoint: str,
        response: Response,
        original_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Validate the `response` by performing the following validations:
        - validate the `response` against the openapi schema for the `endpoint`
        - validate that the response does not contain extra properties
        - validate that a href, if present, refers to the correct resource
        - validate that the value for a property that is in the response is equal to
            the property value that was send
        - validate that no `original_data` is preserved when performing a PUT operation
        - validate that a PATCH operation only updates the provided properties
        """
        if response.status_code == 204:
            assert not response.content
            return None
        # validate the response against the schema
        self._validate_response_against_spec(response)

        request_method = response.request.method
        if request_method is None:
            logger.warning(
                f"Could not validate response for endpoint {endpoint}; no method found "
                f"on the request property of the provided response."
            )
            return None

        response_spec = self._get_response_spec(
            endpoint=endpoint,
            method=request_method,
            status_code=response.status_code,
        )
        # content should be a single key/value entry, so use tuple assignment
        (content_type,) = response_spec["content"].keys()
        if content_type != "application/json":
            # at present, only json reponses are supported
            raise NotImplementedError(f"content_type '{content_type}' not supported")
        if response.headers["Content-Type"] != content_type:
            raise ValueError(
                f"Content-Type '{response.headers['Content-Type']}' of the response "
                f"is not '{content_type}' as specified in the OpenAPI document."
            )

        json_response = response.json()
        response_schema = resolve_schema(
            response_spec["content"][content_type]["schema"]
        )
        if list_item_schema := response_schema.get("items"):
            if not isinstance(json_response, list):
                raise AssertionError(
                    f"Response schema violation: the schema specifies an array as "
                    f"response type but the response was of type {type(json_response)}."
                )
            # at present, only lists of resource objects are supported
            if list_item_schema.get("type") != "object":
                raise NotImplementedError(
                    f"response validation of lists of "
                    f"{list_item_schema.get('type')} not supported"
                )
            expected_properties = list_item_schema["properties"]
            for resource in json_response:
                run_keyword(
                    "validate_resource_properties", resource, expected_properties
                )
            # no further validation; value validation of individual resources should
            # be performed on the endpoints for the specific resource
            return None

        run_keyword(
            "validate_resource_properties", json_response, response_schema["properties"]
        )
        # ensure the href is valid if present in the response
        if href := json_response.get("href"):
            self._assert_href_is_valid(href, json_response)
        # every property that was sucessfully send and that is in the response
        # schema must have the value that was send
        if response.ok and response.request.method in ["POST", "PUT", "PATCH"]:
            run_keyword("validate_send_response", response, original_data)
        return None

    def _assert_href_is_valid(self, href: str, json_response: Dict[str, Any]):
        url = f"{self.origin}{href}"
        endpoint = url.replace(self.base_url, "")
        request_data = self.get_request_data(endpoint=endpoint, method="GET")
        params = request_data.params
        headers = request_data.headers
        get_response = run_keyword("authorized_request", url, "GET", params, headers)
        assert (
            get_response.json() == json_response
        ), f"{get_response.json()} not equal to original {json_response}"

    def _validate_response_against_spec(self, response: Response):
        validation_result = self.response_validator.validate(
            request=RequestsOpenAPIRequest(response.request),
            response=RequestsOpenAPIResponse(response),
        )
        if self.disable_server_validation:
            validation_result.errors = [
                e for e in validation_result.errors if not isinstance(e, ServerNotFound)
            ]
        if self.response_validation == ValidationLevel.STRICT:
            validation_result.raise_for_errors()
        if self.response_validation in [ValidationLevel.WARN, ValidationLevel.INFO]:
            for validation_error in validation_result.errors:
                if self.response_validation == ValidationLevel.WARN:
                    logger.warning(validation_error)
                else:
                    logger.info(validation_error)

    @staticmethod
    @keyword
    def validate_resource_properties(
        resource: Dict[str, Any], schema_properties: Dict[str, Any]
    ) -> None:
        """
        Validate that the `resource` does not contain any properties that are not
        defined in the `schema_properties`.
        """
        if resource.keys() != schema_properties.keys():
            expected_property_names = sorted(schema_properties.keys())
            property_names_in_resource = sorted(resource.keys())
            raise AssertionError(
                f"Response schema violation: the response contains properties that are "
                f"not specified in the schema."
                f"\n\tExpected: {expected_property_names}"
                f"\n\tGot: {property_names_in_resource}"
            )

    @staticmethod
    @keyword
    def validate_send_response(
        response: Response, original_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Validate that each property that was send that is in the response has the value
        that was send.
        In case a PATCH request, validate that only the properties that were patched
        have changed and that other properties are still at their pre-patch values.
        """

        def validate_array_response(
            send_value: List[Any], received_value: List[Any]
        ) -> None:
            for item in send_value:
                if item not in received_value:
                    raise AssertionError(
                        f"Received value for {send_property_name} '{received_value}' does "
                        f"not contain '{item}' in the {response.request.method} request."
                        f"\nSend: {_json.dumps(send_json, indent=4, sort_keys=True)}"
                        f"\nGot: {_json.dumps(response_data, indent=4, sort_keys=True)}"
                    )

        if response.request.body is None:
            logger.warning(
                "Could not validate send response; the body of the request property "
                "on the provided response was None."
            )
            return None
        if isinstance(response.request.body, bytes):
            send_json = _json.loads(response.request.body.decode("UTF-8"))
        else:
            send_json = _json.loads(response.request.body)

        response_data = response.json()
        # POST on /resource_type/{id}/array_item/ will return the updated {id} resource
        # instead of a newly created resource. In this case, the send_json must be
        # in the array of the 'array_item' property on {id}
        send_path: str = response.request.path_url
        response_path = response_data.get("href", None)
        if response_path and send_path not in response_path:
            property_to_check = send_path.replace(response_path, "")[1:]
            if response_data.get(property_to_check) and isinstance(
                response_data[property_to_check], list
            ):
                item_list: List[Dict[str, Any]] = response_data[property_to_check]
                # Use the (mandatory) id to get the POSTed resource from the list
                [response_data] = [
                    item for item in item_list if item["id"] == send_json["id"]
                ]
        for send_property_name, send_value in send_json.items():
            # sometimes, a property in the request is not in the response, e.g. a password
            if send_property_name not in response_data.keys():
                continue
            if send_value is not None:
                # if a None value is send, the target property should be cleared or
                # reverted to the default value (which cannot be specified in the
                # openapi document)
                received_value = response_data[send_property_name]
                # In case of lists / arrays, the send values are often appended to
                # existing data
                if isinstance(received_value, list):
                    validate_array_response(
                        send_value=send_value, received_value=received_value
                    )
                    continue
                assert response_data[send_property_name] == send_value, (
                    f"Received value for {send_property_name} '{received_value}' does not "
                    f"match '{send_value}' in the {response.request.method} request."
                    f"\nSend: {_json.dumps(send_json, indent=4, sort_keys=True)}"
                    f"\nGot: {_json.dumps(response_data, indent=4, sort_keys=True)}"
                )
        # In case of PATCH requests, ensure that only send properties have changed
        if original_data:
            for send_property_name, send_value in original_data.items():
                if send_property_name not in send_json.keys():
                    assert send_value == response_data[send_property_name], (
                        f"Received value for {send_property_name} '{response_data[send_property_name]}' does not "
                        f"match '{send_value}' in the pre-patch data"
                        f"\nPre-patch: {_json.dumps(original_data, indent=4, sort_keys=True)}"
                        f"\nGot: {_json.dumps(response_data, indent=4, sort_keys=True)}"
                    )
        return None

    def _get_response_spec(
        self, endpoint: str, method: str, status_code: int
    ) -> Dict[str, Any]:
        method = method.lower()
        status = str(status_code)
        spec = {**self.openapi_spec}["paths"][endpoint][method]["responses"][status]
        return spec
