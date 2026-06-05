from .utility import Config, ValidationRequest
from .job_control import JobControl, JobResult
from rich.console import Console
import subprocess
import platform
import os
from pathlib import Path
from operator import attrgetter
from dataclasses import dataclass
from typing import Optional, Callable, Any

@dataclass
class ValidSelection:
    status: bool
    choice: Optional[int | str] = None
    back: Optional[bool] = None
    quit: Optional[bool] = None

@dataclass
class NextScreen:
    screen: Callable
    ags: Optional[Any] = None

class UserInterface:
    def __init__(self):
        self.on = True
        self.config = Config()
        self.console = Console()
        self.file_dictionary: dict[int, os.DirEntry] = {}

    def __choice_validator(
            self,
            user_choice:str,
            valid_options: list,
            quit:bool = False
            ) -> ValidSelection:
        try:
            user_choice= int(user_choice)
        except Exception:
            user_choice = user_choice.lower()
        if user_choice in valid_options:
            return ValidSelection(
                status=True, choice=user_choice
            )
        elif user_choice.lower() == 'q':
            return ValidSelection(
                status=True, quit=True
            )
        else:
            return ValidSelection(status=False)

    def __clear_screen(self):
        command = "cls" if platform.system() == 'Windows' else 'clear'
        subprocess.run([command], shell=True)

    def __get_file_paths(self):
        self.file_list = os.scandir(self.config.input_folder)
        a = sorted(self.file_list, key=attrgetter('name'))
        mydict = {}
        for n,i in enumerate(a):
            mydict[n+1] = i
        self.file_dictionary = mydict

    def __rule(self):
        self.console.rule('DCMA 14 Point Assessment')

    def screen_welcome(self):
        self.__clear_screen()
        self.console.print('Welcome...')
        self.console.input('Press Enter to Continue...')
        return NextScreen(self.screen_choose_files)

    def screen_quit(self):
        self.__clear_screen()
        self.console.print('\n')
        self.console.print('Goodbye')
        self.on = False

    def screen_choose_files(self):
        choice_valid = False
        while not choice_valid:
            self.__clear_screen()
            self.__get_file_paths()
            self.__rule()
            self.console.print('Select a File:\n')
            for k,v in self.file_dictionary.items():
                self.console.print(f'{k}: {v.name}')
            self.console.print('\n') 
            uc = self.console.input('Select a file by number or "q" to quit: ')
            ucp = self.__choice_validator(uc, self.file_dictionary.keys())
            choice_valid = ucp.status
        if ucp.quit:
            return NextScreen(self.screen_quit)
        else:
            return NextScreen(self.screen_wait, ucp.choice)

    def screen_wait(self, selection):
        self.__clear_screen()
        self.__rule()
        self.console.print('\nPlease wait while we create the report...')
        path = self.file_dictionary[selection]
        vr = ValidationRequest(input_path=path.path, output_folder=self.config.output_folder)
        jc = JobControl(vr)
        result = jc.run()
        return NextScreen(self.screen_display_results, result)

    def screen_display_results(self, results: JobResult):
        choice_ok = False
        while not choice_ok:
            self.__clear_screen()
            self.__rule()
            self.console.print(f"Status: {results.status}")
            self.console.print(f"Output: {results.output}")
            uc = self.console.input('Would you like to validate another schedule? "y" or "n": ')
            ucp = self.__choice_validator(user_choice=uc, valid_options=['y', 'n'])
            choice_ok = ucp.status
        if ucp.choice == 'y':
            return NextScreen(self.screen_choose_files)
        else:
            return NextScreen(self.screen_quit)

    def run(self):
        current_screen = NextScreen(self.screen_welcome)
        while self.on:
            if current_screen.ags:
                next_screen = current_screen.screen(current_screen.ags)
            else:
                next_screen = current_screen.screen()
            current_screen = next_screen





if __name__ == '__main__':
    from load_dotenv import load_dotenv
    load_dotenv()
    ui = UserInterface()
    ui.run()