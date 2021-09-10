from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, conint, constr, confloat

app = FastAPI()


class WeekDay(str, Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"


class Message(BaseModel):
    message: str


class Detail(BaseModel):
    detail: str


class WageGroup(BaseModel):
    id: str
    # hourly_rate: confloat(ge=14.37, lt=50.00)
    hourly_rate: float


class EmployeeDetails(BaseModel):
    id: str
    name: str
    # login_name: constr(strip_whitespace=True, min_length=1, max_length=20)
    employee_number: int
    wagegroup_id: str
    parttime_day: Optional[WeekDay]


class Employee(BaseModel):
    name: str
    # login_name: constr(strip_whitespace=True, min_length=1, max_length=20)
    wagegroup_id: str
    parttime_day: Optional[WeekDay]


class EmployeeUpdate(BaseModel):
    name: Optional[str]
    # login_name: Optional[constr(strip_whitespace=True, min_length=1, max_length=20)]
    employee_number: Optional[int]
    wagegroup_id: Optional[str]
    parttime_day: Optional[WeekDay]


WAGE_GROUPS: Dict[str, WageGroup] = {}
EMPLOYEES: Dict[str, EmployeeDetails] = {}
EMPLOYEE_NUMBERS = iter(range(1, 1000))


@app.get("/", status_code=200, response_model=Message)
def get_root() -> Message:
    return Message(message="Welcome!")


@app.post(
    "/wagegroups",
    status_code=201,
    response_model=WageGroup,
    responses={409: {"model": Detail}},
)
def post_wagegroup(wagegroup: WageGroup) -> WageGroup:
    if wagegroup.id in WAGE_GROUPS.keys():
        raise HTTPException(status_code=409, detail="Wage group already exists.")
    WAGE_GROUPS[wagegroup.id] = wagegroup
    return wagegroup


@app.get(
    "/wagegroups/{wagegroup_id}",
    status_code=200,
    response_model=WageGroup,
    responses={404: {"model": Detail}},
)
def get_wagegroup(wagegroup_id: str) -> WageGroup:
    if wagegroup_id not in WAGE_GROUPS.keys():
        raise HTTPException(status_code=404, detail="Wage group not found")
    return WAGE_GROUPS[wagegroup_id]


@app.put(
    "/wagegroups/{wagegroup_id}",
    status_code=200,
    response_model=WageGroup,
    responses={404: {"model": Detail}},
)
def put_wagegroup(wagegroup_id: str, wagegroup: WageGroup) -> WageGroup:
    if wagegroup_id not in WAGE_GROUPS.keys():
        raise HTTPException(status_code=404, detail="Wage group not found.")
    WAGE_GROUPS[wagegroup.id] = wagegroup
    return wagegroup


@app.delete(
    "/wagegroups/{wagegroup_id}",
    status_code=204,
    response_class=Response,
    responses={404: {"model": Detail}, 403: {"model": Detail}},
)
def delete_wagegroup(wagegroup_id: str) -> None:
    if wagegroup_id not in WAGE_GROUPS.keys():
        raise HTTPException(status_code=404, detail="Wage group not found.")
    used_by = [e for e in EMPLOYEES.values() if e.wagegroup_id == wagegroup_id]
    if used_by:
        raise HTTPException(
            status_code=403,
            detail=f"Wage group still in use by {len(used_by)} employees."
        )
    WAGE_GROUPS.pop(wagegroup_id)


@app.post(
    "/employees",
    status_code=201,
    response_model=EmployeeDetails,
    responses={409: {"model": Detail}},
)
def post_employee(employee: Employee) -> EmployeeDetails:
    wagegroup_id = employee.wagegroup_id
    if wagegroup_id not in WAGE_GROUPS.keys():
        raise HTTPException(
            status_code=409,
            detail=f"Wage group with id {wagegroup_id} does not exist."
        )
    new_employee = EmployeeDetails(
        id=uuid4().hex,
        employee_number=next(EMPLOYEE_NUMBERS),
        **employee.dict(),
    )
    EMPLOYEES[new_employee.id] = new_employee
    return new_employee


@app.get(
    "/employees/{employee_id}",
    status_code=200,
    response_model=EmployeeDetails,
    responses={404: {"model": Detail}},
)
def get_employee(employee_id: str) -> EmployeeDetails:
    if employee_id not in EMPLOYEES.keys():
        raise HTTPException(status_code=404, detail="Employee not found")
    return EMPLOYEES[employee_id]


@app.patch(
    "/employees/{employee_id}",
    status_code=200,
    response_model=EmployeeDetails,
    responses={404: {"model": Detail}},
)
def patch_employee(employee_id: str, employee: EmployeeUpdate) -> EmployeeDetails:
    if employee_id not in EMPLOYEES.keys():
        raise HTTPException(status_code=404, detail="Employee not found")
    stored_employee_data = EMPLOYEES[employee_id]
    employee_update_data = employee.dict(exclude_unset=True)
    updated_employee = stored_employee_data.copy(update=employee_update_data)
    EMPLOYEES[employee_id] = updated_employee
    return updated_employee


def main():
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
