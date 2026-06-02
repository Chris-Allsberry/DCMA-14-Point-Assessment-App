
from .data_extractor import DataExtractor
import os
from load_dotenv import load_dotenv
from .job_control import JobControl
from .utility import Config, ValidationRequest



if __name__ == '__main__':
    load_dotenv()
    config = Config()
    file = 'CAD Template.mpp'
    vr = ValidationRequest(
        input_path=os.path.join(config.input_folder,file),
        output_folder=config.output_folder
    )
    mc = JobControl(request=vr)
    res = mc.run()
    print(res.status)
    for i in res.results_data:
        print(i.summary)
    # print(vr.input_path)
    # print(os.path.exists(vr.input_path))