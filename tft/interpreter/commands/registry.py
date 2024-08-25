
from abc import ABC, abstractmethod
from typing import Any

class ValidationException(Exception):
    pass

class Command(ABC):
    @abstractmethod
    def validate(self, inputs=None) -> Any:
        """Does any validation and conversion before executing the command.
        Should be overriden. Should throw validation exception. Should return
        validated parameters."""
        raise NotImplementedError('Need to implement validate().')

    @abstractmethod
    def execute(self, inputs=None) -> Any:
        """Executes the command."""
        raise NotImplementedError('Need to implement execute().')
    
    def print(self, outputs=None) -> None:
        """Prints outputs of command to command line. Should be overriden
        with specific rendering logic."""
        print(outputs)

COMMAND_REGISTRY: dict[str, Command] = {}
QUIT_COMMANDS = {'q', 'exit', 'quit'}

def register(name: str):
    """Register a command name. Command name will be used in command line."""
    def identity(cls):
        assert name not in COMMAND_REGISTRY, f"Two commands registered under: {name}"
        assert name not in QUIT_COMMANDS, f"Command name cannot be a quit command: {QUIT_COMMANDS}"
        COMMAND_REGISTRY[name] = cls
        return cls
    return identity