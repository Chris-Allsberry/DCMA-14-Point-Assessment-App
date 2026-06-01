from .point_1_logic import Check_1_Logic
from .point_2_leads import Check_2_Leeds
from .point_3_lags import Check_3_Lags
from .point_4_relationship_types import Check_4_RelationshipType
from .point_5_hard_constraints import Check_5_Hard_Contraints
from .point_6_high_float import Check_6_HighFloat
from .point_7_negative_float import Check_7_NegativeFloat
from .point_8_high_duration import Check_8_HighDuration
from .point_9_invalid_dates import Check_9_InvalidDates
from .point_10_resources import Check_10_Resources
from .validation_classes import ValidationResult
from ..data_extractor.project_classes import ProjectData

class Validator:
    def __init__(self, project: ProjectData):
        self.project: ProjectData = project
        self.output:list[ValidationResult] = []
        self.validation_list: list = [
            Check_1_Logic,
            Check_2_Leeds,
            Check_3_Lags,
            Check_4_RelationshipType,
            Check_5_Hard_Contraints,
            Check_6_HighFloat,
            Check_7_NegativeFloat,
            Check_8_HighDuration,
            Check_9_InvalidDates,
            Check_10_Resources
        ]

    def run(self) -> list[ValidationResult]:
        for validation_class in self.validation_list:
            validation = validation_class(self.project)
            result = validation.run()
            self.output.append(result)

        return self.output