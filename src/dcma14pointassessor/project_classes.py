import datetime as dt
from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectBase:
    def to_dict(self):
        return {k:v for k,v in self.__dict__.items()}


@dataclass(frozen=True)
class Duration(ProjectBase):
    value: float
    unit: str


@dataclass(frozen=True)
class ProjectProperties(ProjectBase):
    status_date: dt.datetime


@dataclass(frozen=True)
class Task(ProjectBase):
    id: int
    name: str
    baseline_duration: Duration
    duration: Duration
    actual_duration: Duration
    baseline_start: dt.datetime
    start: dt.datetime
    actual_start: dt.datetime
    baseline_finish: dt.datetime
    finish: dt.datetime
    actual_finish: dt.datetime
    baseline_work: Duration
    work: Duration
    actual_work: Duration
    milestone: bool
    summary: bool
    critical: bool
    guid: str
    resume: dt.datetime
    stop: dt.datetime
    constraint_date: dt.datetime
    constraint_type: str
    active: bool
    task_mode: str
    type: str
    wbs: str
    outline_level: int
    outline_number: str

    def to_error(self):
        return {
            'task_id': self.guid,
            'task_index': self.id,
            'task_name': self.name
        }


@dataclass(frozen=True)
class TaskRelation(ProjectBase):
    lag: Duration
    notes: str
    predecessor: str
    successor: str
    type: str
    uid: int


@dataclass(frozen=True)
class ResourceAssignment(ProjectBase):
    actual_finish: dt.datetime
    actual_start: dt.datetime
    actual_work: Duration
    baseline_finish: dt.datetime
    baseline_start: dt.datetime
    baseline_work: Duration
    create_date: dt.datetime
    delay: Duration
    finish: dt.datetime
    guid: str
    resource: str
    start: dt.datetime
    task_guid: str
    work: Duration


@dataclass(frozen=True)
class ProjectData:
    project_properties: ProjectProperties
    tasks:list[Task]
    task_relations: list[TaskRelation]
    resource_assigments: list[ResourceAssignment]