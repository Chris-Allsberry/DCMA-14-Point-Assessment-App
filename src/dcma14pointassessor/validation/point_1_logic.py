from operator import attrgetter

from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..project_classes import ProjectData, Task

class Check_1_Logic:
    def __init__(self, project:ProjectData):
        self.project = project
        self.tasks = list(filter(lambda x: x.id != 0, self.project.tasks))
        self.info = ValidationInfo(
            id=1,
            name='Missing Logic',
            type='Error',
            description="Ensure that every task has at least one predecessor "\
                "and one successor. Exceptions are the starting task in the project "\
                "(which should only have a successor) and the finishing task of a project "\
                "(which should only have a predecessor). Milestones should also "\
                "only have predecessors and should not be used to drive activities."
        )
        self.first_tasks = self.__find_first_non_summary_task()
        self.error_list = []

    def __find_first_non_summary_task(self) -> list[Task]:
        non_summary_tasks = list(filter(lambda x: x.summary is False, self.tasks))
        first_date = min(non_summary_tasks, key=attrgetter('start')).start
        first_tasks = list(filter(lambda x: x.start == first_date, non_summary_tasks))
        return first_tasks

    def __multiple_first_tasks(self):
            if len(self.first_tasks) > 1:
                for index, task in enumerate(self.first_tasks):
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error=f"This task is {index + 1} of {len(self.first_tasks)} "\
                        "which start the Schedule. The Schedule should start with a single task."
                        )
                    )

    def __check_logic(self):
        for task in self.tasks:
            preds = len(
                list(filter(lambda x: x.successor == task.guid, self.project.task_relations))
            )
            succs = len(
                list(filter(lambda x: x.predecessor == task.guid, self.project.task_relations))
            )
            first_task_guids = [task.guid for task in self.first_tasks]

            # Summary Task
            if task.summary:
                if preds > 0 or succs > 0:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="Summary Task with Logic."
                        )
                    )

            # Milestone Task
            elif task.milestone:
                if preds == 0 and succs == 0:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="Milestone Task with No Logic"
                        )
                    )
                elif preds == 0 and succs > 0 and task.guid not in first_task_guids:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="Milestone with Successors but no Predecessors."
                        )
                    )
            # Regular Task
            else:
                if preds == 0 and succs == 0:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="Task With no Logic."
                        )
                    )
                elif preds == 0 and succs > 0 and task.guid not in first_task_guids:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="Task with Successors but no Predecessors."
                        )
                    )
                elif preds > 0 and succs == 0:
                    self.error_list.append(
                        ValidationError(
                            **task.to_error(),
                            error="Task with Predecessors but no Successors."
                        )
                    )

    def __create_summary(self):
        bad_count = len(self.error_list)
        total_count = len(self.tasks)
        if total_count == 0:
            result = "N/A"
            summary = "You have 0 Tasks in this project schedule."
        else:
            if bad_count > 0:
                result = "Fail"
            else:
                result = "Pass"
            summary = f"You have {bad_count} of {total_count} tasks with bad logic."

        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__multiple_first_tasks()
        self.__check_logic()
        result = self.__create_summary()
        return result