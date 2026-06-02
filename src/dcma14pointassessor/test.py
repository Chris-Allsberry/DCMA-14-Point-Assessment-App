
from .data_extractor import DataExtractor
import os
from .validation import Validator
from .reportbuilder import ReportBuilder



if __name__ == '__main__':
    path = os.path.join('.', 'TEMP', 'project_files', 'CAD Template.mpp')
    de = DataExtractor(path)
    data = de.extract_data()
    v = Validator(data)
    result = v.run()
    rb = ReportBuilder(result)
    xlsx_bytes = rb.create_xlsx()
    with open(os.path.join('.','TEMP','output_files','test.xlsx'), 'wb') as file:
        file.write(xlsx_bytes)