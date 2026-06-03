from .utility import Config
from rich.console import Console
import subprocess
import platform
import os
from pathlib import Path

class UserInterface:
    def __init__(self):
        self.config = Config()
        self.console = Console()
        self.file_dictionary = {}

    def __clear_screen(self):
        command = "cls" if platform.system() == 'Windows' else 'clear'
        subprocess.run([command], shell=True)

    def __get_file_paths(self):
        self.file_list = os.scandir(self.config.input_folder)
        mydict = {}
        for n,i in enumerate(self.file_list):
            mydict[n+1] = i
        self.file_dictionary = mydict

    def screen_welcome(self):
        self.__clear_screen()
        self.console.print('Welcome...')
        self.console.input('Press Enter to Continue...')
        return














if __name__ == '__main__':
    from load_dotenv import load_dotenv
    load_dotenv()
    ui = UserInterface()
    ui.__get_file_paths()