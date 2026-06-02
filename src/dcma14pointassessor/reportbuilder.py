from io import BytesIO
import inspect
from openpyxl import Workbook
from openpyxl.styles import (
    NamedStyle,
    Font,
    PatternFill,
    Border,
    Color,
    Side,
    Alignment,
)
from openpyxl.utils import get_column_letter
from operator import methodcaller
from .validation.validation_classes import ValidationResult

class ReportBuilder:
    def __init__(self, validation_results: list[ValidationResult]):
        self.results = validation_results
        self.wb = Workbook()

    def __data_transformer(self,data):
        output = []
        output.append(list(data[0].keys()))
        for i in data:
            output.append(list(i.values()))
        return output

    def __add_summary_data(self):
        summary_sheet = self.wb.active
        summary_sheet.title = "Summary"
        all_data = []
        for res in self.results:
            all_data.append(res.to_summary_dict())
        summary_tranformed = self.__data_transformer(all_data)
        for row in summary_tranformed:
            summary_sheet.append(row)

    def __add_details_data(self):
        details_sheet = self.wb.create_sheet("Details")
        all_data = []
        for res in self.results:
            for item in res.data:
                all_data.append(item.to_dict())
        details_transformed = self.__data_transformer(all_data)
        for row in details_transformed:
            details_sheet.append(row)


    def create_xlsx(self) -> bytes:
        self.__add_summary_data()
        self.__add_details_data()
        buffer = BytesIO()
        self.wb.save(buffer)
        return buffer.getvalue()