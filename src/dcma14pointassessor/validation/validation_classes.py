from dataclasses import dataclass

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
            'Result': self.result,
            'Id': self.validation_info.id,
            'Name': self.validation_info.name,
            'Type': self.validation_info.type,
            'Description': self.validation_info.description,
            'Summary': self.summary
        }

    def create_details_list(self):
        output = []
        for i in self.data:
            new = {
                'Id': self.validation_info.id,
                'Name': self.validation_info.name,
                'Type': self.validation_info.type,
                'Task GUID': i.task_id,
                'Task Index': i.task_index,
                'Task Name': i.task_name,
                'Error': i.error
            }
            output.append(new)
        return output