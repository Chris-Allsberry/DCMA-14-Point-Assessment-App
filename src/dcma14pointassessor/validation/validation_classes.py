from dataclasses import dataclass
from operator import attrgetter


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

    def to_summary_dict(self):
        return {
            'id': self.validation_info.id,
            'name': self.validation_info.name,
            'desc': self.validation_info.description,
            'type': self.validation_info.type,
            'result': self.result,
            'summary': self.summary
        }

    def create_details_list(self): # Work on this!!
        output = []
        for i in self.data:
            new = {

            }