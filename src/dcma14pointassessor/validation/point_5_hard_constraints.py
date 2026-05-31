from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData


class Check_5_Hard_Contraints:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=4,
            name="Hard Start Constraints",
            type="Warning",
            description="Hard constraints should be used sparingly. "\
                "While they are sometimes necessary, the vast majority of tasks should "\
                "be driven by logic rather than a constraint date.",
        )
        self.CONTRAINT_TYPES = [
            "MUST_START_ON",
            "MUST_FINISH_ON",
            "START_NO_EARLIER_THAN",
            "FINISH_NO_EARLIER_THAN"
            "START_NO_LATER_THAN",
            "FINISH_NO_LATER_THAN"
        ]
        self.total_tasks = 0

    def __check_constraints(self):
        for task in self.project.tasks:
            if task.id != 0:
                self.total_tasks += 1
                ct = task.constraint_type
                if ct in self.CONTRAINT_TYPES:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error=f"This Task has a Hard Constraint: {ct}"
                        )
                    )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = self.total_tasks
        if total == 0:
            result = "N/A"
            summary = f"You have 0 Tasks in this project schedule."
        else:
            if bad / total > 0.05:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {format(bad/total,'0.2%')} ({bad} of {total}) tasks with Hard Constraints."

            return ValidationResult(
                validation_info=self.info,
                result=result,
                summary=summary,
                data=self.error_list
            )

    def run(self) -> ValidationResult:
        self.__check_constraints()
        return self.__create_summary()