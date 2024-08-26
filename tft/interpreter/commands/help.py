


from typing import Any, override
from tft.interpreter.commands.registry import COMMAND_REGISTRY, Command, ValidationException, register


@register(name='help')
class HelpCommand(Command):
    
    @override
    def validate(self, inputs: list | None = None) -> Any:
        if inputs is None:
            raise ValidationException("Parameter to inputs cannot be none.")
        if len(inputs) > 2:
            raise ValidationException("Number of params to inputs has to 0 or 1.")
        for inp in inputs:
            if inp not in COMMAND_REGISTRY:
                raise ValidationException(f"Command not found: {inp}")
        return inputs
    
    @override
    def execute(self, inputs: Any = None) -> Any:
        return inputs
    
    @override
    def print(self, outputs: Any = None) -> None:
        if len(outputs) == 0:
            print("Available commands:")
            for command in sorted(COMMAND_REGISTRY.keys()):
                print(f"  {command:10} {COMMAND_REGISTRY[command].name()}")
        else:
            command = outputs[0]
            command_name = COMMAND_REGISTRY[command].name()
            print(f"{command_name} ({command})")
            COMMAND_REGISTRY[command].description()
    
    @override
    def name(self) -> str:
        return "Help"
    
    @override
    def description(self) -> None:
        print("This command is used to view all commands and to view details about")
        print("other commands.")
        print("Usage: help <?command>")
        