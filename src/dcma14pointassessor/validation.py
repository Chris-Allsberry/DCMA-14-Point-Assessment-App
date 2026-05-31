from dataclasses import dataclass
from operator import attrgetter

from .project_classes import ProjectData, ProjectProperties, Task, TaskRelation, ResourceAssignment

@dataclass(frozen=True)
class ValidationBase:

    def to_dict(self):
        return {k:v for k,v in self.__dict__.items()}

@dataclass(frozen=True)
class ValidationInfo(ValidationBase):
    id: int
    name: str
    type: str
    description: str

@dataclass(frozen=True)
class ValidationError(ValidationBase):
    task_id: str
    task_index: int
    task_name: str
    error: str

@dataclass(frozen=True)
class ValidationResult(ValidationBase):
    validation_info: ValidationInfo
    result: str
    summary: str
    data: list[ValidationError]

class Validation:
    def __init__(self, schedule_data: ProjectData):
        self.schedule = schedule_data

    # Check 1: Missing Logic
    def _check_1_missing_logic(self) -> ValidationResult:

        # Create Validation Info
        info = ValidationInfo(
            id=1,
            name='Missing Logic',
            type='Error',
            description="Ensure that every task has at least one predecessor "\
                "and one successor. Exceptions are the starting task in the project "\
                "(which should only have a successor) and the finishing task of a project "\
                "(which should only have a predecessor). Milestones should also "\
                "only have predecessors and should not be used to drive activities."
        )

        # Find the First Non Summary Tasks






if __name__ == "__main__":
    i = ValidationInfo(
        id=1,
        name='MyName',
        type='MyType',
        description='Mydesc'
    )
    j = i.to_dict()
    print(j)