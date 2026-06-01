
from .data_extractor import DataExtractor
import os
from .validation.point_7_negative_float import Check_7_NegativeFloat

if __name__ == '__main__':
    path = os.path.join('.', 'TEMP', 'project_files', 'CAD Template.mpp')
    de = DataExtractor(path)
    data = de.extract_data()
    v = Check_7_NegativeFloat(data)
    result = v.run()
    print(result)
    for r in result.data:
        print(r)