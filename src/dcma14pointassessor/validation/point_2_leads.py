from operator import attrgetter

from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData


class Check_2_Leeds:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=2,
            name='Leads',
            type='Error',
            description="Remove all leads (AKA negative lags) from the schedule. "\
                "This may involve breaking down the predecessor task into two distinct "\
                "tasks in order to capture when the task with a lead should begin.",
        )

    def __check_leeds(self):
        for tr in self.project.task_relations:
            if tr.lag.value < 0:
                task_guid = tr.successor
                task = self.project.task_lookup[task_guid]
                self.error_list.append(
                    ValidationError(
                        task_id=task.guid,
                        task_index=task.id,
                        task_name=task.name,
                        error="The Relationship to the Predecessor is a Lead (Negative Lag)."
                    )
                )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = len(self.project.task_relations)
        if total > 0:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} of {total} task relationships with leads."
        else:
            result = "N/A"
            summary = f"There are 0 Task Relationships in this project schedule."
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_leeds()
        return self.__create_summary()