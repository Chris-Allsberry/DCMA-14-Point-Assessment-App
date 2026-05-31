from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..data_extractor.project_classes import ProjectData

class Check_4_RelationshipType:
    def __init__(self, project: ProjectData):
        self.error_list = []
        self.project = project
        self.info = ValidationInfo(
            id=2,
            name='Relationship Type',
            type='Warning   ',
            description="DCMA recommends that 90% of scheduled activities follow a finish-to-start "\
                "(FS) relationship type. This approach is fundamental to the Waterfall method and provides "\
                "the clearest representation of scheduled activities. While other relationship types "\
                "exist (FF, SS, SF), their use should be limited due to increased complexity in monitoring and control."
            )

    def __check_relationship_types(self):
        for tr in self.project.task_relations:
            if tr.type != 'FS':
                task = self.project.task_lookup[tr.successor]
                self.error_list.append(
                    ValidationError(
                        **task.to_error(),
                        error='Task Relationship is not Finish-to-Start.'
                    )
                )

    def __create_summary(self) -> ValidationResult:
        bad = len(self.error_list)
        total = len(self.project.task_relations)
        percentage =  bad / total
        if total == 0:
            result = "N/A"
            summary = f"There are 0 Task Relationships in this project schedule."
        else:
            if percentage > .1:
                result = 'Fail'
            else:
                result = 'Pass'
            summary = f"You have {percentage} ({bad} of {total}) "\
                "of Task Relations as Non Finish-to-Start."
        return ValidationResult(
            validation_info=self.info,
            result=result,
            summary=summary,
            data=self.error_list
        )

    def run(self) -> ValidationResult:
        self.__check_relationship_types()
        return self.__create_summary()