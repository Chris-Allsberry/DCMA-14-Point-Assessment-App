
from .data_extractor import DataExtractor
from .validation.point_1_logic import Check_1_Logic
import os

if __name__ == '__main__':
    path = os.path.join('.', 'TEMP', 'project_files', 'CAD Template.mpp')
    de = DataExtractor(path)
    data = de.extract_data()
    cl = Check_1_Logic(data)
    result = cl.run()
    print(result)

