from .validation_classes import ValidationInfo, ValidationError, ValidationResult
from ..project_classes import ProjectData

class Check_1_Logic:
    def __init__(self, project:ProjectData):
        self.project = project
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

