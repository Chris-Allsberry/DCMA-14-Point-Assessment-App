import datetime as dt
from dataclasses import dataclass
from operator import attrgetter
import os
import platform
import subprocess
import time
from typing import Optional, Callable, Any

from rich.console import Console

from .art import Gallery
from .job_control import JobControl, JobResult
from .utility import Config, ValidationRequest

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
        self.art = Gallery()
        self.config = Config()
        self.console = Console()
        self.wait_seconds = 2
        self.file_dictionary: dict[int, os.DirEntry] = {}

    def __choice_validator(
            self,
            user_choice:str,
            valid_options: list,
            quit:bool = False
            ) -> ValidSelection:
        try:
            user_choice= int(user_choice)
            if user_choice in valid_options:
                return ValidSelection(
                    status=True, choice=user_choice
                )
            else:
                return ValidSelection(
                    status=False
                )
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

    def __time_waster(self, start:dt.datetime, finish:dt.datetime):
        time_delta = finish - start
        if time_delta.seconds > self.wait_seconds:
            return
        else:
            time.sleep(self.wait_seconds - time_delta.seconds)

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
        self.console.print('\n')

    def screen_welcome(self):
        self.__clear_screen()
        self.__rule()
        self.console.print(self.art.title1)
        self.console.print(self.art.title2)
        self.console.print('\n')
        self.console.input('Press Enter to Continue...')
        return NextScreen(self.screen_choose_files)

    def screen_quit(self):
        self.__clear_screen()
        self.__rule()
        self.console.print('\n')
        self.console.print(self.art.goodbye)
        self.on = False

    def screen_choose_files(self):
        choice_valid = False
        while not choice_valid:
            self.__clear_screen()
            self.__get_file_paths()
            self.__rule()
            self.console.print(f'[bold]Files in input path ([/bold][green]{self.config.input_folder}[/green][bold]):[/bold]\n')
            if len(self.file_dictionary) == 0:
                self.console.print(self.art.no_files)
                uc = self.console.input('\nLooks like there are no files here. Press "Enter" to refresh or "q" to quit: ')
            else:
                for k,v in self.file_dictionary.items():
                    self.console.print(f'{k}: {v.name}')
                self.console.print('\n') 
                uc = self.console.input('Select a file by [green]number[/green] or enter "q" to quit: ')
            ucp = self.__choice_validator(uc, self.file_dictionary.keys())
            choice_valid = ucp.status
        if ucp.quit:
            return NextScreen(self.screen_quit)
        else:
            return NextScreen(self.screen_wait, ucp.choice)

    def screen_wait(self, selection):
        self.__clear_screen()
        self.__rule()
        with self.console.status('\nPlease wait while we create the report...', spinner='aesthetic'):
            start = dt.datetime.now(dt.timezone.utc)
            path = self.file_dictionary[selection]
            vr = ValidationRequest(input_path=path.path, output_folder=self.config.output_folder)
            jc = JobControl(vr)
            result = jc.run()
            finish = dt.datetime.now(dt.timezone.utc)
            self.__time_waster(start=start, finish=finish)
            return NextScreen(self.screen_display_results, result)

    def screen_display_results(self, results: JobResult):
        choice_ok = False
        while not choice_ok:
            self.__clear_screen()
            self.__rule()
            self.console.print('Validation Results:\n', style='bold')
            self.console.print(f"Status: {results.status}")
            if results.status:
                self.console.print(f"Output: {results.output}")
            else:
                self.console.print(results.error)
            print('\n')
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
