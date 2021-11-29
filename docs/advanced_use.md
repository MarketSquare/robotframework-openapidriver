# Advanced use scenario's: using the mappings_path

## Introduction
When working with APIs, there are often relations between resources or constraints on values.
The property on one resource may refer to the `id` of another resource.
The value for a certain property may have to be unique within a certain scope.
Perhaps an endpoint path contains parameters that must match values that are defined outside the API itself.

These types of relations and limitations cannot be described / modeled within the openapi document.
To support automatic validation of API endpoints where such relations apply, OpenApiDriver supports the usage of a custom mappings file.

## Taking a custom mappings file into use
To take a custom mappings file into use, the absolute path to it has to be passed to OpenApiDriver as the `mappings_path` parameter:

```robot framework
*** Settings ***
Library             OpenApiDriver
...                 source=http://localhost:8000/openapi.json
...                 origin=http://localhost:8000
...                 mappings_path=${root}/tests/custom_user_mappings.py
...
```

> Note: An absolute path is required.
> In the example above, `${root}` is a global variable that holds the absolute path to the repository root.

## The custom mappings file
Just like custom Robot Framework libraries, the mappings file has to be implemented in Python.
Since this Python file is imported by the OpenApiDriver, it has to follow a fixed format (more technically, implement a certain interface).
The bare minimum implementation of a mappings.py file looks like this:

```python
from OpenApiDriver import (
    IGNORE,
    Dto,
    IdDependency,
    IdReference,
    PathPropertiesConstraint,
    PropertyValueConstraint,
    UniquePropertyValueConstraint,
)


class MyDtoThatDoesNothing(Dto):
    @staticmethod
    def get_relations():
        relations = []
        return relations


DTO_MAPPING = {
    ("/myspecialendpoint", "post"): MyDtoThatDoesNothing
}

```

There are 3 main parts in this mappings file:

1. The import section.
Here the classes needed to implement custom mappings are imported.
This section can just be copied without changes.
2. The section defining the mapping Dtos.
More on this later.
3. The `DTO_MAPPING` "constant" definition / assignment.

## The DTO_MAPPING
When a custom mappings file is used, the OpenApiDriver will attempt to import it and then import `DTO_MAPPING` from it.
For this reason, the exact same name must be used in a custom mappings file (capitilization matters).

The `DTO_MAPPING` is a dictionary with a tuple as its key and a mappings Dto as its value.
The tuple must be in the form `("endpoint_from_the_paths_section", "method_supported_by_the_endpoint")`.
The `endpoint_from_the_paths_section` must be exactly as found in the openapi document.
The `method_supported_by_the_endpoint` must be one of the methods supported by the endpoint and must be in lowercase.

## Dto mapping classes
As can be seen from the import section above, a number of classes are available to deal with relations between resources and / or constraints on properties.
Each of these classes is designed to handle a relation or constraint commonly seen in REST APIs.

---

To explain the different mapping classes, we'll use the following example:

Imagine we have an API endpoint `/employees` where we can create (`post`) a new Employee resource.
The Employee has a number of required properties; name, employee_number, wagegroup_id, and date_of_birth.

There is also the the `/wagegroups` endpoint where a Wagegroup resource can be created.
This Wagegroup also has a number of required properties: name and hourly rate.

---

### `IdReference`
> *The value for this propery must the the `id` of another resource*

To add an Employee, a `wagegroup_id` is required, the `id` of a Wagegroup resource that is already present in the system.

Since a typical REST API generates this `id` for a new resource and returns that `id` as part of the `post` response, the required `wagegroup_id` can be obtained by posting a new Wagegroup. This relation can be implemented as follows:

```python
class EmployeeDto(Dto):
    @staticmethod
    def get_relations():
        relations = [
            IdDependency(
                property_name="wagegroup_id",
                get_path="/wagegroups",
                error_code=451,
            ),
        ]
        return relations

DTO_MAPPING = {
    ("/employees", "post"): EmployeeDto
}
```

Notice that the `get_path` of the `IdDependency` is not named `post_path` instead.
This is deliberate for two reasons:

1. The purpose is getting an `id`
2. If the `post` operation is not supported on the provided path, a `get` operation is performed instead.
It is assumed that such a `get` will yield a list of resources and that each of these resources has an `id` that is valid for the desired `post` operation.

Also note the `error_code` of the `IdDependency`.
If a `post` is attempted with a value for the `wagegroup_id` that does not exist, the API should return an `error_code` response.
This `error_code` should be described as one of the `responses` in the openapi document for the `post` operation of the `/employees` path.

---

### `IdDependency`
> *This resource may not be DELETED if another resource refers to it*

If an Employee has been added to the system, this Employee refers to the `id` of a Wagegroup for its required `employee_number` property.

Now let's say there is also the `/wagegroups/${wagegroup_id}` endpoint that supports the `delete` operation.
If the Wagegroup refered to the Employee would be deleted, the Employee would be left with an invalid reference for one of its required properties.
To prevent this, an API typically returns an `error_code` when such a `delete` operation is attempted on a resource that is refered to in this fashion.
This `error_code` should be described as one of the `responses` in the openapi document for the `delete` operation of the `/wagegroups/${wagegroup_id}` path.

To verify that the specified `error_code` indeed occurs when attempting to `delete` the Wagegroup, we can implement the following dependency:

```python
class WagegroupDto(Dto):
    @staticmethod
    def get_relations():
        relations = [
            IdReference(
                property_name="wagegroup_id",
                post_path="/employees",
                error_code=406,
            ),
        ]
        return relations

DTO_MAPPING = {
    ("/wagegroups/{wagegroup_id}", "delete"): WagegroupDto
}
```

---

### `UniquePropertyValueConstraint`
> *The value of this property must be unique within its scope*

In a lot of systems, there is data that should be unique; an employee number, the email address of an employee, the domain name for the employee, etc.
Often those values are automatically generated based on other data, but for some data, an "available value" must be chosen by hand.

In our example, the required `employee_number` must be chosen from the "free" numbers.
When a number is chosen that is already in use, the API should return the `error_code` specified in the openapi document for the operation (typically `post`, `put` and `patch`) on the endpoint.

To verify that the specified `error_code` occurs when attempting to `post` an Employee with an `employee_number` that is already in use, we can implement the following dependency:

```python
class EmployeeDto(Dto):
    @staticmethod
    def get_relations():
        relations = [
            UniquePropertyValueConstraint(
                property_name="employee_number",
                value=42,
                error_code=422,
            ),
        ]
        return relations

DTO_MAPPING = {
    ("/employees", "post"): EmployeeDto,
    ("/employees/${employee_id}", "put"): EmployeeDto,
    ("/employees/${employee_id}", "patch"): EmployeeDto,
}
```

Note how this example reuses the `EmployeeDto` to model the uniqueness constraint for all the operations (`post`, `put` and `patch`) that all relate to the same `employee_number`.

---

### `PropertyValueConstraint`
> *Use one of these values for this property*

The OpenApiDriver uses the `type` information in the openapi document to generate random data of the correct type to perform the operations that need it.
While this works in many situations (e.g. a random `string` for a `name`), there can be additional restrictions to a value that cannot be specified in an openapi document.

In our example, the `date_of_birth` must be a string in a specific format, e.g. 1995-03-27.
This type of constraint can be modeled as follows:

```python
class EmployeeDto(Dto):
    @staticmethod
    def get_relations():
        relations = [
            PropertyValueConstraint(
                property_name="date_of_birth",
                values=["1995-03-27", "1980-10-02"],
                error_code=422,
            ),
        ]
        return relations

DTO_MAPPING = {
    ("/employees", "post"): EmployeeDto,
    ("/employees/${employee_id}", "put"): EmployeeDto,
    ("/employees/${employee_id}", "patch"): EmployeeDto,
}
```

Now in addition, there could also be the restriction that the Employee must be 18 years or older.
To support additional restrictions like these, the `PropertyValueConstraint` supports two additional properties: `error_value` and `invalid_value_error_code`:

```python
class EmployeeDto(Dto):
    @staticmethod
    def get_relations():
        relations = [
            PropertyValueConstraint(
                property_name="date_of_birth",
                values=["1995-03-27", "1980-10-02"],
                error_code=422,
                invalid_value="2020-02-20",
                invalid_value_error_code=403,
            ),
        ]
        return relations

DTO_MAPPING = {
    ("/employees", "post"): EmployeeDto,
    ("/employees/${employee_id}", "put"): EmployeeDto,
    ("/employees/${employee_id}", "patch"): EmployeeDto,
}
```

So now if an incorrectly formatted date is send a 422 response is expected, but when `2020-02-20` is send the expected repsonse is 403.

---

### `PathPropertiesConstraint`
> *Just use this for the `path`*

To be able to automatically perform endpoint validations, the OpenApiDriver has to construct the `url` for the resource from the `path` as found in the openapi document.
Often, such a `path` contains a reference to a resource id, e.g. `/employees/${employee_id}`.
When such an `id` is needed, the OpenApiDriver tries to obtain a valid `id` by taking these steps:

1. Attempt a `post` on the "parent endpoint" and extract the `id` from the response.
In our example: perform a `post` request on the `/employees` endpoint and get the `id` from the response.
2. If 1. fails, perform a `get` request on the `/employees` endpoint. It is assumed that this will return a list of Employee objects with an `id`.
One item from the returned list is picked at rondom and its `id` is used.

This mechanism relies on the standard REST structure and patterns.

Unfortunately, this structure / pattern does not apply to every endpoint, not every path parameter refers to a resource id.
Imagine we want to extend the API from our example with an endpoint that returns all the Employees that have their birthday at a given date:
`/birthdays/${month}/${date}`.
It should be clear that the OpenApiDriver won't be able to acquire a valid `month` and `date`. The `PathPropertiesConstraint` can be used in this case:

```python
class BirthdaysDto(Dto):
    @staticmethod
    def get_relations():
        relations = [
            PathPropertiesConstraint(path="/birthdays/03/27"),
        ]
        return relations

DTO_MAPPING = {
    ("/birthdays/{month}/{date}", "get"): BirthdaysDto
}
```

---

### `IGNORE`
> *Never send this query parameter as part of a request*

Some optional query parameters have a range of valid values that depend on one or more path parameters.
Since path parameters are part of a url, they cannot be optional or empty so to extend the path parameters with optional parameters, query parameters can be used.

To illustrate this, let's imagine an API where the energy label for a building can be requested: `/energylabel/${zipcode}/${home_number}`.
Some addresses however have an address extension, e.g. 1234AB 42 <sup>2.C</sup>.
The extension may not be limited to a fixed pattern / range and if an address has an extension, in many cases the address without an extension part is invalid.

To prevent OpenApiDriver from generating invalid combinations of path and query parameters in this type of endpoint, the `IGNORE` special value can be used to ensure the related query parameter is never send in a request.

```python
class EnergyLabelDto(Dto):
    @staticmethod
    def get_parameter_relations():
        relations = [
            PropertyValueConstraint(
                property_name="address_extension",
                values=[IGNORE],
                error_code=422,
            ),
        ]
        return relations

    @staticmethod
    def get_relations(:
        relations = [
            PathPropertiesConstraint(path="/energy_label/1111AA/10"),
        ]
        return relations

DTO_MAPPING = {
    ("/energy_label/{zipcode}/{home_number}", "get"): EnergyLabelDto
}
```

Note that in this example, the `get_parameter_relations()` method is implemented.
This method works mostly the same as the `get_relations()` method but applies to headers and query parameters.

---

## Type annotations

An additional import to support type annotations is also available: `Relation`.
A fully typed example can be found
[here](https://github.com/MarketSquare/robotframework-openapidriver/blob/main/tests/user_implemented/custom_user_mappings.py).
