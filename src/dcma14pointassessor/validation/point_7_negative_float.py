from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData

class Check_7_NegativeFloat:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=7,
            name='Negative Float',
            type='Error',
            description="Negative float, often resulting from hard constraints, "\
            "can signal potential delays in project or milestone completion. "\
            "The DCMA threshold for this metric is zero, emphasizing the need "\
            "for regular schedule reviews and proactive mitigation of tasks "\
            "with significant negative float."
        )
        self.incomplete_tasks = list(filter(lambda t: t.actual_finish is None and t.id != 0, self.project.tasks))

# Calculation: (Incomplete Tasks with Total Float < 0 / Total Incomplete Tasks) x 100.

    def __check_negative_float(self):
            for task in self.incomplete_tasks:
                if task.total_slack.to_days() < 0:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error=f'Incomplete Task with negative Float/Slack of {task.total_slack.to_days()} Days.'
                        )
                    )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = len(self.incomplete_tasks)
        if total == 0:
            result = 'N/A'
            summary = 'You have 0 Incomplete Tasks.'
        else:
            if bad > 0:
                result = 'Fail'
            else:
                result = 'Pass'
            summary = f'You have {bad} of tasks with more than nagative Float.'
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_negative_float()
        return self.__create_summary()