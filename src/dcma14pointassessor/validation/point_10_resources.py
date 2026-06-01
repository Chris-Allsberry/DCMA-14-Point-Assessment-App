from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData

class Check_10_Resources:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=10,
            name='Resources',
            type='Warning',
            description=""
        )
        self.elligible_task_count = 0


    def __check_resources(self):
        for task in self.project.tasks:
            if not task.summary and not task.milestone and task.id != 0:
                self.elligible_task_count =+ 1
                assignments = list(filter(lambda ra: ra.guid == task.guid, self.project.resource_assignments))
                if len(assignments) == 0:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="This task doesn't have a resource assigned."
                        )
                    )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = self.elligible_task_count
        if total == 0:
            result = "N/A"
            summary = "There are no tasks in the schedule."
        else:
            if bad > 0:
                result = 'Fail'
            else:
                result = 'Pass'
            summary = f"There are {bad} tasks without resources assigned."
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_resources()
        return self.__create_summary()