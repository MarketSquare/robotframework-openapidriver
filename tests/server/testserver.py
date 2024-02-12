# pylint: disable="missing-class-docstring", "missing-function-docstring"
import datetime
from enum import Enum
from sys import float_info
from typing import Dict, List, Optional, Union
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Path, Query, Response
from pydantic import BaseModel, Field

API_KEY = "OpenApiLibCore"
API_KEY_NAME = "api_key"


app = FastAPI()


REMOVE_ME: str = uuid4().hex
DEPRECATED: int = uuid4().int
DELTA = 1000 * float_info.epsilon


class EnergyLabel(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    X = "No registered label"


class WeekDay(str, Enum):
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"


class Wing(str, Enum):
    N = "North"
    E = "East"
    S = "South"
    W = "West"


class Message(BaseModel):
    message: str


class Detail(BaseModel):
    detail: str


class Event(BaseModel, extra="forbid"):
    message: Message
    details: List[Detail]


class WageGroup(BaseModel):
    wagegroup_id: str
    hourly_rate: Union[float, int] = Field(alias="hourly-rate")
    overtime_percentage: Optional[int] = DEPRECATED


class EmployeeDetails(BaseModel):
    identification: str
    name: str
    employee_number: int
    wagegroup_id: str
    date_of_birth: datetime.date
    parttime_day: Optional[WeekDay] = None


class Employee(BaseModel):
    name: str
    wagegroup_id: str
    date_of_birth: datetime.date
    parttime_day: Optional[WeekDay] = None


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    employee_number: Optional[int] = None
    wagegroup_id: Optional[str] = None
    date_of_birth: Optional[datetime.date] = None
    parttime_day: Optional[WeekDay] = None


WAGE_GROUPS: Dict[str, WageGroup] = {}
EMPLOYEES: Dict[str, EmployeeDetails] = {}
EMPLOYEE_NUMBERS = iter(range(1, 1000))
ENERGY_LABELS: Dict[str, Dict[int, Dict[str, EnergyLabel]]] = {
    "1111AA": {
        10: {
            "": EnergyLabel.A,
            "C": EnergyLabel.C,
        },
    }
}
EVENTS: List[Event] = [
    Event(message=Message(message="Hello?"), details=[Detail(detail="First post")]),
    Event(message=Message(message="First!"), details=[Detail(detail="Second post")]),
]


@app.get("/", status_code=200, response_model=Message)
def get_root(*, name_from_header: str = Header(""), title: str = Header("")) -> Message:
    name = name_from_header if name_from_header else "stranger"
    return Message(message=f"Welcome {title}{name}!")


@app.get(
    "/secret_message",
    status_code=200,
    response_model=Message,
    responses={401: {"model": Detail}, 403: {"model": Detail}},
)
def get_message(
    *, secret_code: int = Header(...), seal: str = Header(REMOVE_ME)
) -> Message:
    if secret_code != 42:
        raise HTTPException(
            status_code=401, detail=f"Provided code {secret_code} is incorrect!"
        )
    if seal is not REMOVE_ME:
        raise HTTPException(status_code=403, detail="Seal was not removed!")
    return Message(message="Welcome, agent HAL")


# deliberate trailing /
@app.get("/events/", status_code=200, response_model=List[Event])
def get_events(
    search_strings: Optional[List[str]] = Query(default=[]),
) -> List[Event]:
    if search_strings:
        result: List[Event] = []
        for search_string in search_strings:
            result.extend([e for e in EVENTS if search_string in e.message.message])
        return result
    return EVENTS


# deliberate trailing /
@app.post("/events/", status_code=201, response_model=Event)
def post_event(event: Event) -> Event:
    event.details.append(Detail(detail=str(datetime.datetime.now())))
    EVENTS.append(event)
    return event


@app.get(
    "/energy_label/{zipcode}/{home_number}",
    status_code=200,
    response_model=Message,
)
def get_energy_label(
    zipcode: str = Path(..., min_length=6, max_length=6),
    home_number: int = Path(..., ge=1),
    extension: Optional[str] = Query(" ", min_length=1, max_length=9),
) -> Message:
    if not (labels_for_zipcode := ENERGY_LABELS.get(zipcode)):
        return Message(message=EnergyLabel.X)
    if not (labels_for_home_number := labels_for_zipcode.get(home_number)):
        return Message(message=EnergyLabel.X)
    extension = "" if extension is None else extension.strip()
    return Message(message=labels_for_home_number.get(extension, EnergyLabel.X))


@app.post(
    "/wagegroups",
    status_code=201,
    response_model=WageGroup,
    responses={418: {"model": Detail}, 422: {"model": Detail}},
)
def post_wagegroup(wagegroup: WageGroup) -> WageGroup:
    if wagegroup.wagegroup_id in WAGE_GROUPS:
        raise HTTPException(status_code=418, detail="Wage group already exists.")
    if not (0.99 - DELTA) < (wagegroup.hourly_rate % 1) < (0.99 + DELTA):
        raise HTTPException(
            status_code=422,
            detail="Hourly rates must end with .99 for psychological reasons.",
        )
    if wagegroup.overtime_percentage != DEPRECATED:
        raise HTTPException(
            status_code=422, detail="Overtime percentage is deprecated."
        )
    wagegroup.overtime_percentage = None
    WAGE_GROUPS[wagegroup.wagegroup_id] = wagegroup
    return wagegroup


@app.get(
    "/wagegroups/{wagegroup_id}",
    status_code=200,
    response_model=WageGroup,
    responses={404: {"model": Detail}},
)
def get_wagegroup(wagegroup_id: str) -> WageGroup:
    if wagegroup_id not in WAGE_GROUPS:
        raise HTTPException(status_code=404, detail="Wage group not found")
    return WAGE_GROUPS[wagegroup_id]


@app.put(
    "/wagegroups/{wagegroup_id}",
    status_code=200,
    response_model=WageGroup,
    responses={404: {"model": Detail}, 418: {"model": Detail}, 422: {"model": Detail}},
)
def put_wagegroup(wagegroup_id: str, wagegroup: WageGroup) -> WageGroup:
    if wagegroup_id not in WAGE_GROUPS:
        raise HTTPException(status_code=404, detail="Wage group not found.")
    if wagegroup.wagegroup_id in WAGE_GROUPS:
        raise HTTPException(status_code=418, detail="Wage group already exists.")
    if not (0.99 - DELTA) < (wagegroup.hourly_rate % 1) < (0.99 + DELTA):
        raise HTTPException(
            status_code=422,
            detail="Hourly rates must end with .99 for psychological reasons.",
        )
    if wagegroup.overtime_percentage != DEPRECATED:
        raise HTTPException(
            status_code=422, detail="Overtime percentage is deprecated."
        )
    wagegroup.overtime_percentage = None
    WAGE_GROUPS[wagegroup.wagegroup_id] = wagegroup
    return wagegroup


@app.delete(
    "/wagegroups/{wagegroup_id}",
    status_code=204,
    response_class=Response,
    responses={404: {"model": Detail}, 406: {"model": Detail}},
)
def delete_wagegroup(wagegroup_id: str) -> None:
    if wagegroup_id not in WAGE_GROUPS:
        raise HTTPException(status_code=404, detail="Wage group not found.")
    used_by = [e for e in EMPLOYEES.values() if e.wagegroup_id == wagegroup_id]
    if used_by:
        raise HTTPException(
            status_code=406,
            detail=f"Wage group still in use by {len(used_by)} employees.",
        )
    WAGE_GROUPS.pop(wagegroup_id)


@app.get(
    "/wagegroups/{wagegroup_id}/employees",
    status_code=200,
    response_model=List[EmployeeDetails],
    responses={404: {"model": Detail}},
)
def get_employees_in_wagegroup(wagegroup_id: str) -> List[EmployeeDetails]:
    if wagegroup_id not in WAGE_GROUPS:
        raise HTTPException(status_code=404, detail="Wage group not found.")
    return [e for e in EMPLOYEES.values() if e.wagegroup_id == wagegroup_id]


@app.post(
    "/employees",
    status_code=201,
    response_model=EmployeeDetails,
    responses={403: {"model": Detail}, 451: {"model": Detail}},
)
def post_employee(employee: Employee) -> EmployeeDetails:
    wagegroup_id = employee.wagegroup_id
    if wagegroup_id not in WAGE_GROUPS:
        raise HTTPException(
            status_code=451, detail=f"Wage group with id {wagegroup_id} does not exist."
        )
    today = datetime.date.today()
    employee_age = today - employee.date_of_birth
    if employee_age.days < 18 * 365:
        raise HTTPException(
            status_code=403, detail="An employee must be at least 18 years old."
        )
    new_employee = EmployeeDetails(
        identification=uuid4().hex,
        employee_number=next(EMPLOYEE_NUMBERS),
        **employee.dict(),
    )
    EMPLOYEES[new_employee.identification] = new_employee
    return new_employee


@app.get(
    "/employees",
    status_code=200,
    response_model=List[EmployeeDetails],
)
def get_employees() -> List[EmployeeDetails]:
    return list(EMPLOYEES.values())


@app.get(
    "/employees/{employee_id}",
    status_code=200,
    response_model=EmployeeDetails,
    responses={404: {"model": Detail}},
)
def get_employee(employee_id: str) -> EmployeeDetails:
    if employee_id not in EMPLOYEES:
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
    employee_update_data = employee.model_dump(
        exclude_defaults=True, exclude_unset=True
    )

    wagegroup_id = employee_update_data.get("wagegroup_id", None)
    if wagegroup_id and wagegroup_id not in WAGE_GROUPS:
        raise HTTPException(
            status_code=451, detail=f"Wage group with id {wagegroup_id} does not exist."
        )

    today = datetime.date.today()
    if date_of_birth := employee_update_data.get("date_of_birth", None):
        employee_age = today - date_of_birth
        if employee_age.days < 18 * 365:
            raise HTTPException(
                status_code=403, detail="An employee must be at least 18 years old."
            )

    updated_employee = stored_employee_data.model_copy(update=employee_update_data)
    EMPLOYEES[employee_id] = updated_employee
    return updated_employee


@app.get("/available_employees", status_code=200, response_model=List[EmployeeDetails])
def get_available_employees(weekday: WeekDay = Query(...)) -> List[EmployeeDetails]:
    return [
        e for e in EMPLOYEES.values() if getattr(e, "parttime_day", None) != weekday
    ]
