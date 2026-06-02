from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData

class Check_6_HighFloat:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=6,
            name='High Float',
            type='Warning',
            description="The high float metric examines the percentage of unfinished tasks, "\
                "with total float exceeding 44 working days. Total float should not "\
                "surpass 5% of total, incomplete tasks. High float can indicate missing "\
                "predecessors or successors and requires careful management to prevent "\
                "schedule disruptions.",
        )
        self.incomplete_tasks = list(filter(lambda t: t.actual_finish is None and t.id != 0, self.project.tasks))

# Calculation: (Incomplete Tasks with Total Float > 44 Days / Total Incomplete Tasks) x 100.

    def __check_float(self):
        for task in self.incomplete_tasks:
            if task.total_slack.to_days() > 44:
                self.error_list.append(
                    ValidationError(
                        **task.to_error(),
                        error=f'Incomplete Task with more than 44 Days of Float/Slack ({task.total_slack.to_days()} Days).'
                    )
                )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = len(self.incomplete_tasks)
        percentage = bad / total
        if total == 0:
            result = 'N/A'
            summary = 'You have 0 Incomplete Tasks.'
        else:
            if percentage > .05:
                result = 'Fail'
            else:
                result = 'Pass'
            summary = f'You have {format(percentage, '0.2%')} of tasks with more than 44 Days of Float.'
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_float()
        return self.__create_summary()