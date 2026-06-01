from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData, Task

class Check_9_InvalidDates:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=9,
            name='Invalid Dates',
            type='Error',
            description="This crucial metric analyzes forecast "\
                "and actual dates of project activities. The goal "\
                "is to eliminate any instances of invalid dates, such "\
                "as forecast dates in the past or actual dates in the "\
                "future. Date integrity is vital for accurate schedule management."
        )
        self.eligible_tasks = 0
        self.status_date = self.project.project_properties.status_date

# Cases
# 1) Actual Start Date is in the future
# 2) Actual Finish Date is in the future.
# 3) Start Date in Past w/o Actual Start
# 4) Finish Date in Past w/o Actual Finish


    def __check_future_act_start(self, task: Task):
            if task.actual_start and task.actual_start > self.status_date:
                self.error_list.append(
                    ValidationError(
                        **task.to_error(),
                        error=f"Task Actual Start Date ({task.actual_start}) "\
                            f"is after the Project Status Date ({self.status_date}).",
                    )
                )

    def __check_future_act_finish(self, task: Task):
        if task.actual_finish and task.actual_finish > self.status_date:
            self.error_list.append(
                ValidationError(
                    **task.to_error(),
                    error=f"Task Actual Finish Date ({task.actual_finish}) "\
                        f"is after the Project Status Date ({self.status_date}).",
                )
            )

    def __check_start_no_act(self, task: Task):
        if task.start < self.status_date and task.actual_start is None:
            self.error_list.append(
                ValidationError(
                    **task.to_error(),
                    error=f"Task has a Start Date in the past but is missing an Actual Start Date."
                )
            )

    def __check_finish_no_act(self, task: Task):
        if task.finish < self.status_date and task.actual_finish is None:
            self.error_list.append(
                ValidationError(
                    **task.to_error(),
                    error=f"Task has a Finish Date in the past but is missing an Actual Finish Date."
                )
            )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = self.eligible_tasks
        if total == 0:
            result = "N/A"
            summary = "There are no tasks in the schedule."
        else:
            if bad > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad} task errors related to Invalid Dates"
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        for task in self.project.tasks:
            if task.id != 0:
                self.eligible_tasks += 1
                self.__check_start_no_act(task)
                self.__check_finish_no_act(task)
                self.__check_future_act_start(task)
                self.__check_future_act_finish(task)
        return self.__create_summary()