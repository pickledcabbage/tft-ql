
from abc import ABC, abstractmethod
from typing import Any

class ValidationException(Exception):
    pass

class Command(ABC):
    @abstractmethod
    def validate(self, inputs: list | None = None) -> Any:
        """Does any validation and conversion before executing the command.
        Should be overriden. Should throw validation exception. Should return
        validated parameters."""
        return None

    @abstractmethod
    def execute(self, inputs: Any = None) -> Any:
        """Executes the command."""
        return None
    
    def print(self, outputs: Any = None) -> None:
        """Prints outputs of command to command line. Should be overriden
        with specific rendering logic."""
        print(outputs)

COMMAND_REGISTRY: dict[str, Command] = {}
QUIT_COMMANDS = {'q', 'exit', 'quit'}

def register(name: str):
    """Register a command name. Command name will be used in command line."""
    assert ' ' not in name, "Command names cannot have spaces!"
    def identity(cls):
        assert name not in COMMAND_REGISTRY, f"Two commands registered under: {name}"
        assert name not in QUIT_COMMANDS, f"Command name cannot be a quit command: {QUIT_COMMANDS}"
        COMMAND_REGISTRY[name] = cls()
        return cls
    return identity