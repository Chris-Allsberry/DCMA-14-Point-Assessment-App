from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData

class Check_8_HighDuration:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=8,
            name='High Duration',
            type='Warning',
            description="If more than 5% of incomplete tasks surpass the "\
                "duration threshold of 44 working days, it's advisable to "\
                "break them into more minor, more manageable activities. "\
                "This approach enhances control while preserving the "\
                "integrity of the critical path.",
        )
        self.total_non_0_tasks = 0

    def __check_high_duration(self):
        for task in self.project.tasks:
            if task.id != 0 and task.actual_finish is None:
                self.total_non_0_tasks += 1
                if task.duration.to_days() > 44:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error=f"This Task's duration of {task.duration.to_days()} Days is more than 44 Days"
                        )
                    )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = self.total_non_0_tasks
        if total == 0:
            result = "N/A"
            summary = "There are no tasks in the schedule."
        else:
            percentage = bad / total
            if percentage > .05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(percentage,'0.2%')} ({bad} of {total}) "\
                "unfinished tasks with Duration over 44 Days."
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_high_duration()
        return self.__create_summary()
