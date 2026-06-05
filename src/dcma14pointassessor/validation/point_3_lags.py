from operator import attrgetter

from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData, Task

class Check_3_Lags:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=3,
            name='Lags',
            type='Warning',
            description="Some lags are acceptable, but they need to be limited to less "\
                "than 5% of the total task relationships in the schedule. Review the lags that "\
                "exist and ensure they're minimized."
        )

    def __check_lags(self):
        for tr in self.project.task_relations:
            if tr.lag.value > 0:
                task_guid = tr.successor
                task = self.project.task_lookup[task_guid]
                self.error_list.append(
                    ValidationError(
                        task_id=task.guid,
                        task_index=task.id,
                        task_name=task.name,
                        error="The Relationship to the Pred is a Lag."
                    )
                )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = len(self.project.task_relations)
        if total > 0:
            percentage = bad / total
            if percentage > 0.05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(percentage,'0.2%')} ({bad} of {total}) task relationships with lags."
        else:
            result = "N/A"
            summary = f"You have 0 Task Relationships in this project schedule."
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_lags()
        return self.__create_summary()
