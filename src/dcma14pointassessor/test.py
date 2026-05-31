
from .data_extractor import DataExtractor
from .validation.point_1_logic import Check_1_Logic
from .validation.point_4_relationship_types import Check_4_RelationshipType
import os

if __name__ == '__main__':
    path = os.path.join('.', 'TEMP', 'project_files', 'CAD Template.mpp')
    de = DataExtractor(path)
    data = de.extract_data()
    v = Check_4_RelationshipType(data)
    result = v.run()
    for r in data.tasks:
        print(r.total_slack, r.total_slack.to_days())
    # print(result.result, result.summary)
