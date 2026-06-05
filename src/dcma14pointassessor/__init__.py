from .user_interface import UserInterface

__all__ = ['UserInterface']

def main():
    ui = UserInterface()
    ui.run()