from dataclasses import dataclass
import datetime as dt
import os

from pathlib import Path

@dataclass(frozen=True)
class ValidationRequest:
    input_path: str
    output_folder: str

    def create_output_path(self) -> str:
        now = dt.datetime.now(dt.timezone.utc)
        timestamp = now.strftime('%Y%m%dT%H%M%SZ')
        path = Path(self.input_path)
        new_file_name = f'{path.stem}_{timestamp}.xlsx'
        return os.path.join(self.output_folder, new_file_name)

class Config:
    def __init__(self):
        data_path = os.getenv('INPUT_OUTPUT_PATH')
        self.input_folder = os.path.join(data_path, 'input')
        self.output_folder = os.path.join(data_path , 'output')
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)