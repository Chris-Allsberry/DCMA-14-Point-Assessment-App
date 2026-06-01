
from .data_extractor import DataExtractor
import os
from .validation import Validator
if __name__ == '__main__':
    path = os.path.join('.', 'TEMP', 'project_files', 'CAD Template.mpp')
    de = DataExtractor(path)
    data = de.extract_data()
    v = Validator(data)
    result = v.run()
    print(result)