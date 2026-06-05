from .user_interface import UserInterface

__all__ = ['UserInterface']

def main():
    from load_dotenv import load_dotenv # Remove Before Prod
    load_dotenv() # Remove Before Prod
    ui = UserInterface()
    ui.run()