import os
from dataclasses import dataclass
from typing import Optional
import traceback

from .data_extractor import DataExtractor
from .validation import Validator
from .validation.validation_classes import ValidationResult
from .reportbuilder import ReportBuilder
from .utility import ValidationRequest

@dataclass
class JobResult:
    status: bool
    output: Optional[str] = None
    error: Optional[str] = None
    results_data: Optional[ValidationResult] = None

class JobControl:
    def __init__(self, request: ValidationRequest):
        self.request = request
        self.output_bytes = None
        self.validation_results = None

    def __run_validation(self):
        de = DataExtractor(self.request.input_path)
        data = de.extract_data()
        validator = Validator(data)
        self.validation_results = validator.run()
        report_builder = ReportBuilder(self.validation_results)
        self.output_bytes = report_builder.create_xlsx()


    def __write_output(self, path):
        with open(path, 'wb') as file:
            file.write(self.output_bytes)

    def run(self) -> JobResult:
        try:
            self.__run_validation()
            output_path = self.request.create_output_path()
            self.__write_output(output_path)
            return JobResult(
                status=True,
                output=output_path,
                results_data=self.validation_results
            )
        except Exception as e:
            return JobResult(
                status=False,
                error=traceback.extract_tb(e.__traceback__)
            )